#!/usr/bin/env python3
"""Live Graphiti run for the derived-conflict-v0 (Polaris) substitution experiment.

Requires the pinned environment in requirements.txt. Graphiti's own storage,
contradiction-resolution, deduplication, and episode-removal code runs against
an embedded Kuzu database.

No LLM is used. Once edges carry `valid_at`, Graphiti's only LLM step on the
exercised paths is the contradiction verdict (`dedupe_edges.resolve_edge`).
That verdict is scripted so Graphiti's deterministic handling of a given
verdict can be observed. Any other LLM call raises. Nothing here measures what
a real model would judge.
"""
import os

os.environ["GRAPHITI_TELEMETRY_ENABLED"] = "false"  # must precede graphiti imports

import asyncio
import copy
import inspect
import json
import logging
import pathlib
import platform
import subprocess
import sys
import warnings
from datetime import datetime, timezone
from importlib.metadata import version
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))

from run_graphiti_adapter_v0 import (  # noqa: E402
    GROUP_ID,
    RESULTS,
    admission_is_read_only,
    admission_projection,
    adapter_attribute_loss,
    conformance_report,
    edge_candidate,
    graphiti_edge,
    graphiti_uuid,
    load_fixture,
    ml_meta,
    plan_edge,
    support_assessments,
    translate_polaris,
)

import graphiti_core  # noqa: E402
import graphiti_core.utils.maintenance.edge_operations as edge_operations  # noqa: E402
from graphiti_core.driver.kuzu_driver import KuzuDriver  # noqa: E402
from graphiti_core.edges import EntityEdge, EpisodicEdge  # noqa: E402
from graphiti_core.graphiti import Graphiti  # noqa: E402
from graphiti_core.nodes import EntityNode, EpisodeType, EpisodicNode  # noqa: E402

logging.basicConfig(level=logging.WARNING)

LATER = "2026-06-02T00:00:00+00:00"
EARLIER = "2026-05-31T00:00:00+00:00"
RESTATED_EVIDENCE = "EV-POLARIS-CHECKS-RESTATED"


class ScriptedVerdictLLM:
    """Stands in for Graphiti's LLM participant on the contradiction prompt only."""

    def __init__(self, verdicts):
        self.verdicts = list(verdicts)
        self.calls = []

    async def generate_response(self, messages, response_model=None, max_tokens=None,
                                model_size=None, group_id=None, prompt_name=None, **kwargs):
        self.calls.append(prompt_name)
        if prompt_name != "dedupe_edges.resolve_edge" or not self.verdicts:
            raise RuntimeError(f"unscripted LLM call: {prompt_name}")
        return self.verdicts.pop(0)


def dt(value):
    return None if value is None else datetime.fromisoformat(value)


def iso(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def to_entity_edge(edge):
    return EntityEdge(
        uuid=edge["uuid"],
        group_id=edge["group_id"],
        source_node_uuid=edge["source_node_uuid"],
        target_node_uuid=edge["target_node_uuid"],
        created_at=dt(edge["created_at"]),
        name=edge["name"],
        fact=edge["fact"],
        episodes=list(edge["episodes"]),
        valid_at=dt(edge["valid_at"]),
        invalid_at=dt(edge["invalid_at"]),
        expired_at=dt(edge["expired_at"]),
        reference_time=dt(edge["reference_time"]),
        attributes=copy.deepcopy(edge["attributes"]),
    )


def from_entity_edge(edge):
    attributes = edge.attributes
    if isinstance(attributes, str):
        attributes = json.loads(attributes or "{}")
    return {
        "uuid": edge.uuid,
        "group_id": edge.group_id,
        "source_node_uuid": edge.source_node_uuid,
        "target_node_uuid": edge.target_node_uuid,
        "created_at": iso(edge.created_at),
        "name": edge.name,
        "fact": edge.fact,
        "episodes": list(edge.episodes),
        "valid_at": iso(edge.valid_at),
        "invalid_at": iso(edge.invalid_at),
        "expired_at": iso(edge.expired_at),
        "reference_time": iso(edge.reference_time),
        "attributes": attributes or {},
    }


def episode_record(evidence_id, source_id, text, valid_at, edge_uuids):
    return {
        "uuid": graphiti_uuid("episode:" + evidence_id),
        "name": evidence_id,
        "group_id": GROUP_ID,
        "source": "text",
        "source_description": source_id,
        "content": text,
        "valid_at": valid_at,
        "created_at": valid_at,
        "entity_edges": list(edge_uuids),
    }


async def save_episode(driver, plan, episode):
    await EpisodicNode(
        uuid=episode["uuid"],
        name=episode["name"],
        group_id=episode["group_id"],
        source=EpisodeType.text,
        source_description=episode["source_description"],
        content=episode["content"],
        valid_at=dt(episode["valid_at"]),
        created_at=dt(episode["created_at"]),
        entity_edges=list(episode["entity_edges"]),
    ).save(driver)
    for mention in plan["mentions"]:
        if mention["source_node_uuid"] == episode["uuid"]:
            await EpisodicEdge(
                uuid=mention["uuid"],
                group_id=mention["group_id"],
                source_node_uuid=mention["source_node_uuid"],
                target_node_uuid=mention["target_node_uuid"],
                created_at=dt(mention["created_at"]),
            ).save(driver)


async def write_plan(driver, plan, *, skip_edges=(), skip_episodes=()):
    created = dt(plan["reference_times"]["SYN-DM-0400"])
    for entity in plan["entities"]:
        await EntityNode(
            uuid=entity["uuid"], name=entity["name"], group_id=entity["group_id"],
            labels=[], created_at=created,
        ).save(driver)
    for episode in plan["episodes"]:
        if episode["uuid"] not in skip_episodes:
            await save_episode(driver, plan, episode)
    for edge in plan["edges"]:
        if edge["uuid"] not in skip_edges:
            await to_entity_edge(edge).save(driver)


async def read_state(driver):
    try:
        edges = await EntityEdge.get_by_group_ids(driver, [GROUP_ID])
    except Exception as exc:  # Graphiti raises when a group has no edges
        if "NotFound" not in type(exc).__name__:
            raise
        edges = []
    try:
        episodes = await EpisodicNode.get_by_group_ids(driver, [GROUP_ID])
    except Exception as exc:
        if "NotFound" not in type(exc).__name__:
            raise
        episodes = []
    edge_state = sorted((from_entity_edge(edge) for edge in edges), key=lambda item: item["uuid"])
    return edge_state, sorted(episode.uuid for episode in episodes)


def new_driver(deprecations):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        driver = KuzuDriver(":memory:")
    deprecations.update(str(item.message) for item in caught)
    return driver


def graphiti_native_current(edges, labels):
    return sorted(labels[edge["uuid"]] for edge in edges if edge["invalid_at"] is None and edge["expired_at"] is None)


def summarize(scenario, labels):
    admission = scenario["admission"]
    return {
        "graphiti_native_current": graphiti_native_current(scenario["after"], labels),
        "newly_closed": [labels[item] for item in scenario["conformance"]["observed"]["newly_closed"]],
        "deleted": [labels[item] for item in scenario["conformance"]["observed"]["deleted"]],
        "memory_lab_dispositions": {
            labels[edge_uuid]: f"{item['disposition']} ({item['reason']})"
            for edge_uuid, item in admission["dispositions"].items()
        },
        "consistency_outcomes": [item["consistency_outcome"] for item in admission["consistency"]],
        "conformance": {
            key: value["verdict"] for key, value in scenario["conformance"].items() if key.startswith("EP-")
        },
    }


def finish(name, description, plan, before, after, episodes_after, snapshot, llm, verdicts, extra=None):
    admission = admission_projection(after, snapshot, plan["side_table"], plan["names"])
    scenario = {
        "description": description,
        "snapshot": snapshot,
        "scripted_verdicts": verdicts,
        "llm_calls": list(llm.calls) if llm else [],
        "before": before,
        "after": after,
        "episodes_after": episodes_after,
        "adapter_attribute_loss": adapter_attribute_loss(after),
        "admission": admission,
        "introduced": list((extra or {}).get("introduced", [])),
        "conformance": conformance_report(
            before, after, episodes_after, plan["side_table"], snapshot,
            (extra or {}).get("introduced", []),
        ),
    }
    scenario.update(extra or {})
    return name, scenario


async def direct_write_world_change(plan, deprecations):
    """Recommended adapter path: direct writes, admission as projection, and one
    genuine world change resolved by Graphiti's own contradiction code."""
    sigma_clear = plan_edge(plan, evidence_id="EV-SIGMA-CLEAR-0401")
    sigma_blocked = plan_edge(plan, evidence_id="EV-SIGMA-BLOCKED-0400")
    clear_episode = graphiti_uuid("episode:EV-SIGMA-CLEAR-0401")
    driver = new_driver(deprecations)
    await write_plan(driver, plan, skip_edges={sigma_clear["uuid"]}, skip_episodes={clear_episode})
    before, _ = await read_state(driver)
    admission_0400 = admission_projection(before, "SYN-DM-0400", plan["side_table"], plan["names"])
    after_admission, _ = await read_state(driver)
    read_only = admission_is_read_only(before, after_admission)

    await save_episode(driver, plan, next(item for item in plan["episodes"] if item["uuid"] == clear_episode))
    verdicts = [{"duplicate_facts": [], "contradicted_facts": [0]}]
    llm = ScriptedVerdictLLM(verdicts)
    resolved, invalidated, _ = await edge_operations.resolve_extracted_edge(
        llm,
        to_entity_edge(sigma_clear),
        [],
        [await EntityEdge.get_by_uuid(driver, sigma_blocked["uuid"])],
        await EpisodicNode.get_by_uuid(driver, clear_episode),
    )
    for edge in [resolved] + invalidated:
        await edge.save(driver)
    after, episodes_after = await read_state(driver)
    return finish(
        "direct_write_world_change",
        "Polaris written directly (no resolution). Admission computed as a projection at 0400; "
        "then Sigma-clear arrives and Graphiti's resolve_extracted_edge handles a scripted "
        "'contradicts Sigma-blocked' verdict (a genuine world change).",
        plan, before, after, episodes_after, "SYN-DM-0401", llm, verdicts,
        {
            "introduced": [sigma_clear["uuid"]],
            "admission_before": admission_0400,
            "EP-08_admission_read_only": read_only,
            "graphiti_native_current_before": sorted(
                edge["uuid"] for edge in before if edge["invalid_at"] is None and edge["expired_at"] is None
            ),
        },
    )


async def native_resolution(plan, deprecations, *, name, description, new_evidence=None,
                            new_derived=None, candidate_evidence=None, candidate_derived=None,
                            valid_at, verdicts, episode_evidence):
    new_edge = copy.deepcopy(plan_edge(plan, evidence_id=new_evidence, derived=new_derived))
    candidate = plan_edge(plan, evidence_id=candidate_evidence, derived=candidate_derived)
    sigma_clear = plan_edge(plan, evidence_id="EV-SIGMA-CLEAR-0401")
    clear_episode = graphiti_uuid("episode:EV-SIGMA-CLEAR-0401")
    driver = new_driver(deprecations)
    await write_plan(
        driver, plan,
        skip_edges={sigma_clear["uuid"], new_edge["uuid"]},
        skip_episodes={clear_episode},
    )
    before, _ = await read_state(driver)
    new_edge["valid_at"] = valid_at
    llm = ScriptedVerdictLLM(verdicts)
    resolved, invalidated, _ = await edge_operations.resolve_extracted_edge(
        llm,
        to_entity_edge(new_edge),
        [],
        [await EntityEdge.get_by_uuid(driver, candidate["uuid"])],
        await EpisodicNode.get_by_uuid(driver, graphiti_uuid("episode:" + episode_evidence)),
    )
    for edge in [resolved] + invalidated:
        await edge.save(driver)
    after, episodes_after = await read_state(driver)
    return finish(name, description, plan, before, after, episodes_after, "SYN-DM-0400", llm, verdicts,
                  {"new_edge_valid_at": valid_at, "introduced": [new_edge["uuid"]]})


async def corroborated_driver(plan, deprecations):
    """Plan at 0400 plus a second episode restating the release-checks fact,
    merged by Graphiti's deterministic exact-fact fast path (no LLM)."""
    checks = plan_edge(plan, evidence_id="EV-POLARIS-CHECKS-0400")
    sigma_clear = plan_edge(plan, evidence_id="EV-SIGMA-CLEAR-0401")
    clear_episode = graphiti_uuid("episode:EV-SIGMA-CLEAR-0401")
    driver = new_driver(deprecations)
    await write_plan(driver, plan, skip_edges={sigma_clear["uuid"]}, skip_episodes={clear_episode})
    before, _ = await read_state(driver)
    restated = episode_record(RESTATED_EVIDENCE, "SRC-POLARIS-CHECKS-RESTATED", checks["fact"], LATER, [checks["uuid"]])
    mentions = [
        {
            "uuid": graphiti_uuid(f"mention:{RESTATED_EVIDENCE}:{node}"),
            "group_id": GROUP_ID,
            "source_node_uuid": restated["uuid"],
            "target_node_uuid": node,
            "created_at": LATER,
        }
        for node in (checks["source_node_uuid"], checks["target_node_uuid"])
    ]
    await save_episode(driver, {"mentions": mentions}, restated)
    extracted = graphiti_edge(
        graphiti_uuid("edge:restated-checks"),
        checks["source_node_uuid"], checks["target_node_uuid"], "release_checks",
        checks["fact"], [restated["uuid"]], valid_at=LATER, meta={},
    )
    llm = ScriptedVerdictLLM([])
    resolved, invalidated, _ = await edge_operations.resolve_extracted_edge(
        llm,
        to_entity_edge(extracted),
        [await EntityEdge.get_by_uuid(driver, checks["uuid"])],
        [],
        await EpisodicNode.get_by_uuid(driver, restated["uuid"]),
    )
    for edge in [resolved] + invalidated:
        await edge.save(driver)
    return driver, before, llm, restated["uuid"], resolved.uuid


async def corroboration_fast_path(plan, deprecations):
    driver, before, llm, _, resolved_uuid = await corroborated_driver(plan, deprecations)
    after, episodes_after = await read_state(driver)
    return finish(
        "corroboration_fast_path",
        "A second episode restates an existing fact verbatim; Graphiti merges it by appending "
        "the episode to the existing edge without an LLM call.",
        plan, before, after, episodes_after, "SYN-DM-0400", llm, [],
        {"resolved_edge_uuid": resolved_uuid, "introduced": [graphiti_uuid("edge:restated-checks")]},
    )


async def remove_episode(plan, deprecations, *, first):
    checks = plan_edge(plan, evidence_id="EV-POLARIS-CHECKS-0400")
    driver, _, _, restated_uuid, _ = await corroborated_driver(plan, deprecations)
    before, _ = await read_state(driver)
    target = checks["episodes"][0] if first else restated_uuid
    await Graphiti.remove_episode(SimpleNamespace(driver=driver), target)
    after, episodes_after = await read_state(driver)
    if first:
        return finish(
            "remove_first_supporting_episode",
            "Graphiti.remove_episode on the release-checks fact's first episode while a second "
            "episode still supports it (a withdrawal mapped onto deletion).",
            plan, before, after, episodes_after, "SYN-DM-0400", None, [],
            {"removed_episode": target},
        )
    return finish(
        "remove_corroborating_episode",
        "Graphiti.remove_episode on the corroborating (second) episode of the release-checks fact.",
        plan, before, after, episodes_after, "SYN-DM-0400", None, [],
        {"removed_episode": target},
    )


def labels_for(plan):
    labels = {}
    for edge in plan["edges"]:
        meta = edge["attributes"]
        subject = plan["names"][edge["source_node_uuid"]]
        obj = plan["names"][edge["target_node_uuid"]]
        labels[edge["uuid"]] = f"{subject} {edge['name'].lower()}={obj} ({meta['ml_derivation']})"
    return labels


def source_anchor(obj):
    lines, start = inspect.getsourcelines(obj)
    path = pathlib.Path(inspect.getsourcefile(obj)).relative_to(pathlib.Path(graphiti_core.__file__).parent)
    return {"file": f"graphiti_core/{path}", "first_line": start, "last_line": start + len(lines) - 1}


def memory_lab_commit():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"head": head, "working_tree_dirty": bool(dirty)}


async def run():
    plan = translate_polaris(load_fixture())
    labels = labels_for(plan)
    deprecations = set()
    same = plan_edge(plan, derived="blocked")["valid_at"]
    runs = [
        await direct_write_world_change(plan, deprecations),
        await native_resolution(
            plan, deprecations, name="native_equal_valid_at_contradiction",
            description="Polaris-ready arrives after Polaris-blocked with the same valid_at; scripted verdict: contradicts.",
            new_derived="ready", candidate_derived="blocked", valid_at=same,
            verdicts=[{"duplicate_facts": [], "contradicted_facts": [0]}],
            episode_evidence="EV-POLARIS-APPROVAL-0400",
        ),
        await native_resolution(
            plan, deprecations, name="native_later_valid_at_contradiction",
            description="Polaris-ready arrives with a later valid_at than Polaris-blocked; scripted verdict: contradicts.",
            new_derived="ready", candidate_derived="blocked", valid_at=LATER,
            verdicts=[{"duplicate_facts": [], "contradicted_facts": [0]}],
            episode_evidence="EV-POLARIS-APPROVAL-0400",
        ),
        await native_resolution(
            plan, deprecations, name="native_earlier_valid_at_contradiction",
            description="Polaris-ready arrives after Polaris-blocked but with an earlier valid_at; scripted verdict: contradicts.",
            new_derived="ready", candidate_derived="blocked", valid_at=EARLIER,
            verdicts=[{"duplicate_facts": [], "contradicted_facts": [0]}],
            episode_evidence="EV-POLARIS-APPROVAL-0400",
        ),
        await native_resolution(
            plan, deprecations, name="native_equal_valid_at_no_contradiction",
            description="Polaris-ready arrives with the same valid_at; scripted verdict: no contradiction.",
            new_derived="ready", candidate_derived="blocked", valid_at=same,
            verdicts=[{"duplicate_facts": [], "contradicted_facts": []}],
            episode_evidence="EV-POLARIS-APPROVAL-0400",
        ),
        await native_resolution(
            plan, deprecations, name="native_multivalue_equal_valid_at_wrong_verdict",
            description="Tau dependency arrives with the same valid_at as the Sigma dependency; scripted (wrong) verdict: contradicts.",
            new_evidence="EV-POLARIS-TAU-DEP", candidate_evidence="EV-POLARIS-SIGMA-DEP", valid_at=same,
            verdicts=[{"duplicate_facts": [], "contradicted_facts": [0]}],
            episode_evidence="EV-POLARIS-TAU-DEP",
        ),
        await native_resolution(
            plan, deprecations, name="native_multivalue_later_valid_at_wrong_verdict",
            description="Tau dependency arrives with a later valid_at; scripted (wrong) verdict: contradicts (Graphiti issue #1728 shape).",
            new_evidence="EV-POLARIS-TAU-DEP", candidate_evidence="EV-POLARIS-SIGMA-DEP", valid_at=LATER,
            verdicts=[{"duplicate_facts": [], "contradicted_facts": [0]}],
            episode_evidence="EV-POLARIS-TAU-DEP",
        ),
        await corroboration_fast_path(plan, deprecations),
        await remove_episode(plan, deprecations, first=True),
        await remove_episode(plan, deprecations, first=False),
    ]
    scenarios = dict(runs)
    footprint = {
        fn.__name__: len(inspect.getsource(fn).splitlines())
        for fn in (translate_polaris, graphiti_edge, ml_meta, edge_candidate, support_assessments, admission_projection)
    }
    result = {
        "experiment": "graphiti-conflict-v0",
        "status": "executed",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "graphiti_core": version("graphiti-core"),
            "kuzu": version("kuzu"),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "driver": "KuzuDriver(':memory:'), embedded",
            "driver_deprecation_warnings": sorted(deprecations),
            "telemetry": "disabled (GRAPHITI_TELEMETRY_ENABLED=false)",
            "llm": "none: dedupe_edges.resolve_edge verdicts are scripted; any other LLM call raises",
            "embedder": "none: fact/name embeddings are null; Graphiti search is not exercised",
            "memory_lab_commit": memory_lab_commit(),
        },
        "graphiti_source_anchors": {
            "EntityEdge": source_anchor(EntityEdge),
            "resolve_extracted_edge": source_anchor(edge_operations.resolve_extracted_edge),
            "resolve_edge_contradictions": source_anchor(edge_operations.resolve_edge_contradictions),
            "_extract_edge_timestamps": source_anchor(edge_operations._extract_edge_timestamps),
            "Graphiti.remove_episode": source_anchor(Graphiti.remove_episode),
        },
        "translation_assumptions": [
            "snapshot SYN-DM-0400 -> reference/valid time 2026-06-01T00:00:00Z; SYN-DM-0401 -> 2026-06-15T00:00:00Z",
            "state facts are edges from subject entity to a value entity named by the value",
            "derived edges carry the canonical evidence closure as their Graphiti episodes list",
            "Memory Lab metadata (record id, qualifiers, derivation type, justifications, change kind) is carried in edge attributes and mirrored in an adapter side table",
            "candidate sets for contradiction are supplied directly rather than found by Graphiti search",
            "timing variants (later/earlier valid_at) are experimental perturbations, not fixture facts",
        ],
        "labels": labels,
        "adapter_footprint_lines": footprint,
        "scenarios": scenarios,
        "summary": {name: summarize(scenario, labels) for name, scenario in scenarios.items()},
    }
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    print(json.dumps({"environment": result["environment"], "adapter_footprint_lines": footprint}, indent=2, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(run())

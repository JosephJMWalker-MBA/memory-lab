#!/usr/bin/env python3
"""Graphiti substitution adapter for derived-conflict-v0 (Polaris).

This module owns only Memory Lab behavior:

- translating the Polaris fixture into graphiti-core 0.30.2 episode, entity,
  mention, and entity-edge shapes;
- a read-only current-view admission projection over Graphiti edge state that
  reuses the existing conflict and justification semantics unchanged;
- ML-EP-0 conformance checks over observed Graphiti edge state.

Graphiti is not imported here. Live Graphiti behavior is exercised by
experiments/graphiti-conflict-v0/run_graphiti_live.py and recorded under
experiments/graphiti-conflict-v0/results/.
"""
import copy
import json
import pathlib
import sys
import uuid

from run_contract_schema_validation import load_schema, validate
from run_derived_conflict_v0 import (
    CONSISTENCY_SCHEMA,
    CONSTRAINT_SCHEMA,
    assess_consistency,
    derived_record,
    load_fixture,
    predicate_constraint,
)
from run_derived_memory_adversarial import evidence_map, record, stable_id
from run_multiple_justifications_v0 import (
    ASSESSMENT_SCHEMA as JUSTIFICATION_ASSESSMENT_SCHEMA,
    SET_SCHEMA,
    assess as assess_justifications,
    justification,
    justification_set,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = (
    ROOT
    / "experiments"
    / "graphiti-conflict-v0"
    / "results"
    / "graphiti-conflict-v0.observed.json"
)
GROUP_ID = "memory-lab-polaris-v0"
UUID_NAMESPACE = uuid.UUID("5b0f5a1e-6d1c-4c52-9a51-6f1d2b0e7c01")
QUALIFIERS = {"environment": "production"}
DERIVED_VALID_FROM = "2026-06-01"

# Translation assumption: the fixture names snapshots, not calendar times.
# Graphiti needs datetimes, so each snapshot gets a fixed reference time.
REFERENCE_TIMES = {
    "SYN-DM-0400": "2026-06-01T00:00:00+00:00",
    "SYN-DM-0401": "2026-06-15T00:00:00+00:00",
}
# The existing conflict lane marks the Sigma-clear evidence as a world change.
WORLD_CHANGE_EVIDENCE = {"EV-SIGMA-CLEAR-0401"}

DERIVATIONS = (
    {
        "object": "blocked",
        "rule": "dependency_block_propagation",
        "antecedents": ("EV-POLARIS-SIGMA-DEP", "EV-SIGMA-BLOCKED-0400"),
        "fact": "Project Polaris status is blocked.",
    },
    {
        "object": "ready",
        "rule": "release_ready_propagation",
        "antecedents": ("EV-POLARIS-CHECKS-0400", "EV-POLARIS-APPROVAL-0400"),
        "fact": "Project Polaris status is ready.",
    },
)

# The same two groups the existing conflict lane assesses.
ADMISSION_GROUPS = (
    ("Project Polaris", "status", "derived"),
    ("Project Polaris", "depends_on", "extracted"),
)
ADMISSION_POLICY = "derived-conflict-v0/withhold-unresolved-supported-conflict"
STATUS_CONSTRAINT = predicate_constraint("state", "status")
CONSTRAINTS = {("state", "status"): STATUS_CONSTRAINT}

# Fields a Graphiti operation must never change on a retained edge. Temporal
# closure (invalid_at / expired_at) and episode growth are reported separately.
STABLE_FIELDS = ("source_node_uuid", "target_node_uuid", "name", "fact", "valid_at")
ML_META_KEYS = (
    "ml_record_id",
    "ml_record_type",
    "ml_qualifiers",
    "ml_derivation",
    "ml_justifications",
    "ml_evidence_refs",
    "ml_change_kind",
    "ml_snapshot",
)


def graphiti_uuid(key):
    return str(uuid.uuid5(UUID_NAMESPACE, key))


def extracted_record_id(assertion, snapshot_id):
    return stable_id(
        assertion["record_type"],
        assertion["subject"],
        assertion["predicate"],
        assertion["object"],
        assertion["qualifiers"],
        None,
        snapshot_id,
    )


def derived_record_id(obj):
    return stable_id(
        "state",
        "Project Polaris",
        "status",
        obj,
        QUALIFIERS,
        DERIVED_VALID_FROM,
        "SYN-DM-0400",
    )


def graphiti_edge(edge_uuid, source, target, predicate, fact, episodes, *, valid_at, meta):
    return {
        "uuid": edge_uuid,
        "group_id": GROUP_ID,
        "source_node_uuid": source,
        "target_node_uuid": target,
        "created_at": valid_at,
        "name": predicate.upper(),
        "fact": fact,
        "episodes": list(episodes),
        "valid_at": valid_at,
        "invalid_at": None,
        "expired_at": None,
        "reference_time": valid_at,
        "attributes": meta,
    }


def translate_polaris(fixture):
    """Map the Polaris fixture onto Graphiti-native shapes without an LLM."""
    entities = {}
    episodes = []
    mentions = []
    edges = []
    record_by_evidence = {}

    def entity(name):
        if name not in entities:
            entities[name] = {
                "uuid": graphiti_uuid("entity:" + name),
                "name": name,
                "group_id": GROUP_ID,
            }
        return entities[name]["uuid"]

    for item in fixture["evidence"]:
        assertion = item["assertions"][0]
        snapshot_id = item["snapshot_id"]
        reference_time = REFERENCE_TIMES[snapshot_id]
        record_id = extracted_record_id(assertion, snapshot_id)
        record_by_evidence[item["evidence_id"]] = record_id
        episode_uuid = graphiti_uuid("episode:" + item["evidence_id"])
        edge_uuid = graphiti_uuid("edge:" + record_id)
        source = entity(assertion["subject"])
        target = entity(assertion["object"])
        episodes.append(
            {
                "uuid": episode_uuid,
                "name": item["evidence_id"],
                "group_id": GROUP_ID,
                "source": "text",
                "source_description": item["source_id"],
                "content": item["text"],
                "valid_at": reference_time,
                "created_at": reference_time,
                "entity_edges": [edge_uuid],
            }
        )
        for node in (source, target):
            mentions.append(
                {
                    "uuid": graphiti_uuid(f"mention:{item['evidence_id']}:{node}"),
                    "group_id": GROUP_ID,
                    "source_node_uuid": episode_uuid,
                    "target_node_uuid": node,
                    "created_at": reference_time,
                }
            )
        change_kind = (
            "world_state_changed" if item["evidence_id"] in WORLD_CHANGE_EVIDENCE else "initial"
        )
        edges.append(
            graphiti_edge(
                edge_uuid,
                source,
                target,
                assertion["predicate"],
                item["text"],
                [episode_uuid],
                valid_at=reference_time,
                meta={
                    "ml_record_id": record_id,
                    "ml_record_type": assertion["record_type"],
                    "ml_qualifiers": dict(assertion["qualifiers"]),
                    "ml_derivation": "extracted",
                    "ml_justifications": [],
                    "ml_evidence_refs": [item["evidence_id"]],
                    "ml_change_kind": change_kind,
                    "ml_snapshot": snapshot_id,
                },
            )
        )

    derived_valid_at = DERIVED_VALID_FROM + "T00:00:00+00:00"
    for derivation in DERIVATIONS:
        record_id = derived_record_id(derivation["object"])
        antecedents = list(derivation["antecedents"])
        parents = [record_by_evidence[ref] for ref in antecedents]
        edges.append(
            graphiti_edge(
                graphiti_uuid("edge:" + record_id),
                entity("Project Polaris"),
                entity(derivation["object"]),
                "status",
                derivation["fact"],
                [graphiti_uuid("episode:" + ref) for ref in antecedents],
                valid_at=derived_valid_at,
                meta={
                    "ml_record_id": record_id,
                    "ml_record_type": "state",
                    "ml_qualifiers": dict(QUALIFIERS),
                    "ml_derivation": "derived",
                    "ml_justifications": [
                        justification(derivation["rule"], parents, antecedents)
                    ],
                    "ml_evidence_refs": sorted(antecedents),
                    "ml_change_kind": "initial",
                    "ml_snapshot": "SYN-DM-0400",
                },
            )
        )

    ordered_entities = sorted(entities.values(), key=lambda item: item["name"])
    return {
        "group_id": GROUP_ID,
        "reference_times": dict(REFERENCE_TIMES),
        "entities": ordered_entities,
        "episodes": episodes,
        "mentions": mentions,
        "edges": edges,
        "side_table": {edge["uuid"]: copy.deepcopy(edge["attributes"]) for edge in edges},
        "names": {item["uuid"]: item["name"] for item in ordered_entities},
    }


def ml_meta(edge, side_table):
    """Adapter metadata: from Graphiti attributes when present, else the side table.

    Graphiti 0.30.2 clears the attributes of a newly resolved edge when no custom
    edge type matches, so adapter data cannot rely on attributes alone.
    """
    attributes = edge.get("attributes") or {}
    if "ml_record_id" in attributes:
        return attributes
    return side_table[edge["uuid"]]


def graphiti_current(edge):
    return edge["invalid_at"] is None and edge["expired_at"] is None


def day(value):
    return None if value is None else value[:10]


def edge_candidate(edge, meta, names):
    """Project a Graphiti edge into the record shape the conflict lane consumes."""
    return {
        "record_id": meta["ml_record_id"],
        "record_type": meta["ml_record_type"],
        "subject": names[edge["source_node_uuid"]],
        "predicate": edge["name"].lower(),
        "object": names[edge["target_node_uuid"]],
        "qualifiers": meta["ml_qualifiers"],
        "valid_time": {"from": day(edge["valid_at"]), "to": day(edge["invalid_at"])},
    }


def support_assessments(edges, snapshot_id, side_table):
    """Evaluate derived-edge justifications against current extracted edges."""
    current_extracted = set()
    for edge in edges:
        meta = ml_meta(edge, side_table)
        if meta["ml_derivation"] == "extracted" and graphiti_current(edge):
            current_extracted.add(meta["ml_record_id"])

    results = {}
    for edge in edges:
        meta = ml_meta(edge, side_table)
        if meta["ml_derivation"] != "derived":
            continue
        set_artifact = justification_set(meta["ml_record_id"], meta["ml_justifications"])
        results[meta["ml_record_id"]] = assess_justifications(
            set_artifact, current_extracted, snapshot_id
        )
    return results


def admission_projection(edges, snapshot_id, side_table, names):
    """Read-only current-view admission over Graphiti edges.

    Nothing is written back to Graphiti. Dispositions use the GEI CVD value set
    and carry scope, policy, and as-of identity.
    """
    support = support_assessments(edges, snapshot_id, side_table)
    assessments = []
    dispositions = {}
    for subject, predicate, derivation in ADMISSION_GROUPS:
        members = [
            edge
            for edge in edges
            if names[edge["source_node_uuid"]] == subject
            and edge["name"] == predicate.upper()
            and ml_meta(edge, side_table)["ml_derivation"] == derivation
        ]
        if not members:
            continue
        candidates = [edge_candidate(edge, ml_meta(edge, side_table), names) for edge in members]
        if derivation == "derived":
            supported = {
                record_id
                for record_id, item in support.items()
                if item["support_outcome"] == "retained"
            }
            unsupported_reason = "support_withdrawn"
        else:
            supported = {
                ml_meta(edge, side_table)["ml_record_id"]
                for edge in members
                if graphiti_current(edge)
            }
            unsupported_reason = "closed_in_graphiti"
        constraint = CONSTRAINTS.get((candidates[0]["record_type"], predicate))
        assessment = assess_consistency(candidates, supported, snapshot_id, constraint)
        assessments.append(assessment)
        for edge, candidate in zip(members, candidates):
            record_id = candidate["record_id"]
            if record_id in assessment["selected_record_ids"]:
                disposition, reason = "admitted", assessment["reason_code"]
            elif record_id in assessment["supported_record_ids"]:
                disposition, reason = "withheld", "unresolved_supported_conflict"
            else:
                disposition, reason = "withheld", unsupported_reason
            dispositions[edge["uuid"]] = {
                "record_id": record_id,
                "disposition": disposition,
                "reason": reason,
                "assessment_id": assessment["assessment_id"],
                "scope": edge["group_id"],
                "policy": ADMISSION_POLICY,
                "as_of": snapshot_id,
            }
    return {
        "support": support,
        "consistency": assessments,
        "dispositions": dict(sorted(dispositions.items())),
    }


def admission_is_read_only(edges_before, edges_after):
    unchanged = json.dumps(edges_before, sort_keys=True) == json.dumps(edges_after, sort_keys=True)
    leaked = sorted(
        edge["uuid"]
        for edge in edges_after
        if any(key.startswith("ml_disposition") for key in (edge.get("attributes") or {}))
    )
    return {
        "verdict": "pass" if unchanged and not leaked else "fail",
        "violations": leaked if unchanged else ["graphiti_edges_changed_by_admission"] + leaked,
    }


def newly_closed(before_by_uuid, after):
    closed = []
    for edge in after:
        prior = before_by_uuid.get(edge["uuid"])
        was_current = prior is None or graphiti_current(prior)
        if was_current and not graphiti_current(edge):
            closed.append(edge)
    return closed


def world_change_supported(edge, after, side_table):
    """True when a successor with the same subject/predicate/scope starts at the
    closure time and its evidence is marked as a world change."""
    if edge["invalid_at"] is None:
        return False
    meta = ml_meta(edge, side_table)
    for successor in after:
        if successor["uuid"] == edge["uuid"]:
            continue
        successor_meta = ml_meta(successor, side_table)
        if (
            successor["source_node_uuid"] == edge["source_node_uuid"]
            and successor["name"] == edge["name"]
            and successor_meta["ml_qualifiers"] == meta["ml_qualifiers"]
            and successor["valid_at"] == edge["invalid_at"]
            and successor_meta["ml_change_kind"] == "world_state_changed"
        ):
            return True
    return False


def verdict(violations):
    return {"verdict": "fail" if violations else "pass", "violations": sorted(violations)}


def conformance_report(before, after, episodes_after, side_table, snapshot_id, introduced=()):
    """ML-EP-0 checks over one observed Graphiti operation (before -> after).

    `introduced` lists edges the operation was asked to add. Any other new
    derived edge counts as an invented proposition.
    """
    before_by_uuid = {edge["uuid"]: edge for edge in before}
    after_by_uuid = {edge["uuid"]: edge for edge in after}
    live_episodes = set(episodes_after)

    deleted = sorted(set(before_by_uuid) - set(after_by_uuid))
    rewritten = []
    lost_episodes = []
    temporal_updates = []
    for edge_uuid, prior in before_by_uuid.items():
        current = after_by_uuid.get(edge_uuid)
        if current is None:
            continue
        if any(prior[field] != current[field] for field in STABLE_FIELDS):
            rewritten.append(edge_uuid)
        if not set(prior["episodes"]) <= set(current["episodes"]):
            lost_episodes.append(edge_uuid)
        if (prior["invalid_at"], prior["expired_at"]) != (
            current["invalid_at"],
            current["expired_at"],
        ):
            temporal_updates.append(edge_uuid)

    dangling = [
        edge["uuid"]
        for edge in after
        if any(episode not in live_episodes for episode in edge["episodes"])
    ]
    deleted_with_surviving_support = [
        edge_uuid
        for edge_uuid in deleted
        if any(episode in live_episodes for episode in before_by_uuid[edge_uuid]["episodes"])
    ]
    invented = [
        edge["uuid"]
        for edge in after
        if edge["uuid"] not in before_by_uuid
        and edge["uuid"] not in introduced
        and ml_meta(edge, side_table)["ml_derivation"] == "derived"
    ]

    support = support_assessments(after, snapshot_id, side_table)
    closed = newly_closed(before_by_uuid, after)
    collapsed_support = []
    unconstrained = []
    unsupported_world_change = []
    for edge in closed:
        meta = ml_meta(edge, side_table)
        world_change = world_change_supported(edge, after, side_table)
        if meta["ml_derivation"] == "derived":
            support_valid = support[meta["ml_record_id"]]["support_outcome"] == "retained"
        else:
            support_valid = any(episode in live_episodes for episode in edge["episodes"])
        if support_valid and not world_change:
            collapsed_support.append(edge["uuid"])
        constraint = CONSTRAINTS.get((meta["ml_record_type"], edge["name"].lower()))
        if constraint is None or constraint["value_cardinality"] != "single_value_per_scope":
            unconstrained.append(edge["uuid"])
        if edge["invalid_at"] is not None and not world_change:
            unsupported_world_change.append(edge["uuid"])

    return {
        "EP-01_historical_preservation": verdict(deleted + rewritten + lost_episodes),
        "EP-02_provenance_closure": verdict(dangling),
        "EP-04_multiple_support": verdict(deleted_with_surviving_support),
        "EP-05_withdrawal_not_negation": verdict(invented),
        "EP-07_support_vs_consistency": verdict(collapsed_support),
        "EP-09_explicit_conflict_basis": verdict(unconstrained),
        "EP-10_world_change_vs_correction": verdict(unsupported_world_change),
        "observed": {
            "deleted": deleted,
            "newly_closed": sorted(edge["uuid"] for edge in closed),
            "in_place_temporal_updates": sorted(temporal_updates),
        },
    }


def adapter_attribute_loss(edges):
    return sorted(
        edge["uuid"]
        for edge in edges
        if not set(ML_META_KEYS) <= set((edge.get("attributes") or {}))
    )


# --------------------------------------------------------------------------
# Synthetic checks of Memory-Lab-owned behavior (no Graphiti required)
# --------------------------------------------------------------------------


def plan_edge(plan, *, evidence_id=None, derived=None):
    for edge in plan["edges"]:
        meta = edge["attributes"]
        if evidence_id is not None and meta["ml_evidence_refs"] == [evidence_id] and meta["ml_derivation"] == "extracted":
            return edge
        if derived is not None and meta["ml_derivation"] == "derived" and plan["names"][edge["target_node_uuid"]] == derived:
            return edge
    raise KeyError(evidence_id or derived)


def state(plan, *, drop=(), updates=None):
    updates = updates or {}
    edges = []
    for edge in plan["edges"]:
        if edge["uuid"] in drop:
            continue
        item = copy.deepcopy(edge)
        item.update(updates.get(edge["uuid"], {}))
        edges.append(item)
    return sorted(edges, key=lambda item: item["uuid"])


def episode_ids(plan, *, drop=()):
    return sorted(item["uuid"] for item in plan["episodes"] if item["uuid"] not in drop)


def expected_lane_assessments(fixture):
    """Rebuild the existing conflict lane's assessments from native ML records."""
    evidence = evidence_map(fixture)
    ids = {
        ref: extracted_record_id(evidence[ref]["assertions"][0], evidence[ref]["snapshot_id"])
        for ref in evidence
    }
    valid_time = {"from": DERIVED_VALID_FROM, "to": None}
    native = {}
    for derivation in DERIVATIONS:
        record_id = derived_record_id(derivation["object"])
        antecedents = list(derivation["antecedents"])
        parents = [ids[ref] for ref in antecedents]
        set_artifact = justification_set(
            record_id, [justification(derivation["rule"], parents, antecedents)]
        )
        native[derivation["object"]] = derived_record(
            record_id,
            "Project Polaris",
            "status",
            derivation["object"],
            QUALIFIERS,
            antecedents,
            parents,
            set_artifact["justification_set_id"],
            "SYN-DM-0400",
            derivation["fact"],
            valid_time,
        )
    blocked, ready = native["blocked"], native["ready"]
    sigma_dep = record(
        "relationship", "Project Polaris", "depends_on", "Module Sigma",
        ["EV-POLARIS-SIGMA-DEP"], "SYN-DM-0400", qualifiers=QUALIFIERS,
    )
    tau_dep = record(
        "relationship", "Project Polaris", "depends_on", "Module Tau",
        ["EV-POLARIS-TAU-DEP"], "SYN-DM-0400", qualifiers=QUALIFIERS,
    )
    both = {blocked["record_id"], ready["record_id"]}
    return {
        "conflict_0400": assess_consistency(
            [blocked, ready], both, "SYN-DM-0400", STATUS_CONSTRAINT
        ),
        "resolved_0401": assess_consistency(
            [blocked, ready], {ready["record_id"]}, "SYN-DM-0401", STATUS_CONSTRAINT
        ),
        "multivalue_0400": assess_consistency(
            [sigma_dep, tau_dep],
            {sigma_dep["record_id"], tau_dep["record_id"]},
            "SYN-DM-0400",
            None,
        ),
    }


def outcome(admission, predicate):
    for item in admission["consistency"]:
        members = item["record_ids"]
        if predicate == "status" and len(members) == 2 and item["constraint_id"] == STATUS_CONSTRAINT["constraint_id"]:
            return item
        if predicate == "depends_on" and item["constraint_id"] is None:
            return item
    raise KeyError(predicate)


def verify_recorded_evidence(plan):
    if not RESULTS.exists():
        return "absent"
    recorded = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert recorded["environment"]["graphiti_core"] == "0.30.2", recorded["environment"]
    assert recorded["environment"]["llm"].startswith("none"), recorded["environment"]
    for name, scenario in recorded["scenarios"].items():
        side_table = dict(plan["side_table"])
        conformance = conformance_report(
            scenario["before"],
            scenario["after"],
            scenario["episodes_after"],
            side_table,
            scenario["snapshot"],
            scenario.get("introduced", ()),
        )
        assert conformance == scenario["conformance"], name
        admission = admission_projection(
            scenario["after"], scenario["snapshot"], side_table, plan["names"]
        )
        assert admission["dispositions"] == scenario["admission"]["dispositions"], name
        assert [item["assessment_id"] for item in admission["consistency"]] == [
            item["assessment_id"] for item in scenario["admission"]["consistency"]
        ], name
    return "verified"


def main():
    fixture = load_fixture()
    plan = translate_polaris(fixture)
    results = {}

    # Translation is deterministic and covers the fixture.
    assert json.dumps(plan, sort_keys=True) == json.dumps(translate_polaris(fixture), sort_keys=True)
    assert len(plan["episodes"]) == len(fixture["evidence"]) == 6
    assert len(plan["edges"]) == 8
    derived = [edge for edge in plan["edges"] if edge["attributes"]["ml_derivation"] == "derived"]
    assert len(derived) == 2
    for edge in derived:
        closure = {graphiti_uuid("episode:" + ref) for ref in edge["attributes"]["ml_evidence_refs"]}
        assert set(edge["episodes"]) == closure
    results["translation"] = "deterministic_six_episodes_eight_edges_derivation_type_preserved"

    blocked = plan_edge(plan, derived="blocked")
    ready = plan_edge(plan, derived="ready")
    sigma_blocked = plan_edge(plan, evidence_id="EV-SIGMA-BLOCKED-0400")
    sigma_clear = plan_edge(plan, evidence_id="EV-SIGMA-CLEAR-0401")
    sigma_dep = plan_edge(plan, evidence_id="EV-POLARIS-SIGMA-DEP")
    tau_dep = plan_edge(plan, evidence_id="EV-POLARIS-TAU-DEP")
    checks = plan_edge(plan, evidence_id="EV-POLARIS-CHECKS-0400")
    expected = expected_lane_assessments(fixture)
    side_table = plan["side_table"]
    names = plan["names"]
    clear_episode = graphiti_uuid("episode:EV-SIGMA-CLEAR-0401")

    # S0400: both status edges current in Graphiti. The projection reproduces
    # the existing lane's assessments exactly and writes nothing.
    s0400 = state(plan, drop={sigma_clear["uuid"]})
    frozen = copy.deepcopy(s0400)
    admission_0400 = admission_projection(s0400, "SYN-DM-0400", side_table, names)
    assert admission_is_read_only(frozen, s0400)["verdict"] == "pass"
    assert outcome(admission_0400, "status") == expected["conflict_0400"]
    assert outcome(admission_0400, "depends_on") == expected["multivalue_0400"]
    for item in admission_0400["consistency"]:
        validate(item, load_schema(CONSISTENCY_SCHEMA))
    for item in admission_0400["support"].values():
        validate(item, load_schema(JUSTIFICATION_ASSESSMENT_SCHEMA))
    validate(STATUS_CONSTRAINT, load_schema(CONSTRAINT_SCHEMA))
    assert admission_0400["dispositions"][blocked["uuid"]]["disposition"] == "withheld"
    assert admission_0400["dispositions"][ready["uuid"]]["disposition"] == "withheld"
    assert admission_0400["dispositions"][sigma_dep["uuid"]]["disposition"] == "admitted"
    results["projection_equivalence_0400"] = "identical_assessment_ids_to_native_conflict_lane"

    # S0401 as Graphiti records a world change: the old Sigma edge is closed
    # in place and the new edge (attributes cleared by native resolution) starts
    # at the closure time.
    clear_resolved = copy.deepcopy(sigma_clear)
    clear_resolved["attributes"] = {}
    s0401 = state(
        plan,
        updates={
            sigma_blocked["uuid"]: {
                "invalid_at": sigma_clear["valid_at"],
                "expired_at": "2026-09-14T00:00:00+00:00",
            },
            sigma_clear["uuid"]: {"attributes": {}},
        },
    )
    admission_0401 = admission_projection(s0401, "SYN-DM-0401", side_table, names)
    assert outcome(admission_0401, "status") == expected["resolved_0401"]
    assert admission_0401["support"][blocked["attributes"]["ml_record_id"]]["support_outcome"] == "withdrawn"
    assert adapter_attribute_loss(s0401) == [sigma_clear["uuid"]]
    world_change = conformance_report(
        s0400, s0401, episode_ids(plan), side_table, "SYN-DM-0401"
    )
    for key in (
        "EP-01_historical_preservation",
        "EP-02_provenance_closure",
        "EP-04_multiple_support",
        "EP-05_withdrawal_not_negation",
        "EP-07_support_vs_consistency",
        "EP-09_explicit_conflict_basis",
        "EP-10_world_change_vs_correction",
    ):
        assert world_change[key]["verdict"] == "pass", (key, world_change[key])
    results["world_change_0401"] = "resolved_by_support_change_all_checks_pass_via_side_table"

    # Recency collapse: conflicting supported claims rendered as succession.
    later = "2026-06-02T00:00:00+00:00"
    collapse = state(
        plan,
        drop={sigma_clear["uuid"]},
        updates={
            ready["uuid"]: {"valid_at": later},
            blocked["uuid"]: {"invalid_at": later, "expired_at": "2026-09-14T00:00:00+00:00"},
        },
    )
    collapse_before = state(plan, drop={sigma_clear["uuid"]}, updates={ready["uuid"]: {"valid_at": later}})
    report = conformance_report(
        collapse_before, collapse, episode_ids(plan, drop={clear_episode}), side_table, "SYN-DM-0400"
    )
    assert report["EP-07_support_vs_consistency"]["violations"] == [blocked["uuid"]]
    assert report["EP-10_world_change_vs_correction"]["violations"] == [blocked["uuid"]]
    assert report["EP-09_explicit_conflict_basis"]["verdict"] == "pass"
    laundered = admission_projection(collapse, "SYN-DM-0400", side_table, names)
    assert outcome(laundered, "status")["consistency_outcome"] == "compatible"
    results["recency_collapse"] = "conflict_rendered_as_succession_detected_by_EP07_EP10"

    # Multi-valued over-invalidation (Graphiti issue #1728 shape) cascades into
    # a false resolution of the status conflict.
    over = state(
        plan,
        drop={sigma_clear["uuid"]},
        updates={
            tau_dep["uuid"]: {"valid_at": later},
            sigma_dep["uuid"]: {"invalid_at": later, "expired_at": "2026-09-14T00:00:00+00:00"},
        },
    )
    over_before = state(plan, drop={sigma_clear["uuid"]}, updates={tau_dep["uuid"]: {"valid_at": later}})
    report = conformance_report(
        over_before, over, episode_ids(plan, drop={clear_episode}), side_table, "SYN-DM-0400"
    )
    assert report["EP-09_explicit_conflict_basis"]["violations"] == [sigma_dep["uuid"]]
    cascade = admission_projection(over, "SYN-DM-0400", side_table, names)
    assert outcome(cascade, "status")["consistency_outcome"] == "resolved_by_support_change"
    assert outcome(cascade, "status")["selected_record_ids"] == [ready["attributes"]["ml_record_id"]]
    results["multivalue_over_invalidation"] = "unconstrained_invalidation_detected_and_false_resolution_exposed"

    # Deleting the first supporting episode removes a corroborated fact.
    second_episode = graphiti_uuid("episode:EV-POLARIS-CHECKS-RESTATED")
    corroborated = state(
        plan,
        drop={sigma_clear["uuid"]},
        updates={checks["uuid"]: {"episodes": checks["episodes"] + [second_episode]}},
    )
    first_episode = checks["episodes"][0]
    deleted = [edge for edge in corroborated if edge["uuid"] != checks["uuid"]]
    live = sorted(set(episode_ids(plan, drop={clear_episode, first_episode})) | {second_episode})
    report = conformance_report(corroborated, deleted, live, side_table, "SYN-DM-0400")
    assert report["EP-01_historical_preservation"]["violations"] == [checks["uuid"]]
    assert report["EP-04_multiple_support"]["violations"] == [checks["uuid"]]
    false_resolution = admission_projection(deleted, "SYN-DM-0400", side_table, names)
    assert outcome(false_resolution, "status")["selected_record_ids"] == [blocked["attributes"]["ml_record_id"]]
    results["deletion_as_withdrawal"] = "surviving_support_deleted_detected_by_EP01_EP04"

    # Removing the corroborating episode leaves a dangling provenance reference.
    dangling = conformance_report(
        corroborated,
        corroborated,
        sorted(set(episode_ids(plan, drop={clear_episode}))),
        side_table,
        "SYN-DM-0400",
    )
    assert dangling["EP-02_provenance_closure"]["violations"] == [checks["uuid"]]
    results["dangling_provenance"] = "detected_by_EP02"

    results["live_evidence"] = verify_recorded_evidence(plan)

    output = {
        "status": "passed",
        "mode": "graphiti substitution adapter for derived-conflict-v0 (Memory-Lab-owned behavior)",
        "results": results,
        "research_findings": {
            "projection_fidelity": "Graphiti-shaped edge state carries enough to reproduce the native conflict lane's assessments byte-for-byte",
            "admission_is_projection": "current-view admission is computed without writing to Graphiti",
            "conformance_detects_collapse": "recency invalidation, unconstrained invalidation, and deletion-as-withdrawal are each detected by an ML-EP-0 check",
        },
        "not_validated": [
            "what a real LLM would judge as contradictory",
            "Graphiti hybrid search ranking",
            "production Graphiti backends (Neo4j, FalkorDB)",
            "coverage semantics",
            "private or real corpora",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"GRAPHITI_ADAPTER_V0_FAIL: {exc}", file=sys.stderr)
        raise

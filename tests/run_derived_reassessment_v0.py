#!/usr/bin/env python3
import copy
import hashlib
import json
import pathlib
import sys

from run_contract_schema_validation import load_schema, validate, SchemaError
from run_derived_memory_adversarial import (
    RECORD_SCHEMA,
    apply_support,
    evidence_map,
    record,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "derived-reassessment-v0" / "evidence.json"
PLAN_SCHEMA = "derived-reassessment-plan-v0.schema.json"
RESULT_SCHEMA = "derived-reassessment-result-v0.schema.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def artifact_id(prefix, payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return prefix + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def reverse_dependencies(records):
    reverse = {record_id: [] for record_id in records}
    for child_id, item in records.items():
        for parent_id in item.get("derived_from_records", []):
            reverse.setdefault(parent_id, []).append(child_id)
    for children in reverse.values():
        children.sort()
    return reverse


def dependency_distances(records, trigger_ids):
    reverse = reverse_dependencies(records)
    distance = {record_id: 0 for record_id in trigger_ids}
    queue = list(sorted(trigger_ids))
    while queue:
        parent_id = queue.pop(0)
        parent_distance = distance[parent_id]
        for child_id in reverse.get(parent_id, []):
            new_distance = parent_distance + 1
            if child_id not in distance or new_distance < distance[child_id]:
                distance[child_id] = new_distance
                queue.append(child_id)
    return distance


def build_plan(records, trigger_ids, from_snapshot, to_snapshot):
    trigger_ids = sorted(trigger_ids)
    distances = dependency_distances(records, trigger_ids)
    direct = sorted(record_id for record_id, d in distances.items() if d == 1)
    transitive = sorted(record_id for record_id, d in distances.items() if d > 1)
    evaluation_order = sorted(distances, key=lambda record_id: (distances[record_id], record_id))
    affected = set(evaluation_order)
    unaffected = sorted(set(records) - affected)
    payload = {
        "from_snapshot": from_snapshot,
        "to_snapshot": to_snapshot,
        "trigger_record_ids": trigger_ids,
        "directly_affected_record_ids": direct,
        "transitively_affected_record_ids": transitive,
        "evaluation_order": evaluation_order,
        "unaffected_record_ids": unaffected,
    }
    return {
        "schema": "derived-reassessment-plan-v0",
        "plan_id": artifact_id("RP-", payload),
        "status": "planned",
        **payload,
    }


def result_id(plan_id, record_id, support_outcome, replacement_ids):
    return artifact_id("RR-", [plan_id, record_id, support_outcome, sorted(replacement_ids)])


def reassess(plan, records, replacement_by_trigger):
    results = []
    historical = set()

    for record_id in plan["evaluation_order"]:
        item = records[record_id]
        replacement_ids = replacement_by_trigger.get(record_id, [])
        if record_id in plan["trigger_record_ids"]:
            if replacement_ids:
                support_outcome = "replaced"
                resulting_view = "historical_only"
                note = "New evidence replaces this direct support record in the current view."
            else:
                support_outcome = "withdrawn"
                resulting_view = "historical_only"
                note = "Trigger support was withdrawn without a replacement proposition."
            historical.add(record_id)
        else:
            invalid_parent = any(
                parent_id in historical for parent_id in item.get("derived_from_records", [])
            )
            if invalid_parent:
                support_outcome = "withdrawn"
                resulting_view = "historical_only"
                note = (
                    "At least one required derived dependency is no longer active; "
                    "support is withdrawn without inferring the opposite proposition."
                )
                historical.add(record_id)
            else:
                support_outcome = "retained"
                resulting_view = "active"
                note = "All required direct dependencies remain active."

        result = {
            "schema": "derived-reassessment-result-v0",
            "result_id": result_id(
                plan["plan_id"], record_id, support_outcome, replacement_ids
            ),
            "plan_id": plan["plan_id"],
            "record_id": record_id,
            "assessed_at_snapshot": plan["to_snapshot"],
            "prior_status": item["status"],
            "support_outcome": support_outcome,
            "resulting_view": resulting_view,
            "trigger_record_ids": list(plan["trigger_record_ids"]),
            "replacement_record_ids": list(replacement_ids),
            "note": note,
        }
        results.append(result)

    return results


def validate_artifact(artifact, schema_name):
    validate(artifact, load_schema(schema_name))


def expect_schema_rejection(artifact, schema_name, fragment):
    try:
        validate_artifact(artifact, schema_name)
    except SchemaError as exc:
        assert fragment in str(exc), (fragment, str(exc))
        return str(exc)
    raise AssertionError("expected schema rejection")


def main():
    fixture = load_fixture()
    evidence = evidence_map(fixture)
    records = {}
    report_results = {}

    vega_dependency = record(
        "relationship",
        "Project Vega",
        "depends_on",
        "Module Sigma",
        ["EV-VEGA-DEP-0200"],
        "SYN-DM-0200",
    )
    vega_dependency, _ = apply_support(vega_dependency, evidence, records)
    records[vega_dependency["record_id"]] = vega_dependency

    sigma_blocked = record(
        "state",
        "Module Sigma",
        "status",
        "blocked",
        ["EV-SIGMA-BLOCKED-0200"],
        "SYN-DM-0200",
    )
    sigma_blocked, _ = apply_support(sigma_blocked, evidence, records)
    records[sigma_blocked["record_id"]] = sigma_blocked

    vega_blocked = record(
        "state",
        "Project Vega",
        "status",
        "blocked",
        ["EV-VEGA-DEP-0200", "EV-SIGMA-BLOCKED-0200"],
        "SYN-DM-0200",
        derived_from_records=[
            vega_dependency["record_id"],
            sigma_blocked["record_id"],
        ],
        derivation_rule="dependency_block_propagation",
    )
    vega_blocked, _ = apply_support(vega_blocked, evidence, records)
    records[vega_blocked["record_id"]] = vega_blocked

    helios_dependency = record(
        "relationship",
        "Project Helios",
        "depends_on",
        "Project Vega",
        ["EV-HELIOS-DEP-0200"],
        "SYN-DM-0200",
    )
    helios_dependency, _ = apply_support(helios_dependency, evidence, records)
    records[helios_dependency["record_id"]] = helios_dependency

    helios_blocked = record(
        "state",
        "Project Helios",
        "status",
        "blocked",
        [
            "EV-HELIOS-DEP-0200",
            "EV-VEGA-DEP-0200",
            "EV-SIGMA-BLOCKED-0200",
        ],
        "SYN-DM-0200",
        derived_from_records=[
            helios_dependency["record_id"],
            vega_blocked["record_id"],
        ],
        derivation_rule="dependency_block_propagation",
    )
    helios_blocked, _ = apply_support(helios_blocked, evidence, records)
    records[helios_blocked["record_id"]] = helios_blocked

    for item in records.values():
        validate_artifact(item, RECORD_SCHEMA)
        assert item["status"] == "verified"

    historical_before = json.dumps(records, sort_keys=True)

    sigma_clear = record(
        "state",
        "Module Sigma",
        "status",
        "clear",
        ["EV-SIGMA-CLEAR-0201"],
        "SYN-DM-0201",
        change_kind="world_state_changed",
    )
    sigma_clear, _ = apply_support(sigma_clear, evidence, records)
    validate_artifact(sigma_clear, RECORD_SCHEMA)
    assert sigma_clear["status"] == "verified"

    plan = build_plan(
        records,
        [sigma_blocked["record_id"]],
        "SYN-DM-0200",
        "SYN-DM-0201",
    )
    validate_artifact(plan, PLAN_SCHEMA)

    expected_order = [
        sigma_blocked["record_id"],
        vega_blocked["record_id"],
        helios_blocked["record_id"],
    ]
    assert plan["evaluation_order"] == expected_order
    assert plan["directly_affected_record_ids"] == [vega_blocked["record_id"]]
    assert plan["transitively_affected_record_ids"] == [helios_blocked["record_id"]]
    assert set(plan["unaffected_record_ids"]) == {
        vega_dependency["record_id"],
        helios_dependency["record_id"],
    }
    report_results["minimal_dependency_closure"] = "direct_and_transitive_dependents_only"

    replay = build_plan(
        records,
        [sigma_blocked["record_id"]],
        "SYN-DM-0200",
        "SYN-DM-0201",
    )
    assert replay == plan
    report_results["deterministic_reassessment_plan"] = "exact_replay_identity"

    results = reassess(
        plan,
        records,
        {sigma_blocked["record_id"]: [sigma_clear["record_id"]]},
    )
    for item in results:
        validate_artifact(item, RESULT_SCHEMA)

    by_record = {item["record_id"]: item for item in results}
    assert by_record[sigma_blocked["record_id"]]["support_outcome"] == "replaced"
    assert by_record[sigma_blocked["record_id"]]["replacement_record_ids"] == [
        sigma_clear["record_id"]
    ]
    assert by_record[vega_blocked["record_id"]]["support_outcome"] == "withdrawn"
    assert by_record[helios_blocked["record_id"]]["support_outcome"] == "withdrawn"
    assert by_record[vega_blocked["record_id"]]["replacement_record_ids"] == []
    assert by_record[helios_blocked["record_id"]]["replacement_record_ids"] == []
    report_results["support_withdrawal_propagation"] = "parent_then_child_reassessment"

    current_records = list(records.values()) + [sigma_clear]
    invented_opposites = [
        item
        for item in current_records
        if item["record_type"] == "state"
        and item["subject"] in {"Project Vega", "Project Helios"}
        and item["object"] == "clear"
    ]
    assert invented_opposites == []
    report_results["no_opposite_hallucination"] = "withdrawn_support_does_not_infer_clear"

    historical_after = json.dumps(records, sort_keys=True)
    assert historical_before == historical_after
    report_results["historical_records_immutable"] = "reassessment_is_append_only"

    bad_plan = copy.deepcopy(plan)
    del bad_plan["evaluation_order"]
    report_results["malformed_plan_rejected"] = expect_schema_rejection(
        bad_plan, PLAN_SCHEMA, "missing required key"
    )
    bad_result = copy.deepcopy(results[0])
    bad_result["support_outcome"] = "magically_true"
    report_results["malformed_result_rejected"] = expect_schema_rejection(
        bad_result, RESULT_SCHEMA, "expected one of"
    )

    output = {
        "status": "passed",
        "mode": "dependency-aware derived-memory reassessment",
        "results": report_results,
        "research_findings": {
            "targeted_reassessment": "new support changes trigger only dependency descendants rather than global recomputation",
            "topological_order": "support providers are reassessed before conclusions that depend on them",
            "withdrawal_is_not_negation": "loss of a justification removes a conclusion from the current view but does not prove its opposite",
            "history_is_append_only": "historical derived records remain unchanged; reassessment results describe the newer current view",
        },
        "not_validated": [
            "multiple independent justifications for one semantic record",
            "general rule engines",
            "automatic trigger discovery from real retrieval/index deltas",
            "private corpus scale",
            "incremental persistent graph storage",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"DERIVED_REASSESSMENT_V0_FAIL: {exc}", file=sys.stderr)
        raise

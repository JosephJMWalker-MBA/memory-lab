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
    stable_id,
)
from run_multiple_justifications_v0 import (
    SET_SCHEMA,
    justification,
    justification_set,
    stable_artifact_id,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "derived-conflict-v0" / "evidence.json"
V02_SCHEMA = "derived-memory-record-v0.2.schema.json"
CONSTRAINT_SCHEMA = "derived-predicate-constraint-v0.schema.json"
CONSISTENCY_SCHEMA = "derived-consistency-assessment-v0.schema.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def constraint_id(payload):
    return stable_artifact_id("PC-", payload)


def predicate_constraint(record_type, predicate):
    payload = {
        "record_type": record_type,
        "predicate": predicate,
        "value_cardinality": "single_value_per_scope",
        "qualifier_matching": "exact",
        "temporal_rule": "overlap_required",
    }
    return {
        "schema": "derived-predicate-constraint-v0",
        "constraint_id": constraint_id(payload),
        **payload,
    }


def derived_record(
    record_id,
    subject,
    predicate,
    obj,
    qualifiers,
    evidence_refs,
    parent_ids,
    set_id,
    snapshot_id,
    rule_note,
    valid_time,
):
    return {
        "schema": "derived-memory-record-v0.2",
        "record_id": record_id,
        "record_type": "state",
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "qualifiers": dict(qualifiers),
        "evidence_refs": sorted(evidence_refs),
        "derived_from_records": sorted(parent_ids),
        "support_semantics": "alternative_justifications",
        "justification_set_id": set_id,
        "source_snapshot_id": snapshot_id,
        "status": "verified",
        "change_kind": "initial",
        "attribution_check": {
            "outcome": "supported",
            "checked_evidence_refs": sorted(evidence_refs),
            "checked_derived_records": sorted(parent_ids),
            "reason_code": "alternative_justification_support",
            "note": rule_note,
        },
        "valid_time": dict(valid_time),
        "knowledge_time": {
            "first_known_snapshot": snapshot_id,
            "last_assessed_snapshot": snapshot_id,
        },
    }


def interval_overlap(left, right):
    left_start = left.get("from")
    left_end = left.get("to")
    right_start = right.get("from")
    right_end = right.get("to")

    if left_start is None or right_start is None:
        return True
    if left_end is not None and right_start >= left_end:
        return False
    if right_end is not None and left_start >= right_end:
        return False
    return True


def records_conflict(left, right, constraint):
    if constraint is None:
        return False
    if constraint["value_cardinality"] != "single_value_per_scope":
        return False
    if left["record_type"] != constraint["record_type"]:
        return False
    if right["record_type"] != constraint["record_type"]:
        return False
    if left["predicate"] != constraint["predicate"]:
        return False
    if right["predicate"] != constraint["predicate"]:
        return False
    if left["subject"] != right["subject"]:
        return False
    if left["object"] == right["object"]:
        return False
    if constraint["qualifier_matching"] == "exact":
        if left["qualifiers"] != right["qualifiers"]:
            return False
    if constraint["temporal_rule"] == "overlap_required":
        if not interval_overlap(left.get("valid_time", {}), right.get("valid_time", {})):
            return False
    return True


def consistency_id(payload):
    return stable_artifact_id("CA-", payload)


def assess_consistency(records, supported_ids, snapshot_id, constraint=None):
    record_ids = sorted(item["record_id"] for item in records)
    supported = sorted(set(record_ids) & set(supported_ids))
    unsupported = sorted(set(record_ids) - set(supported))
    by_id = {item["record_id"]: item for item in records}
    active_records = [by_id[record_id] for record_id in supported]

    conflicting_ids = set()
    if constraint is not None:
        for index, left in enumerate(active_records):
            for right in active_records[index + 1 :]:
                if records_conflict(left, right, constraint):
                    conflicting_ids.update([left["record_id"], right["record_id"]])

    if conflicting_ids:
        consistency_outcome = "unresolved_conflict"
        current_view_outcome = "withhold_conflicting_supported"
        selected = sorted(set(supported) - conflicting_ids)
        reason_code = "exclusive_values_overlap"
        note = (
            "Individually supported records violate an explicit exclusivity "
            "constraint; no conflicting record is selected automatically."
        )
    elif unsupported and len(supported) == 1 and constraint is not None:
        consistency_outcome = "resolved_by_support_change"
        current_view_outcome = "allow_surviving_supported"
        selected = supported
        reason_code = "support_change_removed_conflict"
        note = (
            "The prior conflict disappeared because one proposition lost support; "
            "the surviving supported record may return to the current view."
        )
    else:
        consistency_outcome = "compatible"
        current_view_outcome = "allow_all_supported"
        selected = supported
        reason_code = "no_exclusivity_constraint"
        note = "No explicit exclusivity constraint makes these supported records incompatible."

    payload = {
        "constraint_id": constraint["constraint_id"] if constraint else None,
        "record_ids": record_ids,
        "assessed_at_snapshot": snapshot_id,
        "supported_record_ids": supported,
        "unsupported_record_ids": unsupported,
        "consistency_outcome": consistency_outcome,
        "current_view_outcome": current_view_outcome,
        "selected_record_ids": selected,
        "reason_code": reason_code,
    }
    return {
        "schema": "derived-consistency-assessment-v0",
        "assessment_id": consistency_id(payload),
        **payload,
        "note": note,
    }


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
    base = {}
    results = {}

    qualifiers = {"environment": "production"}
    valid_time = {"from": "2026-06-01", "to": None}

    sigma_dep = record(
        "relationship",
        "Project Polaris",
        "depends_on",
        "Module Sigma",
        ["EV-POLARIS-SIGMA-DEP"],
        "SYN-DM-0400",
        qualifiers=qualifiers,
    )
    sigma_dep, _ = apply_support(sigma_dep, evidence, base)
    base[sigma_dep["record_id"]] = sigma_dep

    sigma_blocked = record(
        "state",
        "Module Sigma",
        "status",
        "blocked",
        ["EV-SIGMA-BLOCKED-0400"],
        "SYN-DM-0400",
        qualifiers=qualifiers,
    )
    sigma_blocked, _ = apply_support(sigma_blocked, evidence, base)
    base[sigma_blocked["record_id"]] = sigma_blocked

    checks = record(
        "state",
        "Project Polaris",
        "release_checks",
        "passed",
        ["EV-POLARIS-CHECKS-0400"],
        "SYN-DM-0400",
        qualifiers=qualifiers,
    )
    checks, _ = apply_support(checks, evidence, base)
    base[checks["record_id"]] = checks

    approval = record(
        "state",
        "Project Polaris",
        "release_approval",
        "granted",
        ["EV-POLARIS-APPROVAL-0400"],
        "SYN-DM-0400",
        qualifiers=qualifiers,
    )
    approval, _ = apply_support(approval, evidence, base)
    base[approval["record_id"]] = approval

    tau_dep = record(
        "relationship",
        "Project Polaris",
        "depends_on",
        "Module Tau",
        ["EV-POLARIS-TAU-DEP"],
        "SYN-DM-0400",
        qualifiers=qualifiers,
    )
    tau_dep, _ = apply_support(tau_dep, evidence, base)
    base[tau_dep["record_id"]] = tau_dep

    for item in base.values():
        validate_artifact(item, RECORD_SCHEMA)
        assert item["status"] == "verified"

    blocked_id = stable_id(
        "state",
        "Project Polaris",
        "status",
        "blocked",
        qualifiers,
        valid_time["from"],
        "SYN-DM-0400",
    )
    blocked_j = justification(
        "dependency_block_propagation",
        [sigma_dep["record_id"], sigma_blocked["record_id"]],
        ["EV-POLARIS-SIGMA-DEP", "EV-SIGMA-BLOCKED-0400"],
    )
    blocked_set = justification_set(blocked_id, [blocked_j])
    validate_artifact(blocked_set, SET_SCHEMA)
    blocked = derived_record(
        blocked_id,
        "Project Polaris",
        "status",
        "blocked",
        qualifiers,
        ["EV-POLARIS-SIGMA-DEP", "EV-SIGMA-BLOCKED-0400"],
        [sigma_dep["record_id"], sigma_blocked["record_id"]],
        blocked_set["justification_set_id"],
        "SYN-DM-0400",
        "Dependency on blocked Sigma supports the blocked status.",
        valid_time,
    )
    validate_artifact(blocked, V02_SCHEMA)

    ready_id = stable_id(
        "state",
        "Project Polaris",
        "status",
        "ready",
        qualifiers,
        valid_time["from"],
        "SYN-DM-0400",
    )
    ready_j = justification(
        "release_ready_propagation",
        [checks["record_id"], approval["record_id"]],
        ["EV-POLARIS-CHECKS-0400", "EV-POLARIS-APPROVAL-0400"],
    )
    ready_set = justification_set(ready_id, [ready_j])
    validate_artifact(ready_set, SET_SCHEMA)
    ready = derived_record(
        ready_id,
        "Project Polaris",
        "status",
        "ready",
        qualifiers,
        ["EV-POLARIS-CHECKS-0400", "EV-POLARIS-APPROVAL-0400"],
        [checks["record_id"], approval["record_id"]],
        ready_set["justification_set_id"],
        "SYN-DM-0400",
        "Passed checks plus release approval support the ready status.",
        valid_time,
    )
    validate_artifact(ready, V02_SCHEMA)

    # Both propositions are individually support-verified.
    assert blocked["status"] == ready["status"] == "verified"
    results["individual_support"] = "blocked_and_ready_both_support_verified"

    status_constraint = predicate_constraint("state", "status")
    validate_artifact(status_constraint, CONSTRAINT_SCHEMA)

    conflict = assess_consistency(
        [blocked, ready],
        {blocked["record_id"], ready["record_id"]},
        "SYN-DM-0400",
        status_constraint,
    )
    validate_artifact(conflict, CONSISTENCY_SCHEMA)
    assert conflict["consistency_outcome"] == "unresolved_conflict"
    assert conflict["current_view_outcome"] == "withhold_conflicting_supported"
    assert conflict["selected_record_ids"] == []
    results["supported_conflict"] = "both_preserved_no_arbitrary_winner"

    # Different values on a multi-valued relation are not contradictions merely
    # because their subject/predicate match.
    relation_compatibility = assess_consistency(
        [sigma_dep, tau_dep],
        {sigma_dep["record_id"], tau_dep["record_id"]},
        "SYN-DM-0400",
        constraint=None,
    )
    validate_artifact(relation_compatibility, CONSISTENCY_SCHEMA)
    assert relation_compatibility["consistency_outcome"] == "compatible"
    assert set(relation_compatibility["selected_record_ids"]) == {
        sigma_dep["record_id"],
        tau_dep["record_id"],
    }
    results["multivalue_relation"] = "different_depends_on_objects_remain_compatible"

    # New evidence clears Sigma. The historical blocked record is unchanged but
    # no longer supported in the current projection; ready remains supported.
    sigma_clear = record(
        "state",
        "Module Sigma",
        "status",
        "clear",
        ["EV-SIGMA-CLEAR-0401"],
        "SYN-DM-0401",
        qualifiers=qualifiers,
        change_kind="world_state_changed",
    )
    sigma_clear, _ = apply_support(sigma_clear, evidence, base)
    validate_artifact(sigma_clear, RECORD_SCHEMA)

    resolved = assess_consistency(
        [blocked, ready],
        {ready["record_id"]},
        "SYN-DM-0401",
        status_constraint,
    )
    validate_artifact(resolved, CONSISTENCY_SCHEMA)
    assert resolved["consistency_outcome"] == "resolved_by_support_change"
    assert resolved["current_view_outcome"] == "allow_surviving_supported"
    assert resolved["selected_record_ids"] == [ready["record_id"]]
    assert resolved["unsupported_record_ids"] == [blocked["record_id"]]
    results["conflict_resolution"] = "support_change_resolves_without_ranking"

    # Historical support-verified records are not rewritten by consistency
    # assessment; support and consistency are separate dimensions.
    assert blocked["status"] == "verified"
    assert ready["status"] == "verified"
    results["support_vs_consistency"] = "record_support_status_preserved_separately"

    bad_constraint = copy.deepcopy(status_constraint)
    bad_constraint["value_cardinality"] = "sometimes_single"
    results["bad_constraint_rejected"] = expect_schema_rejection(
        bad_constraint, CONSTRAINT_SCHEMA, "expected one of"
    )

    bad_assessment = copy.deepcopy(conflict)
    bad_assessment["selected_record_ids"] = ["not-a-record-id"]
    results["bad_consistency_record_id_rejected"] = expect_schema_rejection(
        bad_assessment, CONSISTENCY_SCHEMA, "does not match pattern"
    )

    output = {
        "status": "passed",
        "mode": "derived-memory conflict and consistency semantics",
        "results": results,
        "research_findings": {
            "support_vs_consistency": "individual evidentiary support does not imply joint consistency",
            "constraint_required": "different values conflict only under an explicit exclusivity constraint in matching scope/time",
            "no_arbitrary_winner": "simultaneously supported incompatible records are preserved while the current view withholds them",
            "resolution_by_support_change": "a conflict can resolve when one proposition loses support without source ranking or historical rewriting",
        },
        "not_validated": [
            "source-authority adjudication",
            "probabilistic conflict resolution",
            "partial qualifier compatibility",
            "complex temporal overlap policies",
            "automatic predicate-constraint discovery",
            "private corpus behavior",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"DERIVED_CONFLICT_V0_FAIL: {exc}", file=sys.stderr)
        raise

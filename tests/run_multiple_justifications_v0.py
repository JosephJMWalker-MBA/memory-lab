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
from run_derived_reassessment_v0 import build_plan


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "multiple-justifications-v0" / "evidence.json"
V02_SCHEMA = "derived-memory-record-v0.2.schema.json"
SET_SCHEMA = "derived-justification-set-v0.schema.json"
ASSESSMENT_SCHEMA = "derived-justification-assessment-v0.schema.json"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def stable_artifact_id(prefix, payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return prefix + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def justification(rule, parent_ids, evidence_refs):
    payload = {
        "derivation_rule": rule,
        "derived_record_refs": sorted(parent_ids),
        "evidence_refs": sorted(evidence_refs),
    }
    return {
        "justification_id": stable_artifact_id("JX-", payload),
        **payload,
    }


def justification_set(record_id, justifications):
    ordered = sorted(justifications, key=lambda item: item["justification_id"])
    payload = {
        "record_id": record_id,
        "semantics": "any_satisfied_justification_supports_record",
        "justifications": ordered,
    }
    return {
        "schema": "derived-justification-set-v0",
        "justification_set_id": stable_artifact_id("JS-", payload),
        **payload,
    }


def multi_record(record_id, parent_ids, evidence_refs, set_id):
    return {
        "schema": "derived-memory-record-v0.2",
        "record_id": record_id,
        "record_type": "state",
        "subject": "Project Aurora",
        "predicate": "status",
        "object": "blocked",
        "qualifiers": {},
        "evidence_refs": sorted(evidence_refs),
        "derived_from_records": sorted(parent_ids),
        "support_semantics": "alternative_justifications",
        "justification_set_id": set_id,
        "source_snapshot_id": "SYN-DM-0300",
        "status": "verified",
        "change_kind": "initial",
        "attribution_check": {
            "outcome": "supported",
            "checked_evidence_refs": sorted(evidence_refs),
            "checked_derived_records": sorted(parent_ids),
            "reason_code": "alternative_justification_support",
            "note": "At least one explicit justification environment supports this proposition.",
        },
        "knowledge_time": {
            "first_known_snapshot": "SYN-DM-0300",
            "last_assessed_snapshot": "SYN-DM-0300",
        },
    }


def assess(set_artifact, active_record_ids, snapshot_id):
    active_record_ids = set(active_record_ids)
    active = []
    inactive = []
    for item in set_artifact["justifications"]:
        parents = set(item["derived_record_refs"])
        if parents <= active_record_ids:
            active.append(item["justification_id"])
        else:
            inactive.append(item["justification_id"])

    support_outcome = "retained" if active else "withdrawn"
    resulting_view = "active" if active else "historical_only"
    payload = {
        "justification_set_id": set_artifact["justification_set_id"],
        "record_id": set_artifact["record_id"],
        "assessed_at_snapshot": snapshot_id,
        "active_justification_ids": sorted(active),
        "inactive_justification_ids": sorted(inactive),
        "support_outcome": support_outcome,
        "resulting_view": resulting_view,
    }
    return {
        "schema": "derived-justification-assessment-v0",
        "assessment_id": stable_artifact_id("JA-", payload),
        **payload,
        "note": (
            "At least one independent justification remains satisfied."
            if active
            else "No independent justification remains satisfied."
        ),
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
    records = {}
    results = {}

    sigma_dep = record(
        "relationship",
        "Project Aurora",
        "depends_on",
        "Module Sigma",
        ["EV-AURORA-SIGMA-DEP"],
        "SYN-DM-0300",
    )
    sigma_dep, _ = apply_support(sigma_dep, evidence, records)
    records[sigma_dep["record_id"]] = sigma_dep

    sigma_blocked = record(
        "state",
        "Module Sigma",
        "status",
        "blocked",
        ["EV-SIGMA-BLOCKED-0300"],
        "SYN-DM-0300",
    )
    sigma_blocked, _ = apply_support(sigma_blocked, evidence, records)
    records[sigma_blocked["record_id"]] = sigma_blocked

    tau_dep = record(
        "relationship",
        "Project Aurora",
        "depends_on",
        "Module Tau",
        ["EV-AURORA-TAU-DEP"],
        "SYN-DM-0300",
    )
    tau_dep, _ = apply_support(tau_dep, evidence, records)
    records[tau_dep["record_id"]] = tau_dep

    tau_blocked = record(
        "state",
        "Module Tau",
        "status",
        "blocked",
        ["EV-TAU-BLOCKED-0300"],
        "SYN-DM-0300",
    )
    tau_blocked, _ = apply_support(tau_blocked, evidence, records)
    records[tau_blocked["record_id"]] = tau_blocked

    for item in records.values():
        validate_artifact(item, RECORD_SCHEMA)
        assert item["status"] == "verified"

    aurora_id = stable_id(
        "state", "Project Aurora", "status", "blocked", {}, None, "SYN-DM-0300"
    )

    j_sigma = justification(
        "dependency_block_propagation",
        [sigma_dep["record_id"], sigma_blocked["record_id"]],
        ["EV-AURORA-SIGMA-DEP", "EV-SIGMA-BLOCKED-0300"],
    )
    j_tau = justification(
        "dependency_block_propagation",
        [tau_dep["record_id"], tau_blocked["record_id"]],
        ["EV-AURORA-TAU-DEP", "EV-TAU-BLOCKED-0300"],
    )
    support_set = justification_set(aurora_id, [j_sigma, j_tau])
    validate_artifact(support_set, SET_SCHEMA)

    aurora = multi_record(
        aurora_id,
        [
            sigma_dep["record_id"],
            sigma_blocked["record_id"],
            tau_dep["record_id"],
            tau_blocked["record_id"],
        ],
        [
            "EV-AURORA-SIGMA-DEP",
            "EV-SIGMA-BLOCKED-0300",
            "EV-AURORA-TAU-DEP",
            "EV-TAU-BLOCKED-0300",
        ],
        support_set["justification_set_id"],
    )
    validate_artifact(aurora, V02_SCHEMA)
    records[aurora["record_id"]] = aurora

    record_before = json.dumps(aurora, sort_keys=True)
    support_before = json.dumps(support_set, sort_keys=True)

    # Initial state: both alternative justifications are active.
    initial = assess(support_set, records.keys(), "SYN-DM-0300")
    validate_artifact(initial, ASSESSMENT_SCHEMA)
    assert len(initial["active_justification_ids"]) == 2
    assert initial["support_outcome"] == "retained"
    results["initial_alternative_support"] = "two_active_justifications"

    # Sigma changes. The dependency closure correctly marks Aurora as affected,
    # but its current-view outcome must be retained because Tau still supports it.
    plan_sigma = build_plan(
        records,
        [sigma_blocked["record_id"]],
        "SYN-DM-0300",
        "SYN-DM-0301",
    )
    assert aurora["record_id"] in plan_sigma["directly_affected_record_ids"]

    sigma_clear = record(
        "state",
        "Module Sigma",
        "status",
        "clear",
        ["EV-SIGMA-CLEAR-0301"],
        "SYN-DM-0301",
        change_kind="world_state_changed",
    )
    sigma_clear, _ = apply_support(sigma_clear, evidence, records)
    validate_artifact(sigma_clear, RECORD_SCHEMA)

    active_0301 = (set(records) - {sigma_blocked["record_id"]}) | {
        sigma_clear["record_id"]
    }
    after_sigma = assess(support_set, active_0301, "SYN-DM-0301")
    validate_artifact(after_sigma, ASSESSMENT_SCHEMA)
    assert after_sigma["support_outcome"] == "retained"
    assert after_sigma["resulting_view"] == "active"
    assert after_sigma["active_justification_ids"] == [j_tau["justification_id"]]
    assert after_sigma["inactive_justification_ids"] == [j_sigma["justification_id"]]
    results["single_path_failure"] = "record_retained_by_independent_tau_path"

    # Tau later changes too. Only now are all independent justifications gone.
    plan_tau = build_plan(
        records,
        [tau_blocked["record_id"]],
        "SYN-DM-0301",
        "SYN-DM-0302",
    )
    assert aurora["record_id"] in plan_tau["directly_affected_record_ids"]

    tau_clear = record(
        "state",
        "Module Tau",
        "status",
        "clear",
        ["EV-TAU-CLEAR-0302"],
        "SYN-DM-0302",
        change_kind="world_state_changed",
    )
    tau_clear, _ = apply_support(tau_clear, evidence, records)
    validate_artifact(tau_clear, RECORD_SCHEMA)

    active_0302 = (
        set(records)
        - {sigma_blocked["record_id"], tau_blocked["record_id"]}
    ) | {sigma_clear["record_id"], tau_clear["record_id"]}
    after_tau = assess(support_set, active_0302, "SYN-DM-0302")
    validate_artifact(after_tau, ASSESSMENT_SCHEMA)
    assert after_tau["support_outcome"] == "withdrawn"
    assert after_tau["resulting_view"] == "historical_only"
    assert after_tau["active_justification_ids"] == []
    assert set(after_tau["inactive_justification_ids"]) == {
        j_sigma["justification_id"],
        j_tau["justification_id"],
    }
    results["all_paths_failed"] = "record_withdrawn_only_after_last_justification_failed"

    # Support-path changes do not mint a new semantic record.
    assert aurora["record_id"] == aurora_id
    results["semantic_identity_stable"] = "support_changes_do_not_change_record_id"

    # Nor do they mutate the historical record or justification structure.
    assert json.dumps(aurora, sort_keys=True) == record_before
    assert json.dumps(support_set, sort_keys=True) == support_before
    results["support_history_immutable"] = "record_and_justification_set_unchanged"

    # Loss of every blocked justification still does not prove Aurora is clear.
    all_records = list(records.values()) + [sigma_clear, tau_clear]
    invented = [
        item
        for item in all_records
        if item["record_type"] == "state"
        and item["subject"] == "Project Aurora"
        and item["object"] == "clear"
    ]
    assert invented == []
    results["no_negation_from_support_loss"] = "aurora_clear_not_invented"

    bad_record = copy.deepcopy(aurora)
    del bad_record["support_semantics"]
    results["missing_support_semantics_rejected"] = expect_schema_rejection(
        bad_record, V02_SCHEMA, "missing required key"
    )

    bad_set = copy.deepcopy(support_set)
    bad_set["semantics"] = "all_justifications_required"
    results["wrong_set_semantics_rejected"] = expect_schema_rejection(
        bad_set, SET_SCHEMA, "expected const"
    )

    bad_assessment = copy.deepcopy(after_sigma)
    bad_assessment["support_outcome"] = "maybe"
    results["bad_assessment_outcome_rejected"] = expect_schema_rejection(
        bad_assessment, ASSESSMENT_SCHEMA, "expected one of"
    )

    output = {
        "status": "passed",
        "mode": "multiple independent derived-memory justifications",
        "results": results,
        "research_findings": {
            "or_of_and_support": "antecedents inside one justification are conjunctive while independent justifications are alternatives",
            "affected_is_not_invalid": "a support change can require reassessment without forcing the derived record out of the current view",
            "last_path_rule": "a record is withdrawn only after its final independent justification fails",
            "proposition_identity_vs_support_identity": "semantic record identity remains stable while justification state changes",
        },
        "prior_art_alignment": "assumption-based truth maintenance systems maintain alternative supporting environments for a node",
        "not_validated": [
            "minimal-environment subsumption",
            "inconsistent assumption environments",
            "default or nonmonotonic justifications",
            "probabilistic support weights",
            "large-scale justification indexing",
            "private corpus behavior",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"MULTIPLE_JUSTIFICATIONS_V0_FAIL: {exc}", file=sys.stderr)
        raise

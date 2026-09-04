#!/usr/bin/env python3
import copy
import hashlib
import json
import pathlib
import sys

from run_contract_schema_validation import load_schema, validate, SchemaError


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "fixtures" / "derived-memory-v0" / "evidence.json"
SCHEMA_NAME = "derived-memory-record-v0.schema.json"
TEMPORAL_TYPES = {"state", "relationship", "temporal_transition"}


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def evidence_map(fixture):
    return {item["evidence_id"]: item for item in fixture["evidence"]}


def stable_record_id(record_type, subject, predicate, obj, start_snapshot=None):
    identity = [record_type, subject, predicate, obj]
    if record_type in TEMPORAL_TYPES:
        identity.append(start_snapshot)
    raw = json.dumps(identity, separators=(",", ":"), ensure_ascii=True)
    return "DM-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def proposed_record(record_type, subject, predicate, obj, evidence_refs, snapshot_id, change_kind="initial", start_snapshot=None):
    if record_type in TEMPORAL_TYPES and start_snapshot is None:
        start_snapshot = snapshot_id
    record = {
        "schema": "derived-memory-record-v0",
        "record_id": stable_record_id(record_type, subject, predicate, obj, start_snapshot),
        "record_type": record_type,
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "evidence_refs": list(evidence_refs),
        "source_snapshot_id": snapshot_id,
        "status": "proposed",
        "change_kind": change_kind,
        "attribution_check": {
            "outcome": "not_checked",
            "checked_evidence_refs": [],
            "reason_code": "not_checked",
            "note": "Attribution has not yet been checked."
        }
    }
    if record_type in TEMPORAL_TYPES:
        record["temporal_scope"] = {"start_snapshot": start_snapshot, "end_snapshot": None}
    return record


def relevant_assertions(record, refs, evidence):
    exact = []
    alternatives = []
    for ref in refs:
        item = evidence[ref]
        for assertion in item.get("assertions", []):
            if (
                assertion["record_type"] == record["record_type"]
                and assertion["subject"] == record["subject"]
                and assertion["predicate"] == record["predicate"]
            ):
                if assertion["object"] == record["object"]:
                    exact.append((ref, assertion))
                else:
                    alternatives.append((ref, assertion))
    return exact, alternatives


def explicit_corrections(record, refs, evidence):
    supporting_refs = set()
    for ref in refs:
        item = evidence[ref]
        for assertion in item.get("assertions", []):
            if (
                assertion["record_type"] == record["record_type"]
                and assertion["subject"] == record["subject"]
                and assertion["predicate"] == record["predicate"]
                and assertion["object"] == record["object"]
            ):
                supporting_refs.add(ref)

    corrections = []
    for ref in refs:
        item = evidence[ref]
        corrected = set(item.get("corrects_evidence_refs", []))
        if corrected & supporting_refs:
            for assertion in item.get("assertions", []):
                if (
                    assertion["record_type"] == record["record_type"]
                    and assertion["subject"] == record["subject"]
                    and assertion["predicate"] == record["predicate"]
                    and assertion["object"] != record["object"]
                ):
                    corrections.append((ref, assertion))
    return corrections


def backward_attribution_check(record, evidence):
    refs = record["evidence_refs"]
    unknown = [ref for ref in refs if ref not in evidence]
    if unknown:
        raise AssertionError(f"unknown evidence refs: {unknown}")

    exact, alternatives = relevant_assertions(record, refs, evidence)
    corrections = explicit_corrections(record, refs, evidence)

    if corrections:
        suggested = corrections[-1][1]["object"]
        return {
            "outcome": "rejected",
            "checked_evidence_refs": refs,
            "reason_code": "explicit_correction",
            "note": f"Later evidence explicitly corrects this interpretation; supported replacement is {suggested!r}.",
            "suggested_object": suggested,
        }

    alternative_values = sorted({assertion["object"] for _, assertion in alternatives})
    if exact and alternative_values:
        return {
            "outcome": "unresolved",
            "checked_evidence_refs": refs,
            "reason_code": "conflicting_evidence",
            "note": "The attributed evidence supports conflicting values for the same proposition.",
        }

    if exact:
        reason = "corroborated_support" if len({ref for ref, _ in exact}) > 1 else "direct_support"
        return {
            "outcome": "supported",
            "checked_evidence_refs": refs,
            "reason_code": reason,
            "note": "The normalized attributed evidence supports the proposition as written.",
        }

    if len(alternative_values) == 1:
        return {
            "outcome": "revised",
            "checked_evidence_refs": refs,
            "reason_code": "overreach",
            "note": f"The proposition overreaches the evidence; supported value is {alternative_values[0]!r}.",
            "suggested_object": alternative_values[0],
        }

    return {
        "outcome": "rejected",
        "checked_evidence_refs": refs,
        "reason_code": "overreach",
        "note": "The attributed evidence does not support this proposition.",
    }


def apply_check(record, evidence):
    checked = copy.deepcopy(record)
    result = backward_attribution_check(checked, evidence)
    checked["attribution_check"] = {key: value for key, value in result.items() if key != "suggested_object"}
    if result["outcome"] == "supported":
        checked["status"] = "verified"
    elif result["outcome"] == "unresolved":
        checked["status"] = "unresolved"
        checked["change_kind"] = "conflict_detected"
    elif result["outcome"] in {"rejected", "revised"}:
        checked["status"] = "rejected"
    return checked, result.get("suggested_object")


def accumulate_evidence(record, new_ref, snapshot_id, evidence):
    updated = copy.deepcopy(record)
    prior_id = updated["record_id"]
    if new_ref not in updated["evidence_refs"]:
        updated["evidence_refs"].append(new_ref)
    updated["source_snapshot_id"] = snapshot_id
    updated["change_kind"] = "evidence_added"
    updated, _ = apply_check(updated, evidence)
    assert updated["record_id"] == prior_id
    return updated


def supersede_world_state(old_record, new_record):
    old = copy.deepcopy(old_record)
    new = copy.deepcopy(new_record)
    old["status"] = "superseded"
    old["superseded_by"] = [new["record_id"]]
    old["temporal_scope"]["end_snapshot"] = new["temporal_scope"]["start_snapshot"]
    new["supersedes"] = [old["record_id"]]
    new["change_kind"] = "world_state_changed"
    new["attribution_check"]["reason_code"] = "temporal_update"
    new["attribution_check"]["note"] = "Later evidence supports a new world state; the earlier state remains historically inspectable."
    return old, new


def supersede_correction(old_record, new_record, correction_check):
    old = copy.deepcopy(old_record)
    new = copy.deepcopy(new_record)
    old["status"] = "superseded"
    old["superseded_by"] = [new["record_id"]]
    old["attribution_check"] = {
        key: value for key, value in correction_check.items() if key != "suggested_object"
    }
    new["supersedes"] = [old["record_id"]]
    new["change_kind"] = "interpretation_changed"
    return old, new


def revised_from_same_evidence(rejected_record, suggested_object, evidence):
    revised = proposed_record(
        rejected_record["record_type"],
        rejected_record["subject"],
        rejected_record["predicate"],
        suggested_object,
        rejected_record["evidence_refs"],
        rejected_record["source_snapshot_id"],
        change_kind="interpretation_changed",
        start_snapshot=rejected_record.get("temporal_scope", {}).get("start_snapshot"),
    )
    revised["revision_of"] = rejected_record["record_id"]
    revised, _ = apply_check(revised, evidence)
    return revised


def validate_record(record, schema):
    validate(record, schema)
    return record


def expect_schema_rejection(record, schema, fragment):
    try:
        validate(record, schema)
    except SchemaError as exc:
        assert fragment in str(exc), (fragment, str(exc))
        return str(exc)
    raise AssertionError("expected schema rejection")


def main():
    fixture = load_fixture()
    evidence = evidence_map(fixture)
    schema = load_schema(SCHEMA_NAME)
    evidence_before = json.dumps(fixture["evidence"], sort_keys=True)
    results = {}

    owner = proposed_record("fact", "Project Atlas", "owner", "Rowan", ["EV-ATLAS-OWNER-1"], "SYN-DM-0001")
    owner, _ = apply_check(owner, evidence)
    validate_record(owner, schema)
    owner_id = owner["record_id"]
    owner = accumulate_evidence(owner, "EV-ATLAS-OWNER-2", "SYN-DM-0002", evidence)
    validate_record(owner, schema)
    assert owner["status"] == "verified"
    assert owner["record_id"] == owner_id
    assert owner["attribution_check"]["reason_code"] == "corroborated_support"
    results["stable_fact_accumulation"] = "verified_same_record_id"

    active = proposed_record("state", "Project Atlas", "status", "active", ["EV-ATLAS-STATUS-1"], "SYN-DM-0001")
    active, _ = apply_check(active, evidence)
    paused = proposed_record("state", "Project Atlas", "status", "paused", ["EV-ATLAS-STATUS-2"], "SYN-DM-0002")
    paused, _ = apply_check(paused, evidence)
    active, paused = supersede_world_state(active, paused)
    validate_record(active, schema)
    validate_record(paused, schema)
    assert active["status"] == "superseded" and paused["status"] == "verified"
    assert paused["change_kind"] == "world_state_changed"
    results["temporal_state_transition"] = "history_preserved"

    harbor_10 = proposed_record("fact", "Project Harbor", "launch_date", "May 10", ["EV-HARBOR-DATE-1", "EV-HARBOR-DATE-2"], "SYN-DM-0002")
    harbor_17 = proposed_record("fact", "Project Harbor", "launch_date", "May 17", ["EV-HARBOR-DATE-1", "EV-HARBOR-DATE-2"], "SYN-DM-0002")
    harbor_10, _ = apply_check(harbor_10, evidence)
    harbor_17, _ = apply_check(harbor_17, evidence)
    harbor_10["contradicts"] = [harbor_17["record_id"]]
    harbor_17["contradicts"] = [harbor_10["record_id"]]
    validate_record(harbor_10, schema)
    validate_record(harbor_17, schema)
    assert harbor_10["status"] == harbor_17["status"] == "unresolved"
    results["unresolved_contradiction"] = "conflict_preserved"

    ceramic = proposed_record("fact", "Project Northwind", "casing_material", "ceramic", ["EV-NORTHWIND-MATERIAL-1"], "SYN-DM-0001")
    ceramic, _ = apply_check(ceramic, evidence)
    correction_probe = copy.deepcopy(ceramic)
    correction_probe["evidence_refs"].append("EV-NORTHWIND-MATERIAL-2")
    correction_probe["source_snapshot_id"] = "SYN-DM-0003"
    correction_check = backward_attribution_check(correction_probe, evidence)
    assert correction_check["outcome"] == "rejected"
    composite = proposed_record("fact", "Project Northwind", "casing_material", "composite", ["EV-NORTHWIND-MATERIAL-2"], "SYN-DM-0003", change_kind="interpretation_changed")
    composite, _ = apply_check(composite, evidence)
    ceramic, composite = supersede_correction(ceramic, composite, correction_check)
    validate_record(ceramic, schema)
    validate_record(composite, schema)
    assert ceramic["status"] == "superseded" and composite["status"] == "verified"
    assert composite["change_kind"] == "interpretation_changed"
    results["explicit_correction"] = "prior_interpretation_retained_and_superseded"

    rel_active = proposed_record("relationship", "Project Lumen", "partnership_with_Ardent", "active", ["EV-LUMEN-REL-1"], "SYN-DM-0001")
    rel_active, _ = apply_check(rel_active, evidence)
    rel_ended = proposed_record("relationship", "Project Lumen", "partnership_with_Ardent", "ended", ["EV-LUMEN-REL-2"], "SYN-DM-0003")
    rel_ended, _ = apply_check(rel_ended, evidence)
    rel_active, rel_ended = supersede_world_state(rel_active, rel_ended)
    validate_record(rel_active, schema)
    validate_record(rel_ended, schema)
    assert rel_ended["change_kind"] == "world_state_changed"
    results["evolving_relationship"] = "temporal_relation_preserved"

    cancelled = proposed_record("state", "Project Kepler", "status", "cancelled", ["EV-KEPLER-STATUS-1"], "SYN-DM-0002")
    cancelled, suggested = apply_check(cancelled, evidence)
    validate_record(cancelled, schema)
    assert cancelled["status"] == "rejected"
    assert cancelled["attribution_check"]["outcome"] == "revised"
    assert suggested == "slowed"
    slowed = revised_from_same_evidence(cancelled, suggested, evidence)
    validate_record(slowed, schema)
    assert slowed["status"] == "verified"
    assert slowed["revision_of"] == cancelled["record_id"]
    assert slowed["change_kind"] == "interpretation_changed"
    results["backward_attribution_overreach"] = "cancelled_rejected_slowed_verified"

    missing_evidence = copy.deepcopy(owner)
    del missing_evidence["evidence_refs"]
    results["schema_missing_evidence_rejected"] = expect_schema_rejection(missing_evidence, schema, "missing required key")
    bad_status = copy.deepcopy(owner)
    bad_status["status"] = "true_forever"
    results["schema_bad_status_rejected"] = expect_schema_rejection(bad_status, schema, "expected one of")

    evidence_after = json.dumps(fixture["evidence"], sort_keys=True)
    assert evidence_before == evidence_after
    results["canonical_evidence_immutability"] = "fixture_unchanged"

    report = {
        "status": "passed",
        "mode": "experimental public derived-memory semantics",
        "schema_status": "experimental/public research contract; synthetic only",
        "results": results,
        "distinctions": {
            "evidence_changed": "stable fact gained corroborating evidence without changing semantic record identity",
            "world_state_changed": "state/relationship records were temporally superseded while earlier records remained inspectable",
            "interpretation_changed": "explicit correction and backward-check revision replaced an interpretation without rewriting evidence"
        },
        "not_validated": [
            "LLM extraction",
            "automatic evidence normalization",
            "private corpus behavior",
            "Chroma/HNSW/FTS integration",
            "probabilistic confidence calibration",
            "production persistence or query APIs"
        ]
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"DERIVED_MEMORY_V0_FAIL: {exc}", file=sys.stderr)
        raise

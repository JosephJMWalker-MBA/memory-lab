#!/usr/bin/env python3
import copy
import hashlib
import json
import pathlib
import sys

from run_contract_schema_validation import load_schema, validate, SchemaError


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "derived-memory-adversarial" / "evidence.json"
RECORD_SCHEMA = "derived-memory-record-v0.1.schema.json"
ASSESSMENT_SCHEMA = "derived-evidence-assessment-v0.schema.json"
TEMPORAL_TYPES = {"state", "relationship", "temporal_transition"}


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def evidence_map(fixture):
    return {item["evidence_id"]: item for item in fixture["evidence"]}


def stable_id(record_type, subject, predicate, obj, qualifiers, valid_from, first_known_snapshot):
    identity = {
        "record_type": record_type,
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "qualifiers": qualifiers,
    }
    if record_type in TEMPORAL_TYPES:
        identity["temporal_anchor"] = valid_from or first_known_snapshot
    raw = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return "DM-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def record(
    record_type,
    subject,
    predicate,
    obj,
    evidence_refs,
    snapshot_id,
    *,
    qualifiers=None,
    derived_from_records=None,
    derivation_rule=None,
    valid_time=None,
    change_kind="initial",
    revision_of=None,
):
    qualifiers = qualifiers or {}
    derived_from_records = derived_from_records or []
    valid_from = valid_time["from"] if valid_time else None
    rec = {
        "schema": "derived-memory-record-v0.1",
        "record_id": stable_id(record_type, subject, predicate, obj, qualifiers, valid_from, snapshot_id),
        "record_type": record_type,
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "qualifiers": qualifiers,
        "evidence_refs": list(evidence_refs),
        "derived_from_records": list(derived_from_records),
        "derivation_rule": derivation_rule,
        "source_snapshot_id": snapshot_id,
        "status": "proposed",
        "change_kind": change_kind,
        "attribution_check": {
            "outcome": "not_checked",
            "checked_evidence_refs": [],
            "checked_derived_records": [],
            "reason_code": "not_checked",
            "note": "Attribution has not yet been checked.",
        },
        "knowledge_time": {
            "first_known_snapshot": snapshot_id,
            "last_assessed_snapshot": snapshot_id,
        },
    }
    if valid_time is not None:
        rec["valid_time"] = copy.deepcopy(valid_time)
    if revision_of is not None:
        rec["revision_of"] = revision_of
    return rec


def same_core(record, assertion):
    return (
        assertion["record_type"] == record["record_type"]
        and assertion["subject"] == record["subject"]
        and assertion["predicate"] == record["predicate"]
    )


def direct_support_check(record, evidence):
    candidates = []
    for ref in record["evidence_refs"]:
        item = evidence[ref]
        for assertion in item.get("assertions", []):
            if same_core(record, assertion):
                candidates.append((ref, item, assertion))

    exact_object = [(ref, item, a) for ref, item, a in candidates if a["object"] == record["object"]]
    alternatives = sorted({a["object"] for _, _, a in candidates if a["object"] != record["object"]})

    if exact_object:
        for ref, item, assertion in exact_object:
            required_qualifiers = assertion.get("qualifiers", {})
            if record["qualifiers"] == required_qualifiers:
                reason = "retroactive_correction" if item.get("corrects_evidence_refs") else "direct_support"
                return {
                    "outcome": "supported",
                    "reason_code": reason,
                    "checked_evidence_refs": list(record["evidence_refs"]),
                    "checked_derived_records": [],
                    "note": "Canonical normalized evidence supports the proposition and qualifiers as written.",
                }

        suggested = exact_object[0][2].get("qualifiers", {})
        return {
            "outcome": "revised",
            "reason_code": "qualifier_loss",
            "checked_evidence_refs": list(record["evidence_refs"]),
            "checked_derived_records": [],
            "note": "The core proposition is supported only with qualifiers that the candidate omitted or changed.",
            "suggested_qualifiers": suggested,
        }

    if len(alternatives) == 1:
        return {
            "outcome": "revised",
            "reason_code": "overreach",
            "checked_evidence_refs": list(record["evidence_refs"]),
            "checked_derived_records": [],
            "note": f"Attributed evidence supports {alternatives[0]!r}, not the proposed object.",
            "suggested_object": alternatives[0],
        }

    if len(alternatives) > 1:
        return {
            "outcome": "unresolved",
            "reason_code": "conflicting_evidence",
            "checked_evidence_refs": list(record["evidence_refs"]),
            "checked_derived_records": [],
            "note": "Attributed evidence supports multiple incompatible objects.",
        }

    return {
        "outcome": "rejected",
        "reason_code": "overreach",
        "checked_evidence_refs": list(record["evidence_refs"]),
        "checked_derived_records": [],
        "note": "No attributed canonical evidence supports this proposition.",
    }


def recursive_support_check(record, derived_records):
    if record.get("derivation_rule") != "dependency_block_propagation":
        return {
            "outcome": "rejected",
            "reason_code": "recursive_support",
            "checked_evidence_refs": list(record["evidence_refs"]),
            "checked_derived_records": list(record["derived_from_records"]),
            "note": "No recognized derivation rule justifies this derived proposition.",
        }

    parents = [derived_records[parent_id] for parent_id in record["derived_from_records"]]
    if any(parent["status"] != "verified" for parent in parents):
        return {
            "outcome": "rejected",
            "reason_code": "recursive_support",
            "checked_evidence_refs": list(record["evidence_refs"]),
            "checked_derived_records": list(record["derived_from_records"]),
            "note": "A direct derived dependency is not verified.",
        }

    dependency = next(
        (p for p in parents if p["record_type"] == "relationship" and p["subject"] == record["subject"] and p["predicate"] == "depends_on"),
        None,
    )
    blocked = next(
        (p for p in parents if p["record_type"] == "state" and p["predicate"] == "status" and p["object"] == "blocked"),
        None,
    )
    if not dependency or not blocked or dependency["object"] != blocked["subject"]:
        return {
            "outcome": "rejected",
            "reason_code": "recursive_support",
            "checked_evidence_refs": list(record["evidence_refs"]),
            "checked_derived_records": list(record["derived_from_records"]),
            "note": "Dependency parents do not satisfy the declared propagation rule.",
        }

    if not (record["predicate"] == "status" and record["object"] == "blocked"):
        return {
            "outcome": "rejected",
            "reason_code": "recursive_support",
            "checked_evidence_refs": list(record["evidence_refs"]),
            "checked_derived_records": list(record["derived_from_records"]),
            "note": "The child proposition does not match the declared propagation rule.",
        }

    expected_leaves = sorted(set().union(*(set(parent["evidence_refs"]) for parent in parents)))
    if sorted(record["evidence_refs"]) != expected_leaves:
        return {
            "outcome": "rejected",
            "reason_code": "recursive_support",
            "checked_evidence_refs": list(record["evidence_refs"]),
            "checked_derived_records": list(record["derived_from_records"]),
            "note": "Child canonical evidence leaves do not equal the direct dependency closure.",
        }

    return {
        "outcome": "supported",
        "reason_code": "recursive_support",
        "checked_evidence_refs": expected_leaves,
        "checked_derived_records": list(record["derived_from_records"]),
        "note": "Verified dependencies and the declared deterministic rule support this proposition.",
    }


def support_check(record, evidence, derived_records):
    if record["derived_from_records"]:
        return recursive_support_check(record, derived_records)
    return direct_support_check(record, evidence)


def apply_support(record, evidence, derived_records):
    checked = copy.deepcopy(record)
    result = support_check(checked, evidence, derived_records)
    checked["attribution_check"] = {
        key: value
        for key, value in result.items()
        if key not in {"suggested_qualifiers", "suggested_object"}
    }
    if result["outcome"] == "supported":
        checked["status"] = "verified"
    elif result["outcome"] == "unresolved":
        checked["status"] = "unresolved"
        checked["change_kind"] = "conflict_detected"
    else:
        checked["status"] = "rejected"
    return checked, result


def relevant_refs(record, evidence):
    refs = []
    for ref, item in evidence.items():
        if item["snapshot_id"] != record["source_snapshot_id"]:
            continue
        if any(same_core(record, assertion) for assertion in item.get("assertions", [])):
            refs.append(ref)
    return sorted(refs)


def assessment_id(record_id, considered_refs, basis):
    raw = json.dumps([record_id, sorted(considered_refs), basis], separators=(",", ":"))
    return "DA-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def assess_evidence_set(record, considered_refs, evidence, coverage_basis):
    local = direct_support_check(record, evidence)
    if coverage_basis == "synthetic_closed_world":
        relevant = relevant_refs(record, evidence)
        omitted = sorted(set(relevant) - set(considered_refs))
        coverage = "complete" if not omitted else "incomplete"
        objects = set()
        for ref in relevant:
            for assertion in evidence[ref].get("assertions", []):
                if same_core(record, assertion):
                    objects.add(assertion["object"])
        contrary = any(obj != record["object"] for obj in objects)
    else:
        relevant = []
        omitted = []
        coverage = "unknown"
        contrary = False

    if local["outcome"] == "supported":
        if contrary:
            overall = "unresolved"
        elif coverage == "complete":
            overall = "verified"
        else:
            overall = "provisionally_supported"
    else:
        overall = local["outcome"]

    return {
        "schema": "derived-evidence-assessment-v0",
        "assessment_id": assessment_id(record["record_id"], considered_refs, coverage_basis),
        "record_id": record["record_id"],
        "source_snapshot_id": record["source_snapshot_id"],
        "support_outcome": local["outcome"],
        "coverage_outcome": coverage,
        "coverage_basis": coverage_basis,
        "considered_evidence_refs": sorted(considered_refs),
        "relevant_evidence_refs": relevant,
        "omitted_relevant_evidence_refs": omitted,
        "overall_outcome": overall,
        "note": "Support and evidence coverage are assessed separately.",
    }


def trace_canonical_evidence(record_id, records, stack=None):
    stack = list(stack or [])
    if record_id in stack:
        raise AssertionError("DERIVATION_CYCLE")
    record = records[record_id]
    stack.append(record_id)
    leaves = set(record["evidence_refs"])
    for parent_id in record["derived_from_records"]:
        leaves.update(trace_canonical_evidence(parent_id, records, stack))
    return leaves


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

    # 1. Local support is insufficient when relevant contrary evidence was omitted.
    orion = record("fact", "Project Orion", "launch_date", "June 4", ["EV-ORION-DATE-A"], "SYN-DM-0100")
    orion, local = apply_support(orion, evidence, records)
    validate_artifact(orion, RECORD_SCHEMA)
    assert orion["status"] == "verified"
    incomplete = assess_evidence_set(orion, ["EV-ORION-DATE-A"], evidence, "synthetic_closed_world")
    validate_artifact(incomplete, ASSESSMENT_SCHEMA)
    assert incomplete["coverage_outcome"] == "incomplete"
    assert incomplete["omitted_relevant_evidence_refs"] == ["EV-ORION-DATE-B"]
    assert incomplete["overall_outcome"] == "unresolved"
    unknown = assess_evidence_set(orion, ["EV-ORION-DATE-A"], evidence, "unknown")
    validate_artifact(unknown, ASSESSMENT_SCHEMA)
    assert unknown["coverage_outcome"] == "unknown"
    assert unknown["overall_outcome"] == "provisionally_supported"
    complete = assess_evidence_set(orion, ["EV-ORION-DATE-A", "EV-ORION-DATE-B"], evidence, "synthetic_closed_world")
    validate_artifact(complete, ASSESSMENT_SCHEMA)
    assert complete["coverage_outcome"] == "complete"
    assert complete["overall_outcome"] == "unresolved"
    results["omitted_contrary_evidence"] = "local_support_downgraded_by_coverage_assessment"

    # 2. Qualifiers are semantically load-bearing.
    meridian = record("state", "Project Meridian", "access", "approved", ["EV-MERIDIAN-ACCESS"], "SYN-DM-0100")
    meridian, qualifier_check = apply_support(meridian, evidence, records)
    validate_artifact(meridian, RECORD_SCHEMA)
    assert meridian["status"] == "rejected"
    assert qualifier_check["reason_code"] == "qualifier_loss"
    revised_meridian = record(
        "state",
        "Project Meridian",
        "access",
        "approved",
        ["EV-MERIDIAN-ACCESS"],
        "SYN-DM-0100",
        qualifiers=qualifier_check["suggested_qualifiers"],
        change_kind="interpretation_changed",
        revision_of=meridian["record_id"],
    )
    revised_meridian, _ = apply_support(revised_meridian, evidence, records)
    validate_artifact(revised_meridian, RECORD_SCHEMA)
    assert revised_meridian["status"] == "verified"
    results["qualifier_loss"] = "unqualified_claim_rejected_qualified_revision_verified"

    # 3. Recursive derivation retains direct dependencies and canonical leaves.
    dependency = record(
        "relationship",
        "Project Vega",
        "depends_on",
        "Module Sigma",
        ["EV-VEGA-DEPENDENCY"],
        "SYN-DM-0101",
    )
    dependency, _ = apply_support(dependency, evidence, records)
    records[dependency["record_id"]] = dependency
    sigma = record("state", "Module Sigma", "status", "blocked", ["EV-SIGMA-STATUS"], "SYN-DM-0101")
    sigma, _ = apply_support(sigma, evidence, records)
    records[sigma["record_id"]] = sigma
    vega = record(
        "state",
        "Project Vega",
        "status",
        "blocked",
        ["EV-VEGA-DEPENDENCY", "EV-SIGMA-STATUS"],
        "SYN-DM-0101",
        derived_from_records=[dependency["record_id"], sigma["record_id"]],
        derivation_rule="dependency_block_propagation",
    )
    vega, _ = apply_support(vega, evidence, records)
    records[vega["record_id"]] = vega
    validate_artifact(vega, RECORD_SCHEMA)
    assert vega["status"] == "verified"
    assert trace_canonical_evidence(vega["record_id"], records) == {"EV-VEGA-DEPENDENCY", "EV-SIGMA-STATUS"}
    cyclic = copy.deepcopy(vega)
    cyclic["derived_from_records"] = [vega["record_id"]]
    records[vega["record_id"]] = cyclic
    try:
        trace_canonical_evidence(vega["record_id"], records)
    except AssertionError as exc:
        assert str(exc) == "DERIVATION_CYCLE"
    else:
        raise AssertionError("expected derivation cycle rejection")
    records[vega["record_id"]] = vega
    results["recursive_provenance"] = "canonical_leaf_closure_verified_and_cycle_rejected"

    # 4. Valid time and knowledge time are separate axes.
    nova_active = record(
        "state",
        "Project Nova",
        "status",
        "active",
        ["EV-NOVA-INITIAL"],
        "SYN-DM-0100",
        valid_time={"from": "2026-01-01", "to": None},
    )
    nova_active, _ = apply_support(nova_active, evidence, records)
    nova_paused = record(
        "state",
        "Project Nova",
        "status",
        "paused",
        ["EV-NOVA-RETROACTIVE-CORRECTION"],
        "SYN-DM-0102",
        valid_time={"from": "2026-01-15", "to": None},
        change_kind="world_state_changed",
    )
    nova_paused, correction = apply_support(nova_paused, evidence, records)
    assert correction["reason_code"] == "retroactive_correction"
    nova_active["status"] = "superseded"
    nova_active["valid_time"]["to"] = "2026-01-15"
    nova_active["knowledge_time"]["last_assessed_snapshot"] = "SYN-DM-0102"
    nova_active["superseded_by"] = [nova_paused["record_id"]]
    nova_paused["supersedes"] = [nova_active["record_id"]]
    validate_artifact(nova_active, RECORD_SCHEMA)
    validate_artifact(nova_paused, RECORD_SCHEMA)
    assert nova_paused["valid_time"]["from"] == "2026-01-15"
    assert nova_paused["knowledge_time"]["first_known_snapshot"] == "SYN-DM-0102"
    assert nova_active["knowledge_time"]["first_known_snapshot"] == "SYN-DM-0100"
    results["bitemporal_separation"] = "valid_time_distinct_from_when_system_learned_correction"

    # 5. Schemas reject malformed research artifacts.
    bad = copy.deepcopy(revised_meridian)
    del bad["knowledge_time"]
    results["missing_knowledge_time_rejected"] = expect_schema_rejection(bad, RECORD_SCHEMA, "missing required key")
    bad_assessment = copy.deepcopy(unknown)
    del bad_assessment["coverage_basis"]
    results["missing_coverage_basis_rejected"] = expect_schema_rejection(bad_assessment, ASSESSMENT_SCHEMA, "missing required key")

    report = {
        "status": "passed",
        "mode": "adversarial public derived-memory semantics",
        "results": results,
        "research_findings": {
            "support_is_not_coverage": "a claim can be locally supported while contrary evidence is omitted or coverage is unknown",
            "qualifiers_are_semantic": "dropping scope/environment qualifiers changes the proposition and must trigger revision",
            "recursive_provenance": "multi-hop records retain direct derived dependencies plus canonical evidence closure",
            "bitemporal_memory": "valid time in the world differs from the snapshot when the system learned or reassessed the claim",
        },
        "not_validated": [
            "real retrieval coverage completeness",
            "automatic discovery of relevant contrary evidence",
            "LLM extraction or normalization",
            "probabilistic source authority",
            "private corpus behavior",
            "production recursive reasoning",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"DERIVED_MEMORY_ADVERSARIAL_FAIL: {exc}", file=sys.stderr)
        raise

#!/usr/bin/env python3
import copy
import json
import pathlib
import re
import sys

from run_synthetic_lifecycle import FIXTURE_ROOT, classify_delta, snapshot
from run_failure_semantics import add_plan, base_index, transition_ids


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas"


class SchemaError(Exception):
    pass


def load_schema(name):
    return json.loads((SCHEMA_ROOT / name).read_text(encoding="utf-8"))


def type_matches(value, expected):
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    raise SchemaError(f"unsupported schema type {expected!r}")


def resolve_ref(schema, ref):
    prefix = "#/$defs/"
    if not ref.startswith(prefix):
        raise SchemaError(f"unsupported ref {ref!r}")
    return schema["$defs"][ref[len(prefix):]]


def validate(instance, schema, root=None, path="$"):
    root = root or schema

    if "$ref" in schema:
        validate(instance, resolve_ref(root, schema["$ref"]), root, path)
        return

    if "anyOf" in schema:
        errors = []
        for option in schema["anyOf"]:
            try:
                validate(instance, option, root, path)
                return
            except SchemaError as exc:
                errors.append(str(exc))
        raise SchemaError(f"{path}: did not match anyOf: {errors}")

    if "const" in schema and instance != schema["const"]:
        raise SchemaError(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(f"{path}: expected one of {schema['enum']!r}, got {instance!r}")

    if "type" in schema:
        expected_types = schema["type"]
        if isinstance(expected_types, str):
            expected_types = [expected_types]
        if not any(type_matches(instance, expected) for expected in expected_types):
            raise SchemaError(f"{path}: expected type {schema['type']!r}, got {type(instance).__name__}")

    if isinstance(instance, str) and "minLength" in schema and len(instance) < schema["minLength"]:
        raise SchemaError(f"{path}: shorter than minLength")
    if isinstance(instance, str) and "pattern" in schema and not re.search(schema["pattern"], instance):
        raise SchemaError(f"{path}: does not match pattern {schema['pattern']!r}")

    if isinstance(instance, int) and "minimum" in schema and instance < schema["minimum"]:
        raise SchemaError(f"{path}: below minimum")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise SchemaError(f"{path}: too few items")
        if schema.get("uniqueItems") and len(instance) != len(set(json.dumps(x, sort_keys=True) for x in instance)):
            raise SchemaError(f"{path}: duplicate array items")
        if "items" in schema:
            for index, item in enumerate(instance):
                validate(item, schema["items"], root, f"{path}[{index}]")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                raise SchemaError(f"{path}: missing required key {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(instance) - set(properties)
            if extra:
                raise SchemaError(f"{path}: unexpected keys {sorted(extra)!r}")
        additional = schema.get("additionalProperties")
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                validate(value, properties[key], root, child_path)
            elif isinstance(additional, dict):
                validate(value, additional, root, child_path)


def expect_invalid(label, instance, schema, expected_fragment):
    try:
        validate(instance, schema)
    except SchemaError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"{label}: expected {expected_fragment!r} in {exc!r}")
        return str(exc)
    raise AssertionError(f"{label}: expected schema rejection")


def public_snapshot_artifact():
    snap = snapshot(FIXTURE_ROOT / "S0")
    return {
        "schema": "source-snapshot-contract-v1",
        "status": "reproduced_by_public_synthetic_harness",
        "snapshot_id": snap["snapshot_id"],
        "files": snap["files"],
    }


def public_delta_artifact():
    left = snapshot(FIXTURE_ROOT / "S0")
    right = snapshot(FIXTURE_ROOT / "S1")
    return {
        "schema": "source-delta-contract-v1",
        "status": "reproduced_by_public_synthetic_harness",
        "from_snapshot": left["snapshot_id"],
        "to_snapshot": right["snapshot_id"],
        **classify_delta(left, right),
    }


def public_mutation_plan_artifact():
    return {
        "schema": "mutation-plan-contract-v1",
        "status": "reproduced_by_public_synthetic_harness",
        "mutation": "add",
        "from_snapshot": "A",
        "to_snapshot": "B",
        "source": "added.md",
        "expected_count_before": 3,
        "expected_count_after": 4,
        "desired_ids": ["added:0"],
    }


def public_index_state_artifact():
    idx = base_index()
    return {
        "schema": "index-state-contract-v1",
        "status": "reproduced_by_public_synthetic_harness",
        "current_snapshot": idx.state["current_snapshot"],
        "current_count": idx.state["current_count"],
        "last_transition_id": idx.state["last_transition_id"],
    }


def public_pending_transaction_artifact():
    idx = base_index()
    plan = add_plan()
    edge_id, transition_id = transition_ids(idx.state["last_transition_id"], plan, {"added_ids": ["added:0"]})
    return {
        "schema": "pending-transaction-contract-v1",
        "status": "prepared",
        "mutation": "add",
        "from_snapshot": "A",
        "to_snapshot": "B",
        "source": "added.md",
        "edge_id": edge_id,
        "transition_id": transition_id,
        "parent_transition_id": "TX-GENESIS",
        "expected_count_before": 3,
        "expected_count_after": 4,
        "affected_ids": ["added:0"],
    }


def public_ledger_entry_artifact():
    idx = base_index()
    plan = add_plan()
    edge_id, transition_id = transition_ids(idx.state["last_transition_id"], plan, {"added_ids": ["added:0"]})
    return {
        "schema": "ledger-entry-contract-v1",
        "status": "committed",
        "mutation": "add",
        "from_snapshot": "A",
        "to_snapshot": "B",
        "source": "added.md",
        "edge_id": edge_id,
        "transition_id": transition_id,
        "parent_transition_id": "TX-GENESIS",
        "count_before": 3,
        "count_after": 4,
    }


def main():
    cases = {
        "source_snapshot": ("source-snapshot-contract-v1.schema.json", public_snapshot_artifact()),
        "source_delta": ("source-delta-contract-v1.schema.json", public_delta_artifact()),
        "mutation_plan": ("mutation-plan-contract-v1.schema.json", public_mutation_plan_artifact()),
        "index_state": ("index-state-contract-v1.schema.json", public_index_state_artifact()),
        "pending_transaction": ("pending-transaction-contract-v1.schema.json", public_pending_transaction_artifact()),
        "ledger_entry": ("ledger-entry-contract-v1.schema.json", public_ledger_entry_artifact()),
    }

    results = {}
    for name, (schema_name, artifact) in cases.items():
        schema = load_schema(schema_name)
        validate(artifact, schema)
        results[f"{name}_valid"] = "accepted"

    snapshot_bad = copy.deepcopy(cases["source_snapshot"][1])
    del snapshot_bad["snapshot_id"]
    results["missing_snapshot_identity_rejected"] = expect_invalid(
        "missing snapshot identity",
        snapshot_bad,
        load_schema(cases["source_snapshot"][0]),
        "missing required key",
    )

    snapshot_bad_id = copy.deepcopy(cases["source_snapshot"][1])
    snapshot_bad_id["snapshot_id"] = "snapshot-a"
    results["invalid_snapshot_identifier_rejected"] = expect_invalid(
        "invalid snapshot identifier",
        snapshot_bad_id,
        load_schema(cases["source_snapshot"][0]),
        "does not match pattern",
    )

    plan_bad_mutation = copy.deepcopy(cases["mutation_plan"][1])
    plan_bad_mutation["mutation"] = "rewrite"
    results["malformed_mutation_type_rejected"] = expect_invalid(
        "malformed mutation type",
        plan_bad_mutation,
        load_schema(cases["mutation_plan"][0]),
        "expected one of",
    )

    pending_incomplete = copy.deepcopy(cases["pending_transaction"][1])
    del pending_incomplete["parent_transition_id"]
    results["incomplete_pending_transaction_rejected"] = expect_invalid(
        "incomplete pending transaction",
        pending_incomplete,
        load_schema(cases["pending_transaction"][0]),
        "missing required key",
    )

    ledger_bad = copy.deepcopy(cases["ledger_entry"][1])
    del ledger_bad["parent_transition_id"]
    results["ledger_without_chain_identity_rejected"] = expect_invalid(
        "ledger without chain identity",
        ledger_bad,
        load_schema(cases["ledger_entry"][0]),
        "missing required key",
    )

    plan_extra = copy.deepcopy(cases["mutation_plan"][1])
    plan_extra["unreviewed_field"] = True
    results["unexpected_additional_field_rejected"] = expect_invalid(
        "unexpected additional field",
        plan_extra,
        load_schema(cases["mutation_plan"][0]),
        "unexpected keys",
    )

    structurally_valid_but_semantically_invalid = copy.deepcopy(cases["mutation_plan"][1])
    structurally_valid_but_semantically_invalid["from_snapshot"] = "B"
    validate(structurally_valid_but_semantically_invalid, load_schema(cases["mutation_plan"][0]))
    results["schema_validity_is_not_transition_validity"] = "accepted_by_schema_semantic_tests_must_reject"

    report = {
        "status": "passed",
        "mode": "public research contract schema validation",
        "validated_schemas": sorted(schema_name for schema_name, _ in cases.values()),
        "results": results,
        "semantic_invariants_outside_json_schema": [
            "plan from_snapshot must match current index state",
            "state current_count must match current logical records",
            "last_transition_id must exist in the ledger",
            "replay no-op requires resulting state and records to be verified",
            "CHANGE must materialize desired records before stale deletion",
            "DELETE must persist a pending transaction before destructive removal",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"CONTRACT_SCHEMA_VALIDATION_FAIL: {exc}", file=sys.stderr)
        raise

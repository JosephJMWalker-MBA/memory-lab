#!/usr/bin/env python3
import copy
import hashlib
import json
import sys


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def transition_ids(parent_transition_id, plan, mutation_details):
    edge_core = {
        "from_snapshot": plan["from_snapshot"],
        "to_snapshot": plan["to_snapshot"],
        "mutation": plan["mutation"],
        "details": mutation_details,
    }
    edge_id = "EDGE-" + digest(edge_core)[:16]
    transition_id = "TX-" + digest(
        {
            "parent_transition_id": parent_transition_id,
            "edge_id": edge_id,
        }
    )[:16]
    return edge_id, transition_id


class FailClosed(Exception):
    pass


class SyntheticIndex:
    def __init__(self, records=None, state=None, ledger=None, pending=None):
        self.records = copy.deepcopy(records or {})
        self.state = copy.deepcopy(state or {})
        self.ledger = copy.deepcopy(ledger or [])
        self.pending = copy.deepcopy(pending)

    def source_ids(self, source):
        return sorted(
            record_id
            for record_id, record in self.records.items()
            if record["source"] == source
        )

    def ledger_ids(self):
        return {entry["transition_id"] for entry in self.ledger}

    def verify_common_preconditions(self, plan):
        if self.pending:
            raise FailClosed("PENDING_TRANSACTION_EXISTS")
        if self.state["current_snapshot"] != plan["from_snapshot"]:
            raise FailClosed("SNAPSHOT_MISMATCH")
        if self.state["current_count"] != len(self.records):
            raise FailClosed("STATE_COUNT_MISMATCH")
        if self.state["last_transition_id"] not in self.ledger_ids():
            raise FailClosed("STATE_LAST_TRANSITION_NOT_IN_LEDGER")

    def verify_replay(self, plan, mutation_details):
        parent = self.state["parent_before_replay"]
        edge_id, transition_id = transition_ids(parent, plan, mutation_details)
        matching = [
            entry for entry in self.ledger
            if entry["transition_id"] == transition_id
            and entry["edge_id"] == edge_id
            and entry["to_snapshot"] == plan["to_snapshot"]
        ]
        if not matching:
            raise FailClosed("REPLAY_LEDGER_ENTRY_MISSING")
        if self.state["current_snapshot"] != plan["to_snapshot"]:
            raise FailClosed("REPLAY_STATE_NOT_AT_TO_SNAPSHOT")
        if self.state["current_count"] != len(self.records):
            raise FailClosed("REPLAY_STATE_COUNT_MISMATCH")
        return "ALREADY_COMMITTED_NOOP"

    def apply_add(self, plan):
        self.verify_common_preconditions(plan)
        source = plan["source"]
        desired = plan["desired_records"]
        if self.source_ids(source):
            raise FailClosed("ADD_TARGET_ALREADY_HAS_RECORDS")
        for record_id, record in desired.items():
            existing = self.records.get(record_id)
            if existing and existing["source"] != record["source"]:
                raise FailClosed("FOREIGN_OWNERSHIP_COLLISION")
        self.records.update(copy.deepcopy(desired))
        self.commit(plan, {"added_ids": sorted(desired)})
        return "COMMITTED"

    def apply_change(self, plan, crash_after_upsert=False):
        self.verify_common_preconditions(plan)
        source = plan["source"]
        desired = plan["desired_records"]
        current_ids = self.source_ids(source)
        if not current_ids:
            raise FailClosed("CHANGE_SOURCE_MISSING")
        for record_id, record in desired.items():
            existing = self.records.get(record_id)
            if existing and existing["source"] != record["source"]:
                raise FailClosed("FOREIGN_OWNERSHIP_COLLISION")

        desired_ids = set(desired)
        stale_ids = sorted(set(current_ids) - desired_ids)

        # Evidence continuity over cleanup convenience: the desired
        # representation exists before stale records are removed.
        self.records.update(copy.deepcopy(desired))
        if crash_after_upsert:
            return {
                "status": "INTERRUPTED_AFTER_DESIRED_UPSERT",
                "desired_present": all(record_id in self.records for record_id in desired_ids),
                "stale_present": all(record_id in self.records for record_id in stale_ids),
            }

        for record_id in stale_ids:
            del self.records[record_id]
        self.commit(plan, {"desired_ids": sorted(desired_ids), "stale_ids": stale_ids})
        return "COMMITTED"

    def apply_delete(self, plan, crash_after_journal=False):
        self.verify_common_preconditions(plan)
        source = plan["source"]
        delete_ids = self.source_ids(source)
        if not delete_ids:
            raise FailClosed("DELETE_SOURCE_ALREADY_ABSENT")

        parent = self.state["last_transition_id"]
        edge_id, transition_id = transition_ids(parent, plan, {"deleted_ids": delete_ids})
        self.pending = {
            "transition_id": transition_id,
            "edge_id": edge_id,
            "deleted_ids": delete_ids,
        }
        if crash_after_journal:
            return "INTERRUPTED_AFTER_PENDING_JOURNAL"

        for record_id in delete_ids:
            del self.records[record_id]
        self.finish_commit(plan, edge_id, transition_id, {"deleted_ids": delete_ids})
        self.pending = None
        return "COMMITTED"

    def commit(self, plan, mutation_details):
        parent = self.state["last_transition_id"]
        edge_id, transition_id = transition_ids(parent, plan, mutation_details)
        self.finish_commit(plan, edge_id, transition_id, mutation_details)

    def finish_commit(self, plan, edge_id, transition_id, mutation_details):
        if transition_id in self.ledger_ids():
            raise FailClosed("TRANSITION_ID_ALREADY_EXISTS")
        self.ledger.append(
            {
                "transition_id": transition_id,
                "edge_id": edge_id,
                "from_snapshot": plan["from_snapshot"],
                "to_snapshot": plan["to_snapshot"],
                "mutation": plan["mutation"],
                "details": mutation_details,
            }
        )
        self.state["current_snapshot"] = plan["to_snapshot"]
        self.state["current_count"] = len(self.records)
        self.state["last_transition_id"] = transition_id


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(condition, label):
    if not condition:
        raise AssertionError(label)


def assert_fail_closed(label, fn, expected_reason):
    try:
        fn()
    except FailClosed as exc:
        assert_equal(str(exc), expected_reason, label)
        return str(exc)
    raise AssertionError(f"{label}: expected fail closed")


def base_index():
    records = {
        "alpha:0": {"source": "alpha.md", "document": "alpha baseline"},
        "change:0": {"source": "change.md", "document": "change baseline"},
        "delete:0": {"source": "delete.md", "document": "delete baseline"},
    }
    ledger = [
        {
            "transition_id": "TX-GENESIS",
            "edge_id": "EDGE-GENESIS",
            "from_snapshot": None,
            "to_snapshot": "A",
            "mutation": "bootstrap",
            "details": {},
        }
    ]
    state = {
        "current_snapshot": "A",
        "current_count": len(records),
        "last_transition_id": "TX-GENESIS",
    }
    return SyntheticIndex(records=records, state=state, ledger=ledger)


def add_plan(from_snapshot="A", to_snapshot="B", record_id="added:0"):
    return {
        "mutation": "add",
        "from_snapshot": from_snapshot,
        "to_snapshot": to_snapshot,
        "source": "added.md",
        "desired_records": {
            record_id: {"source": "added.md", "document": "added desired"}
        },
    }


def change_plan(from_snapshot="A", to_snapshot="B", desired=None):
    return {
        "mutation": "change",
        "from_snapshot": from_snapshot,
        "to_snapshot": to_snapshot,
        "source": "change.md",
        "desired_records": desired or {
            "change:0": {"source": "change.md", "document": "change replacement"},
            "change:1": {"source": "change.md", "document": "change expansion"},
        },
    }


def delete_plan(from_snapshot="A", to_snapshot="B"):
    return {
        "mutation": "delete",
        "from_snapshot": from_snapshot,
        "to_snapshot": to_snapshot,
        "source": "delete.md",
    }


def test_unexpected_pre_existing_add():
    idx = base_index()
    idx.records["added:old"] = {"source": "added.md", "document": "unexpected existing"}
    idx.state["current_count"] = len(idx.records)
    return assert_fail_closed(
        "unexpected pre-existing ADD",
        lambda: idx.apply_add(add_plan()),
        "ADD_TARGET_ALREADY_HAS_RECORDS",
    )


def test_missing_change_source():
    idx = base_index()
    del idx.records["change:0"]
    idx.state["current_count"] = len(idx.records)
    return assert_fail_closed(
        "missing CHANGE source",
        lambda: idx.apply_change(change_plan()),
        "CHANGE_SOURCE_MISSING",
    )


def test_already_absent_delete_source():
    idx = base_index()
    del idx.records["delete:0"]
    idx.state["current_count"] = len(idx.records)
    return assert_fail_closed(
        "already-absent DELETE source",
        lambda: idx.apply_delete(delete_plan()),
        "DELETE_SOURCE_ALREADY_ABSENT",
    )


def test_snapshot_mismatch():
    idx = base_index()
    return assert_fail_closed(
        "snapshot mismatch",
        lambda: idx.apply_add(add_plan(from_snapshot="WRONG")),
        "SNAPSHOT_MISMATCH",
    )


def test_replay_idempotence():
    idx = base_index()
    plan = add_plan()
    parent = idx.state["last_transition_id"]
    idx.apply_add(plan)
    idx.state["parent_before_replay"] = parent
    return idx.verify_replay(plan, {"added_ids": ["added:0"]})


def test_pending_transaction_recovery_barrier():
    idx = base_index()
    idx.pending = {"transition_id": "TX-PENDING"}
    return assert_fail_closed(
        "pending transaction recovery barrier",
        lambda: idx.apply_add(add_plan()),
        "PENDING_TRANSACTION_EXISTS",
    )


def test_crash_after_desired_upsert_before_stale_delete():
    idx = base_index()
    idx.records["change:stale"] = {"source": "change.md", "document": "stale evidence"}
    idx.state["current_count"] = len(idx.records)
    result = idx.apply_change(
        change_plan(
            desired={
                "change:0": {"source": "change.md", "document": "desired replacement"},
                "change:new": {"source": "change.md", "document": "desired addition"},
            }
        ),
        crash_after_upsert=True,
    )
    assert_true(result["desired_present"], "desired representation survived interruption")
    assert_true(result["stale_present"], "stale representation remains until cleanup")
    assert_true("change:new" in idx.records, "new desired ID is present")
    assert_true("change:stale" in idx.records, "stale ID is still present")
    return result["status"]


def test_crash_during_delete_after_journal_creation():
    idx = base_index()
    result = idx.apply_delete(delete_plan(), crash_after_journal=True)
    assert_equal(result, "INTERRUPTED_AFTER_PENDING_JOURNAL", "delete crash marker")
    return assert_fail_closed(
        "pending journal blocks subsequent mutation",
        lambda: idx.apply_add(add_plan()),
        "PENDING_TRANSACTION_EXISTS",
    )


def test_foreign_ownership_collision():
    idx = base_index()
    idx.records["foreign:0"] = {"source": "other.md", "document": "foreign owner"}
    idx.state["current_count"] = len(idx.records)
    plan = add_plan(record_id="foreign:0")
    return assert_fail_closed(
        "foreign ownership collision",
        lambda: idx.apply_add(plan),
        "FOREIGN_OWNERSHIP_COLLISION",
    )


def test_ledger_chain_integrity():
    idx = base_index()
    plan_ab = add_plan(from_snapshot="A", to_snapshot="B", record_id="added:0")
    idx.apply_add(plan_ab)

    plan_ba = delete_plan(from_snapshot="B", to_snapshot="A")
    plan_ba["source"] = "added.md"
    idx.apply_delete(plan_ba)

    plan_ab_again = add_plan(from_snapshot="A", to_snapshot="B", record_id="added:0")
    idx.apply_add(plan_ab_again)

    first_ab = idx.ledger[1]
    second_ab = idx.ledger[3]
    assert_equal(first_ab["edge_id"], second_ab["edge_id"], "repeated A to B edge identity")
    assert_true(
        first_ab["transition_id"] != second_ab["transition_id"],
        "chained transition identity distinguishes repeated A to B edge",
    )
    return "CHAINED_TRANSITIONS_DISTINCT"


def test_tampered_state_ledger_and_records():
    idx = base_index()
    idx.state["current_count"] = 999
    return assert_fail_closed(
        "tampered state count",
        lambda: idx.apply_add(add_plan()),
        "STATE_COUNT_MISMATCH",
    )


def main():
    tests = [
        test_unexpected_pre_existing_add,
        test_missing_change_source,
        test_already_absent_delete_source,
        test_snapshot_mismatch,
        test_replay_idempotence,
        test_pending_transaction_recovery_barrier,
        test_crash_after_desired_upsert_before_stale_delete,
        test_crash_during_delete_after_journal_creation,
        test_foreign_ownership_collision,
        test_ledger_chain_integrity,
        test_tampered_state_ledger_and_records,
    ]
    results = {}
    for test in tests:
        results[test.__name__] = test()

    report = {
        "status": "passed",
        "mode": "synthetic state-machine validation",
        "tests": results,
        "not_validated": [
            "Chroma collection behavior",
            "HNSW cosine retrieval",
            "SQLite FTS synchronization",
            "embedding generation or vector equality",
            "Magician/WSL recovered-baseline integration",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"SYNTHETIC_FAILURE_SEMANTICS_FAIL: {exc}", file=sys.stderr)
        raise

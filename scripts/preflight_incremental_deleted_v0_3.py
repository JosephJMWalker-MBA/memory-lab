import json
import pathlib
import sys
import chromadb


db_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
plan_path = pathlib.Path(sys.argv[2]).resolve()
state_path = db_path / "incremental-state.json"
ledger_path = db_path / "incremental-ledger.jsonl"

with plan_path.open("r", encoding="utf-8-sig") as f:
    plan = json.load(f)
with state_path.open("r", encoding="utf-8-sig") as f:
    state = json.load(f)

if plan.get("added"):
    raise RuntimeError("DELETE PREFLIGHT REFUSES ADDED SOURCES")
if plan.get("changed"):
    raise RuntimeError("DELETE PREFLIGHT REFUSES CHANGED SOURCES")
if not plan.get("deleted"):
    raise RuntimeError("NO DELETED SOURCES")

ledger_ids = set()
with ledger_path.open("r", encoding="utf-8-sig") as f:
    for line in f:
        if line.strip():
            ledger_ids.add(json.loads(line).get("transition_id"))

if state.get("last_transition_id") not in ledger_ids:
    raise RuntimeError("STATE LAST TRANSITION NOT PRESENT IN LEDGER")

client = chromadb.PersistentClient(path=str(db_path))
collections = client.list_collections()
if len(collections) != 1:
    raise RuntimeError("Expected exactly one collection")

name = collections[0].name if hasattr(collections[0], "name") else str(collections[0])
collection = client.get_collection(name)
count_before = collection.count()

if state["current_snapshot"] != plan["from_snapshot"]:
    raise RuntimeError("STATE SNAPSHOT DOES NOT MATCH PLAN FROM")
if state["current_count"] != count_before:
    raise RuntimeError("STATE COUNT DOES NOT MATCH COLLECTION")

anomalies = []
seen_sources = set()
delete_ids = []

for group in plan["deleted"]:
    source = group["source"]

    if source in seen_sources:
        anomalies.append("DUPLICATE_DELETED_SOURCE: " + source)
    seen_sources.add(source)

    got = collection.get(
        where={"source": source},
        include=["metadatas"],
    )
    ids = sorted(got.get("ids") or [])

    if not ids:
        anomalies.append("DELETED_SOURCE_MISSING_FROM_INDEX: " + source)

    delete_ids.extend(ids)

    print()
    print("DELETED_SOURCE:", source)
    print(" CURRENT_IDS:", ids)
    print(" TO_DELETE:", len(ids))

if len(delete_ids) != len(set(delete_ids)):
    anomalies.append("DUPLICATE_DELETE_IDS")

expected_after = count_before - len(delete_ids)

print()
print("COLLECTION:", name)
print("COUNT_BEFORE:", count_before)
print("STATE_CURRENT_SNAPSHOT:", state["current_snapshot"])
print("PLAN_FROM:", plan["from_snapshot"])
print("PLAN_TO:", plan["to_snapshot"])
print("DELETE_RECORDS:", len(delete_ids))
print("EXPECTED_COUNT_AFTER:", expected_after)
print("ANOMALIES:", len(anomalies))

for anomaly in anomalies:
    print(" !", anomaly)

if anomalies:
    print("DELETED_PREFLIGHT_FAIL_CLOSED")
    raise SystemExit(2)

print("STATE_ACTION: READY_TO_APPLY_DELETED")
print("INCREMENTAL_DELETED_PREFLIGHT_OK")

import chromadb
import hashlib
import json
import os
import pathlib
import sqlite3
import sys
from datetime import datetime, timezone


db_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
plan_path = pathlib.Path(sys.argv[2]).resolve()
result_path = pathlib.Path(sys.argv[3]).resolve()
state_path = db_path / "incremental-state.json"
ledger_path = db_path / "incremental-ledger.jsonl"
pending_path = db_path / "incremental-pending.json"

with plan_path.open("r", encoding="utf-8-sig") as f:
    plan = json.load(f)
with state_path.open("r", encoding="utf-8-sig") as f:
    state = json.load(f)

if pending_path.exists():
    raise RuntimeError("PENDING TRANSACTION EXISTS; RECOVERY REQUIRED")
if plan.get("added"):
    raise RuntimeError("V0.3 REFUSES ADDED SOURCES")
if plan.get("changed"):
    raise RuntimeError("V0.3 REFUSES CHANGED SOURCES")
if not plan.get("deleted"):
    raise RuntimeError("NO DELETED SOURCES")

ledger_entries = []
with ledger_path.open("r", encoding="utf-8-sig") as f:
    for line in f:
        if line.strip():
            ledger_entries.append(json.loads(line))

ledger_ids = {x.get("transition_id") for x in ledger_entries}
parent_transition_id = state.get("last_transition_id")

if parent_transition_id not in ledger_ids:
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

deleted_sources = []
delete_ids = []

for group in plan["deleted"]:
    source = group["source"]
    got = collection.get(where={"source": source}, include=["metadatas"])
    ids = sorted(got.get("ids") or [])

    if not ids:
        raise RuntimeError("DELETED SOURCE MISSING FROM INDEX: " + source)

    deleted_sources.append(source)
    delete_ids.extend(ids)

if len(delete_ids) != len(set(delete_ids)):
    raise RuntimeError("DUPLICATE DELETE IDS")

count_after_expected = count_before - len(delete_ids)

edge_core = {
    "from_snapshot": plan["from_snapshot"],
    "to_snapshot": plan["to_snapshot"],
    "deleted_sources": sorted(deleted_sources),
    "deleted_ids": sorted(delete_ids),
    "count_before": count_before,
    "count_after": count_after_expected,
}

edge_bytes = json.dumps(edge_core, sort_keys=True, separators=(",", ":")).encode("utf-8")
edge_id = "EDGE-" + hashlib.sha256(edge_bytes).hexdigest()[:16]

commit_core = {
    "parent_transition_id": parent_transition_id,
    "edge_id": edge_id,
}
commit_bytes = json.dumps(commit_core, sort_keys=True, separators=(",", ":")).encode("utf-8")
transition_id = "TX-" + hashlib.sha256(commit_bytes).hexdigest()[:16]

if transition_id in ledger_ids:
    raise RuntimeError("TRANSITION ID ALREADY EXISTS")

pending = {
    "schema": "incremental-pending-v0.3",
    "status": "prepared",
    "mutation_type": "deleted",
    "transition_id": transition_id,
    "edge_id": edge_id,
    "parent_transition_id": parent_transition_id,
    **edge_core,
}

with pending_path.open("x", encoding="utf-8") as f:
    json.dump(pending, f, ensure_ascii=False, indent=2)
    f.flush()
    os.fsync(f.fileno())

# Destructive operation begins only after pending journal is durable.
collection.delete(ids=delete_ids)

count_after = collection.count()
if count_after != count_after_expected:
    raise RuntimeError("COUNT MISMATCH AFTER DELETE")

# Deleted sources must now have no indexed records.
for source in deleted_sources:
    got = collection.get(where={"source": source}, include=["metadatas"])
    if got.get("ids"):
        raise RuntimeError("DELETED SOURCE STILL PRESENT: " + source)

# Deleted IDs must not be visible through Chroma.
got = collection.get(ids=delete_ids, include=["metadatas"])
if got.get("ids"):
    raise RuntimeError("DELETED IDS STILL PRESENT: " + repr(got["ids"]))

# Chroma FTS must contract with the collection.
sqlite_path = db_path / "chroma.sqlite3"
con = sqlite3.connect("file:" + str(sqlite_path) + "?mode=ro", uri=True)
cur = con.cursor()

fts_count = cur.execute(
    "SELECT count(*) FROM embedding_fulltext_search"
).fetchone()[0]

if fts_count != count_after:
    raise RuntimeError("FTS COUNT DOES NOT MATCH COLLECTION COUNT")

placeholders = ",".join("?" for _ in delete_ids)
rows = cur.execute(
    "SELECT e.embedding_id "
    "FROM embedding_fulltext_search f "
    "JOIN embeddings e ON e.id = f.rowid "
    "WHERE e.embedding_id IN (" + placeholders + ")",
    delete_ids,
).fetchall()
con.close()

fts_deleted_ids_remaining = sorted({row[0] for row in rows})
if fts_deleted_ids_remaining:
    raise RuntimeError("DELETED IDS STILL PRESENT IN FTS: " + repr(fts_deleted_ids_remaining))

entry = {
    "schema": "incremental-index-ledger-entry-v0.3",
    "transition_id": transition_id,
    "edge_id": edge_id,
    "parent_transition_id": parent_transition_id,
    "status": "committed",
    "mutation_type": "deleted",
    "committed_at_utc": datetime.now(timezone.utc).isoformat(),
    **edge_core,
}

new_state = dict(state)
new_state["current_snapshot"] = plan["to_snapshot"]
new_state["current_count"] = count_after
new_state["last_transition_id"] = transition_id
new_state["last_transition_type"] = "deleted"
new_state["last_edge_id"] = edge_id

temp_state = db_path / "incremental-state.json.tmp"
with temp_state.open("w", encoding="utf-8") as f:
    json.dump(new_state, f, ensure_ascii=False, indent=2)
    f.flush()
    os.fsync(f.fileno())

with ledger_path.open("a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    f.flush()
    os.fsync(f.fileno())

os.replace(temp_state, state_path)

result = {
    "schema": "incremental-deleted-result-v0.3",
    "status": "passed",
    "transition_id": transition_id,
    "edge_id": edge_id,
    "parent_transition_id": parent_transition_id,
    **edge_core,
    "fts_count_after": fts_count,
    "fts_deleted_ids_remaining": fts_deleted_ids_remaining,
}

with result_path.open("w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

pending_path.unlink()

print("COLLECTION:", name)
print("COUNT_BEFORE:", count_before)
print("DELETED_SOURCES:", sorted(deleted_sources))
print("DELETED_IDS:", sorted(delete_ids))
print("COUNT_AFTER:", count_after)
print("FTS_COUNT:", fts_count)
print("FTS_DELETED_IDS_REMAINING:", fts_deleted_ids_remaining)
print("FROM:", plan["from_snapshot"])
print("TO:", plan["to_snapshot"])
print("PARENT_TRANSITION_ID:", parent_transition_id)
print("EDGE_ID:", edge_id)
print("TRANSITION_ID:", transition_id)
print("RESULT:", result_path)
print("PRODUCTION_COMPATIBLE_INCREMENTAL_DELETED_OK")

# Incremental ingestion protocol

This document captures the currently validated mutation semantics for a legacy-compatible Chroma/HNSW retrieval index.

## Preconditions

An incremental plan is always defined between two deterministic source snapshots:

```text
FROM snapshot -> TO snapshot
```

The index carries a state record naming the snapshot it currently claims to represent. A mutation is authorized only when the state, collection count, and source-specific expectations agree with the plan.

## Added source

For an `ADDED` source, preflight requires that the source have no existing indexed records. Existing records are treated as drift, not as an invitation to silently repair state.

Mutation order:

1. Generate legacy-compatible chunks and embeddings.
2. Verify desired IDs do not already exist under another source.
3. Add records.
4. Verify count increase.
5. Verify documents and metadata by ID.
6. Verify FTS synchronization.
7. Verify exact-vector HNSW reachability.
8. Commit state / ledger.

## Changed source

A changed source is regenerated as a whole source representation. This is intentionally source-granular even when only a few characters changed, because chunk boundaries and location-derived IDs can shift.

Mutation order:

1. Generate full desired representation for the changed source.
2. Read the current source record set.
3. Compute stale IDs = current IDs - desired IDs.
4. Upsert all desired records first.
5. Verify desired documents, metadata, embeddings, and source ownership.
6. Delete stale IDs afterward.
7. Verify final source ID set equals desired ID set exactly.
8. Verify collection / FTS counts.
9. Verify desired vectors remain reachable.
10. Commit state / ledger.

### Why upsert before stale deletion?

If the process dies after upsert but before stale deletion, retrieval may temporarily contain stale evidence but still retains the desired replacement. If deletion happened first, a crash could destroy the last known-good representation before its replacement exists.

## Deleted source

A deleted source has no desired replacement.

Mutation order:

1. Verify the source currently exists.
2. Discover the exact current IDs belonging to that source.
3. Persist a pending transaction journal.
4. Delete exactly those IDs.
5. Verify source lookup returns no records.
6. Verify deleted IDs are absent by ID lookup and FTS.
7. Verify count contraction.
8. Append a committed ledger entry and update state.
9. Remove the pending journal.

A surviving pending journal means recovery is required before another mutation is allowed.

## Replay and drift

Three outcomes are meaningful:

### READY_TO_APPLY

The index state matches the plan's `from_snapshot` and all source-specific invariants pass.

### ALREADY_COMMITTED_NOOP

The state already equals the plan's `to_snapshot`, an exact matching committed ledger entry exists, and the resulting source records are verified. Replaying the transition performs no mutation.

### FAIL_CLOSED

Examples:

- added source unexpectedly already has records;
- changed source is missing from the index;
- deleted source is already absent when the state claims otherwise;
- collection count disagrees with state;
- desired chunk ID is owned by another source;
- a pending transaction exists;
- current state is neither the plan's `from_snapshot` nor a verifiable committed `to_snapshot`.

## Transaction identity

A source edge (`FROM -> TO` plus mutation details) can be hashed into an `EDGE-*` identity. A committed transaction should additionally incorporate the previous committed transaction ID so historical cycles such as:

```text
A -> B -> A -> B
```

produce distinct commit identities rather than colliding on the repeated `A -> B` edge.

## Operational note

Long-running audits and maintenance jobs should be detached from interactive SSH sessions. A connection reset must not terminate or ambiguously interrupt a node-owned maintenance task.

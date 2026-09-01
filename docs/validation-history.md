# Validation history

This document records what has actually been demonstrated. Designed-but-untested behavior should not be promoted into this list until exercised.

## Recovered baseline

- Canonical source corpus: 4,488 Markdown files in the validated snapshot.
- Recovered Chroma collection: 302,240 live chunks.
- Chroma FTS: 302,240 live lexical rows.
- Embedding model: `all-MiniLM-L6-v2`, 384 dimensions.
- Vector distance: cosine.

Private source content and local filesystem paths are intentionally omitted from this public repository.

## Legacy compatibility audit

Six structurally different source documents were regenerated under the WSL query-encoder runtime and compared with their records in the recovered baseline.

Aggregate result:

- sources: 6
- chunks compared: 2,756
- missing IDs: 0
- unexpected IDs: 0
- metadata mismatches: 0
- text mismatches: 0

The audit covered small and very large sources, including one source with more than 1,700 chunks. This demonstrated compatibility of chunk IDs, boundaries, documents, headings, folders, tags, categories, auto-tags, and zero-based start-line metadata for the tested sample.

## Deterministic source snapshots

A source snapshot was generated twice from the same corpus and reproduced the same snapshot identity. A disposable corpus with one synthetic source produced an exact delta:

- added: 1
- changed: 0
- deleted: 0
- unchanged: 4,488

Deleting that synthetic source later returned the corpus to the exact original source snapshot identity, demonstrating deterministic round-trip identity for the test.

## Incremental ADD

A production-compatible synthetic source was chunked using the frozen legacy identity scheme and incrementally added to a clean clone of the recovered baseline.

Demonstrated:

- collection count: 302,240 -> 302,241;
- record readback by ID;
- 384-dimensional embedding readback;
- FTS count: 302,241;
- FTS ID presence;
- exact-vector HNSW self-query rank: 1;
- fail-closed preflight against a deliberately contaminated test index.

## Replay idempotence

The committed ADD transition was replayed after state/ledger bootstrap. The state-aware preflight matched the exact committed transition, verified resulting source IDs and documents, and returned an explicit `ALREADY_COMMITTED_NOOP` rather than treating the existing source as drift.

## Incremental CHANGE: expansion

The synthetic source was changed from one desired chunk to two.

Demonstrated:

- existing legacy chunk ID updated in place by upsert;
- second legacy chunk inserted in the same source transition;
- count: 302,241 -> 302,242;
- FTS count synchronized to 302,242;
- both desired vectors returned rank 1 on exact-vector query;
- state and ledger advanced only after verification.

## Incremental CHANGE: contraction / stale deletion

The synthetic source was changed from two desired chunks back to one.

Demonstrated:

- desired replacement upserted first;
- replacement verified before destructive cleanup;
- one stale chunk deleted afterward;
- count: 302,242 -> 302,241;
- FTS count synchronized to 302,241;
- surviving desired vector returned rank 1;
- state and ledger advanced after final verification.

## Incremental DELETE

The synthetic source was removed from the source corpus and the resulting deletion plan targeted exactly one current indexed record.

Demonstrated:

- delete preflight matched state snapshot and current index count;
- pending transaction journal created before deletion;
- exactly one source ID deleted;
- count: 302,241 -> 302,240;
- FTS count: 302,240;
- deleted ID absent from FTS afterward;
- ledger entry chained to the preceding transition;
- source snapshot returned to the exact original snapshot identity.

## Full round-trip audit

A full logical equivalence audit was started between the untouched recovered baseline and the round-tripped incremental test index. The first interactive run was interrupted by an SSH connection reset after more than 50,000 records. The audit itself was read-only; the validated index state was not mutated. Long-running reruns are intended to execute detached from SSH.

**Status:** pending final complete result. Do not yet claim full 302,240-record logical equivalence until the detached audit finishes successfully.

## Retrieval findings retained from earlier experiments

- Vector retrieval is strong for named projects, technical concepts, and semantic paraphrases.
- Literal / lexical retrieval provides complementary recall, especially for exact phrases and opaque identifiers.
- Equal chunk-level fusion can over-weight multiple weak chunks from one source.
- Source-level aggregation can recover agreement that is invisible at exact chunk level.
- Cross-encoder reranking can rescue some lexical candidates but can degrade already-solved easy cases; it should not be treated as a universal final ranker.
- Temporal, causal, and autobiographical relationships often require derived relational memory rather than expecting conventional chunk retrieval to reconstruct them reliably.

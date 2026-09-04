# Validation history

This document records what has actually been demonstrated. Designed-but-untested behavior should not be promoted into this list until exercised.

## Recovered baseline

- Canonical source corpus: 4,488 Markdown files in the validated snapshot.
- Recovered Chroma collection: 302,240 live chunks.
- Chroma FTS: 302,240 live lexical rows.
- Embedding model: `all-MiniLM-L6-v2`, 384 dimensions.
- Vector distance: cosine.

Private source content and local filesystem paths are intentionally omitted from this public repository.

## Public synthetic validation

The environment-independent public fixture in `fixtures/synthetic-lifecycle/`
has been reproduced with:

```bash
python3 tests/run_synthetic_lifecycle.py
```

This public check validates deterministic synthetic snapshot reproduction, exact
ADD / CHANGE / DELETE classification, legacy-v1 chunk ID mechanics,
zero-based heading line handling, Windows-style nested relative source identity,
final source snapshot equality, and final logical chunk-record equality.

The fixture sequence is:

```text
S0 -> ADD -> CHANGE expansion -> CHANGE contraction -> DELETE -> S4
```

`S4` intentionally equals `S0`. This is reproduced with public synthetic
fixture data only. It does not validate the recovered baseline, Chroma
cardinality, HNSW cosine retrieval, SQLite FTS, embedding vectors, or the
pending full 302,240-record logical equivalence audit.

## Public synthetic state-machine validation

The environment-independent failure-semantics runner has been reproduced with:

```bash
python3 tests/run_failure_semantics.py
```

This is synthetic state-machine validation only. It demonstrates fail-closed
handling for unexpected pre-existing ADD records, missing CHANGE sources,
already-absent DELETE sources, snapshot mismatch, pending transaction barriers,
foreign ownership collisions, and tampered state/ledger/record disagreement.

It also demonstrates replay idempotence as an explicit no-op only when the
committed transition and resulting state can be verified, CHANGE interruption
semantics that preserve desired evidence before stale cleanup, DELETE
interruption detection through a surviving pending journal, and chained ledger
identity for repeated `A -> B -> A -> B` source edges.

This is reproduced with public synthetic fixture logic. It is not recovered
baseline integration validation and does not validate Chroma, HNSW, FTS,
embeddings, or the pending 302,240-record equivalence audit.

## Public contract schema validation

The environment-independent public contract schemas have been reproduced with:

```bash
python3 tests/run_contract_schema_validation.py
```

This validates structurally correct synthetic source snapshot, source delta,
mutation plan, index state, pending transaction, and ledger-entry artifacts. It
also demonstrates schema rejection for missing identity/provenance fields,
malformed mutation types, incomplete pending transactions, ledger entries
missing chain identity, invalid snapshot identifiers, and unexpected additional
fields.

This is public research contract validation. It is pending Magician comparison
and is not a claim that the schemas reproduce undocumented recovered
implementation file formats.

## Legacy compatibility audit

Six structurally different source documents were regenerated under the WSL query-encoder runtime and compared with their records in the recovered baseline.

Aggregate result:

- sources: 6
- chunks compared: 2,756
- missing IDs: 0
- unexpected IDs: 0
- metadata mismatches: 0
- text mismatches: 0

The audit covered small and very large sources, including one source with more than 1,700 chunks. This validated against recovered baseline compatibility of chunk IDs, boundaries, documents, headings, folders, tags, categories, auto-tags, and zero-based start-line metadata for the tested sample.

## Deterministic source snapshots

A source snapshot was generated twice from the same corpus and reproduced the same snapshot identity. A disposable corpus with one synthetic source produced an exact delta:

- added: 1
- changed: 0
- deleted: 0
- unchanged: 4,488

Deleting that synthetic source later returned the corpus to the exact original source snapshot identity, demonstrating deterministic round-trip identity for the test.

## Incremental ADD

A production-compatible synthetic source was chunked using the frozen legacy identity scheme and incrementally added to a clean clone of the recovered baseline.

Validated against recovered baseline:

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

Validated against recovered baseline:

- existing legacy chunk ID updated in place by upsert;
- second legacy chunk inserted in the same source transition;
- count: 302,241 -> 302,242;
- FTS count synchronized to 302,242;
- both desired vectors returned rank 1 on exact-vector query;
- state and ledger advanced only after verification.

## Incremental CHANGE: contraction / stale deletion

The synthetic source was changed from two desired chunks back to one.

Validated against recovered baseline:

- desired replacement upserted first;
- replacement verified before destructive cleanup;
- one stale chunk deleted afterward;
- count: 302,242 -> 302,241;
- FTS count synchronized to 302,241;
- surviving desired vector returned rank 1;
- state and ledger advanced after final verification.

## Incremental DELETE

The synthetic source was removed from the source corpus and the resulting deletion plan targeted exactly one current indexed record.

Validated against recovered baseline:

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

## Implementation categories

- `validated against recovered baseline`: exercised against the private recovered
  Chroma/FTS/vector index or its recovered source snapshot.
- `reproduced with public synthetic fixture`: exercised by the public fixture and
  environment-independent runner.
- `pending exact validated-script migration`: validated local scripts that must
  be imported from exact files rather than recreated from documentation.
- `designed but unimplemented`: architectural direction that is not yet
  executable behavior, including derived memory.

## Retrieval findings retained from earlier experiments

- Vector retrieval is strong for named projects, technical concepts, and semantic paraphrases.
- Literal / lexical retrieval provides complementary recall, especially for exact phrases and opaque identifiers.
- Equal chunk-level fusion can over-weight multiple weak chunks from one source.
- Source-level aggregation can recover agreement that is invisible at exact chunk level.
- Cross-encoder reranking can rescue some lexical candidates but can degrade already-solved easy cases; it should not be treated as a universal final ranker.
- Temporal, causal, and autobiographical relationships often require derived relational memory rather than expecting conventional chunk retrieval to reconstruct them reliably.

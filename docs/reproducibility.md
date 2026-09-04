# Public reproducibility lane

Memory Lab separates public reproducibility from private-corpus validation. The
public lane uses only invented Markdown fixtures and environment-independent
Python checks. It does not require Magician, WSL, Chroma, HNSW indexes, FTS
tables, embeddings, or private source archives.

## Synthetic lifecycle

The fixture in `fixtures/synthetic-lifecycle/` models this sequence:

```text
S0
  -> ADD
  -> CHANGE expansion
  -> CHANGE contraction
  -> DELETE
  -> S4
```

`S0` is the baseline corpus. `S1` adds `foxtrot-added.md`. `S2` expands
`charlie-expand.md`. `S3` contracts `delta-contract.md`. `S4` deletes the added
source and restores the changed sources to their baseline content.

The final state intentionally satisfies:

```text
S4 == S0
```

That equality matters because it proves the public fixture can express a full
round trip through source additions, source-granular changes, and deletion while
returning to the same deterministic source snapshot identity and the same
logical legacy chunk records.

## What the public test proves

`python3 tests/run_synthetic_lifecycle.py` proves, with public synthetic data:

- deterministic source snapshot reproduction;
- exact ADD / CHANGE / DELETE classification;
- legacy-v1 chunk ID mechanics for heading-derived chunks;
- zero-based heading `start_line` handling;
- Windows-style nested relative source identity;
- final source snapshot equality between `S4` and `S0`;
- final logical chunk-record equality between `S4` and `S0`;
- a deliberately detectable contaminated-state condition that integration
  scripts must fail closed against.

This is reproduced with the public synthetic fixture. It is not a recovered
baseline validation.

## What the public test does not prove

The public synthetic test does not prove:

- compatibility with all 302,240 recovered baseline records;
- Chroma collection cardinality;
- HNSW cosine retrieval behavior;
- embedding generation or 384-dimensional vector equality;
- SQLite FTS cardinality or deleted-ID absence;
- pending journal durability around real index mutation;
- ledger advancement in a real index directory;
- exact behavior of validated local scripts that are still pending import;
- derived-memory behavior beyond the separate experimental synthetic v0 lane.

The full 302,240-record logical equivalence audit remains a separate validation
lane tracked by GitHub Issue #2. Synthetic logical equality is useful because it
is public and reproducible in CI, but it is not evidence that the private
round-tripped index is fully equivalent to the recovered baseline.

## Environment-specific validations

These validations require the private or platform-specific environment and are
not part of the public CI lane:

- Magician Windows machine: access to the known validated workspace and exact
  local scripts that are pending exact validated-script migration.
- WSL: recovered legacy query-encoder runtime used for validated local
  compatibility checks.
- Chroma: persistent collection creation, mutation, and count verification.
- HNSW: exact-vector cosine reachability and rank checks.
- SQLite FTS: lexical row cardinality and deleted-ID absence checks.

Until the exact validated local scripts are imported and sanitized, their
repository state remains pending exact validated-script migration rather than
public validation.

## Synthetic state-machine validation

The public failure-semantics runner exercises mutation protocol invariants
without pretending to validate Chroma, embeddings, HNSW, or FTS behavior:

```bash
python3 tests/run_failure_semantics.py
```

The fail-closed philosophy is that disagreement among the plan, claimed state,
ledger, pending journal, or current logical records must stop mutation. The
public tests cover unexpected pre-existing ADD records, missing CHANGE sources,
already-absent DELETE sources, snapshot mismatch, foreign ownership collisions,
pending transaction barriers, and tampered state/ledger/record disagreement.

Replay is not treated as drift when the exact previously committed transition
can be verified. It is an explicit no-op only when the ledger entry, chained
transition identity, resulting snapshot, and logical record count agree.

Interruption is part of the protocol, not an operational afterthought. For
CHANGE, evidence continuity has priority over cleanup convenience: the desired
representation must exist before stale records are destructively removed, so an
interruption may leave temporary stale evidence rather than lose the desired
replacement. For DELETE, a durable pending marker must exist before destructive
removal begins, so an interrupted deletion is detectable and blocks subsequent
mutation until recovery is resolved.

The synthetic state-machine tests prove these control-flow invariants over
invented logical records. They do not prove recovered-baseline compatibility,
real Chroma mutation, HNSW reachability, SQLite FTS synchronization, embedding
readback, or exact validated-script behavior. Those remain dependent on the
Magician/WSL integration environment and pending exact validated-script
migration.

## Public contract validation

The public schema runner validates the versioned state-machine contracts:

```bash
python3 tests/run_contract_schema_validation.py
```

It checks valid synthetic snapshot, delta, mutation plan, index state, pending
transaction, and ledger-entry artifacts against standard JSON Schema files in
`schemas/`. It also verifies that missing identity/provenance fields, malformed
mutation types, incomplete pending transactions, ledger entries missing chain
identity, invalid snapshot identifiers, and unexpected additional fields are
rejected.

Schema validity remains separate from transition validity. A mutation plan can
be structurally valid while still being unsafe to apply because its
`from_snapshot` does not match the current index state. Those cross-object
invariants stay in the synthetic state-machine tests.


## Experimental derived-memory v0

The public derived-memory experiment runs with:

```bash
python3 tests/run_derived_memory_v0.py
```

It uses only fictional normalized evidence in
`fixtures/derived-memory-v0/evidence.json`. The normalization step is treated
as given so the experiment can isolate derived-memory semantics from extraction
quality.

The test exercises corroboration, temporal supersession, contradiction,
explicit correction, unsupported-inference revision, record-schema validation,
and evidence immutability. It distinguishes evidence change from world-state
change and interpretation change.

This lane does not validate LLM extraction, retrieval selection, private corpus
behavior, confidence calibration, or production persistence. See
`docs/derived-memory-v0.md`.


## Adversarial derived-memory semantics

The adversarial public experiment runs with:

```bash
python3 tests/run_derived_memory_adversarial.py
```

It uses only `fixtures/derived-memory-adversarial/evidence.json` and tests the
difference between local evidentiary support and evidence-set coverage,
qualifier preservation, recursive provenance, cycle rejection, and valid-time
versus knowledge-time semantics.

The fixture is closed-world solely so omitted relevant evidence can be detected
deterministically. Real retrieval completeness remains unknown unless a bounded
system can actually prove it. See `docs/derived-memory-adversarial.md`.

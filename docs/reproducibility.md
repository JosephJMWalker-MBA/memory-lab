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
- derived memory behavior, which is designed but unimplemented.

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

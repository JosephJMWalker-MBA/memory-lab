# Synthetic lifecycle fixture

This fixture is fully invented public data. It is designed to exercise the
incremental ingestion protocol without copying private source text.

Lifecycle:

```text
S0 baseline
  -> S1 ADD foxtrot-added.md
  -> S2 CHANGE expansion in charlie-expand.md
  -> S3 CHANGE contraction in delta-contract.md
  -> S4 DELETE foxtrot-added.md and restore changed sources to S0 content
```

The final source state intentionally equals the baseline:

```text
S4 == S0
```

The fixture includes:

- a single-section Markdown source;
- a multi-heading Markdown source;
- an opaque lexical marker;
- a metadata-like source;
- a nested source for Windows-style relative source identity;
- expansion, contraction, deletion, and unchanged cases.

Run the public environment-independent check with:

```bash
python3 tests/run_synthetic_lifecycle.py
```

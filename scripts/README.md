# Scripts

The local Memory Lab workspace contains a growing set of validated scripts. This public repository should receive them only after they have been reviewed for hard-coded private paths, source-derived text, or machine-specific secrets.

## Migration status

Exact validated local implementations were not found in the current Mac
workspace during the first `build/reproducible-harness` migration pass. The
known validated workspace may exist on the separate Magician Windows machine and
was not available to this Codex session. Missing exact files remain pending
rather than being recreated from documentation.

### Included here

- `preflight_incremental_deleted_v0_3.py` — read-only delete preflight.
- `apply_incremental_deleted_v0_3.py` — delete transaction with pending journal, FTS verification, and chained ledger commit.

### Validated locally; exact sanitized import still pending

- `build_source_snapshot.py`
- `compare_source_snapshots.py`
- `regenerate_legacy_chunks.py`
- `verify_legacy_chunk_compat.py`
- `build_legacy_full_metadata_expected.py`
- `verify_legacy_full_metadata.py`
- `prepare_incremental_legacy_chunks.py`
- `inspect_incremental_legacy_plan.py`
- `preflight_incremental_legacy_plan.py`
- `embed_incremental_legacy_plan.py`
- `apply_incremental_added_v0_1.py`
- `verify_incremental_added_vector.py`
- `bootstrap_incremental_index_state.py`
- `preflight_incremental_with_state.py`
- `preflight_incremental_changed_v0_2.py`
- `apply_incremental_changed_v0_2.py`
- `audit_roundtrip_logical_equivalence.py`

The migration rule is deliberately conservative: do not retype a locally validated script from memory and silently call it equivalent. Import the actual validated file, sanitize only deployment-specific material, and re-run its relevant fixture tests before marking the repository copy validated.

## Synthetic lifecycle regression

The public repository includes a fully invented Markdown lifecycle fixture under
`fixtures/synthetic-lifecycle/` and an environment-independent runner:

```bash
python3 tests/run_synthetic_lifecycle.py
```

This check validates deterministic synthetic snapshot reproduction, exact delta
classification, legacy-v1 chunk ID mechanics, zero-based heading line handling,
final source snapshot equality, final logical chunk equality, and a deliberately
detectable contaminated-state condition. Chroma, HNSW, embeddings, pending
journal execution, ledger advancement, FTS cardinality, and collection
cardinality remain integration checks until the exact validated scripts and
runtime are imported.

For per-script state and reasons, see `docs/script-migration-status.json`.

# Scripts

The local Memory Lab workspace contains a growing set of validated scripts. This public repository should receive them only after they have been reviewed for hard-coded private paths, source-derived text, or machine-specific secrets.

## Migration status

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

# Memory Lab

Memory Lab is a local-first research harness for provenance-aware semantic memory over immutable source archives.

The project separates three concerns that are often conflated in retrieval systems:

1. **Canonical source** — immutable source material and deterministic corpus snapshots.
2. **Retrieval indexes** — rebuildable vector and lexical structures used to locate evidence.
3. **Derived memory** — provenance-bearing facts, decisions, relationships, principles, and temporal transitions that can be verified, rejected, or superseded without rewriting source material.

## Current validated direction

The first implementation track has focused on incremental maintenance of a legacy-compatible Chroma/HNSW index. The test program has demonstrated:

- deterministic source snapshot identity and exact delta detection;
- regeneration of legacy chunk IDs, boundaries, text, and metadata under a WSL runtime;
- incremental `ADD` with vector and FTS synchronization;
- fail-closed detection of index/source drift;
- replay idempotence using an index-state ledger;
- `CHANGE` expansion and contraction with upsert-before-stale-delete ordering;
- `DELETE` with explicit transaction journaling;
- round-trip restoration of the logical source snapshot and index cardinality.

These are empirical validation claims, not claims that the system is finished. See [`docs/validation-history.md`](docs/validation-history.md).

## Design principles

- Canonical source is not silently rewritten.
- Retrieval chunks are evidence units; sources/conversations are retrieval units; derived records are relationship units.
- Exact identifiers and literal strings belong to lexical retrieval; semantic paraphrases belong to vector retrieval; neither should be forced to replace the other.
- Source snapshots make statements such as `unsupported_in_snapshot` precise rather than absolute.
- Incremental mutation fails closed when index state does not match the claimed source snapshot.
- Destructive operations occur only after replacement state has been materialized and verified when a replacement exists.
- Long-running maintenance jobs should be detached from interactive SSH sessions.

## Repository boundaries

This repository contains reusable code, contracts, sanitized fixtures, and validation documentation. It must **not** contain private source archives, personal transcripts, Chroma databases, embeddings, local state ledgers, or derived-memory records based on private material.

See [`docs/security-and-data-boundaries.md`](docs/security-and-data-boundaries.md) and [`.gitignore`](.gitignore).

## Status

Research / engineering harness. Interfaces and schemas are versioned as they are validated.

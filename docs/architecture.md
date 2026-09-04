# Architecture

Memory Lab is organized around a strict separation between source truth, retrieval machinery, and derived relational memory.

## 1. Canonical source

Canonical source is treated as immutable evidence. A source snapshot is a deterministic identity over the ordered corpus. The snapshot makes claims such as `unsupported_in_snapshot` precise: the claim means the available evidence was insufficient in a named corpus state, not that the proposition is permanently false.

The source layer owns:

- source files;
- deterministic file hashes;
- corpus snapshot identity;
- added / changed / deleted source deltas.

It does not own retrieval ranking or derived claims.

## 2. Retrieval layer

Retrieval indexes are rebuildable projections over canonical source. The validated baseline uses:

- ChromaDB for record persistence;
- HNSW cosine search;
- `all-MiniLM-L6-v2` embeddings (384 dimensions);
- Chroma's SQLite FTS table for literal / lexical retrieval;
- source-level aggregation above chunk-level evidence when useful.

A key empirical result is that opaque identifiers can be excellent lexical evidence and poor semantic queries. Vector and lexical retrieval therefore remain complementary rather than competing implementations of one universal lookup method.

### Retrieval unit hierarchy

- **Chunks** are evidence units.
- **Sources / conversations** are retrieval units.
- **Derived records** are relationship units.

This distinction matters for temporal, causal, and autobiographical questions that cannot reliably be reconstructed from a few independently ranked chunks.

## 3. Legacy chunk contract

The recovered baseline has a frozen compatibility contract. Incremental ingestion must reproduce that contract rather than silently inventing a new one for later records.

Validated properties include:

- Windows-style relative source paths are part of identity;
- `start_line` is zero-based;
- Markdown headings define primary sections;
- large sections are semantically sub-chunked at adjacent-paragraph cosine similarity below `0.45`;
- nominal maximum chunk size is 2000 characters;
- ordinary chunk ID: `MD5("<file_rel>:<start_line>")[:12]`;
- semantic subchunk ID: `MD5("<file_rel>:<start_line>:<subchunk_index>")[:12]`;
- metadata fields: `source`, `heading`, `folder`, `tags`, `category`, `auto_tags`, `start_line`;
- embedding model: `all-MiniLM-L6-v2`;
- distance: cosine.

The production incremental path intentionally preserves even awkward legacy edge behavior when that behavior participates in index identity.

## 4. Incremental mutation protocol

Incremental mutation is snapshot-driven and fail-closed.

### Added source

1. Prove index state corresponds to the plan's `from_snapshot`.
2. Require the added source to have no current records.
3. Generate legacy-compatible chunks and embeddings.
4. Add desired records.
5. Verify record, FTS, and vector reachability.
6. Commit state and ledger.

### Changed source

1. Regenerate the entire desired representation for the changed source.
2. Verify current index state.
3. **Upsert desired records first.**
4. Verify the desired representation exists.
5. Delete stale old IDs afterward.
6. Verify exact final source state, FTS count, and vector reachability.
7. Commit state and ledger.

This ordering chooses temporary stale evidence over temporary loss of the last known-good representation if a process crashes between mutation stages.

### Deleted source

1. Verify the source currently exists in the index.
2. Write a pending transaction journal durably.
3. Delete exactly the discovered source IDs.
4. Verify source absence, deleted-ID absence, and FTS contraction.
5. Append the ledger entry and advance state.
6. Remove the pending journal only after commit.

## 5. State, ledger, and replay

An index carries a small state record naming its claimed current source snapshot and last committed transaction. A ledger records committed transitions.

Replay semantics distinguish:

- unexpected pre-existing data -> **drift / fail closed**;
- exact previously committed transition with verified resulting state -> **idempotent no-op**;
- matching `from_snapshot` and clean preflight -> **ready to apply**.

Later transaction IDs should be chained to the previous committed transaction so repeated corpus edges (for example A -> B -> A -> B) remain distinct historical commits.

## 6. Derived memory

Derived memory does not rewrite source and does not inherit truth merely because
a model generated it. Derived records remain downstream interpretations with
explicit evidence references and source snapshot identity.

The first public executable model is **derived memory v0**, an experimental
synthetic research lane. It begins after evidence normalization and tests:

- stable derived identity with later corroborating evidence;
- temporal state and relationship supersession;
- unresolved contradictory evidence;
- explicit correction without source rewriting;
- unsupported-inference rejection and revision;
- backward attribution checking from a proposed conclusion to its evidence.

The v0 status vocabulary is `proposed`, `verified`, `rejected`,
`unresolved`, and `superseded`. Supersession is reason-sensitive: a later
record can replace an earlier one because the world changed, or because the
interpretation changed. Those cases are not equivalent.

v0 explicitly distinguishes:

- **evidence changed** — additional evidence supports the same proposition;
- **world state changed** — an older and newer derived state may both have been
  correct at different times;
- **interpretation changed** — the same or corrected evidence shows that an
  earlier interpretation was wrong or too strong.

The backward attribution check is not neural-network backpropagation. It is a
provenance check that traces a derived proposition back through its attributed
evidence and verifies whether the proposition is supported as written. Failure
revises or rejects the derived record, never the canonical evidence.

The public v0 schema intentionally omits scalar confidence because no calibrated
confidence model has yet been demonstrated. See
[`docs/derived-memory-v0.md`](derived-memory-v0.md).

An adversarial v0.1 lane extends this model where v0 proved too weak. It
separates local support from evidence-set coverage, treats qualifiers as part of
the proposition, preserves explicit recursive derivation dependencies plus
canonical evidence closure, and separates world-valid time from knowledge time.
See [`docs/derived-memory-adversarial.md`](derived-memory-adversarial.md).

A dependency-aware reassessment lane adds the complementary direction: when a
supporting derived record changes, Memory Lab computes the minimal reverse
dependency closure and appends reassessment results for affected conclusions.
Historical derived records are not rewritten, and withdrawal of support is not
treated as proof of the opposite proposition. See
[`docs/derived-reassessment-v0.md`](derived-reassessment-v0.md).

A multiple-justification refinement separates provenance ancestry from logical
necessity. A record can have several conjunctive justifications while remaining
active if **any** independent justification survives. This means "affected by a
support change" is not the same as "invalidated by that change." See
[`docs/multiple-justifications-v0.md`](multiple-justifications-v0.md).

This remains experimental synthetic semantics. LLM extraction, automatic
evidence normalization, real retrieval-coverage estimation, automatic discovery
of contrary evidence, private-corpus behavior, production persistence, and
general recursive reasoning remain unimplemented.

## 7. Runtime boundary

The validated implementation uses WSL for Chroma/HNSW read-write operations. Native Windows HNSW operations were not sufficiently reliable in the recovered environment. Long-running audits should run detached from interactive SSH sessions so terminal lifetime does not determine job lifetime.

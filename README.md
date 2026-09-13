# Memory Lab

> **Research into governed epistemic memory over time.**

Memory Lab studies how a system can preserve what was known, why it was believed, what evidence was considered, what remained unknown, how conclusions changed, and whether earlier conclusions should still participate in a later current view.

It is a local-first research and engineering harness, not a claim that one custom memory runtime should replace established truth-maintenance, provenance, temporal-knowledge, graph, or retrieval systems.

## Start here

Read:

1. [`STATUS.md`](STATUS.md) — current research state and next direction
2. [`AGENTS.md`](AGENTS.md) — prior-art-first operating guidance
3. [`docs/research-position.md`](docs/research-position.md) — what Memory Lab is trying to discover
4. [`docs/architecture.md`](docs/architecture.md) — current architecture and validated implementation tracks
5. [`docs/derived-memory-prior-art.md`](docs/derived-memory-prior-art.md) — established work constraining the research

For long-horizon reopening / historical-memory work, see:

[`docs/inheritance-without-foreclosure.md`](docs/inheritance-without-foreclosure.md)

## Core separations

Memory Lab began with a strict separation among:

1. **Canonical source** — immutable source material and deterministic corpus snapshots.
2. **Retrieval indexes** — rebuildable lexical/vector structures used to locate evidence.
3. **Derived memory** — provenance-bearing interpretations and relationships that may be reassessed without rewriting source material.

Prior-art pressure has sharpened the deeper research distinctions:

```text
local support
!= relevant evidence coverage

support validity
!= consistency validity

historical derived status
!= current-view admission

withdrawal of support
!= negation

world change
!= interpretation correction

preserved history
!= permanent veto
```

The project now treats these boundaries as the main research target.

## Prior-art posture

Large parts of memory machinery already have strong prior art.

Memory Lab does **not** claim to have invented:

- truth maintenance or dependency-aware belief revision;
- ATMS-style multiple support environments;
- provenance-bearing assertions;
- bitemporal knowledge;
- event-sourced retained history;
- temporal knowledge graphs;
- hybrid semantic / lexical / graph retrieval.

Relevant substrates include classical TMS / ATMS, W3C PROV, nanopublications and Whyis, temporal/bitemporal systems, event sourcing, Graphiti/Zep, and ordinary relational/application-state machinery.

The project should reuse those systems where they already solve the problem.

The strongest remaining question is whether Memory Lab's exact boundary discipline adds measurable value and whether that value is best delivered as:

```text
semantic contracts
+ adversarial fixtures
+ conformance tests
+ adapters
```

rather than another standalone memory engine.

See [`docs/research-position.md`](docs/research-position.md).

## Validated engineering track

One implementation track has deeply tested incremental maintenance of a recovered legacy-compatible Chroma/HNSW index. Work has demonstrated:

- deterministic source snapshot identity and exact delta detection;
- regeneration of legacy chunk IDs, boundaries, text, and metadata;
- incremental `ADD`, `CHANGE`, and `DELETE` behavior;
- vector and FTS synchronization;
- fail-closed source/index drift detection;
- replay idempotence and state-ledger behavior;
- transaction journaling;
- restoration to the original logical source/cardinality state.

These are useful empirical engineering results. They do **not** make Chroma/HNSW the canonical future Memory Lab or GEI runtime.

See [`docs/validation-history.md`](docs/validation-history.md).

## Derived-memory research

The synthetic research lanes test how interpretations remain accountable to evidence over time without rewriting history.

Current experiments cover:

- derived-record provenance and source-snapshot identity;
- local support checking;
- support vs evidence-set coverage;
- valid time vs knowledge time;
- explicit qualifiers;
- recursive derivation closure;
- dependency-aware reassessment;
- multiple independent justifications;
- conflict among individually supported records;
- historical record vs current-view participation.

The project deliberately omits scalar confidence until a meaningful calibration method is demonstrated.

These are synthetic semantics, not production-memory claims.

## Inheritance without foreclosure

Memory should prevent wasteful repetition without turning old conclusions into eternal vetoes.

A useful historical negative result needs more than:

```text
this failed
```

It should preserve:

```text
what was attempted
why it failed / was rejected / deferred
what assumptions and environment made that conclusion binding
what conditions would justify reconsideration
```

Then later work can distinguish:

```text
blind repetition of a known failure
!=
bounded re-test after material causal conditions changed
```

This is a research hypothesis, not an established result. See [`docs/inheritance-without-foreclosure.md`](docs/inheritance-without-foreclosure.md).

## Relationship to GIE / GEI

Memory Lab is a research site for **epistemic continuity**.

GIE/GEI does not need to deploy this repository as its production memory system.

A valid outcome is:

```text
Memory Lab
    discovers and tests the needed semantics

GEI
    composes those semantics over the simplest adequate runtime
```

If an existing system already provides the required responsibility end-to-end more simply, Memory Lab should narrow rather than compete with it.

## Repository boundary

This repository contains reusable code, schemas, contracts, sanitized fixtures, and validation documentation.

It must **not** contain private source archives, personal transcripts, private Chroma databases, embeddings, local state ledgers, or derived-memory records based on private material.

See [`docs/security-and-data-boundaries.md`](docs/security-and-data-boundaries.md) and [`.gitignore`](.gitignore).

## Status

Research / engineering harness in a **prior-art integration + semantic hardening** phase.

The goal is not to maximize custom architecture.

The goal is to discover the smallest governed-memory model that survives comparison with reality and established systems.

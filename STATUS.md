# Memory Lab Status

**Standing:** active research / engineering harness  
**Current phase:** prior-art integration + semantic hardening  
**Runtime choice:** unresolved / deliberately replaceable  

## Current identity

Memory Lab studies governed epistemic memory over time.

It is not currently committed to becoming the production memory runtime for GIE/GEI or any other system.

The current research question is:

> What memory semantics are actually required to preserve evidence, justification, uncertainty, contradiction, reassessment, historical state, and current-view participation without silently rewriting history or turning prior conclusions into permanent vetoes?

See `docs/research-position.md`.

## Validated engineering track

The incremental retrieval-maintenance track has demonstrated substantial mechanics around a recovered legacy-compatible Chroma/HNSW index, including:

- deterministic source snapshots and deltas;
- legacy-compatible chunk regeneration;
- incremental ADD / CHANGE / DELETE behavior;
- vector + FTS synchronization;
- fail-closed drift detection;
- replay / ledger behavior;
- transaction journaling;
- restoration to baseline logical source/cardinality state.

These are useful engineering results.

They do **not** establish that Chroma/HNSW is the preferred future Memory Lab or GIE/GEI memory substrate.

Open engineering issues #1 and #2 remain about migration / full equivalence auditing of that track.

## Validated synthetic semantics

The synthetic derived-memory lanes currently exercise:

- provenance-bearing derived records;
- support checking;
- support vs evidence-coverage separation;
- valid time vs knowledge time;
- explicit qualifiers;
- recursive derivation closure;
- dependency-aware reassessment;
- withdrawal without invented negation;
- multiple independent justifications;
- support validity vs joint consistency;
- historical record vs current-view participation;
- preservation of contradictory support states.

These demonstrate internally executable semantics over synthetic fixtures.

They do **not** establish production utility, real-corpus coverage estimation, general nonmonotonic reasoning, or superiority over established systems.

## Prior-art pressure

Current prior-art posture:

```text
TMS / ATMS
    substantially cover justification and truth-maintenance machinery

W3C PROV / nanopublications / Whyis
    substantially cover provenance-bearing knowledge, revision, curation,
    archival history, and derived truth maintenance

temporal / bitemporal systems
    cover valid-time and knowledge-time separation

Graphiti / Zep
    provide serious reusable temporal graph + provenance + hybrid retrieval machinery

event sourcing
    covers retained state-changing history and current-state projection
```

Memory Lab therefore should not claim these primitives as novel and should not rebuild them without concrete evidence that composition is insufficient.

## Strongest current research distinctions

Under current pressure, the most promising Memory Lab distinctions are:

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

The final distinction is developed in `docs/inheritance-without-foreclosure.md` and remains empirically unresolved.

## Relationship to GIE / GEI

Memory Lab is a research site for epistemic continuity.

GIE/GEI may reuse Memory Lab findings while using another implementation substrate.

That outcome is acceptable and may be preferable.

A successful Memory Lab program discovers the smallest defensible semantic contract for governed memory; it does not require deployment of this repository as a standalone service.

## What is not yet true

- Memory Lab is not a production memory engine.
- Chroma/HNSW is not the canonical future runtime.
- A standalone custom truth-maintenance engine is not justified.
- A custom knowledge-graph runtime is not justified by current evidence.
- Evidence coverage is not yet measured robustly on open real corpora.
- Real-corpus derived-memory behavior is not yet established.
- Inheritance without foreclosure is not yet empirically established.
- Current-view semantics have not yet been demonstrated across multiple independent existing runtimes.
- Memory Lab has not shown that its surviving distinctions outperform simpler application-state representations.

## Immediate next research direction

Do not add broad new runtime machinery first.

Prefer this sequence:

1. map Memory Lab semantics explicitly onto strong prior-art substrates;
2. identify which distinctions are native, adaptable, or genuinely missing;
3. build conformance fixtures around the surviving distinctions;
4. test at least one existing runtime / composition against those fixtures;
5. run real-corpus experiments for evidence coverage and current-view behavior;
6. test inheritance without foreclosure with controlled tasks where simpler baselines can win;
7. only then decide whether any custom runtime component is justified.

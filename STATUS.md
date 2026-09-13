# Memory Lab Status

**Standing:** active research / engineering harness  
**Current phase:** prior-art integration + semantic hardening  
**Runtime choice:** unresolved / deliberately replaceable  
**Current substitution map:** `docs/substitution-conformance-map-v0.md`  
**Prior-art integration tracker:** GitHub issue #11

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

## Substitution/conformance mapping status

The first field-by-field mapping is complete in:

`docs/substitution-conformance-map-v0.md`

The map compares current schemas and responsibilities against:

- TMS / ATMS;
- W3C PROV + nanopublication / Whyis-like machinery;
- Graphiti / Zep;
- ordinary temporal / event-sourced application state.

Classification vocabulary:

```text
NATIVE
ADAPTABLE
MISSING
UNNECESSARY
```

Main result:

**Most record, temporal, provenance, justification, reassessment, and retrieval machinery is substitutable.**

The current JSON schemas remain useful synthetic fixtures but should not be promoted wholesale into a production ontology.

A draft implementation-independent research profile, `ML-EP-0`, now captures the surviving behavioral obligations. It is not a ratified standard and no external runtime has yet been shown to conform.

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

### Strongest surviving gap

The clearest missing cross-runtime semantic in the current comparison is **evidence coverage**.

TMS/ATMS can establish support from reasons; provenance systems can record what evidence was used; Graphiti/Zep can preserve source-episode associations. None of those facts alone proves that the materially relevant evidence universe was adequately considered.

That distinction now carries the highest empirical burden: it must demonstrate decision value beyond retrieval metrics, search receipts, provenance, and ordinary uncertainty labels.

### Current-view admission

Separate historical/support status from current-view participation remains useful in the synthetic fixtures, but ordinary application state is a serious simpler baseline. Memory Lab must show that a portable conformance boundary adds value rather than merely renaming a well-designed projection table.

### Inheritance without foreclosure

The historical-memory hypothesis is developed in `docs/inheritance-without-foreclosure.md` and remains empirically unresolved.

Its likely strongest form is a reassessment protocol over preserved causal history, not a bespoke storage primitive.

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
- The `ML-EP-0` draft profile is not ratified or externally validated.
- No external runtime has yet passed a Memory Lab adapter/conformance fixture.
- Evidence coverage is not yet measured robustly on open real corpora.
- Real-corpus derived-memory behavior is not yet established.
- Inheritance without foreclosure is not yet empirically established.
- Current-view semantics have not yet been demonstrated across multiple independent existing runtimes.
- Memory Lab has not shown that its surviving distinctions outperform simpler application-state representations.

## Immediate next research direction

Do not add broad new runtime machinery first.

The mapping phase is complete enough to move to substitution experiments.

Next sequence:

1. **Graphiti adapter:** port `derived-conflict-v0` / Polaris and test whether its preserve-both-support-histories + withhold-current-view behavior can be represented cleanly over Graphiti's native contradiction/invalidation model;
2. measure adapter complexity and distinguish a true semantic gap from configuration/application policy;
3. **Whyis adapter:** port a reassessment/revision fixture and test whether separate current-view admission adds value beyond native revision, retirement, archive, and truth-maintenance behavior;
4. add a bounded evidence-coverage receipt over one external runtime without creating a new memory engine;
5. test whether coverage state changes downstream decisions beyond provenance/retrieval metrics alone;
6. test inheritance without foreclosure with controlled tasks where simpler baselines can win;
7. only then decide whether any custom runtime component is justified.

The next useful result should be an external-runtime substitution result, including a clean result where the external runtime makes a Memory Lab component unnecessary.

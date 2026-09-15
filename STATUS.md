# Memory Lab Status

**Standing:** active research / engineering harness  
**Current phase:** prior-art integration + semantic hardening  
**Runtime choice:** unresolved / deliberately replaceable  
**Current substitution map:** `docs/substitution-conformance-map-v0.md`  
**First executed substitution result:** `docs/graphiti-substitution-v0.md`  
**GEI backpropagation audit:** `docs/gei-backpropagation-audit.md`  
**Prior-art integration tracker:** GitHub issue #11 (focused follow-ons: #12 coverage decision value, #13 current-view vs application state, #14 argumentation baseline, #15 export to the GEI profile)

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

## First external-runtime substitution result: Graphiti

`docs/graphiti-substitution-v0.md` ran `derived-conflict-v0` (Polaris) against `graphiti-core==0.30.2` on embedded Kuzu. It executed Graphiti's own storage, contradiction-resolution, deduplication, and episode-removal code. Contradiction verdicts were **scripted**: no LLM, search, or production backend was involved.

Result: **adaptable, by bypassing Graphiti's contradiction resolver for constrained predicates.**

- **Representation.** Graphiti's data model preserved both support-valid incompatible claims natively. Memory Lab computed admission as a read-only projection using unchanged conflict-lane code. That projection reproduced the native lane's assessments byte-for-byte and withheld both claims.
- **Native resolution.** Graphiti's resolver has one conflict operator: the later `valid_at` wins.
  - With different `valid_at` values, it turned a consistency conflict into a false world-time succession (EP-07/EP-10 failures).
  - With equal `valid_at` values, it closed nothing and left both claims current.
- **Wrong verdicts.** A wrong verdict on a multi-valued relation (the Graphiti #1728 shape) cascaded into a false resolution of the status conflict. EP-09 flagged it.
- **Removal.** `remove_episode` is deletion, not withdrawal. It deleted a fact that still had surviving support (EP-01/EP-04) and left dangling provenance (EP-02).
- **Propagation.** Graphiti does not propagate support loss to dependent facts. That is TMS work.

Memory Lab narrowed as a result:

- Record storage, evidence references, valid/knowledge time, historical retention, and corroboration belong to the substrate.
- Memory Lab keeps explicit predicate constraints, a read-only admission projection, and ML-EP-0 conformance checks.
- Justification evaluation should be delegated to a TMS/ATMS, not grown inside Memory Lab.

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

Any coverage representation should reuse OpenTelemetry GenAI retrieval spans, PROV, and a W3C DQV measurement rather than a new object. The executable coverage schema still uses the unscoped `complete` value, which lags ML-EP-0's `bounded-complete`; see #12.

### Current-view admission

Separate historical/support status from current-view participation remains useful in the synthetic fixtures, but ordinary application state is a serious simpler baseline. Memory Lab must show that a portable conformance boundary adds value rather than merely renaming a well-designed projection table.

Admission is also a policy choice. `withhold` is the Polaris lane's default, not a semantic necessity: plural admission is legitimate under a declared policy (audit GB-07). Choosing the policy for a scope belongs to governance, not Memory Lab. The test is #13.

### Inheritance without foreclosure

The historical-memory hypothesis is developed in `docs/inheritance-without-foreclosure.md` and remains empirically unresolved.

Its likely strongest form is a reassessment protocol over preserved causal history, not a bespoke storage primitive.

The controlled test is GEI experiment C-001, together with its pre-outcome amendment; it is not a Memory Lab experiment. Memory Lab does not run a competing protocol and does not author or preview C-001's sealed instruments. Memory Lab's role is to supply the minimum historical-record shape.

## Relationship to GIE / GEI

Memory Lab is a research site for epistemic continuity.

GIE/GEI may reuse Memory Lab findings while using another implementation substrate.

That outcome is acceptable and may be preferable.

A successful Memory Lab program discovers the smallest defensible semantic contract for governed memory; it does not require deployment of this repository as a standalone service.

Memory Lab reports epistemic state. Preserving information about the following does not make Memory Lab their owner:

- authority;
- admission-policy selection;
- decision sufficiency;
- participant standing;
- corrective independence;
- use rights and erasure;
- truth.

The negative boundary and interface obligations are in `docs/gei-backpropagation-audit.md` §5–§6.

## What is not yet true

- Memory Lab is not a production memory engine.
- Chroma/HNSW is not the canonical future runtime.
- A standalone custom truth-maintenance engine is not justified.
- A custom knowledge-graph runtime is not justified by current evidence.
- The `ML-EP-0` draft profile is not ratified or externally validated.
- Only one external runtime has been exercised: Graphiti 0.30.2 on embedded Kuzu, with scripted verdicts and one synthetic fixture.
  - Its data model plus a thin adapter satisfied the Polaris conformance checks.
  - Its native contradiction-resolution and episode-removal paths did not.
  - No real LLM, production backend, or real corpus was involved.
- Memory Lab's admission rule has not yet been compared with formal argumentation semantics (#14).
- Evidence coverage is not yet measured robustly on open real corpora.
- Real-corpus derived-memory behavior is not yet established.
- Inheritance without foreclosure is not yet empirically established.
- Current-view semantics have not yet been demonstrated across multiple independent existing runtimes.
- Memory Lab has not shown that its surviving distinctions outperform simpler application-state representations.

## Immediate next research direction

Do not add broad new runtime machinery first.

The mapping phase is complete enough to move to substitution experiments.

Completed: the Graphiti adapter experiment for `derived-conflict-v0` (see above).

Next sequence, ranked by information gain (`docs/gei-backpropagation-audit.md` §7):

1. **#13 current-view admission vs ordinary application state.** The Graphiti result showed that admission is a pure projection over substrate state. Test whether a plain event-sourced projection table (stdlib `sqlite3`) already preserves every fixture distinction, including scoped and policy-attributed dispositions.
2. **#12 evidence-coverage decision value.** First align the coverage vocabulary with ML-EP-0. Then test whether coverage state changes decisions beyond provenance plus retrieval metrics.
3. **#14 argumentation baseline.** Test whether grounded or preferred semantics reproduce the conflict-admission rule.
4. **Whyis reassessment/revision substitution** (#11). Blocked here: no Whyis deployment is available.
5. **#15 neutral export to the GEI profile.** Interface conformance against ST-002/ST-003.
6. **Real-LLM Graphiti replication** on a production backend. Requires infrastructure and a provider key.
7. Only then decide whether any custom runtime component is justified.

Inheritance without foreclosure is tested by GEI C-001, not by a Memory Lab experiment.

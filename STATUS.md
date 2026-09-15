# Memory Lab Status

**Standing:** active research / engineering harness  
**Current phase:** conformance harness for epistemic-continuity obligations. The research distinctions have been tested or delegated; see `docs/what-remains-v0.md`.  
**Runtime choice:** unresolved / deliberately replaceable  
**Current substitution map:** `docs/substitution-conformance-map-v0.md`  
**First executed substitution result:** `docs/graphiti-substitution-v0.md`  
**GEI backpropagation audit:** `docs/gei-backpropagation-audit.md`  
**Prior-art integration tracker:** GitHub issue #11 (focused follow-ons: #12 coverage decision value, #13 current-view vs application state, #14 argumentation baseline, #15 export to the GEI profile)

## Current identity

Memory Lab studies governed epistemic memory over time.

**Narrowed on 2026-09-15** (`docs/what-remains-v0.md`). Three substitution experiments were run:

- Graphiti (#11);
- ordinary application state (#13);
- evidence coverage on SciFact (#12).

None of the six research distinctions survives as a Memory Lab primitive. Memory Lab is now:

> a conformance harness for epistemic-continuity obligations O1–O8. It holds executable fixtures, thin substrate adapters, and checks that report whether a memory substrate or application design preserves those obligations or collapses them.

It is not a memory system, a runtime, an ontology, or a source of new distinctions.

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

*As of 2026-09-15, each distinction below has been tested or delegated. None survives as a Memory Lab primitive; they now appear as obligations O1–O8 in `docs/what-remains-v0.md`.*

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

**Executed (#12, `docs/coverage-scifact-v0.md`).** This was a preregistered test on SciFact. All six predictions held, and the explicit coverage state added **no decision value**:

- Default-accept made 119 wrong accepts at k = 10. NEI semantics made none, with no coverage state involved.
- Under non-exhaustive retrieval, categorical coverage was `unknown` for every claim.
- Reassessing on `known-incomplete` matched plain pooling on every claim.

This is recorded as a narrowing:

- the decision consequence of coverage is NEI label semantics;
- its informative variants are extra retrieval and recall estimation;
- its representation is a DQV + PROV envelope.

What survives is the rendering obligation O4. The conflicting-evidence case (H4) was not testable, because SciFact has no mixed-polarity claims.

Consequence for the schema: the coverage schema change (GB-03) is no longer justified. Map legacy values to REC values at export (#15).

### Current-view admission

Separate historical/support status from current-view participation remains useful in the synthetic fixtures, but ordinary application state is a serious simpler baseline. Memory Lab must show that a portable conformance boundary adds value rather than merely renaming a well-designed projection table.

Admission is also a policy choice. `withhold` is the Polaris lane's default, not a semantic necessity: plural admission is legitimate under a declared policy (audit GB-07). Choosing the policy for a scope belongs to governance, not Memory Lab.

**Executed (#13, `docs/appstate-baseline-v0.md`).** The comparison baseline was ordinary event-sourced application state with a scoped, versioned policy table: 77 SQL lines and 97 Python lines.

- It reproduced every Memory Lab current-view outcome across the three lanes.
- It also expressed scope and policy versions, which Memory Lab's artifacts cannot.
- Current-view admission is therefore an **ordinary application pattern, not a Memory Lab primitive**.

What survives is the conformance checks, plus one obligation: conclusions must be recorded, not recomputed on read, when derivation rules can change. The recompute-on-read variant silently rewrote history.

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
- Evidence coverage has been tested once, on a real judged collection (SciFact, oracle stance, lexical retrieval), where it added no decision value. It has not been tested on a collection with conflicting evidence, and not with a real stance model.
- Real-corpus derived-memory behavior is not yet established.
- Inheritance without foreclosure is not yet empirically established.
- Current-view semantics have not yet been demonstrated across multiple independent existing runtimes.
- For current-view admission, a simpler application-state representation matched Memory Lab on every synthetic fixture, and exceeded it on scope and policy attribution (#13).
- Memory Lab has not shown that any of its surviving distinctions outperforms a simpler application-state representation.

## Immediate next research direction

Do not add broad new runtime machinery first.

The mapping phase is complete enough to move to substitution experiments.

Completed:

- the Graphiti adapter experiment for `derived-conflict-v0` (#11);
- the current-view vs application-state comparison (#13);
- the coverage decision-value experiment (#12).

All three narrowed Memory Lab. The resulting redefinition is in `docs/what-remains-v0.md`.

Next sequence, given the redefinition:

1. **#15: move obligations O1–O8 into GEI's conformance layer.** This means exporting Memory Lab states to the GEI profile and expressing the obligations as GEI shapes and fixtures where RDF is natural. The executable checks for Graphiti, SQL, and retrieval pipelines stay here.
2. **Concurrent contradictory base evidence.** This is an O3/O5 check. Both Graphiti and the ordinary baseline resolve single-valued base facts by recency, and neither was tested against concurrent contradiction at the base level.
3. **#14 argumentation baseline.** This would further narrow O5's admission rule. Low priority.
4. **Optional:**
   - a Whyis substitution (#11), which would exercise O1/O2 on nanopublication revision; blocked here with no deployment;
   - a real-LLM Graphiti replication, which needs infrastructure and a provider key;
   - H4 on a licensed conflicting-evidence collection, which is predicted to measure retrieval, not coverage.
5. **No custom runtime component is justified** by current evidence.

Inheritance without foreclosure is tested by GEI C-001, not by a Memory Lab experiment.

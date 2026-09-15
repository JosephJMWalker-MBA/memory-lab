# Memory Lab Substitution / Conformance Map v0

**Status:** current research mapping; non-canonical implementation guidance  
**Date:** 2026-09-13  
**Purpose:** determine which Memory Lab semantics are already native to established systems, which are adaptable, which remain missing, and which should not survive as Memory-Lab-owned primitives.

This document implements the first comparison pass from GitHub issue #11.

It does **not** select a production runtime.

The governing question is:

> What is the smallest implementation-independent governed-memory contract that survives strong prior art?

## 1. Classification vocabulary

Each Memory Lab concern is classified against a candidate substrate as:

- **NATIVE** — the substrate already represents and operationalizes substantially the same responsibility.
- **ADAPTABLE** — the substrate can represent the responsibility cleanly through an adapter/profile/configuration without changing its core model.
- **MISSING** — no equivalent responsibility was demonstrated in the reviewed substrate; custom semantics or an additional composed system appear necessary.
- **UNNECESSARY** — the Memory Lab field/object should probably not survive as a separately owned primitive because it duplicates established machinery or can be derived as a projection.

`MISSING` does not mean novel. It means only that the reviewed substrate did not demonstrate the same responsibility end-to-end.

## 2. Systems under comparison

### TMS / ATMS

Use as the prior-art baseline for:

- reasons / justifications;
- dependency-directed reassessment;
- alternative support environments;
- inconsistent environments;
- withdrawal of support without automatic proof of the opposite.

Memory Lab should not build a general truth-maintenance engine unless concrete experiments demonstrate a conformance gap.

### W3C PROV + nanopublication / Whyis-like machinery

Use as the prior-art baseline for:

- assertion/provenance separation;
- attributed derivation;
- revisions;
- archived historical knowledge;
- curation/publication lifecycle;
- provenance-driven truth maintenance.

Whyis explicitly models revisions as new nanopublications linked with `prov:wasRevisionOf`; prior and transitively derived knowledge can be retired from the active RDF graph while remaining available from archive history.

### Graphiti / Zep

Use as the prior-art baseline for:

- raw source episodes;
- episode associations / source provenance;
- temporal facts and relationships;
- valid/invalid time and created/expired time;
- incremental graph construction;
- hybrid semantic + lexical + graph retrieval;
- fact invalidation as new information arrives.

Current Graphiti/Zep documentation states that contradiction resolution can invalidate older facts rather than preserving incompatible facts together in the active graph. That behavior is a direct pressure point for Memory Lab's separate support/consistency/current-view contract.

### Ordinary temporal / relational / event-sourced application state

Use as the baseline for:

- immutable event history;
- point-in-time reconstruction;
- current state as projection;
- ordinary lifecycle/status fields;
- explicit application policy for admission/withholding.

Memory Lab should not introduce a semantic primitive when ordinary application state preserves the same distinction adequately.

---

# 3. Derived memory record v0.2 mapping

Current schema: `schemas/derived-memory-record-v0.2.schema.json`.

| Memory Lab field / responsibility | TMS / ATMS | PROV / Whyis | Graphiti / Zep | Temporal/event-sourced app state | Memory Lab disposition |
|---|---|---|---|---|---|
| `record_id` | NATIVE node identity | NATIVE RDF/nanopub identity | NATIVE node/edge UUID | NATIVE entity/event identity | **UNNECESSARY as special semantics**; require stable identity, do not prescribe format |
| `record_type` | ADAPTABLE proposition/node type | NATIVE RDF types / vocabularies | ADAPTABLE custom entity/edge types | NATIVE discriminator | Keep only as bounded profile vocabulary where useful |
| `subject/predicate/object` | ADAPTABLE proposition representation | NATIVE RDF assertion | NATIVE relationship/fact model | NATIVE relational/domain state | **UNNECESSARY as proprietary representation** |
| `qualifiers` | ADAPTABLE through assumptions/context | NATIVE/ADAPTABLE through RDF structures/nanopub assertion graph | ADAPTABLE edge/entity attributes | NATIVE scoped columns/JSON/domain tables | Keep **semantic requirement that qualifiers are load-bearing when they alter proposition identity**, not this JSON shape |
| `evidence_refs` | ADAPTABLE as premise nodes, but not full source provenance | NATIVE `prov:wasDerivedFrom` / nanopub provenance | NATIVE episode associations/source links | ADAPTABLE foreign keys/event references | Preserve requirement; delegate representation |
| `derived_from_records` | NATIVE dependency graph | NATIVE derivation links | ADAPTABLE custom relation; not demonstrated as general derived-fact justification graph | NATIVE dependency/event links | Preserve requirement where recursive derivation exists; delegate graph machinery |
| `support_semantics` | **NATIVE** TMS/ATMS support model | ADAPTABLE through inference rules/provenance | MISSING as an explicit general support algebra | ADAPTABLE application/rule engine | **UNNECESSARY as Memory-Lab-owned general reasoner**; use TMS/ATMS or narrow rules |
| `justification_set_id` | **NATIVE** ATMS label/environment analogue | ADAPTABLE nanopub/inference bundle | MISSING explicit alternative-support environment | ADAPTABLE normalized support tables | Keep only adapter-facing reference if needed |
| `source_snapshot_id` | MISSING unless modeled externally | ADAPTABLE named bundle/version/provenance context | ADAPTABLE episodes/document/time, but not equivalent to deterministic corpus snapshot | NATIVE event/version/snapshot identity | Preserve *named evidence-state* requirement; do not require current synthetic ID form |
| `status` (`proposed/verified/...`) | ADAPTABLE belief in/out/support state but not same lifecycle | ADAPTABLE curation/publication/retirement | ADAPTABLE validity/invalidation, but semantics differ | NATIVE application lifecycle | Likely **projection/application state**, not proposition identity; avoid hard-wiring one universal vocabulary |
| `change_kind` | ADAPTABLE belief revision/update distinction | ADAPTABLE qualified derivation/revision + local type | ADAPTABLE temporal invalidation/update metadata | NATIVE event type | **UNNECESSARY as core object field** if change reason is derivable from explicit event/reassessment records; retain the distinction, not necessarily the field |
| `attribution_check` | NATIVE/ADAPTABLE explanation from reasons | ADAPTABLE provenance walk plus validation logic | ADAPTABLE source associations, but support-as-written check is not native | ADAPTABLE validator/event | Preserve as conformance behavior; probably separate assessment artifact, not embedded mutable status |
| `valid_time` | MISSING in classical TMS core | ADAPTABLE temporal RDF/model | **NATIVE** `valid_at/invalid_at` | **NATIVE** bitemporal/domain model | **UNNECESSARY as custom innovation**; require capability |
| `knowledge_time` | MISSING in classical TMS core | ADAPTABLE provenance/publication time | **NATIVE** `created_at/expired_at` approximates learned/expired knowledge timing | **NATIVE** transaction/system time | **UNNECESSARY as custom innovation**; require capability |
| `supersedes/superseded_by` | ADAPTABLE support-state transition | **NATIVE** revision/derivation vocabulary, Whyis revision | ADAPTABLE fact invalidation/history | NATIVE event/version relation | Prefer PROV/native runtime relation |
| `revision_of` | ADAPTABLE | **NATIVE** `prov:wasRevisionOf` | ADAPTABLE invalidated/replacement relation | NATIVE version lineage | **REMOVE proprietary semantic claim**; project to PROV where applicable |
| `contradicts` | **NATIVE** inconsistent/nogood environments conceptually | ADAPTABLE explicit relation/constraints | PARTIAL: contradiction path exists but often invalidates older fact | ADAPTABLE constraint/policy layer | Preserve conflict visibility but avoid bespoke graph engine |
| `qualifies` | ADAPTABLE | NATIVE/ADAPTABLE RDF relation | ADAPTABLE custom edge | ADAPTABLE relation | No independent research burden unless real cases require it |

## Result for the record contract

The `derived-memory-record-v0.2` schema is useful as a **synthetic executable fixture format**, but it should not be promoted wholesale into a production ontology.

Most of its storage fields are already ordinary features of RDF/provenance systems, temporal graphs, TMS/ATMS, or event-sourced application state.

The surviving Memory Lab value is primarily in **cross-field obligations**:

```text
proposition identity
!= support environment identity

source provenance
!= support sufficiency

valid time
!= knowledge time

historical record state
!= current-view admission
```

---

# 4. Evidence assessment mapping

Current schema: `schemas/derived-evidence-assessment-v0.schema.json`.

This is the strongest surviving pressure point.

| Memory Lab field / responsibility | TMS / ATMS | PROV / Whyis | Graphiti / Zep | Retrieval/app state | Disposition |
|---|---|---|---|---|---|
| `support_outcome` | **NATIVE** support from reasons | ADAPTABLE inference/provenance validation | ADAPTABLE extracted fact + source links, but not explicit logical support audit | ADAPTABLE | Established machinery; do not claim novelty |
| `considered_evidence_refs` | ADAPTABLE premises considered | NATIVE provenance-used set | ADAPTABLE episode associations/search results | NATIVE retrieval trace | Require inspectability where consequential |
| `coverage_basis` | **MISSING** as retrieval-set completeness claim | **MISSING** as generic completeness claim | **MISSING** as explicit completeness basis | ADAPTABLE from retrieval protocol | **SURVIVING contract candidate** |
| `coverage_outcome` | **MISSING** | **MISSING** | **MISSING** | ADAPTABLE custom policy | **SURVIVING contract candidate** |
| `relevant_evidence_refs` | Outside classical support model unless supplied | Can represent once known, does not establish completeness | Can retrieve/store episodes, does not prove all relevant evidence considered | Retrieval/evaluator-specific | Keep only when basis makes relevance set defensible |
| `omitted_relevant_evidence_refs` | MISSING | MISSING generically | MISSING generically | Derived from bounded evaluation | Useful diagnostic, not universal requirement |
| `overall_outcome` | ADAPTABLE current belief state | ADAPTABLE curation state | ADAPTABLE validity/current context | NATIVE app projection | Prefer **derived projection** from support + coverage + policy, not a second source of truth |

### Key result

No reviewed substrate demonstrated the general equivalence:

```text
provenance of evidence used
=
proof that relevant evidence was adequately covered
```

They are not equivalent.

Graphiti/Zep can trace facts and observations back to episodes and preserve episode associations, but that provenance says **where the result came from**, not that the system searched or considered the materially relevant evidence universe.

Whyis can enumerate nanopublications used by an inference, but derivation provenance likewise does not prove that omitted relevant nanopublications were considered.

TMS/ATMS can correctly establish that a conclusion follows from its support environment without establishing that the environment contains all materially relevant premises.

Therefore **evidence coverage remains the strongest candidate for a Memory Lab conformance extension**.

The research burden is now empirical: determine whether explicit coverage state improves real decisions beyond retrieval metrics, search logs, provenance, and ordinary uncertainty labels.

---

# 5. Multiple justifications mapping

Current schemas:

- `derived-justification-set-v0`
- `derived-justification-assessment-v0`

| Responsibility | Result |
|---|---|
| AND antecedents inside one justification | **NATIVE ATMS/TMS territory** |
| OR across independent justifications | **NATIVE ATMS territory** |
| proposition identity separate from support-environment identity | **NATIVE/strongly established ATMS discipline** |
| reassess when one support path changes | **NATIVE truth-maintenance behavior** |
| retain proposition if another independent support path survives | **NATIVE ATMS behavior** |
| support withdrawal does not infer negation | Established truth-maintenance/belief-revision discipline |

### Disposition

Memory Lab should **not** evolve the current justification schemas into a bespoke general ATMS.

Keep them as:

- executable synthetic fixtures;
- adapter/conformance examples;
- a compact way to state the expected behavior of an external truth-maintenance substrate.

If an external TMS/ATMS implementation satisfies the fixture semantics, prefer the external machinery.

---

# 6. Consistency and current-view admission mapping

Current schemas:

- `derived-predicate-constraint-v0`
- `derived-consistency-assessment-v0`

Memory Lab currently distinguishes:

```text
support validity
!= consistency validity
!= current-view admission
```

## Predicate constraints

`single_value_per_scope`, qualifier matching, and temporal overlap are ordinary domain constraints. They do not justify a Memory-Lab-owned constraint language.

Candidate implementation sources include:

- ATMS inconsistent/nogood environments;
- OWL/SHACL or domain validation where appropriate;
- relational constraints/application rules;
- an existing policy/rule engine.

**Disposition:** retain the requirement that incompatibility be justified by an explicit rule; do not promote the current JSON constraint shape as general ontology.

## Supported conflict

The current Polaris fixture intentionally permits:

```text
A support-valid
B support-valid
A and B incompatible in same scope/time
=> preserve both historical support states
=> withhold both from authoritative current view unless an explicit resolution rule selects one
```

### TMS / ATMS

**NATIVE / ADAPTABLE.** ATMS can preserve incompatible supported environments and reason about inconsistent environments. This is the strongest conceptual predecessor.

### Whyis

**ADAPTABLE, but not demonstrated as identical end-to-end behavior.** Whyis provides provenance, revision, retirement, archive, and truth maintenance. A profile can preserve both assertions as nanopublications while a separate admission projection withholds them. That admission semantics would be Memory-Lab/application policy rather than Whyis core.

### Graphiti / Zep

**PARTIAL / SEMANTIC MISMATCH WORTH TESTING.** Current graph-creation documentation says contradictory facts are compared against existing edges and contradictions invalidate older facts rather than leaving conflicting truths side by side in the active graph.

That is useful product behavior, but it is not the same as Memory Lab's deliberate three-way separation.

This makes `derived-conflict-v0` an excellent first Graphiti adapter fixture.

**Executed result (2026-09-14):** see `graphiti-substitution-v0.md`.

- Written directly, both claims are preserved natively by Graphiti 0.30.2's data model.
- A read-only admission projection then withholds both.
- Graphiti's native resolver keeps both current when `valid_at` is equal.
- Otherwise the native resolver lets the later `valid_at` win, which writes a world-time end onto a support-valid record.

Classification is refined from **PARTIAL** to: representation **NATIVE**; the resolver must be **bypassed for constrained predicates**.

### Ordinary application state

**ADAPTABLE and a serious simpler baseline.** A database can preserve historical assertions and maintain a separate current-view table/projection. Memory Lab must demonstrate that an explicit reusable conformance profile adds value beyond ordinary careful application design.

**Executed result (2026-09-14):** see `appstate-baseline-v0.md`. The baseline won.

- An event-sourced facts table with SQL derivation rules and a scoped, versioned policy table reproduced every Memory Lab current-view outcome.
- It also expressed scope and policy version.
- A recompute-on-read variant rewrote history after a rule change.
- A naive mutable design invented negations and erased the conflict.

What survives is the conformance checks, not a representation.

## Disposition

Keep the **three-way distinction** under empirical pressure.

Do not yet claim that a new runtime object is required.

---

# 7. Reassessment mapping

Current schemas:

- `derived-reassessment-plan-v0`
- `derived-reassessment-result-v0`

| Responsibility | Prior-art result | Disposition |
|---|---|---|
| reverse dependency closure after support change | **NATIVE TMS**, Whyis truth-maintenance analogue | Do not rebuild generally |
| parent-before-child reassessment | Native graph dependency/topological evaluation | Infrastructure concern |
| targeted rather than global reassessment | Established dependency-directed behavior | Reuse |
| append-only record of reassessment | NATIVE/ADAPTABLE event sourcing + provenance/nanopubs | Keep history requirement, not schema ownership |
| `prior_status` | Ordinary historical/application state | Derivable |
| `support_outcome` | TMS/application projection | Reuse |
| `resulting_view` | Application/current-view policy | **Candidate conformance distinction**, not core truth-maintenance machinery |
| trigger/replacement IDs | Provenance/dependency links | Reuse |

### Whyis pressure

Whyis is especially strong here: its documented revision behavior retires revised nanopublications and knowledge derived from them from the active RDF graph while preserving historical nanopublications in archive; derivation links are central to truth maintenance.

That substantially covers the *mechanics* Memory Lab's reassessment experiment was designed to discover.

### Surviving question

What Whyis/TMS mechanics do not automatically answer is whether Memory Lab's separate **current-view admission state** improves auditability or decision quality enough to standardize as a portable contract.

That must be tested, not assumed.

---

# 8. Inheritance without foreclosure mapping

Current hypothesis: `docs/inheritance-without-foreclosure.md`.

This is not primarily a graph-storage problem.

A historical negative conclusion needs enough structure to recover:

```text
approach/proposition considered
observed outcome
failure mechanism / governing reason
assumptions
relevant environment / versions / dependencies
scope
diagnostic confidence
reopening conditions
```

## TMS / ATMS

**ADAPTABLE but not native as stated.** TMS can track why a belief/rejection depends on assumptions, and can change belief status when support changes. But a software-development conclusion such as "do not retry technique X until parser capability Y changes" is application-level causal/problem-solving history, not automatically a TMS primitive.

## PROV / Whyis

**ADAPTABLE.** Provenance can preserve the attempt, inputs, responsible activity, result, revision lineage, and subsequent reevaluation. Custom vocabulary/application metadata can represent failure mechanism and reopening conditions.

No bespoke storage runtime is implied.

## Graphiti / Zep

**ADAPTABLE for episodes/history/context, weak for the governing semantics.** Episodes can preserve the historical attempt and temporal facts can represent changed conditions, but an explicit causal reopening test is not demonstrated as a native memory operation.

## Event-sourced / relational state

**ADAPTABLE and probably sufficient for representation.** Structured event records can preserve negative-result history and a later evaluator can compare old binding assumptions to current conditions.

## Result

The strongest Memory Lab contribution here is likely a **reassessment protocol/conformance behavior**, not a storage type:

```text
historical negative result
+ preserved causal basis
+ current condition comparison
→ binding / eligible-for-bounded-retest / superseded / unresolved
```

Whether that protocol improves real long-horizon work remains empirically unresolved.

---

# 9. Minimal implementation-independent conformance profile — draft ML-EP-0

This is a research draft, not a ratified standard.

A candidate runtime/composition does **not** need Memory Lab's JSON schemas. It needs to demonstrate the following behaviors where the relevant capability is in scope.

## EP-01 Historical preservation

Source evidence and prior derived/reassessment history must not be silently rewritten merely because the current view changes.

*Draft amendment (from #13):* this includes recomputation under a changed derivation rule or interpretation. Conclusions drawn under an earlier rule must remain readable as they were drawn.

## EP-02 Provenance closure

A consequential derived proposition must be traceable through its immediate derivation/support relationships to source evidence or an explicitly external assumption.

## EP-03 Support/coverage separation

The system must not infer adequate evidence coverage solely from the fact that cited evidence supports a proposition.

Coverage must be representable as at least:

```text
bounded-complete
known-incomplete
unknown
not-assessed
```

or an explicitly mapped equivalent.

*Executed test (#12, `coverage-scifact-v0.md`):* on SciFact, an explicit coverage state added no decision value beyond provenance plus retrieval metrics.

- NEI claim-verification semantics already enforce the decision consequence of this requirement.
- Under non-exhaustive retrieval, the categorical state is constant (`unknown`).

EP-03 is retained only as a rendering obligation (O4 in `what-remains-v0.md`): "no contrary evidence retrieved" must not be stated as "no contrary evidence exists".

## EP-04 Multiple-support correctness

When multiple independent support paths exist, loss of one path must not withdraw the proposition while another valid path remains.

This requirement should normally be delegated to TMS/ATMS or equivalent machinery.

## EP-05 Withdrawal is not negation

Loss of support for `P` must not automatically assert `not-P`.

## EP-06 Valid time / knowledge time separation

When temporal assertions are used, the system must be able to distinguish when a proposition held in the modeled world from when the system learned/recorded/reassessed it.

## EP-07 Support/consistency separation

An individually support-valid record must not lose its historical support status merely because it conflicts with another individually supported record.

## EP-08 Current-view admission separation

The system must be able to represent whether a historical/support-valid record participates in the current working view without rewriting the historical record.

*Executed comparison (#13, `appstate-baseline-v0.md`):* ordinary event-sourced state with a scoped, versioned policy table satisfies this requirement. It also represents scope and policy version.

EP-08 is retained as a conformance obligation, not as a Memory Lab primitive.

*Draft amendment:* the disposition should be scoped and attributable to a policy identity/version.

## EP-09 Explicit conflict basis

Conflicting values must not be declared incompatible merely because their object values differ. The incompatibility must arise from an inspectable constraint over scope/time/semantics.

## EP-10 Change reason separation

Where materially relevant, the system must distinguish:

```text
world state changed
!= interpretation/correction changed
```

## EP-11 Conditional historical inheritance

When a prior negative conclusion is used to govern a new attempt, the system should be able to expose the historical reason/assumptions and determine whether the causal basis still applies before treating the old conclusion as an unconditional veto.

EP-11 remains an empirical hypothesis rather than an established requirement.

---

# 10. What should become smaller now

The mapping supports immediate restraint.

Memory Lab should **not** currently build:

- a proprietary general truth-maintenance engine;
- a proprietary ATMS environment engine;
- a proprietary temporal graph solely for bitemporal facts;
- a proprietary provenance graph where W3C PROV/nanopublications suffice;
- a new hybrid vector/lexical/graph retrieval platform merely to own retrieval;
- a universal predicate-constraint language;
- a universal lifecycle vocabulary for all memory runtimes.

The existing synthetic schemas remain valuable as fixtures because they make hidden assumptions executable.

They should be treated as **test vectors**, not presumptive production ontology.

---

# 11. Strongest remaining Memory Lab research surface

After substitution pressure, the research center is approximately:

```text
retrieved / cited evidence
        ↓
local support assessment
        ↓
coverage assessment
        ↓
support environment(s)
        ↓
consistency assessment
        ↓
current-view admission
        ↓
later evidence / changed conditions
        ↓
reassessment without historical rewrite
```

The runtime beneath that path may be Whyis, Graphiti, a TMS/ATMS implementation, ordinary event-sourced relational storage, another maintained system, or a composition.

The important question is whether the **separations themselves** improve real correction, auditability, and long-horizon discovery.

---

# 12. Recommended adapter experiments

## First: Graphiti conflict adapter

Port the `derived-conflict-v0` Polaris case first.

Why this is high-information:

- Graphiti/Zep is actively maintained and strong on exactly the temporal/provenance/retrieval machinery Memory Lab might otherwise build.
- Its documented contradiction path tends to invalidate older contradictory facts.
- Memory Lab deliberately preserves both support-valid conflicting histories and withholds them from current view until an explicit rule resolves the conflict.

Test:

> Can Graphiti represent the Memory Lab behavior cleanly without fighting its native contradiction semantics?

Possible outcomes:

- **Native/adaptable:** Memory Lab narrows; use Graphiti plus a thin admission profile.
- **Awkward but possible:** quantify adapter complexity before claiming a gap.
- **Not representable without bypassing core behavior:** preserve the conformance distinction and test another substrate.

Do not grade Graphiti negatively merely because its product semantics choose a different useful tradeoff.

**Outcome:** adaptable, by bypassing the contradiction resolver for constrained predicates.

Memory Lab narrowed to constraints, the admission projection, and conformance checks. See `graphiti-substitution-v0.md`.

## Second: Whyis reassessment/revision adapter

Port a `derived-reassessment-v0` or revision fixture to Whyis/nanopublications.

Test whether:

- historical assertion remains accessible;
- revision is represented through native PROV lineage;
- dependent knowledge is retired/recomputed through native truth maintenance;
- Memory Lab's separate current-view result adds anything beyond Whyis's active-vs-archive behavior.

## Third: evidence-coverage adapter over either runtime

Add no new memory runtime machinery.

Wrap one of the above with a bounded retrieval/evaluation receipt containing:

```text
query/scope
retrieval method
considered evidence
known relevant evidence when defensible
coverage basis
coverage disposition
```

Then test whether explicit coverage state changes downstream decisions compared with provenance alone.

---

# 13. Sources / evidence boundary

Repository contracts inspected:

- `schemas/derived-memory-record-v0.2.schema.json`
- `schemas/derived-evidence-assessment-v0.schema.json`
- `schemas/derived-justification-set-v0.schema.json`
- `schemas/derived-justification-assessment-v0.schema.json`
- `schemas/derived-predicate-constraint-v0.schema.json`
- `schemas/derived-consistency-assessment-v0.schema.json`
- `schemas/derived-reassessment-plan-v0.schema.json`
- `schemas/derived-reassessment-result-v0.schema.json`
- `docs/derived-memory-adversarial.md`
- `docs/multiple-justifications-v0.md`
- `docs/derived-conflict-v0.md`
- `docs/derived-reassessment-v0.md`
- `docs/inheritance-without-foreclosure.md`

External references checked for this mapping:

- W3C PROV-O / PROV-DM: https://www.w3.org/TR/prov-o/ and https://www.w3.org/TR/prov-dm/
- Whyis revision/truth-maintenance use cases: https://whyis.readthedocs.io/en/latest/usecases.html
- Whyis CLI revision/retirement/archive operations: https://whyis.readthedocs.io/en/latest/commands.html
- Graphiti/Zep episodes: https://help.getzep.com/graphiti/core-concepts/adding-episodes and https://help.getzep.com/episodes
- Zep facts/temporal lifecycle: https://help.getzep.com/facts
- Zep graph creation/contradiction behavior: https://help.getzep.com/how-graph-creation-works
- Zep episode associations/provenance: https://help.getzep.com/v3/episode-metadata-projection
- Graphiti overview: https://help.getzep.com/graphiti/getting-started/overview

Classical TMS/ATMS references remain listed in `docs/derived-memory-prior-art.md`.

## Current conclusion

A large amount of Memory Lab's machinery is substitutable.

That is a positive result.

The strongest surviving program is not "build a better memory database." It is:

> **Define and falsify the smallest portable contract that prevents support, coverage, consistency, historical state, and current-view admission from silently collapsing into one another—and determine whether conditional historical inheritance improves long-horizon correction rather than merely adding process.**

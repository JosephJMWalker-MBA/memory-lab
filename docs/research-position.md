# Memory Lab Research Position

**Status:** current research orientation  
**Phase:** prior-art integration + semantic hardening  

Memory Lab is a research program for **governed epistemic memory over time**.

It is not committed to one database, graph store, vector index, truth-maintenance engine, or agent-memory framework. Those are replaceable implementation choices.

The durable research problem is narrower:

> How should a system preserve what was known, why it was believed, what evidence was considered, what remained unknown, how conclusions changed, and whether an older conclusion should still participate in the current view — without rewriting historical evidence or allowing memory to become a permanent veto on later rediscovery?

## 1. Research problem != runtime

Keep these layers distinct:

```text
research question
!= semantic contract
!= conformance tests
!= adapter
!= memory runtime
!= retrieval implementation
```

A mature external system may replace custom runtime machinery without eliminating the research question.

Conversely, a useful research distinction does not justify building a standalone runtime when existing systems already implement the required machinery well.

Current rule:

> **Reuse machinery aggressively. Preserve research questions provisionally. Demand evidence for every custom semantic or runtime layer.**

## 2. What prior art already solves substantially

Memory Lab does not claim novelty for the following ideas.

### Truth-maintenance systems

Classical TMS already establishes:

- retained reasons / justifications for beliefs;
- dependency-aware reassessment;
- explanation from support structure;
- revision when assumptions or supporting beliefs fail.

### Assumption-based truth maintenance

ATMS already establishes:

- conjunctive antecedents within one justification;
- alternative support environments across independent justifications;
- multiple simultaneous contexts;
- explicit handling of inconsistent environments.

### Provenance systems and nanopublications

W3C PROV and nanopublication systems already establish strong machinery for:

- assertion / provenance separation;
- derivation and revision lineage;
- attributed agents and activities;
- publication / curation metadata;
- historical traceability.

Whyis is especially relevant because it combines nanopublications, curation, revision, archival history, inference provenance, and generalized truth-maintenance behavior.

### Temporal / bitemporal knowledge systems

Established temporal systems already distinguish:

- valid time — when a proposition holds in the modeled world;
- transaction / knowledge time — when a system recorded or knew it.

### Event-sourced history

Event sourcing already establishes current state as a projection over retained state-changing history rather than the only preserved state.

### Modern agent-memory graphs

Graphiti / Zep already demonstrates a serious reusable implementation path for:

- raw source episodes;
- derived facts / relationships;
- source linkage;
- temporal validity;
- incremental graph construction;
- contradiction / invalidation behavior;
- hybrid semantic, lexical, and graph retrieval.

Memory Lab should therefore not build a custom graph runtime merely to reproduce these capabilities.

## 3. What remains worth testing

The strongest surviving research distinctions are currently about **boundary discipline**, not storage primitives.

### Local support != evidence coverage

```text
cited evidence supports proposition
!=
relevant evidence set was adequately considered
```

A proposition can be well supported by the evidence cited while still being misleading because material contrary evidence was never retrieved or admitted.

Coverage therefore needs its own state, potentially including:

```text
bounded-complete
known-incomplete
unknown
not-assessed
```

A claim with strong local support and unknown coverage should not silently become globally verified.

### Support validity != consistency validity

Two propositions can each have adequate support and still be mutually incompatible under the same scope and valid time.

The system should be able to preserve both support histories without forcing one to disappear merely because the pair cannot jointly occupy the same current view.

### Historical status != current-view admission

A historical record describes what a named evidence / reasoning state justified at a given time.

The current view is a later projection that may admit, withhold, reject, or supersede that historical record without rewriting it.

### Withdrawal != negation

Losing support for `P` does not establish `not-P`.

### World change != interpretation correction

A proposition may stop being current because the world changed, or because the earlier interpretation was wrong or too strong. These are not equivalent events.

### Memory != permanent veto

Preserved history must not turn a prior failure, rejection, or deferral into an unconditional prohibition when the causal conditions behind that conclusion have changed.

See `inheritance-without-foreclosure.md`.

## 4. Memory Lab's likely strongest form

The strongest form of Memory Lab may be smaller than a standalone memory product.

A plausible target is:

```text
semantic contracts
+ adversarial fixtures
+ conformance tests
+ reusable governance rules
+ adapters over existing runtimes
```

Possible implementation substrates may include combinations of:

```text
TMS / ATMS discipline
W3C PROV
nanopublications / Whyis-like knowledge units
bitemporal storage
Graphiti/Zep-like temporal graphs
ordinary relational/event-sourced stores
hybrid lexical/vector retrieval
```

No one substrate is privileged by the research program.

## 5. Relationship to GIE / GEI

Memory Lab is a research site for **epistemic continuity**.

That does not mean GIE/GEI must deploy `memory-lab` as its production runtime.

The relationship is:

```text
Memory Lab research
    discovers / tests epistemic-memory distinctions

GIE / GEI
    may reuse those distinctions
    while selecting the simplest runtime that preserves them
```

A GEI implementation using Whyis, Graphiti, a relational event store, or another substrate would not invalidate Memory Lab if Memory Lab's tested semantic contracts remain useful.

Likewise, if existing systems already provide the same semantics end-to-end more simply, Memory Lab should narrow accordingly.

## 6. Falsification posture

Memory Lab should be narrowed or rejected where:

- an existing system already provides the same responsibility at the same level;
- a proposed distinction cannot be measured without circular definitions;
- a semantic boundary adds complexity without improving correction, auditability, or decision quality;
- current-view admission can be represented adequately by ordinary application state;
- evidence coverage does not add useful information beyond retrieval metrics / provenance in practice;
- inheritance-without-foreclosure produces more wasted repetition than useful reopening;
- the benefits disappear outside hand-designed synthetic fixtures.

The objective is not to preserve Memory Lab as a product thesis.

The objective is to discover the smallest memory-governance model reality actually needs.

## 7. Position after the substitution experiments (2026-09-15)

Three of the falsification conditions in §6 have now been met by executed tests:

| Condition | Test | What happened |
|---|---|---|
| "an existing system already provides the same responsibility" | Graphiti (#11) | Graphiti covers storage, provenance, temporal fields, history, and corroboration |
| "current-view admission can be represented adequately by ordinary application state" | #13 | Ordinary application state represented it, and also expressed scope and policy |
| "evidence coverage does not add useful information beyond retrieval metrics / provenance in practice" | SciFact (#12) | Coverage added no decision value on homogeneous-polarity evidence |

The smallest model reality needs, as far as these tests reach, is the one already present in:

- TMS/ATMS;
- bitemporal and event-sourced state;
- PROV/DQV;
- NEI claim-verification semantics.

Memory Lab's remaining role is to check that composition does not lose it. See `what-remains-v0.md`.

The research questions in this document remain valid questions. They are now answered by prior art plus executed checks, or delegated: inheritance without foreclosure goes to GEI C-001.

# What Remains of Memory Lab

**Status:** adversarial check after the substitution experiments. This document narrows the identity statements in `STATUS.md`, `README.md`, and `research-position.md`.  
**Date:** 2026-09-15  
**Inputs:**

- `graphiti-substitution-v0.md` (#11)
- `appstate-baseline-v0.md` (#13)
- `coverage-scifact-v0.md` (#12)
- `gei-backpropagation-audit.md`

The rule for this check, set before it was run: **if coverage also collapses to ordinary machinery, say what remains. Do not invent a new distinction to keep the project alive.**

## 1. The check

Memory Lab's stated research surface was six distinctions. Each one now has either executed evidence or a named owner outside Memory Lab.

| Distinction | Executed test | What it showed | Where the responsibility now lives |
|---|---|---|---|
| local support ≠ evidence coverage | #12, SciFact (preregistered) | The coverage state is decision-inert. Its decision consequence is NEI label semantics. Its informative variants are extra retrieval. It is constant `unknown` under non-exhaustive retrieval | FEVER/SciFact label semantics; IR pooling and TAR recall estimation; DQV + PROV envelope |
| support validity ≠ consistency validity | #11 Graphiti; #13 sqlite | Both a temporal graph data model and plain SQL preserve both supported claims. Recency resolvers collapse them | the substrate's data model, with a conformance check |
| historical status ≠ current-view admission | #13 | An ordinary event-sourced projection with a scoped, versioned policy table reproduced every Memory Lab outcome, and also expressed scope and policy, which Memory Lab could not | application state; GEI CVD profile |
| withdrawal ≠ negation | #11, #12, #13 | Violated by closed-world defaults (B0), default-accept (A0), and deletion operations (`remove_episode`). Preserved by NEI semantics and append-only designs | ordinary discipline, with a conformance check |
| world change ≠ interpretation correction | #11 | Bitemporal fields can represent it. A recency resolver writes a false world-time end | bitemporal stores, with a conformance check |
| preserved history ≠ permanent veto | not executed here | GEI C-001 owns the controlled test | GEI |

The supporting machinery was also placed:

| Machinery | Where it belongs |
|---|---|
| multiple justifications, dependency-aware reassessment | TMS/ATMS. Reassessment plans are an efficiency device (#13) |
| record storage, provenance, valid/knowledge time, history, corroboration | the substrate (#11) |

**Coverage collapsed, as did the other five distinctions.** None of them is a new memory semantics. All six were already prior art, and Memory Lab had said so.

## 2. What the experiments added

The experiments did not add new distinctions. They added two things.

1. **Evidence about which ordinary designs violate distinctions everyone agrees on:**
   - Graphiti's native contradiction resolver and `remove_episode`;
   - recompute-on-read after a rule change;
   - naive mutable state with closed-world defaults;
   - default-accept claim verification.
2. **Portable, executable checks that detect those violations** on a temporal graph, in SQL application state, and in a retrieval-plus-decision pipeline. The checks separated careful designs from collapsing ones in every experiment.

## 3. Redefinition

> **Memory Lab is a conformance harness for epistemic-continuity obligations. It holds executable fixtures, thin substrate adapters, and checks that report whether a memory substrate or application design preserves or collapses a small set of obligations.**

It is **not**:

- a memory system;
- a runtime;
- an ontology;
- a schema family;
- a source of new epistemic distinctions.

### The obligations

Each obligation has the executed test that motivated it.

| ID | Obligation | Motivating evidence |
|---|---|---|
| O1 | Recorded conclusions are not rewritten when derivation rules or interpretations change. Record them; do not recompute history on read. | #13: B2 dropped a 0200 conclusion after a rule change |
| O2 | Withdrawal is never deletion. Lawful erasure is a separate, explicit operation. | #11: `remove_episode`. Prior art: XTDB `DELETE` vs `ERASE` |
| O3 | A support-valid record for a constrained predicate is not closed by a substrate's native resolver. Every closure has an inspectable conflict basis. | #11: recency resolver; unconstrained invalidation (#1728 shape) |
| O4 | Absence of retrieved support or contrary evidence is never decided or rendered as confirmation or negation. | #12: A0, 119 wrong accepts. #13: B0 invented `clear` |
| O5 | Supported conflicting claims stay visible. The admission policy (withhold vs plural) is scoped, versioned, and chosen by governance. | #13: C8/C9. Audit GB-07 |
| O6 | No operation leaves dangling provenance. | #11: EP-02 |
| O7 | Removing one support does not remove a record that still has another. | #11: EP-04. Prior art: ATMS |
| O8 | Temporal succession does not stand in for a world-change vs correction judgement. | #11: EP-10 |

These are GEI-level conformance obligations under GEI's T1–T7 general obligations, not Memory Lab primitives. `gei-conformance-mapping-v0.md` §4 gives the GEI contract text for each one. They restate GEI's discipline that **persisted information is not automatically true, authoritative, wanted, selected, or governing** as tests someone can run.

## 4. What Memory Lab stops doing

- Proposing new memory primitives, record schemas, or coverage and admission vocabularies. Its schemas remain test vectors only.
- Growing adapter-side machinery. Justification evaluation goes to a TMS/ATMS; admission goes to application state or an argumentation solver.
- Treating the evidence-coverage state as a research primitive.
- Running an inheritance-without-foreclosure experiment. GEI C-001 owns it.

## 5. Where the work should live

- **O1–O8 belong in GEI's conformance layer.** #15, the export to the GEI profile, becomes the main integration path:
  - where RDF is natural, express the obligations as GEI shapes and fixtures;
  - keep the executable Python checks here for substrates that are not RDF (Graphiti, SQL, retrieval pipelines).
- **The Chroma/HNSW engineering track** remains separate, validated lineage. #1 and #2 remain open.

**Executed (#15, `gei-conformance-mapping-v0.md`).** Seventeen overlays, preregistered at `0dd7d4a`, were validated against GEI's unmodified shapes at `4dd69ff` with pinned pySHACL. All predictions held.

- **Single-graph forms:** GEI's shapes reject every single-graph structural form of the obligations except one, an invalidation with no invalidating activity. O3 is therefore ADAPTABLE.
- **The other seven:** these are OUT-OF-SCOPE for single-graph SHACL. Each has a motivating failure that is an absence, an unresolved reference, an entailment, a plan-adequacy judgement, or support algebra. GEI's contract prose states each of them, with two exceptions: O2 lacks a lawful-erasure clause, and O7 is delegated to support models.
- **MISSING:** none.
- **A conflict inside GEI:** ST-007 rejects the `prov:wasRevisionOf` that GEI's T5 prescribes for corrected records.

The result: O1–O8 are GEI obligations with GEI citations, except O7, which GEI delegates to TMS/ATMS-style support models. Memory Lab keeps the differential (before/after) checks for substrates that are not RDF, and adds no responsibility.

### Implications back up for GEI

These are recorded for GEI's maintainers. They have not been applied to the GEI repository.

- **ST-002.** GEI's ST-002 requires every current-view disposition to consume an explicit Relevant Evidence Coverage measurement. `not-assessed` is an allowed value. On SciFact, the coverage state was decision-inert. ST-002 is consistent with that result if its purpose is explicitness and auditability (O4), and not if it is read as saying coverage determines the disposition. GEI may want to say which reading it means.
- **Stop criterion 4 and the REC falsification condition.** GEI round 12's stop criterion 4 asks for "explicit evidence-set coverage state distinct from local support", and the REC profile's §12 has a falsification condition. For bounded collections, both are largely met by established technology-assisted-review recall certification (Cormack & Grossman 2016; Lewis, Yang & Frieder 2021). For decision consequences, both are met by NEI semantics. The surviving GEI-specific part is the anti-promotion rendering rule.

## 6. What would reopen a research claim

| Trigger | What it would justify |
|---|---|
| A substrate or design that passes O1–O8 yet produces a demonstrable epistemic failure in real use | A new obligation |
| GEI C-001 shows causal reopening beats its baselines | EP-11 becomes an obligation with evidence |
| A conflicting-evidence collection shows the coverage **label**, not retrieval, changing decisions (H4) | A reopening of coverage. By construction this is not expected (A3-reassess ≡ A2-pool). **Reopen condition only:** the search for such a collection was dropped on 2026-09-15 |

Without one of these, the answer to "what memory semantics are actually required?" is: the ones already in TMS/ATMS, bitemporal stores, event sourcing, PROV/DQV, and NEI claim-verification semantics. Memory Lab supplies checks that they were not lost in composition.

## 7. Consequences for open issues

| Issue | Recommendation |
|---|---|
| #11 | The Graphiti result is recorded. The Whyis target is optional (it would exercise O1/O2 on nanopublication revision). Low priority |
| #12 | Closed as a completed narrowing. H4 is a reopen condition only; the dataset search was dropped |
| #13 | Closed as a completed narrowing |
| #14 | Argumentation would further narrow O5's admission rule. Low priority |
| #15 | Mapping executed (`gei-conformance-mapping-v0.md`). GEI's contracts state seven of the obligations (O2 without its erasure clause) and delegate O7. Its shapes check their single-graph forms, except PROV invalidation provenance. The two shape changes and one prose clause are recommendations for GEI's maintainers. The code exporter is deferred |

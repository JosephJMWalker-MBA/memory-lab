# GEI Conformance Mapping v0 (O1–O8)

**Status:** executed; preregistered  
**Date:** 2026-09-15  
**Issue:** #15  
**Protocol:** `experiments/gei-conformance-v0/expectations.json`, commit `0dd7d4a`, committed before any SHACL run. Two harness fixes followed (`226c8aa`, `cab806d`). Neither changed an overlay, a candidate, or a prediction, and no validation had run before them.  
**Evidence:** `experiments/gei-conformance-v0/results/gei-conformance-v0.results.json`, recorded at `cab806d` on a clean tree  
**GEI:** `JosephJMWalker-MBA/governed-intelligence-ecology` at `4dd69ff`, read only. GEI was not modified.  
**Processor:** pySHACL 0.40.1, rdflib 7.6.0, owlrl 7.6.2, with GEI's own processor options; Python 3.13.5 on macOS arm64

## 1. Question

Does GEI's existing SHACL and conformance machinery already absorb obligations O1–O8 (`what-remains-v0.md` §3)?

The method has two steps:

1. Classify each obligation as NATIVE, ADAPTABLE, MISSING, or OUT-OF-SCOPE, with evidence.
2. Only then, recommend the smallest GEI changes that the evidence justifies.

The standing rule: if GEI absorbs most or all of O1–O8, that is a narrowing. It is not a reason to invent Memory Lab responsibilities.

## 2. Method

**Overlays.** There are seventeen hand-authored Turtle files. Each one is a faithful export of something observed in:

- #11 (Graphiti);
- #12 (SciFact);
- #13 (application state).

They use only PROV-O, DQV, DCAT, Dublin Core, and GEI profile terms. They fall into two groups:

- **Violation forms: 14.**
  - 11 are **motivating**: the form in which the failure was actually observed.
  - 3 are alternative representations of the same failures.
- **Capability forms: 3.** These are things a conforming system should be able to express.

Each overlay is built so that the targeted defect is its only defect. Everything else in it satisfies GEI's shapes.

**Validation.**

- Each overlay was composed with GEI's positive reference path (the seven `POSITIVE_FILES`).
- It was then validated against all sixteen `SHAPE_FILES`.
- The processor options are copied from GEI's `scripts/validate_reference_path.py`: `inference="none"`, `meta_shacl=True`, `advanced=False`.
- To attribute a rejection to a shape file, the overlay was validated against each file alone. This is sound because no GEI shape file references a named shape defined in another file.
- The same run executed GEI's own `scripts/validate_semantics.py` in full mode. It exited 0.

**Candidate shapes.** Two shapes were written for this experiment. Neither is GEI text. Both are SHACL Core, and both use existing terms only.

- **A. Invalidation provenance (additive).** A subject of `prov:invalidatedAtTime` must have a `prov:wasInvalidatedBy` Activity. That Activity must have used something, and must have a qualified association with an agent and a `prov:Plan`.
- **B. ST-007 narrowed (replaces ST-007 in one run).** GEI's ST-007 constraints, copied unchanged, sit behind an `sh:or` guard. The guard applies them only to revisions of Relevant Evidence Coverage measurements. GEI's ST-003 already uses this guard pattern.

**Non-interference.** A candidate counts only if, with it applied:

- GEI's composed positive path still conforms;
- all twelve composed negatives still fail;
- all fourteen atomic cases keep good-conforms / bad-fails.

**Classification rule** (fixed in `expectations.json`).

Each violation form gets one class:

| Class | Condition |
|---|---|
| **NATIVE** | GEI's unmodified shapes reject it |
| **ADAPTABLE** | GEI accepts it, but a candidate that passes non-interference rejects it |
| **OUT-OF-SCOPE** | GEI accepts it, and the form was declared before running as not checkable in one conformance graph |
| **MISSING** | otherwise |

A form is "not checkable in one conformance graph" if it is an absence, a semantic entailment, the adequacy of a plan, a runtime operation, or something GEI delegates.

Each obligation takes the weakest class among its motivating forms, in the order MISSING < OUT-OF-SCOPE < ADAPTABLE < NATIVE.

## 3. Results

Everything predicted held:

- all seventeen overlay predictions;
- the GEI-internal check;
- both non-interference predictions;
- the predicted obligation classes.

| Overlay | Obligation | Kind | GEI | Rejected by | GEI + A | B | Class |
|---|---|---|---|---|---|---|---|
| `ml-good` | all | capability | conforms | | conforms | conforms | represented |
| `o1-recompute-no-history` | O1 | motivating | conforms | | conforms | conforms | OUT-OF-SCOPE |
| `o1-backdated-plan` | O1 | alternative | **rejects** | ST-012 | rejects | rejects | NATIVE |
| `o2-deleted-evidence` | O2 | motivating | conforms | | conforms | conforms | OUT-OF-SCOPE |
| `o2-deleted-coverage-input` | O2 | alternative | **rejects** | ST-002 | rejects | rejects | NATIVE |
| `o3-closure-without-basis` | O3 | motivating | **rejects** | ST-002 | rejects | rejects | NATIVE |
| `o3-invalidation-without-basis` | O3 | motivating | conforms | | **rejects** | conforms | ADAPTABLE |
| `o3-closure-with-recency-plan` | O3 | alternative | conforms | | conforms | conforms | OUT-OF-SCOPE |
| `o4-absence-as-bounded-complete` | O4 | motivating | **rejects** | ST-003 | rejects | rejects | NATIVE |
| `o4-admitted-without-coverage` | O4 | motivating | **rejects** | ST-002 | rejects | rejects | NATIVE |
| `o4-invented-negation` | O4 | motivating | conforms | | conforms | conforms | OUT-OF-SCOPE |
| `o5-conflict-dropped` | O5 | motivating | conforms | | conforms | conforms | OUT-OF-SCOPE |
| `o5-scoped-dual-dispositions` | O5 | capability | conforms | | conforms | conforms | represented |
| `o6-dangling-episode` | O6 | motivating | conforms | | conforms | conforms | OUT-OF-SCOPE |
| `o7-withdrawn-despite-support` | O7 | motivating | conforms | | conforms | conforms | OUT-OF-SCOPE |
| `o8-recency-invalidation-with-plan` | O8 | motivating | conforms | | conforms | conforms | OUT-OF-SCOPE |
| `o8-correction-as-revision` | O8 | capability | **rejects** | ST-007 | rejects | **conforms** | rejected by GEI; represented with B |

Violation forms by class:

| Class | All forms | Motivating forms |
|---|---|---|
| NATIVE | 5 | 3 |
| ADAPTABLE | 1 | 1 |
| OUT-OF-SCOPE | 8 | 7 |
| MISSING | 0 | 0 |

Examples of GEI's own messages:

- **`o3-closure-without-basis`:** "Less than 1 values on ml:o3BlockedProjection->prov:wasGeneratedBy" (ST-002).
- **`o4-absence-as-bounded-complete`:** ST-003's message.
- **`o8-correction-as-revision`:** eight distinct messages, all from ST-007, including "Value does not have class dqv:QualityMeasurement".

**GEI-internal check.** GEI's own atomic fixture `semantic-transition-v0/st012-positive-v0.ttl` asserts `ex:decisionReassessment12 prov:wasRevisionOf ex:decisionRecord12Good`, a reassessed decision record.

- Validated against GEI's ST-007, it **fails**.
- Under candidate B, it conforms.
- GEI's harness never runs that fixture under ST-007, so the conflict has stayed latent.

**Non-interference.** Both candidates passed:

- the composed positive conforms;
- 12 of 12 composed negatives fail;
- all 14 atomic cases are unchanged.

## 4. Classification of O1–O8, with GEI's own text

All citations are to GEI at `4dd69ff`. The contract file is `semantics/contracts/semantic-transition-and-disposition-v1.md`, abbreviated **ST&D-v1** below.

### O1: OUT-OF-SCOPE

- **Rejected natively:** a recomputed conclusion that uses a later-generated rule at the original decision time (ST-012).
- **Out of single-graph scope:** the lost 0200 conclusion is an absence. The export does not contain it.
- **GEI text:**
  - T5: "A material change produces a new artifact/state/assessment or an explicitly versioned revision. Earlier states remain reconstructible." (ST&D-v1:112)
  - §11 Historical integrity (ST&D-v1:322–326).
  - CVD-004 (`semantics/profiles/current-view-disposition-v0.md:458–462`).
- **Gap:** none.

### O2: OUT-OF-SCOPE

- **Rejected natively:** deleting a typed, load-bearing input, here the coverage measurement a decision used (ST-002).
- **Out of single-graph scope:**
  - A deleted fact that is still referenced by IRI counts as represented identity (T1a).
  - Whether it resolves is T1b, which is adapter-level: "No universal RDF-only resolver shape is justified." (`semantics/contracts/general-obligation-coverage-v0.md:53`)
- **GEI text:**
  - T5 relation selection: "entity ceases to be available for use -> PROV invalidation" (`general-obligation-coverage-v0.md:136–143`).
  - The resource-resolution obligation §5, which says an unresolved condition must remain represented (`semantics/contracts/resource-resolution-adapter-obligation-v0.md:93–97`).
- **Gap: no lawful-erasure clause.**
  - T5 has no exception for erasure.
  - A search of GEI's Markdown for erasure, erase, deletion, and purge finds no such clause.

### O3: ADAPTABLE

- **Rejected natively:** a superseded projection with no generating decision (ST-002).
- **Adaptable:** `prov:invalidatedAtTime` with no invalidating activity. GEI accepts it, and candidate A rejects it.
- **Out of single-graph scope:** whether "latest valid_at wins" is an adequate basis for a closure. That is a question of plan adequacy.
- **GEI text:**
  - The contract thesis requires "an explicit provenance-bearing operation … whose governing basis and scope remain reconstructible" (ST&D-v1:13).
  - T2–T4 (ST&D-v1 §4).
  - CVD-001 (`current-view-disposition-v0.md:446–448`).
- **Gap:** no shape applies the thesis to PROV invalidation.

### O4: OUT-OF-SCOPE

- **Rejected natively:**
  - bounded-complete coverage from a top-10 retrieval with no envelope (ST-003);
  - an admission whose decision consumed no coverage measurement (ST-002).
- **Out of single-graph scope:** whether "Vega status clear" follows from the evidence. That is an entailment.
- **GEI text:**
  - `withheld` does not mean false (`current-view-disposition-v0.md:173`), and CVD-003 (`:454–456`).
  - The bounded-complete rendering rule (`semantics/profiles/relevant-evidence-coverage-v0.md:125–131`), and REC-003 (`:327–329`).
  - T7 (`general-obligation-coverage-v0.md:189–195`).
- **Gap:** none.
- **Note:** under the weakest-form rule, O4 is OUT-OF-SCOPE even though GEI natively rejects two of its three motivating forms.

### O5: OUT-OF-SCOPE

- **Represented:** two scoped dispositions of one record, under distinct versioned plans.
- **Out of single-graph scope:** a dropped conflict is the absence of a projection.
- **GEI text:**
  - "unresolved supported conflict" is listed as a reason to withhold (`current-view-disposition-v0.md:166`).
  - CVD-005 (`:464–466`).
  - T6 (`general-obligation-coverage-v0.md:161–187`).
- **Gap:** none.

### O6: OUT-OF-SCOPE

- **Out of single-graph scope:** T1b, as for O2.
- **GEI text:** T1a/T1b (`general-obligation-coverage-v0.md:26–53`; `research/prior-art/round-57-identity-vs-native-resolution.md:22–34`).
- **Gap:** none. Resolution is adapter-level by GEI's design.

### O7: OUT-OF-SCOPE

- **Out of single-graph scope:** support algebra, meaning which of a record's supports survive. GEI has no support model.
- **GEI text:** evidence structure is left to SEPIO, Web Annotation, and PROV (`semantics/standards-crosswalk-v0.md:136–140`; ST&D-v1 §3, the standards-first rule).
- **Gap:** none for GEI. This is TMS/ATMS work.

### O8: OUT-OF-SCOPE

- **Out of single-graph scope:** whether the later claim reports a change in the world is a semantic question. The structural provenance is complete, because the resolver and its plan are recorded.
- **Capability blocked:** recording an interpretation correction as `prov:wasRevisionOf`. ST-007 rejects it.
- **GEI text:**
  - "Supersession MUST also identify why it occurred where material". The listed reasons include world state changed and interpretation corrected (`current-view-disposition-v0.md:210–217`).
  - Round 56: "ordinary supersession should not be encoded as PROV invalidation merely to obtain an end-of-currentness signal" (`research/prior-art/round-56-historical-preservation-relation-selection.md:56`).
- **Gap:** see F4 (post-hoc).

### Summary

- No obligation is MISSING.
- One obligation is ADAPTABLE (O3).
- Seven are OUT-OF-SCOPE for single-graph SHACL. For each of them, GEI's shapes reject every structural shadow that a single graph can show.
- GEI's contract text states seven of the eight obligations. Two exceptions:
  - O2 is stated only in part, because GEI has no lawful-erasure clause.
  - O7 is not stated. GEI delegates support structure to models it does not own.

## 5. Findings

### F1. GEI's shapes already enforce the structural half of the obligations

GEI's unmodified ST-002, ST-003, and ST-012 reject all five violation forms that one graph can show:

- a closure with no decision;
- a decision with no coverage input;
- a deleted typed input;
- bounded-complete coverage with no envelope;
- a backdated rule use.

Memory Lab needs no shapes of its own for these.

### F2. PROV invalidation is unchecked

- **The contract covers it.** GEI's T5 names PROV invalidation for an entity that "ceases to be available for use". The contract thesis requires material changes to be explicit, attributable, and basis-bearing.
- **No shape checks it.** No GEI shape targets `prov:invalidatedAtTime`, and no GEI fixture uses PROV invalidation.
- **The gap is real.** A Graphiti `invalid_at` exported with no invalidating activity conforms to GEI. Candidate A rejects it.
- **Caveat:** candidate A's non-interference result is vacuous, because GEI has no invalidation fixtures. Its justification is the contract text, not the fixture suite.

### F3. ST-007's target contradicts T5

- **The contradiction.**
  - ST-007 targets **every** subject of `prov:wasRevisionOf`, and requires it to be a `known-incomplete` Relevant Evidence Coverage measurement.
  - GEI's T5 selects `prov:wasRevisionOf` when an entity is a "revised version of an earlier entity".
  - Round 56 lists "a native system that publishes a corrected version of the same assessment/document" as a case where revision is justified (`round-56…md:95`).
- **Evidence.**
  - An interpretation correction recorded that way is rejected.
  - GEI's own `st012-positive-v0.ttl` fails ST-007.
  - Candidate B fixes both, with no effect on any GEI case.
- **Severity.** This is a consistency defect between GEI's prose and one shape. It is not a missing capability.
  - A workaround exists. Round 56's default, a new entity plus derivation plus `dcterms:isReplacedBy`, conforms today; see `o3-closure-with-recency-plan`.
  - The defect bites producers that version records natively and follow T5 literally.

### F4. The supersession reason has no binding (post-hoc, not preregistered)

- **The requirement.** CVD §4 says supersession "MUST also identify why it occurred where material".
- **What happened.** Every superseded projection in these overlays conforms without a reason. That includes `o8-recency-invalidation-with-plan`, where a recency resolver superseded a concurrent claim.
- **Two readings:**
  - If the decision's `prov:Plan` counts as the reason, ST-002 already binds it. The O8 failure is then semantic: the plan gives the wrong reason.
  - If a reason category is required, there is no binding, and GEI has no vocabulary for one.

This was noticed after the run. It was not a preregistered form, so it is recorded as a question for GEI, not as a result.

### F5. The gap SHACL leaves is what Memory Lab's Python checks cover

Every OUT-OF-SCOPE form was caught in #11 or #13 by one of three means:

- comparing a substrate's state before and after an operation (the Graphiti adapter's `conformance_report(before, after, …)`);
- comparing designs (the appstate B0, B1, and B2 designs);
- a support model (the multiple-justifications lane).

That is what Memory Lab still does.

**Untested alternative.** Put both snapshots in one graph, with snapshot membership expressed in DCAT/PROV terms, and use SHACL-SPARQL. That could move the absence checks (O1, O5) into SHACL. It was not tested. GEI's T1b position argues against doing the same for resolution (O2, O6).

## 6. Recommended GEI changes (not applied)

These are ordered by strength of evidence. Each is the smallest change the evidence supports. GEI's maintainers decide; this repository does not edit GEI.

**R1. Narrow ST-007's target.**

- **Evidence:** a failing capability, a failing GEI fixture, and passing non-interference.
- **Smallest form:** candidate B's `sh:or` guard, as in `experiments/gei-conformance-v0/candidate/st-007-narrowed.shacl.ttl`. It is SHACL Core, adds no vocabulary, and follows the pattern ST-003 already uses.
- **Why not a SPARQL-based target:** that is a SHACL Advanced Feature, and GEI's harness runs with `advanced=False`.
- **Regression fixture:** add a non-coverage `prov:wasRevisionOf` that must conform. `st012-positive-v0.ttl` already is one.

**R2. Check invalidation provenance.**

- **Evidence:** contract text and one failing form. Non-interference is vacuous.
- **Placement:** GEI prefers not to add universal shapes. It says "No universal T2 shape is justified" (`general-obligation-coverage-v0.md:63`) and "Do not create seven universal SHACL shapes" (`:236`). The smallest placement is therefore an **adapter profile** for substrates that export temporal invalidation (Graphiti/Zep-style `invalid_at`), alongside GEI's existing reference-path scope and history profiles.
- **Content:** candidate A is the shape body. `ml-good` supplies a positive fixture (the world-change invalidation), and `o3-invalidation-without-basis` a negative.

**R3. Add a lawful-erasure clause to T5 (prose).**

- **Suggested content:** erasure required by law or policy is a distinct, explicit operation. It is attributable and plan-governed, and the erasure itself is recorded. It may remove content.
- **What it is not:** erasure is not withdrawal, supersession, or invalidation.
- **Effect on T5:** reconstructibility then applies to the fact of erasure, not to the erased content.
- **Prior art:** XTDB distinguishes `DELETE` (history kept) from `ERASE`.
- **Placement:** T5, or ST&D-v1 §10 (knowledge-use rights). GEI's choice.

**R4. Clarify two points in prose (no shapes).**

- ST-002's coverage input exists for explicitness and audit (O4). It is not a claim that coverage determines disposition (`what-remains-v0.md` §5).
- Does the decision's `prov:Plan` carry CVD §4's supersession reason (F4)?

**R5. Record processor evidence.**

- **GEI's current claim:** its `STATUS.md:331` says complete pinned pySHACL suite execution is "not yet recorded for current suite".
- **What this run did:** it executed GEI's `validate_semantics.py` in full mode at `4dd69ff` with pinned pySHACL 0.40.1. It exited 0, with the final line "PASS: all selected semantic validation steps completed successfully."
- **What GEI may record:** Level-1 evidence, from an external harness, on one platform. It is not Level 2.

**Not recommended:**

- shapes for absences (O1, O5), reference resolution (O2, O6), plan adequacy (O3), entailment (O4, O8), or support algebra (O7);
- any new GEI vocabulary;
- adopting Memory Lab's candidate shapes without GEI's own review.

## 7. What this means for Memory Lab

This is a successful narrowing.

- **Seven of O1–O8 are GEI contract obligations** with GEI text (§4); O2 lacks only its erasure clause. **O7 belongs to support models (TMS/ATMS),** which GEI delegates. Memory Lab owns none of them as semantics.
- **GEI owns the shapes.** The two candidates stay in `experiments/gei-conformance-v0/candidate/` as proposals.
- **Memory Lab's residual is:**
  - differential (before/after) checks for substrates that are not RDF, reported against GEI clauses;
  - this mapping harness, which can be rerun against later GEI commits.
- **#15's code exporter is deferred.** The overlays demonstrate the mapping by hand. A code exporter pays off only when a real integration with a non-RDF substrate needs one.
- **#15's export-boundary assertions already exist in GEI.** They are CVD-002, CVD-003, and REC-003. They constrain presentation adapters, and nothing here renders.

## 8. Threats to validity

- **The predictions were derived from the shape text.** They were made after reading the shapes. Their holding shows that pySHACL behaves as the text reads; it is not a surprising empirical result. What the run adds is processor confirmation of the classification and of the two defects.
- **The overlays are hand-authored,** by the same author as the obligations. A real exporter might produce different graphs. Each overlay's `export_mapping` in `expectations.json` states how it was derived, for review.
- **The checkability declarations are judgements.** They were made before the run, with reasons, but they can be contested. The strongest challenge is F5's two-snapshot alternative.
- **Candidate A's non-interference is vacuous** (F2).
- **Only one processor was used.** This is Level-1 evidence. There was no Apache Jena comparison.
- **The weakest-form rule is conservative** (O4 in §4).
- **"OUT-OF-SCOPE" is narrow.** It means out of scope for single-graph SHACL, not out of scope for GEI.
- **Post-hoc material is labelled.** F4 is the only post-hoc finding.

### What would change these conclusions

- **A MISSING obligation.** A single-graph form that GEI accepts and no existing-terms candidate rejects would make an obligation MISSING, and would reopen a claim.
- **SHACL-checkable absences.** A two-snapshot SHACL-SPARQL design inside GEI's language profile would move the absence checks into GEI, and Memory Lab's residual would shrink further.
- **An intended broad target.** GEI text showing that ST-007's broad target is deliberate would withdraw R1.

## 9. Reproduce

See `experiments/gei-conformance-v0/README.md`. `python3 tests/run_gei_mapping_v0.py` runs in `make test` and in CI. It needs no RDF libraries, and it re-derives every prediction check and every class from the recorded results.

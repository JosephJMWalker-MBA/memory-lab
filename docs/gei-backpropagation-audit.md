# GEI → Memory Lab Backpropagation Audit

**Status:** research audit; non-canonical; synthetic and documentary evidence only  
**Date:** 2026-09-14  
**Scope:** research developed in the Governed Intelligence Ecology (GIE/GEI) program and adjacent repositories that has implications for Memory Lab but had not yet been turned into Memory Lab documentation, fixtures, experiments, issues, or tests.

This audit is a recovered future-work map plus a negative-boundary record. It does not ratify anything, and it does not treat GEI research as authority over Memory Lab. GEI documents are evidence about pressure that Memory Lab should answer, not instructions Memory Lab must obey.

## 1. Method and evidence boundary

### Sources searched

| Source | What was inspected |
|---|---|
| `JosephJMWalker-MBA/governed-intelligence-ecology` @ `4dd69ff` (origin/main) | `AGENTS.md`, `STATUS.md`, `README.md`, `docs/architecture-levels-and-roles.md`, `docs/component-implementation-status.md`, `semantics/` (contracts, profiles, shapes, fixtures), `research/experiments/` (C-001 protocol, amendment, review, reconnaissance), prior-art rounds 01–12 plus 03A, theory paper v0.3, GEI issue #1 |
| Local `~/Desktop/governed-intelligence-ecology` | Working copy 37 commits behind origin, with two untracked C-001 files and one uncommitted README change. The two files match their origin copies apart from a trailing newline. The README change only indexes those two files, which origin's README already lists. No research exists only locally. The working tree was read, not modified |
| `JosephJMWalker-MBA/Telos` | foundation ontology, correction/supersession pressure (XTDB), invariant hostile reviews, experiment 0007 (stale view / fencing), issue #194 |
| `JosephJMWalker-MBA/Hermeneia` | vision freeze issue #78, integration docs |
| `JosephJMWalker-MBA/pyxis` | README principles (evidence-first, no authority promotion) |
| `JosephJMWalker-MBA/masi-bus`, `Continuity-Node`, `artificial-cognitive-pathology`, `TRACE` | boundary-language search |
| `getzep/graphiti` | issue #1728; `graphiti-core==0.30.2` source (edge model, contradiction/invalidation, bulk ingest, `add_triplet`, `remove_episode`, search filters, Kuzu driver) |
| Memory Lab `main` @ `6832a0f` | all docs, schemas, fixtures, tests, issues #1, #2, #11, commit history |

Search terms included `Memory Lab`, `memory-lab`, `epistemic continuity`, `GIE`, `GEI`, `evidence coverage`, `current-view`, `support validity`, `consistency validity`, `reassessment`, `inheritance without foreclosure`, `withdrawal`, `negation`, `world change`, `interpretation correction`, `provenance`, `persisted != authoritative`, `asserted != true`, `preserved != active`, and related boundary language.

### Evidence boundary

```text
GEI research record
!= GEI ratified contract
!= Memory Lab requirement
!= executed Memory Lab experiment
```

Everything below is classified by what Memory Lab should do with it. Most findings narrow Memory Lab or move a responsibility elsewhere.

## 2. Layer placement used by this audit

GEI places Memory Lab primarily at the epistemic-continuity layer:

```text
PYXIS → HERMENEIA → MEMORY LAB → TELOS → ACTION → PYXIS
(evidence)  (interpretation)  (epistemic standing)  (purpose/authority)  (effect)  (what happened)
```

GEI's encoded separation invariant (`semantics/contracts/semantic-transition-and-disposition-v1.md`) is:

```text
evidence
!= interpretation
!= epistemic assessment / current-view disposition     <- Memory Lab's plane
!= participant standing
!= authority / authorization
!= execution eligibility
!= execution occurrence
!= outcome observation
!= outcome assessment
!= downstream use right
```

Memory Lab's legitimate research ownership is therefore the **epistemic-assessment / current-view-disposition plane**, which covers support, evidence coverage, consistency, historical standing, reassessment, and admission projection. It owns that plane as semantics, fixtures, and conformance tests, not necessarily as a runtime.

Two GEI statements define the boundary most sharply:

> Memory may report epistemic state. It must not manufacture action authority. (GEI round 03A §16.8)

```text
preserved
!= currently admitted
!= true
!= authoritative
!= permanently binding
```

(GEI theory v0.3 §3.3; `docs/architecture-levels-and-roles.md` §4.3)

## 3. Findings summary

Artifact key: **DOC** documentation, **FIX** fixture, **TEST** test, **ADP** adapter, **EXP** experiment, **NONE** nothing Memory Lab should build.

| ID | Finding | Already covered? | Needs | Priority |
|---|---|---|---|---|
| GB-01 | Admission is scoped and policy-attributed in GEI; Memory Lab's is global and unattributed | No | FIX + TEST (app-state baseline) | P1 |
| GB-02 | GEI's disposition vocabulary was derived from Memory Lab; Memory Lab has three unaligned view vocabularies | Partial (recoverable, not explicit) | TEST (lossless mapping) | P2 |
| GB-03 | Memory Lab's own coverage schema uses the unscoped `complete` that GEI's profile forbids | No (drift) | DOC now; schema change only with GB-04 | P2 |
| GB-04 | Coverage should reuse OTel GenAI + PROV + DQV; its decision value is still unmeasured | Named in #11; no design | EXP | P1 |
| GB-05 | Formal argumentation already covers supported conflict and admission | No | DOC now; EXP (baseline) | P2 |
| GB-06 | `EpistemicAssessment` was killed as a bespoke schema; SEPIO/EVI/AIF/DQV are the substrate | No | DOC now | P3 |
| GB-07 | Wikidata ranks separate support from standing; withhold vs plural-admit is **policy** | No | DOC now | P2 |
| GB-08 | Graphiti invalidation is LLM-judged and recency-resolved (#1728) | Map only | EXP (executed; see §7) | P1 |
| GB-09 | A policy/version change is a distinct cause of view change | No | FIX + TEST | P2 |
| GB-10 | `admitted`/`verified` must never become authority or truth | Implicit | DOC now; TEST at export | P2 |
| GB-11 | Neutral export to GEI's PROV/DQV/CVD profile, checked against ST-002/ST-003 | No | ADP + TEST | P2 |
| GB-12 | GEI C-001 governs the inheritance experiment; Memory Lab must not duplicate it | Stale | DOC now | P1 |
| GB-13 | Withdrawal ≠ deletion; erasure is separate and not Memory Lab's | Partial | DOC; covered by GB-08 lane | P2 |
| GB-14 | Alternative justification ≠ independent evidence | Wording overclaims | DOC | P3 |
| GB-15 | Adapters must preserve derivation type (interpretation ≠ evidence) | Internal only | Covered by GB-08 | P2 |
| GB-16 | Human correction can change coverage without disposition authority | No | FIX inside GB-04 | P3 |
| GB-17 | Views must carry as-of identity so consumers can fence staleness | Partial | DOC | P3 |
| GB-18 | Junction claim: failures cluster where distinctions meet | No | DOC; evaluation lens | P3 |
| GB-19 | Reality feedback re-enters Memory Lab only as evidence | No | DOC (boundary) | P3 |

## 4. Findings in detail

Each entry records: **source**, **implication**, **coverage**, **needs**, **baseline** (the simplest established prior art), **falsifier / success**, and **priority**.

### GB-01 — Current-view admission is scoped and policy-attributed

- **Source.** GEI `semantics/profiles/current-view-disposition-v0.md` §5 ("a disposition with no scope is potentially misleading") and rules CVD-001 (explicit decision provenance) and CVD-005 (scope preserved). ST-002 requires the disposition to be generated by an attributable, plan-governed decision. GEI round 06: `remembered != currently usable`, with consequence-sensitive freshness. Telos 0007: `stale read != stale effect authority`.
- **Implication.** Memory Lab's `current_view_outcome` and `resulting_view` are global. The same record cannot be `admitted` for exploratory research and `withheld` for production, and no admission artifact names the policy (identity/version) that produced it. GEI's profile depends on both, and Memory Lab supplied the lineage for that profile.
- **Coverage.** None. `assessed_at_snapshot` supplies knowledge-time identity, but scope and policy reference are missing.
- **Needs.** A fixture and test in which one record set is projected under two declared scopes and policies without contradiction, run against an **ordinary event-sourced application-state baseline** (stdlib `sqlite3` projection table) to see whether Memory Lab's separation adds anything.
- **Baseline.** An event-sourced table plus a per-scope projection view, with policy version logged per projection row (the ordinary pattern of OPA/Cedar decision logs).
- **Falsifier / success.** Falsified as a Memory Lab contribution if the plain application-state baseline preserves every distinction exercised by the Polaris, Vega, and Aurora fixtures with no information loss. That would be a successful narrowing, leaving Memory Lab only conformance assertions. Survives only if some fixture distinction is lost or silently collapsed by the baseline.
- **Priority.** P1. This is the cheapest direct attack on EP-08, which STATUS already names as under falsification.

### GB-02 — Disposition vocabulary alignment

- **Source.** The GEI CVD profile §2 says it inherited its separation from Memory Lab's later lanes. Its v0 values are `pending | admitted | withheld | rejected | superseded`, and `superseded` must name a successor (`dcterms:isReplacedBy`, CVD-004).
- **Implication.** Memory Lab currently emits three unaligned view vocabularies:
  - consistency: `allow_all_supported | withhold_conflicting_supported | allow_surviving_supported`
  - reassessment: `active | historical_only | unresolved`
  - justification: `active | historical_only`

  In `derived-reassessment-v0`, Sigma-replaced and Vega/Helios-withdrawn both become `historical_only`. The difference (superseded-with-successor vs withdrawn-without-successor) survives only in `support_outcome` plus `replacement_record_ids`.
- **Coverage.** Partial. The information is recoverable, but the projection is not explicit.
- **Needs.** A mapping test only, no new schema: derive CVD values from existing Memory Lab artifacts and assert the mapping is lossless.
- **Baseline.** Whyis active-vs-archive with `prov:wasRevisionOf`; an ordinary status column.
- **Falsifier / success.** If the mapping is lossless in both directions, the CVD vocabulary is an explicitness improvement, not new information. Record that honestly. If some Memory Lab state has no CVD image (or the reverse), one side is under-specified.
- **Priority.** P2. Fold into the GB-01 issue.

### GB-03 — Coverage vocabulary drift

- **Source.** GEI `semantics/profiles/relevant-evidence-coverage-v0.md` (values `not-assessed | unknown | known-incomplete | bounded-complete`; REC-001..005). ST-003 requires a reconstructible evaluation envelope for `bounded-complete`. Memory Lab's own ML-EP-0 (EP-03) lists the same four values.
- **Implication.** Memory Lab's executable schema `derived-evidence-assessment-v0` still uses `coverage_outcome ∈ {complete, incomplete, unknown}` and has no `not-assessed`. That unscoped `complete` is exactly what REC-003 ("no global rendering") prohibits, and `overall_outcome: verified` can be derived from it. Memory Lab's fixtures therefore lag the profile Memory Lab helped create.
- **Coverage.** No. The drift is new in this audit.
- **Needs.** Documentation now. Schema evolution only as part of GB-04, so the coverage contract is changed once, with an evaluation envelope, rather than renamed twice.
- **Baseline.** W3C DQV `QualityMeasurement` with a scoped metric; IR recall against a judged reference set.
- **Falsifier / success.** Not a research claim, just an alignment defect. Success is that no Memory Lab artifact can express unscoped completeness.
- **Priority.** P2.

### GB-04 — Evidence coverage: reuse the instrumentation, test the decision value

- **Source.** GEI round 08 §16 ("benchmark recall is not open-world coverage"), round 10 §8 (`RetrievalReport`), round 11 §6 (coverage belongs over DQV, not a new datatype), round 12 §10.2 and stop criterion 4, and the REC profile §8 anti-promotion rule:

  ```text
  no contrary evidence retrieved != no contrary evidence exists
  ```

- **Implication.** Memory Lab should build no coverage "receipt" object. A receipt is already expressible as:
  - OpenTelemetry GenAI retrieval spans (query, data source, returned documents, scores)
  - PROV activity/plan/agent
  - a DQV measurement whose value is a coverage state
  - an explicit evaluation envelope: corpus/snapshot, access scope, procedure, exclusions, index/embedding version, cutoff

  Memory Lab's unique burden is empirical: **does explicit coverage state change a downstream decision beyond what provenance plus retrieval metrics already give?**
- **Coverage.** Named as a checkbox in #11 and STATUS steps 4–5. No experimental design exists.
- **Needs.** An experiment. A decision task set with ground truth, including cases with omitted material contrary evidence. Arms:
  1. provenance only;
  2. provenance + retrieval metrics (recall@k against a judged set, scores);
  3. provenance + metrics + categorical coverage with envelope.

  The human-correction transition (GB-16) is included as a fixture.
- **Baseline.** Arms 1 and 2 are the baselines. DQV and OTel are the substrate.
- **Falsifier / success.** Falsified if arm 3's decisions equal arm 2's on the task set, including omitted-contrary cases. Survives if arm 3 prevents at least one class of wrong decision that arm 2 permits, without adding wrong abstentions on cases where coverage is immaterial (see GB-19/NB-04 on decision sufficiency).
- **Priority.** P1. This is STATUS's "strongest surviving gap."

### GB-05 — Formal argumentation is prior art for supported conflict and admission

- **Source.** GEI round 09 §9 (Dung abstract argumentation, ASPIC+; "Memory Lab's differentiating work should not be 'we support contradictory claims'") and round 11 §7 (AIF acceptability; "current_view_admission should not be treated as a new theory of belief").
- **Implication.** The Polaris current-view rule behaves like grounded (skeptical) acceptance: two support-valid arguments attack each other symmetrically, the grounded extension is empty, and both are withheld. When the blocked argument loses its premise, the ready argument is unattacked and is accepted. `docs/derived-memory-prior-art.md` omits argumentation entirely.
- **Coverage.** None.
- **Needs.** Documentation now. Then an experiment: map every Memory Lab conflict fixture to an argumentation framework, and compare Memory Lab dispositions with grounded and preferred semantics computed by an **existing** solver library, not a bespoke one.
- **Baseline.** Dung grounded semantics; ASPIC+ with rule preferences.
- **Falsifier / success.** If grounded semantics reproduces every Memory Lab admission outcome, the admission rule is substitutable. Memory Lab then keeps only the mappings constraint → attack and support → argument existence. That is a successful narrowing.
- **Priority.** P2.

### GB-06 — The representation substrate already exists

- **Source.** GEI round 11 §4–7: SEPIO (EvidenceLine/Statement/direction/strength), EVI (a PROV-O extension with support/challenge), Micropublications, ECO, and DQV. "`EpistemicAssessment`: standalone object KILLED as a broad bespoke schema."
- **Implication.** Any Memory Lab export or production mapping should compose PROV + SEPIO/EVI/AIF + DQV + bitemporal fields + a current-view projection. The Memory Lab JSON schemas stay test vectors, which is consistent with substitution map §10.
- **Coverage.** Directionally consistent; these ontologies are simply absent from Memory Lab's prior-art notes.
- **Needs.** Documentation (prior-art note).
- **Baseline.** SEPIO/EVI.
- **Falsifier / success.** Not applicable; this is inheritance.
- **Priority.** P3.

### GB-07 — Wikidata ranks: withhold vs plural-admit is a policy choice

- **Source.** GEI round 05: Wikidata keeps references (where a value comes from) separate from rank (current community standing), and multiple qualified values can coexist.
- **Implication.**
  - Separating support from current standing is ordinary deployed practice, not a Memory Lab distinction.
  - Wikidata has no rank meaning "withheld, not false." `deprecated` means known-wrong (≈ `rejected`). With no `preferred` statement, all normal-rank values are returned together, which is plural admission.
  - Memory Lab's hard-coded `withhold_conflicting_supported` is therefore **one admission policy among legitimate alternatives**, not a semantic necessity. GEI's CVD profile already allows admission "as one side of a plural interpretation where policy permits plurality."
  - Memory Lab should own only these obligations: unresolved conflict stays visible, and whatever the policy decides stays separate from support and from rejection. Choosing withhold or plural-admit belongs to scope policy (see NB-03).
- **Coverage.** No. The Polaris lane hard-codes withholding.
- **Needs.** Documentation now. The GB-01 fixture should include a plural-admit policy.
- **Baseline.** Wikidata statement ranks plus qualifiers.
- **Falsifier / success.** Narrowing already accepted: `withhold` is demoted from semantic rule to default policy.
- **Priority.** P2.

### GB-08 — Graphiti's invalidation semantics

- **Source.** GEI round 03 §3.6 and round 03A §7 cite Graphiti issue #1728. That issue says invalidation candidates are unscoped since #906 and that "nothing checks the LLM's contradiction call." In a hand-audit of four retired facts, three were collateral retirements.
- **Implication.** This is direct pressure on EP-09 (explicit conflict basis). The Graphiti adapter experiment therefore needs a multi-valued-relation over-invalidation variant and a conformance check that flags invalidation with no declared constraint.
- **Coverage.** The substitution map predicted a semantic mismatch but did not know #1728 or the recency rule.
- **Needs.** An experiment. **Executed in this session; see §7 and `docs/graphiti-substitution-v0.md`.**
- **Baseline.** Graphiti itself.
- **Falsifier / success.** Defined in the experiment document.
- **Priority.** P1.

### GB-09 — Policy change is a distinct cause of current-view change

- **Source.** The CVD profile §4 lists supersession reasons: world state changed, interpretation corrected, record revised, **policy/version changed**. GEI round 03A §14 separates evidence correction, world change, and interpretation change.
- **Implication.** Memory Lab's `change_kind` covers `evidence_added | world_state_changed | interpretation_changed | conflict_detected`. It cannot express "the view changed because the admission policy changed, while support, coverage, and consistency did not." Without that, a policy change would look like epistemic reassessment. Choosing the policy is not Memory Lab's job (NB-03); recording which policy version produced a projection is.
- **Coverage.** No.
- **Needs.** A fixture and test inside the GB-01 lane: change only the policy version and assert that support, coverage, and consistency artifacts are byte-identical while the disposition changes, with the policy reference recorded.
- **Baseline.** Event-sourced event types; policy-engine decision logs that carry policy version.
- **Falsifier / success.** Likely satisfied by the ordinary baseline, leaving Memory Lab only a conformance assertion. Record it that way if so.
- **Priority.** P2.

### GB-10 — The authority boundary: admitted ≠ authorized ≠ true

- **Source.**
  - GEI theory v0.3 §3.4: `ASSERTED != TRUE`, `PERSISTED != AUTHORITATIVE`
  - CVD-002 (admitted does not imply authority) and CVD-003 (withheld does not imply false)
  - contract v1 ST-004, ST-005, ST-008, ST-009
  - Telos `docs/foundation/04-ontology.md`: `context != governing state merely because executor saw it`, `projection != canonical authority`
  - Telos invariant reviews: `persisted != active`, `preserved != active`
  - Pyxis README: inspection without authority promotion
- **Implication.** Memory Lab's vocabulary uses `verified` (record `status`, `overall_outcome`). A downstream consumer can easily read `verified` as true, approved, or authoritative, and Memory Lab docs never state the authority boundary explicitly. Memory Lab should state it and should test it at the **export boundary** (GB-11). The GEI-layer shapes ST-004/ST-005 already cover the cross-plane transition, so Memory Lab should not duplicate them.
- **Coverage.** Implicit. No Memory Lab artifact carries authority fields, but nothing asserts that.
- **Needs.** Documentation now (the negative boundary in §5). A test at export time: no authority, eligibility, or use-right field, and `admitted` never renders as authorized or true.
- **Baseline.** GEI ST-004/ST-005/ST-008.
- **Falsifier / success.** Not a research claim, just boundary hygiene.
- **Priority.** P2.

### GB-11 — Neutral export and cross-layer conformance

- **Source.** GEI round 03A §19: "neutral export reproduces the semantic state without vendor/runtime lock-in" is a stop criterion for a custom runtime. The fixtures `epistemic-good.ttl`, `epistemic-bad-*-overlay.ttl`, and `history-*.ttl` encode Memory Lab distinctions for SHACL.
- **Implication.** Memory Lab has no export. Its synthetic outputs (support, coverage, consistency, disposition, history) should map into GEI's PROV/DQV/CVD profile and pass ST-002/ST-003 under the pinned GEI processor. This is the real interface-conformance test between the two repositories.
- **Coverage.** None.
- **Needs.** An adapter (JSON → RDF export, pinned `rdflib`/`pyshacl` in an optional lane) and a test.
- **Baseline.** A PROV-O JSON-LD serialization.
- **Falsifier / success.** If the export loses a Memory Lab distinction, or GEI shapes reject a state Memory Lab considers valid, the two contracts disagree, and the disagreement is the finding. Success is a lossless round trip for the Polaris, Vega, and Aurora states.
- **Priority.** P2.

### GB-12 — C-001 governs inheritance-without-foreclosure testing

- **Source.** GEI C-001 protocol and pre-outcome amendment v1: A–E arms including a structure-matched D control, a balanced reopen/do-not-reopen portfolio, a history-judgement instrument, and three or more replicates. `docs/component-implementation-status.md`: "Do not describe a prompt checklist used by C-001 as 'the Memory Lab implementation.'"
- **Implication.** Memory Lab's `docs/inheritance-without-foreclosure.md` predates the amendment, and STATUS step 6 ("test inheritance without foreclosure with controlled tasks") would duplicate C-001. The contamination risk is concrete: if Memory Lab authored history-judgement items, the experimenter would see items before sealing.
- **Coverage.** Stale.
- **Needs.** Documentation now: point to C-001 as the governing experiment and restrict Memory Lab's contribution to the minimum historical-record shape and to reading C-001's outcome when it exists.
- **Baseline.** C-001 arms A (ordinary context) and B (neutral supplied history).
- **Falsifier / success.** Owned by C-001.
- **Priority.** P1. It is cheap and prevents duplicated or contaminated work.

### GB-13 — Withdrawal ≠ deletion; erasure is separate

- **Source.** Telos `correction-supersession-pressure.md`: XTDB ordinary `DELETE` is versioned, while `ERASE` is a separate, exceptional legal operation. "Removing something from current applicability is not the same operation as destroying its historical record." Graphiti `remove_episode` hard-deletes derived edges (confirmed in 0.30.2 source).
- **Implication.**
  - Adapters must never map Memory Lab withdrawal onto a substrate's delete operation.
  - Memory Lab's historical-preservation rule (EP-01) needs an explicit carve-out: lawful erasure is a distinct, explicit operation owned by rights/governance (ODRL/DPV; see NB-06). Memory Lab only requires that erasure never masquerade as withdrawal.
- **Coverage.** Partial. Withdrawal is append-only in the fixtures; erasure is unmentioned.
- **Needs.** Documentation. An executable check lives in the GB-08 withdrawal lane.
- **Baseline.** XTDB delete vs erase.
- **Falsifier / success.** Not applicable (boundary).
- **Priority.** P2.

### GB-14 — Alternative justification ≠ independent evidence

- **Source.** GEI `architecture-levels-and-roles.md` §4.5 (`plurality != corrective independence`), REC profile §10 (coverage is pathway-specific), and ST-006.
- **Implication.** `multiple-justifications-v0` says "independent justifications," but its meaning is logical alternatives (ATMS OR). Two justifications that share an evidence leaf or an upstream extraction are alternatives without being failure-independent. The number of justifications must never be presented as corroboration strength. Scalar confidence is correctly omitted. Common-cause assessment belongs to GEI corrective independence (NB-05).
- **Coverage.** The wording overclaims; the semantics do not.
- **Needs.** Documentation (wording). A shared-leaf fixture would only re-test ATMS-native behavior, so none is proposed.
- **Baseline.** ATMS environments over shared assumptions.
- **Falsifier / success.** Not applicable.
- **Priority.** P3.

### GB-15 — Typed provenance: interpretation must not be consumed as evidence

- **Source.** GEI round 10 §6: "PROV can show that interpretation I was derived from evidence E, but PROV alone does not say I is an interpretation and therefore must not be consumed as if it were direct evidence." ST-001. Hermeneia `machine suggestions non-canonical`. Continuity-Node raw/interpretation separation.
- **Implication.** Internally, Memory Lab separates canonical evidence (`EV-…`) from derived records (`DM-…`). In a substrate such as Graphiti, however, an LLM-extracted fact and a Memory Lab-derived fact are both plain `EntityEdge`s. An adapter must preserve the derivation type, or derived conclusions become indistinguishable from evidence-extracted facts.
- **Coverage.** Internal only.
- **Needs.** Measured in the GB-08 experiment (derivation type carried as an adapter attribute).
- **Baseline.** SEPIO EvidenceLine vs EvidenceItem.
- **Falsifier / success.** The adapter must be able to distinguish the two for every edge.
- **Priority.** P2.

### GB-16 — Human correction changes coverage, not disposition authority

- **Source.** CVD profile §11 and REC profile §9: a human who supplies an omitted contrary item moves coverage `unknown → known-incomplete`, which triggers review. The human does not decide the disposition unless they hold standing for that decision.
- **Implication.** This is a concrete coverage-state transition that Memory Lab fixtures do not exercise. Standing belongs elsewhere (NB-02).
- **Coverage.** No.
- **Needs.** A fixture inside GB-04.
- **Baseline.** A W3C Web Annotation correction plus a DQV re-measurement.
- **Falsifier / success.** Part of GB-04.
- **Priority.** P3.

### GB-17 — Views carry as-of identity for downstream fencing

- **Source.** Telos experiment 0007: stale replicated views were survivable only because effect commitment revalidated against a current fence. Pyxis preserves decision-time evidence and blocks backward projection. CVD-004 requires that later evidence not appear to have existed at the earlier decision time.
- **Implication.** Every Memory Lab view must carry the knowledge-time identity it was computed at. Consistency and reassessment artifacts already do (`assessed_at_snapshot`). **Fencing a stale view before action is Telos's job, not Memory Lab's.**
- **Coverage.** Partial (synthetic snapshot IDs).
- **Needs.** Documentation (interface obligation IO-03).
- **Baseline.** Bitemporal as-of queries.
- **Falsifier / success.** Not applicable.
- **Priority.** P3.

### GB-18 — The junction claim

- **Source.** C-001 independent review: the one part that is "clearly GIE's own" is the claim that failures cluster where individually familiar semantic boundaries meet, especially when capable models can silently collapse them.
- **Implication.** Memory Lab's distinctions are exactly such junctions: support/consistency, consistency/view, and world-change/correction. Graphiti's LLM contradiction judge, followed by a temporal-recency rule, is a concrete collapse mechanism at the consistency → world-change junction. Memory Lab's adversarial fixtures are best used as junction probes for adapters. GEI owns the junction-claim protocol itself.
- **Coverage.** No.
- **Needs.** Documentation. Used as the evaluation lens for GB-08.
- **Baseline.** Not applicable.
- **Falsifier / success.** Owned by GEI.
- **Priority.** P3.

### GB-19 — Reality feedback re-enters only as evidence

- **Source.** GEI T-GIE-07 / L-001: reality feedback has no concrete owner, and "later success does not retroactively validate earlier reasoning."
- **Implication.** Memory Lab's append-only reassessment plus valid/knowledge time is a plausible substrate for outcome evidence re-entering without rewriting decision-time records. Updating reliance, routing, or governance from outcomes is **not** Memory Lab's (NB-08).
- **Coverage.** No.
- **Needs.** Documentation (boundary).
- **Baseline.** Bitemporal decision/outcome journals (GEI's stated alternative).
- **Falsifier / success.** Owned by GEI L-001.
- **Priority.** P3.

## 5. Negative boundary: what does not belong in Memory Lab

Memory Lab can *preserve information about* each of these without *owning* it. Owning any of them would silently turn preserved epistemic state into authority.

| ID | Responsibility | Owner | What Memory Lab may do |
|---|---|---|---|
| NB-01 | Authority, authorization, execution eligibility, occurrence | Telos; ODRL/IAM/policy engines (GEI ST-005, ST-009, ST-010) | Nothing beyond refusing to emit such fields |
| NB-02 | Participant standing; steward acceptance; interpretation stewardship | Hermeneia; GEI standing transitions | Consume steward acceptance as an **input** to an admission policy, never as support, coverage, or admission itself |
| NB-03 | **Choosing** the admission policy for a scope (withhold vs plural-admit, coverage thresholds) | Telos / application governance | Record which policy identity/version produced each disposition (GB-01, GB-09) |
| NB-04 | Decision sufficiency: whether remaining uncertainty is material enough to block action | Telos; GEI `decision-sufficiency-v0`; round 06 value-of-information | Report support, coverage, consistency, unknowns faithfully |
| NB-05 | Corrective independence / common-cause analysis across participants | GEI ST-006; MASI | Keep justifications and evidence paths inspectable (GB-14) |
| NB-06 | Downstream use rights; lawful erasure | ODRL/DPV; governance (ST-008) | Require erasure to be explicit and distinct from withdrawal (GB-13) |
| NB-07 | Evidence capture and decision-time availability | Pyxis | Reference Pyxis evidence-state identity; never backfill evidence to an earlier knowledge time |
| NB-08 | Updating reliance, routing, or governance from outcomes | Unowned in GEI (TrustVector/Telos candidates) | Accept outcome observations as new evidence only (GB-19) |
| NB-09 | Running C-001 or authoring its sealed instruments | GEI `research/experiments/` | Supply the minimum historical-record shape (GB-12) |
| NB-10 | SHACL processor conformance of the GEI suite | GEI `scripts/` | Pass GEI shapes at the export boundary (GB-11) |
| NB-11 | Truth | Nobody's lifecycle state (CVD §12: "Do not add `true`") | Never emit `true`/`false` as disposition |
| NB-12 | Retrieval runtime, graph runtime, TMS engine, temporal DB | Graphiti, Whyis, TMS/ATMS, bitemporal stores | Adapters and conformance tests only (AGENTS.md) |
| NB-13 | Generating interpretations | Hermeneia; model participants | Treat interpretations as typed candidate records (GB-15) |

## 6. Interface obligations

| ID | Direction | Obligation |
|---|---|---|
| IO-01 | Pyxis → Memory Lab | Evidence arrives with stable identity and decision-time availability. Memory Lab snapshot identity references that evidence state and never re-owns capture. |
| IO-02 | Hermeneia → Memory Lab | Interpretations arrive typed as interpretations (candidate derived records), not evidence. Steward acceptance may feed an admission policy; it never sets support, coverage, or consistency. |
| IO-03 | Memory Lab → Telos / MASI / models | Exports carry support, coverage (with envelope), consistency, disposition (with scope, policy reference, and as-of identity), and history references. They carry **no** authority, eligibility, or use-right fields. `admitted` must not render as authorized or true; `withheld` must not render as false; `unknown` coverage must stay unknown. |
| IO-04 | Telos / governance → Memory Lab | Admission policy identity and version are supplied by governance. Memory Lab records them and never selects them. |
| IO-05 | Memory Lab ↔ GEI conformance | Memory Lab states must be exportable to PROV/DQV/CVD and pass ST-002/ST-003 (GB-11). |
| IO-06 | Reality → Pyxis → Memory Lab | Outcome observations re-enter through Pyxis as evidence. Memory Lab reassesses without rewriting decision-time records. |

## 7. Execution selected from this audit

Ranked by information gain per unit of tractable work in this environment:

| Rank | Candidate | Information gain | Tractable here? |
|---|---|---|---|
| 1 | **GB-08 Graphiti substitution (Polaris)** | High. It tests EP-07/08/09/10 and a runtime-shrink hypothesis directly | Yes: `graphiti-core==0.30.2` + embedded Kuzu. No LLM key available, so contradiction verdicts are injected under experimental control and Graphiti's deterministic code is exercised for real |
| 2 | GB-01/02/09 current-view vs application-state baseline | High, and cheap: attacks EP-08 | Yes (stdlib `sqlite3`) |
| 3 | GB-04 coverage decision value | Highest burden, but needs a defensible task set with ground truth | Design yes; a credible run needs non-hand-picked tasks |
| 4 | GB-05 argumentation baseline | Medium: likely a clean narrowing | Yes, with an existing solver |
| 5 | Whyis reassessment substitution (#11 second target) | Medium | No here: needs a Whyis deployment (Blazegraph/Java); no Docker |
| 6 | GB-11 export to GEI SHACL | Medium (interface) | Yes, with pinned `rdflib`/`pyshacl` |

GB-08 was executed in this session. Results, including what Graphiti makes unnecessary in Memory Lab, are in `docs/graphiti-substitution-v0.md`.

Rank 2 (GB-01, GB-02, GB-09) was then executed as #13; see `docs/appstate-baseline-v0.md`.

- The ordinary baseline reproduced every Memory Lab current-view outcome.
- It also represented scope and policy version.
- EP-08 is therefore narrowed to a conformance obligation.

Rank 3 (GB-04) was executed as #12, as a preregistered test on SciFact; see `docs/coverage-scifact-v0.md`.

- An explicit coverage state added no decision value.
- GB-03's schema change is withdrawn in favour of mapping to REC values at export.

After all three experiments, `docs/what-remains-v0.md` redefines Memory Lab as a conformance harness for obligations O1–O8.

## 8. Relationship to existing issues

| Existing issue | Relationship |
|---|---|
| #11 prior-art integration | Umbrella. GB-08 executes its first adapter experiment. GB-04 and GB-01/02 decompose its unchecked "coverage decision value" and "current-view vs application state" items into focused issues. GB-12 redirects its inheritance item to GEI C-001. The Whyis target remains in #11 unchanged |
| #1 migrate validated local scripts | Engineering track; unaffected by GEI findings. See §9 |
| #2 detached round-trip audit | Engineering track; unaffected by GEI findings. See §9 |

New focused issues created from this audit:

| Issue | Findings |
|---|---|
| #12 Evidence coverage: decision-value experiment over OTel GenAI + PROV + DQV | GB-03, GB-04, GB-16 |
| #13 Current-view admission vs ordinary application state | GB-01, GB-02, GB-07, GB-09 |
| #14 Argumentation baseline for supported-conflict admission | GB-05, GB-07 |
| #15 Neutral export to the GEI PROV/DQV/CVD profile | GB-06, GB-10, GB-11 |

No issue was created for:

- GB-08, which was executed here under #11;
- GB-12, which is resolved by documentation;
- the P3 documentation findings.

## 9. Engineering-track items not advanced

- **#1.** A local Spotlight/filesystem search for the validated legacy scripts named in the issue (for example `build_source_snapshot.py`, `audit_roundtrip_logical_equivalence.py`, `apply_incremental_changed_v0_2.py`) found no copies outside this repository. The scripts live in the Magician workspace, which is not accessible here. **Not reconstructed from memory; remains open.**
- **#2.** No recovered Chroma index (`chroma.sqlite3`) or 302,240-record baseline is present on this machine. **The detached audit was not rerun and remains outstanding. No equivalence is claimed.**

## 10. What this audit does not establish

- It does not show that any GEI profile is correct or should be adopted wholesale.
- It does not show that the GEI-derived findings improve real decisions. Several are explicitly scheduled to be falsified by ordinary baselines (GB-01, GB-04, GB-05, GB-09).
- It does not ratify ML-EP-0.
- Its negative-boundary table is a design constraint, not evidence that the named owners implement those responsibilities today. Several owners are research systems, and some responsibilities (NB-08) are currently unowned.

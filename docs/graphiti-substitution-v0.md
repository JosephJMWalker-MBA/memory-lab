# Graphiti Substitution v0: derived-conflict-v0 (Polaris)

**Status:** executed synthetic substitution experiment. This is not production validation and not a real-LLM result.  
**Date:** 2026-09-14  
**Tracker:** GitHub issue #11 (first adapter experiment)  
**Audit links:** `gei-backpropagation-audit.md` GB-08, GB-13, GB-15, GB-18  
**Evidence file:** `experiments/graphiti-conflict-v0/results/graphiti-conflict-v0.observed.json`  
**Run procedure:** `experiments/graphiti-conflict-v0/README.md`

## 1. Question

> Can Graphiti cleanly preserve both individually support-valid incompatible histories while Memory Lab separately withholds them from the current view?

Measured:

- what Graphiti provides natively;
- what requires configuration;
- what requires a thin adapter;
- which Memory Lab machinery becomes unnecessary;
- whether any surviving gap is semantic or an implementation artifact.

A result in which Graphiti makes Memory Lab smaller counts as success.

## 2. What was executed and what was not

### Executed

| Item | Detail |
|---|---|
| Runtime | `graphiti-core==0.30.2`, `kuzu==0.11.3` (embedded; the Kuzu backend is deprecated upstream), Python 3.13.5, macOS arm64 |
| Memory Lab code | commit `c3d12d7`, clean working tree (recorded in the evidence file) |
| Graphiti code actually run | `EntityNode` / `EpisodicNode` / `EpisodicEdge` / `EntityEdge` persistence and readback on Kuzu; `resolve_extracted_edge`, including the exact-fact fast path, verdict handling, attribute handling, the "new edge born expired" rule, and the `resolve_edge_contradictions` rule it calls; `Graphiti.remove_episode` |
| Telemetry | disabled (`GRAPHITI_TELEMETRY_ENABLED=false`) |

### Not executed

| Item | Consequence |
|---|---|
| Any LLM | Graphiti's contradiction verdict (`dedupe_edges.resolve_edge`) is **scripted**. Once edges carry `valid_at`, it is the only LLM step on the exercised paths (`_extract_edge_timestamps` returns early). Any other LLM call raises, and none occurred. |
| LLM extraction; `add_episode` / `add_triplet` end-to-end | Both need an LLM and an embedder. Their resolution step is the part exercised here. |
| Embeddings and hybrid search | Contradiction candidate sets were **supplied directly**, not found by Graphiti's search. Graphiti issue #1728 reports that real candidate search is unscoped. |
| Neo4j / FalkorDB backends | The Graphiti logic exercised is backend-independent Python; persistence was Kuzu only. |

The results therefore say **what Graphiti's own code does given a contradiction verdict**. They say nothing about how often a real model returns that verdict.

## 3. Mapping

`tests/run_graphiti_adapter_v0.py` translates the Polaris fixture without an LLM:

| Fixture item | Graphiti representation |
|---|---|
| canonical evidence item | `EpisodicNode` (text in `content`) |
| extracted fact | `EntityEdge` from subject entity to value entity, `episodes=[its episode]` |
| derived record (Polaris blocked / ready) | `EntityEdge` whose `episodes` is the canonical evidence closure |
| valid time | `valid_at` / `invalid_at` |
| knowledge time | `created_at` / `expired_at`, with snapshots given fixed reference times |
| Memory Lab metadata | edge `attributes`, mirrored in an adapter side table keyed by edge UUID (eight keys: record id, record type, qualifiers, derivation type, justifications, evidence refs, change kind, snapshot) |

Two Memory Lab functions were reused **unchanged** over Graphiti state:

- current-view admission: `assess_consistency` from `derived-conflict-v0`;
- support evaluation: `assess` from `multiple-justifications-v0`.

Admission is a read-only projection. Nothing is written back to Graphiti.

## 4. Scenario results

All ten scenarios run against real Graphiti code; the verdicts are scripted. **Graphiti-current** means `invalid_at` and `expired_at` are both null, which is the natural filter an application would pass through `SearchFilters`. Graphiti itself defines no "current view", and no default temporal filter was found in its search code.

| Scenario | Scripted verdict | Timing | Graphiti outcome | Memory Lab admission | Failed checks |
|---|---|---|---|---|---|
| `direct_write_world_change` | "Sigma-clear contradicts Sigma-blocked" | clear is later (world change) | Sigma-blocked closed (`invalid_at` = 06-15) and retained. **Polaris-blocked stays Graphiti-current.** | 0400: both status records withheld. 0401: blocked support withdrawn, ready admitted (`resolved_by_support_change`) | none (EP-08 read-only: pass) |
| `native_equal_valid_at_contradiction` | "ready contradicts blocked" | equal `valid_at` | nothing closed; both Graphiti-current | both withheld | none |
| `native_equal_valid_at_no_contradiction` | "no contradiction" | equal | nothing closed; both Graphiti-current | both withheld | none |
| `native_later_valid_at_contradiction` | "ready contradicts blocked" | ready later | blocked closed with `invalid_at` = ready.`valid_at` | "compatible": both admitted for disjoint intervals (conflict laundered into succession) | EP-07, EP-10 |
| `native_earlier_valid_at_contradiction` | "ready contradicts blocked" | ready earlier | **new** ready edge born closed (`invalid_at` = blocked.`valid_at`) | "compatible": both admitted for disjoint intervals | EP-07, EP-10 |
| `native_multivalue_equal_valid_at_wrong_verdict` | "Tau-dependency contradicts Sigma-dependency" (wrong) | equal | nothing closed | status conflict withheld; both dependencies admitted | none |
| `native_multivalue_later_valid_at_wrong_verdict` | same wrong verdict (#1728 shape) | Tau later | Sigma-dependency closed | **cascade:** Polaris-blocked loses support, conflict falsely "resolved" for ready | EP-07, EP-09, EP-10 |
| `corroboration_fast_path` | none (**0 LLM calls**) | restated later | episode appended to the existing edge (2 episodes) | unchanged | none |
| `remove_first_supporting_episode` | none | n/a | release-checks fact **deleted** despite a surviving second episode; the derived ready edge keeps a dangling episode reference | **cascade:** ready loses support, conflict falsely "resolved" for blocked | EP-01, EP-02, EP-04 |
| `remove_corroborating_episode` | none | n/a | fact kept; its `episodes` still lists the removed episode | unchanged | EP-02 |

Notes on the results:

- In `direct_write_world_change`, the projection reproduced the native conflict lane's assessments **byte-for-byte**, with identical `assessment_id`s. The CI test asserts this.
- Every edge that went through the LLM-verdict branch of `resolve_extracted_edge` came back with empty `attributes`: 7 of 7 new edges. The one edge merged by the exact-fact fast path kept its attributes. The side table is what kept Memory Lab's metadata recoverable.

## 5. Findings

### F1. Graphiti's data model preserves both incompatible supported claims

Written directly, bypassing resolution, the two Polaris status edges coexist with:

- provenance to their evidence episodes;
- valid time and system time;
- no closure.

Memory Lab's admission over that state withheld both and wrote nothing (EP-08 pass). Graphiti's representation is **native** for this requirement. Admission is a **thin projection** that reuses existing conflict-lane code.

### F2. Graphiti's native resolver resolves conflicts only by recency

Whatever the LLM flags as contradictory is handed to `resolve_edge_contradictions` and the "new edge born expired" rule. Both compare `valid_at` only. So on the edge-resolution path of 0.30.2 there is exactly one conflict operator: the later `valid_at` wins, and the loser gets an `invalid_at`.

For the three timing cases:

- **Equal `valid_at`:** nothing closes, regardless of the verdict, and both claims stay Graphiti-current. Graphiti's "current" set is then plural, not withheld.
- **Different `valid_at`:** the resolver writes an unsupported world-time end onto a support-valid record. That turns a consistency problem into a false temporal succession, which fails EP-07 and EP-10.
- **Memory Lab's admission over those native fields** then sees no conflict at all, because the intervals no longer overlap. The collapse happens upstream, in the data. Only the conformance checks see it.

### F3. For a genuine world change, Graphiti is correct but does not propagate

Sigma-clear correctly closed Sigma-blocked at the change time and retained it. But Graphiti has no edge-to-edge derivation, so Polaris-blocked remained Graphiti-current after its only support path ended.

Memory Lab's reused justification evaluation withdrew Polaris-blocked's support and resolved the conflict. Reassessment propagation is **missing** in Graphiti. It is truth-maintenance work, which should be delegated to a TMS/ATMS rather than grown in the adapter.

### F4. A wrong verdict on a multi-valued relation cascades into a false resolution

With a later `valid_at`, the wrong verdict closed the Sigma dependency. That removed an antecedent of Polaris-blocked, so the status conflict was "resolved" for ready without any evidence about status. EP-09 (explicit conflict basis) flagged the root cause, because `depends_on` has no exclusivity constraint.

With equal `valid_at`, the same wrong verdict was harmless.

This is the mechanism behind the collateral retirements reported in Graphiti #1728, and a concrete instance of the GEI "junction" claim (audit GB-18).

### F5. `remove_episode` is deletion, not withdrawal

It deletes edges whose **first** episode is the one removed, even when a later episode still supports them. It does not clean up references in other edges' `episodes`.

Mapping Memory Lab withdrawal onto it failed EP-01, EP-02, and EP-04, and cascaded into a false conflict resolution. It may well be intended as "undo ingestion." Either way, an adapter must never use it for epistemic withdrawal (audit GB-13).

### F6. Graphiti records that an edge closed and when, but not what closed it

`EntityEdge` in 0.30.2 has no field for the invalidating edge or episode, and no successor field (verified by inspecting the source and grepping the package). An adapter must itself record:

- the conflict basis (EP-09);
- the successor required by the GEI CVD profile (CVD-004).

### F7. Native resolution clears adapter attributes

When no custom edge type matches, `resolve_extracted_edge` sets `attributes = {}` on the resolved edge. When a custom type does match, the source shows attributes are re-extracted by the LLM with `merge_mode='replace'`. That branch was source-inspected, not executed.

Memory Lab metadata therefore cannot live only in Graphiti attributes on any native-resolution path.

### F8. Exact restatement is deterministic corroboration

Graphiti's exact-fact fast path appended the second episode with zero LLM calls. Corroboration (`evidence_added`) is **native**.

## 6. Classification

| Responsibility | Result | Evidence |
|---|---|---|
| Evidence units, raw text | **NATIVE**: `EpisodicNode.content` | all scenarios |
| Evidence references / provenance | **NATIVE**: `EntityEdge.episodes`. The adapter maps a derived record's evidence closure into it | translation; EP-02 |
| Corroboration | **NATIVE**: exact-fact fast path, no LLM | `corroboration_fast_path` |
| Valid time / knowledge time | **NATIVE** fields | all |
| Retention of closed facts | **NATIVE**, but by in-place update of `invalid_at` / `expired_at`, not versioned records | all closing scenarios |
| Stable proposition identity | **ADAPTABLE**: Graphiti UUIDs are opaque, so the semantic record id is carried as metadata | translation |
| Preserving both incompatible supported claims | **NATIVE** via direct write. Via the native resolver, preserved only when `valid_at` is equal | F1, F2 |
| Explicit conflict basis (EP-09) | **MISSING** natively (LLM verdict, no constraint, no recorded basis). **ADAPTER**: the constraint check is reused | F4, F6 |
| Current-view admission (EP-08) | **ADAPTER** (read-only projection). Graphiti has no withheld state, and `SearchFilters` are per-edge, so pairwise-conflict admission cannot be expressed as a filter without precomputation | F1 |
| Support validity vs consistency (EP-07) | Preserved **only if constrained predicates bypass the native resolver** | F2 |
| World change vs correction (EP-10) | The native resolver encodes every flagged contradiction as world-time succession. That is correct for genuine world change (F3) and wrong for concurrent conflict (F2). A retroactive correction with the same `valid_at` cannot close the older edge natively. The data model *can* represent retraction (`expired_at` set, `invalid_at` null) through a direct write: **ADAPTABLE**, never produced natively | F2, F3 |
| Justification / derivation dependencies | **MISSING** (no edge-to-edge derivation). Carried as metadata; evaluation reused. Belongs in a TMS/ATMS | F3 |
| Reassessment propagation | **MISSING** | F3 |
| Withdrawal without deletion (EP-01/04/05) | Graphiti's removal operation is deletion. **Do not use it for withdrawal** | F5 |
| Successor for `superseded` (CVD-004) | **MISSING** field; the adapter must record it | F6 |
| Scope | `group_id` partitions data natively. Different dispositions of the same edge per scope are **adapter-side** | design |

## 7. What becomes unnecessary in Memory Lab

With Graphiti, or a comparable temporal graph, as the substrate, Memory Lab should not own any of these:

- a record store or storage keys;
- evidence-text storage or evidence references;
- valid-time / knowledge-time fields;
- historical retention;
- corroboration merging;
- retrieval.

That is the storage role of `derived-memory-record-v0.2`. The substitution map predicted this; it is now executed for one fixture.

What remains Memory Lab-owned, measured as adapter code (line counts recorded by the runner):

| Piece | Lines | Status |
|---|---|---|
| fixture → Graphiti translation (`translate_polaris`, `graphiti_edge`) | 115 + 16 | fixture-specific ingestion glue |
| metadata access and projection (`ml_meta`, `edge_candidate`) | 10 + 11 | thin |
| support evaluation over current edges (`support_assessments`) | 18 | reuses `assess` unchanged. **TMS work that should move to a TMS/ATMS, not grow here** |
| admission projection (`admission_projection`) | 59 | reuses `assess_consistency` unchanged |
| predicate constraint | reused | EP-09 input |
| ML-EP-0 conformance checks (`conformance_report`) | test code | **the durable contribution**: detected every collapse the native paths produced |

## 8. Semantic gap or implementation artifact

### Semantic differences

These are coherent product choices, not bugs.

- **S1. Graphiti's only conflict operator is temporal succession.** It cannot represent "concurrently supported, jointly inconsistent, unresolved" except by leaving both claims current. That is a reasonable default for agent memory, where most contradictions are updates. It is also exactly where Memory Lab's EP-07/EP-10 diverge: the consistency → world-change junction.
- **S2. Invalidation is judged by an LLM participant,** with no inspectable constraint and no recorded basis (EP-09).
- **S3. There are no derivation dependencies and no propagation.** This gap belongs to TMS, not Memory Lab.

### Implementation artifacts

These are fixable without changing Graphiti's semantics.

- **A1.** Attributes are cleared on native resolution. A side table or custom edge types work around it.
- **A2.** Invalidation candidates have been unscoped since upstream PR #906 (issue #1728). Not exercised here, because candidates were supplied directly. Real use would widen exposure to F4.
- **A3.** `remove_episode` uses a first-episode rule and leaves dangling references.
- **A4.** Closure is an in-place mutation, so the prior belief state is reconstructible only from `expired_at`.
- **A5.** The Kuzu backend is deprecated.
- **A6.** There is no successor or basis field.

## 9. Falsifier outcome

The pre-stated outcomes (substitution map §12) were: native/adaptable, awkward but possible, or not representable without bypassing core behavior.

**Result: adaptable, by bypassing Graphiti's contradiction resolver for constrained predicates.**

- **Representation is native.** Memory Lab narrows: storage, temporal fields, provenance, history, and corroboration move to the substrate.
- **Resolution is where the semantics diverge.** Memory Lab's behavior requires three things:
  1. writing constrained-predicate facts directly, or never letting the native resolver close them;
  2. holding admission, constraints, justifications, conflict basis, and successor outside Graphiti;
  3. keeping a side table.

The distinctions EP-07, EP-09, and EP-10 survive as **conformance obligations on the composition**, not as a reason to build a runtime. They detected every collapse observed here.

Graphiti is not graded negatively. Its resolver implements a coherent update semantics. The experiment locates the precise point where the two semantics part.

## 10. Negative finding about our own harness

On the first live run, EP-05 ("withdrawal is not negation") flagged the Polaris-ready edge as an invented proposition in four scenarios. That edge was the arrival each scenario deliberately introduced, so the flag was a **checker bug**, not Graphiti behavior. The check now takes the set of edges an operation was asked to add.

The CI test's hand-built expectations for recency collapse, multi-valued over-invalidation, and deletion-as-withdrawal were written before the first live run and matched the observed behavior unchanged.

## 11. Threats to validity

- **Scripted verdicts.** Nothing here estimates real LLM contradiction behavior. Upstream reports cover both over-invalidation (#1728) and missed contradictions (#1666, as referenced in #1728).
- **Candidate sets were supplied directly.** Graphiti's real search path is broader (#1728).
- **One hand-designed synthetic fixture,** built specifically to stress this boundary. The timing variants are perturbations, not fixture facts.
- **Derived facts are not how Graphiti normally learns facts.** A real deployment would LLM-extract "Polaris status is blocked" from an episode with no justification structure at all. The derived-edge mapping is an adapter decision.
- **Kuzu only.**
- **The same author wrote the adapter and the conformance checks.** Partial mitigation: expectations were fixed before the live run, and CI recomputes every recorded verdict from the recorded states.
- **The EP-10 check infers successors.** Graphiti records no basis for a closure. The check therefore matches a successor by subject, predicate, qualifiers, and `valid_at == invalid_at`. A production adapter should record the basis at resolution time, for example as a PROV activity, rather than infer it.
- **The adapter both selects and records its admission policy.** It hard-codes the lane's `withhold` policy. Real use must take the policy from governance input (audit NB-03, IO-04).

## 12. Next

1. **Highest information next:** current-view admission vs ordinary application state. This experiment showed Memory Lab's admission is a pure projection over substrate state. The open question is whether a plain event-sourced projection table already provides everything.
2. **Real-LLM replication** on Neo4j or FalkorDB, measuring how often concurrent conflicts and multi-valued relations are flagged. This needs infrastructure and a provider key, which is a user decision. It was not attempted here.
3. **Delegate the justification evaluation** to an existing TMS/ATMS implementation before any further adapter growth.

# Current-View Admission vs Ordinary Application State v0

**Status:** executed synthetic comparison (stdlib `sqlite3`, runs in CI)  
**Date:** 2026-09-14  
**Issue:** #13  
**Audit links:** `gei-backpropagation-audit.md` GB-01, GB-02, GB-07, GB-09  
**Runner:** `tests/run_appstate_baseline_v0.py`

## 1. Question

ML-EP-0 EP-08 ("current-view admission separation") was marked *under falsification against ordinary application state*. The substitution map (§6) put the burden on Memory Lab to show that a portable conformance boundary adds value, rather than merely renaming a well-designed projection table.

This experiment asks whether a plain event-sourced application design already preserves every current-view distinction exercised by the derived-memory fixtures. It is designed so the baseline can win.

## 2. Designs compared

| Design | What it is |
|---|---|
| **Memory Lab artifacts** | The existing lanes' outputs (consistency, reassessment, and justification assessments), rebuilt with the lane code and mapped onto GEI current-view disposition values |
| **B1, recorded conclusions** | An append-only `facts` table. Derivation rules run as a recursive SQL CTE. Each snapshot's derived conclusions are appended as rows. A `single_valued` table declares exclusivity. Dispositions are a query under a **scoped, versioned `policies` table** |
| **B2, recompute-on-read** | Same as B1, except derived conclusions are recomputed on read with whatever rule version is currently deployed (the common read-model pattern) |
| **B0, naive control** | One mutable status per entity, recomputed on every change, with precedence `blocked > ready` and a closed-world default of `clear` |

B0, B1, and B2 import no Memory Lab semantics. B1 and B2 share **77 lines of SQL** (schema, current facts, supersession, rules) and **97 lines of Python**.

### Fixtures

- `derived-reassessment-v0`: Sigma → Vega → Helios
- `multiple-justifications-v0`: Aurora
- `derived-conflict-v0`: Polaris

Knowledge time is the snapshot ordinal × 10.

### Scopes and policies

Polaris is viewed under two scopes:

- `release-gate`, which withholds unresolved conflict;
- `exploratory`, which admits conflicting records plurally.

A second `release-gate` policy version (plural admission) becomes effective at time 4005.

### Rule-change probe

After snapshot 0201, rule version 2 is deployed. It propagates `blocked` through direct dependencies only. The 0200 view is then replayed.

### Expectations were fixed before the first run

The runner's assertions state them. All held on the first run.

## 3. Results

| Check | Memory Lab artifacts | B1 recorded | B2 recompute | B0 naive |
|---|---|---|---|---|
| **C11** equivalence: dispositions equal the CVD mapping of Memory Lab artifacts at all seven snapshots | reference | **pass** | **pass** | fail |
| **C3** withdrawal ≠ negation: no invented `clear` | pass | pass | pass | **fail** (Vega, Helios, Aurora) |
| **C4** both supported Polaris claims preserved | pass | pass | pass | **fail** (`ready` overwritten) |
| **C1** history, same rule: an earlier view re-queried later equals what was shown then | pass | pass | pass | unrepresentable |
| **C1** history after a rule change | pass (immutable records) | **pass** | **fail** | unrepresentable |
| **C10** why a record is retained after one support path is lost (Aurora at 0301: only the Tau path) | pass | pass | pass | unrepresentable |
| **C8** scoped dispositions: release-gate withholds while exploratory admits, at the same time | **unrepresentable** (no scope) | pass | pass | unrepresentable |
| **C9** policy version change flips a disposition; derived rows and conflict set unchanged; earlier view reproducible | **unrepresentable** (no policy) | pass | pass | unrepresentable |

Two details behind the table:

- **B2 after the rule change:** the replayed 0200 view admits status only for `Module Sigma` and `Project Vega`. Helios's `blocked` conclusion, which was shown at 0200 under rule v1, is gone from history.
- **B0 at the final snapshots:** it shows `clear` for Vega, Helios, and Aurora, with no evidence for any of them.

## 4. Findings

### F1. Current-view admission is an ordinary projection

B1 reproduced every Memory Lab current-view outcome: three lanes, seven snapshots, 77 + 97 lines. It also expressed two things Memory Lab's artifacts cannot: per-scope dispositions and policy versions.

**EP-08 is not a Memory Lab primitive. The simpler baseline wins.**

### F2. Memory Lab's artifacts are less expressive than the baseline for admission

They carry no scope and no policy identity or version (GB-01, GB-09). They should not be promoted as *the* representation of admission. That representation is an application's projection with scope and policy provenance, which is what GEI's CVD profile already describes.

### F3. Reassessment plans are for efficiency and audit, not correctness

B1 and B2 computed the same current views without dependency-closure plans. Targeted closure and parent-before-child ordering buy efficiency and an explanation of what was affected. In this fixture set, the rule-body provenance column (`via`) supplied that explanation.

### F4. Surviving obligation: record conclusions; do not recompute them on read when rules can change

Recompute-on-read silently rewrote history once the rule changed. This is a known event-sourcing hazard: rebuilding read models with new code. It is prior art, not a Memory Lab discovery. It is also the most operational form of "historical derived status ≠ current-view admission."

Draft amendment to ML-EP-0 EP-01: a change of derivation rule or interpretation must not rewrite what was concluded under the earlier rule.

### F5. Withdrawal ≠ negation and support ≠ consistency are not automatic

B0 invented `clear` through its closed-world default and erased the Polaris conflict through precedence. The careful designs preserve both, and the checks detect the difference.

### F6. The CVD mapping is lossless where tested (GB-02)

Reassessment results map to CVD values and back without loss: support outcome, resulting view, and the presence of a replacement all survive the round trip. The consistency and justification artifacts were mapped one way only. The CVD vocabulary adds explicitness plus a place for scope and policy. It adds no new information.

## 5. What narrowed

- **EP-08** is reclassified from "candidate conformance distinction under falsification" to "ordinary application pattern". Memory Lab keeps the **checks**.
- **Reassessment plan and result artifacts** are not needed for current-view correctness. They are optional, for efficiency and audit.
- **Memory Lab's durable contribution in this area** is checks C1–C11 plus the fixtures. These are a portable test that separates B1 from B2 and B0. It is not the schemas, and not a runtime.
- **Draft ML-EP-0 amendments** are recorded in `substitution-conformance-map-v0.md` §9:
  - EP-01 extended to cover rule and interpretation changes;
  - EP-08 restated as scoped and policy-attributed.

## 6. Threats to validity

- **The baseline author knew the Memory Lab semantics.** A designer starting cold might reach for precedence instead of withholding, or skip scope and policy tables. B0 stands in for that common default. The result is conditional: ordinary machinery suffices **once the obligations are known**. That conditionality is the only thing Memory Lab still owns here.
- **Derived facts are evaluated as of knowledge time.** Valid-time intervals on derived facts are not modeled, so Polaris's temporal overlap is trivial.
- **Base facts use latest-wins for single-valued predicates.** That is the same recency rule found in Graphiti. It is correct here, because each later base fact in these fixtures is an explicit world change. It would mishandle concurrent contradictory base evidence, which none of these three fixtures exercise (derived-memory v0's unresolved-contradiction case does). **Untested.**
- **Scale.** Synthetic data; three hand-designed fixtures; seven snapshots.
- **The `why` column is a by-product of the SQL join.** Not every application exposes rule-body provenance.
- **Memory Lab's "pass" on history after a rule change is by construction** (immutable derived records). No rule change was executed in Memory Lab code.

## 7. Next

1. **#12 evidence coverage.** This is now the only candidate Memory Lab distinction not yet reduced to ordinary machinery.
2. **Extend this baseline with concurrent contradictory base evidence** (derived-memory v0). This tests whether latest-wins is the silent failure at the base-fact level, in both Graphiti and ordinary state.
3. **#14 argumentation.** Could replace B1's conflict rule with grounded semantics, computed by an existing solver.

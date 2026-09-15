# Coverage Decision Value v0 (SciFact)

**Status:** executed preregistered experiment. Real collection, oracle stance, dev split only.  
**Date:** 2026-09-15  
**Issue:** #12  
**Audit links:** `gei-backpropagation-audit.md` GB-03, GB-04  
**Preregistration:** `experiments/coverage-scifact-v0/PREREGISTRATION.md`, commit `66892ed`, before any arm ran  
**Code and run:** commit `5e4ae07`, clean tree  
**Evidence:** `experiments/coverage-scifact-v0/results/coverage-scifact-v0.results.json`  
**Verification:** CI recomputes every aggregate, threshold, prediction, and bootstrap interval from the recorded per-claim rankings and labels (`tests/run_coverage_scifact_v0.py`).

## 1. Question

> Does an explicit evidence-coverage state (`not-assessed | unknown | known-incomplete | bounded-complete`) change claim-verification decisions beyond what provenance plus retrieval metrics already give?

The preregistration fixed the interpretation in advance: a negative result counts as a narrowing.

## 2. What was run

- **Data.** SciFact dev set (300 claims) against the released 5,183-abstract corpus. The 809 train claims were used only to choose the A2-gate threshold.
- **Stance.** Oracle stance at abstract level, taken from SciFact's gold labels. Unjudged abstracts count as non-evidence.
- **Retrieval.**
  - P1: BM25 over title and abstract (k1 = 0.9, b = 0.4).
  - P2 (audit): sentence-level TF-IDF.
  - k ∈ {3, 10, 20}; k = 10 is primary.
- **Arms.** Eight arms plus an exhaustive oracle ceiling, exactly as preregistered. No parameter or arm changed after the dev run.
- **Structural limit, disclosed before registration.** SciFact's judged universe contains **no claim with evidence of both polarities**. So hypothesis H4 (coverage catching "support retrieved while contrary evidence exists unretrieved") cannot be observed here.

## 3. Results

### Predictions: all six held

| # | Prediction | Observed |
|---|---|---|
| 1 | NEI-semantics arms make 0 wrong decisions at every k | 0 wrong for all six D1 arms, at k = 3, 10, and 20 |
| 2 | Default-accept makes at least 112 wrong accepts at k = 10 | **119** (112 NEI claims, plus 7 contradicted claims whose contradicting abstract was not retrieved) |
| 3 | Strict-coverage arms accept nothing | 0 accepts at every k |
| 4 | A3-reassess makes the same decision as A2-pool on every claim | 0 mismatches at every k |
| 5 | Under P1 alone, coverage is `unknown` for every claim; with the audit, `known-incomplete` is a minority | P1 alone: `unknown` for 300/300. Audited: `known-incomplete` for 5 claims (k = 3), 1 (k = 10), 0 (k = 20) |
| 6 | The best coverage arm's U3 is at most the best non-coverage arm's U3 | A3-reassess 175 = A2-pool 175. Bootstrap difference 0, 95% interval [0, 0] |

### Utility U3 (correct − 3·wrong; withhold scores 0), dev, 300 claims

| Arm | Uses coverage | k = 3 | k = 10 | k = 20 |
|---|---|---|---|---|
| A0 default-accept | no | −212 | **−176** | −164 |
| A0-cov (default-accept, accept only if `bounded-complete`) | yes | 48 | 57 | 60 |
| A1 NEI semantics, provenance only | no | 157 | **174** | 181 |
| A2-gate (A1 plus BM25-score gate; τ chosen on train) | no | 157 (τ: none) | 174 (τ: none) | 181 (τ: none) |
| A2-pool (NEI semantics on P1 ∪ P2) | no | 161 | **175** | 181 |
| A3-strict (decide only if `bounded-complete`) | yes | 0 | 0 | 0 |
| A3-reassess (pool when `known-incomplete`) | yes | 161 | **175** | 181 |
| A3-caution (withhold when `known-incomplete`) | yes | 156 | 174 | 181 |
| Ceiling (all 5,183 abstracts, oracle stance) | exhaustive | 188 | 188 | 188 |

U1 and U10 give the same ordering. NEI-semantics arms never make a wrong decision, so their utilities are identical across weights.

Evidence recall@k:

| Retriever | k = 3 | k = 10 | k = 20 |
|---|---|---|---|
| P1 | 0.770 | 0.885 | 0.923 |
| P2 | 0.632 | 0.790 | 0.852 |
| Pool | 0.799 | 0.890 | 0.923 |

## 4. Findings

### F1. The absence fallacy is real and large, and ordinary label semantics removes it completely

Default-accept ("accept unless contrary evidence is retrieved") made 119 wrong accepts at k = 10. NEI semantics made none, and needed no coverage state to do it. NEI semantics is the three-way claim-verification convention: supported / refuted / not-enough-info. It is FEVER's `NotEnoughInfo` (Thorne et al., NAACL 2018), which SciFact inherits.

The gap between A0 and A1 is where the rule "no contrary evidence retrieved ≠ none exists" has decision value, and prior-art label semantics already capture it.

### F2. Categorical coverage is constant under non-exhaustive retrieval

Read strictly, the REC profile never allows `bounded-complete` short of exhaustive assessment. So the coverage of any top-k evidence set was `unknown` for 300/300 claims. As a per-claim decision signal it carries no information.

Gating on it produces one of two degenerate results:

- **Withhold everything:** A3-strict scores 0.
- **Withhold every acceptance:** A0-cov scores 57.

### F3. The only decision gains in coverage arms came from extra evidence, not from the label

A3-reassess improved on A1 by 4 at k = 3 and by 1 at k = 10. In both cases the gain came from the audit's additional retrieval. A2-pool obtains the same evidence without any coverage state, and matched A3-reassess on every claim at every k. That gain is ordinary IR pooling.

### F4. Coverage used as a caution signal only loses decisions

A3-caution withheld decisions that NEI semantics already got right, costing 1 at k = 3. It never prevented a wrong decision, because there were none to prevent.

### F5. Metric gating chose "no gating"

On train, a BM25-score threshold could not remove wrong decisions that did not exist, so τ = none at every k. Provenance plus NEI semantics was already enough.

## 5. Interpretation, under the preregistered rule

Prediction 6 held. **Explicit coverage state added no decision value on homogeneous-polarity evidence.** This is recorded as a narrowing.

| Aspect of coverage | Result | Where it lives instead |
|---|---|---|
| Decision consequence | Already implemented by NEI semantics | FEVER/SciFact label convention |
| Informative per-claim variants | A procedure that retrieves more | IR pooling; recall estimation and stopping rules from technology-assisted review (Cormack & Grossman, SIGIR 2016; Lewis, Yang & Frieder, CIKM 2021) |
| Representation | A scoped measurement | W3C DQV + PROV envelope (GEI REC profile) |

**What survives is not a decision primitive.** It is a rendering and conformance obligation: "no contrary evidence retrieved" must not be stated as "no contrary evidence exists", and a declared envelope (known exclusions) should travel with any claim of completeness. Whether a known gap is material enough to block action is decision sufficiency, which belongs to Telos (audit NB-04).

**GB-03 consequence.** Evolving `derived-evidence-assessment-v0` into a coverage schema is no longer justified.

- Its legacy `coverage_outcome: complete` should be read as `bounded-complete` inside the adversarial fixture's closed world.
- Exports use the REC values (#15).

## 6. H4: conflicting evidence

**Not tested.** SciFact has no mixed-polarity claims.

SciFact-Open (Wadden et al., 2022) pools evidence over 500K abstracts and would contain such cases. Its tarball is 287,369,773 bytes. Its repository states no license for its annotations; the corpus is S2ORC, which is ODC-By. It was **not downloaded**. That needs your decision.

Expectation for H4 if it is ever run: by construction, A3-reassess equals A2-pool. So even with conflicting evidence, the coverage label cannot beat pooling. The CI test demonstrates this on a synthetic mixed claim.

What a conflicting-evidence collection *could* measure is the value of retrieving more and of recall-estimation stopping rules. Both are IR prior art. H4 is therefore low priority for Memory Lab.

## 7. Threats to validity

- **Oracle stance.** A real stance model would add classification errors, which coverage does not address.
- **Limited judged universe.** It covers only cited abstracts. Unjudged relevant abstracts exist in larger corpora.
- **Lexical retrievers only.**
- **One dataset, dev split only (300 claims).** The bootstrap interval is degenerate ([0, 0]) because the two compared arms made identical decisions.
- **Homogeneous polarity.** This limits the test to the absence-fallacy, informativeness, and cost sides.
- **Same author for the protocol and the coverage semantics.** Mitigations: preregistration before any run, disclosure of the zero-mixed structure, and a narrowing-by-default interpretation rule.

# Coverage decision value v0 (SciFact): preregistration

**Status:** preregistered on 2026-09-15, before any retrieval or decision arm was run  
**Issue:** #12  
**Branch / review surface:** `research/gei-backprop-graphiti-v0` (PR #16)

After this file is committed, the retrievers, parameters, arms, endpoints, and interpretation rules below will not change. Any bug fix will be reported alongside the pre-fix result.

## 1. Question

Does an explicit evidence-coverage state change claim-verification decisions beyond what provenance plus retrieval metrics already give? The coverage states are the GEI REC values `not-assessed | unknown | known-incomplete | bounded-complete`.

A negative result counts as a successful narrowing of Memory Lab.

## 2. Data

- **Dataset:** SciFact release (Wadden et al., EMNLP 2020), `https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz`
  - size: 3,115,079 bytes
  - MD5: `cb7da4d8609e30f2c7483b61aa447f7e` (equal to the S3 ETag)
  - SHA-256: `11c621288d41ac144d29b13b0f8503b3820b7d6e8b1f6ff24dff335c196d76be`
- **Licenses, per the upstream `LICENSE.md` in `allenai/scifact`:**
  - claims and evidence annotations: CC BY 4.0;
  - corpus abstracts (S2ORC): ODC-By 1.0.
- **License conflict:** the Hugging Face card for `allenai/scifact` lists `cc-by-nc-2.0`. That conflicts with the upstream license; the upstream license governs.
- **Handling:** the data is not redistributed here. It is gitignored and fetched and verified by `fetch_scifact.py`.
- **Attribution:** David Wadden, Shanchuan Lin, Kyle Lo, Lucy Lu Wang, Madeleine van Zuylen, Arman Cohan, Hannaneh Hajishirzi. *Fact or Fiction: Verifying Scientific Claims.* EMNLP 2020.

## 3. What was examined before registration

Only the label structure was examined, from the claim files and corpus size. No retrieval was run and no decisions were computed.

| Split | Claims | Supported | Contradicted | Mixed | NEI |
|---|---|---|---|---|---|
| train | 809 | 332 | 173 | 0 | 304 |
| dev | 300 | 124 | 64 | 0 | 112 |

- Evidence documents are a subset of cited documents for 809/809 train claims and 300/300 dev claims.
- No document carries both labels for the same claim.
- The corpus has 5,183 abstracts.

### Structural consequence, stated before running

Measured against SciFact's judged universe, a support-required decision can be wrong only when a claim has evidence of both polarities. SciFact has no such claims.

The benefit coverage most needs to show is catching this case: support was retrieved, while contrary evidence exists but was not retrieved. That case **cannot be observed on this dataset.** This preregistration tests what SciFact can test and defers the rest (H4).

## 4. Hypotheses

- **H1, absence fallacy.** Default-accept ("accept unless contrary evidence is retrieved") makes many wrong accepts. Ordinary NEI semantics (support-required, the FEVER/SciFact label convention) removes them without any coverage state.
- **H2, informativeness.** Under non-exhaustive retrieval, the categorical coverage of the considered set is `unknown` for every claim. Per-claim variation appears only as `known-incomplete`, when an additional procedure finds evidence that the primary procedure missed.
- **H3, decision value on homogeneous-polarity evidence.** No coverage arm beats the best non-coverage arm on dev utility.
- **H4, benefit under conflicting evidence.** Not testable here. It requires a collection whose judged universe contains mixed-polarity claims.

## 5. Fixed design

### Evaluation universe and stance

- The evaluation universe is judged SciFact evidence at abstract level.
- The stance of a considered abstract is its gold label for the claim (`SUPPORT` / `CONTRADICT`). Anything else is not-evidence, including unjudged abstracts.
- This oracle stance isolates retrieval coverage from stance-classification error.

### Collection truth and scoring

Collection truth is one of `SUPPORTED`, `CONTRADICTED`, or `NEI`. `MIXED` would be a fourth value, but none is present.

| Decision | Correct when truth is | Wrong when truth is |
|---|---|---|
| ACCEPT | SUPPORTED | CONTRADICTED or NEI |
| REJECT | CONTRADICTED | SUPPORTED or NEI |
| WITHHOLD | neither correct nor wrong | neither correct nor wrong |

### Retrieval (stdlib, deterministic)

- **Tokenizer:** lowercase, split on non-alphanumerics, drop a fixed English stopword list defined in code, no stemming.
- **P1 (primary):** Okapi BM25 over title and abstract, with k1 = 0.9 and b = 0.4.
- **P2 (audit):** TF-IDF cosine at sentence level. The title counts as a sentence, IDF is computed over all corpus sentences, and a document's score is its best sentence score.
- **Cutoff:** k = 10 is primary; k = 3 and k = 20 are sensitivity runs.

### Decision rules

- **D0, default-accept:** REJECT if any considered abstract contradicts the claim; otherwise ACCEPT.
- **D1, NEI semantics:**
  - ACCEPT if support is present and no contradiction is present;
  - REJECT if a contradiction is present and no support is present;
  - otherwise WITHHOLD.

### Coverage state

Coverage uses the GEI REC profile. It applies to a considered set E and is computed only from the procedures a system actually ran.

| State | Condition |
|---|---|
| `bounded-complete` | Every abstract in the declared universe (5,183) was considered and assessed |
| `known-incomplete` | A procedure the system ran surfaced judged evidence that is not in E |
| `unknown` | A procedure ran, but completeness is not demonstrated |
| `not-assessed` | No procedure is recorded |

### Arms

| Arm | Evidence considered | Decision | Uses coverage |
|---|---|---|---|
| A0 | P1@k | D0 | no. Reference arm: absence fallacy |
| A0-cov | P1@k | D0, but ACCEPT only when coverage is `bounded-complete`; otherwise WITHHOLD | yes |
| A1 | P1@k | D1 | no. Provenance only |
| A2-gate | P1@k | D1, but WITHHOLD when the decisive abstract's BM25 score is below τ | no. Provenance plus retrieval metric |
| A2-pool | P1@k ∪ P2@k | D1 | no. Ordinary pooling |
| A3-strict | P1@k | D1, but decide only when coverage is `bounded-complete`; otherwise WITHHOLD | yes |
| A3-reassess | P1@k, or P1@k ∪ P2@k when coverage(P1@k) = `known-incomplete` | D1 | yes |
| A3-caution | P1@k | D1, but WITHHOLD when coverage(P1@k) = `known-incomplete` under the P2 audit | yes |
| Ceiling | all 5,183 abstracts | D1 | exhaustive. Uses the oracle; not a realistic arm |

**How A2-gate's threshold τ is chosen:**
- It is chosen on train to maximize U3.
- The candidates are "no gating" and the train deciles of decisive scores.
- Ties go to the least gating.
- The "decisive abstract" is the highest-ranked considered abstract that carries the label D1 decided on.

### Endpoints

Dev is used for all endpoints. Train is used only to choose τ.

- **Decision counts:** correct ACCEPT, correct REJECT, wrong ACCEPT, wrong REJECT, and WITHHOLD broken down by truth.
- **Utility:** U_w = correct − w·wrong, with WITHHOLD scoring 0, for w ∈ {1, 3, 10}. The primary weight is w = 3.
- **Coverage:** the distribution of coverage states for each arm.
- **Retrieval:** evidence recall@k for P1, P2, and the pool.
- **Uncertainty:** a bootstrap over dev claims (2,000 resamples, seed 12) gives the 95% interval for the U3 difference between the best coverage arm and the best non-coverage arm.

### Predictions

1. D1 arms (A1, A2-\*, A3-\*) make 0 wrong decisions at every k. This follows from MIXED = 0.
2. At k = 10, A0 makes at least 112 wrong accepts: every NEI claim, plus contradicted claims whose contradicting abstract is not retrieved.
3. A0-cov and A3-strict withhold every ACCEPT, because no arm is ever `bounded-complete` at k < 5,183.
4. A3-reassess makes the same decision as A2-pool on every claim.
5. Under P1 alone, coverage is `unknown` for every claim. With the P2 audit, `known-incomplete` occurs for a minority of claims.
6. The best coverage arm's U3 is at most the best non-coverage arm's U3 (H3).

### Interpretation rules

- **If prediction 6 holds:** an explicit coverage state adds no decision value on homogeneous-polarity evidence. Record this as a narrowing. The decision consequence of REC's anti-promotion rule ("no contrary evidence retrieved ≠ none exists") is already implemented by NEI semantics, which is prior art. H4 stays open.
- **If a coverage arm beats every non-coverage arm on U3, with a bootstrap interval that excludes 0:** coverage has decision value here. Report the mechanism.
- **Failed predictions** are reported as observed, not repaired.

## 6. Threats known at registration

- The stance is an oracle, so there is no stance-model error.
- The judged universe is limited to cited abstracts. SciFact-Open (Wadden et al., 2022) found additional evidence in a larger corpus.
- Only lexical retrievers are used.
- The dataset has no conflicting evidence, so H4 is deferred.
- The author of this protocol also wrote Memory Lab's coverage semantics. Mitigations: this registration, the zero-mixed disclosure made before running, and a narrowing-by-default interpretation rule.

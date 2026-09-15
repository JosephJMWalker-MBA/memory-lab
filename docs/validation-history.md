# Validation history

This document records what has actually been demonstrated. Designed-but-untested behavior should not be promoted into this list until exercised.

## Recovered baseline

- Canonical source corpus: 4,488 Markdown files in the validated snapshot.
- Recovered Chroma collection: 302,240 live chunks.
- Chroma FTS: 302,240 live lexical rows.
- Embedding model: `all-MiniLM-L6-v2`, 384 dimensions.
- Vector distance: cosine.

Private source content and local filesystem paths are intentionally omitted from this public repository.

## Public synthetic validation

The environment-independent public fixture in `fixtures/synthetic-lifecycle/`
has been reproduced with:

```bash
python3 tests/run_synthetic_lifecycle.py
```

This public check validates deterministic synthetic snapshot reproduction, exact
ADD / CHANGE / DELETE classification, legacy-v1 chunk ID mechanics,
zero-based heading line handling, Windows-style nested relative source identity,
final source snapshot equality, and final logical chunk-record equality.

The fixture sequence is:

```text
S0 -> ADD -> CHANGE expansion -> CHANGE contraction -> DELETE -> S4
```

`S4` intentionally equals `S0`. This is reproduced with public synthetic
fixture data only. It does not validate the recovered baseline, Chroma
cardinality, HNSW cosine retrieval, SQLite FTS, embedding vectors, or the
pending full 302,240-record logical equivalence audit.

## Public synthetic state-machine validation

The environment-independent failure-semantics runner has been reproduced with:

```bash
python3 tests/run_failure_semantics.py
```

This is synthetic state-machine validation only. It demonstrates fail-closed
handling for unexpected pre-existing ADD records, missing CHANGE sources,
already-absent DELETE sources, snapshot mismatch, pending transaction barriers,
foreign ownership collisions, and tampered state/ledger/record disagreement.

It also demonstrates replay idempotence as an explicit no-op only when the
committed transition and resulting state can be verified, CHANGE interruption
semantics that preserve desired evidence before stale cleanup, DELETE
interruption detection through a surviving pending journal, and chained ledger
identity for repeated `A -> B -> A -> B` source edges.

This is reproduced with public synthetic fixture logic. It is not recovered
baseline integration validation and does not validate Chroma, HNSW, FTS,
embeddings, or the pending 302,240-record equivalence audit.

## Public contract schema validation

The environment-independent public contract schemas have been reproduced with:

```bash
python3 tests/run_contract_schema_validation.py
```

This validates structurally correct synthetic source snapshot, source delta,
mutation plan, index state, pending transaction, and ledger-entry artifacts. It
also demonstrates schema rejection for missing identity/provenance fields,
malformed mutation types, incomplete pending transactions, ledger entries
missing chain identity, invalid snapshot identifiers, and unexpected additional
fields.

This is public research contract validation. It is pending Magician comparison
and is not a claim that the schemas reproduce undocumented recovered
implementation file formats.

## Experimental public derived-memory v0

The environment-independent derived-memory semantics experiment has been
reproduced with:

```bash
python3 tests/run_derived_memory_v0.py
```

This synthetic experiment begins after evidence normalization. It demonstrates:

- stable fact corroboration without minting a duplicate semantic record;
- temporal state supersession that preserves the earlier state;
- unresolved contradictory evidence rather than arbitrary overwrite;
- explicit correction that supersedes interpretation without rewriting source;
- temporal relationship change;
- a backward attribution check that rejects the unsupported claim
  `status = cancelled` when the attributed evidence only supports
  `status = slowed`, then verifies the narrower revision;
- schema rejection for malformed derived records;
- unchanged canonical synthetic evidence across derived-memory operations.

The test also makes an executable distinction among **evidence changed**,
**world state changed**, and **interpretation changed**.

This is experimental public research semantics only. It does not validate LLM
extraction, automatic evidence normalization, private-corpus behavior,
retrieval-to-attribution selection, confidence calibration, production storage,
or recursive multi-hop derived reasoning.

## Adversarial public derived-memory semantics

The follow-on adversarial experiment runs with:

```bash
python3 tests/run_derived_memory_adversarial.py
```

It tests four failure modes not covered by v0:

- a locally supported claim can still be downgraded when relevant contrary
  evidence was omitted, and unknown evidence coverage yields provisional rather
  than global support;
- semantically load-bearing qualifiers cannot be dropped without revision;
- multi-hop derived records retain direct derived dependencies, an explicit
  derivation rule, and canonical evidence closure, while cyclic support is
  rejected;
- valid time in the modeled world is distinct from the snapshot in which the
  system first learned or reassessed a claim.

This is synthetic public research only. Closed-world evidence completeness is
available only inside the adversarial fixture and is not claimed for real
retrieval. The experiment does not validate automatic contrary-evidence
discovery, real retrieval coverage, source-authority ranking, LLM extraction,
or production recursive reasoning.

## Dependency-aware derived reassessment v0

The synthetic reassessment experiment runs with:

```bash
python3 tests/run_derived_reassessment_v0.py
```

It demonstrates that a changed supporting record can produce a deterministic,
minimal reverse-dependency reassessment plan. Direct dependents are distinguished
from transitive dependents and evaluated parent-before-child.

The synthetic chain replaces `Module Sigma status = blocked` with
`status = clear`. The prior Vega and Helios blocked derivations lose their
required support and become historical-only in the newer current view. No
opposite `status = clear` records are invented for Vega or Helios.

Historical derived records remain byte-for-byte unchanged. Reassessment plans
and results are separate append-only artifacts.

This experiment does not yet model multiple independent justifications for the
same semantic record, general rule engines, automatic trigger discovery from
real source/index deltas, or persistent dependency indexes at corpus scale.

## Multiple independent justifications v0

The alternative-support experiment runs with:

```bash
python3 tests/run_multiple_justifications_v0.py
```

It demonstrates an OR-of-AND support model for one semantic derived record.
Antecedents inside one justification are jointly required, while independent
justifications are alternatives.

The synthetic Aurora record is initially supported through both Sigma and Tau.
When Sigma becomes clear, Aurora is correctly marked as affected but remains
active through the independent Tau justification. Only when Tau also becomes
clear does Aurora lose its final support path and become historical-only.

The semantic Aurora record keeps the same identity across support-path changes.
The historical record and justification-set artifact remain unchanged, and loss
of all blocked justifications does not invent `Aurora status = clear`.

This is synthetic public research only. It does not implement ATMS
minimal-environment subsumption, inconsistent/nogood environments, defaults,
probabilistic support weights, or corpus-scale support indexing.

## Derived conflict and consistency v0

The supported-conflict experiment runs with:

```bash
python3 tests/run_derived_conflict_v0.py
```

It separates individual evidentiary support from cross-record consistency. In the
synthetic Polaris case, `status = blocked` and `status = ready` are each
individually support-verified, but an explicit single-value status constraint in
matching scope and overlapping valid time makes them jointly inconsistent.

The consistency layer preserves both historical records and withholds an
arbitrary winner from the current view. Different values on the multi-valued
`depends_on` relation remain compatible because no exclusivity constraint
applies.

When the blocked derivation later loses support, the conflict resolves by support
change and the surviving ready record may return to the current view.

This experiment does not validate source-authority adjudication, probabilistic
conflict resolution, automatic predicate-constraint discovery, complex temporal
constraint logic, or private-corpus conflict handling.

## Graphiti substitution v0 (external runtime, synthetic)

The Memory-Lab-owned adapter and conformance checks run with:

```bash
python3 tests/run_graphiti_adapter_v0.py
```

This demonstrates the following without Graphiti installed:

- the Polaris translation is deterministic;
- a read-only admission projection over Graphiti-shaped edge state reproduces the native conflict lane's assessments byte-for-byte;
- the ML-EP-0 checks detect four failure modes:
  - recency collapse;
  - unconstrained invalidation;
  - deletion-as-withdrawal;
  - dangling provenance;
- every conformance verdict and admission recorded in the live evidence file can be recomputed from the recorded states.

The live run executed `graphiti-core==0.30.2` on embedded Kuzu 0.11.3 at Memory Lab commit `c3d12d7`:

```bash
python experiments/graphiti-conflict-v0/run_graphiti_live.py
```

It exercised Graphiti's own code across ten scenarios:

- persistence;
- `resolve_extracted_edge`: the fast path, verdict handling, attribute handling, and temporal resolution;
- `Graphiti.remove_episode`.

Contradiction verdicts were scripted. No LLM, embedder, search, or production backend was used. See `graphiti-substitution-v0.md`.

This is executed external-runtime evidence over one synthetic fixture. It does not validate:

- real LLM contradiction behavior;
- Graphiti search;
- Neo4j or FalkorDB persistence;
- real-corpus behavior.

## Current-view admission vs application-state baseline v0

The comparison runs with:

```bash
python3 tests/run_appstate_baseline_v0.py
```

It rebuilds the reassessment, multiple-justification, and conflict lanes' artifacts with the existing lane code. It then compares them with three sqlite3 designs that import no Memory Lab semantics:

- **B1:** recorded conclusions;
- **B2:** recompute-on-read;
- **B0:** naive mutable state.

What it demonstrates:

- B1 reproduces every Memory Lab current-view outcome, and also expresses scoped dispositions and policy versions.
- B2 rewrites history when a derivation rule changes.
- B0 invents negations, erases the conflict, and keeps no history.
- The reassessment results' mapping onto CVD values round-trips without loss.

These are synthetic comparisons over hand-designed fixtures. They do not validate real application code, concurrent writers, valid-time intervals on derived facts, or concurrent contradictory base evidence. See `appstate-baseline-v0.md`.

## Coverage decision value v0 (SciFact, preregistered)

The protocol is `experiments/coverage-scifact-v0/PREREGISTRATION.md`, committed before any arm ran. The run and its verification:

```bash
python3 experiments/coverage-scifact-v0/fetch_scifact.py
```

```bash
python3 experiments/coverage-scifact-v0/run_coverage_scifact.py
```

```bash
python3 tests/run_coverage_scifact_v0.py
```

The run was executed on the SciFact dev split (300 claims) at commit `5e4ae07` on a clean tree. It used oracle abstract-level stance, stdlib BM25, and a sentence-level TF-IDF audit, with k ∈ {3, 10, 20}. All six preregistered predictions held:

- Default-accept made 119 wrong accepts at k = 10; NEI semantics made none.
- Categorical coverage was `unknown` for every claim under non-exhaustive retrieval.
- The reassess-on-`known-incomplete` arm matched plain pooling on every claim.
- The metric gate chose no threshold at every k.

CI recomputes every recorded aggregate, threshold, prediction, and bootstrap interval from the recorded per-claim rankings and labels.

Limits of this evidence:

- It covers one judged collection whose judged universe contains no mixed-polarity claims.
- The stance is an oracle, and retrieval is lexical only.
- It does not test conflicting evidence, a real stance model, or neural retrieval.

## Legacy compatibility audit

Six structurally different source documents were regenerated under the WSL query-encoder runtime and compared with their records in the recovered baseline.

Aggregate result:

- sources: 6
- chunks compared: 2,756
- missing IDs: 0
- unexpected IDs: 0
- metadata mismatches: 0
- text mismatches: 0

The audit covered small and very large sources, including one source with more than 1,700 chunks. This validated against recovered baseline compatibility of chunk IDs, boundaries, documents, headings, folders, tags, categories, auto-tags, and zero-based start-line metadata for the tested sample.

## Deterministic source snapshots

A source snapshot was generated twice from the same corpus and reproduced the same snapshot identity. A disposable corpus with one synthetic source produced an exact delta:

- added: 1
- changed: 0
- deleted: 0
- unchanged: 4,488

Deleting that synthetic source later returned the corpus to the exact original source snapshot identity, demonstrating deterministic round-trip identity for the test.

## Incremental ADD

A production-compatible synthetic source was chunked using the frozen legacy identity scheme and incrementally added to a clean clone of the recovered baseline.

Validated against recovered baseline:

- collection count: 302,240 -> 302,241;
- record readback by ID;
- 384-dimensional embedding readback;
- FTS count: 302,241;
- FTS ID presence;
- exact-vector HNSW self-query rank: 1;
- fail-closed preflight against a deliberately contaminated test index.

## Replay idempotence

The committed ADD transition was replayed after state/ledger bootstrap. The state-aware preflight matched the exact committed transition, verified resulting source IDs and documents, and returned an explicit `ALREADY_COMMITTED_NOOP` rather than treating the existing source as drift.

## Incremental CHANGE: expansion

The synthetic source was changed from one desired chunk to two.

Validated against recovered baseline:

- existing legacy chunk ID updated in place by upsert;
- second legacy chunk inserted in the same source transition;
- count: 302,241 -> 302,242;
- FTS count synchronized to 302,242;
- both desired vectors returned rank 1 on exact-vector query;
- state and ledger advanced only after verification.

## Incremental CHANGE: contraction / stale deletion

The synthetic source was changed from two desired chunks back to one.

Validated against recovered baseline:

- desired replacement upserted first;
- replacement verified before destructive cleanup;
- one stale chunk deleted afterward;
- count: 302,242 -> 302,241;
- FTS count synchronized to 302,241;
- surviving desired vector returned rank 1;
- state and ledger advanced after final verification.

## Incremental DELETE

The synthetic source was removed from the source corpus and the resulting deletion plan targeted exactly one current indexed record.

Validated against recovered baseline:

- delete preflight matched state snapshot and current index count;
- pending transaction journal created before deletion;
- exactly one source ID deleted;
- count: 302,241 -> 302,240;
- FTS count: 302,240;
- deleted ID absent from FTS afterward;
- ledger entry chained to the preceding transition;
- source snapshot returned to the exact original snapshot identity.

## Full round-trip audit

A full logical equivalence audit was started between the untouched recovered baseline and the round-tripped incremental test index. The first interactive run was interrupted by an SSH connection reset after more than 50,000 records. The audit itself was read-only; the validated index state was not mutated. Long-running reruns are intended to execute detached from SSH.

**Status:** pending final complete result. Do not yet claim full 302,240-record logical equivalence until the detached audit finishes successfully.

## Implementation categories

- `validated against recovered baseline`: exercised against the private recovered
  Chroma/FTS/vector index or its recovered source snapshot.
- `reproduced with public synthetic fixture`: exercised by the public fixture and
  environment-independent runner.
- `pending exact validated-script migration`: validated local scripts that must
  be imported from exact files rather than recreated from documentation.
- `experimental public research semantics`: executable synthetic behavior that
  tests a research model without claiming production or private-corpus validity,
  currently including derived memory v0, its adversarial v0.1 refinement, dependency-aware reassessment v0, multiple independent justifications v0, and derived conflict/consistency v0.
- `executed external-runtime substitution (synthetic)`: a published runtime's
  own code exercised against a Memory Lab fixture, with any substituted
  participant (for example scripted LLM verdicts) declared; currently Graphiti
  substitution v0.
- `designed but unimplemented`: architectural direction that is not yet
  executable behavior, including LLM extraction, automatic evidence
  normalization, real retrieval-coverage estimation, automatic contrary-evidence
  discovery, and production multi-hop reasoning.

## Retrieval findings retained from earlier experiments

- Vector retrieval is strong for named projects, technical concepts, and semantic paraphrases.
- Literal / lexical retrieval provides complementary recall, especially for exact phrases and opaque identifiers.
- Equal chunk-level fusion can over-weight multiple weak chunks from one source.
- Source-level aggregation can recover agreement that is invisible at exact chunk level.
- Cross-encoder reranking can rescue some lexical candidates but can degrade already-solved easy cases; it should not be treated as a universal final ranker.
- Temporal, causal, and autobiographical relationships often require derived relational memory rather than expecting conventional chunk retrieval to reconstruct them reliably.

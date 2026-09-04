# Derived memory v0

Derived memory v0 is an experimental public research lane for testing how
interpretations can remain accountable to evidence over time. It is not a
production memory engine, an extraction pipeline, or a claim that model output
is truth.

The core boundary is:

    canonical evidence
      -> normalized evidence assertion
      -> proposed derived record
      -> backward attribution check
      -> verified / unresolved / rejected
      -> later evidence
      -> corroboration / temporal supersession / correction / revision

Canonical source remains unchanged throughout this process. A retrieval index
may help locate evidence later, but neither retrieval ranking nor a derived
record becomes the archive.

## What v0 starts after

This experiment deliberately starts after evidence normalization. Each synthetic
evidence item includes both invented human-readable text and a normalized
assertion containing a record type, subject, predicate, and object.

That means v0 does not test whether an LLM can extract the assertion correctly.
It tests what should happen once a candidate proposition and its evidence refs
exist.

This boundary keeps the first experiment falsifiable. Extraction can be added
later as a separate layer without confusing extraction quality with memory
semantics.

## Experimental record contract

`schemas/derived-memory-record-v0.schema.json` is an experimental/public
research contract. It is reproduced only by the synthetic derived-memory test.
It is not a recovered Magician format and is not production-ready.

A v0 record requires:

- stable record identity;
- record type;
- subject / predicate / object;
- evidence references;
- source snapshot identity;
- lifecycle status;
- change classification;
- an explicit attribution-check result.

Optional links preserve relationships among interpretations:

- `supersedes` / `superseded_by`;
- `contradicts`;
- `qualifies`;
- `revision_of`;
- temporal scope for state-like records.

v0 intentionally omits scalar confidence. A numeric confidence field would add
precision before the project has demonstrated a meaningful calibration method.
The experiment instead records the outcome and reason of the attribution check.

## Lifecycle vocabulary

The smallest useful status vocabulary found for this experiment is:

- `proposed` — candidate interpretation awaiting support check;
- `verified` — attributed normalized evidence supports the proposition as
  written;
- `rejected` — the attributed evidence does not justify the proposition;
- `unresolved` — attributed evidence supports incompatible interpretations and
  no resolution rule is justified;
- `superseded` — the record remains historically inspectable but a later record
  replaces it for a later world state or corrected interpretation.

`superseded` does not by itself mean the older record was false. The reason for
supersession matters.

## Three different kinds of change

Derived memory must not collapse all change into one operation.

### Evidence changed

New evidence can support the same proposition. In the stable-fact case, a later
source corroborates the same owner relationship. The derived record retains its
semantic identity and accumulates an additional evidence reference.

### World state changed

A proposition can be correct at one time and different later. Project Atlas is
synthetically active in one snapshot and paused in a later snapshot. The active
record is preserved and temporally closed; the paused record supersedes it as a
new world state.

The same rule is exercised with an evolving partnership relationship.

### Interpretation changed

The world need not have changed. An earlier interpretation may simply have been
wrong or too strong.

The fixture exercises two forms:

1. explicit correction — later evidence states that an earlier material claim
   was incorrect;
2. backward-check revision — the same evidence that says testing "slowed" does
   not justify the derived claim "cancelled".

Both cases change interpretation without rewriting the evidence that produced
the earlier interpretation.

## Backward attribution check

The backward check is not neural-network backpropagation and does not modify
model weights.

It is a provenance check from conclusion back to evidence:

1. take the proposed derived record;
2. resolve every attributed evidence reference;
3. inspect normalized assertions relevant to the same subject and predicate;
4. ask whether the evidence supports the object as written;
5. detect explicit correction, conflicting values, or overreach;
6. verify, reject, leave unresolved, or propose a narrower revision;
7. never alter canonical evidence as part of that correction.

The synthetic Kepler case is intentionally simple:

    Evidence: Project Kepler prototype testing slowed this week.
    Proposed: Project Kepler status = cancelled.
    Backward check: REVISE — "cancelled" overreaches the evidence.
    Revised: Project Kepler status = slowed.

The rejected record remains inspectable and the revised record points back to it
with `revision_of`.

## Contradiction

The synthetic Harbor case contains two pieces of evidence in the same snapshot
with incompatible launch dates. v0 does not choose one merely because a record
was proposed first.

Both candidate records become `unresolved` and explicitly point to each other
through `contradicts`.

A later research pass may add source authority, recency, directness, or explicit
resolution evidence. v0 does not invent those rules prematurely.

## Temporal supersession

State and relationship records receive temporal scope. When later evidence
supports a new state:

- the earlier record becomes `superseded` but remains inspectable;
- its temporal end is set to the later record's start snapshot;
- the later record links back with `supersedes`;
- the later record is classified as `world_state_changed`.

This keeps "the world changed" distinct from "the earlier interpretation was
wrong."

## Synthetic cases

`tests/run_derived_memory_v0.py` exercises:

- stable fact accumulation without duplicate semantic identity;
- temporal state transition;
- unresolved contradiction;
- explicit correction;
- evolving relationship;
- unsupported inference rejection and same-evidence revision;
- schema rejection for malformed derived records;
- canonical synthetic evidence remaining unchanged during all derived-memory
  operations.

The test uses only `fixtures/derived-memory-v0/evidence.json`.

## What this demonstrates

The public synthetic experiment demonstrates that the proposed semantics are
internally executable without allowing derived interpretation to overwrite its
evidence.

It demonstrates a concrete distinction among evidence change, world-state
change, and interpretation change. It also demonstrates that a backward support
check can reject an over-broad proposition while preserving both the evidence
and the rejected interpretation.

## What remains unimplemented

v0 does not validate or implement:

- LLM extraction;
- automatic evidence normalization;
- retrieval-to-attribution selection;
- vector or lexical retrieval integration;
- private corpus behavior;
- probabilistic confidence calibration;
- source-authority ranking;
- automatic contradiction resolution;
- graph storage;
- production persistence;
- APIs or user interfaces;
- recursive multi-hop derived reasoning.

The project should add those only when a concrete experiment requires them.

## Research direction

The next useful questions are not "how many more fields can a memory record
have?" They are questions that can falsify the semantics:

- Can a derived record cite sufficient evidence but still be misleading because
  a relevant contrary source was not retrieved?
- How should an attribution check represent partial support or necessary
  qualifiers without turning every record into free-form prose?
- When does a relationship change count as a new world state versus a corrected
  historical interpretation?
- How should multi-hop derivations carry provenance so a backward check can
  traverse derived records back to canonical evidence?
- Can a later pass re-evaluate earlier records under a newer snapshot without
  silently rewriting what the earlier snapshot justified?

Those questions belong after the v0 semantics remain stable under more
adversarial synthetic cases.


## Adversarial follow-on

The questions listed above are exercised in the follow-on adversarial lane rather
than being silently folded back into v0. See:

- `docs/derived-memory-adversarial.md`;
- `schemas/derived-memory-record-v0.1.schema.json`;
- `schemas/derived-evidence-assessment-v0.schema.json`;
- `tests/run_derived_memory_adversarial.py`.

v0 remains the first executable semantics baseline. v0.1 records the contract
changes forced by adversarial cases rather than rewriting what v0 originally
demonstrated.

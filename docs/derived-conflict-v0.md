# Derived conflict and consistency v0

This experiment separates two questions that earlier derived-memory passes could
still blur:

1. **Is this individual record supported by its provenance?**
2. **Can this record coexist consistently with other supported records?**

A record may answer yes to the first question and no to the second.

## Why support is not consistency

At the synthetic Polaris snapshot, two derived records are each supported:

    Project Polaris status = blocked

and:

    Project Polaris status = ready

The blocked status follows from a blocked dependency. The ready status follows
from passed checks plus granted release approval.

Neither justification is fabricated, incomplete inside the closed synthetic
fixture, or automatically weaker than the other.

The correct response is therefore not to erase one record or arbitrarily choose
a winner.

Both historical derived records remain support-verified. A separate consistency
assessment determines whether either may appear as authoritative in the current
view.

## Conflict requires a constraint

Different object values are not automatically contradictory.

For example:

    Polaris depends_on Sigma
    Polaris depends_on Tau

are both legitimate because `depends_on` is naturally multi-valued.

Conflict detection therefore requires an explicit predicate constraint.

The experimental `derived-predicate-constraint-v0` contract can declare that a
predicate is:

- single-valued within an exact qualifier scope; or
- multi-valued.

It also states whether valid-time overlap is required before values are treated
as incompatible.

The synthetic `status` constraint is:

    one value per exact subject/scope during overlapping valid time

Only under that declared rule do `blocked` and `ready` conflict.

## Scope and time matter

Two values should not be treated as the same proposition merely because their
subject and predicate match.

The conflict check therefore considers:

- record type;
- subject;
- predicate;
- exact qualifiers;
- different values;
- valid-time overlap when required by the constraint.

This preserves the earlier lesson that qualifiers and temporal scope are part of
meaning, not explanatory decorations.

## Unresolved supported conflict

At `SYN-DM-0400`:

- blocked is individually support-verified;
- ready is individually support-verified;
- both have matching production scope and overlapping valid time;
- the status predicate is explicitly single-valued.

The consistency result is:

    unresolved_conflict

and the current-view action is:

    withhold_conflicting_supported

No record is automatically selected.

This is different from changing either historical record's support status to
`unresolved`. Their provenance can remain valid while their joint consistency
is unresolved.

## Resolution by support change

At `SYN-DM-0401`, new evidence says Sigma is clear.

That removes the active support path for the historical Polaris-blocked
derivation. The Polaris-ready derivation remains supported.

The consistency layer can now return:

    resolved_by_support_change

and admit the surviving supported record to the current view.

This is resolution by changed support, not by hidden source ranking, confidence
guessing, or destructive rewriting.

## Contracts

### `derived-predicate-constraint-v0`

Declares the semantic condition under which different values are incompatible.

### `derived-consistency-assessment-v0`

Records separately:

- all candidate record IDs;
- which candidates remain support-valid;
- which candidates do not;
- the consistency outcome;
- the current-view outcome;
- which supported records, if any, are admitted.

The separation is deliberate:

    support validity != consistency validity

## What the synthetic test demonstrates

`tests/run_derived_conflict_v0.py` demonstrates:

- two incompatible derived records can both remain individually support-verified;
- an explicit single-value predicate constraint detects their incompatibility;
- the current view withholds conflicting supported records instead of choosing a
  winner;
- two different `depends_on` values remain compatible without an exclusivity
  constraint;
- a conflict can resolve when one proposition loses support;
- historical records remain unchanged across consistency assessment;
- malformed constraints and consistency assessments fail schema validation.

## Relationship to truth maintenance

Truth-maintenance systems explicitly track inconsistency rather than assuming
that every supported proposition can coexist.

Memory Lab keeps the same discipline while separating three layers:

1. provenance/support of each record;
2. semantic constraints among records;
3. current-view admission.

That separation makes conflict visible without turning contradiction into source
rewriting.

## Still unresolved

This experiment does not implement:

- source-authority adjudication;
- probabilistic conflict resolution;
- partial qualifier compatibility;
- complex temporal overlap policies;
- automatically learned predicate constraints;
- logical constraints involving more than one predicate;
- private-corpus conflict handling.

A future resolution layer should only choose among conflicting supported records
when an explicit, inspectable rule justifies doing so.

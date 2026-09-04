# Derived reassessment v0

Derived reassessment v0 is an experimental dependency-aware re-evaluation layer
for derived memory.

Its purpose is to answer:

> When support changes, which prior derived conclusions must be checked again?

The experiment is synthetic and environment-independent. It does not implement
a production rule engine or private-corpus graph.

## Why reassessment is separate from record mutation

Historical derived records describe what a named evidence state justified at the
time. Reassessment therefore does not rewrite them.

Instead, Memory Lab appends reassessment results that describe whether a prior
record remains active in the newer current view.

This preserves two different questions:

- What did the system previously conclude from the earlier evidence state?
- Should that conclusion still participate in the current view after new
  evidence arrived?

## Dependency closure

Each derived record may depend directly on earlier derived records.

When one supporting record changes, the reassessment planner builds the reverse
dependency closure:

    changed support
        -> direct dependent
        -> transitive dependent
        -> ...

Only records in that closure need reassessment. Unrelated records remain
untouched.

The synthetic chain is:

    Sigma blocked
        -> Vega blocked
        -> Helios blocked

with separate unchanged relationship evidence:

    Vega depends_on Sigma
    Helios depends_on Vega

When new evidence replaces `Sigma blocked` with `Sigma clear`, the plan
contains:

1. the triggering Sigma record;
2. Vega as directly affected;
3. Helios as transitively affected.

The dependency relationship records are unaffected.

## Parent-before-child order

Reassessment follows support dependencies in topological order. A support
provider is evaluated before any conclusion that depends on it.

For the synthetic case:

    Sigma blocked
    Vega blocked
    Helios blocked

This prevents a child from being evaluated against a stale interpretation of its
parent.

The v0 planner is deliberately narrow and assumes the already-validated
dependency graph is acyclic. The adversarial v0.1 lane separately rejects
derivation cycles.

## Withdrawal is not negation

This is a central rule.

When Sigma is no longer blocked, the justification for deriving Vega as blocked
disappears. That means the old Vega-blocked record becomes historical-only in
the current view.

It does **not** mean:

    Vega status = clear

The same applies to Helios.

Support withdrawal removes a conclusion from the active projection; it does not
prove the logical opposite unless independent evidence or a rule supports that
opposite proposition.

## Reassessment contracts

### `derived-reassessment-plan-v0`

The plan records:

- source snapshot transition;
- triggering record IDs;
- directly affected records;
- transitively affected records;
- deterministic evaluation order;
- unaffected records.

The same graph and trigger set reproduce the same plan identity.

### `derived-reassessment-result-v0`

Each reassessed historical record receives an append-only result containing:

- the plan;
- assessed snapshot;
- prior record status;
- support outcome;
- resulting current-view state;
- triggering records;
- replacement records when one actually exists.

Current-view outcomes are separate from historical record status.

## Synthetic outcomes

The test demonstrates:

- targeted dependency-closure reassessment instead of global recomputation;
- deterministic reassessment-plan replay;
- parent-before-child evaluation;
- direct and transitive support withdrawal;
- replacement of the direct Sigma support record;
- no invented opposite state for Vega or Helios;
- byte-for-byte preservation of historical derived records;
- schema rejection for malformed plans and results.

## Relationship to truth maintenance

This pass is intentionally close to the classical truth-maintenance idea of
retaining reasons for beliefs and revising belief status when dependencies
change.

Memory Lab keeps one additional hard boundary: canonical source and historical
derived records remain immutable evidence/history. Reassessment changes the
newer projection of which derived records are active, not the older record
itself.

## Relationship to the user's backward-check concept

There are now two complementary directions:

- **backward attribution check**: start from a conclusion and trace backward to
  ask whether its evidence actually supports it;
- **dependency-aware reassessment**: when support changes, propagate the need for
  checking forward through conclusions that depend on it.

Together they form an incremental correction loop without neural-network weight
updates.

## Unresolved research

v0 intentionally leaves these open:

- multiple independent justifications for one semantic record;
- alternative support paths where one justification disappears but another
  remains;
- general rule representation and validation;
- automatic trigger discovery from source/index deltas;
- efficient persistent dependency indexes at large scale;
- scheduling/reassessment when many changes arrive together;
- how probabilistic or authority-weighted evidence affects support withdrawal.

The next strong adversarial case is multiple justifications. A truth-maintenance
system should not withdraw a conclusion merely because one support path failed
if another valid independent justification remains.

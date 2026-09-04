# Multiple independent justifications v0

This experiment refines derived reassessment so one semantic record can have
multiple independent reasons for remaining in the current view.

The problem is simple:

> If one support path fails, should the derived conclusion disappear?

Not necessarily.

## OR-of-AND support

The experiment follows the structure used by assumption-based truth maintenance
systems:

- antecedents **inside one justification** are conjunctive;
- multiple justifications for the same conclusion are alternatives.

For the synthetic Aurora case:

    J1:
      Aurora depends_on Sigma
      AND Sigma status = blocked

    J2:
      Aurora depends_on Tau
      AND Tau status = blocked

    Aurora status = blocked
      IF J1 OR J2

This is materially different from flattening all four parent records into one
conjunctive dependency list.

## Why v0.1 needed another contract refinement

\`derived-memory-record-v0.1\` records direct derived ancestry but its executable
recursive support check treats those direct parents conjunctively.

That is sufficient for one derivation path but wrong once a proposition has
independent alternative explanations.

\`derived-memory-record-v0.2\` therefore separates:

- \`derived_from_records\` — immediate provenance ancestry across all support paths;
- \`support_semantics\` — whether support is direct, conjunctive, or represented by
  alternative justifications;
- \`justification_set_id\` — an explicit support structure when alternatives
  exist.

The semantic record does not change identity merely because its active support
path changes.

## Justification-set contract

\`derived-justification-set-v0\` records a set of justifications for one derived
record.

Each justification contains:

- a stable justification ID;
- the derivation rule;
- the derived antecedent record IDs that are all required for that path;
- the canonical evidence leaves associated with that path.

The set semantics are fixed to:

    any_satisfied_justification_supports_record

This is deliberately narrower than a general propositional reasoner. It is the
smallest executable structure needed to falsify the single-support-path model.

## Justification assessment

\`derived-justification-assessment-v0\` records which support paths are active or
inactive at a named snapshot.

At \`SYN-DM-0300\`:

- J1 active;
- J2 active;
- Aurora blocked remains active.

At \`SYN-DM-0301\`:

- Sigma becomes clear;
- J1 inactive;
- J2 still active;
- Aurora blocked remains active.

At \`SYN-DM-0302\`:

- Tau also becomes clear;
- J1 inactive;
- J2 inactive;
- Aurora blocked becomes historical-only.

No transition creates \`Aurora status = clear\`. Loss of all blocked
justifications is still not proof of the opposite state.

## Affected is not invalid

Dependency closure still has value.

When Sigma changes, Aurora is correctly included in the reassessment plan because
one of its possible support paths depends on Sigma.

But inclusion in the plan means only:

> reassess this record

It does not mean:

> withdraw this record

The justification assessment decides the latter.

This cleanly separates:

1. **change propagation** — which conclusions might be affected;
2. **support evaluation** — whether enough independent support remains.

## Stable semantic identity

The Aurora blocked record keeps the same \`record_id\` across both support
transitions.

That means the identity of a proposition is not the identity of its current
justification environment.

Justification state can change while the semantic record remains the same
historical proposition.

## Prior-art alignment

Johan de Kleer's assumption-based truth maintenance system represents nodes with
sets of supporting environments and keeps multiple alternatives simultaneously.
A justification is a Horn-style implication whose antecedents are jointly
required, while a node can have multiple supporting environments.

Memory Lab is not implementing a full ATMS. It inherits the specific discipline
needed here:

- keep independent support paths explicit;
- do not retract a conclusion merely because one path disappears;
- distinguish proposition identity from support-environment identity.

See \`docs/derived-memory-prior-art.md\`.

## What the test demonstrates

\`tests/run_multiple_justifications_v0.py\` demonstrates:

- two independent justification paths can support one semantic record;
- the reassessment planner marks a record affected when either path changes;
- failure of one justification retains the record when another remains active;
- failure of the final justification withdraws the record from the current view;
- semantic record identity remains stable across support changes;
- the historical record and justification-set artifact remain unchanged;
- support withdrawal does not infer the opposite proposition;
- malformed v0.2 records, justification sets, and assessments fail schema
  validation.

## Still unresolved

This pass does not implement:

- ATMS minimal-environment subsumption;
- inconsistent/nogood environments;
- defaults or nonmonotonic justifications;
- source-authority or probabilistic support weights;
- deduplication of semantically equivalent justification paths;
- persistent support indexes at corpus scale;
- private-corpus reasoning.

The next useful pressure test is likely **contradictory independent
justifications**: what happens when one valid environment supports a proposition
and another valid environment supports an incompatible proposition, especially
when neither environment can be dismissed as incomplete?


## Conflict follow-on

The next pressure test is implemented in `docs/derived-conflict-v0.md`.

That pass keeps justification validity separate from consistency validity: two
records may each retain valid support while an explicit semantic constraint
prevents both from being admitted to the current view simultaneously.

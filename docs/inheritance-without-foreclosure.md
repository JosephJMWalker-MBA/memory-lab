# Inheritance Without Foreclosure

**Status:** research hypothesis / design principle under empirical test  
**Scope:** long-horizon memory and reassessment

Memory systems should preserve prior attempts, failures, rejections, and deferrals without allowing those historical conclusions to become unconditional permanent vetoes.

The core distinction is:

```text
blindly repeat a known failure
!=
revisit an old approach because the conditions that produced the failure changed
```

## Problem

A system with weak memory can waste effort by rediscovering failures that are already well understood.

A system with strong undifferentiated memory can fail in the opposite direction: an old conclusion can be inherited as if it were timeless even after tools, dependencies, architecture, requirements, evidence, or governing assumptions change.

The goal is therefore not maximum forgetting or maximum recall.

The goal is **conditional inheritance**.

## Minimum historical record

A useful retained failure / rejection / deferral should preserve more than a verdict.

At minimum, preserve:

```text
proposition / approach considered
observed outcome
failure mechanism or governing reason
relevant assumptions
relevant environment / versions / dependencies
scope
confidence in the diagnosis
conditions under which the conclusion should be reconsidered
```

A record that stores only:

```text
"this failed"
```

is epistemically weaker than one that stores:

```text
"this failed under conditions X because mechanism Y was observed;
reconsider if X materially changes or Y no longer applies"
```

## Reopening test

When inherited history is relevant to a current problem:

1. identify the proposition or approach previously rejected / failed / deferred;
2. identify the failure mechanism or governing reason actually observed;
3. identify the environmental and architectural assumptions that made that reason binding;
4. compare those assumptions with current conditions;
5. preserve the old conclusion as binding only to the extent its causal basis still applies;
6. if a material condition changed, permit a bounded re-test;
7. preserve the result of the re-test and whether the old failure mechanism remained active.

## Important non-equivalences

```text
remembered
!= currently admitted

previously rejected
!= permanently prohibited

reopened
!= accepted

changed environment
!= old conclusion invalid

failed support
!= opposite proposition proven
```

Reopening is permission to test again, not evidence that the earlier conclusion was wrong.

## What counts as productive reopening

A reopening is productive when:

- at least one material condition genuinely changed;
- the old failure mechanism may therefore no longer bind;
- the test is bounded and independently evaluable;
- the system reports that it is revisiting inherited history rather than pretending the idea is novel;
- negative re-test results are retained.

It is not productive merely because an agent generates a different implementation of an unchanged known failure.

## What counts as correct non-reopening

A strong memory system must also know when history should remain binding.

If the causal reason for rejection still applies, declining to retry is not foreclosure. It is appropriate inheritance.

This means the research target needs both:

```text
sensitivity
= reopen when changed causal conditions justify it

specificity
= retain the historical rejection when its causal basis still holds
```

A memory system optimized only for reopening would be as defective as one optimized only for avoidance.

## Relationship to truth maintenance

Truth-maintenance systems already address changing support for beliefs.

Inheritance without foreclosure asks a related but different engineering question about **historical problem-solving conclusions**:

> When should a system treat an earlier negative result as still governing a present attempt?

The answer depends not only on whether the conclusion was recorded, but on whether the causal conditions behind it remain true.

This may ultimately be representable using ordinary provenance, temporal state, TMS/ATMS support, and structured application metadata. Memory Lab does not assume a bespoke runtime is required.

## Relationship to current-view disposition

Historical failure records remain preserved regardless of current disposition.

A later system may treat an inherited conclusion as:

```text
currently binding
eligible for bounded reopening
superseded by changed conditions
unresolved
```

Those current-view decisions should not rewrite the historical record.

## Empirical status

This principle is not yet established by Memory Lab's synthetic tests.

It should be tested against real software-development and research tasks where:

- a prior failure / rejection / deferral is preserved;
- the original causal reason can be reconstructed;
- at least one material condition may have changed;
- task success is independently evaluable;
- simpler baselines are allowed to win.

Evidence against the hypothesis includes:

- full historical memory performs equally well without an explicit reopening procedure;
- ordinary current-context reasoning reliably rediscovers the relevant conditionality;
- reopening mostly repeats known failures;
- historical causes cannot be represented precisely enough to guide later decisions;
- the structured reopening procedure adds prompt/attention advantages rather than a genuine memory-governance advantage.

The principle survives only if conditional inheritance improves long-horizon work under controlled or sufficiently strong naturalistic evidence.

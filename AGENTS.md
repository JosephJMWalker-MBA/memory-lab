# Memory Lab Agent Guidance

Read this before adding architecture, schemas, storage, retrieval machinery, or memory semantics.

## Current phase

Memory Lab is in **prior-art integration + semantic hardening**.

The repository already contains useful engineering and synthetic semantics, but it is not committed to becoming a standalone production memory runtime.

Start with:

1. `STATUS.md`
2. `README.md`
3. `docs/research-position.md`
4. `docs/architecture.md`
5. `docs/derived-memory-prior-art.md`
6. the specific experiment / schema relevant to the task

For long-horizon historical reopening work, also read:

`docs/inheritance-without-foreclosure.md`

## Primary rule

Do not confuse the research problem with an implementation.

```text
research question
!= semantic contract
!= conformance test
!= adapter
!= runtime
!= retrieval index
```

A mature external system may be the correct implementation substrate.

## Prior-art-first requirement

Before inventing a new memory primitive, graph layer, truth-maintenance engine, temporal model, or provenance object, check whether the responsibility is already substantially covered by:

- classical TMS;
- ATMS;
- belief-revision literature;
- W3C PROV;
- nanopublications / Whyis;
- temporal / bitemporal databases and knowledge graphs;
- event sourcing;
- Graphiti / Zep;
- ordinary relational application state;
- lexical / vector / graph retrieval composition.

Prefer reuse, profiling, adapters, and conformance tests over bespoke machinery.

## No novelty theater

Do not claim novelty for:

- retaining reasons for beliefs;
- dependency-aware reassessment;
- alternative support environments;
- bitemporal facts;
- provenance-bearing assertions;
- revision lineage;
- event-sourced historical state;
- temporal knowledge graphs;
- hybrid semantic / lexical retrieval.

Those have substantial prior art.

If Memory Lab remains useful, it must do so because a measurable boundary or composition problem remains unsolved or insufficiently explicit.

## Current high-value distinctions

Pressure these rather than expanding generic memory infrastructure:

```text
local support
!= evidence coverage

support validity
!= consistency validity

historical status
!= current-view admission

withdrawal
!= negation

world change
!= interpretation correction

preserved history
!= permanent veto
```

## Evidence coverage discipline

Do not use provenance as a substitute for coverage.

A complete record of which evidence supported a proposition does not prove that the relevant evidence universe was adequately searched.

Keep separate:

```text
support from cited evidence
coverage of relevant evidence
```

Do not claim bounded completeness without a defensible envelope.

In open-world settings, `unknown` may be the correct answer.

## Historical-memory discipline

Prior failures and rejections are evidence, not timeless vetoes.

When an old conclusion is relevant, preserve:

- what was attempted;
- what failed / was rejected / deferred;
- the observed mechanism or governing reason;
- assumptions and environment;
- conditions under which reopening would be justified.

Do not reopen merely for novelty.
Do not refuse reopening merely because history contains a rejection.

## Experimental discipline

Synthetic fixtures prove only the semantics exercised by those fixtures.

Keep separate:

```text
schema-valid
!= synthetic experiment passes
!= existing runtime conforms
!= real corpus works
!= production behavior
!= research claim established
```

When comparing an existing runtime, allow it to win.

If ordinary application state or a mature framework preserves the required property more simply, record that as a successful narrowing of Memory Lab.

## Runtime discipline

Do not make Chroma, HNSW, Whyis, Graphiti, SQLite, RDF, or any other runtime part of Memory Lab's identity unless evidence justifies that dependency.

The current Chroma/HNSW work is a validated engineering track and useful lineage, not a constitutional commitment.

## Relationship to GIE / GEI

Do not assume GIE/GEI must deploy this repository directly.

Memory Lab may contribute:

- semantic distinctions;
- schemas;
- conformance fixtures;
- experimental evidence;
- adapters;
- governance rules;

while another system supplies runtime machinery.

That is a valid success state.

## Change rule

Before adding a new semantic object or runtime component, answer:

1. What exact failure requires this addition?
2. What established system already addresses the same failure?
3. Why is reuse / adaptation insufficient?
4. What observable behavior would falsify the need for this addition?
5. Can the research question be tested without owning the runtime?

If those questions cannot be answered, do not expand the architecture yet.

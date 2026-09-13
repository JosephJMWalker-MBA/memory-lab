# Derived-memory prior art notes

**Status:** current prior-art pressure map  
**Purpose:** constrain Memory Lab toward reuse, narrower claims, and testable distinctions

This note records established ideas that constrain Memory Lab's derived-memory research.

The goal is convergence where prior work already has the right abstraction, not novelty for its own sake.

## Bottom line

Large parts of Memory Lab are established prior art by design.

The project should not claim novelty for:

- reasons / justifications for beliefs;
- dependency-aware reassessment;
- multiple alternative support environments;
- inconsistent environments;
- provenance-bearing assertions;
- bitemporal facts;
- event-sourced historical state;
- revision lineage;
- temporal knowledge graphs;
- hybrid semantic / lexical / graph retrieval.

The strongest surviving research question is narrower:

> Does the explicit separation among local support, evidence coverage, consistency, historical record, current-view admission, and open-world uncertainty define a useful contract that is not already available end-to-end — and can that contract be implemented mostly by composing established systems?

That question permits a strong outcome in which Memory Lab becomes primarily a semantic contract, conformance suite, and adapter research program rather than a standalone memory runtime.

## W3C PROV

W3C PROV separates entities, activities, agents, derivations, revisions, attribution, and provenance bundles.

Two points are especially relevant:

- a derived entity can carry a chain back to entities used in its production;
- revision is a specialized form of derivation rather than silent replacement.

Memory Lab should therefore keep direct derived-record dependencies explicit and retain canonical evidence leaves so a recursive provenance walk can terminate at source evidence.

References:
- https://www.w3.org/TR/prov-dm/
- https://www.w3.org/TR/prov-o/

## Truth-maintenance systems

Jon Doyle's Truth Maintenance System work records the reasons for beliefs and uses those dependencies when contradictions require belief revision.

That is very close to Memory Lab's backward attribution and dependency-aware reassessment work.

Memory Lab therefore should describe those mechanisms as applications / refinements of truth-maintenance discipline, not as a new class of reasoning.

The useful inheritance is:

- retain reasons;
- retain dependency structure;
- use dependency changes to trigger reassessment;
- support explanations from retained justifications.

Reference:
- Jon Doyle, "A truth maintenance system", Artificial Intelligence 12(3), 1979. DOI: 10.1016/0004-3702(79)90008-0

## Assumption-based truth maintenance

Johan de Kleer's Assumption-Based Truth Maintenance System (ATMS) directly constrains Memory Lab's multiple-justification model.

The central support algebra is already established:

```text
antecedents inside one justification = AND
independent justification environments = OR
```

Consequences for Memory Lab:

- losing one environment must not retract a proposition while another valid environment survives;
- proposition identity must remain distinct from support-environment identity;
- inconsistent environments can be represented rather than erased;
- broad general nonmonotonic reasoning should not be rebuilt casually.

Memory Lab does not currently need to reproduce a full ATMS. Minimal-environment subsumption, nogoods, defaults, and general nonmonotonic reasoning remain out of scope unless concrete experiments require them.

References:
- Johan de Kleer, "An assumption-based TMS", Artificial Intelligence 28(2), 1986. DOI: 10.1016/0004-3702(86)90080-9
- Johan de Kleer, "Extending the ATMS", Artificial Intelligence 28(2), 1986. DOI: 10.1016/0004-3702(86)90081-0
- Johan de Kleer, "Problem solving with the ATMS", Artificial Intelligence 28(2), 1986. DOI: 10.1016/0004-3702(86)90082-2

## Belief revision

AGM and later belief-revision work distinguish operations such as expansion, contraction, and revision.

A particularly important distinction for Memory Lab is between:

```text
world changed
!=
our interpretation changed
```

A system should not treat both as one generic supersession event.

Memory Lab should inherit the discipline of explicit change semantics rather than claim that distinction as unique.

Reference:
- Stanford Encyclopedia of Philosophy, "Logic of Belief Revision"

## Nanopublications

Nanopublications separate an assertion from its provenance and publication information.

This reinforces Memory Lab's decision not to collapse proposition, evidence, and lifecycle metadata into one undifferentiated record.

Reference:
- https://nanopub.net/

## Whyis

Whyis is a particularly strong pressure target because it combines several capabilities that Memory Lab should not rebuild without reason:

- nanopublications as provenance-bearing knowledge units;
- assertion separated from provenance and publication information;
- direct user, ingestion, statistical, and inference contributions;
- human curation / approval workflows;
- explicit revision and retirement;
- archival access to historical nanopublications;
- provenance-based justification;
- generalized truth maintenance through derivation links;
- transitive retirement / recomputation when supporting knowledge is revised;
- RDF / OWL / SPARQL / W3C PROV-compatible machinery.

This substantially overlaps Memory Lab's reassessment and historical-preservation goals.

### Consequence

Before inventing another provenance-bearing derived-record runtime, test whether Memory Lab's surviving semantics can be represented as a profile / adapter / conformance layer over Whyis-like machinery.

References:
- https://github.com/tetherless-world/whyis
- https://whyis.readthedocs.io/
- Jamie McCusker et al., "Whyis 2: An Open Source Framework for Knowledge Graph Development and Research," The Semantic Web, 2023. DOI: 10.1007/978-3-031-33455-9_32

## Temporal and bitemporal knowledge

Temporal knowledge systems treat facts as time-qualified rather than timeless triples.

Bitemporal models distinguish:

- **valid time** — when the proposition holds in the modeled world;
- **transaction / knowledge time** — when the system recorded or knew it.

Memory Lab's earlier snapshot-based temporal scope mixed these concerns. The adversarial lane correctly separates them.

This distinction is established prior art and should remain an inherited constraint rather than a novelty claim.

References:
- Yuchao Zhang et al., "A survey on temporal knowledge graph embedding: Models and applications", Knowledge-Based Systems 304 (2024), 112454
- "Time-Aware Probabilistic Knowledge Graphs", TIME 2019
- "Time Travel with the BiTemporal RDF Model", Mathematics 13(13), 2025

## Event sourcing

Event sourcing preserves state-changing events so prior states can be reconstructed rather than overwritten.

Memory Lab already applies a similar discipline to source/index mutation and derived interpretation:

```text
current view
=
projection over retained history
```

This is established engineering precedent, not a Memory Lab invention.

Reference:
- https://martinfowler.com/eaaDev/EventSourcing.html

## Graphiti / Zep

Graphiti / Zep places substantial implementation pressure on Memory Lab's temporal-graph and retrieval ambitions.

Graphiti models:

- raw episodes as source context;
- entities and derived facts / relationships;
- source links from facts back to episodes;
- created / expired time;
- valid / invalid time;
- incremental graph construction;
- contradiction / invalidation behavior;
- hybrid semantic, lexical, and graph retrieval.

### What this may replace

Graphiti-like machinery is a serious candidate substrate for:

- temporal fact graphs;
- source episode linkage;
- historical fact retention;
- incremental integration;
- graph retrieval;
- semantic + lexical retrieval composition.

Memory Lab should not build those capabilities from scratch merely to own them.

### Where Memory Lab still asks a different question

Graph construction and fact invalidation do not by themselves establish:

```text
local support
!= evidence coverage
```

Nor do they necessarily require:

```text
individually support-valid conflicting claims
→ both histories preserved
→ neither silently promoted to authoritative current view
```

Those are candidate contract-level distinctions to test rather than assumed differentiation.

References:
- https://github.com/getzep/graphiti
- Zep: A Temporal Knowledge Graph Architecture for Agent Memory, arXiv:2501.13956

## Whyis + Graphiti + TMS/ATMS as a substitute architecture

A plausible substitute architecture covers a large fraction of the current problem:

```text
Whyis / nanopublications
    assertion + provenance + attribution
    curation / publication state
    revisions and archive
    inference provenance / truth maintenance

Graphiti / Zep
    temporal entity/fact graph
    source episodes
    valid / invalid time
    incremental graph construction
    hybrid retrieval

TMS / ATMS discipline
    reasons and dependencies
    multiple justifications
    inconsistent environments
```

### Falsification hypothesis

> If Memory Lab's remaining distinctions can be represented cleanly as a small contract over these or similarly mature systems, Memory Lab should not build a standalone general memory runtime.

That would be a successful narrowing of custom infrastructure, not a failure of the research.

## Strongest surviving distinction: support is not coverage

The most important current distinction is:

```text
local support
!= evidence coverage
```

A cited evidence set can genuinely support a proposition while omitting relevant contrary evidence.

Memory Lab therefore treats evidence coverage as a separate assessment dimension.

Useful coverage states may include:

```text
bounded-complete
known-incomplete
unknown
not-assessed
```

A locally supported proposition with unknown coverage should not silently become globally verified.

### Why prior art does not automatically collapse this distinction

TMS asks whether a belief follows from its reasons.

That does not automatically ask whether the system considered the right universe of reasons.

Graph provenance can show which source episodes produced a fact without proving that relevant contrary episodes were searched or available.

Nanopublication derivation can preserve all inputs used by an inference without proving that omitted relevant knowledge was considered.

This is therefore partly a retrieval-age completeness problem:

> a valid inference from selected premises can still mislead when material premises were absent from consideration.

This distinction still needs targeted comparison with information-retrieval recall, database completeness statements, open-world reasoning, defeasible argumentation, provenance semirings, and evidence-completeness research before any novelty claim is justified.

## Support validity != consistency validity

Another useful separation is:

```text
record A has adequate support
record B has adequate support
!=
A and B can jointly occupy one current view
```

ATMS already provides substantial conceptual ancestry here.

Memory Lab's remaining task is to determine whether making this separation explicit at the application/conformance layer improves real auditability and correction.

## Historical record != current-view admission

Memory Lab preserves what a named evidence / reasoning state justified historically.

A later projection may admit, withhold, reject, or supersede that record without rewriting it.

This resembles event sourcing, curation state, and truth-maintenance projections.

The research question is whether the explicit boundary is useful enough to standardize / test independently of a particular runtime.

## Inheritance without foreclosure

A newer research pressure concerns historical negative conclusions.

A memory system should preserve prior failure, rejection, and deferral history without automatically converting those conclusions into permanent vetoes.

This requires preserving the causal basis of the old conclusion — not merely the verdict — so a later system can check whether the relevant conditions still hold.

See `inheritance-without-foreclosure.md`.

This principle is currently a hypothesis. Existing provenance, temporal, truth-maintenance, and workflow systems may already be sufficient to represent it. Memory Lab should test that before adding bespoke machinery.

## Consequence for future experiments

The next important experiments should not ask:

> How many more fields should a Memory Lab record contain?

They should ask:

1. Can an existing runtime or composition satisfy Memory Lab's surviving semantic boundaries without custom core machinery?
2. Does explicit evidence-coverage state improve decisions over provenance + retrieval metrics alone?
3. Does separate current-view admission improve correction / auditability over ordinary application state?
4. Can inheritance-without-foreclosure improve long-horizon problem solving over both fresh-context and full-history baselines?
5. Do these effects survive real corpora and non-hand-designed tasks?

## Current posture

Prior art is not a threat to Memory Lab.

It is a design constraint and an implementation gift.

The strongest version of Memory Lab should reuse mature machinery, preserve only the distinctions that survive falsification, and remain willing to become smaller as the evidence improves.

# Derived-memory prior art notes

This note records established ideas that constrain Memory Lab's derived-memory
research. The goal is convergence where prior work already has the right
abstraction, not novelty for its own sake.

## W3C PROV

W3C PROV separates entities, activities, agents, derivations, revisions,
attribution, and provenance bundles. Two points are especially relevant:

- a derived entity can carry a chain back to entities used in its production;
- revision is a specialized form of derivation rather than silent replacement.

Memory Lab should therefore keep direct derived-record dependencies explicit and
retain canonical evidence leaves so a recursive provenance walk can terminate at
source evidence.

References:
- https://www.w3.org/TR/prov-dm/
- https://www.w3.org/TR/prov-o/

## Truth-maintenance systems

Jon Doyle's Truth Maintenance System work records the reasons for beliefs and
uses those dependencies when contradictions require belief revision. That is
very close to the purpose of Memory Lab's backward attribution check.

Memory Lab differs in scope: canonical source evidence remains immutable, while
derived interpretations may be rejected, revised, or superseded. The useful
inheritance is the discipline of retaining justifications/dependencies rather
than treating the current belief set as self-justifying.

Reference:
- Jon Doyle, "A truth maintenance system", Artificial Intelligence 12(3), 1979.
  DOI: 10.1016/0004-3702(79)90008-0

## Assumption-based truth maintenance

Johan de Kleer's Assumption-Based Truth Maintenance System (ATMS) extends truth
maintenance by tracking alternative supporting environments for a node. A
justification has conjunctive antecedents, while a node can remain supported by
multiple alternative environments.

That distinction directly constrains Memory Lab's multiple-justification model:

- antecedents inside one justification are AND;
- independent justification environments are OR;
- losing one environment must not retract a derived record while another valid
  environment survives;
- proposition identity must remain distinct from support-environment identity.

Memory Lab is not attempting to reproduce a full ATMS. The v0 experiment adopts
only this support-structure discipline and leaves minimal-environment
subsumption, nogood environments, defaults, and general nonmonotonic reasoning
out of scope.

### Inconsistent environments

ATMS work also treats inconsistency as something to represent and manage across
supporting environments rather than as a reason to erase whichever supported
node arrived second. That constrains Memory Lab's consistency layer: support for
an individual record and compatibility among multiple supported records are
separate questions.

Memory Lab's first conflict experiment uses explicit predicate constraints
rather than implementing full ATMS nogood propagation. The narrower requirement
is that two support-valid records may be withheld together when an inspectable
constraint establishes that they cannot both hold in the same scope/time.

References:
- Johan de Kleer, "An assumption-based TMS", Artificial Intelligence 28(2),
  1986. DOI: 10.1016/0004-3702(86)90080-9.
- Johan de Kleer, "Extending the ATMS", Artificial Intelligence 28(2), 1986.
  DOI: 10.1016/0004-3702(86)90081-0.

## Nanopublications

Nanopublications separate an assertion from its provenance and publication
information. This reinforces Memory Lab's decision not to collapse proposition,
evidence, and lifecycle metadata into one undifferentiated text blob.

Reference:
- https://nanopub.net/

## Temporal and bitemporal knowledge

Temporal knowledge-graph work treats facts as time-qualified rather than
timeless triples. Bitemporal models go further by distinguishing:

- **valid time** — when the proposition is true in the modeled world;
- **transaction / knowledge time** — when the knowledge system recorded or knew
  the proposition.

Memory Lab's earlier snapshot-based temporal scope mixed these concerns. The
adversarial v0.1 experiment therefore separates valid time from knowledge time.

References:
- Yuchao Zhang et al., "A survey on temporal knowledge graph embedding: Models
  and applications", Knowledge-Based Systems 304 (2024), 112454.
- "Time-Aware Probabilistic Knowledge Graphs", TIME 2019.
- "Time Travel with the BiTemporal RDF Model", Mathematics 13(13), 2025.

## Event sourcing

Event sourcing preserves the sequence of state-changing events so prior states
can be reconstructed rather than overwritten. Memory Lab already applies a
similar principle to source/index mutation and should carry the same historical
discipline into derived interpretation: current view is a projection over
retained history, not the only retained state.

Reference:
- https://martinfowler.com/eaaDev/EventSourcing.html

## Consequence for the next experiment

The most important weakness in derived-memory v0 is not record shape. It is
**evidence-set completeness**.

A backward attribution check can correctly conclude that cited evidence supports
a claim while still being misleading if relevant contrary evidence was omitted.
The next experiment therefore separates:

1. local support: do the cited items support the proposition?
2. evidence coverage: did the evaluation consider the relevant evidence set?
3. overall assessment: may the record be treated as verified, only provisionally
   supported, unresolved, revised, or rejected?

In a real open corpus, completeness may often be unknown. The synthetic harness
uses a closed-world fixture only to prove that omission is detectable when a
complete relevant set is actually knowable. It must not generalize that
closed-world property to real retrieval.

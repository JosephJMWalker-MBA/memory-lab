# Adversarial derived-memory semantics

This pass attacks four weaknesses in derived-memory v0:

1. cited support can be correct while relevant contrary evidence was omitted;
2. qualifiers can carry essential scope that disappears in a flattened triple;
3. multi-hop derivations need explicit dependency rules and recursive provenance;
4. snapshot chronology is not the same thing as world-valid time.

The implementation remains synthetic public research. It does not make claims
about real retrieval completeness or private-corpus behavior.

## Support is not evidence coverage

A backward attribution check answers a local question:

> Do the evidence items attributed to this record support the proposition?

That is necessary but insufficient. A second question is:

> Did the evaluation consider the relevant evidence set?

The new `derived-evidence-assessment-v0` contract keeps these dimensions
separate.

Possible evidence-coverage outcomes are:

- `complete` — completeness is demonstrated inside a bounded scope;
- `incomplete` — known relevant evidence was omitted;
- `unknown` — no defensible completeness claim is available.

A locally supported record with unknown coverage becomes
`provisionally_supported`, not globally verified by the assessment.

The synthetic Orion fixture uses a closed world only so omission can be detected
deterministically. That property must not be generalized to open retrieval.

## Qualifiers are part of the proposition

The Meridian fixture says access is approved **for an internal pilot in
staging**. The flattened proposition:

    Project Meridian access = approved

is materially broader.

v0.1 therefore adds a `qualifiers` object to derived records. If the normalized
evidence requires qualifiers and the candidate omits or changes them, the
backward check returns `qualifier_loss` and requires revision.

This is deliberately stricter than treating qualifiers as explanatory metadata.
They participate in semantic identity.

## Recursive provenance

W3C PROV and truth-maintenance systems both reinforce the need to preserve
dependency chains rather than only final conclusions.

v0.1 records:

- direct canonical `evidence_refs`;
- direct `derived_from_records`;
- an explicit `derivation_rule`.

The synthetic Vega case uses a deliberately simple deterministic rule:

    Vega depends_on Sigma
    Sigma status = blocked
    ----------------------
    Vega status = blocked

The child record must retain the canonical evidence closure of its parents, and
a recursive provenance walk must terminate at canonical evidence. Cyclic derived
support is rejected.

This is not a general reasoning engine. The narrow rule exists only to make the
provenance semantics executable.

## Valid time vs knowledge time

Temporal knowledge and bitemporal database work distinguish two questions:

- **valid time** — when was the proposition true in the modeled world?
- **knowledge time** — when did this system first know or reassess it?

The Nova case demonstrates why the distinction matters. The system initially
records Nova as active. At a later snapshot it receives a correction stating
that Nova has actually been paused since an earlier calendar date.

The corrected state therefore has:

- a valid-time start earlier than the snapshot in which the system learned it;
- a knowledge-time start at the later snapshot.

The history can answer both:

- "What do we now believe was true on January 20?"
- "What did the system believe before the later correction arrived?"

## Contract refinement

`derived-memory-record-v0.1.schema.json` is an adversarial refinement, not a
replacement claim for production.

Compared with v0 it adds:

- semantically load-bearing qualifiers;
- explicit direct derived dependencies;
- explicit derivation rule;
- separate valid time;
- separate knowledge time;
- attribution checks that can report qualifier loss, recursive support, and
  retroactive correction.

`derived-evidence-assessment-v0.schema.json` is separate because evidence-set
coverage is not a property of the proposition itself.

## Prior-art alignment

The design intentionally converges with established ideas rather than renaming
them:

- W3C PROV: derivation/revision/provenance chains;
- truth-maintenance systems: reasons for beliefs and dependency-aware revision;
- nanopublications: separation of assertion and provenance;
- temporal/bitemporal knowledge: valid time distinct from system knowledge time;
- event sourcing: retained historical changes rather than current-state-only
  overwrite.

See `docs/derived-memory-prior-art.md`.

## What the adversarial test demonstrates

`tests/run_derived_memory_adversarial.py` demonstrates:

- local support can be downgraded when contrary relevant evidence was omitted;
- unknown coverage yields provisional support rather than an unjustified
  completeness claim;
- complete coverage can expose unresolved contradiction;
- qualifier loss forces revision;
- multi-hop derived support retains canonical evidence closure;
- cyclic derived provenance is rejected;
- valid time and knowledge time remain distinct;
- malformed v0.1 records/assessments fail schema validation.

## Still unresolved

This pass does not solve:

- how a real retrieval system proves or estimates evidence coverage;
- how to discover relevant contrary evidence automatically;
- how source authority should affect contradictory evidence;
- how probabilistic confidence should be calibrated;
- how general multi-hop reasoning rules are represented or validated;
- how derived-memory re-evaluation should scale over a large evolving corpus.

Those are research questions, not hidden implementation details.

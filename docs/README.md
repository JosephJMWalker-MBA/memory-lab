# Memory Lab Documentation Map

Memory Lab contains two related but different bodies of work:

1. validated engineering around source snapshots and incremental retrieval maintenance;
2. experimental semantics for governed derived memory and epistemic continuity.

Do not treat success in one track as proof of the other.

## Start here

1. `../STATUS.md` — current state and immediate research direction
2. `../README.md` — project identity
3. `research-position.md` — implementation-independent research thesis
4. `architecture.md` — current architecture and validated tracks
5. `derived-memory-prior-art.md` — prior-art pressure and substitution map
6. `inheritance-without-foreclosure.md` — historical-memory reopening hypothesis

## Engineering / retrieval track

- `incremental-ingestion.md`
- `state-machine-contracts.md`
- `reproducibility.md`
- `validation-history.md`
- `script-migration-status.json`

These documents preserve substantial validated work on a recovered legacy-compatible Chroma/HNSW environment.

They are important engineering lineage, but do not define the only acceptable future runtime.

## Derived-memory research track

Read roughly in this sequence:

1. `derived-memory-v0.md`
2. `derived-memory-adversarial.md`
3. `derived-reassessment-v0.md`
4. `multiple-justifications-v0.md`
5. `derived-conflict-v0.md`
6. `derived-memory-prior-art.md`

This sequence shows how synthetic adversarial cases forced the semantics to become more precise.

Do not infer:

```text
later document
=
production architecture
```

These are research contracts and experiments unless explicitly promoted by later evidence.

## Security boundary

- `security-and-data-boundaries.md`

The public repository must not receive private archives, transcripts, embeddings, local index stores, or private derived-memory records.

## Evidence ladder

Keep these distinct:

```text
documented design
!= schema exists
!= synthetic fixture passes
!= validated local engineering behavior
!= external runtime conforms
!= real corpus succeeds
!= production behavior
!= general research claim established
```

`validation-history.md` contains engineering evidence for the retrieval track.
The derived-memory documents state what their synthetic fixtures actually demonstrate.

## Current research rule

> Reuse established machinery aggressively. Keep only the semantic distinctions that survive comparison and experiment.

Memory Lab succeeds if it discovers the smallest defensible governed-memory contract, even if another runtime implements it.

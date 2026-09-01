# Security and data boundaries

This repository is public. Treat that as a hard design constraint.

## Never commit

- private chat or note archives;
- exported account data;
- source manifests containing private filenames when those filenames reveal personal information;
- Chroma databases or HNSW files built from private source;
- embeddings generated from private source;
- local index-state or transaction-ledger files from a private deployment;
- derived-memory records based on private source;
- benchmark outputs containing verbatim private source text;
- API keys, tokens, credentials, hostnames, private IPs, usernames, or machine-specific secrets.

## Safe to commit

- reusable scripts that accept paths as arguments rather than hard-coding private paths;
- schemas and contracts;
- sanitized synthetic fixtures;
- aggregate validation counts;
- architecture documentation;
- examples that use invented source names and markers;
- test expectations that contain no private content.

## Local/private deployment layout

A deployment may keep private material adjacent to a clone of this repository, but those directories should remain ignored. Suggested separation:

```text
memory-lab/              # public/reusable code
private-source/          # never commit
indexes/                 # never commit
snapshots/               # private deployment artifacts
benchmarks/private/      # private evaluation material
runtime/                  # state, ledger, pending journal, logs
```

## Provenance policy

The public repository may document that a validation occurred and report sanitized aggregate results. It should not publish evidence excerpts from private source merely to make the validation more reproducible. Reproducibility should instead come from synthetic fixtures that exercise the same behavior.

## Fail-closed publication rule

When in doubt about whether an artifact contains source-derived content, keep it local until it has been reviewed and sanitized. The cost of omitting an artifact from the public repository is lower than the cost of accidentally publishing private memory data.

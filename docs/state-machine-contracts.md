# Public state-machine contracts

Memory Lab's public contracts describe accountability objects for source and
index mutation. They do not replace the frozen `legacy-chunk-contract-v1`, and
they do not claim to reproduce undocumented Magician file formats until the
exact validated implementations are available for comparison.

The accountable flow is:

```text
canonical evidence
  -> source snapshot
  -> source delta
  -> mutation plan
  -> index state
  -> pending transaction
  -> committed ledger entry
```

Canonical evidence remains the source of record. Snapshots identify source
states. Deltas describe source-level differences. Mutation plans describe the
intended transition. Index state records what snapshot the retrieval projection
claims to represent. Pending transactions make interrupted destructive work
detectable. Ledger entries record committed transitions and chain each commit to
the previous transaction identity.

This supports accountable mutation without allowing the retrieval index to
become canonical truth. An index can claim a snapshot, but that claim must be
checked against state, plans, ledger entries, pending journals, and logical
records before mutation proceeds.

## Schema status

| Schema | Status |
| --- | --- |
| `source-snapshot-contract-v1.schema.json` | proposed/public research contract; reproduced by public synthetic harness; pending Magician comparison |
| `source-delta-contract-v1.schema.json` | proposed/public research contract; reproduced by public synthetic harness; pending Magician comparison |
| `mutation-plan-contract-v1.schema.json` | proposed/public research contract; reproduced by public synthetic harness; pending Magician comparison |
| `index-state-contract-v1.schema.json` | proposed/public research contract; reproduced by public synthetic harness; pending Magician comparison |
| `pending-transaction-contract-v1.schema.json` | proposed/public research contract; reproduced by public synthetic harness; pending Magician comparison |
| `ledger-entry-contract-v1.schema.json` | proposed/public research contract; reproduced by public synthetic harness; pending Magician comparison |

None of these new schemas is marked as validated against recovered
implementation formats. The only recovered historical compatibility contract in
this repository remains `legacy-chunk-contract-v1`.

## Additional fields

The public state-machine schemas reject unexpected additional fields. This is a
publication-boundary choice: new provenance or runtime fields should be added by
versioning the contract or explicitly updating the schema, not by silently
normalizing unknown material.

## Schema validity and transition validity

Schema validity is not transition validity. JSON Schema can check object shape,
required identity fields, identifier syntax, mutation-type spelling, and whether
chain identity is present. It cannot prove that a transition is safe to apply.

Semantic checks remain in the Python state-machine tests. Examples:

- a structurally valid mutation plan is still invalid if its `from_snapshot`
  does not match current index state;
- an index state is invalid for mutation if `current_count` disagrees with
  current logical records;
- replay is an explicit no-op only when the committed ledger entry and resulting
  state can be verified;
- CHANGE must materialize desired records before stale records are deleted;
- DELETE must persist a pending transaction before destructive removal begins.

## Out of scope

These contracts do not implement derived memory. Future derived-memory contracts
should remain separate from both `legacy-chunk-contract-v1` and the public
state-machine contracts.

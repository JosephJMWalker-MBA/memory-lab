# Derived conflict v0 fixture

This fictional fixture tests the difference between **support validity** and
**consistency validity**.

At `SYN-DM-0400`, two independently supported derived records exist:

- `Project Polaris status = blocked`
  - derived from Polaris depending on blocked Module Sigma;
- `Project Polaris status = ready`
  - derived from passed release checks plus granted release approval.

Both use the same `environment = production` qualifier and overlapping valid
time.

An explicit predicate constraint declares `status` single-valued per exact
scope during overlapping valid time. Therefore the two individually supported
records form an unresolved conflict. Neither wins automatically.

The fixture also contains two `depends_on` relationships with different
objects. No exclusivity constraint is defined for `depends_on`, so those
records are compatible rather than contradictory.

At `SYN-DM-0401`, Sigma becomes clear. The blocked derivation loses support
while the ready derivation remains supported. The conflict can then resolve by
support change without ranking sources or rewriting either historical record.

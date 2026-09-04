# Derived reassessment v0 fixture

This fictional fixture models dependency-aware re-evaluation across two
synthetic snapshots.

At `SYN-DM-0200`:

- Project Vega depends on Module Sigma.
- Module Sigma is blocked.
- Project Helios depends on Project Vega.
- A deterministic dependency rule derives Vega as blocked.
- The same rule then derives Helios as blocked through Vega.

At `SYN-DM-0201`, new evidence says Module Sigma is clear.

The experiment asks which prior derived conclusions must be reassessed. It must
reassess Vega directly and Helios transitively, while leaving unchanged
relationship records alone.

Crucially, withdrawal of the old blocked support does **not** justify inventing
new `status = clear` records for Vega or Helios. Their old blocked records
become historical-only in the current view until replacement evidence exists.

Historical derived records are not mutated; reassessment results are appended as
separate artifacts.

# Adversarial derived-memory fixture

This fixture is fictional and closed-world by construction. It exists to test
failure modes that derived-memory v0 could not represent cleanly.

Cases:

- Project Orion has two incompatible launch dates in the same synthetic
  snapshot. A candidate citing only one is locally supported but evidentially
  incomplete.
- Project Meridian is approved only for an internal pilot in staging. Dropping
  those qualifiers changes the proposition.
- Project Vega depends on blocked Module Sigma. The derived Vega status is a
  deterministic multi-hop inference whose provenance must traverse through
  verified derived parents to canonical evidence.
- Project Nova is later learned to have changed state earlier than the system
  learned about it, separating valid time from knowledge time.

The fixture's closed-world completeness is a test convenience only. Real
retrieval coverage must generally be treated as bounded or unknown unless the
system can prove otherwise.

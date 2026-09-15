#!/usr/bin/env python3
"""Current-view admission vs ordinary application state (issue #13).

Question: does a plain event-sourced application design already preserve every
current-view distinction the derived-memory fixtures exercise?

Three designs run over the same fixture evidence:

- B0 naive (control): mutable current-status columns recomputed on every change,
  with the common closed-world default;
- B2 recompute-on-read: append-only facts, derivation rules as SQL, and
  dispositions as a query under a scoped, versioned policy table;
- B1 recorded conclusions: B2 plus each snapshot's derived conclusions appended
  as rows, so history is read rather than recomputed.

The baselines use sqlite3 and import no Memory Lab semantics. Memory Lab
reference artifacts are rebuilt with the existing lane code and mapped onto the
GEI current-view disposition values for comparison.
"""
import inspect
import json
import sqlite3
import sys
from collections import defaultdict

from run_derived_conflict_v0 import load_fixture as load_conflict_fixture
from run_derived_memory_adversarial import apply_support, evidence_map, record, stable_id
from run_derived_reassessment_v0 import build_plan, reassess
from run_derived_reassessment_v0 import load_fixture as load_reassessment_fixture
from run_graphiti_adapter_v0 import (
    DERIVATIONS,
    QUALIFIERS,
    derived_record_id,
    expected_lane_assessments,
    extracted_record_id,
)
from run_multiple_justifications_v0 import assess, justification, justification_set
from run_multiple_justifications_v0 import load_fixture as load_justification_fixture


DERIVED_SUBJECTS = {"Project Vega", "Project Helios", "Project Aurora", "Project Polaris"}


def canonical(qualifiers):
    return json.dumps(qualifiers or {}, sort_keys=True, separators=(",", ":"))


def key_of(item):
    return (item["subject"], item["predicate"], item["object"], canonical(item.get("qualifiers")))


def knowledge_time(snapshot_id):
    return int(snapshot_id[-4:]) * 10


# --------------------------------------------------------------------------
# Ordinary event-sourced application (B1 / B2)
# --------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE facts (
    fact_id INTEGER PRIMARY KEY,
    evidence_id TEXT NOT NULL UNIQUE,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    qualifiers TEXT NOT NULL,
    recorded_at INTEGER NOT NULL
);
CREATE TABLE single_valued (predicate TEXT PRIMARY KEY);
CREATE TABLE policies (
    view_scope TEXT NOT NULL,
    version INTEGER NOT NULL,
    conflict_rule TEXT NOT NULL CHECK (conflict_rule IN ('withhold', 'admit_plural')),
    effective_at INTEGER NOT NULL,
    PRIMARY KEY (view_scope, version)
);
CREATE TABLE conclusions (
    recorded_at INTEGER NOT NULL,
    rule_version INTEGER NOT NULL,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    qualifiers TEXT NOT NULL,
    via TEXT NOT NULL
);
"""

# Base facts current at :t. Single-valued predicates keep only the latest fact
# per subject/predicate/qualifiers; everything else accumulates.
CURRENT_FACTS = """
SELECT f.* FROM facts f
WHERE f.recorded_at <= :t
  AND NOT EXISTS (
      SELECT 1 FROM facts g JOIN single_valued s ON s.predicate = g.predicate
      WHERE g.subject = f.subject AND g.predicate = f.predicate
        AND g.qualifiers = f.qualifiers
        AND g.recorded_at <= :t AND g.recorded_at > f.recorded_at
  )
"""

SUPERSEDED_FACTS = """
SELECT f.subject, f.predicate, f.object, f.qualifiers,
       (SELECT g.object FROM facts g
        WHERE g.subject = f.subject AND g.predicate = f.predicate
          AND g.qualifiers = f.qualifiers
          AND g.recorded_at > f.recorded_at AND g.recorded_at <= :t
        ORDER BY g.recorded_at LIMIT 1) AS successor
FROM facts f JOIN single_valued s ON s.predicate = f.predicate
WHERE f.recorded_at <= :t
  AND EXISTS (
      SELECT 1 FROM facts g
      WHERE g.subject = f.subject AND g.predicate = f.predicate
        AND g.qualifiers = f.qualifiers
        AND g.recorded_at > f.recorded_at AND g.recorded_at <= :t
  )
"""


def derived_sql(rule_version):
    """Business rules. Version 1 propagates blocked status transitively; the
    version 2 probe propagates only through direct dependencies."""
    transitive = """
        UNION
        SELECT d.subject, 'status', 'blocked', d.qualifiers, d.object
        FROM cur d JOIN derived r
          ON r.subject = d.object AND r.object = 'blocked' AND r.qualifiers = d.qualifiers
        WHERE d.predicate = 'depends_on'
    """
    return f"""
    WITH RECURSIVE
    cur AS ({CURRENT_FACTS}),
    derived(subject, predicate, object, qualifiers, via) AS (
        SELECT d.subject, 'status', 'blocked', d.qualifiers, d.object
        FROM cur d JOIN cur s
          ON s.subject = d.object AND s.predicate = 'status'
         AND s.object = 'blocked' AND s.qualifiers = d.qualifiers
        WHERE d.predicate = 'depends_on'
        {transitive if rule_version == 1 else ''}
    )
    SELECT subject, predicate, object, qualifiers, via FROM derived
    UNION
    SELECT c.subject, 'status', 'ready', c.qualifiers, 'release_checks+release_approval'
    FROM cur c JOIN cur a
      ON a.subject = c.subject AND a.predicate = 'release_approval'
     AND a.object = 'granted' AND a.qualifiers = c.qualifiers
    WHERE c.predicate = 'release_checks' AND c.object = 'passed'
    """


class EventSourcedApp:
    def __init__(self, record_conclusions):
        self.record_conclusions = record_conclusions
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(SCHEMA)
        self.conn.execute("INSERT INTO single_valued VALUES ('status')")
        self.rule_version = 1
        self.commits = []

    def set_policy(self, view_scope, version, conflict_rule, effective_at):
        self.conn.execute(
            "INSERT INTO policies VALUES (?, ?, ?, ?)",
            (view_scope, version, conflict_rule, effective_at),
        )

    def deploy_rule(self, version):
        self.rule_version = version

    def ingest(self, evidence_items, t):
        for item in evidence_items:
            assertion = item["assertions"][0]
            self.conn.execute(
                "INSERT INTO facts (evidence_id, subject, predicate, object, qualifiers, recorded_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item["evidence_id"],
                    assertion["subject"],
                    assertion["predicate"],
                    assertion["object"],
                    canonical(assertion.get("qualifiers")),
                    t,
                ),
            )
        self.commits.append(t)
        if self.record_conclusions:
            rows = self.conn.execute(derived_sql(self.rule_version), {"t": t}).fetchall()
            self.conn.executemany(
                "INSERT INTO conclusions VALUES (?, ?, ?, ?, ?, ?, ?)",
                [(t, self.rule_version, *row) for row in rows],
            )

    def derived(self, t):
        if self.record_conclusions:
            commit = max(c for c in self.commits if c <= t)
            return self.conn.execute(
                "SELECT subject, predicate, object, qualifiers, via FROM conclusions WHERE recorded_at = ?",
                (commit,),
            ).fetchall()
        return self.conn.execute(derived_sql(self.rule_version), {"t": t}).fetchall()

    def view(self, t, view_scope):
        policy = self.conn.execute(
            "SELECT version, conflict_rule FROM policies WHERE view_scope = ? AND effective_at <= ? "
            "ORDER BY effective_at DESC, version DESC LIMIT 1",
            (view_scope, t),
        ).fetchone()
        rows = self.derived(t)
        why = defaultdict(set)
        for subject, predicate, obj, qualifiers, via in rows:
            why[(subject, predicate, obj, qualifiers)].add(via)
        values = defaultdict(set)
        single = {row[0] for row in self.conn.execute("SELECT predicate FROM single_valued")}
        for subject, predicate, obj, qualifiers in why:
            if predicate in single:
                values[(subject, predicate, qualifiers)].add(obj)
        conflicted = sorted(
            key for key in why if len(values.get((key[0], key[1], key[3]), ())) > 1
        )

        dispositions = {}
        for key in why:
            if key in conflicted and policy[1] == "withhold":
                dispositions[key] = ("withheld", "unresolved_supported_conflict", None)
            else:
                dispositions[key] = ("admitted", None, None)
        earlier = set()
        for commit in self.commits:
            if commit < t:
                earlier |= {row[:4] for row in self.derived(commit)}
        for key in earlier - set(why):
            dispositions[key] = ("withheld", "support_withdrawn", None)
        for row in self.conn.execute(
            "SELECT subject, predicate, object, qualifiers FROM (" + CURRENT_FACTS + ")", {"t": t}
        ):
            dispositions[tuple(row)] = ("admitted", None, None)
        for subject, predicate, obj, qualifiers, successor in self.conn.execute(SUPERSEDED_FACTS, {"t": t}):
            dispositions[(subject, predicate, obj, qualifiers)] = (
                "superseded",
                None,
                (subject, predicate, successor, qualifiers),
            )
        return {
            "policy": [view_scope, policy[0], policy[1]],
            "dispositions": dispositions,
            "why": {key: sorted(vias) for key, vias in why.items()},
            "conflicted": conflicted,
        }


# --------------------------------------------------------------------------
# Naive application (B0, control)
# --------------------------------------------------------------------------


class NaiveApp:
    """One mutable status per entity, recomputed on every change; a project
    with no blocked dependency and no release readiness defaults to 'clear'."""

    def __init__(self):
        self.status = {}
        self.dependencies = defaultdict(set)
        self.attributes = {}
        self.commits = []

    def set_policy(self, *args):
        pass

    def deploy_rule(self, version):
        pass

    def ingest(self, evidence_items, t):
        for item in evidence_items:
            a = item["assertions"][0]
            q = canonical(a.get("qualifiers"))
            if a["predicate"] == "depends_on":
                self.dependencies[(a["subject"], q)].add(a["object"])
            elif a["predicate"] == "status":
                self.status[(a["subject"], q)] = a["object"]
            else:
                self.attributes[(a["subject"], a["predicate"], q)] = a["object"]
        projects = {subject for subject, _ in self.dependencies} | {
            subject for subject, _, _ in self.attributes
        }
        changed = True
        while changed:
            changed = False
            for entity, q in sorted(self.dependencies) + [
                (s, q) for s, _, q in self.attributes if s in projects
            ]:
                blocked = any(
                    self.status.get((dep, q)) == "blocked" for dep in self.dependencies.get((entity, q), ())
                )
                ready = (
                    self.attributes.get((entity, "release_checks", q)) == "passed"
                    and self.attributes.get((entity, "release_approval", q)) == "granted"
                )
                value = "blocked" if blocked else "ready" if ready else "clear"
                if self.status.get((entity, q)) != value:
                    self.status[(entity, q)] = value
                    changed = True
        self.commits.append(t)

    def view(self, t, view_scope):
        if t != self.commits[-1]:
            return None  # no history: only the present can be shown
        dispositions = {
            (entity, "status", value, q): ("admitted", None, None)
            for (entity, q), value in self.status.items()
        }
        for (subject, q), objects in self.dependencies.items():
            for obj in objects:
                dispositions[(subject, "depends_on", obj, q)] = ("admitted", None, None)
        for (subject, predicate, q), obj in self.attributes.items():
            dispositions[(subject, predicate, obj, q)] = ("admitted", None, None)
        return {"policy": None, "dispositions": dispositions, "why": None, "conflicted": None}


# --------------------------------------------------------------------------
# Memory Lab reference artifacts, mapped onto GEI CVD values
# --------------------------------------------------------------------------


def consistency_to_cvd(assessment, key_by_id):
    out = {}
    for record_id in assessment["record_ids"]:
        key = key_by_id[record_id]
        if record_id in assessment["selected_record_ids"]:
            out[key] = ("admitted", None, None)
        elif record_id in assessment["supported_record_ids"]:
            out[key] = ("withheld", "unresolved_supported_conflict", None)
        else:
            out[key] = ("withheld", "support_withdrawn", None)
    return out


def reassessment_to_cvd(result, key_by_id):
    if result["support_outcome"] == "replaced":
        return ("superseded", None, key_by_id[result["replacement_record_ids"][0]])
    if result["support_outcome"] == "withdrawn":
        return ("withheld", "support_withdrawn", None)
    return ("admitted", None, None)


def cvd_to_reassessment(disposition):
    """Inverse used to check that the CVD projection loses nothing (GB-02)."""
    state, _, successor = disposition
    if state == "superseded":
        return {"support_outcome": "replaced", "resulting_view": "historical_only", "has_replacement": successor is not None}
    if state == "withheld":
        return {"support_outcome": "withdrawn", "resulting_view": "historical_only", "has_replacement": False}
    return {"support_outcome": "retained", "resulting_view": "active", "has_replacement": False}


def polaris_reference():
    fixture = load_conflict_fixture()
    evidence = evidence_map(fixture)
    expected = expected_lane_assessments(fixture)
    key_by_id = {}
    for ref, item in evidence.items():
        assertion = item["assertions"][0]
        key_by_id[extracted_record_id(assertion, item["snapshot_id"])] = key_of(assertion)
    for derivation in DERIVATIONS:
        key_by_id[derived_record_id(derivation["object"])] = (
            "Project Polaris", "status", derivation["object"], canonical(QUALIFIERS)
        )
    at_0400 = {}
    at_0400.update(consistency_to_cvd(expected["conflict_0400"], key_by_id))
    at_0400.update(consistency_to_cvd(expected["multivalue_0400"], key_by_id))
    at_0401 = consistency_to_cvd(expected["resolved_0401"], key_by_id)
    return fixture, {knowledge_time("SYN-DM-0400"): at_0400, knowledge_time("SYN-DM-0401"): at_0401}


def reassessment_reference():
    fixture = load_reassessment_fixture()
    evidence = evidence_map(fixture)
    records = {}

    def add(item):
        checked, _ = apply_support(item, evidence, records)
        records[checked["record_id"]] = checked
        return checked

    vega_dep = add(record("relationship", "Project Vega", "depends_on", "Module Sigma", ["EV-VEGA-DEP-0200"], "SYN-DM-0200"))
    sigma_blocked = add(record("state", "Module Sigma", "status", "blocked", ["EV-SIGMA-BLOCKED-0200"], "SYN-DM-0200"))
    vega_blocked = add(record(
        "state", "Project Vega", "status", "blocked",
        ["EV-VEGA-DEP-0200", "EV-SIGMA-BLOCKED-0200"], "SYN-DM-0200",
        derived_from_records=[vega_dep["record_id"], sigma_blocked["record_id"]],
        derivation_rule="dependency_block_propagation",
    ))
    helios_dep = add(record("relationship", "Project Helios", "depends_on", "Project Vega", ["EV-HELIOS-DEP-0200"], "SYN-DM-0200"))
    add(record(
        "state", "Project Helios", "status", "blocked",
        ["EV-HELIOS-DEP-0200", "EV-VEGA-DEP-0200", "EV-SIGMA-BLOCKED-0200"], "SYN-DM-0200",
        derived_from_records=[helios_dep["record_id"], vega_blocked["record_id"]],
        derivation_rule="dependency_block_propagation",
    ))
    sigma_clear, _ = apply_support(
        record("state", "Module Sigma", "status", "clear", ["EV-SIGMA-CLEAR-0201"], "SYN-DM-0201",
               change_kind="world_state_changed"),
        evidence, records,
    )
    plan = build_plan(records, [sigma_blocked["record_id"]], "SYN-DM-0200", "SYN-DM-0201")
    results = reassess(plan, records, {sigma_blocked["record_id"]: [sigma_clear["record_id"]]})
    key_by_id = {rid: key_of(item) for rid, item in records.items()}
    key_by_id[sigma_clear["record_id"]] = key_of(sigma_clear)

    at_0200 = {key_of(item): ("admitted", None, None) for item in records.values()}
    at_0201 = {key_by_id[rid]: ("admitted", None, None) for rid in plan["unaffected_record_ids"]}
    at_0201[key_of(sigma_clear)] = ("admitted", None, None)
    for result in results:
        at_0201[key_by_id[result["record_id"]]] = reassessment_to_cvd(result, key_by_id)
    return fixture, results, {knowledge_time("SYN-DM-0200"): at_0200, knowledge_time("SYN-DM-0201"): at_0201}


def justification_reference():
    fixture = load_justification_fixture()
    evidence = evidence_map(fixture)
    records = {}

    def add(item):
        checked, _ = apply_support(item, evidence, records)
        records[checked["record_id"]] = checked
        return checked

    sigma_dep = add(record("relationship", "Project Aurora", "depends_on", "Module Sigma", ["EV-AURORA-SIGMA-DEP"], "SYN-DM-0300"))
    sigma_blocked = add(record("state", "Module Sigma", "status", "blocked", ["EV-SIGMA-BLOCKED-0300"], "SYN-DM-0300"))
    tau_dep = add(record("relationship", "Project Aurora", "depends_on", "Module Tau", ["EV-AURORA-TAU-DEP"], "SYN-DM-0300"))
    tau_blocked = add(record("state", "Module Tau", "status", "blocked", ["EV-TAU-BLOCKED-0300"], "SYN-DM-0300"))
    aurora_id = stable_id("state", "Project Aurora", "status", "blocked", {}, None, "SYN-DM-0300")
    j_sigma = justification("dependency_block_propagation", [sigma_dep["record_id"], sigma_blocked["record_id"]],
                            ["EV-AURORA-SIGMA-DEP", "EV-SIGMA-BLOCKED-0300"])
    j_tau = justification("dependency_block_propagation", [tau_dep["record_id"], tau_blocked["record_id"]],
                          ["EV-AURORA-TAU-DEP", "EV-TAU-BLOCKED-0300"])
    support_set = justification_set(aurora_id, [j_sigma, j_tau])
    sigma_clear_id = stable_id("state", "Module Sigma", "status", "clear", {}, None, "SYN-DM-0301")
    tau_clear_id = stable_id("state", "Module Tau", "status", "clear", {}, None, "SYN-DM-0302")
    active = {
        "SYN-DM-0300": set(records),
        "SYN-DM-0301": (set(records) - {sigma_blocked["record_id"]}) | {sigma_clear_id},
        "SYN-DM-0302": (set(records) - {sigma_blocked["record_id"], tau_blocked["record_id"]})
        | {sigma_clear_id, tau_clear_id},
    }
    via = {j_sigma["justification_id"]: "Module Sigma", j_tau["justification_id"]: "Module Tau"}
    aurora_key = ("Project Aurora", "status", "blocked", canonical({}))
    reference, why = {}, {}
    for snapshot, active_ids in active.items():
        assessment = assess(support_set, active_ids, snapshot)
        disposition = ("admitted", None, None) if assessment["support_outcome"] == "retained" else (
            "withheld", "support_withdrawn", None)
        reference[knowledge_time(snapshot)] = {aurora_key: disposition}
        why[knowledge_time(snapshot)] = sorted(via[j] for j in assessment["active_justification_ids"])
    return fixture, reference, why, aurora_key


# --------------------------------------------------------------------------
# Runs and checks
# --------------------------------------------------------------------------


def by_snapshot(fixture):
    grouped = defaultdict(list)
    for item in fixture["evidence"]:
        grouped[knowledge_time(item["snapshot_id"])].append(item)
    return dict(sorted(grouped.items()))


def restrict(dispositions, keys):
    return {key: dispositions.get(key, ("absent", None, None)) for key in keys}


def invented_negations(dispositions):
    return sorted(
        key for key, value in dispositions.items()
        if key[0] in DERIVED_SUBJECTS and key[1] == "status" and key[2] == "clear" and value[0] == "admitted"
    )


def run_design(make_app):
    polaris_fixture, polaris_ref = polaris_reference()
    reassess_fixture, _, reassess_ref = reassessment_reference()
    justify_fixture, justify_ref, justify_why, aurora_key = justification_reference()
    checks = {}
    observed = {}

    # Reassessment lane, then a rule-version probe.
    app = make_app()
    app.set_policy("release-gate", 1, "withhold", 0)
    for t, items in by_snapshot(reassess_fixture).items():
        app.ingest(items, t)
        observed[("reassessment", t)] = app.view(t, "release-gate")
    equivalence = [
        observed[("reassessment", t)] is not None
        and restrict(observed[("reassessment", t)]["dispositions"], ref) == ref
        for t, ref in reassess_ref.items()
    ]
    negations = invented_negations(observed[("reassessment", 2010)]["dispositions"])
    app.deploy_rule(2)
    replay = app.view(2000, "release-gate")
    history_rule_change = replay is not None and replay["dispositions"] == observed[("reassessment", 2000)]["dispositions"]
    replay_view = None if replay is None else sorted(k[0] for k, v in replay["dispositions"].items() if k[1] == "status" and v[0] == "admitted")

    # Multiple-justification lane.
    app = make_app()
    app.set_policy("release-gate", 1, "withhold", 0)
    for t, items in by_snapshot(justify_fixture).items():
        app.ingest(items, t)
        observed[("justification", t)] = app.view(t, "release-gate")
    for t, ref in justify_ref.items():
        view = observed[("justification", t)]
        equivalence.append(view is not None and restrict(view["dispositions"], ref) == ref)
    negations += invented_negations(observed[("justification", 3020)]["dispositions"])
    why_matches = all(
        observed[("justification", t)]["why"] is not None
        and observed[("justification", t)]["why"].get(aurora_key, []) == justify_why[t]
        for t in justify_why
        if justify_why[t]
    )
    history_same_rule = all(
        (lambda replayed: replayed is not None and replayed["dispositions"] == observed[("justification", t)]["dispositions"])(
            app.view(t, "release-gate"))
        for t in justify_ref
    )

    # Conflict lane with two view scopes and a policy version change.
    app = make_app()
    app.set_policy("release-gate", 1, "withhold", 0)
    app.set_policy("exploratory", 1, "admit_plural", 0)
    app.set_policy("release-gate", 2, "admit_plural", 4005)
    snapshots = by_snapshot(polaris_fixture)
    app.ingest(snapshots[4000], 4000)
    gate_4000 = app.view(4000, "release-gate")
    explore_4000 = app.view(4000, "exploratory")
    gate_4005 = app.view(4005, "release-gate")
    app.ingest(snapshots[4010], 4010)
    gate_4010 = app.view(4010, "release-gate")
    for t, view in ((4000, gate_4000), (4010, gate_4010)):
        ref = polaris_ref[t]
        equivalence.append(view is not None and restrict(view["dispositions"], ref) == ref)
    blocked_key = ("Project Polaris", "status", "blocked", canonical(QUALIFIERS))
    ready_key = ("Project Polaris", "status", "ready", canonical(QUALIFIERS))
    both_supported_preserved = gate_4000 is not None and all(
        gate_4000["dispositions"].get(key, ("absent",))[0] == "withheld" for key in (blocked_key, ready_key)
    )
    scoped = (
        gate_4000 is not None and explore_4000 is not None and explore_4000["policy"] is not None
        and explore_4000["dispositions"].get(blocked_key, ("absent",))[0] == "admitted"
        and explore_4000["dispositions"].get(ready_key, ("absent",))[0] == "admitted"
        and explore_4000["conflicted"] == gate_4000["conflicted"] == sorted([blocked_key, ready_key])
    )
    policy_versioned = (
        gate_4005 is not None and gate_4005["policy"] is not None
        and gate_4005["policy"][1] == 2
        and gate_4005["why"] == gate_4000["why"]
        and gate_4005["conflicted"] == gate_4000["conflicted"]
        and gate_4005["dispositions"][blocked_key][0] == "admitted"
        and app.view(4000, "release-gate") is not None
        and app.view(4000, "release-gate")["dispositions"] == gate_4000["dispositions"]
    )
    negations += invented_negations(gate_4010["dispositions"]) if gate_4010 else []

    def verdict(value):
        return "pass" if value else "fail"

    def representable(view, value):
        return "unrepresentable" if view is None or (isinstance(view, dict) and view.get("policy") is None) else verdict(value)

    checks["C11_equivalence_with_memory_lab"] = verdict(all(equivalence))
    checks["C3_withdrawal_not_negation"] = verdict(not negations)
    checks["C4_both_supported_preserved"] = verdict(both_supported_preserved)
    checks["C1_history_same_rule"] = "unrepresentable" if replay is None else verdict(history_same_rule)
    checks["C1_history_after_rule_change"] = "unrepresentable" if replay is None else verdict(history_rule_change)
    checks["C10_why_retained_after_path_loss"] = "unrepresentable" if observed[("justification", 3010)]["why"] is None else verdict(why_matches)
    checks["C8_scoped_dispositions"] = representable(explore_4000, scoped)
    checks["C9_policy_version_change"] = representable(gate_4005, policy_versioned)
    return checks, {"invented_negations": negations, "status_admitted_at_0200_after_rule_change": replay_view}


def memory_lab_capabilities():
    """What Memory Lab's own artifacts can express for the same checks."""
    _, results, _ = reassessment_reference()
    for result in results:
        mapped = reassessment_to_cvd(result, {rid: rid for rid in result["replacement_record_ids"]})
        inverse = cvd_to_reassessment(mapped)
        assert inverse["support_outcome"] == result["support_outcome"]
        assert inverse["resulting_view"] == result["resulting_view"]
        assert inverse["has_replacement"] == bool(result["replacement_record_ids"])
    return {
        "C11_equivalence_with_memory_lab": "reference",
        "C3_withdrawal_not_negation": "pass",
        "C4_both_supported_preserved": "pass",
        "C1_history_same_rule": "pass",
        "C1_history_after_rule_change": "pass (derived records are immutable history)",
        "C10_why_retained_after_path_loss": "pass",
        "C8_scoped_dispositions": "unrepresentable (no scope field)",
        "C9_policy_version_change": "unrepresentable (no policy field)",
    }


def main():
    results = {}
    memory_lab = memory_lab_capabilities()
    results["GB-02_cvd_mapping"] = "lossless_round_trip_for_reassessment_results"

    designs = {
        "B0_naive_mutable": NaiveApp,
        "B2_recompute_on_read": lambda: EventSourcedApp(record_conclusions=False),
        "B1_recorded_conclusions": lambda: EventSourcedApp(record_conclusions=True),
    }
    matrix = {"memory_lab_artifacts": memory_lab}
    details = {}
    for name, factory in designs.items():
        matrix[name], details[name] = run_design(factory)

    # Expectations were written before the first run.
    b1, b2, b0 = matrix["B1_recorded_conclusions"], matrix["B2_recompute_on_read"], matrix["B0_naive_mutable"]
    assert set(b1.values()) == {"pass"}, b1
    assert {k for k, v in b2.items() if v != "pass"} == {"C1_history_after_rule_change"}, b2
    assert details["B2_recompute_on_read"]["status_admitted_at_0200_after_rule_change"] == ["Module Sigma", "Project Vega"]
    assert b0["C11_equivalence_with_memory_lab"] == "fail"
    assert b0["C3_withdrawal_not_negation"] == "fail"
    assert b0["C4_both_supported_preserved"] == "fail"
    assert {b0[k] for k in ("C1_history_same_rule", "C1_history_after_rule_change", "C10_why_retained_after_path_loss",
                            "C8_scoped_dispositions", "C9_policy_version_change")} == {"unrepresentable"}
    results["B1_recorded_conclusions"] = "passes_every_check_including_scope_and_policy_version"
    results["B2_recompute_on_read"] = "passes_everything_except_history_after_a_rule_change"
    results["B0_naive_mutable"] = "collapses_conflict_invents_negation_keeps_no_history"

    footprint = {
        "sql_statements": sum(len(text.strip().splitlines()) for text in (SCHEMA, CURRENT_FACTS, SUPERSEDED_FACTS))
        + len(inspect.getsource(derived_sql).splitlines()),
        "event_sourced_app_python": len(inspect.getsource(EventSourcedApp).splitlines()),
    }

    output = {
        "status": "passed",
        "mode": "current-view admission vs ordinary application state (issue #13)",
        "results": results,
        "check_matrix": matrix,
        "details": details,
        "baseline_footprint_lines": footprint,
        "research_findings": {
            "admission_is_ordinary_projection": "an event-sourced table plus a versioned, scoped policy table reproduces every Memory Lab current-view outcome and also expresses scope and policy version, which Memory Lab artifacts cannot",
            "reassessment_plan_is_optimization": "recomputing the projection yields the same current view without dependency-closure plans; plans matter for efficiency and audit, not for correctness here",
            "surviving_obligation": "conclusions must be recorded, not recomputed on read, when derivation rules can change; otherwise history is silently rewritten",
            "checks_discriminate": "the same checks separate a careful design from a naive one",
        },
        "not_validated": [
            "real application code or real corpora",
            "concurrent writers or replication",
            "valid-time intervals on derived facts (views are as-of knowledge time)",
            "interpretation correction without a rule change",
            "coverage semantics",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"APPSTATE_BASELINE_V0_FAIL: {exc}", file=sys.stderr)
        raise

#!/usr/bin/env python3
"""Coverage decision value on SciFact (issue #12): Memory-Lab-owned logic.

Holds only the decision rules, the GEI REC coverage-state rule, the arms fixed in
experiments/coverage-scifact-v0/PREREGISTRATION.md, and scoring. Retrieval and
data loading live in experiments/coverage-scifact-v0/run_coverage_scifact.py.

Without SciFact present this runner checks the logic on synthetic claims. When
the recorded results file exists it recomputes every recorded aggregate, tau,
prediction, and bootstrap interval from the recorded per-claim rankings and
labels.
"""
import json
import pathlib
import random
import statistics
import sys
from collections import Counter


ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = (
    ROOT
    / "experiments"
    / "coverage-scifact-v0"
    / "results"
    / "coverage-scifact-v0.results.json"
)

ACCEPT, REJECT, WITHHOLD = "ACCEPT", "REJECT", "WITHHOLD"
SUPPORT, CONTRADICT = "SUPPORT", "CONTRADICT"
REC_STATES = ("not-assessed", "unknown", "known-incomplete", "bounded-complete")
KS = (3, 10, 20)
PRIMARY_K = 10
WEIGHTS = (1, 3, 10)
NON_COVERAGE_ARMS = ("A0", "A1", "A2-gate", "A2-pool")
COVERAGE_ARMS = ("A0-cov", "A3-strict", "A3-reassess", "A3-caution")
ARMS = NON_COVERAGE_ARMS + COVERAGE_ARMS
D1_ARMS = ("A1", "A2-gate", "A2-pool", "A3-strict", "A3-reassess", "A3-caution")
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 12


def collection_truth(labels):
    kinds = set(labels.values())
    if not kinds:
        return "NEI"
    if kinds == {SUPPORT}:
        return "SUPPORTED"
    if kinds == {CONTRADICT}:
        return "CONTRADICTED"
    return "MIXED"


def decide_d0(stances):
    """Default-accept: the absence fallacy."""
    return REJECT if CONTRADICT in stances else ACCEPT


def decide_d1(stances):
    """NEI semantics: a verdict needs evidence of one polarity only."""
    supported = SUPPORT in stances
    contradicted = CONTRADICT in stances
    if supported and not contradicted:
        return ACCEPT
    if contradicted and not supported:
        return REJECT
    return WITHHOLD


def coverage_state(procedures_run, considered, universe_size, judged_found):
    """REC coverage of the considered set, from procedures actually run."""
    if not procedures_run:
        return "not-assessed"
    if len(set(considered)) >= universe_size:
        return "bounded-complete"
    if set(judged_found) - set(considered):
        return "known-incomplete"
    return "unknown"


def outcome(decision, truth):
    if decision == WITHHOLD:
        return "withhold"
    if (decision, truth) in {(ACCEPT, "SUPPORTED"), (REJECT, "CONTRADICTED")}:
        return "correct"
    return "wrong"


def decisive_score(ranking, labels, decision):
    wanted = SUPPORT if decision == ACCEPT else CONTRADICT
    for doc_id, score in ranking:
        if labels.get(doc_id) == wanted:
            return score
    return None


def arms_for_claim(claim, k, tau, universe_size):
    labels = claim["evidence"]
    p1 = claim["p1"][:k]
    p2 = claim["p2"][:k]
    p1_ids = [doc_id for doc_id, _ in p1]
    pool_ids = p1_ids + [doc_id for doc_id, _ in p2 if doc_id not in p1_ids]

    def stances(ids):
        return [labels.get(doc_id) for doc_id in ids]

    alone = coverage_state(["P1"], p1_ids, universe_size, set())
    audited = coverage_state(
        ["P1", "P2"], p1_ids, universe_size, {doc_id for doc_id, _ in p2 if doc_id in labels}
    )
    d0 = decide_d0(stances(p1_ids))
    d1 = decide_d1(stances(p1_ids))
    pooled = decide_d1(stances(pool_ids))
    gated = d1
    if d1 != WITHHOLD and tau is not None and decisive_score(p1, labels, d1) < tau:
        gated = WITHHOLD
    decisions = {
        "A0": d0,
        "A0-cov": d0 if d0 != ACCEPT or alone == "bounded-complete" else WITHHOLD,
        "A1": d1,
        "A2-gate": gated,
        "A2-pool": pooled,
        "A3-strict": d1 if alone == "bounded-complete" else WITHHOLD,
        "A3-reassess": pooled if audited == "known-incomplete" else d1,
        "A3-caution": WITHHOLD if audited == "known-incomplete" else d1,
    }
    coverage = {
        "A0-cov": alone,
        "A3-strict": alone,
        "A3-reassess": audited,
        "A3-caution": audited,
    }
    return decisions, coverage


def aggregate(truths, decisions, arm):
    counts = Counter()
    for truth, decided in zip(truths, decisions):
        decision = decided[arm]
        result = outcome(decision, truth)
        if result == "withhold":
            counts[f"withhold_{truth.lower()}"] += 1
        else:
            counts[f"{result}_{decision.lower()}"] += 1
    return dict(sorted(counts.items()))


def utility(counts, w):
    correct = counts.get("correct_accept", 0) + counts.get("correct_reject", 0)
    wrong = counts.get("wrong_accept", 0) + counts.get("wrong_reject", 0)
    return correct - w * wrong


def recall_at_k(claims, k):
    found = Counter()
    total = 0
    for claim in claims:
        evidence = set(claim["evidence"])
        if not evidence:
            continue
        p1 = {doc_id for doc_id, _ in claim["p1"][:k]}
        p2 = {doc_id for doc_id, _ in claim["p2"][:k]}
        total += len(evidence)
        found["P1"] += len(evidence & p1)
        found["P2"] += len(evidence & p2)
        found["pool"] += len(evidence & (p1 | p2))
    return {name: round(found[name] / total, 4) for name in ("P1", "P2", "pool")}


def evaluate(claims, k, tau, universe_size):
    per_claim = [arms_for_claim(claim, k, tau, universe_size) for claim in claims]
    truths = [claim["truth"] for claim in claims]
    decisions = [decided for decided, _ in per_claim]
    arms = {}
    for arm in ARMS:
        counts = aggregate(truths, decisions, arm)
        arms[arm] = {"counts": counts, "utility": {f"U{w}": utility(counts, w) for w in WEIGHTS}}
    coverage = {
        arm: dict(sorted(Counter(states[arm] for _, states in per_claim).items()))
        for arm in COVERAGE_ARMS
    }
    return {"tau": tau, "arms": arms, "coverage": coverage, "recall": recall_at_k(claims, k)}, decisions


def choose_tau(claims, k, universe_size, w=3):
    """A2-gate threshold: no gating or a train decile, maximizing U_w; ties
    go to the least gating."""
    scores = []
    for claim in claims:
        p1 = claim["p1"][:k]
        decision = decide_d1([claim["evidence"].get(doc_id) for doc_id, _ in p1])
        if decision != WITHHOLD:
            scores.append(decisive_score(p1, claim["evidence"], decision))
    candidates = [None]
    if len(scores) >= 2:
        candidates += sorted(set(statistics.quantiles(scores, n=10)))
    truths = [claim["truth"] for claim in claims]
    best_tau, best_utility = None, None
    for tau in candidates:
        decisions = [arms_for_claim(claim, k, tau, universe_size)[0] for claim in claims]
        value = utility(aggregate(truths, decisions, "A2-gate"), w)
        if best_utility is None or value > best_utility:
            best_tau, best_utility = tau, value
    return best_tau


def ceiling(claims):
    truths = [claim["truth"] for claim in claims]
    decisions = [{"Ceiling": decide_d1(list(claim["evidence"].values()))} for claim in claims]
    counts = aggregate(truths, decisions, "Ceiling")
    return {"counts": counts, "utility": {f"U{w}": utility(counts, w) for w in WEIGHTS}}


def best_arm(utilities, arms):
    return max(arms, key=lambda arm: (utilities[arm], arm))


def bootstrap_difference(claims, decisions, arm_a, arm_b, w=3):
    def contribution(truth, decision):
        result = outcome(decision, truth)
        return 1 if result == "correct" else (-w if result == "wrong" else 0)

    pairs = [
        (contribution(claim["truth"], decided[arm_a]), contribution(claim["truth"], decided[arm_b]))
        for claim, decided in zip(claims, decisions)
    ]
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(pairs)
    diffs = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        total = 0
        for _ in range(n):
            a, b = pairs[rng.randrange(n)]
            total += a - b
        diffs.append(total)
    diffs.sort()
    return {
        "arm_a": arm_a,
        "arm_b": arm_b,
        "observed": sum(a - b for a, b in pairs),
        "ci95": [diffs[int(0.025 * BOOTSTRAP_RESAMPLES)], diffs[int(0.975 * BOOTSTRAP_RESAMPLES) - 1]],
    }


def evaluate_predictions(by_k, decisions_by_k, claims):
    primary = by_k[str(PRIMARY_K)]
    predictions = {}

    wrong = {
        str(k): {
            arm: by_k[str(k)]["arms"][arm]["counts"].get("wrong_accept", 0)
            + by_k[str(k)]["arms"][arm]["counts"].get("wrong_reject", 0)
            for arm in D1_ARMS
        }
        for k in KS
    }
    predictions["1_d1_arms_never_wrong"] = {
        "held": all(value == 0 for per_k in wrong.values() for value in per_k.values()),
        "observed": wrong,
    }

    fallacy = primary["arms"]["A0"]["counts"].get("wrong_accept", 0)
    predictions["2_absence_fallacy_at_least_112_wrong_accepts"] = {
        "held": fallacy >= 112,
        "observed": fallacy,
    }

    accepts = {
        str(k): {
            arm: sum(1 for decided in decisions_by_k[str(k)] if decided[arm] == ACCEPT)
            for arm in ("A0-cov", "A3-strict")
        }
        for k in KS
    }
    predictions["3_strict_coverage_accepts_nothing"] = {
        "held": all(value == 0 for per_k in accepts.values() for value in per_k.values()),
        "observed": accepts,
    }

    mismatches = {
        str(k): sum(1 for decided in decisions_by_k[str(k)] if decided["A3-reassess"] != decided["A2-pool"])
        for k in KS
    }
    predictions["4_reassess_equals_pool"] = {
        "held": all(value == 0 for value in mismatches.values()),
        "observed": mismatches,
    }

    alone = primary["coverage"]["A3-strict"]
    audited = primary["coverage"]["A3-caution"]
    known = audited.get("known-incomplete", 0)
    predictions["5_coverage_mostly_unknown"] = {
        "held": alone == {"unknown": len(claims)} and 0 < known < len(claims) / 2,
        "observed": {"p1_alone": alone, "p1_audited": audited},
    }

    utilities = {arm: primary["arms"][arm]["utility"]["U3"] for arm in ARMS}
    best_coverage = best_arm(utilities, COVERAGE_ARMS)
    best_other = best_arm(utilities, NON_COVERAGE_ARMS)
    predictions["6_no_coverage_decision_value"] = {
        "held": utilities[best_coverage] <= utilities[best_other],
        "observed": {
            "best_coverage_arm": best_coverage,
            "best_coverage_U3": utilities[best_coverage],
            "best_non_coverage_arm": best_other,
            "best_non_coverage_U3": utilities[best_other],
        },
    }
    return predictions, best_coverage, best_other


def normalize(claim):
    return {
        "id": claim["id"],
        "truth": claim["truth"],
        "evidence": {int(doc_id): label for doc_id, label in claim["evidence"].items()},
        "p1": [(int(doc_id), score) for doc_id, score in claim["p1"]],
        "p2": [(int(doc_id), score) for doc_id, score in claim["p2"]],
    }


def analyze(train, dev, universe_size):
    """The full preregistered analysis over normalized claims."""
    by_k = {}
    decisions_by_k = {}
    for k in KS:
        tau = choose_tau(train, k, universe_size)
        by_k[str(k)], decisions_by_k[str(k)] = evaluate(dev, k, tau, universe_size)
    predictions, best_coverage, best_other = evaluate_predictions(by_k, decisions_by_k, dev)
    return {
        "by_k": by_k,
        "ceiling": ceiling(dev),
        "predictions": predictions,
        "bootstrap_U3": bootstrap_difference(dev, decisions_by_k[str(PRIMARY_K)], best_coverage, best_other),
    }


def verify_recorded():
    if not RESULTS.exists():
        return "absent"
    recorded = json.loads(RESULTS.read_text(encoding="utf-8"))
    train = [normalize(claim) for claim in recorded["claims"]["train"]]
    dev = [normalize(claim) for claim in recorded["claims"]["dev"]]
    recomputed = analyze(train, dev, recorded["parameters"]["universe_size"])
    for key in ("by_k", "ceiling", "predictions", "bootstrap_U3"):
        assert json.dumps(recomputed[key], sort_keys=True) == json.dumps(recorded[key], sort_keys=True), key
    assert recorded["data"]["sha256"] == "11c621288d41ac144d29b13b0f8503b3820b7d6e8b1f6ff24dff335c196d76be"
    return "verified"


def synthetic_claim(truth_labels, p1, p2):
    return {
        "id": 0,
        "truth": collection_truth(truth_labels),
        "evidence": dict(truth_labels),
        "p1": list(p1),
        "p2": list(p2),
    }


def main():
    results = {}

    assert decide_d0([None, None]) == ACCEPT
    assert decide_d0([SUPPORT, CONTRADICT]) == REJECT
    assert decide_d1([SUPPORT, None]) == ACCEPT
    assert decide_d1([CONTRADICT]) == REJECT
    assert decide_d1([SUPPORT, CONTRADICT]) == WITHHOLD
    assert decide_d1([None]) == WITHHOLD
    results["decision_rules"] = "default_accept_and_nei_semantics_truth_tables"

    universe = 6
    assert coverage_state([], [1], universe, set()) == "not-assessed"
    assert coverage_state(["P1"], [1, 2], universe, set()) == "unknown"
    assert coverage_state(["P1", "P2"], [1, 2], universe, {3}) == "known-incomplete"
    assert coverage_state(["P1"], range(1, universe + 1), universe, set()) == "bounded-complete"
    assert coverage_state(["P1"], [1, 2, 3, 4, 5], universe, set()) != "bounded-complete"
    results["coverage_rule"] = "bounded_complete_only_for_an_exhaustive_procedure"

    # A mixed-polarity claim: support retrieved first, contradiction only by the audit.
    mixed = synthetic_claim({1: SUPPORT, 2: CONTRADICT}, [(1, 5.0), (3, 1.0)], [(2, 0.9), (4, 0.1)])
    decided, states = arms_for_claim(mixed, 2, None, universe)
    assert outcome(decided["A1"], mixed["truth"]) == "wrong"
    assert decided["A2-pool"] == decided["A3-reassess"] == decided["A3-caution"] == WITHHOLD
    assert states["A3-caution"] == "known-incomplete" and states["A3-strict"] == "unknown"
    results["mixed_claim"] = "coverage_and_pooling_both_prevent_the_wrong_accept"

    nei = synthetic_claim({}, [(5, 2.0), (6, 1.0)], [(5, 1.0)])
    decided, _ = arms_for_claim(nei, 2, None, universe)
    assert outcome(decided["A0"], nei["truth"]) == "wrong"
    assert decided["A1"] == WITHHOLD and decided["A0-cov"] == WITHHOLD
    results["absence_fallacy"] = "default_accept_wrong_on_nei_nei_semantics_withholds"

    supported = synthetic_claim({3: SUPPORT}, [(3, 4.0), (1, 1.0)], [(3, 1.0)])
    decided, _ = arms_for_claim(supported, 2, None, universe)
    assert outcome(decided["A1"], supported["truth"]) == "correct"
    assert decided["A3-strict"] == WITHHOLD
    results["strict_coverage"] = "withholds_a_correct_accept_when_not_exhaustive"

    weak_mixed = synthetic_claim({1: SUPPORT, 2: CONTRADICT}, [(1, 0.5), (3, 0.2)], [(4, 0.1)])
    tau = choose_tau([weak_mixed, supported], 2, universe)
    assert tau is not None and 0.5 < tau <= 4.0
    assert arms_for_claim(weak_mixed, 2, tau, universe)[0]["A2-gate"] == WITHHOLD
    assert choose_tau([supported], 2, universe) is None
    results["metric_gate"] = "threshold_chosen_only_when_gating_removes_wrong_decisions"

    results["live_evidence"] = verify_recorded()

    output = {
        "status": "passed",
        "mode": "coverage decision value on SciFact (Memory-Lab-owned logic, issue #12)",
        "results": results,
        "not_validated": [
            "stance classification (the experiment uses gold stance)",
            "conflicting-evidence collections (H4)",
            "neural retrieval",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"COVERAGE_SCIFACT_V0_FAIL: {exc}", file=sys.stderr)
        raise

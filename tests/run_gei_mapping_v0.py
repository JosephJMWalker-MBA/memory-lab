#!/usr/bin/env python3
"""GEI conformance mapping for obligations O1-O8 (issue #15): the fixed rules.

Holds the classification rule and the prediction checks used by
experiments/gei-conformance-v0/run_gei_mapping.py.

- Without results, it checks the rule on synthetic records and checks that the
  expectations file is consistent.
- With the recorded results file, it recomputes every prediction check and
  every class from the recorded validation outcomes.

It needs no RDF or SHACL libraries.
"""
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "gei-conformance-v0"
EXPECTATIONS = EXPERIMENT / "expectations.json"
RESULTS = EXPERIMENT / "results" / "gei-conformance-v0.results.json"
ORDER = ("MISSING", "OUT-OF-SCOPE", "ADAPTABLE", "NATIVE")
OBLIGATIONS = tuple(f"O{index}" for index in range(1, 9))


def form_class(form, recorded, invalidation_candidate_passes):
    if not recorded["gei_conforms"]:
        return "NATIVE"
    if invalidation_candidate_passes and not recorded["candidate_invalidation_conforms"]:
        return "ADAPTABLE"
    if not form["single_graph_checkable"]:
        return "OUT-OF-SCOPE"
    return "MISSING"


def capability_status(recorded, narrowing_passes):
    if recorded["gei_conforms"]:
        return "represented"
    if narrowing_passes and recorded["candidate_st007_narrowed_conforms"]:
        return "rejected-by-gei; represented-with-st007-narrowing"
    return "rejected-by-gei"


def classify_all(expectations, results):
    invalidation_ok = results["noninterference"]["candidate_invalidation"]["passes"]
    narrowing_ok = results["noninterference"]["candidate_st007_narrowed"]["passes"]
    forms = {}
    for form in expectations["overlays"]:
        recorded = results["overlays"][form["file"]]
        if form["kind"] == "violation":
            forms[form["file"]] = form_class(form, recorded, invalidation_ok)
        else:
            forms[form["file"]] = capability_status(recorded, narrowing_ok)
    obligations = {}
    for obligation in OBLIGATIONS:
        motivating = [
            forms[form["file"]]
            for form in expectations["overlays"]
            if form["obligation"] == obligation and form["kind"] == "violation" and form["motivating"]
        ]
        obligations[obligation] = min(motivating, key=ORDER.index)
    return {"forms": forms, "obligations": obligations}


def prediction_checks(expectations, results):
    checks = {}
    for form in expectations["overlays"]:
        recorded = results["overlays"][form["file"]]
        observed = {key: recorded[key] for key in form["predicted"]}
        checks[form["file"]] = {"held": observed == form["predicted"], "observed": observed}
    for check in expectations["gei_internal_checks"]:
        recorded = results["gei_internal_checks"][check["name"]]
        observed = {key: recorded[key] for key in check["predicted"]}
        checks[check["name"]] = {"held": observed == check["predicted"], "observed": observed}
    observed = {
        name: results["noninterference"][name]["passes"]
        for name in expectations["predicted_noninterference"]
    }
    checks["noninterference"] = {
        "held": observed == expectations["predicted_noninterference"],
        "observed": observed,
    }
    classes = classify_all(expectations, results)["obligations"]
    checks["obligation_classes"] = {
        "held": classes == expectations["predicted_obligation_classes"],
        "observed": classes,
    }
    return checks


def check_expectations(expectations):
    files = [form["file"] for form in expectations["overlays"]]
    assert len(files) == len(set(files))
    for form in expectations["overlays"]:
        assert (EXPERIMENT / "overlays" / form["file"]).exists(), form["file"]
        assert form["obligation"] in OBLIGATIONS or form["obligation"] == "ALL", form["file"]
        assert form["kind"] in ("violation", "capability"), form["file"]
        if form["kind"] == "violation":
            assert isinstance(form["motivating"], bool) and isinstance(form["single_graph_checkable"], bool)
            assert form["single_graph_checkable"] or form["why"], form["file"]
    for obligation in OBLIGATIONS:
        assert obligation in expectations["obligations"], obligation
        assert expectations["obligations"][obligation]["gei_contract"], obligation
        assert any(
            form["obligation"] == obligation and form["kind"] == "violation" and form["motivating"]
            for form in expectations["overlays"]
        ), obligation
    assert set(expectations["predicted_obligation_classes"]) == set(OBLIGATIONS)
    assert set(expectations["predicted_obligation_classes"].values()) <= set(ORDER)


def verify_recorded(expectations):
    if not RESULTS.exists():
        return "absent"
    recorded = json.loads(RESULTS.read_text(encoding="utf-8"))
    assert recorded["gei"]["commit"] == expectations["gei"]["commit"]
    assert set(recorded["overlays"]) == {form["file"] for form in expectations["overlays"]}
    assert prediction_checks(expectations, recorded) == recorded["predictions"]
    assert classify_all(expectations, recorded) == recorded["classification"]
    return "verified"


def main():
    results = {}

    checkable = {"single_graph_checkable": True}
    unobservable = {"single_graph_checkable": False}
    rejected = {"gei_conforms": False, "candidate_invalidation_conforms": False}
    caught_by_candidate = {"gei_conforms": True, "candidate_invalidation_conforms": False}
    accepted = {"gei_conforms": True, "candidate_invalidation_conforms": True}
    assert form_class(checkable, rejected, True) == "NATIVE"
    assert form_class(checkable, caught_by_candidate, True) == "ADAPTABLE"
    assert form_class(checkable, caught_by_candidate, False) == "MISSING"
    assert form_class(unobservable, accepted, True) == "OUT-OF-SCOPE"
    assert form_class(checkable, accepted, True) == "MISSING"
    assert min(["NATIVE", "ADAPTABLE", "NATIVE"], key=ORDER.index) == "ADAPTABLE"
    assert min(["NATIVE", "OUT-OF-SCOPE"], key=ORDER.index) == "OUT-OF-SCOPE"
    assert capability_status({"gei_conforms": True, "candidate_st007_narrowed_conforms": True}, True) == "represented"
    assert capability_status({"gei_conforms": False, "candidate_st007_narrowed_conforms": True}, True).endswith("narrowing")
    assert capability_status({"gei_conforms": False, "candidate_st007_narrowed_conforms": True}, False) == "rejected-by-gei"
    results["classification_rule"] = "weakest_motivating_form_with_candidate_noninterference_gate"

    expectations = json.loads(EXPECTATIONS.read_text(encoding="utf-8"))
    check_expectations(expectations)
    results["expectations"] = "consistent_every_obligation_has_a_motivating_violation_form"

    results["live_evidence"] = verify_recorded(expectations)

    output = {
        "status": "passed",
        "mode": "GEI conformance mapping for obligations O1-O8 (issue #15)",
        "results": results,
        "not_validated": [
            "SHACL execution (requires the pinned environment in experiments/gei-conformance-v0)",
            "Apache Jena or any second processor",
            "exports produced by a real adapter rather than hand-authored overlays",
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"GEI_MAPPING_V0_FAIL: {exc}", file=sys.stderr)
        raise

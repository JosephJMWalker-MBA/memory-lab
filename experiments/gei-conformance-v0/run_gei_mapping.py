#!/usr/bin/env python3
"""Map Memory Lab obligations O1-O8 onto GEI's existing SHACL machinery (issue #15).

    python experiments/gei-conformance-v0/run_gei_mapping.py --gei /path/to/governed-intelligence-ecology
    python experiments/gei-conformance-v0/run_gei_mapping.py --gei /path/to/gei --expectations expectations-<name>.json

Requirements:

- The pinned environment in requirements.txt (pySHACL pinned as in GEI's
  requirements-semantic.txt).
- A GEI checkout at the commit pinned in the expectations file. The checkout
  is only read.

Each overlay is validated together with GEI's composed positive reference
path, using the same processor options as GEI's
scripts/validate_reference_path.py.

An expectations file may name its own candidate shapes and results file.
In a candidate path, a `gei:` prefix means a path inside the GEI checkout.
"""
import argparse
import importlib.util
import json
import os
import pathlib
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version

from pyshacl import validate
from rdflib import Graph
from rdflib.namespace import SH

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.dont_write_bytecode = True  # importing GEI's harness must not write into the GEI checkout

from run_gei_mapping_v0 import EXPECTATIONS, classify_all, prediction_checks, results_path  # noqa: E402

OVERLAYS = HERE / "overlays"
DEFAULT_CANDIDATES = {
    "invalidation": "candidate/prov-invalidation-provenance.shacl.ttl",
    "st007_narrowed": "candidate/st-007-narrowed.shacl.ttl",
}
GEI_ST007 = "st-007-human-feedback-transition.shacl.ttl"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # GEI's dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def graph(paths):
    result = Graph()
    for path in paths:
        result.parse(path, format="turtle")
    return result


def shacl(data_paths, shape_paths):
    conforms, report, _ = validate(
        data_graph=graph(data_paths),
        shacl_graph=graph(shape_paths),
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        meta_shacl=True,
        advanced=False,
        js=False,
        debug=False,
    )
    messages = sorted({str(message) for message in report.objects(None, SH.resultMessage)})
    return bool(conforms), messages


def git(path, *args):
    return subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def resolve(candidate, gei):
    if candidate.startswith("gei:"):
        return gei / candidate[len("gei:"):]
    return HERE / candidate


def noninterference(ref, atomic, composed_shapes, transform):
    """Does GEI's own fixture suite behave identically with the candidate applied?"""
    positive = shacl([ref.FIXTURES / name for name in ref.POSITIVE_FILES], composed_shapes)[0]
    negatives = {
        description: not shacl([ref.FIXTURES / name for name in files], composed_shapes)[0]
        for files, description in ref.NEGATIVE_CASES
    }
    cases = {}
    for case in atomic.CASES:
        shapes = transform([atomic.SHAPES / name for name in case.shape_files])
        good = (case.good_fixture, *getattr(case, "extra_good_fixtures", ()))
        bad = (case.bad_fixture, *getattr(case, "extra_bad_fixtures", ()))
        cases[case.case_id] = {
            "good_conforms": all(shacl([atomic.FIXTURES / name], shapes)[0] for name in good),
            "bad_fails": all(not shacl([atomic.FIXTURES / name], shapes)[0] for name in bad),
        }
    passes = (
        positive
        and all(negatives.values())
        and all(item["good_conforms"] and item["bad_fails"] for item in cases.values())
    )
    return {
        "composed_positive_conforms": positive,
        "composed_negatives_fail": negatives,
        "atomic": cases,
        "passes": passes,
    }


def memory_lab_commit():
    return {
        "head": git(ROOT, "rev-parse", "HEAD"),
        "working_tree_dirty": bool(git(ROOT, "status", "--porcelain")),
    }


def main():
    parser = argparse.ArgumentParser(description="Map Memory Lab obligations onto GEI SHACL.")
    parser.add_argument("--gei", required=True, help="path to a governed-intelligence-ecology checkout")
    parser.add_argument("--expectations", default=EXPECTATIONS.name, help="expectations file in this experiment")
    args = parser.parse_args()
    gei = pathlib.Path(args.gei).resolve()
    expectations_file = HERE / args.expectations
    expectations = json.loads(expectations_file.read_text(encoding="utf-8"))
    candidates = {**DEFAULT_CANDIDATES, **expectations.get("candidates", {})}
    candidate_invalidation = resolve(candidates["invalidation"], gei)
    candidate_st007 = resolve(candidates["st007_narrowed"], gei)

    def replace_st007(paths):
        return [candidate_st007 if path.name == GEI_ST007 else path for path in paths]

    def add_invalidation(paths):
        return list(paths) + [candidate_invalidation]

    commit = git(gei, "rev-parse", "HEAD")
    if commit != expectations["gei"]["commit"]:
        raise SystemExit(f"GEI checkout is at {commit}, expected {expectations['gei']['commit']}")
    if git(gei, "status", "--porcelain"):
        raise SystemExit("GEI checkout has local changes; use a clean checkout")
    ml_commit = memory_lab_commit()

    ref = load_module(gei / "scripts" / "validate_reference_path.py", "gei_reference_path")
    atomic = load_module(gei / "scripts" / "validate_semantic_transitions.py", "gei_semantic_transitions")
    gei_shapes = [ref.SHAPES / name for name in ref.SHAPE_FILES]
    positives = [ref.FIXTURES / name for name in ref.POSITIVE_FILES]
    with_invalidation = add_invalidation(gei_shapes)
    with_narrowed = replace_st007(gei_shapes)

    baseline = subprocess.run(
        [sys.executable, "-B", "scripts/validate_semantics.py"],
        cwd=gei,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if git(gei, "status", "--porcelain"):
        raise SystemExit("GEI validation modified the checkout")

    overlays = {}
    for form in expectations["overlays"]:
        data = positives + [OVERLAYS / form["file"]]
        conforms, messages = shacl(data, gei_shapes)
        rejecting = [] if conforms else [shape.name for shape in gei_shapes if not shacl(data, [shape])[0]]
        overlays[form["file"]] = {
            "gei_conforms": conforms,
            "rejecting_gei_shape_files": rejecting,
            "messages": messages,
            "candidate_invalidation_conforms": shacl(data, with_invalidation)[0],
            "candidate_st007_narrowed_conforms": shacl(data, with_narrowed)[0],
        }

    internal = {}
    for check in expectations["gei_internal_checks"]:
        fixture = [gei / "semantics" / "fixtures" / check["fixture"]]
        shapes = [ref.SHAPES / name for name in check["shapes"]]
        internal[check["name"]] = {
            "conforms": shacl(fixture, shapes)[0],
            "conforms_with_st007_narrowed": shacl(fixture, replace_st007(shapes))[0],
        }

    results = {
        "experiment": "gei-conformance-v0",
        "status": "executed",
        "expectations_file": expectations_file.name,
        "candidates": candidates,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pyshacl": version("pyshacl"),
            "rdflib": version("rdflib"),
            "owlrl": version("owlrl"),
        },
        "gei": {
            "repository": expectations["gei"]["repository"],
            "commit": commit,
            "baseline_validate_semantics": {
                "exit": baseline.returncode,
                "final_line": (baseline.stdout.strip().splitlines() or [""])[-1],
            },
        },
        "memory_lab_commit": ml_commit,
        "overlays": overlays,
        "gei_internal_checks": internal,
        "noninterference": {
            "candidate_invalidation": noninterference(ref, atomic, with_invalidation, add_invalidation),
            "candidate_st007_narrowed": noninterference(ref, atomic, with_narrowed, replace_st007),
        },
    }
    results["predictions"] = prediction_checks(expectations, results)
    results["classification"] = classify_all(expectations, results)
    output = results_path(expectations)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"GEI {commit[:7]} baseline exit={baseline.returncode}; Memory Lab {ml_commit}")
    print(f"expectations {expectations_file.name}; candidates {candidates}")
    print(f"{'overlay':40} {'GEI':6} {'rejected by':36} {'+inval':7} {'st007n':7} prediction")
    for form in expectations["overlays"]:
        item = overlays[form["file"]]
        print(
            f"{form['file']:40} {str(item['gei_conforms']):6} "
            f"{','.join(item['rejecting_gei_shape_files']) or '-':36} "
            f"{str(item['candidate_invalidation_conforms']):7} "
            f"{str(item['candidate_st007_narrowed_conforms']):7} "
            f"{'held' if results['predictions'][form['file']]['held'] else 'FAILED'}"
        )
    for name, check in results["predictions"].items():
        if not name.endswith(".ttl"):
            print(f"{name}: {'held' if check['held'] else 'FAILED'} {check['observed']}")
    print(json.dumps(results["classification"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

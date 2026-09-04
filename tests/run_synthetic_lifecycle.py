#!/usr/bin/env python3
import hashlib
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "fixtures" / "synthetic-lifecycle"
CONTRACT_PATH = ROOT / "schemas" / "legacy-chunk-contract-v1.json"
MIGRATION_STATUS_PATH = ROOT / "docs" / "script-migration-status.json"


def read_text(path):
    return path.read_text(encoding="utf-8")


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(corpus_path):
    files = {}
    for path in sorted(corpus_path.rglob("*.md")):
        rel = path.relative_to(corpus_path).as_posix()
        files[rel] = {
            "sha256": file_digest(path),
            "bytes": path.stat().st_size,
        }

    core = {
        "schema": "synthetic-source-snapshot-v1",
        "files": files,
    }
    encoded = json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "snapshot_id": "SYN-" + hashlib.sha256(encoded).hexdigest()[:16],
        **core,
    }


def classify_delta(left, right):
    left_files = left["files"]
    right_files = right["files"]
    left_names = set(left_files)
    right_names = set(right_files)
    common = left_names & right_names
    return {
        "added": sorted(right_names - left_names),
        "deleted": sorted(left_names - right_names),
        "changed": sorted(
            name for name in common if left_files[name]["sha256"] != right_files[name]["sha256"]
        ),
        "unchanged": sorted(
            name for name in common if left_files[name]["sha256"] == right_files[name]["sha256"]
        ),
    }


def legacy_source_path(path):
    return pathlib.PureWindowsPath(path).as_posix().replace("/", "\\")


def legacy_chunk_id(source, start_line, subchunk_index=None):
    if subchunk_index is None:
        payload = f"{source}:{start_line}"
    else:
        payload = f"{source}:{start_line}:{subchunk_index}"
    return hashlib.md5(payload.encode("utf-8")).hexdigest()[:12]


def heading_chunks(corpus_path):
    records = []
    for path in sorted(corpus_path.rglob("*.md")):
        rel = path.relative_to(corpus_path).as_posix()
        source = legacy_source_path(rel)
        lines = read_text(path).splitlines()
        starts = [idx for idx, line in enumerate(lines) if line.startswith("#")]
        if not starts:
            starts = [0]
        for offset, start in enumerate(starts):
            end = starts[offset + 1] if offset + 1 < len(starts) else len(lines)
            text = "\n".join(lines[start:end]).strip()
            heading = lines[start].lstrip("#").strip() if lines[start].startswith("#") else ""
            records.append(
                {
                    "id": legacy_chunk_id(source, start),
                    "source": source,
                    "start_line": start,
                    "heading": heading,
                    "document_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                }
            )
    return records


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(condition, label):
    if not condition:
        raise AssertionError(label)


def main():
    states = {name: snapshot(FIXTURE_ROOT / name) for name in ["S0", "S1", "S2", "S3", "S4"]}
    deltas = {
        "S0->S1": classify_delta(states["S0"], states["S1"]),
        "S1->S2": classify_delta(states["S1"], states["S2"]),
        "S2->S3": classify_delta(states["S2"], states["S3"]),
        "S3->S4": classify_delta(states["S3"], states["S4"]),
    }

    assert_equal(deltas["S0->S1"]["added"], ["foxtrot-added.md"], "ADD classification")
    assert_equal(deltas["S1->S2"]["changed"], ["charlie-expand.md"], "expansion CHANGE")
    assert_equal(deltas["S2->S3"]["changed"], ["delta-contract.md"], "contraction CHANGE")
    assert_equal(deltas["S3->S4"]["deleted"], ["foxtrot-added.md"], "DELETE classification")
    assert_equal(states["S4"]["snapshot_id"], states["S0"]["snapshot_id"], "round-trip snapshot")
    assert_equal(states["S4"]["files"], states["S0"]["files"], "round-trip source files")

    baseline_records = heading_chunks(FIXTURE_ROOT / "S0")
    final_records = heading_chunks(FIXTURE_ROOT / "S4")
    assert_equal(final_records, baseline_records, "round-trip logical chunk records")
    assert_true(
        any(record["source"] == "bravo-multi.md" and record["start_line"] == 4 for record in baseline_records),
        "zero-based heading start_line was exercised",
    )
    assert_true(
        any(record["source"] == "folder\\golf-nested.md" for record in baseline_records),
        "Windows-style nested relative source identity was exercised",
    )

    contract = json.loads(read_text(CONTRACT_PATH))
    assert_equal(contract["contract"], "legacy-chunk-contract-v1", "legacy contract name")
    assert_equal(contract["source_identity"]["start_line_base"], 0, "legacy start line base")
    assert_equal(contract["chunk_ids"]["unsplit"], "MD5(<file_rel>:<start_line>)[:12]", "legacy ID rule")

    migration_status = json.loads(read_text(MIGRATION_STATUS_PATH))
    script_states = {entry["script"]: entry["state"] for entry in migration_status["scripts"]}
    assert_equal(
        script_states["build_source_snapshot.py"],
        "validated_local_pending_import",
        "missing validated imports stay pending",
    )
    assert_equal(
        script_states["audit_roundtrip_logical_equivalence.py"],
        "validated_local_pending_import",
        "roundtrip audit stays pending",
    )
    assert_equal(
        script_states["tests/run_synthetic_lifecycle.py"],
        "synthetic_reimplementation",
        "synthetic runner is explicitly labeled",
    )

    contaminated_state = {
        "state_snapshot": states["S1"]["snapshot_id"],
        "plan_from_snapshot": states["S0"]["snapshot_id"],
        "pending_journal_exists": True,
    }
    assert_true(
        contaminated_state["state_snapshot"] != contaminated_state["plan_from_snapshot"]
        and contaminated_state["pending_journal_exists"],
        "contaminated state is detectable and must fail closed in integration",
    )

    report = {
        "status": "passed",
        "mode": "environment-independent",
        "snapshots": {name: state["snapshot_id"] for name, state in states.items()},
        "deltas": deltas,
        "baseline_logical_records": len(baseline_records),
        "final_logical_records": len(final_records),
        "integration_tests": "pending exact validated script imports and Chroma/embedding runtime",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"SYNTHETIC_LIFECYCLE_FAIL: {exc}", file=sys.stderr)
        raise

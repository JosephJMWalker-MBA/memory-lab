# graphiti-conflict-v0

This experiment runs a live substitution test of `derived-conflict-v0` (Polaris) against `graphiti-core==0.30.2`.

Results and interpretation live in `docs/graphiti-substitution-v0.md`.

## Layout

| Path | Role |
|---|---|
| `../../tests/run_graphiti_adapter_v0.py` | Memory Lab-owned translation, read-only admission projection, and ML-EP-0 conformance checks. Runs in `make test` / CI **without** Graphiti, and verifies the recorded evidence below |
| `run_graphiti_live.py` | Exercises Graphiti's own code on embedded Kuzu and writes the evidence file |
| `requirements.txt` | Pinned environment for the live runner only |
| `results/graphiti-conflict-v0.observed.json` | Recorded evidence: environment, Graphiti source anchors, before/after edge states, scripted verdicts, LLM calls, admission, and conformance for every scenario |

## Reproduce

```bash
python3 -m venv .venv-graphiti
```

```bash
.venv-graphiti/bin/pip install -r experiments/graphiti-conflict-v0/requirements.txt
```

```bash
.venv-graphiti/bin/python experiments/graphiti-conflict-v0/run_graphiti_live.py
```

```bash
python3 tests/run_graphiti_adapter_v0.py
```

The adapter test recomputes every recorded conformance verdict and admission projection from the recorded states. It fails if they disagree.

`make graphiti-live` runs the live runner with whatever `python3` is on `PATH`, so activate the venv first. The runner rewrites the evidence file on every run. `expired_at` values and `run_at` change between runs; the verdicts and outcomes should not.

## What the live runner does and does not do

- It sets `GRAPHITI_TELEMETRY_ENABLED=false` before importing Graphiti.
- It uses no LLM. The contradiction verdict (`dedupe_edges.resolve_edge`) is scripted, and any other LLM call raises.
- It uses no embedder. Embeddings are null and Graphiti search is not exercised; contradiction candidate sets are supplied directly.
- It writes Polaris directly with Graphiti's node and edge `save` methods. It then exercises:
  - `resolve_extracted_edge`: fast path, verdict handling, attribute handling, "born expired" rule, `resolve_edge_contradictions`;
  - `Graphiti.remove_episode`.

## Extending to a real LLM backend

This has not been done. The steps would be:

1. Replace `ScriptedVerdictLLM` with a Graphiti LLM client.
2. Replace `KuzuDriver` with `Neo4jDriver` or `FalkorDriver`.
3. Ingest the fixture evidence through `add_episode`, so Graphiti's own extraction, search, and candidate selection run.

Keep the Memory Lab adapter and conformance checks unchanged. Record provider, model id, and configuration in the evidence file. Report verdict rates over repeated runs, not a single run.

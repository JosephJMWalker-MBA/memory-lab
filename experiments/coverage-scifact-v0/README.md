# coverage-scifact-v0

This is the preregistered test of whether an explicit evidence-coverage state changes claim-verification decisions beyond provenance plus retrieval metrics (issue #12).

- Protocol: `PREREGISTRATION.md`, committed before any arm ran.
- Results and interpretation: `docs/coverage-scifact-v0.md`.

## Layout

| Path | Role |
|---|---|
| `PREREGISTRATION.md` | The protocol, fixed before the run |
| `fetch_scifact.py` | Downloads the SciFact release into `data/` (gitignored) and verifies its size and SHA-256 |
| `run_coverage_scifact.py` | Retrieval (stdlib BM25 and sentence-level TF-IDF) plus the run. Writes the results file |
| `results/coverage-scifact-v0.results.json` | Environment, data hashes and licenses, parameters, per-k aggregates, predictions, bootstrap, and per-claim records |
| `../../tests/run_coverage_scifact_v0.py` | Memory Lab-owned logic: decision rules, REC coverage state, arms, scoring. Runs in `make test` and CI without the data, and recomputes everything in the results file |

## Reproduce

```bash
python3 experiments/coverage-scifact-v0/fetch_scifact.py
```

```bash
python3 experiments/coverage-scifact-v0/run_coverage_scifact.py
```

```bash
python3 tests/run_coverage_scifact_v0.py
```

The run uses only the Python standard library and takes a few seconds. `run_at` changes between runs; nothing else should.

## Data, licenses, attribution

- **Source:** `https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz`
  - size: 3,115,079 bytes
  - SHA-256: `11c621288d41ac144d29b13b0f8503b3820b7d6e8b1f6ff24dff335c196d76be`
- **Licenses,** from the upstream `LICENSE.md` in `allenai/scifact`:
  - claims and evidence annotations: CC BY 4.0;
  - corpus abstracts (from S2ORC): ODC-By 1.0.
  - The Hugging Face card for `allenai/scifact` lists `cc-by-nc-2.0`. That conflicts with the upstream license; the upstream license governs.
- **What this repository records:**
  - recorded: claim ids, collection truth, evidence abstract ids with their labels, and top-20 ranked abstract ids with scores;
  - not recorded: any claim text or abstract text;
  - not redistributed: the data files themselves.
- **Attribution:** David Wadden, Shanchuan Lin, Kyle Lo, Lucy Lu Wang, Madeleine van Zuylen, Arman Cohan, Hannaneh Hajishirzi. *Fact or Fiction: Verifying Scientific Claims.* EMNLP 2020.

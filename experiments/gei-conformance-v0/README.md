# gei-conformance-v0

This experiment maps Memory Lab obligations O1–O8 onto GEI's existing SHACL conformance machinery (issue #15). GEI itself is not modified.

- **Results and interpretation:** `docs/gei-conformance-mapping-v0.md`.
- **Protocol:** `expectations.json`, fixed before any SHACL run (commit `0dd7d4a`).

| File | Content |
|---|---|
| `expectations.json` | GEI commit and processor options; the classification rule; each obligation's GEI contract citations and contract gaps; each overlay's predictions and declared checkability; predicted obligation classes |
| `overlays/*.ttl` | 17 hand-authored exports: 14 violation forms (11 motivating) and 3 capability forms. Each is mapped from a failure or capability observed in #11, #12, or #13 |
| `candidate/prov-invalidation-provenance.shacl.ttl` | Candidate A. Additive; SHACL Core; existing terms only. Not GEI text |
| `candidate/st-007-narrowed.shacl.ttl` | Candidate B. GEI's ST-007 constraints behind an `sh:or` guard that applies them only to coverage revisions. Replaces ST-007 in one run only. Not GEI text |
| `run_gei_mapping.py` | The runner |
| `results/gei-conformance-v0.results.json` | Environment; GEI's own baseline run; per-overlay outcomes, rejecting shape files, and messages; non-interference; prediction checks; classification |
| `requirements.txt` | The pinned environment (pySHACL pinned as in GEI's `requirements-semantic.txt`) |
| `expectations-gei-efeb1ba.json` | Rerun predictions for GEI Round 66 (`efeb1ba`, GEI PR #2). Derived from `expectations.json`; candidate A is GEI's own opt-in profile shape |
| `results/gei-conformance-v0-gei-efeb1ba.results.json` | The recorded rerun |

## Run

Set up an isolated environment:

```bash
python3 -m venv .venv-gei
.venv-gei/bin/pip install -r experiments/gei-conformance-v0/requirements.txt
```

Check out GEI at the pinned commit:

```bash
git clone https://github.com/JosephJMWalker-MBA/governed-intelligence-ecology /path/to/gei
git -C /path/to/gei checkout 4dd69ff2119ea34a7ea791c85bf9185c65263bb3
```

Run the mapping:

```bash
.venv-gei/bin/python experiments/gei-conformance-v0/run_gei_mapping.py --gei /path/to/gei
```

To rerun against a later GEI commit, check that commit out and pass its expectations file:

```bash
.venv-gei/bin/python experiments/gei-conformance-v0/run_gei_mapping.py --gei /path/to/gei --expectations expectations-gei-efeb1ba.json
```

The equivalent Make target is `make gei-mapping GEI=/path/to/gei`, but it calls `python3`, so the pinned environment must be active.

The runner:

- refuses a GEI checkout at any other commit, or with local changes;
- writes nothing into the GEI checkout;
- also runs GEI's own `scripts/validate_semantics.py` and records the result.

`python3 tests/run_gei_mapping_v0.py` runs in `make test` and CI and needs no RDF libraries. It checks the classification rule and the expectations file. It then re-derives every prediction check and every class from the recorded results.

## Run log

1. **`0dd7d4a`:** the protocol was committed.
2. **First run: crashed.** Importing GEI's `validate_semantic_transitions.py` failed before any validation ran: its dataclasses need the module registered in `sys.modules`. Fixed in `226c8aa`.
3. **Second run: stopped by the clean-checkout guard.** The first import had written two `.pyc` files into the GEI clone's `scripts/__pycache__`. They were removed, and `cab806d` disables bytecode writing.
4. **Third run: recorded.** At `cab806d`, with a clean tree. It took 82 s on macOS arm64 with Python 3.13.5.
5. **Rerun against GEI Round 66: recorded.** At `b9db0a5`, with a clean tree, against GEI `efeb1ba` (GEI PR #2). All 20 prediction checks held, and GEI's own suite exited 0. Before this run, `a61ddd2` let the runner take one expectations file per GEI commit.

None of the fixes changed an overlay, a candidate, or a prediction.

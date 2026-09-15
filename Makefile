.PHONY: test graphiti-live gei-mapping

test:
	python3 tests/run_synthetic_lifecycle.py
	python3 tests/run_failure_semantics.py
	python3 tests/run_contract_schema_validation.py
	python3 tests/run_derived_memory_v0.py
	python3 tests/run_derived_memory_adversarial.py
	python3 tests/run_derived_reassessment_v0.py
	python3 tests/run_multiple_justifications_v0.py
	python3 tests/run_derived_conflict_v0.py
	python3 tests/run_graphiti_adapter_v0.py
	python3 tests/run_appstate_baseline_v0.py
	python3 tests/run_coverage_scifact_v0.py
	python3 tests/run_gei_mapping_v0.py

# Requires the pinned environment in experiments/graphiti-conflict-v0/requirements.txt.
graphiti-live:
	python3 experiments/graphiti-conflict-v0/run_graphiti_live.py

# Requires the pinned environment in experiments/gei-conformance-v0/requirements.txt
# and a clean GEI checkout at the commit pinned in its expectations.json.
gei-mapping:
	python3 experiments/gei-conformance-v0/run_gei_mapping.py --gei $(GEI)

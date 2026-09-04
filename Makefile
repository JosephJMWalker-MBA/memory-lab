.PHONY: test

test:
	python3 tests/run_synthetic_lifecycle.py
	python3 tests/run_failure_semantics.py
	python3 tests/run_contract_schema_validation.py
	python3 tests/run_derived_memory_v0.py
	python3 tests/run_derived_memory_adversarial.py
	python3 tests/run_derived_reassessment_v0.py
	python3 tests/run_multiple_justifications_v0.py

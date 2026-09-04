.PHONY: test

test:
	python3 tests/run_synthetic_lifecycle.py
	python3 tests/run_failure_semantics.py

export PYTHONPATH ?= .

.PHONY: test

test:
	py.test --doctest-modules

ci:
	flake8 thrall -v

coverage:
	py.test --cov-config .coveragerc --verbose --cov=thrall tests

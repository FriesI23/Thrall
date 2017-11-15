export PYTHONPATH ?= .

.PHONY: init test ci cov benckmark clean build

init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock

test:
	pipenv run tox -epy27 -epy36

ci:
	pipenv run flake8 thrall --verbose

cov:
	pipenv run py.test --doctest-module --cov-config .coveragerc --verbose --cov=thrall

benckmark:
	pipenv run py.test  --pyargs benchmarks

clean:
	rm -rf dist build

build: test clean
	python setup.py sdist bdist_wheel
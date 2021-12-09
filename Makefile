.DEFAULT: help
.PHONY: help bootstrap build fmt lint test testcov mypy outdated upload clean

VENV = .venv
PYTHON = $(VENV)/bin/python

help:
	@echo "Please use \`$(MAKE) <target>' where <target> is one of the following:"
	@echo "  help        - show help information"
	@echo "  bootstrap   - setup packaging dependencies and initialize venv"
	@echo "  build       - build project packages"
	@echo "  fmt         - format source code according to project conventions"
	@echo "  lint        - inspect project source code for errors"
	@echo "  mypy        - run type checking with mypy"
	@echo "  outdated    - list outdated project requirements"
	@echo "  test        - run project tests"
	@echo "  testcov     - project test coverage reports"
	@echo "  upload      - upload built packages to package repository"
	@echo "  clean       - clean up project environment and all the build artifacts"

bootstrap: $(VENV)/bin/activate
$(VENV)/bin/activate:
	python3.9 -m venv $(VENV)
	$(PYTHON) -m pip install -U pip==21.3.1 setuptools==59.4.0 wheel==0.37.0
	$(PYTHON) -m pip install -e .[dev,doc,test]

build: bootstrap
	$(PYTHON) setup.py sdist bdist_wheel

fmt: bootstrap
	$(PYTHON) -m isort arku tests
	$(PYTHON) -m black -S -l 120 arku tests

lint: bootstrap
	$(PYTHON) -m flake8 arku/ tests/
	$(PYTHON) -m isort arku tests --check-only --df
	$(PYTHON) -m black -S -l 120 arku tests --check

mypy: bootstrap
	$(PYTHON) -m mypy arku

outdated: bootstrap
	$(PYTHON) -m pip list --outdated --format=columns

test: bootstrap
	$(PYTHON) -m pytest --cov=arku

testcov: test
	$(PYTHON) -m coverage html
	$(PYTHON) -m coverage xml

upload: build
	$(PYTHON) -m twine upload dist/*

clean:
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info .eggs
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build dist
	make -C docs clean
	rm -rf $(VENV)

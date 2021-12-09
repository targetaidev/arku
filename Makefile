.DEFAULT_GOAL := all

VENV = .venv
PYTHON = $(VENV)/bin/python

.PHONY: bootstrap
bootstrap: $(VENV)/bin/activate
$(VENV)/bin/activate:
	python3.9 -m venv $(VENV)
	$(PYTHON) -m pip install -U pip==21.3.1 setuptools==59.4.0 wheel==0.37.0
	$(PYTHON) -m pip install -e .[dev,doc,test]

build: bootstrap
	$(PYTHON) setup.py sdist bdist_wheel

upload: build
	$(PYTHON) -m twine upload dist/*

.PHONY: format
format: bootstrap
	$(PYTHON) -m isort arq tests
	$(PYTHON) -m black -S -l 120 arq tests

.PHONY: lint
lint: bootstrap
	$(PYTHON) -m flake8 arq/ tests/
	$(PYTHON) -m isort arq tests --check-only --df
	$(PYTHON) -m black -S -l 120 arq tests --check

.PHONY: test
test: bootstrap
	$(PYTHON) -m pytest --cov=arq

.PHONY: testcov
testcov: test
	@echo "building coverage html and xml"
	$(PYTHON) -m coverage html
	$(PYTHON) -m coverage xml

.PHONY: mypy
mypy: bootstrap
	$(PYTHON) -m mypy arq

.PHONY: all
all: lint mypy testcov

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
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

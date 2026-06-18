PYTHON ?= python

.PHONY: install test lint build check

install:
	$(PYTHON) -m pip install -e .[dev]

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

build:
	$(PYTHON) -m build

check:
	$(PYTHON) -m compileall src tests
	$(PYTHON) -m ruff check .
	$(PYTHON) -m pytest
	$(PYTHON) -m build

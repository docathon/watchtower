PYTHON ?= python
PYTEST ?= pytest


all: clean inplace test

clean-ctags:
	rm -f tags

clean: clean-ctags
	$(PYTHON) setup.py clean
	rm -rf dist

in: inplace # just a shortcut
inplace:
	$(PYTHON) setup.py build_ext -i

test-code: in
	$(PYTEST) --showlocals -v watchtower --durations=20

test-doc:
	#$(PYTEST) $(shell find doc -name '*.rst' | sort)

test-coverage:
	rm -rf coverage .coverage
	$(PYTEST) watchtower --showlocals -v --cov=watchtower --cov-report=html:coverage

test: test-code test-doc


doc: inplace
	$(MAKE) -C doc html

flake8-diff:
	./build_tools/travis/flake8_diff.sh


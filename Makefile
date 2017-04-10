PYTHON ?= python
CYTHON ?= cython
NOSETESTS ?= nosetests
CTAGS ?= ctags

all: test

in: inplace

inplace:	

test: test-code

test-code: in
	$(NOSETESTS) -s -v watchtower

test-coverage:
	rm -rf coverage .coverage
	$(NOSETESTS) -s -v --with-coverage --cover-package=watchtower watchtower

flake:
	@if command -v flake8 > /dev/null; then \
		echo "Running flake8"; \
		flake8 --count watchtower examples; \
	else \
		echo "flake8 not found, please install it!"; \
		exit 1; \
	fi;
	@echo "flake8 passed"
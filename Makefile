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

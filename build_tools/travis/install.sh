#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.

# License: 3-clause BSD
  

set -e
pip install doctr sphinx numpydoc pillow matplotlib numpy pandas
pip install sphinx_gallery
pip install pytest


if [[ "$COVERAGE" == "true" ]]; then
    pip install pytest-cov codecov
fi

# Build watchtower in the install.sh script to collapse the verbose
# build output in the travis output when it succeeds.
python --version
python -c "import numpy; print('numpy %s' % numpy.__version__)"
python -c "import pandas; print('pandas %s' % pandas.__version__)"

python setup.py develop

if [[ "$RUN_FLAKE8" == "true" ]]; then
    # flake8 version is temporarily set to 2.5.1 because the next
    # version available on conda (3.3.0) has a bug that checks non
    # python files and cause non meaningful flake8 errors
    pip install flake8==2.5.1
fi


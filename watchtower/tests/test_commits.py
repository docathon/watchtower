import os
from os.path import dirname
import tempfile

import pandas as pd
from watchtower.commits_ import is_doc
from watchtower._config import clear_data_home
from watchtower.commits_ import load_commits
from watchtower.datasets import _fake_datasets
from watchtower.utils.testing import assert_true, assert_equal
from watchtower.utils.testing import assert_false

DATA_HOME = tempfile.mkdtemp(prefix="watchtower_data_home_test_")


def test_is_doc():
    # FIXME
    return
    # First, create scratch commit as panda's dataframe.
    commit = pd.DataFrame({"message": "DOC improved documentation",
                           "added": ["doc/module.rst"]})
    is_doc_ = is_doc(commit)
    assert_true(is_doc_.all())

    commit = pd.DataFrame({"message": "ENH added super cool feature",
                           "added": ["watchtower/commits.py"]})
    is_doc_ = is_doc(commit)
    assert_false(is_doc_.any())


def test_load_commits():
    commits = load_commits("matplotlib", "matplotlib", data_home=DATA_HOME)
    clear_data_home(data_home=DATA_HOME)
    assert_equal(commits, None)

    # Now use some mockdata
    data_home = _fake_datasets.get_mock_directory_path()
    commits = load_commits("matplotlib", "matplotlib", data_home=data_home)
    assert_true(len(commits) == 3)

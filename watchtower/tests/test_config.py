import os
from os.path import dirname
import tempfile

from watchtower._config import get_data_home, clear_data_home
from watchtower._config import get_issues, get_commits, get_PRs

from watchtower.utils.testing import assert_true, assert_false
from watchtower.utils.testing import assert_equal


DATA_HOME = tempfile.mkdtemp(prefix="watchtower_data_home_test_")


def test_data_home():
    # get_data_home will point to a pre-existing folder
    data_home = get_data_home(data_home=DATA_HOME)
    assert_equal(data_home, DATA_HOME)
    assert_true(os.path.exists(data_home))

    # clear_data_home will delete both the content and the folder it-self
    clear_data_home(data_home=data_home)
    assert_false(os.path.exists(data_home))

    # if the folder is missing it will be created again
    data_home = get_data_home(data_home=DATA_HOME)
    assert_true(os.path.exists(data_home))


def test_get_issues():
    issues = get_issues("matplotlib", "matplotlib", data_home=DATA_HOME)
    clear_data_home(data_home=DATA_HOME)
    assert_equal(issues, None)

    # Now use some mockdata
    data_home = os.path.join(dirname(__file__), "../mockdata")
    issues = get_issues("matplotlib", "matplotlib", data_home=data_home)
    assert_true(len(issues) == 11)


def test_get_commits():
    commits = get_commits("matplotlib", "matplotlib", data_home=DATA_HOME)
    clear_data_home(data_home=DATA_HOME)
    assert_equal(commits, None)

    # Now use some mockdata
    data_home = os.path.join(dirname(__file__), "../mockdata")
    commits = get_commits("matplotlib", "matplotlib", data_home=data_home)
    assert_true(len(commits) == 3)


def test_get_PRs():
    PRs = get_PRs("matplotlib", "matplotlib", data_home=DATA_HOME)
    clear_data_home(data_home=DATA_HOME)
    assert_equal(PRs, None)

    # Now use some mockdata
    data_home = os.path.join(dirname(__file__), "../mockdata")
    PRs = get_PRs("matplotlib", "matplotlib", data_home=data_home)
    assert_true(len(PRs) == 21)

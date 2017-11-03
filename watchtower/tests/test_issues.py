import os
from os.path import dirname
import tempfile
from watchtower._config import clear_data_home
from watchtower.issues_ import load_issues
#, get_PRs
from watchtower.utils.testing import assert_true, assert_equal

DATA_HOME = tempfile.mkdtemp(prefix="watchtower_data_home_test_")


def test_load_issues():
    issues = load_issues("matplotlib", "matplotlib", data_home=DATA_HOME)
    clear_data_home(data_home=DATA_HOME)
    assert_equal(issues, None)

    # Now use some mockdata
    data_home = os.path.join(dirname(__file__), "../mockdata")
    issues = load_issues("matplotlib", "matplotlib", data_home=data_home)
    assert_true(len(issues) == 32)


#def test_get_PRs():
#    PRs = get_PRs("matplotlib", "matplotlib", data_home=DATA_HOME)
#    clear_data_home(data_home=DATA_HOME)
#    assert_equal(PRs, None)
#
#    # Now use some mockdata
#    data_home = os.path.join(dirname(__file__), "../mockdata")
#    PRs = get_PRs("matplotlib", "matplotlib", data_home=data_home)
#    assert_true(len(PRs) == 21)

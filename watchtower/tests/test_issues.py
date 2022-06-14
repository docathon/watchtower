import tempfile
from watchtower._config import clear_data_home
from watchtower.issues_ import load_issues, extract_ticket_number
from watchtower.issues_ import estimate_date_since_last_update
from watchtower.utils.testing import assert_true, assert_equal
from watchtower.datasets import _fake_datasets

DATA_HOME = tempfile.mkdtemp(prefix="watchtower_data_home_test_")


def test_load_issues():
    issues = load_issues("matplotlib", "matplotlib", data_home=DATA_HOME)
    clear_data_home(data_home=DATA_HOME)
    assert_equal(issues, None)

    # Now use some mockdata
    data_home = _fake_datasets.get_mock_directory_path()
    issues = load_issues("matplotlib", "matplotlib", data_home=data_home)
    assert_true(len(issues) == 32)


def test_extract_ticket_number():
    data_home = _fake_datasets.get_mock_directory_path()
    issues = load_issues("matplotlib", "matplotlib", data_home=data_home)
    ticket_numbers = extract_ticket_number(issues)
    assert_equal(min(ticket_numbers), 7272)
    assert_equal(max(ticket_numbers), 7303)

    assert_true(len(extract_ticket_number(issues)), 32)


def test_estimate_date_since_last_update():
    data_home = _fake_datasets.get_mock_directory_path()
    issues = load_issues("matplotlib", "matplotlib", data_home=data_home)
    assert estimate_date_since_last_update(issues) is None

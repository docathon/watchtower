import os
from os import environ
import tempfile

from watchtower._config import get_data_home, clear_data_home, get_API_token

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


def test_get_API_token():
    if "WATCHTOWER_TEST" not in environ:
        environ["WATCHTOWER_TEST"] = "username:my_secret_key"

        api_token = get_API_token(token_key="WATCHTOWER_TEST")
        assert api_token == "username:my_secret_key"
        del environ["WATCHTOWER_TEST"]

    # No API token:
    api_token = get_API_token(token_key="LBDPCBAZLZBE")
    assert api_token is None

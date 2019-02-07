from watchtower._github_api import get_frames
import pytest


def test_get_frames():
    # Test that the code raises a warning when authentifaction is wrong
    auth = ("username", "password")
    url = "https://api.github.com/repos/matplotlib/matplotlib/commits"
    with pytest.warns(UserWarning):
        get_frames(auth, url)

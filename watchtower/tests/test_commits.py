import pandas as pd
from watchtower.commits import is_doc
from watchtower.utils.testing import assert_true, assert_false


def test_is_doc():
    # First, create scratch commit as panda's dataframe.
    commit = pd.DataFrame({"message": "DOC improved documentation",
                           "added": ["doc/module.rst"]})
    is_doc_ = is_doc(commit)
    assert_true(is_doc_.all())

    commit = pd.DataFrame({"message": "ENH added super cool feature",
                           "added": ["watchtower/commits.py"]})
    is_doc_ = is_doc(commit)
    assert_false(is_doc_.any())

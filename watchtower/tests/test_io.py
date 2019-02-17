import os
import tempfile

import numpy as np
import pandas as pd
from watchtower._io import _update_and_save
from watchtower.datasets._fake_datasets import get_fake_issues


def test_date_iso():
    issues = get_fake_issues()
    with tempfile.TemporaryDirectory() as tempdir:
        filename = os.path.join(tempdir, "issues.json")
        _update_and_save(filename, issues)

        old_issues = pd.read_json(filename)
        old_date = pd.datetime(1980, 1, 1)
        assert np.all(old_issues["created_at"] > old_date)

        _update_and_save(filename, issues, old_issues)
        issues = pd.read_json(filename)
        assert np.all(issues["created_at"] > old_date)

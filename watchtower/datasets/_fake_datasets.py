import json
import os
import pandas as pd


def get_fake_issues(format="dataframe"):
    filename = os.path.join(
        os.path.dirname(__file__), "data/test_tickets.json")
    with open(filename, "r") as f:
        issues = json.load(f)
    if format == "dataframe":
        return pd.DataFrame(issues)
    else:
        return issues


def get_mock_directory_path():
    filepath = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "data/mockdata"))
    return filepath

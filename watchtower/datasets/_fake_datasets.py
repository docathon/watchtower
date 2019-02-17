import json
import os
import pandas as pd


def get_fake_issues():
    filename = os.path.join(
        os.path.dirname(__file__), "data/test_tickets.json")
    with open(filename, "r") as f:
        issues = json.load(f)
    return pd.DataFrame(issues)

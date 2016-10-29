import os
import json
import pandas as pd

from . import _github_api
from ._config import get_data_home


def update_labels(user, project, auth, data_home=None):
    """
    Updates issues

    Parameters
    ----------

    user : string
        username or organization, e.g, "matplotlib"

    project : string
        project name, e.g., "matplotlib"

    auth : string
        authentification information, e.g. "username/token"

    state : {"all", "open", "closed"}, optional

    Returns
    -------
    raw : string containing all the issues
    """
    auth = _github_api.colon_seperated_pair(auth)
    url = 'https://api.github.com/repos/{}/{}/labels'.format(user, project)
    raw = _github_api.get_frames(auth, url)
    path = get_data_home(data_home=data_home)
    filename = os.path.join(path, user, project, "labels.json")
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    with open(filename, "w") as f:
        json.dump(raw, f)
    return pd.DataFrame(raw)


def get_labels(user, project, data_home=None):
    """
    Reads the labels json files from the data folder.

    Parameters
    ----------
    user : string
        user or organization name, e.g. "matplotlib"

    project : string
        project name, e.g, "matplotlib"

    Returns
    -------
    labels
    """
    data_home = get_data_home(data_home)
    filepath = os.path.join(data_home, user, project, "labels.json")
    try:
        commits = pd.read_json(filepath)
    except ValueError:
        return None
    return commits

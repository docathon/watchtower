import os
import json
import pandas as pd

from . import _github_api
from ._config import get_data_home


def update_labels(user, project, auth=None, data_home=None, verbose=False):
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

    data_home : string, optional

    verbose : boolean, default: False

    Returns
    -------
    raw : string containing all the issues
    """

    path = get_data_home(data_home=data_home)
    auth = get_API_token(auth) if auth is None else auth
    auth = _github_api.colon_seperated_pair(auth)
    api_root = 'https://api.github.com/'
    url = api_root + 'repos/{}/{}/labels?sha={}'.format(
        user, project)
    filename = os.path.join(path, 'projects', user, project,
                            "labels.json")
    # Pull latest activity info
    raw = _github_api.get_frames(auth, url,
                                 verbose=verbose,
                                 **params)
    raw = pd.DataFrame(raw)

    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    with open(filename, "w") as f:
        json.dump(raw, f)
    return pd.DataFrame(raw)


def load_labels(user, project, data_home=None):
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

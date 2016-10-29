import os
from os.path import join
import json

import pandas as pd

from . import _github_api
from ._config import get_data_home


def update_issues(user, project, auth, state="all", data_home=None):
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
    url = 'https://api.github.com/repos/{}/{}/issues'.format(user, project)
    raw = _github_api.get_frames(auth, url, state=state)
    path = get_data_home(data_home=data_home)
    filename = os.path.join(path, user, project, "issues.json")
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    with open(filename, "w") as f:
        json.dump(raw, f)
    return raw


def get_issues(project, user, data_home=None, issues_type="issues"):
    """
    Reads the json issues from the

    """
    # FIXME issues should be reloaded from time to time, as some are opened
    # and closed regularly. That's going to be a mess on large projects.
    # Maybe we could store premantly only the closed issues and update the
    # rest?
    data_home = get_data_home(data_home)
    filepath = join(data_home, user, project, "issues.json")
    try:
        issues = pd.read_json(filepath)
    except ValueError:
        return None

    issues.set_index("number", inplace=True)
    issues.sort_index(inplace=True)
    has_pr = -issues.pull_request.isnull()
    if issues_type == "issues":
        return issues[-has_pr]
    elif issues_type == "PRs":
        return issues[has_pr]
    elif issues_type == "all":
        return issues
    else:
        raise ValueError("%s is an unknown issue type. `issues_type` "
                         "can be 'issues', 'PRs' or 'all'")


def select_opened(issues):
    """
    Select opened issues

    Returns
    -------
    Opened issues
    """
    return issues[issues.state == "open"]


def select_recent(issues, num=20):
    """
    Select recent issues

    Parameters
    ----------
    issues : pd.DataFrame
        list of issues

    number : int, optional, default: 20
    """
    return issues.sort_values("updated_at")[:num]


def get_PRs(project, user, data_home=None):
    """
    Reads the json issues from the

    """
    return get_issues(project, user, data_home=data_home, issues_type="PRs")


def get_commits(user, project, data_home=None):
    """
    Reads the commits json files from the data folder.

    Parameters
    ----------
    user : string
        user or organization name, e.g. "matplotlib"

    project : string
        project name, e.g, "matplotlib"

    Returns
    -------
    commits
    """
    # XXX We need to sometime update that folder - how to do that?
    # XXX for some projects, that's going to get ugly…
    data_home = get_data_home(data_home)
    filepath = join(data_home, user, project, "commits.json")
    try:
        commits = pd.read_json(filepath)
    except ValueError:
        return None
    commits.sort_values("timestamp", inplace=True)
    return commits

import os
from os.path import join

import pandas as pd

from . import _github_api
from ._config import get_data_home, get_API_token
from .handlers_ import ProjectIssues


def update_issues(user, project, auth=None,
                  state="all", since=None, data_home=None):
    """
    Updates issues

    Parameters
    ----------

    user : string
        username or organization, e.g, "matplotlib"

    project : string
        project name, e.g., "matplotlib"

    auth : string | None
        authentification information, e.g. "username:token".
        If None, the key 'GITHUB_API'
        will be queried in `os.environ`.

    state : {"all", "open", "closed"}, optional

    Returns
    -------
    raw : string containing all the issues
    """
    auth = get_API_token(auth)
    auth = _github_api.colon_seperated_pair(auth)
    url = 'https://api.github.com/repos/{}/{}/issues'.format(user, project)
    raw = _github_api.get_frames(auth, url, state=state, since=since)
    path = get_data_home(data_home=data_home)
    raw = pd.DataFrame(raw)

    filename = os.path.join(path, 'projects', user, project, "issues.json")

    # Update pre-existing data
    old_raw = load_issues(user, project, data_home=data_home)
    if old_raw is not None:
        raw = pd.concat([raw, old_raw], ignore_index=True)
        raw = raw.drop_duplicates(subset=['id'])
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    raw.to_json(filename)
    return raw


def load_issues(user, project, data_home=None,
                use_handler=False):
    """
    Reads the json issues from the

    """
    # FIXME issues should be reloaded from time to time, as some are opened
    # and closed regularly. That's going to be a mess on large projects.
    # Maybe we could store premantly only the closed issues and update the
    # rest?
    data_home = get_data_home(data_home)
    filepath = join(data_home, 'projects', user, project, "issues.json")

    try:
        issues = pd.read_json(filepath)
    except ValueError:
        return None
    if use_handler is False:
        return issues
    else:
        return ProjectIssues(user, project, issues)


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
    return issues.sort_values("created_at")[:num]


def get_PRs(project, user, data_home=None):
    """
    Reads the json issues from the

    """
    return get_issues(project, user, data_home=data_home, issues_type="PRs")

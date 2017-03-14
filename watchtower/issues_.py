import os
from os.path import join

import pandas as pd

from . import _github_api
from ._config import get_data_home, get_API_token, DATETIME_FORMAT
from .handlers_ import ProjectIssues


def update_issues(user, project, auth=None,
                  state="all", since=None, data_home=None):
    """
    Updates the issues information for a user / project.

    Parameters
    ----------
    user : string
        user or organization name, e.g. "matplotlib"
    project : string
        project name, e.g, "matplotlib". If None, user
        information will be loaded.
    auth : string (user:api_key)
        The username / API key for github, separated by a colon. If
        None, the key `GITHUB_API` will be searched for in `environ`.
    state : 'all' | 'open' | 'closed'
        Whether to include only a subset, or all issues.
    since : string
        Search for activity since this date
    data_home : string
        The path to the watchtower data. Defaults to ~/watchtower_data.

    Returns
    -------
    raw : json
        The json string containing all the issue information
    """
    auth = get_API_token(auth)
    auth = _github_api.colon_seperated_pair(auth)
    url = 'https://api.github.com/repos/{}/{}/issues'.format(user, project)
    raw = _github_api.get_frames(auth, url, state=state, since=since)
    path = get_data_home(data_home=data_home)
    raw = pd.DataFrame(raw)
    raw = raw.rename(columns={'created_at': 'date'})

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
    raw.to_json(filename, date_format=DATETIME_FORMAT)
    return load_issues(user, project, data_home=data_home)


def load_issues(user, project, data_home=None,
                use_handler=False):
    """
    Reads the commits json files from the data folder.

    Parameters
    ----------
    user : string
        user or organization name, e.g. "matplotlib"
    project : string
        project name, e.g, "matplotlib". If None, user
        information will be loaded.
    data_home : string
        The path to the watchtower data. Defaults to ~/watchtower_data.
    use_handler : bool
        Whether to return data as one of the objects in
        `watchtower.handlers_`

    Returns
    -------
    issues : json | ProjectIssues
        The issues for this project / user.

    """
    # FIXME issues should be reloaded from time to time, as some are opened
    # and closed regularly. That's going to be a mess on large projects.
    # Maybe we could store premantly only the closed issues and update the
    # rest?
    data_home = get_data_home(data_home)
    filepath = join(data_home, 'projects', user, project, "issues.json")

    try:
        issues = pd.read_json(filepath)
        if len(issues) == 0:
            return None
        issues['date'] = pd.to_datetime(issues['date'].values)\
            .tz_localize('UTC')\
            .tz_convert('US/Pacific')
    except ValueError:
        return None
    if use_handler is False:
        return issues
    else:
        return ProjectIssues(user, project, issues)

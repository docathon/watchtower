"""
Some small configuration stuff.
"""

from os import environ
from os.path import join
from os.path import exists
from os.path import expanduser
from os import makedirs
import shutil

import pandas as pd


def get_data_home(data_home=None):
    """Return the path of the watchtower data dir.

    This folder is used by some large dataset loaders to avoid
    downloading the data several times.

    By default the data dir is set to a folder named 'scikit_learn_data'
    in the user home folder.

    Alternatively, it can be set by the 'WATCHTOWER_DATA' environment
    variable or programmatically by giving an explicit folder path. The
    '~' symbol is expanded to the user home folder.

    If the folder does not already exist, it is automatically created.

    Parameters
    ----------
    data_home : string, optional, default: None

    Returns
    -------
    data_home

    Notes
    -----
    This code is highly inspired by scikit-learn's
    """
    if data_home is None:
        data_home = environ.get('WATCHTOWER_DATA',
                                join('~', 'watchtower_data'))
    data_home = expanduser(data_home)
    if not exists(data_home):
        makedirs(data_home)
    return data_home


def clear_data_home(data_home=None):
    """
    Delete all the content of the data home cache.

    Parameters
    ----------
    data_home : string, optional, default: None

    Notes
    -----
    This code is highly inspired by scikit-learn's
    """
    data_home = get_data_home(data_home)
    shutil.rmtree(data_home)


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

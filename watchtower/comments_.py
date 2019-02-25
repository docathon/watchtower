import os
from os.path import join

import pandas as pd

from . import _github_api
from ._config import get_data_home, get_API_token
from ._io import _update_and_save


def update_comments(user, project, auth=None, state="all", since=None,
                    data_home=None, verbose=False,
                    direction="desc",
                    max_pages=100, per_page=500):
    """
    Updates the comments information for a user / project.

    Parameters
    ----------
    user : string
        user or organization name, e.g. "matplotlib"

    project : string
        project name, e.g, "matplotlib". If None, project will be set to
        user.

    auth : string (user:api_key)
        The username / API key for github, separated by a colon. If
        None, the key `GITHUB_API` will be searched for in `environ`.

    state : 'all' | 'open' | 'closed'
        Whether to include only a subset, or all comments.

    since : string
        Search for activity since this date

    direction : ["asc", "desc"]
        Whether to download oldest or newes comments first.

    data_home : string
        The path to the watchtower data. Defaults to ~/watchtower_data.

    verbose : bool
        Controls progress bar display.

    Returns
    -------
    raw : json
        The json string containing all the issue information
    """
    auth = get_API_token() if auth is None else auth
    auth = _github_api.colon_seperated_pair(auth)
    url = 'https://api.github.com/repos/{}/{}/issues/comments'.format(
        user, project)
    raw = _github_api.get_frames(auth, url, state=state, since=since,
                                 max_pages=max_pages, per_page=per_page,
                                 direction=direction,
                                 verbose=verbose)
    path = get_data_home(data_home=data_home)
    raw = pd.DataFrame(raw)

    if project is None:
        project = user
    filename = os.path.join(path, user, project, "comments.json")

    # Update pre-existing data
    old_raw = load_comments(user, project, data_home=data_home)
    _update_and_save(filename, raw, old_raw)
    if old_raw is not None:
        raw = pd.concat([raw, old_raw], ignore_index=True)
        raw = raw.drop_duplicates(subset=['id'])
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    raw.to_json(filename, date_format="iso")
    return load_comments(user, project, data_home=data_home)


def load_comments(user, project, data_home=None,
                  state="all"):
    """
    Reads the comments json files from the data folder.

    Parameters
    ----------
    user : string
        user or organization name, e.g. "matplotlib"

    project : string
        project name, e.g, "matplotlib".

    data_home : string
        The path to the watchtower data. Defaults to ~/watchtower_data.

    Returns
    -------
    comments : json | Projectcomments
        The comments for this project / user.

    """
    # FIXME comments should be reloaded from time to time, as some are opened
    # and closed regularly. That's going to be a mess on large projects.
    # Maybe we could store premantly only the closed comments and update the
    # rest?
    data_home = get_data_home(data_home)
    filepath = join(data_home, user, project, "comments.json")
    try:
        comments = pd.read_json(filepath)
        if len(comments) == 0:
            return None
    except ValueError:
        return None
    return comments

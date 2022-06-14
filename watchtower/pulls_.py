import os
from os.path import join

import pandas as pd
import numpy as np

from . import _github_api
from ._config import get_data_home, get_API_token
from ._io import _update_and_save, _save

from .issues_ import extract_ticket_number


def update_pulls(user, project, auth=None, state="all", since=None,
                 data_home=None, verbose=False, max_pages=100,
                 per_page=100, direction="asc"):
    """
    Updates the pulls information for a user / project.

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
        Whether to include only a subset, or all pulls.

    since : string
        Search for activity since this date

    data_home : string
        The path to the watchtower data. Defaults to ~/watchtower_data.

    verbose : bool
        Controls progress bar display.

    direction : string
        "asc" or "desc"

    Returns
    -------
    raw : json
        The json string containing all the issue information
    """
    auth = get_API_token() if auth is None else auth
    auth = _github_api.colon_seperated_pair(auth)
    url = 'https://api.github.com/repos/{}/{}/pulls'.format(user, project)
    raw = _github_api.get_frames(auth, url, state=state, since=since,
                                 max_pages=max_pages, per_page=per_page,
                                 direction=direction,
                                 verbose=verbose)
    path = get_data_home(data_home=data_home)
    raw = pd.DataFrame(raw)

    # Add a column called 'detailed_pulls' for when we add the extra
    # information.
    raw["detailed_pulls"] = None
    if verbose:
        ticket_ids = extract_ticket_number(raw)
        print("Downloaded pulls from %d to %d" % (
            min(ticket_ids),
            max(ticket_ids)))

    if project is None:
        project = user
    filename = os.path.join(path, user, project, "pulls.json")

    # Update pre-existing data
    old_raw = load_pulls(user, project, data_home=data_home)
    _update_and_save(filename, raw, old_raw)
    return load_pulls(user, project, data_home=data_home)


def update_detailed_pulls(user, project, auth=None, data_home=None,
                          verbose=False, max_download=None, redownload=True,
                          since=0):
    """
    Download detailed information on pulls

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

    max_download : integer, optional, default: None
        The maximum number of item to download.

    Returns
    -------

    """
    auth = get_API_token() if auth is None else auth
    auth = _github_api.colon_seperated_pair(auth)
    path = get_data_home(data_home=data_home)

    if project is None:
        project = user

    pulls = load_pulls(user, project, data_home=data_home)
    if max_download is None:
        max_download = len(pulls)

    current_download = 0

    if pulls is None:
        return None

    for i, pull in pulls.iterrows():
        if i < since:
            continue
        if (pull["detailed_pulls"] is None or pd.isna(pull["detailed_pulls"])
            or redownload):

            if verbose:
                print("Downloading detailed data from PR %d" % i)

            detailed_pull_url = pull["_links"]["self"]["href"]
            raw = _github_api.get_detailed_page(
                auth, detailed_pull_url)
            pulls.at[i, "detailed_pulls"] = raw

            current_download += 1
            if current_download == max_download:
                break

    filename = os.path.join(path, user, project, "pulls.json")

    _save(filename, pulls)
    return load_pulls(user, project, data_home=data_home)


def load_pulls(user, project, data_home=None,
               state="all"):
    """
    Reads the commits json files from the data folder.

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
    pulls : json | Projectpulls
        The pulls for this project / user.

    """
    # FIXME pulls should be reloaded from time to time, as some are opened
    # and closed regularly. That's going to be a mess on large projects.
    # Maybe we could store premantly only the closed pulls and update the
    # rest?
    data_home = get_data_home(data_home)
    filepath = join(data_home, user, project, "pulls.json")
    try:
        pulls = pd.read_json(filepath)
        if len(pulls) == 0:
            return None
    except ValueError:
        return None
    return pulls

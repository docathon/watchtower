import os
from os.path import join
import warnings

import pandas as pd
import numpy as np

from . import _github_api
from ._config import get_data_home, get_API_token
from ._io import _update_and_save


def update_issues(user, project, auth=None, state="all", since=None,
                  data_home=None, verbose=False, max_pages=100,
                  per_page=100, direction="asc"):
    """
    Updates the issues information for a user / project.

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
        Whether to include only a subset, or all issues.

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
    url = 'https://api.github.com/repos/{}/{}/issues'.format(user, project)
    raw = _github_api.get_frames(auth, url, state=state, since=since,
                                 max_pages=max_pages, per_page=per_page,
                                 direction=direction,
                                 verbose=verbose)
    path = get_data_home(data_home=data_home)
    raw = pd.DataFrame(raw)
    if verbose:
        ticket_ids = extract_ticket_number(raw)
        print("Downloaded tickets from %d to %d" % (
            min(ticket_ids),
            max(ticket_ids)))

    if project is None:
        project = user
    filename = os.path.join(path, user, project, "issues.json")

    # Update pre-existing data
    old_raw = load_issues(user, project, data_home=data_home)
    _update_and_save(filename, raw, old_raw)
    return load_issues(user, project, data_home=data_home)


def load_issues(user, project, data_home=None,
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
    issues : json | ProjectIssues
        The issues for this project / user.

    """
    # FIXME issues should be reloaded from time to time, as some are opened
    # and closed regularly. That's going to be a mess on large projects.
    # Maybe we could store premantly only the closed issues and update the
    # rest?
    data_home = get_data_home(data_home)
    filepath = join(data_home, user, project, "issues.json")
    try:
        issues = pd.read_json(filepath)
        if len(issues) == 0:
            return None
    except ValueError:
        return None
    return issues


def extract_ticket_number(tickets):
    """
    Extract ticket number

    Parameters
    ----------
    tickets : pd.DataFrame
        Pandas data frame containing the issues of interest.

    Returns
    -------
    ticket_ids
    """
    if tickets is None or not len(tickets):
        return np.array([0]).astype(int)
    if "html_url" not in tickets.columns:
        raise ValueError(
            "The provided DataFrame object doesn't contain"
            " the column html_url")
    ticket_ids = tickets["html_url"].apply(lambda x: x.split("/")[-1])
    return np.array(ticket_ids).astype(int)


def estimate_date_since_last_update(tickets):
    """
    """
    ticket_ids = extract_ticket_number(tickets)
    ticket_ids.sort()
    if len(ticket_ids) == 0:
        return None
    if min(ticket_ids) != 1:
        return None

    # Ok, so the first ticket is here. Now find the largest ID that is
    # contiguous
    number_missing_tickets = sum((ticket_ids[1:] - 1 - ticket_ids[:-1]) == 0)
    if number_missing_tickets != 0:
        warnings.warn("Some tickets may be missing")

    return max(tickets["created_at"]).isoformat()

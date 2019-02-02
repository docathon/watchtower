import os
from os.path import join

import pandas as pd
from collections.abc import Iterable

from . import _github_api
from ._config import get_data_home, get_API_token


def update_reviews(user, project, pull_request_ids, auth=None, since=None,
                   data_home=None, verbose=False, max_page=100, per_page=500):
    """
    Updates the reviews information for a user / project.

    Parameters
    ----------
    user : string
        user or organization name, e.g. "matplotlib"

    project : string
        project name, e.g, "matplotlib". If None, project will be set to
        user.

    pull_request_ids : int or list of ints
        ID of pull request

    auth : string (user:api_key)
        The username / API key for github, separated by a colon. If
        None, the key `GITHUB_API` will be searched for in `environ`.

    since : string
        Search for activity since this date

    data_home : string
        The path to the watchtower data. Defaults to ~/watchtower_data.

    verbose : bool
        Controls progress bar display.

    Returns
    -------
    raw : json
        The json string containing all the issue information
    """
    auth = get_API_token(auth)
    auth = _github_api.colon_seperated_pair(auth)
    if isinstance(pull_request_ids, Iterable):
        raw = []
        for pr_id in pull_request_ids:
            raw.append(_update_review_single(
                user, project, pr_id, auth=auth,
                verbose=verbose, max_page=max_page,
                per_page=per_page))
        raw = pd.concat(raw)
    else:
        raw = _update_review_single(
                user, project, pull_request_ids, auth=auth,
                verbose=verbose, max_page=max_page,
                per_page=per_page)
    path = get_data_home(data_home=data_home)

    if project is None:
        project = user
    filename = os.path.join(path, user, project, "reviews.json")

    # Update pre-existing data
    old_raw = load_reviews(user, project, data_home=data_home)
    if old_raw is not None:
        raw = pd.concat([raw, old_raw], ignore_index=True)
        raw = raw.drop_duplicates(subset=['id'])
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    raw.set_index("id", inplace=True)
    raw["id"] = raw.index
    raw.to_json(filename)
    return load_reviews(user, project, data_home=data_home)


def _update_review_single(user, project, pull_request_id, auth=None,
                          verbose=False, max_page=100, per_page=500):
    """
    Fetches the data for a single PR.
    """
    url = 'https://api.github.com/repos/{}/{}/pulls/{}/reviews'.format(
            user, project, pull_request_id)
    raw = _github_api.get_frames(auth, url,
                                 max_page=max_page, per_page=per_page,
                                 verbose=verbose)
    raw = pd.DataFrame(raw)
    return raw


def load_reviews(user, project, data_home=None,
                 state="all"):
    """
    Reads the reviews json files from the data folder.

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
    reviews : json | Projectreviews
        The reviews for this project / user.

    """
    # FIXME reviews should be reloaded from time to time, as some are opened
    # and closed regularly. That's going to be a mess on large projects.
    # Maybe we could store premantly only the closed reviews and update the
    # rest?
    data_home = get_data_home(data_home)
    filepath = join(data_home, user, project, "reviews.json")
    try:
        reviews = pd.read_json(filepath)
        if len(reviews) == 0:
            return None
    except ValueError:
        return None
    return reviews

"""
Some utilities to access github's API. Probably needs some love, refactoring
and testing…

Mostly this is some copy paste of github_state's code
"""

import requests
import collections
from tqdm import tqdm
from requests.exceptions import HTTPError
from pandas import to_datetime
from numpy import ndarray

Auth = collections.namedtuple('Auth', 'user auth')


def colon_seperated_pair(arg):
    pair = arg.split(':', 1)
    if len(pair) == 1:
        return Auth(pair[0], '')
    else:
        return Auth(*pair)


def get_frames(auth, url, max_pages=100, per_page=100,
               **params):
    """Return all commit data from a URL"""
    entries = get_entries(auth, url, max_pages=max_pages,
                          per_page=per_page, **params)
    total = sum(entries, [])
    return total


def get_entries(auth, url, max_pages=100, per_page=100,
                **params):
    """
    Get entries from GitHub

    Parameters
    ----------
    auth : string
        GitHub's authentification hash:
            username:858354186d58153086706507501f5a84423426a1
    url : string
        The URL of the github repository
    max_pages : int
        The number of pages of commits to return.
    per_page : int
        The number of commits to return per page.
    params : dict-like
        Will be passed to requests.get

    Yields
    ------
    json : json object
        The returned commit information.
    """
    # TODO this should only fetch new stuff.
    params = {} if params is None else params
    if 'per_page' not in params.keys():
        params['per_page'] = per_page
    print('Updating repository: {}\nParams: {}'.format(url, params))
    for page in tqdm(range(1, max_pages + 1)):  # for safety
        try:
            params['page'] = str(page)
            r = requests.get(url,
                             params=params,
                             auth=auth)

            r.raise_for_status()
            json = r.json()
            if not json:
                # empty list
                break
            yield json
        except HTTPError:
            # Github sometimes just throws an error
            break


def parse_github_dates(dates, tz='US/Pacific'):
    """Parse github dates so they can be read with strptime.

    Parameters
    ----------
    dates : list of date strings
        A list of github date strings
    format : string
        The format to pass to `datetime.strptime`.


    Returns
    -------
    dates : DatetimeIndex
        The dates converted to a pandas index.
    """
    if not isinstance(dates, (list, ndarray)):
        raise ValueError('dates must be a list')
    # github returns ISO style dates in UTC
    dates = to_datetime(dates, utc=True)
    # Convert to tz
    dates = dates.tz_convert(tz)
    return dates

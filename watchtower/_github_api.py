"""
Some utilities to access github's API. Probably needs some love, refactoring
and testing…

Mostly this is some copy paste of github_state's code
"""

import requests
import collections
import warnings
from tqdm import tqdm
from requests.exceptions import HTTPError
from pandas import to_datetime
from numpy import ndarray

Auth = collections.namedtuple('Auth', 'user auth')
# else, it raises weird errors from time to time.
# cf https://github.com/tqdm/tqdm/issues/481
tqdm.monitor_interval = 0


def colon_seperated_pair(arg):
    pair = arg.split(':', 1)
    if len(pair) == 1:
        return Auth(pair[0], '')
    else:
        return Auth(*pair)


def get_frames(auth, url, max_pages=100, per_page=100,
               verbose=False, direction="asc", **params):
    """Return all commit data from a URL"""
    entries = get_entries(auth, url, max_pages=max_pages,
                          per_page=per_page, verbose=verbose,
                          direction=direction,
                          **params)
    total = sum(entries, [])
    return total


def get_entries(auth, url, max_pages=100, per_page=100,
                direction="asc",
                verbose=False, **params):
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
    verbose : bool
        Controls progress bar display.
    direction : string, optional, default="asc"
        "asc" or "desc"
    params : dict-like
        Will be passed to requests.get

    Yields
    ------
    json : json object
        The returned commit information.
    """
    # TODO this should only fetch new stuff.
    params = {} if params is None else params
    iter_indices = range(1, max_pages + 1)
    if 'per_page' not in params.keys():
        params['per_page'] = per_page
    params["direction"] = direction
    if verbose is True:
        print('Updating repository: {}\nParams: {}'.format(url, params))
        iter_indices = tqdm(iter_indices)
    for page in iter_indices:  # for safety
        params["page"] = str(page)
        try:
            r = requests.get(url,
                             params=params,
                             auth=auth)

            r.raise_for_status()
            json = r.json()
            if not json:
                # empty list
                break
            yield json
        except HTTPError as e:
            # Github sometimes just throws an error
            warnings.warn("Latest request raised an error: %s" % e)
            break


def get_detailed_page(auth, url, params=None):
    """
    Get detailed page

    Parameters
    ----------
    auth : string
        GitHub's authentification hash:
            username:hash

    params : dictionary
        
    url : string
        The URl of the github repository
    """
    try:
        r = requests.get(url,
                         params=params,
                         auth=auth)

        r.raise_for_status()
        json = r.json()
        if not json:
            # empty list
            return
        return json
    except HTTPError as e:
        # Github sometimes just throws an error
        warnings.warn("Latest request raised an error: %s" % e)
        return


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

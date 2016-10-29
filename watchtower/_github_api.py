"""
Some utilities to access github's API. Probably needs some love, refactoring
and testing…

Mostly this is some copy paste of github_state's code
"""

import requests
import collections

Auth = collections.namedtuple('Auth', 'user auth')


def colon_seperated_pair(arg):
    pair = arg.split(':', 1)
    if len(pair) == 1:
        return Auth(pair[0], '')
    else:
        return Auth(*pair)


def get_frames(auth, url, **params):
    entries = get_entries(auth, url, **params)
    total = sum(entries, [])
    return total


def get_entries(auth, url, max_pages=100, **params):
    """
    Get entries from GitHub

    Parameters
    ----------
    auth : string
        GitHub's authentification hash:
            username:858354186d58153086706507501f5a84423426a1

    url : string

    max_pages : int, optional, default: 100

    **params :

    Yields
    ------
    json object
    """
    # TODO this should only fetch new stuff.
    params['per_page'] = 100
    for page in range(1, max_pages + 1):  # for safety
        params['page'] = str(page)
        r = requests.get(url,
                         params=params,
                         auth=auth)
        r.raise_for_status()
        json = r.json()
        print('got {}, {} items'.format(url, len(json)))
        if not json:
            # empty list
            break
        yield json

import pandas as pd
import requests
import os
import time
import json


def get_frames(config, url, **params):
    entries = get_entries(config, url, **params)
    total = sum(entries, [])
    return total


def get_issues_json(config, group):
    """
    Fetches the list of issues from github.

    Parameters
    ----------
    config :

    group :

    Returns
    -------
    raw : json string
    """
    fname = config.project.replace('/', '_') + '_' + group + '.json'
    try:
        ts = os.path.getmtime(fname)
        if ts + config.cache_time >= time.time():
            f = open(fname)
            return json.load(f)
    except (IOError, ValueError):
        pass

    url = 'https://api.github.com/repos/{}/{}'.format(config.project, group)
    raw = get_frames(config, url, state='all')
    f = open(fname, 'w')
    json.dump(raw, f)

    return raw


def get_issues(config, group='issues'):
    raw = get_issues_json(config, group)

    df = pd.DataFrame(raw)
    df.set_index('number', inplace=True)
    df.sort_index(inplace=True)

    return df


def get_entries(config, url, max_pages=100, **params):
    """
    Get entries from GitHub

    Parameters
    ----------
    config :

    url : string

    max_pages : int, optional, default: 100

    **params:

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
                         auth=config.auth)
        r.raise_for_status()
        json = r.json()
        print('got {}, {} items'.format(url, len(json)))
        if not json:
            # empty list
            break
        yield json

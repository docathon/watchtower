import os
import pandas as pd
from os.path import join

from ._config import get_data_home, get_API_token
from . import _github_api


def load_commits(user, project=None, data_home=None,
                 branch="master"):
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

    branch : string, optinola, default: "master"
        The branch fo the project to load.

    Returns
    -------
    commits : json
        The commits for this user/project.
    """
    # XXX We need to sometime update that folder - how to do that?
    # XXX for some projects, that's going to get ugly…
    data_home = get_data_home(data_home)
    filepath = join(data_home, user, project,
                    branch, 'commits.json')
    try:
        commits = pd.read_json(filepath)
    except ValueError:
        return None

    if len(commits) == 0:
        raise ValueError('No commits for this project')

    return commits


def update_commits(user, project=None, auth=None, since=None,
                   max_pages=100, per_page=100,
                   data_home=None, branch="master",
                   verbose=False, **params):
    """Update the commit data for a repository.

    Parameters
    ----------
    user : string
        user or organization name, e.g. "matplotlib"

    project : string | None
        project name, e.g, "matplotlib". If None, user
        information will be loaded.

    auth : string (user:api_key)
        The username / API key for github, separated by a colon. If
        None, the key `GITHUB_API` will be searched for in `environ`.

    since : string
        Search for activity since this date

    max_pages : int
        The maximum number of pages to return in the GET request.

    per_page : int
        The number of commits to return per page.

    data_home : string
        The path to the watchtower data. Defaults to ~/watchtower_data.

    branch : string, optional, default: "master"
        The branch fo the project to load.

    verbose : bool
        Controls progress bar display.

    params : dict-like
        Will be passed to `get_frames`.

    Returns
    -------
    raw : json
        The raw json returned by the github API.
    """
    path = get_data_home(data_home=data_home)
    auth = get_API_token(auth) if auth is None else auth
    auth = _github_api.colon_seperated_pair(auth)
    api_root = 'https://api.github.com/'
    url = api_root + 'repos/{}/{}/commits'.format(
        user, project)
    filename = os.path.join(path, user,
                            project, branch, "commits.json")
    # Pull latest activity info
    raw = _github_api.get_frames(auth, url, since=since,
                                 max_pages=max_pages,
                                 per_page=per_page,
                                 verbose=verbose,
                                 **params)
    raw = pd.DataFrame(raw)

    if len(raw) == 0:
        print('No activity found')
        return None

    if project is None:
        raw = raw.rename(columns={'created_at': 'date'})
    else:
        dates = [ii['author']['date'] for ii in raw['commit'].values]
        raw['date'] = dates

    # Update pre-existing data
    old_raw = load_commits(user, project, branch=branch,
                           data_home=data_home)
    if old_raw is not None:
        raw = pd.concat([raw, old_raw], ignore_index=True)
        raw = raw.drop_duplicates(subset=['date'])
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass

    # Save + return
    raw.to_json(filename)
    return load_commits(user, project, data_home=data_home, branch=branch)


def is_doc(commits, use_message=True, use_files=True):
    """
    Find commits that are documentation related.

    Parameters
    ----------
    commits : pd.DataFrame
        pandas dataframe containing the commits information.

    use_message : bool, optional, default: True

    use_files: bool, optional, default: True
    """
    is_doc_message = commits.message.apply(
        lambda x: "doc" in x.lower())
    is_doc_files = commits.added.apply(
            lambda x: "doc" in " ".join(x).lower())
    is_doc = is_doc_message | is_doc_files
    is_doc.rename("is_doc", inplace=True)
    return is_doc


def find_word_in_string(string, queries=None):
    """Find one of a collection of query words in a string.

    Parameters
    ----------
    string : string
        The string in which we will search for words
    queries : string | list of strings | None
        The words to search for in string

    Returns
    -------
    in_strong : bool
        Whether or not one of the queries was found.
    """
    queries = 'doc' if queries is None else queries
    if isinstance(queries, str):
        queries = [queries]
    in_string = 0
    for word in queries:
        if word.lower() in string.lower():
            in_string += 1
    in_string = in_string > 0
    return in_string


class ProjectCommits(object):
    """Represent commit activity for a github project.

    This stores information about commit activity.

    Parameters
    ----------
    user : string
        The user to query
    project : string
        The repository to query.
    raw : json return by github api
        The raw data for this project, as returned by the github api.

    Attributes
    ----------
    commits : DataFrame
        A collection of commit activity for this project.
    """
    def __init__(self, user, project, raw):
        self.user = user
        self.project = project
        self.raw = raw

        # Extract commits information that is useful
        commits = dict(email=[], name=[], message=[], sha=[],
                       date=[])

        for commit, sha, date in raw[['commit', 'sha', 'date']].values:
            commits['email'].append(commit['author']['email'])
            commits['name'].append(commit['author']['name'])
            commits['message'].append(commit['message'])
            commits['sha'].append(sha)
            commits['date'].append(date)
        commits = pd.DataFrame(commits)
        commits = commits.set_index('date')
        commits.index = pd.to_datetime(commits.index)
        commits['project'] = project
        commits['user'] = user
        self.commits = commits

    def __repr__(self):
        s = 'Project: {} / {} | N Events: {}'.format(
            self.user, self.project, len(self.commits))
        return s

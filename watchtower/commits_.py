import os
import pandas as pd
from os.path import join
import json

from ._config import get_data_home
from . import _github_api


def load_commits(user, project=None, data_home=None):
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
    if project is None:
        filepath = join(data_home, 'users', user, "activity.json")
    else:
        filepath = join(data_home, user, project, "commits.json")
    try:
        commits = pd.read_json(filepath)
    except ValueError as e:
        print(e)
        return None
    return commits


def update_commits(user, project=None, auth=None, since=None,
                   max_pages=100, per_page=100,
                   data_home=None, **params):
    """Update the commit data for a repository.

    Parameters
    ----------
    user : string
        The user / organization of the repository
    project : string | None
        The repository name. If None, all user commit activity will
        be pulled. If a string, all activity for the project will
        be pulled.
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
        A path to where the data is stored.
        Defaults to ~/watchtower_data.
    params : dict-like
        Will be passed to `get_frames`.

    Returns
    -------
    raw : json
        The raw json returned by the github API.
    """
    path = get_data_home(data_home=data_home)
    auth = _github_api.colon_seperated_pair(auth)
    if project is None:
        url = 'https://api.github.com/users/{}/events'.format(user)
        filename = os.path.join(path, 'users', user, "activity.json")
    else:
        url = 'https://api.github.com/repos/{}/{}/commits'.format(
            user, project)
        filename = os.path.join(path, user, project, "commits.json")
    raw = _github_api.get_frames(auth, url, since=since,
                                 max_pages=max_pages,
                                 per_page=per_page,
                                 **params)
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass
    with open(filename, "w") as f:
        json.dump(raw, f)
    return raw


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
    is_doc_message = commits.message.apply(lambda x: "doc" in x.lower())
    is_doc_files = commits.added.apply(lambda x: "doc" in " ".join(x).lower())
    is_doc = is_doc_message | is_doc_files
    is_doc.rename("is_doc", inplace=True)
    return is_doc


class CommitHistory(object):
    """Load commit history for a project.

    Parameters
    ----------
    user : string
        The username for a github project
    project : string | None
        The project name. If None, it will be the same as the username.

    Attributes
    ----------
    raw : DataFrame
        The raw data containing all commit information for this project
    commits : DataFrame
        A subset of information in the package that can be easily indexed.
    """
    def __init__(self, user, project=None):
        project = user if project is None else project
        self.user = user
        self.project = project
        self.raw = load_commits(user, project)

        # Package into a more readable DataFrame
        dates = pd.to_datetime([ii['author']['date']
                                for ii in self.raw['commit']])
        authors, emails = zip(*[(ii['author']['name'], ii['author']['email'])
                                for ii in self.raw['commit']])
        messages = [ii['message'] for ii in self.raw['commit']]
        data = dict(message=messages, author=authors, email=emails, date=dates)
        self.commits = pd.DataFrame(data)

    def __repr__(self):
        return '<CommitHistory> User: {} | Project: {} | n_commits: {}'.format(
            self.user, self.project, len(self.commits))

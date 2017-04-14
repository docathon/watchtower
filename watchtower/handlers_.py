from glob import glob
import os
import os.path as op
import pandas as pd
from .datasets import get_data_home
from ._config import get_API_token
from .commits_ import update_commits
from .issues_ import update_issues


class GithubDatabase(object):
    """A database with information about github commits and issues.

    A container for data about project/user activity on github. This
    essentially lists which pieces of information have already been
    loaded from github, and makes it possible to extract information
    from this database into python.

    Parameters
    ----------
    data_home : string | None
        The path to the watchtower data. Defaults to ~/watchtower_data

    auth : string | None
        If a string, must be either a combination of username:token as
        specified by the github api, or a string that exists in os.environ,
        which points to a username:token pair. If None, defaults to
        `GITHUB_API`.

    verbose : bool
        Controls progress bar display.

    Attributes
    ----------
    projects : list of strings
        A collection of projects for which watchtower has data. These are
        listed as repo/project pairs.

    users : list of strings
        A collection of users for which watchtower has data.
    """
    def __init__(self, data_home=None, auth=None, verbose=False,
                 test_data=False):

        self.data_home = get_data_home(data_home)
        self.verbose = verbose
        self._load_db()

        # Authentication
        self.auth = get_API_token(auth)

    def update(self, user, project=None, commits=True, issues=True,
               since=None, max_pages=100, per_page=100, issues_state='all',
               branch=None):
        """Update data for a user / project.

        This will append new data to data for the user / project if it
        already exists.

        Parameters
        ----------
        user : string
            user or organization name, e.g. "matplotlib"

        project : string | None
            project name, e.g, "matplotlib". If None, user
            information will be loaded.

        commits : bool
            Whether to update commits for this user/project

        issues : bool
            Whether to update issues for this user/project

        since : string of form "YYYY-MM-DD"
            Only update with data after this date.

        max_pages : int
            Maximum number of pages to query from the github api.

        per_page : int
            Number of items to return per page

        issues_state : 'all' | 'open' | 'closed'
            Whether to include only a subset, or all issues.
        """
        if commits is True:
            update_commits(user, project=project, auth=self.auth,
                           since=since, max_pages=max_pages,
                           per_page=per_page, data_home=self.data_home,
                           branch=branch, verbose=self.verbose)
        if issues is True and project is not None:
            update_issues(user, project, auth=self.auth, since=since,
                          data_home=self.data_home, state=issues_state)
        self._load_db()

    def update_all(self, commits=True, issues=True, since='2017-01-01',
                   max_pages=100, per_page=100, issues_state='all'):
        """Update all projects / users currently in the database.

        Parameters
        ----------
        commits : bool
            Whether to update commits for this user/project

        issues : bool
            Whether to update issues for this user/project

        since : string of form "YYYY-MM-DD"
            Only update with data after this date.

        max_pages : int
            Maximum number of pages to query from the github api.

        per_page : int
            Number of items to return per page

        issues_state : 'all' | 'open' | 'closed'
            Whether to include only a subset, or all issues.
        """
        # Projects
        for user, project in [ii.split('/') for ii in self.projects]:
            print('{}/{}'.format(user, project))
            self.update(user, project,
                        since=since, max_pages=max_pages,
                        per_page=per_page,
                        issues_state=issues_state,
                        verbose=self.verbose)
        # Users
        for user in self.users:
            print(user)
            self.update(user, auth=self.auth, since=since, max_pages=max_pages,
                        per_page=per_page, data_home=self.data_home,
                        verbose=self.verbose)

    def load(self, user, project=None, branch=None):
        """Load data for a user / project.

        Parameters
        ----------
        user : string
            The user to query

        project : string | None
            The repository to query. If None, only user data will be loaded.

        Returns
        -------
        handler : instance of UserActivity or ProjectActivity
            The activity for the user / project specified
        """
        from .commits_ import load_commits
        if project is None:
            raw = load_commits(user, project=project, data_home=self.data_home)
            return UserActivity(user, raw)
        else:
            return ProjectActivity(user, project, branch=branch)

    def _load_db(self):
        # List users in db
        users = glob(op.join(self.data_home, 'users', '*'))
        self.users = [ii.split(os.sep)[-1] for ii in users]

        # List projects in db
        projects = glob(op.join(self.data_home, 'projects', '*', '*'))
        self.projects = [os.sep.join(ii.split(os.sep)[-2:])
                         for ii in projects]

    def __repr__(self):
        s = 'User Database | {} Users | {} projects'.format(
            len(self.users), len(self.projects))
        return s


collect_user_events = ['PushEvent', 'CreateEvent', 'PullRequestEvent']


class UserActivity(object):
    """Represent activity for a github user.

    This collects subsets of github api data as attributes, and
    stores the raw github API result as well.

    Parameters
    ----------
    user : string
        The user for this data
    raw : json return by github api
        The raw data for this user, as returned by the github api.

    Attributes
    ----------
    PushEvent : DataFrame
        A collection of Push events for this user

    CreateEvent : DataFrame
        A collection of issue creation events for this user.

    PullRequestEvent : DataFrame
        A collection of pull request events for this user.
    """
    def __init__(self, user, raw):
        self.user = user
        self.raw = raw
        for event_type in collect_user_events:
            this_raw = self.raw.query('type == @event_type')
            this_raw = this_raw.set_index('date')
            this_raw.index = pd.to_datetime(this_raw.index)
            setattr(self, event_type, this_raw)

    def __repr__(self):
        s = 'User: {} | N Events: {}'.format(self.user, len(self.raw))
        return s


class ProjectActivity(object):
    """Represent activity for a github project.

    This stores information about both issue activity and commit activity.

    Parameters
    ----------
    user : string
        The user to query

    project : string
        The repository to query.

    branch : string
        The branch fo the project to load.

    Attributes
    ----------
    handlers : dictionary
        A dictionary containing the handler objects for thie project's data

    issues : DataFrame
        A collection of issue information for this project.

    commits : DataFrame

        A collection of commit activity for this project.
    """
    def __init__(self, user, project, branch=None):
        from .issues_ import load_issues
        from .commits_ import load_commits

        self.user = user
        self.project = project
        self.home = get_data_home()

        self.handlers = {}
        self.handlers['issues'] = load_issues(user, project, use_handler=True)
        self.handlers['commits'] = load_commits(
            user, project, branch=branch, use_handler=True,
            data_home=self.data_home)
        if self.handlers['issues'] is not None:
            self.issues = self.handlers['issues'].issues
        else:
            self.issues = None
        if self.handlers['commits'] is not None:
            self.commits = self.handlers['commits'].commits
        else:
            self.commits = None

    def __repr__(self):
        n_issues = len(self.issues) if self.issues is not None else 0
        n_commits = len(self.commits) if self.commits is not None else 0
        s = 'Project: {} / {} | N Issues: {} | N Commits: {}'.format(
            self.user, self.project, n_issues, n_commits)
        return s

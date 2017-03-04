from glob import glob
import os
import os.path as op
import pandas as pd
import numpy as np
from tqdm import tqdm
from ._config import get_data_home, get_API_token

collect_user_events = ['PushEvent', 'CreateEvent', 'PullRequestEvent']


class GithubDatabase(object):
    def __init__(self, data_home=None, auth=None):

        self.data_home = get_data_home(data_home)
        self._load_db()

        # Authentication
        self.auth = get_API_token(auth)

    def update(self, user, project=None, commits=True, issues=True,
               since=None, max_pages=100, per_page=100, issues_state='all'):
        from .commits_ import update_commits
        from .issues_ import update_issues
        if commits is True:
            update_commits(user, project=project, auth=self.auth,
                           since=since, max_pages=max_pages,
                           per_page=per_page, data_home=self.data_home)
        if issues is True and project is not None:
            update_issues(user, project, auth=self.auth, since=since,
                          data_home=self.data_home, state=issues_state)
        self._load_db()

    def update_all(self, commits=True, issues=True, since='2017-01-01',
                   max_pages=100, per_page=100, issues_state='all'):
        # Projects
        for user, project in [ii.split('/') for ii in self.projects]:
            print('{}/{}'.format(user, project))
            self.update(user, project,
                        since=since, max_pages=max_pages,
                        per_page=per_page,
                        issues_state=issues_state)
        # Users
        for user in self.users:
            print(user)
            self.update(user, auth=self.auth, since=since, max_pages=max_pages,
                        per_page=per_page, data_home=self.data_home)

    def load(self, user, project=None):
        from .commits_ import load_commits
        if project is None:
            raw = load_commits(user, project=project, data_home=self.data_home)
            if raw is None:
                raise ValueError('No data exists for this user/project')
            return UserActivity(user, raw)
        else:
            return ProjectActivity(user, project)

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


class UserActivity(object):
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
    def __init__(self, user, project):
        from .issues_ import load_issues
        from .commits_ import load_commits

        self.user = user
        self.project = project
        self.home = get_data_home()

        self.handlers = {}
        self.handlers['issues'] = load_issues(user, project, use_handler=True)
        self.handlers['commits'] = load_commits(user, project, use_handler=True)
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


class ProjectCommits(object):
    def __init__(self, user, project, raw):
        self.user = user
        self.project = project
        self.raw = raw

        # Extract commits information that is useful
        commits = dict(email=[], name=[], message=[], sha=[],
                       date=[])
        for commit in raw['commit'].values:
            commits['email'].append(commit['author']['email'])
            commits['name'].append(commit['author']['name'])
            commits['message'].append(commit['message'])
            commits['sha'].append(commit['tree']['sha'])
            commits['date'].append(commit['author']['date'])
        commits = pd.DataFrame(commits)
        commits['date'] = pd.to_datetime(commits['date'])
        commits = commits.set_index('date')
        commits['project'] = project
        commits['user'] = user
        self.commits = commits

    def __repr__(self):
        s = 'Project: {} / {} | N Events: {}'.format(
            self.user, self.project, len(self.commits))
        return s


class ProjectIssues(object):
    def __init__(self, user, project, raw):
        self.user = user
        self.project = project
        self.raw = raw

        # Extract issue information that is useful
        # Building a dictionary in case we need to dig
        # deeper in future versions of watchtower
        issues = dict(
            title=[], created_at=[], labels=[], state=[],
            updated_at=[], html_url=[], id=[],
            user=[], pull_request=[])
        if len(raw) == 0:
            self.issues = None
            return
        use_keys = list([key for key in issues.keys()
                         if key in raw.columns])
        insert_keys = list([key for key in issues.keys()
                            if key not in raw.columns])
        issues = raw[use_keys]
        issues = issues.rename(columns={'created_at': 'date'})\
            .set_index('date')
        issues.index = pd.to_datetime(issues.index)

        # Label names
        label_names = [list(label['name']
                            for label in labels)
                       for labels in issues['labels'].values]
        issues['label_names'] = label_names
        for key in insert_keys:
            issues[key] = np.nan

        # Has a PR
        has_pr = -1 * issues['pull_request'].isnull()
        issues['has_pr'] = has_pr
        self.issues = issues

    def __repr__(self):
        s = 'Issues: {} / {} | N Open: {} | N Closed: {}'.format(
            self.user, self.project,
            sum(self.issues['state'] == 'open'),
            sum(self.issues['state'] == 'closed'))
        return s

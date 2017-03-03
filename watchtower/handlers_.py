from glob import glob
import os
import pandas as pd
from .commits_ import load_commits, update_commits
from ._config import get_data_home, get_API_token

collect_user_events = ['PushEvent', 'CreateEvent', 'PullRequestEvent']


class GithubDatabase(object):
    def __init__(self, data_home=None, auth=None):

        self.data_home = get_data_home(data_home)
        self._load_db()

        # Authentication
        self.auth = get_API_token(auth)

    def update(self, user, project=None, since=None,
               max_pages=100, per_page=100):
        update_commits(user, project=project, auth=self.auth,
                       since=since, max_pages=max_pages,
                       per_page=per_page, data_home=self.data_home)
        self._load_db()

    def load(self, user, project=None):
        raw = load_commits(user, project=project, data_home=self.data_home)
        if raw is None:
            raise ValueError('No data exists for this user/project')
        if project is None:
            return UserActivity(user, raw)
        else:
            return ProjectActivity(user, project, raw)

    def _load_db(self):
        # List users in db
        users = glob(os.path.join(self.data_home, 'users', '*'))
        self.users = [ii.split(os.sep)[-1] for ii in users]

        # List projects in db
        projects = glob(os.path.join(self.data_home, 'projects', '*', '*'))
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
            this_raw = this_raw.set_index('created_at')
            this_raw.index = pd.to_datetime(this_raw.index)
            setattr(self, event_type, this_raw)

    def __repr__(self):
        s = 'User: {} | N Events: {}'.format(self.user, len(self.raw))
        return s


class ProjectActivity(object):
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

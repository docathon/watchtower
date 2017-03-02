from glob import glob
import os
import pandas as pd
from .commits_ import load_commits, update_commits
from ._github_api import colon_seperated_pair
from ._config import get_data_home, get_API_token

collect_user_events = ['PushEvent', 'CreateEvent', 'PullRequestEvent']


class UserDatabase(object):
    def __init__(self, data_home=None, auth=None):

        self.data_home = get_data_home(data_home)
        users = glob(os.path.join(self.data_home, 'users', '*'))
        users = [ii.split(os.sep)[-1] for ii in users]
        self.users = users
        self.auth = get_API_token(auth)

    def update_user(self, user, since=None,
                    max_pages=100, per_page=100):
        update_commits(user, auth=self.auth, since=since, max_pages=max_pages,
                       per_page=per_page, data_home=self.data_home)

    def load_user(self, user):
        raw = load_commits(user, data_home=self.data_home)
        return UserActivity(user, raw)

    def __repr__(self):
        s = 'User Database | {} Users | {}'.format(
            len(self.users), self.users[:4])
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

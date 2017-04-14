"""
=================================
Identifying documentation commits
=================================

This example shows how to identify documentation specific commits.

"""

from watchtower.handlers_ import GithubDatabase
from watchtower.datasets import dldata
import matplotlib.pyplot as plt
import numpy as np


projects = [('docathon', 'watchtower'),
            ('scikit-learn', 'scikit-learn')]


def is_doc(string):
    check_strings = ['doc', 'documentation', 'docathon']
    is_doc = any(istr in string for istr in check_strings)
    return is_doc


# Fetches the test data if need be.
dldata.fetch_test_data()
# XXX this need to change to call something that is specifically the test data
db = GithubDatabase(verbose=True, data_home="~/watchtower_data/test_data")

since = '2017-02-10'

# Load the data for plotting
projects = [db.load(user, project) for user, project in projects]

# Now plot pushes each day
fig, axs = plt.subplots(nrows=2, figsize=(8, 6), sharex=True, sharey=True)
for proj, ax in zip(projects, axs):
    proj.commits['is_doc'] = proj.commits['message'].apply(is_doc)
    proj.commits = proj.commits.query('date > @since')
    all_commits = proj.commits.resample('D').count().\
        replace(np.nan, 0).astype(int)
    doc_commits = proj.commits.resample('D').sum().\
        replace(np.nan, 0).astype(int)
    ax.bar(all_commits.index, all_commits['is_doc'], label='all')
    ax.bar(doc_commits.index, doc_commits['is_doc'], label='doc')
    ax.set_title("{}/{}".format(proj.user, proj.project), fontweight="bold")
    ax.set_ylabel('# Commits', fontweight="bold")
axs[-1].legend()
plt.setp(axs[-1].get_xticklabels(), rotation=45, horizontalalignment='right')
plt.setp([ax.xaxis.label for ax in axs], visible=False)
plt.tight_layout()
plt.show()

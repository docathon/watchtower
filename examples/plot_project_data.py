from watchtower.handlers_ import GithubDatabase
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

projects = [('matplotlib', 'matplotlib'),
            ('scikit-learn', 'scikit-learn'),
            ('pandas-dev', 'pandas')]


def is_doc(string):
    check_strings = ['doc', 'documentation', 'docathon']
    is_doc = any(istr in string for istr in check_strings)
    return is_doc


auth = os.environ['GITHUB_API']
update_db = True

# Initialize the database
db = GithubDatabase(auth=auth)

# Update users and print the db
since = '2017-02-25'
if update_db is True:
    for user, project in projects:
        db.update(user, project, since='2017-02-25')
since = pd.to_datetime(since)
print(db)

# Load the data for plotting
projects = [db.load(user, project) for user, project in projects]

# Now plot pushes each day
fig, axs = plt.subplots(3, 1, figsize=(10, 15), sharex=True, sharey=True)
for proj, ax in zip(projects, axs):
    proj.commits['is_doc'] = proj.commits['message'].apply(is_doc)
    proj.commits = proj.commits.query('date > @since')
    all_commits = proj.commits.resample('D').count().\
        replace(np.nan, 0).astype(int)
    doc_commits = proj.commits.resample('D').sum().\
        replace(np.nan, 0).astype(int)
    ax.bar(all_commits.index, all_commits['is_doc'], label='all')
    ax.bar(doc_commits.index, doc_commits['is_doc'], label='doc')
    ax.set_title(proj, fontsize=18)
    ax.set_ylabel('N Commits')
axs[-1].legend()
plt.setp(axs[-1].get_xticklabels(), rotation=45, horizontalalignment='right')
plt.setp([ax.xaxis.label for ax in axs], visible=False)
plt.tight_layout()
plt.show()

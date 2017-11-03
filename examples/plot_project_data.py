"""
=================================
Identifying documentation commits
=================================

This example shows how to identify documentation specfic commits.

"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from watchtower import commits_

projects = [('docathon', 'watchtower'),
            ('scikit-learn', 'scikit-learn')]


update_db = False

# Initialize the database

# Update users and print the db
since = '2017-02-10'
if update_db is True:
    for user, project in projects:
        # db.update(user, project, since=since)
        # FIXME
        pass

since = pd.to_datetime(since)

# Now plot pushes each day
fig, axs = plt.subplots(nrows=2, figsize=(8, 6), sharex=True, sharey=True)
for (user, project), ax in zip(projects, axs):
    proj = commits_.load_commits(user, project)
    proj['is_doc'] = commits_.is_doc(proj)
    proj["datetime"] = [t.to_datetime() for t in proj["date"]]
    proj = proj[proj["datetime"] > since]
    proj.set_index("datetime", inplace=True)
    all_commits = proj.resample(
        '7D').count().replace(np.nan, 0).astype(int)
    doc_commits = proj.resample(
        '7D').sum().replace(np.nan, 0).astype(int)
    ax.bar(np.arange(len(all_commits)), all_commits['is_doc'], label='all')
    ax.bar(np.arange(len(doc_commits)), doc_commits['is_doc'], label='doc')
    ax.set_title("{}/{}".format(user, project))
    ax.set_ylabel('# Commits', fontweight="bold")
axs[-1].legend()
plt.setp(axs[-1].get_xticklabels(), rotation=45, horizontalalignment='right')
plt.setp([ax.xaxis.label for ax in axs], visible=False)
plt.tight_layout()
plt.show()

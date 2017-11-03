"""
======
Labels
======

In this small examples, we compare labels between the different projects:

    - scikit-learn
    - watchtower

"""
import numpy as np
import pandas as pd
from watchtower import issues_
import matplotlib.pyplot as plt

projects = (("scikit-learn", "scikit-learn"),
            ("docathon", "watchtower"))

update_issues = False  # Do we update the database
since = '2017-02-01'

for user, project in projects:
    if update_issues is True:
        all_issues = issues_.update_issues(user, project)
    else:
        all_issues = issues_.load_issues(user, project)

    open_issues = all_issues[all_issues["state"] == "open"]
    # Extract the names of the labels
    all_labels = np.array([label["name"] for labels in all_issues['labels']
                           for label in labels])
    open_labels = np.array([label["name"] for labels in open_issues['labels']
                           for label in labels])

    unique_labels = np.unique(all_labels)
    counts = dict()
    for label in unique_labels:
        n_instances = np.sum(all_labels == label)
        n_open = np.sum(open_labels == label)
        counts[label] = (n_instances, n_open)
    counts = pd.DataFrame(counts).T
    counts.columns = ['all', 'open']
    counts = counts.sort_values('all', ascending=False)

    fig = plt.figure(figsize=(14, 5))
    ax = fig.add_axes([0.1, 0.3, 0.8, 0.6])
    ax.grid("off")
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    for column in counts.columns:
        ixs = range(counts.shape[0])
        ax.bar(ixs, counts[column], label=column)
    ax.set_xticks(ixs)
    ax.set_xticklabels(counts.index, rotation=90, fontsize="x-small")

    yticks = ax.get_yticks()
    for l in yticks:
        ax.axhline(l, linewidth=0.75, zorder=-10, color="0.5")
    ax.set_yticks(yticks)
    ax.set_title(project, fontweight="bold")

    ax.legend()
plt.show()

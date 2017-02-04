import numpy as np

from watchtower import issues_
from watchtower import labels_
import matplotlib.pyplot as plt

projects = ("matplotlib", "scikit-learn", "scikit-image", "ipython", "numpy")

for project in projects:
    user = project

    all_issues = issues_.get_issues(user, project, issues_type="all")
    if all_issues is None:
        print('No data for {}'.format(project))
        continue
    opened_issues = issues_.select_opened(all_issues)

    # Get all labels
    labels = labels_.load_labels(user, project)

    # Extract the names of the labels
    labels_names = sorted(labels.name.as_matrix())
    labels_counts = []
    opened_labels = []

    for name in labels_names:
        labels_counts.append(sum(
            [1 for label in all_issues["labels"]
             for l in label if l["name"] == name]))
        opened_labels.append(sum(
            [1 for label in opened_issues["labels"]
             for l in label if l["name"] == name]))

    fig = plt.figure(figsize=(14, 5))
    ax = fig.add_axes([0.1, 0.3, 0.8, 0.6])
    ax.grid("off")
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    ax.bar(np.arange(len(labels_names)), labels_counts, label="Closed")
    ax.bar(np.arange(len(labels_names)), opened_labels, label="Open")

    ax.set_xticks(np.arange(len(labels_names)))
    ax.set_xticklabels(labels_names, rotation=90, fontsize="x-small")

    yticks = ax.get_yticks()
    for l in yticks:
        ax.axhline(l, linewidth=0.75, zorder=-10, color="0.5")
    ax.set_yticks(yticks)
    ax.set_title(project, fontweight="bold")

    ax.legend()

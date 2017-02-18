import numpy as np
import os
from watchtower import commits_
import matplotlib.pyplot as plt


def plot_commits(user, project):
    commits = commits_.load_commits(user, project)

    n_commits = []
    doc_commits = []

    for month in range(1, 12):
        if commits is None:
            doc_commits.append(0)
            n_commits.append(0)
            continue
        dtime = "2017-%02d" % month
        mask = commits.commit.apply(
            lambda x: x["author"]["date"].startswith(dtime))
        n_commits.append(mask.sum())
        doc_commits.append(sum(
            ("DOC" in c["message"]) |
            ("docs" in c["message"]) |
            ("docstring" in c["message"])
            for c in commits[mask].commit))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(np.arange(len(n_commits)), n_commits, label="all")
    ax.bar(np.arange(len(n_commits)), doc_commits, label="doc")
    ax.grid("off")
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    label_names = ["Jan", "Feb", "Mar"]
    ax.set_xticks(np.arange(12))
    ax.set_xticklabels(label_names, rotation=90, fontsize="x-small")
    ax.set_ylabel("# commits")

    yticks = ax.get_yticks()
    for l in yticks:
        ax.axhline(l, linewidth=0.75, zorder=-10, color="0.5")
    ax.set_yticks(yticks)
    ax.legend(loc=1)
    ax.set_title(project, fontweight="bold")
    return fig, ax


informations = np.loadtxt(".downloaded_projects", dtype=bytes)
try:
    os.makedirs("build/images")
except OSError:
    pass

for user, project in informations:
    fig, ax = plot_commits(user.decode(), project.decode())
    filename = os.path.join("build/images", project.decode() + ".png")
    fig.savefig(filename)

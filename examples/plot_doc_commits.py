from watchtower import commits_
import numpy as np
import matplotlib.pyplot as plt

projects = ["matplotlib", "numpy", "scikit-learn"]
for project in projects:
    user = project
    commits = commits_.load_commits(user, project)
    if commits is None:
        print('No data for {}'.format(project))
        continue

    n_commits = commits.shape[0]
    doc_commits = sum("DOC" in commits.commit[i]["message"]
                      for i in range(n_commits))
    n_commits = []
    doc_commits = []
    for month in range(1, 13):
        dtime = "2016-%02d" % month
        mask = commits.commit.apply(
            lambda x: x["author"]["date"].startswith(dtime))
        n_commits.append(mask.sum())
        doc_commits.append(sum(
            ("DOC" in c["message"]) | ("docs" in c["message"]) | ("docstring" in c["message"])
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
    label_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                "Oct", "Nov", "Dec"]
    ax.set_xticks(np.arange(12))
    ax.set_xticklabels(label_names, rotation=90, fontsize="x-small")
    ax.set_ylabel("# commits")

    yticks = ax.get_yticks()
    for l in yticks:
        ax.axhline(l, linewidth=0.75, zorder=-10, color="0.5")
    ax.set_yticks(yticks)
    ax.legend(loc=1)
    ax.set_title(project, fontweight="bold")
plt.show()

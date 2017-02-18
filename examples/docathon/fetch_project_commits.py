import argparse
import numpy as np
from datetime import date
import os
import pandas as pd
from watchtower import commits_

parser = argparse.ArgumentParser()
parser.add_argument("filename",
                    help=("CSV file containing the project "
                          "registration information."))
parser.add_argument("--outdir", "-o", default="build")
parser.add_argument("--per_page", "-n", default=100)
parser.add_argument("--max_pages", "-m", default=100)

parser.add_argument("auth")
args = parser.parse_args()

auth = args.auth
per_page = args.per_page,
max_pages = args.max_pages

columns = ["timestamp", "username", "name", "contact", "github_org",
           "description", "language", "url", "goal", "help",
           "has_github_project",
           "github_project_url"]
information = pd.read_csv(args.filename, header=None, skiprows=1,
                          names=columns).as_matrix()
since = "2017-01-01"

downloaded_commits = []
for project in information:
    if "bitbucket" in project[4]:
        continue
    github_handle = project[4].strip("/")
    user, project = github_handle.split("/")[-2:]
    try:
        commits_.update_commits(user, project, auth,
                                since=since)
    except Exception:
        print("Failed to retrive commits for %s/%s" % (user, project))

    downloaded_commits.append([user, project])
downloaded_commits = np.array(downloaded_commits)
np.savetxt(".downloaded_projects", downloaded_commits, fmt="%s")

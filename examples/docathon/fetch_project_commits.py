import argparse
import numpy as np
import pandas as pd
from watchtower import commits_
from watchtower._config import get_API_token

parser = argparse.ArgumentParser()
parser.add_argument("filename",
                    help=("CSV file with the project "
                          "registration information. This should "
                          "be downloaded manually."))
parser.add_argument("--auth_user", default='GITHUB_API_USER')
parser.add_argument("--auth_token", default='GITHUB_API_TOKEN')
parser.add_argument("--outdir", "-o", default="build")
parser.add_argument("--per_page", "-n", default=100)
parser.add_argument("--max_pages", "-m", default=100)
parser.add_argument("--since", "-s", default="2017-01-01",
                    help="Date from which to search, YYYY-MM-DD")

args = parser.parse_args()

# Generate the github API user:token pair
auth_user = args.auth_user
auth_token = get_API_token(args.auth_token)
auth = ':'.join([auth_user, auth_token])
print('Using authentication pair: {}'.format(auth))

per_page = args.per_page,
max_pages = args.max_pages
since = args.since

# Load data from google drive questionnaire
columns = ["timestamp", "username", "name", "contact", "github_org",
           "description", "language", "url", "goal", "help",
           "has_github_project",
           "github_project_url"]
information = pd.read_csv(args.filename, header=None, skiprows=1,
                          names=columns)

# Iterate projects and retrieve its latest info
print('Updating commits for %s projects' % len(information))
downloaded_commits = []
exceptions = []
for ix, project in information.iterrows():
    try:
        github_handle = project['github_org'].strip("/")
        if "bitbucket" in github_handle:
            continue
        user, project_name = github_handle.split("/")[-2:]
        commits_.update_commits(user, project_name, auth,
                                since=since)
        downloaded_commits.append([user, project_name])
    except Exception:
        exceptions.append(project['name'])

downloaded_commits = np.array(downloaded_commits)
np.savetxt(".downloaded_projects", downloaded_commits, fmt="%s")
print('Finished updating commits.')
if len(exceptions) > 0:
  print('Could not retrieve information for projects: {}'.format(exceptions))


from watchtower import issues_
from watchtower import labels_, commits_
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "auth",
    help="formet username:token, ie"
          " choldgraf:2b1a9de6a5278fd36d1f10379debfb54ef27cbf9")
parser.add_argument("--project", "-p", default="scikit-learn")
args = parser.parse_args()

project = args.project
user = project
auth = args.auth
commits_.update_commits(user, project, auth)


from watchtower import issues_
from watchtower import labels_, commits_
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "auth",
    help=("formet username:token, e.g.: "
          "choldgraf:2b1a9de6a5278fd36d1f10379debfb54ef27cbf9"))
parser.add_argument("--project", "-p", default="scikit-learn")
parser.add_argument("--per_page", "-n", default=100)
parser.add_argument("--max_pages", "-m", default=100)


args = parser.parse_args()

project = args.project
user = project
auth = args.auth

per_page = args.per_page,
max_pages = args.max_pages

commits_.update_commits(user, project, auth,
                        max_pages=max_pages, per_page=per_page)

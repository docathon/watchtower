"""This demonstrates how one could create a script that
retrieves commit information from a project supplied as an
argument.
"""

from watchtower import commits_
import argparse
from watchtower._config import get_API_token

# Arguments machinery
parser = argparse.ArgumentParser()
parser.add_argument("auth_user", help="A github username")
parser.add_argument("auth_token",
    help=("The github API token, or a string corresponding to a"
          " variable in the global environment"))
parser.add_argument("--project", "-p", default="scikit-learn")
parser.add_argument("--per_page", "-n", default=100)
parser.add_argument("--max_pages", "-m", default=100)

args = parser.parse_args()

# Extract relevant information for watchtower
user = project = args.project
auth_user = args.auth_user
auth_token = get_API_token(args.auth_token)
auth = ':'.join([auth_user, auth_token])
per_page = args.per_page,
max_pages = args.max_pages


# Update commit information for this project
commits_.update_commits(user, project, auth,
                        max_pages=max_pages, per_page=per_page)

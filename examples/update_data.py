
from watchtower import issues_
from watchtower import labels_, commits_
import argparse
import sys
import getpass
import requests
import keyring
import json



parser = argparse.ArgumentParser()
parser.add_argument(
    "--auth",
    help=("formet username:token, e.g.: "
          "choldgraf:2b1a9de6a5278fd36d1f10379debfb54ef27cbf9"), default=None)
parser.add_argument("--project", "-p", default="scikit-learn")
parser.add_argument("--per_page", "-n", default=100)
parser.add_argument("--max_pages", "-m", default=100)
parser.add_argument("--keyring", action='store_true')

fake_username = 'watchtower'


def set_username_and_token(project, username, token):
    keyring.set_password('ghlogin', project, user)
    keyring.set_password('github', project, token)


def get_auth_token(*, project=fake_username, store=True):
    """Get the authentication token for current user.


    Get it from the keychain if available, otherwise prompt for username, 
    password, Two Factor Authentication if necessary. Record a token on the keychain
    for this particular project. And store all the information in the keychain. 
    """
    _, token = get_username_and_auth_token(project=project, store=store)
    return token

def get_username_and_auth_token(project=fake_username, store=True):
    """Get username and the authentication token for GitHub.

    If stored in the keyring, get them and return it. Other wise prompt for it,
    as well as 2fa if necessary and store them in keyring before returning it.
    """
    import keyring
    token = keyring.get_password('github', project)
    user = keyring.get_password('ghlogin', project)
    if token is not None and user is not None:
        return user, token

    print("Please enter your github login and password.  Password is not "
          "stored, only used to get an oAuth token. You can revoke this at "
          "any time on Github. At the following URL:"
          "https://github.com/settings/tokens\n"
          "Username: ", file=sys.stderr, end='')
    user = input('')
    pw = getpass.getpass("Password: ", stream=sys.stderr)

    auth_request = {
      "scopes": [
        "public_repo",
        "gist"
      ],
      "note": "Auth requests for %s" % project,
      "note_url": "",
    }
    response = requests.post('https://api.github.com/authorizations',
                            auth=(user, pw), data=json.dumps(auth_request))
    if response.status_code == 401 and \
            'required;' in response.headers.get('X-GitHub-OTP', ''):
        print("Your login API requested a one time password", file=sys.stderr)
        otp = getpass.getpass("One Time Password: ", stream=sys.stderr)
        response = requests.post('https://api.github.com/authorizations',
                            auth=(user, pw),
                            data=json.dumps(auth_request),
                            headers={'X-GitHub-OTP':otp})
    if response.status_code == 422:
        print("Such a token is already set on GitHub for %s see https://github.com/settings/tokens"% project)
    response.raise_for_status()
    token = json.loads(response.text)['token']
    if store:
        set_username_and_token(project=project, username=user, token=token)
    return user, token



args = parser.parse_args()

project = args.project
user = project
auth = args.auth
if not auth:
    auth = ':'.join(get_username_and_auth_token())

per_page = args.per_page,
max_pages = args.max_pages

commits_.update_commits(user, project, auth,
                        max_pages=max_pages, per_page=per_page)

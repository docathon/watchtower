"""
Some small configuration stuff.
"""

from os import environ


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def get_API_token(token_key):
    """Return the API token.

    Parameters
    ----------
    token_key : string
        Either the github API token, or a string corresponding
        to a variable in `os.environ`. If the latter, this should
        be the key which points to the API token.

    Returns
    -------
    token : string
        The github API token
    """
    # XXX add support for keychain lookup as well?
    token_key = 'GITHUB_API' if token_key is None else token_key
    if token_key in environ:
        token = environ.get(token_key)
    else:
        # Assume the string is already a key
        token = token_key
    return token

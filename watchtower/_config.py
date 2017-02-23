"""
Some small configuration stuff.
"""

from os import environ
from os.path import join
from os.path import exists
from os.path import expanduser
from os import makedirs
import shutil


def get_data_home(data_home=None):
    """Return the path of the watchtower data dir.

    This folder is used by some large dataset loaders to avoid
    downloading the data several times.

    By default the data dir is set to a folder named 'scikit_learn_data'
    in the user home folder.

    Alternatively, it can be set by the 'WATCHTOWER_DATA' environment
    variable or programmatically by giving an explicit folder path. The
    '~' symbol is expanded to the user home folder.

    If the folder does not already exist, it is automatically created.

    Parameters
    ----------
    data_home : string, optional, default: '~/watchtower_data')

    Returns
    -------
    data_home

    Notes
    -----
    This code is highly inspired by scikit-learn's
    """
    if data_home is None:
        data_home = environ.get('WATCHTOWER_DATA',
                                join('~', 'watchtower_data'))
    data_home = expanduser(data_home)
    if not exists(data_home):
        makedirs(data_home)
    return data_home


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
    if token_key in environ:
        token = environ.get(token_key)
    else:
        # Assume the string is already a key
        token = token_key
    return token


def get_API_user(username):
    """Return the API username.

    Parameters
    ----------
    username : string
        Either the github username, or a string corresponding
        to a variable in `os.environ`. If the latter, this should
        be the key which points to the API user name.

    Returns
    -------
    username : string
        The github API username
    """
    # XXX add support for keychain lookup as well?
    if username in environ:
        username = environ.get(username)
    else:
        # Assume the string is already a key
        pass
    return username


def clear_data_home(data_home=None):
    """
    Delete all the content of the data home cache.

    Parameters
    ----------
    data_home : string, optional, default: None

    Notes
    -----
    This code is highly inspired by scikit-learn's
    """
    data_home = get_data_home(data_home)
    shutil.rmtree(data_home)

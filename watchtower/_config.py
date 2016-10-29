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
    data_home : string, optional, default: None

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

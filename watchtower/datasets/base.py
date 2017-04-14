from os import environ, makedirs
from os.path import join, expanduser, exists
import shutil

# authors: Nelle Varoquaux <nelle.varoquaux@gmail.com>

# This module is greatly inspired from sklearn.datasets


def get_data_home(data_home=None):
    """Return the path of the watchtower data dir.

    This folder is used by some large dataset loaders to avoid
    downloading the data several times.

    By default the data dir is set to a folder named 'watchtowe_data'
    in the user home folder.

    Alternatively, it can be set by the 'WATCHTOWER_DATA' environment
    variable or programmatically by giving an explicit folder path. The
    '~' symbol is expanded to the user home folder.

    If the folder does not already exist, it is automatically created.
    """
    if data_home is None:
        data_home = environ.get('WATCHTOWER_DATA',
                                join('~', 'watchtower_data'))
    data_home = expanduser(data_home)
    if not exists(data_home):
        makedirs(data_home)
    return data_home


def clear_data_home(data_home=None):
    """Delete all the content of the data home cache."""
    data_home = get_data_home(data_home)
    shutil.rmtree(data_home)

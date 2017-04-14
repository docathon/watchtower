"""
Automatically downloads data.

The data provided here should be small data sets, on which we can tests a
number of elemets and build nice examples.
"""

import os

try:
    # Python 2
    from urllib2 import HTTPError
    from urllib2 import quote
    from urllib2 import urlopen
except ImportError:
    # Python 3+
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.request import urlopen

from shutil import copyfileobj

from .base import get_data_home


TESTDATA_BASE_URL = (
    "https://raw.githubusercontent.com/docathon/watchtower_data_test/"
    "master/%s")


def fetch_test_data(data_home=None):
    """
    Fetch test data.

    Parameters
    ----------

    data_home : optional, default: None
        specify another download and cache folder for the data sets. By
        default, all watchtower data is stored in '~/watchtower_data'
        subfolders.
    """
    data_home = get_data_home(data_home=data_home)
    data_home = os.path.join(data_home, "test_data")
    if not os.path.exists(data_home):
        os.makedirs(data_home)

    filenames = {
        "projects/docathon/watchtower/commits.json",
        "projects/docathon/watchtower/issues.json",
        "projects/scikit-learn/scikit-learn/commits.json",
        "projects/scikit-learn/scikit-learn/issues.json",
        "users/NelleV/activity.json",
        "users/choldgraf/activity.json"
        }
    for filename in filenames:
        _fetch_filename(filename, data_home)


def _fetch_filename(filename, data_home):
    if os.path.exists(os.path.join(data_home, filename)):
        return

    # If the file doesn't exists, fetch it.

    url = (TESTDATA_BASE_URL %
           quote("projects/docathon/watchtower/commits.json"))

    try:
        testdata_url = urlopen(url)
    except HTTPError as e:
        if e.code == 404:
            e.msg = "File %s not found." % filename
            raise

    outfile = os.path.join(data_home, filename)
    if not os.path.exists(os.path.dirname(outfile)):
        os.makedirs(os.path.dirname(outfile))

    try:
        with open(outfile, "w+b") as f:
            copyfileobj(testdata_url, f)
    except:
        os.remove(outfile)
        raise
    testdata_url.close()

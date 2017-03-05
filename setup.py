import os
import setuptools
from numpy.distutils.core import setup


DISTNAME = 'watchtower'
DESCRIPTION = 'Something cool we are working on…'
MAINTAINER = 'Nelle Varoquaux'
MAINTAINER_EMAIL = 'nelle.varoquaux@gmail.com'
VERSION = '0.0.0-git'


def configuration(parent_package='', top_path=None):
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)

    config.add_subpackage('watchtower')

    return config


if __name__ == "__main__":
    setup(configuration=configuration,
          name=DISTNAME,
          maintainer=MAINTAINER,
          include_package_data=True,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          version=VERSION,
          install_requires=['tqdm', 'pandas', 'requests'],
          zip_safe=False,  # the package can run out of an .egg file
          classifiers=[
              'Intended Audience :: Developers',
              'License :: OSI Approved',
              'Programming Language :: Python',
              'Topic :: Software Development',
              'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS'])

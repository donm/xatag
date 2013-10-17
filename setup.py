import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages
import setuptools
setup(name='xatag',
      version='0.0.0',
      description='Tag any file using extended attributes',
      author='Don',
      author_email='don@ohspite.net',
      url='http://xatag.org',
      packages=['xatag'],
      scripts=['bin/xatag'],
      install_requires=['docopt', 'xattr'],
      tests_require=['pytest']
      )

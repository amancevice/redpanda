import os
from setuptools import setup

NAME    = "redpanda"
VERSION = "0.1.4"
AUTHOR  = "amancevice"
EMAIL   = "smallweirdnum@gmail.com"
DESC    = "Pandas-ORM Integration."

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Topic :: Utilities", ]
REQUIRES = [
    "mock",
    "nose",
    "numpy>=1.9.2",
    "pandas>=0.14.0",
    "sqlalchemy>0.7.10" ]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name                 = NAME,
    version              = VERSION,
    author               = AUTHOR,
    author_email         = EMAIL,
    packages             = [ NAME ],
    package_data         = { "%s" % NAME : ['README.md'] },
    include_package_data = True,
    url                  = 'http://www.smallweirdnumber.com',
    description          = DESC,
    long_description     = read('README.md'),
    classifiers          = CLASSIFIERS,
    install_requires     = REQUIRES,
    test_suite           = "nose.collector" )

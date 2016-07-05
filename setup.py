import os
import re
from setuptools import setup

NAME        = "redpanda"
AUTHOR      = "amancevice"
EMAIL       = "smallweirdnum@gmail.com"
DESC        = "Pandas-ORM Integration."
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Utilities",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python"]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def version():
    search = r"^__version__ *= *['\"]([0-9.]+)['\"]"
    initpy = read("./%s/__init__.py" % NAME)
    return re.search(search, initpy, re.MULTILINE).group(1)

setup(
    name                 = NAME,
    version              = version(),
    author               = AUTHOR,
    author_email         = EMAIL,
    packages             = [NAME],
    package_data         = {NAME: ["README.md"]},
    include_package_data = True,
    url                  = "http://www.smallweirdnumber.com",
    description          = DESC,
    long_description     = read("README.md"),
    classifiers          = CLASSIFIERS,
    install_requires     = ["pandas>=0.16.0", "sqlalchemy>=1.0.0"],
    test_suite           = "nose.collector")

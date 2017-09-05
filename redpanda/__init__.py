""" Pandas-ORM Integration. """
import pkg_resources
from sqlalchemy import create_engine
from .orm import Query
from .orm import Session
from .orm import sessionmaker

try:
    __version__ = pkg_resources.get_distribution(__package__).version
except pkg_resources.DistributionNotFound:
    __version__ = None

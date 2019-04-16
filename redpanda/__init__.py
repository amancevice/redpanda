""" Pandas-ORM Integration. """
import pkg_resources
from sqlalchemy import create_engine  # noqa: F401
from .orm import Query                # noqa: F401
from .orm import Session              # noqa: F401
from .orm import sessionmaker         # noqa: F401

try:
    __version__ = pkg_resources.get_distribution(__package__).version
except pkg_resources.DistributionNotFound:  # pragma: no cover
    __version__ = None                      # pragma: no cover

"""
Pandas-ORM Integration.
"""
from pkg_resources import (get_distribution, DistributionNotFound)

from sqlalchemy import create_engine  # noqa: F401
from redpanda.orm import (Query, Session, sessionmaker)  # noqa: F401


def _version():
    """
    Helper to get package version.
    """
    try:
        return get_distribution(__name__).version
    except DistributionNotFound:  # pragma: no cover
        return None


__version__ = _version()

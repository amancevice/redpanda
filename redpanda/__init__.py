""" Pandas-ORM Integration. """


import pandas
import sqlalchemy
from sqlalchemy import create_engine
from . import orm


__author__ = "amancevice"
__version__ = "0.2.4"


# pylint: disable=invalid-name
Session = orm.sessionmaker()

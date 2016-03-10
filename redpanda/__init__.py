""" Pandas-ORM Integration. """


import pandas
from . import orm


__author__ = "amancevice"
__email__ = "smallweirdnum@gmail.com"
__version__ = "0.1.6"


def query(entities, session=None, **read_sql):
    """ Construct RedPanda """
    return orm.RedPanda(entities, session=session, **read_sql)

""" RedPanda SQLAlchemy Mixins. """

import sqlalchemy
from . import orm
from . import utils


class RedPandaMixin(object):
    """ Basic RedPanda Mixin. """
    __redpanda__ = orm.RedPanda
    __read_sql__ = {}

    @classmethod
    def redpanda(cls, con, query=None, **read_sql):
        """ Create RedPanda instance for SQLAlchemy object.

            Arguments:
                con         (sqlalchemy.engine.Engine): SQLAlchemy engine
                query       (sqlalchemy.orm.Query):     Optional SQLAlchemy refinement query
                read_sql    (dict):                     Arguments for pandas.read_sql()

            Returns:
                RedPanda instance. """
        # Use arg-provided or class-provided query
        query = query or sqlalchemy.orm.Query(cls)
        # Combine arg-provided and class-provided read_sql kwargs
        read_sql = utils.dictcombine(cls.__read_sql__, read_sql)
        # Return class-defined RedPanda helper
        return cls.__redpanda__(cls, con, query, **read_sql)

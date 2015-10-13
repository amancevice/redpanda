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
        return cls.__redpanda__(con, query, **read_sql)

    @classmethod
    def redparse(cls, dataframe, parse_index):
        """ Return a generator for SQLAlchemy models from a pandas.DataFrame.

            Arguments:
                dataframe   (pandas.DataFrame): pandas.DataFrame to parse
                parse_index (boolean):          parse the index as a model attribute

            Returns:
                Generator of SQLAlchemy objects. """
        for ix, row in dataframe.iterrows():
            attrs = row.to_dict()
            if parse_index is True:
                assert dataframe.index.name is not None, "Cannot parse unnamed index"
                attrs[dataframe.index.name] = ix
            yield cls(**attrs)

""" RedPanda SQLAlchemy Mixins. """

import sqlalchemy
from . import orm
from . import utils


class RedPandaMixin(object):
    """ Basic RedPanda Mixin. """
    __redpanda__ = orm.RedPanda
    __read_sql__ = {}

    @classmethod
    def redpanda(cls, entities=None, session=None):
        """ Create RedPanda object. """
        entities = cls if entities is None else entities
        return cls.__redpanda__(entities, session, **cls.__read_sql__)

    @classmethod
    def redparse(cls, dataframe, parse_index=False):
        """ Return a generator for SQLAlchemy models from a pandas.DataFrame.

            Arguments:
                dataframe   (pandas.DataFrame): pandas.DataFrame to parse
                parse_index (boolean):          parse the index as a model attribute

            Returns:
                Generator of SQLAlchemy objects. """
        for ix, row in dataframe.iterrows():
            attrs = row.dropna().to_dict()
            if parse_index is True:
                assert dataframe.index.name is not None, "Cannot parse unnamed index"
                attrs[dataframe.index.name] = ix
            yield cls(**attrs)

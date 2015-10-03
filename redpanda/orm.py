""" Custom ORM behavior. """


import pandas
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declared_attr
from . import dialects


START_INCLUSIVE = 2
END_INCLUSIVE   = 4
START_EXCLUSIVE = 8
END_EXCLUSIVE   = 16


class RedPandaMixin(object):
    """ Custom SQLAlchemy Base. """
    index_col    = None
    coerce_float = True
    parse_dates  = None
    columns      = None
    chunksize    = None

    @classmethod
    def frame(cls, engine, query=None):
        """ Frame the results of a query in a pandas.DataFrame.

            Arguments:
                engine  (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
                query   (sqlalchemy.orm.Query)      Optional query

            Returns:
                pandas.DataFrame of results. """
        query       = query or sqlalchemy.orm.Query(cls)
        sql, params = dialects.statement_and_params(engine, query)
        frame       = pandas.read_sql(
            sql          = str(sql),
            con          = engine,
            index_col    = cls.index_col,
            coerce_float = cls.coerce_float,
            params       = params,
            parse_dates  = cls.parse_dates,
            columns      = cls.columns,
            chunksize    = cls.chunksize )
        return frame


class TimestampedMixin(RedPandaMixin):
    """ Model that can be transformed into a pandas datetime-indexed row. """
    timestamp_col = 'timestamp'

    @declared_attr
    def timestamp(cls):
        raise NotImplementedError(
            "<TimestampedMixin> objects must define a 'timestamp' column or synonym")


    @classmethod
    def query_between(cls, start, end, how=None, query=None):
        query = query or sqlalchemy.orm.Query(cls)

        # Bound query
        if how is None or how == START_INCLUSIVE|END_INCLUSIVE:
            query = query.filter(cls.timestamp>=start).filter(cls.timestamp<=end)
        elif how == START_INCLUSIVE|END_EXCLUSIVE:
            query = query.filter(cls.timestamp>=start).filter(cls.timestamp<end)
        elif how == START_EXCLUSIVE|END_INCLUSIVE:
            query = query.filter(cls.timestamp>start).filter(cls.timestamp<=end)
        elif how == START_EXCLUSIVE|END_EXCLUSIVE:
            query = query.filter(cls.timestamp>start).filter(cls.timestamp<end)
        else:
            raise ValueError("how must be bitwise-or of start/end inclusive/exclusive constants")

        return query


    @classmethod
    def between(cls, engine, start, end, how=START_INCLUSIVE|END_INCLUSIVE, query=None):
        """ Find records with <index_col> between start & end (end-inclusive by default)
            and return them as a DataFrame.

            Arguments:
                engine  (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
                start   (str)                       Start of time filter
                end     (str)                       End of time filter
                how     (int)                       Start/End inclusive/exclusive
                query   (sqlalchemy.orm.Query)      Optional query

            Returns:
                pandas.DataFrame of results. """
        query = query or cls.query_between(start, end, how)
        frame = cls.frame(engine, query).set_index(cls.timestamp_col)
        return frame


class PeriodicMixin(RedPandaMixin):
    """ Model that can be transformed into a pandas period-indexed row. """

    @declared_attr
    def period_start(cls):
        raise NotImplementedError(
            "<PeriodicMixin> objects must define 'period_start' column or synonym")

    @declared_attr
    def period_end(cls):
        raise NotImplementedError(
            "<PeriodicMixin> objects must define 'period_end' column or synonym")

    @classmethod
    def find_asof(cls, engine, timestamp, query=None):
        """ Find records as of a given timestamp and return them as a DataFrame. """
        query = (query or sqlalchemy.orm.Query(cls))\
            .filter(cls.period_start<=timestamp)\
            .filter((cls.period_end>timestamp)|(cls.period_end.is_(None)))

        return cls.frame(engine, query)
""" Custom ORM behavior. """


import pandas
import sqlalchemy.orm
from . import dialects


START_INCLUSIVE = 2
END_INCLUSIVE   = 4
START_EXCLUSIVE = 8
END_EXCLUSIVE   = 16


class RedPanda(object):
    def __init__(self, ormcls, index_col=None, coerce_float=True, params=None,
        parse_dates=None, columns=None, chunksize=None):
        self.ormcls       = ormcls
        self.index_col    = index_col
        self.coerce_float = coerce_float
        self.parse_dates  = parse_dates
        self.columns      = columns
        self.chunksize    = chunksize

    def frame(self, engine, query=None):
        """ Frame the results of a query in a pandas.DataFrame.

            Arguments:
                engine  (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
                query   (sqlalchemy.orm.Query)      Optional query

            Returns:
                pandas.DataFrame of results. """
        query       = query or sqlalchemy.orm.Query(self.ormcls)
        sql, params = dialects.statement_and_params(engine, query)
        frame       = pandas.read_sql(
            sql          = str(sql),
            con          = engine,
            index_col    = self.index_col,
            coerce_float = self.coerce_float,
            params       = params,
            parse_dates  = self.parse_dates,
            columns      = self.columns,
            chunksize    = self.chunksize )
        return frame


class TimestampedRedPanda(RedPanda):
    def __init__(self, ormcls, timestamp_col, index_col=None, coerce_float=True,
        params=None, parse_dates=None, columns=None, chunksize=None):
        super(TimestampedRedPanda, self).__init__(
            ormcls, index_col, coerce_float, params, parse_dates, columns, chunksize)
        self.timestamp_col = timestamp_col

    @property
    def timestamp(self):
        try:
            return self._timestamp
        except AttributeError:
            self._timestamp = getattr(self.ormcls, self.timestamp_col)
            return self._timestamp

    def query_between(self, start, end, how=None, query=None):
        query = query or sqlalchemy.orm.Query(self.ormcls)

        # Bound query
        if how is None or how == START_INCLUSIVE|END_INCLUSIVE:
            query = query.filter(self.timestamp>=start).filter(self.timestamp<=end)
        elif how == START_INCLUSIVE|END_EXCLUSIVE:
            query = query.filter(self.timestamp>=start).filter(self.timestamp<end)
        elif how == START_EXCLUSIVE|END_INCLUSIVE:
            query = query.filter(self.timestamp>start).filter(self.timestamp<=end)
        elif how == START_EXCLUSIVE|END_EXCLUSIVE:
            query = query.filter(self.timestamp>start).filter(self.timestamp<end)
        else:
            raise ValueError("how must be bitwise-or of start/end inclusive/exclusive constants")

        return query

    def between(self, engine, start, end, how=START_INCLUSIVE|END_INCLUSIVE, query=None):
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
        query = query or self.query_between(start, end, how)
        frame = self.frame(engine, query).set_index(self.ormcls.timestamp_col)
        return frame


class PeriodicRedPanda(RedPanda):
    def __init__(self, ormcls, period_start_col, period_end_col, index_col=None,
        coerce_float=True, params=None, parse_dates=None, columns=None, chunksize=None):
        super(PeriodicRedPanda, self).__init__(
            ormcls, index_col, coerce_float, params, parse_dates, columns, chunksize)
        self.period_start_col = period_start_col
        self.period_end_col   = period_end_col

    @property
    def period_start(self):
        try:
            return self._period_start
        except AttributeError:
            self._period_start = getattr(self.ormcls, self.period_start_col)
            return self._period_start

    @property
    def period_end(self):
        try:
            return self._period_end
        except AttributeError:
            self._period_end = getattr(self.ormcls, self.period_end_col)
            return self._period_end

    def query_asof(self, timestamp, query=None):
        query = query or sqlalchemy.orm.Query(self.ormcls)
        query = query\
            .filter(self.period_start<=timestamp)\
            .filter((self.period_end>timestamp)|(self.period_end.is_(None)))

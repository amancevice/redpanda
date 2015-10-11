""" Custom ORM behavior. """


import pandas
from . import dialects
from . import timebox
from . import utils


class RedPanda(object):
    """ RedPanda pandas integration helper.

        Arguments:
            ormcls      (object):                   SQLAlchemy parent model
            engine      (sqlalchemy.engine.Engine): SQLAlchemy engine
            query       (sqlalchemy.orm.Query):     SQLAlchemy query
            read_sql    (dict):                     Arguments for pandas.read_sql() """
    def __init__(self, ormcls, engine, query, **read_sql):
        self.ormcls   = ormcls
        self.engine   = engine
        self.query    = query
        self.read_sql = read_sql

    def frame(self, *transformations):
        """ Transform into pandas.DataFrame instance.

            Arguments:
                transformations (tuple):    Transformation functions to apply to result

            Returns:
                pandas.DataFrame instance.
            """
        # Get engine-specific SQL and params
        sql, params = dialects.statement_and_params(self.engine, self.query)
        read_sql    = utils.dictcombine(self.read_sql, {'params' : params})
        # Read SQL into DataFrame
        dataframe   = pandas.read_sql(str(sql), self.engine, **read_sql)
        # Mask columns
        if self.read_sql.get('columns') is not None:
            dataframe = dataframe[self.read_sql['columns']]
        # Apply any transformations
        return reduce((lambda x, y: y(x)), transformations, dataframe)

    def parse(self, dataframe):
        """ Generate list of SQLAlchemy objects from pandas.DataFrame.

            Arguments:
                dataframe   (pandas.DataFrame): pandas.DataFrame to parse

            Returns:
                Generator of SQLAlchemy objects. """
        for ix, row in dataframe.iterrows():
            yield self.ormcls(**row.to_dict())

    def between(self, col, start, end, how=None):
        """ Alter RedPanda query to constrict by dates.

            Examples:
                between('created_at', '2015-01-01', '2015-07-01', '[]')
                between('created_at', '2015-01-01', '2015-07-01', '[)'))

            Arguments:
                col     (str):  Column or column name
                start   (str):  Start of timebox
                end     (str):  End of timebox
                how     (int):  Start/End inclusive/exclusive """
        if isinstance(col, str):
            col = getattr(self.ormcls, col)
        if isinstance(how, str):
            how = timebox.parse(how)
        if how is None or how == timebox.START_INCLUSIVE|timebox.END_INCLUSIVE:
            query = self.query.filter(col>=start).filter(col<=end)
        elif how == timebox.START_INCLUSIVE|timebox.END_EXCLUSIVE:
            query = self.query.filter(col>=start).filter(col<end)
        elif how == timebox.START_EXCLUSIVE|timebox.END_INCLUSIVE:
            query = self.query.filter(col>start).filter(col<=end)
        elif how == timebox.START_EXCLUSIVE|timebox.END_EXCLUSIVE:
            query = self.query.filter(col>start).filter(col<end)
        else:
            raise ValueError("how must be bitwise-or of start/end inclusive/exclusive constants")
        return type(self)(self.ormcls, self.engine, query, **self.read_sql)

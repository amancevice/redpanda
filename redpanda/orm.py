""" Custom ORM behavior. """


import pandas
from . import dialects
from . import utils


class RedPanda(object):
    """ RedPanda pandas integration helper.

        Arguments:
            ormcls      (object):                   SQLAlchemy parent model
            engine      (sqlalchemy.engine.Engine): SQLAlchemy engine
            query       (sqlalchemy.orm.Query):     Optional SQLAlchemy refinement query
            read_sql    (dict):                     Arguments for pandas.read_sql() """
    def __init__(self, engine, query, **read_sql):
        self.engine   = engine
        self.query    = query
        self.read_sql = read_sql

    def frame(self, *transformations):
        """ Return RedPanda pandas.DataFrame instance. """
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

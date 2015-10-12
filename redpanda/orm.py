""" Custom ORM behavior. """


import pandas
import sqlalchemy.orm
from . import dialects
from . import timebox
from . import utils


class RedPanda(object):
    """ RedPanda pandas integration helper.

        Arguments:
            ormcls      (object):                   SQLAlchemy parent model
            engine      (sqlalchemy.engine.Engine): SQLAlchemy engine
            query       (sqlalchemy.orm.Query):     Optional SQLAlchemy refinement query
            read_sql    (dict):                     Arguments for pandas.read_sql() """
    def __init__(self, ormcls, engine, query=None, **read_sql):
        self.ormcls   = ormcls
        self.engine   = engine
        self.query    = query or sqlalchemy.orm.Query(ormcls)
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

    def parse(self, dataframe, parse_index=False):
        """ Generate list of SQLAlchemy objects from pandas.DataFrame.

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
            yield self.ormcls(**attrs)

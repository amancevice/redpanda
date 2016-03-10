""" Custom ORM behavior. """


import pandas
import sqlalchemy.orm
from . import dialects


class RedPanda(sqlalchemy.orm.Query):
    """ Subclass of the SQLAlchemy Query. """
    def __init__(self, entities=None, session=None, **read_sql):
        super(RedPanda, self).__init__(entities, session)
        self._read_sql = read_sql

    def frame(self, engine=None, **read_sql):
        """ Return RedPanda pandas.DataFrame instance. """

        # Get SQL+params from engine
        engine = engine or (self.session and self.session.bind)
        sql, params = dialects.statement_and_params(engine, self)

        # Get read_sql arguments
        dictcombine = lambda *x: {k: v for d in x for k, v in d.iteritems()}
        read_sql = dictcombine(self._read_sql, {'params':params}, read_sql)

        # Read SQL into DataFrame
        dataframe = pandas.read_sql(str(sql), engine, **read_sql)
        if read_sql.get('columns') is not None:
            dataframe = dataframe[read_sql['columns']]
        return dataframe

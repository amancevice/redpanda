""" Custom ORM behavior. """


import numpy
import pandas
import sqlalchemy.orm
from . import dialects
from . import utils


class RedPanda(sqlalchemy.orm.Query):
    def __init__(self, entities=None, session=None, **read_sql):
        super(RedPanda, self).__init__(entities, session)
        self._read_sql = read_sql

    def frame(self, engine=None, **read_sql):
        """ Return RedPanda pandas.DataFrame instance. """
        engine      = engine or (self.session and self.session.bind)
        sql, params = dialects.statement_and_params(engine, self)
        read_sql    = utils.dictcombine(self._read_sql, {'params':params}, read_sql)
        dataframe   = pandas.read_sql(str(sql), engine, **read_sql)
        if read_sql.get('columns') is not None:
            dataframe = dataframe[read_sql['columns']]
        return dataframe

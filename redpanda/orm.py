""" Custom ORM behavior. """


import numpy
import pandas
import sqlalchemy.orm
from . import dialects
from . import utils
from . import engine as bind


class RedPanda(sqlalchemy.orm.Query):
    def __init__(self, entities=None, session=None, engine=None, **read_sql):
        super(RedPanda, self).__init__(entities, session)
        self.engine    = engine or (session and session.bind)
        self._read_sql = read_sql

    def frame(self, **read_sql):
        """ Return RedPanda pandas.DataFrame instance. """
        sql, params = dialects.statement_and_params(self.engine, self)
        read_sql    = utils.dictcombine(self._read_sql, {'params':params}, read_sql)
        dataframe   = pandas.read_sql(str(sql), self.engine, **read_sql)
        if read_sql.get('columns') is not None:
            dataframe = dataframe[read_sql['columns']]
        if read_sql.get('coerce_float') is not None:
            coerce_float = read_sql.get('coerce_float')
            dataframe[coerce_float] = dataframe[coerce_float].applymap(numpy.float)
        return dataframe

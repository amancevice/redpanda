""" Custom ORM behavior. """


import pandas
import sqlalchemy.orm
from . import dialects
from . import utils


class RedPanda(sqlalchemy.orm.Query):
    def __init__(self, parent, entities=None, session=None):
        super(RedPanda, self).__init__(entities or parent, session)
        self._parent = parent

    def frame(self, engine, **read_sql):
        """ Return RedPanda pandas.DataFrame instance. """
        __read_sql__ = self._parent.__read_sql__
        sql, params  = dialects.statement_and_params(engine, self)
        read_sql     = utils.dictcombine(__read_sql__, {'params':params or None}, read_sql)
        dataframe    = pandas.read_sql(str(sql), engine, **read_sql)
        if read_sql.get('columns') is not None:
            dataframe = dataframe[read_sql['columns']]
        return dataframe

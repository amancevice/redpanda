""" Custom ORM behavior. """


import pandas
import sqlalchemy.orm
from . import dialects


class Query(sqlalchemy.orm.Query):
    """ RedPanda SQLAlchemy Query.

        Adds the frame() method to queries.
    """
    def __init__(self, entities, session=None, read_sql=None):
        super(Query, self).__init__(entities, session)
        self._read_sql = read_sql

    def frame(self, **read_sql):
        """ Return RedPanda pandas.DataFrame instance. """

        # Get conecion
        conn = self.session.connection()

        # Get SQL+params from engine
        sql, params = dialects.statement_and_params(conn.engine, self)

        # Get read_sql arguments
        dictcombine = lambda *x: {k: v for d in x for k, v in d.items()}
        read_sql = dictcombine(self._read_sql or {}, {"params":params}, read_sql)

        # Read SQL into DataFrame
        dataframe = pandas.read_sql(str(sql), conn.engine, **read_sql)
        if read_sql.get("columns") is not None:
            dataframe = dataframe[read_sql["columns"]]
        return dataframe


class _Session(sqlalchemy.orm.Session):
    """ RedPanda SQLAlchemy Session.

        Adds add_dataframe() method to session to parse a DataFrame into models.
    """
    def query(self, *entities, **kwargs):
        if len(entities) == 1:
            try:
                kwargs.setdefault("read_sql", entities[0].__read_sql__)
            except AttributeError:
                pass
        return super(_Session, self).query(*entities, **kwargs)

    def add_dataframe(self, cls, dataframe, parse_index=False):
        """ Return a generator for SQLAlchemy models from a pandas.DataFrame.

            Arguments:
                cls         (class):            Target model for DataFrame
                dataframe   (pandas.DataFrame): pandas.DataFrame to parse
                parse_index (boolean):          parse the index as a model attribute

            Returns:
                Generator of SQLAlchemy objects. """

        for idx, row in dataframe.iterrows():
            attrs = row.dropna().to_dict()
            if parse_index is True:
                if dataframe.index.name is None:
                    raise ValueError("Cannot parse unnamed index")
                attrs[dataframe.index.name] = idx
            self.add(cls(**attrs))


def sessionmaker(*args, **kwargs):
    """ Override of sqlalchemy.orm.sessionmaker to use RedPanda Session/Query. """
    kwargs.setdefault("query_cls", Query)
    kwargs.setdefault("class_", _Session)
    return sqlalchemy.orm.sessionmaker(*args, **kwargs)


# pylint: disable=invalid-name
Session = sessionmaker()

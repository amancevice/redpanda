"""
Custom ORM behavior.
"""
import pandas
import sqlalchemy.orm

from redpanda import dialects


class Query(sqlalchemy.orm.Query):
    """
    RedPanda SQLAlchemy Query.

    Adds the frame() method to queries.
    """
    def __init__(self, entities, session=None, read_sql=None):
        super(Query, self).__init__(entities, session)
        if read_sql is None:
            try:
                entity_zero, *_ = entities
                read_sql = entity_zero.__read_sql__
            except (AttributeError, TypeError, ValueError):
                read_sql = {}
        self._read_sql = read_sql

    def frame(self, **read_sql):
        """
        Return RedPanda pandas.DataFrame instance.
        """
        # Get conecion
        conn = self.session.connection()

        # Get SQL+params from engine
        sql, params = dialects.statement_and_params(conn.engine, self)

        # Get read_sql arguments
        read_sql = {**self._read_sql, **{'params': params}, **read_sql}

        # Read SQL into DataFrame
        dataframe = pandas.read_sql(str(sql), conn.engine, **read_sql)
        if read_sql.get('columns') is not None:
            dataframe = dataframe[read_sql['columns']]
        return dataframe


class Session(sqlalchemy.orm.Session):
    """
    RedPanda SQLAlchemy Session.

    Adds add_dataframe() method to session.
    """
    def add_dataframe(self, cls, dataframe, parse_index=False):
        """
        Return a generator for SQLAlchemy models from a pandas.DataFrame.

        :param class cls:                   Target model for DataFrame
        :param pandas.DataFrame dataframe:  pandas.DataFrame to parse
        :param boolean parse_index:         parse the index as a model attr
        :returns iter:                      Generator of SQLAlchemy objects.
        """
        for idx, row in dataframe.iterrows():
            attrs = row.dropna().to_dict()
            if parse_index is True:
                if dataframe.index.name is None:
                    raise ValueError('Cannot parse unnamed index')
                attrs[dataframe.index.name] = idx
            self.add(cls(**attrs))


def sessionmaker(class_=Session, query_cls=Query, **kwargs):
    """
    Override of sqlalchemy.orm.sessionmaker to use RedPanda Session/Query.
    """
    return sqlalchemy.orm.sessionmaker(
        class_=class_, query_cls=query_cls, **kwargs)


def within(self, index):
    """
    Like between() but takes a pandas index object.

    :param pandas.Index index: pandas index
    :returns self: result of between() with start/end as the ends of the index.
    """
    try:
        start = index.min().start_time
        end = index.max().end_time
    except AttributeError:
        start = index.min()
        end = index.max()
    return self.between(start, end)


sqlalchemy.orm.attributes.InstrumentedAttribute.within = within

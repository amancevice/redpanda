""" Dialect parameter generators. """


import sys
from datetime import date
from datetime import datetime


def __default__(statement):
    """ Default parameter generator for SQLAlchemy statement. """
    return statement.params


def __sqlalchemy__dialects__mysql__mysqldb__MySQLDialect_mysqldb__(statement):
    """ MySQL parameter generator for SQLAlchemy statement. """
    return tuple(statement.params[k] for k in statement.positiontup)


def __sqlalchemy__dialects__sqlite__pysqlite__SQLiteDialect_pysqlite__(statement):
    """ SQLite3 parameter generator for SQLite3 statement. """
    def iterhelper(params, positiontup):
        for key in positiontup:
            # SQLite seems to dislike datetime
            if isinstance(params[key], datetime) or isinstance(params[key], date):
                yield str(params[key])
            else:
                yield params[key]
    return tuple(iterhelper(statement.params, statement.positiontup))


def add(dialect, func):
    """ Add a parameter generator for a given dialect class.

        Arguments:
            dialect (class):    SQLAlchemy dialect class
            func    (lambda):   Function to process statement into params

        Returns:
            The response of setattr()"""
    method = '__'.join([''] + dialect.__module__.split('.') + [dialect.__name__, ''])
    module = sys.modules[__name__]
    return setattr(module, method, func)


def params(engine, statement):
    """ Parameter generator for a given SQLAlchemy engine + statement.

        Arguments:
            engine      (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
            statement   (sqlalchemy.dialect.?)      Compiled SQLAlchemy statement

        Returns:
            Parameters in engine-specific format. """
    assert engine is not None, "No engine supplied"
    dialect   = type(engine.dialect)
    method    = '__'.join([''] + dialect.__module__.split('.') + [dialect.__name__, ''])
    generator = globals().get(method, __default__)
    return generator(statement) or None


def statement(engine, query):
    """ Statement compiler for a given SQLAlchemy engine + query.

        Arguments:
            engine  (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
            query   (sqlalchemy.orm.Query)      SQLAlchemy query

        Returns:
            Compiled engine-specific statement. """
    statement = query.statement.compile(engine)
    statement.compile()
    return statement


def statement_and_params(engine, query):
    """ Get compiled statement with params for a given SQLAlchemy engine + query

        Arguments:
            engine  (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
            query   (sqlalchemy.orm.Query)      SQLAlchemy query

        Returns:
            Tuple of statement, params. """
    stmt = statement(engine, query)
    prms = params(engine, stmt)
    return stmt, prms

""" Dialect parameter generators. """


from datetime import date
from datetime import datetime


def __default__(stmt):
    """ Default parameter generator for SQLAlchemy statement. """
    return stmt.params


def __mysql__(stmt):
    """ MySQL parameter generator for SQLAlchemy statement. """
    return tuple(stmt.params[k] for k in stmt.positiontup)


def __sqlite__(stmt):
    """ SQLite3 parameter generator for SQLite3 statement. """
    def iterhelper(args, positiontup):
        """ Helper for params. """
        for key in positiontup:
            # SQLite seems to dislike datetime
            if isinstance(args[key], datetime) or isinstance(args[key], date):
                yield str(args[key])
            else:
                yield args[key]
    return tuple(iterhelper(stmt.params, stmt.positiontup))


__dialects__ = {
    "sqlalchemy.dialects.mysql.mysqldb.MySQLDialect_mysqldb": __mysql__,
    "sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite": __sqlite__}


def add(dialect, func):
    """ Add a parameter generator for a given dialect class.

        Arguments:
            dialect (class):    SQLAlchemy dialect class
            func    (lambda):   Function to process statement into params
    """
    key = "%s.%s" % (dialect.__module__, dialect.__name__)
    __dialects__[key] = func


def params(engine, stmt):
    """ Parameter generator for a given SQLAlchemy engine + statement.

        Arguments:
            engine (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
            stmt   (sqlalchemy.dialect.?)      Compiled SQLAlchemy statement

        Returns:
            Parameters in engine-specific format. """
    assert engine is not None, "No engine supplied"
    dialect = type(engine.dialect)
    key = "%s.%s" % (dialect.__module__, dialect.__name__)
    generator = __dialects__.get(key, __default__)
    return generator(stmt) or None


def statement(engine, query):
    """ Statement compiler for a given SQLAlchemy engine + query.

        Arguments:
            engine  (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
            query   (sqlalchemy.orm.Query)      SQLAlchemy query

        Returns:
            Compiled engine-specific statement. """
    stmt = query.statement.compile(engine)
    stmt.compile()
    return stmt


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

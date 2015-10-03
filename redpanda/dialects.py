""" Dialect parameter generators. """


def __default__(statement):
    """ Default parameter generator for SQLAlchemy statement. """
    return statement.params


def __sqlalchemy__dialects__mysql__mysqldb__MySQLDialect_mysqldb__(statement):
    """ MySQL parameter generator for SQLAlchemy statement. """
    return tuple(statement.params[k] for k in statement.positiontup)


def params(engine, statement):
    """ Parameter generator for a given SQLAlchemy engine + statement.

        Arguments:
            engine      (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
            statement   (sqlalchemy.dialect.?)      Compiled SQLAlchemy statement

        Returns:
            Parameters in engine-specific format. """
    dialect   = type(engine.dialect)
    method    = '__'.join([''] + dialect.__module__.split('.') + [dialect.__name__, ''])
    generator = globals().get(method, __default__)
    return generator(statement)

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
            engine      (sqlalchemy.engine.Engine)  SQLAlchemy connection engine
            statement   (sqlalchemy.dialect.?)      Compiled SQLAlchemy statement

        Returns:
            Tuple of statement, params. """
    stmt = statement(engine, query)
    prms = params(engine, stmt)
    return stmt, prms

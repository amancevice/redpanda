""" Test for dialect module. """

from datetime import datetime

import mock
import redpanda
import sqlalchemy
from nose.tools import assert_equal
from redpanda.example import Widget, create_widgets
from sqlalchemy.dialects.mysql import mysqldb
from sqlalchemy.dialects.postgresql import psycopg2


ENGINE = redpanda.create_engine("sqlite://")
SESSION = redpanda.orm.sessionmaker(bind=ENGINE)()
create_widgets(SESSION)


def test_default():
    query = sqlalchemy.orm.Query(Widget)\
        .filter(Widget.kind == "fizzer")\
        .filter(Widget.units > 10)
    statement = query.statement.compile(SESSION.bind)
    statement.compile()
    returned = redpanda.dialects._default(statement)
    expected = {"kind_1": "fizzer", "units_1": 10}
    assert_equal(returned, expected)


def test_sqlite():
    query = sqlalchemy.orm.Query(Widget)\
        .filter(Widget.kind == "fizzer")\
        .filter(Widget.units > 10)
    statement = query.statement.compile(SESSION.bind)
    statement.compile()
    dialect = "sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite"
    returned = redpanda.dialects.__dialects__[dialect](statement)
    expected = "fizzer", 10
    assert_equal(returned, expected)


def test_sqlite_date():
    query = sqlalchemy.orm.Query(Widget)\
        .filter(Widget.kind == "fizzer")\
        .filter(Widget.units > 10)\
        .filter(Widget.timestamp == datetime(2016, 11, 11, 11, 11, 11))
    statement = query.statement.compile(SESSION.bind)
    statement.compile()
    dialect = "sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite"
    returned = redpanda.dialects.__dialects__[dialect](statement)
    expected = "fizzer", 10, "2016-11-11 11:11:11.000000"
    assert_equal(returned, expected)


def test_mysql():
    query = sqlalchemy.orm.Query(Widget)\
        .filter(Widget.kind == "fizzer")\
        .filter(Widget.units > 10)
    statement = query.statement.compile(SESSION.bind)
    statement.compile()
    dialect = "sqlalchemy.dialects.mysql.mysqldb.MySQLDialect_mysqldb"
    returned = redpanda.dialects.__dialects__[dialect](statement)
    expected = "fizzer", 10
    assert_equal(returned, expected)


def test_add():

    class TestDialect(object):
        pass

    def test_func(statement):
        return "foo", "bar"

    redpanda.dialects.add(TestDialect, test_func)
    dialect = "tests.dialect_test.TestDialect"
    returned = redpanda.dialects.__dialects__[dialect](None)
    expected = "foo", "bar"
    assert_equal(returned, expected)


@mock.patch("sqlalchemy.engine.base.Engine")
@mock.patch("sqlalchemy.sql.compiler.Compiled")
def test_params_mysql(mock_statement, mock_engine):
    mock_engine.dialect = \
        sqlalchemy.dialects.mysql.mysqldb.MySQLDialect_mysqldb()
    mock_statement.params = {"param1": "val1", "param2": "val2"}
    mock_statement.positiontup = ("param1", "param2")
    returned = redpanda.dialects.params(mock_engine, mock_statement)
    expected = "val1", "val2"
    assert_equal(returned, expected)


@mock.patch("sqlalchemy.engine.base.Engine")
@mock.patch("sqlalchemy.sql.compiler.Compiled")
def test_params_sqlite(mock_statement, mock_engine):
    mock_engine.dialect = \
        sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite()
    mock_statement.params = {"param1": "val1", "param2": "val2"}
    mock_statement.positiontup = ("param1", "param2")
    returned = redpanda.dialects.params(mock_engine, mock_statement)
    expected = "val1", "val2"
    assert_equal(returned, expected)


@mock.patch("sqlalchemy.engine.base.Engine")
@mock.patch("sqlalchemy.sql.compiler.Compiled")
def test_params_postgres(mock_statement, mock_engine):
    mock_engine.dialect = \
        sqlalchemy.dialects.postgresql.psycopg2.PGDialect_psycopg2()
    mock_statement.params = {"param1": "val1", "param2": "val2"}
    returned = redpanda.dialects.params(mock_engine, mock_statement)
    expected = {"param1": "val1", "param2": "val2"}
    assert_equal(returned, expected)
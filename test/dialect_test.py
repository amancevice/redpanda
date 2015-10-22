""" Test for dialect module. """


import mock
import redpanda
import sqlalchemy
from nose.tools import assert_equal
from sqlalchemy.dialects.mysql import mysqldb
from sqlalchemy.dialects.postgresql import psycopg2
from . import db

def test_default():
    query = sqlalchemy.orm.Query(db.Widget)\
        .filter(db.Widget.kind=='fizzer')\
        .filter(db.Widget.units>10)
    statement = query.statement.compile(db.ENGINE)
    statement.compile()
    returned = redpanda.dialects.__default__(statement)
    expected = {'kind_1': 'fizzer', 'units_1': 10}
    assert_equal(returned, expected)


def test_sqlite():
    query = sqlalchemy.orm.Query(db.Widget)\
        .filter(db.Widget.kind=='fizzer')\
        .filter(db.Widget.units>10)
    statement = query.statement.compile(db.ENGINE)
    statement.compile()
    returned = redpanda.dialects\
        .__sqlalchemy__dialects__sqlite__pysqlite__SQLiteDialect_pysqlite__(statement)
    expected = 'fizzer', 10
    assert_equal(returned, expected)


def test_mysql():
    query = sqlalchemy.orm.Query(db.Widget)\
        .filter(db.Widget.kind=='fizzer')\
        .filter(db.Widget.units>10)
    statement = query.statement.compile(db.ENGINE)
    statement.compile()
    returned = redpanda.dialects\
        .__sqlalchemy__dialects__mysql__mysqldb__MySQLDialect_mysqldb__(statement)
    expected = 'fizzer', 10
    assert_equal(returned, expected)


def test_add():
    class TestDialect(object):
        pass
    def test_func(statement):
        return 'foo', 'bar'
    redpanda.dialects.add(TestDialect, test_func)
    returned = redpanda.dialects.__test__dialect_test__TestDialect__(None)
    expected = 'foo', 'bar'
    assert_equal(returned, expected)


@mock.patch('sqlalchemy.engine.base.Engine')
@mock.patch('sqlalchemy.sql.compiler.Compiled')
def test_params_mysql(mock_statement, mock_engine):
    mock_engine.dialect        = sqlalchemy.dialects.mysql.mysqldb.MySQLDialect_mysqldb()
    mock_statement.params      = {'param1' : 'val1', 'param2' : 'val2'}
    mock_statement.positiontup = ('param1', 'param2')
    returned = redpanda.dialects.params(mock_engine, mock_statement)
    expected = 'val1', 'val2'
    assert_equal(returned, expected)


@mock.patch('sqlalchemy.engine.base.Engine')
@mock.patch('sqlalchemy.sql.compiler.Compiled')
def test_params_sqlite(mock_statement, mock_engine):
    mock_engine.dialect        = sqlalchemy.dialects.sqlite.pysqlite.SQLiteDialect_pysqlite()
    mock_statement.params      = {'param1' : 'val1', 'param2' : 'val2'}
    mock_statement.positiontup = ('param1', 'param2')
    returned = redpanda.dialects.params(mock_engine, mock_statement)
    expected = 'val1', 'val2'
    assert_equal(returned, expected)


@mock.patch('sqlalchemy.engine.base.Engine')
@mock.patch('sqlalchemy.sql.compiler.Compiled')
def test_params_postgres(mock_statement, mock_engine):
    mock_engine.dialect        = sqlalchemy.dialects.postgresql.psycopg2.PGDialect_psycopg2()
    mock_statement.params      = {'param1' : 'val1', 'param2' : 'val2'}
    returned = redpanda.dialects.params(mock_engine, mock_statement)
    expected = {'param1' : 'val1', 'param2' : 'val2'}
    assert_equal(returned, expected)

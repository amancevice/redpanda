""" Test for dialect module. """


import datetime
import mock
import random
import redpanda.dialects
import redpanda.mixins
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
from nose.tools import assert_equal
from sqlalchemy.dialects import *


# Create an in-memory SQLite engine
ENGINE = sqlalchemy.create_engine('sqlite://', echo=True)

# SQLAlchemy declarative base
Base = sqlalchemy.ext.declarative.declarative_base()

# Declare our model
class Widget(redpanda.mixins.RedPandaMixin, Base):
    __tablename__ = 'widgets'
    id            = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp     = sqlalchemy.Column(sqlalchemy.DateTime)
    name          = sqlalchemy.Column(sqlalchemy.String)
    kind          = sqlalchemy.Column(sqlalchemy.String)
    units         = sqlalchemy.Column(sqlalchemy.Integer)

    # Class-defined RedPanda read_sql() arguments
    # This allows us to forego passing these into Widget.redpanda()
    __read_sql__ = {
        'index_col'   : ['timestamp'],
        'parse_dates' : ['timestamp'] }

    def __repr__(self):
        return "<Widget id: %s timestamp: '%s' name: '%s' kind: '%s' units: %d>" % \
            (self.id, self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                self.name, self.kind, self.units)


def setup():
    def randdate(maxday=31):
        """ Generate a random datetime. """
        year = 2015
        month = random.randint(0,12) + 1
        day   = random.randint(0,maxday) + 1
        hour  = random.randint(0,24)
        minute = random.randint(0,60)
        try:
            return datetime.datetime(year, month, day, hour, minute)
        except ValueError:
            return randdate(maxday-1)

    def widgetgen():
        """ Generate a set of widgets. """
        kinds   = 'fizzer', 'buzzer', 'bopper'
        for i in range(0,25):
            for kind in kinds:
                name      = "%s-%d" % (kind, i)
                timestamp = randdate()
                units     = random.randint(0,100)
                yield Widget(timestamp=timestamp, name=name, kind=kind, units=units)

    # Set up our database
    Base.metadata.create_all(ENGINE)
    sessionmaker = sqlalchemy.orm.sessionmaker(bind=ENGINE)
    sessiongen   = sqlalchemy.orm.scoped_session(sessionmaker)
    session      = sessiongen()
    map(session.add, sorted(widgetgen(), key=lambda x: x.timestamp))
    session.commit()


def test_default():
    query = sqlalchemy.orm.Query(Widget)\
        .filter(Widget.kind=='fizzer')\
        .filter(Widget.units>10)
    statement = query.statement.compile(ENGINE)
    statement.compile()
    returned = redpanda.dialects.__default__(statement)
    expected = {'kind_1': 'fizzer', 'units_1': 10}
    assert_equal(returned, expected)


def test_sqlite():
    query = sqlalchemy.orm.Query(Widget)\
        .filter(Widget.kind=='fizzer')\
        .filter(Widget.units>10)
    statement = query.statement.compile(ENGINE)
    statement.compile()
    returned = redpanda.dialects\
        .__sqlalchemy__dialects__sqlite__pysqlite__SQLiteDialect_pysqlite__(statement)
    expected = 'fizzer', 10
    assert_equal(returned, expected)


def test_mysql():
    query = sqlalchemy.orm.Query(Widget)\
        .filter(Widget.kind=='fizzer')\
        .filter(Widget.units>10)
    statement = query.statement.compile(ENGINE)
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

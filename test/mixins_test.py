""" Test for mixins module. """

import datetime
import mock
import pandas
import random
import redpanda.orm
import sqlalchemy
from copy import copy
from nose.tools import assert_equal
from nose.tools import assert_is_instance
from nose.tools import raises


class MyRedPanda(redpanda.orm.RedPanda):
    pass


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
    __redpanda__ = MyRedPanda
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


def test_redpanda_customizer():
    returned = Widget.redpanda()
    assert_is_instance(returned, MyRedPanda)


@mock.patch('pandas.read_sql')
def test_read_sql_customizer(mock_read_sql):
    Widget.redpanda().frame(ENGINE)
    kwargs = Widget.__read_sql__
    kwargs['params'] = None
    sql = "SELECT widgets.id, widgets.timestamp, widgets.name, widgets.kind, widgets.units \n" +\
        "FROM widgets"
    mock_read_sql.assert_called_with(sql, ENGINE, **kwargs)


@mock.patch('pandas.read_sql')
def test_read_sql_argument_override(mock_read_sql):
    Widget.redpanda().frame(ENGINE, index_col='foo')
    kwargs = copy(Widget.__read_sql__)
    kwargs['index_col'] = 'foo'
    kwargs['params']    = None
    sql = "SELECT widgets.id, widgets.timestamp, widgets.name, widgets.kind, widgets.units \n" +\
        "FROM widgets"
    mock_read_sql.assert_called_with(sql, ENGINE, **kwargs)

def test_redpanda():
    returned = Widget.redpanda()
    expected = MyRedPanda(Widget, Widget)
    assert_equal(str(returned), str(expected))


def test_redpanda_with_query():
    returned = Widget.redpanda().filter(Widget.kind=='buzzer')
    expected = MyRedPanda(Widget).filter(Widget.kind=='buzzer')
    assert_equal(str(returned), str(expected))


def test_redparse():
    frame = pandas.DataFrame({
        datetime.datetime.utcnow() : {"name" : "foo", "kind" : "fizzer", "units" : 10 },
        datetime.datetime.utcnow() : {"name" : "goo", "kind" : "buzzer", "units" : 11 },
        datetime.datetime.utcnow() : {"name" : "hoo", "kind" : "bopper", "units" : 12 }
    }).T
    frame.index.name = 'timestamp'

    widget1, widget2, widget3 = list(Widget.redparse(frame, parse_index=True))
    assert_equal(widget1.name, 'foo')
    assert_equal(widget1.kind, 'fizzer')
    assert_equal(widget1.units, 10)
    assert_equal(widget2.name, 'goo')
    assert_equal(widget2.kind, 'buzzer')
    assert_equal(widget2.units, 11)
    assert_equal(widget3.name, 'hoo')
    assert_equal(widget3.kind, 'bopper')
    assert_equal(widget3.units, 12)


@raises(AssertionError)
def test_redparse_exception():
    frame = pandas.DataFrame({
        datetime.datetime.utcnow() : {"name" : "foo", "kind" : "fizzer", "units" : 10 },
        datetime.datetime.utcnow() : {"name" : "goo", "kind" : "buzzer", "units" : 11 },
        datetime.datetime.utcnow() : {"name" : "hoo", "kind" : "bopper", "units" : 12 }
    }).T

    list(Widget.redparse(frame, parse_index=True))

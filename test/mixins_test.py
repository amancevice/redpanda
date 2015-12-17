""" Test for mixins module. """


import datetime
import mock
import numpy
import pandas
from copy import copy
from nose.tools import assert_equal
from nose.tools import assert_is_instance
from nose.tools import raises
from . import db


def test_redpanda_customizer():
    returned = db.Widget.redpanda()
    assert_is_instance(returned, db.MyRedPanda)


@mock.patch('pandas.read_sql')
def test_read_sql_customizer(mock_read_sql):
    db.Widget.redpanda().frame(db.ENGINE)
    kwargs = db.Widget.__read_sql__
    kwargs['params'] = None
    sql = "SELECT widgets.id, widgets.timestamp, widgets.name, widgets.kind, widgets.units \n" +\
        "FROM widgets"
    mock_read_sql.assert_called_with(sql, db.ENGINE, **kwargs)


@mock.patch('pandas.read_sql')
def test_read_sql_argument_override(mock_read_sql):
    db.Widget.redpanda().frame(db.ENGINE, index_col='foo')
    kwargs = copy(db.Widget.__read_sql__)
    kwargs['index_col'] = 'foo'
    kwargs['params']    = None
    sql = "SELECT widgets.id, widgets.timestamp, widgets.name, widgets.kind, widgets.units \n" +\
        "FROM widgets"
    mock_read_sql.assert_called_with(sql, db.ENGINE, **kwargs)

def test_redpanda():
    returned = db.Widget.redpanda()
    expected = db.MyRedPanda(db.Widget, engine=db.ENGINE)
    assert_equal(str(returned), str(expected))


def test_redpanda_with_query():
    returned = db.Widget.redpanda().filter(db.Widget.kind=='buzzer')
    expected = db.MyRedPanda(db.Widget).filter(db.Widget.kind=='buzzer')
    assert_equal(str(returned), str(expected))


def test_redparse():
    frame = pandas.DataFrame({
        datetime.datetime.utcnow() : {"name" : "foo", "kind" : "fizzer", "units" : 10 },
        datetime.datetime.utcnow() : {"name" : "goo", "kind" : "buzzer", "units" : 11 },
        datetime.datetime.utcnow() : {"name" : "hoo", "kind" : "bopper", "units" : 12 },
        datetime.datetime.utcnow() : {"name" : "ioo", "kind" : "fopper", "units" : numpy.nan },
    }).T
    frame.index.name = 'timestamp'

    widget1, widget2, widget3, widget4 = list(db.Widget.redparse(frame, parse_index=True))
    assert_equal(widget1.name, 'foo')
    assert_equal(widget1.kind, 'fizzer')
    assert_equal(widget1.units, 10)
    assert_equal(widget2.name, 'goo')
    assert_equal(widget2.kind, 'buzzer')
    assert_equal(widget2.units, 11)
    assert_equal(widget3.name, 'hoo')
    assert_equal(widget3.kind, 'bopper')
    assert_equal(widget3.units, 12)
    assert_equal(widget4.name, 'ioo')
    assert_equal(widget4.kind, 'fopper')
    assert_equal(widget4.units, None)


@raises(AssertionError)
def test_redparse_exception():
    frame = pandas.DataFrame({
        datetime.datetime.utcnow() : {"name" : "foo", "kind" : "fizzer", "units" : 10 },
        datetime.datetime.utcnow() : {"name" : "goo", "kind" : "buzzer", "units" : 11 },
        datetime.datetime.utcnow() : {"name" : "hoo", "kind" : "bopper", "units" : 12 }
    }).T

    list(db.Widget.redparse(frame, parse_index=True))

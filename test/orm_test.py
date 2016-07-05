""" Test for mixins module. """


from datetime import datetime
from copy import copy

import mock
import pandas
import redpanda
from nose.tools import assert_equal
from nose.tools import assert_is_instance
from nose.tools import raises
from pandas.util.testing import assert_frame_equal
from redpanda.example import Widget, create_widgets


ENGINE = redpanda.create_engine("sqlite://")
SESSION = redpanda.Session(bind=ENGINE)
create_widgets(SESSION)


def test_query():
    returned = str(SESSION.query(Widget))
    expected = "SELECT " +\
        "widgets.id AS widgets_id, widgets.timestamp AS widgets_timestamp, " + \
        "widgets.name AS widgets_name, widgets.kind AS widgets_kind, " + \
        "widgets.units AS widgets_units \n" + \
        "FROM widgets"
    assert_equal(returned, expected)


@raises(AttributeError)
def test_query_frame_error():
    redpanda.orm.Query(Widget).frame()


def test_query_frame_no_error():
    SESSION.query(Widget).frame()


@mock.patch("pandas.read_sql")
def test_read_sql_customizer(mock_read_sql):
    SESSION.query(Widget).frame()
    kwargs = Widget.__read_sql__
    kwargs["params"] = None
    sql = "SELECT widgets.id, widgets.timestamp, widgets.name, widgets.kind, widgets.units \n" +\
        "FROM widgets"
    mock_read_sql.assert_called_with(sql, SESSION.bind, **kwargs)


@mock.patch("pandas.read_sql")
def test_read_sql_argument_override(mock_read_sql):
    SESSION.query(Widget).frame(index_col="foo")
    kwargs = copy(Widget.__read_sql__)
    kwargs["index_col"] = "foo"
    kwargs["params"]    = None
    sql = "SELECT widgets.id, widgets.timestamp, widgets.name, widgets.kind, widgets.units \n" +\
        "FROM widgets"
    mock_read_sql.assert_called_with(sql, SESSION.bind, **kwargs)

def test_redpanda():
    returned = SESSION.query(Widget)
    expected = redpanda.orm.Query(Widget, session=SESSION)
    assert_equal(str(returned), str(expected))


def test_redpanda_with_query():
    returned = SESSION.query(Widget).filter(Widget.kind=="buzzer")
    expected = redpanda.orm.Query(Widget).filter(Widget.kind=="buzzer")
    assert_equal(str(returned), str(expected))


def test_add_dataframe():
    frame = pandas.DataFrame({
        datetime.utcnow(): {"id": 1, "name": "foo", "kind": "fizzer", "units": 10 },
        datetime.utcnow(): {"id": 2, "name": "goo", "kind": "buzzer", "units": 11 },
        datetime.utcnow(): {"id": 3, "name": "hoo", "kind": "bopper", "units": 12 },
        datetime.utcnow(): {"id": 4, "name": "ioo", "kind": "fopper", "units": pandas.np.nan },
    }).T
    frame.index.name = "timestamp"

    engine = redpanda.create_engine("sqlite://", convert_unicode=True)
    Widget.metadata.create_all(engine)
    session = redpanda.orm.Session(bind=engine)
    session.add_dataframe(Widget, frame, parse_index=True)
    session.commit()

    returned = session.query(Widget).frame()
    cols = sorted(returned.columns|frame.columns)
    assert_frame_equal(returned[cols], frame[cols], check_dtype=False)


@raises(ValueError)
def test_add_dataframe_exception():
    frame = pandas.DataFrame({
        datetime.utcnow() : {"name" : "foo", "kind" : "fizzer", "units" : pandas.np.int64(10) },
        datetime.utcnow() : {"name" : "goo", "kind" : "buzzer", "units" : pandas.np.int64(11) },
        datetime.utcnow() : {"name" : "hoo", "kind" : "bopper", "units" : pandas.np.int64(12) }
    }).T

    list(SESSION.add_dataframe(Widget, frame, parse_index=True))

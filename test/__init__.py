""" RedPanda Test Suite. """


import redpanda
from nose.tools import assert_equal, raises
from . import db


db.create_db()


def test_query():
    returned = str(redpanda.query(db.Widget))
    expected = "SELECT " +\
        "widgets.id AS widgets_id, widgets.timestamp AS widgets_timestamp, " + \
        "widgets.name AS widgets_name, widgets.kind AS widgets_kind, " + \
        "widgets.units AS widgets_units \n" + \
        "FROM widgets"
    assert_equal(returned, expected)


@raises(AssertionError)
def test_query_frame_error():
    redpanda.query(db.Widget).frame()


def test_query_frame_no_error():
    redpanda.query(db.Widget).frame(db.ENGINE)

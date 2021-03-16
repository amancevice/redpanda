"""
Tests for orm module.
"""
from datetime import datetime
from copy import copy
from unittest import mock

import numpy
import pandas
import redpanda
import sqlalchemy
from pandas.testing import assert_frame_equal
from pytest import raises
from redpanda.example import Widget, create_widgets


ENGINE = redpanda.create_engine('sqlite://')
SESSION = redpanda.orm.sessionmaker(bind=ENGINE)()


class NoReadSql(redpanda.example.Base):
    """
    Declare an example model.
    """
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    __tablename__ = 'no_read_sql'


class HasColumns(redpanda.example.Base):
    """
    Declare an example model.
    """
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    fizz = sqlalchemy.Column(sqlalchemy.Integer)
    buzz = sqlalchemy.Column(sqlalchemy.TIMESTAMP)
    __tablename__ = 'has_columns'
    __read_sql__ = {'columns': ['name', 'fizz', 'buzz']}


create_widgets(SESSION)


def test_query():
    returned = str(SESSION.query(Widget))
    expected = 'SELECT widgets.id AS widgets_id, ' \
        'widgets.timestamp AS widgets_timestamp, ' \
        'widgets.name AS widgets_name, widgets.kind AS widgets_kind, ' \
        'widgets.units AS widgets_units \n' \
        'FROM widgets'
    assert returned == expected


def test_query_no_entities():
    returned = SESSION.query()._read_sql
    expected = {}
    assert returned == expected


def test_query_no_read_sql():
    returned = SESSION.query(NoReadSql)._read_sql
    expected = {}
    assert returned == expected


def test_frame_columns():
    returned = SESSION.query(HasColumns).frame().columns
    expected = HasColumns.__read_sql__['columns']
    assert (returned == expected).all()


def test_query_frame_error():
    with raises(AttributeError) as err:
        redpanda.orm.Query(Widget).frame()
    assert "'NoneType' object has no attribute 'connection'" == str(err.value)


def test_query_frame_no_error():
    SESSION.query(Widget).frame()


@mock.patch('pandas.read_sql')
def test_read_sql_customizer(mock_read_sql):
    SESSION.query(Widget).frame()
    kwargs = Widget.__read_sql__
    kwargs['params'] = None
    sql = 'SELECT widgets.id, widgets.timestamp, widgets.name, ' \
        'widgets.kind, widgets.units \nFROM widgets'
    mock_read_sql.assert_called_with(sql, SESSION.bind, **kwargs)


@mock.patch('pandas.read_sql')
def test_read_sql_argument_override(mock_read_sql):
    SESSION.query(Widget).frame(index_col='foo')
    kwargs = copy(Widget.__read_sql__)
    kwargs['index_col'] = 'foo'
    kwargs['params'] = None
    sql = 'SELECT widgets.id, widgets.timestamp, widgets.name, ' \
        'widgets.kind, widgets.units \nFROM widgets'
    mock_read_sql.assert_called_with(sql, SESSION.bind, **kwargs)


def test_redpanda():
    returned = SESSION.query(Widget)
    expected = redpanda.orm.Query(Widget, session=SESSION)
    assert str(returned) == str(expected)


def test_redpanda_with_query():
    returned = SESSION.query(Widget).filter(Widget.kind == 'buzzer')
    expected = redpanda.orm.Query(Widget).filter(Widget.kind == 'buzzer')
    assert str(returned) == str(expected).replace(':kind_1', '?')


def test_add_dataframe():
    frame = pandas.DataFrame({
        datetime.utcnow(): {
            'id': 1, 'name': 'foo', 'kind': 'fizzer', 'units': 10},
        datetime.utcnow(): {
            'id': 2, 'name': 'goo', 'kind': 'buzzer', 'units': 11},
        datetime.utcnow(): {
            'id': 3, 'name': 'hoo', 'kind': 'bopper', 'units': 12},
        datetime.utcnow(): {
            'id': 4, 'name': 'ioo', 'kind': 'fopper', 'units': numpy.nan}
    }).T
    frame.index.name = 'timestamp'

    engine = redpanda.create_engine('sqlite://')
    Widget.metadata.create_all(engine)
    session = redpanda.orm.sessionmaker(bind=engine)()
    session.add_dataframe(Widget, frame, parse_index=True)
    session.commit()

    returned = session.query(Widget).frame()
    cols = sorted(returned.columns.union(frame.columns))
    assert_frame_equal(returned[cols], frame[cols], check_dtype=False)


def test_add_dataframe_exception():
    frame = pandas.DataFrame({
        datetime.utcnow(): {
            'name': 'foo', 'kind': 'fizzer', 'units': numpy.int64(10)},
        datetime.utcnow(): {
            'name': 'goo', 'kind': 'buzzer', 'units': numpy.int64(11)},
        datetime.utcnow(): {
            'name': 'hoo', 'kind': 'bopper', 'units': numpy.int64(12)}
    }).T

    with raises(ValueError) as err:
        list(SESSION.add_dataframe(Widget, frame, parse_index=True))
    assert 'Cannot parse unnamed index' == str(err.value)


@mock.patch('sqlalchemy.orm.attributes.InstrumentedAttribute.between')
def test_within_period_range_d(mock_between):
    index = pandas.period_range('2016-01-01', '2016-12-31', freq='D')
    Widget.timestamp.within(index)
    mock_between.assert_called_once_with(
        pandas.Timestamp('2016-01-01 00:00:00'),
        pandas.Timestamp('2016-12-31 23:59:59.999999999'))


@mock.patch('sqlalchemy.orm.attributes.InstrumentedAttribute.between')
def test_within_period_range_b(mock_between):
    index = pandas.period_range('2016-07-15', '2016-07-16', freq='B')
    Widget.timestamp.within(index)
    mock_between.assert_called_once_with(
        pandas.Timestamp('2016-07-15 00:00:00'),
        pandas.Timestamp('2016-07-18 23:59:59.999999999'))


@mock.patch('sqlalchemy.orm.attributes.InstrumentedAttribute.between')
def test_within_period_range_w(mock_between):
    index = pandas.period_range('2016-07-15', '2016-07-16', freq='W')
    Widget.timestamp.within(index)
    mock_between.assert_called_once_with(
        pandas.Timestamp('2016-07-11 00:00:00'),
        pandas.Timestamp('2016-07-17 23:59:59.999999999'))


@mock.patch('sqlalchemy.orm.attributes.InstrumentedAttribute.between')
def test_within_date_range(mock_between):
    index = pandas.date_range('2016-07-15', '2016-07-16').tz_localize('UTC')
    Widget.timestamp.within(index)
    mock_between.assert_called_once_with(
        pandas.Timestamp('2016-07-15 00:00:00', tz='UTC'),
        pandas.Timestamp('2016-07-16 00:00:00', tz='UTC'))

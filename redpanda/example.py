""" Example Model Setup """


import random
from datetime import datetime

import random_words
import sqlalchemy.ext.declarative
from . import orm


# pylint: disable=invalid-name
Base = sqlalchemy.ext.declarative.declarative_base()


# pylint: disable=too-few-public-methods
class Widget(Base):
    """ Declare an example model. """
    # pylint: disable=invalid-name
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime)
    name = sqlalchemy.Column(sqlalchemy.String)
    kind = sqlalchemy.Column(sqlalchemy.String)
    units = sqlalchemy.Column(sqlalchemy.Integer)
    __read_sql__ = {"index_col": ["timestamp"], "parse_dates": ["timestamp"]}
    __tablename__ = "widgets"


def randtime(maxday=31):
    """ Generate a random datetime. """
    month = random.randint(0, 12) + 1
    day = random.randint(0, maxday) + 1
    hour = random.randint(0, 24)
    minute = random.randint(0, 60)
    try:
        return datetime(2016, month, day, hour, minute)
    except ValueError:
        return randtime(maxday-1)


def widgetgen(maxiter=25):
    """ Generate a set of widgets. """
    wordgen = random_words.RandomWords()
    kinds = "fizzer", "buzzer", "bopper"
    for kind in kinds * maxiter:
        name = wordgen.random_word()
        units = random.randint(0, 100)
        yield Widget(timestamp=randtime(), name=name, kind=kind, units=units)


def create_widgets(session=None):
    """ Create all in engine. """
    if session is None:
        engine = sqlalchemy.create_engine("sqlite://", echo=True)
        session = orm.Session(bind=engine)
    Base.metadata.create_all(session.bind)
    session.add_all(sorted(widgetgen(), key=lambda x: x.timestamp))
    session.commit()

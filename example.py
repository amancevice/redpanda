import datetime
import pandas
import random
import sqlalchemy
import sqlalchemy.ext.declarative
import redpanda.mixins
from random_words import RandomWords

# Create an in-memory SQLite engine
engine = sqlalchemy.create_engine('sqlite://', echo=True)

# SQLAlchemy declarative base
Base = sqlalchemy.ext.declarative.declarative_base()

# Declare our model
class Widget(redpanda.mixins.RedPandaMixin, Base):
    __tablename__ = 'widgets'
    id            = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    created_at    = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)
    name          = sqlalchemy.Column(sqlalchemy.String)
    kind          = sqlalchemy.Column(sqlalchemy.String)
    units         = sqlalchemy.Column(sqlalchemy.Integer)

    # Class-defined RedPanda read_sql() arguments
    # This allows us to forego passing these into Widget.redpanda()
    __read_sql__ = {
        'index_col'   : ['created_at'],
        'parse_dates' : ['created_at'] }

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
    wordgen = RandomWords()
    kinds   = 'fizzer', 'buzzer', 'bopper'
    for i in range(0,25):
        for kind in kinds:
            name       = wordgen.random_word()
            created_at = randdate()
            units      = random.randint(0,100)
            yield Widget(created_at=created_at, name=name, kind=kind, units=units)

# Set up our database
Base.metadata.create_all(engine)
sessionmaker = sqlalchemy.orm.sessionmaker(bind=engine)
sessiongen   = sqlalchemy.orm.scoped_session(sessionmaker)
session      = sessiongen()
map(session.add, sorted(widgetgen(), key=lambda x: x.created_at))
session.commit()

# RedPanda Example usage
widgets = Widget.redpanda(engine)
widgets.frame()

flattener = redpanda.utils.flatten(pandas.TimeGrouper('B'), 'kind', 'units', sum)
widgets.frame(flattener).unstack() # or widgets.frame(flattener, lambda x: x.unstack())

timeboxed = Widget.redpanda(engine).between('created_at', '2015-11-01', '2015-11-30')
timeboxed.frame()
timeboxed.frame(flattener).unstack()

# Add your own SQLAlchemy dialect parameter adapter
dialect = sqlalchemy.dialects.example.dialect.SomeDialect
adapter = lambda statement: statement.params.items()
redpanda.dialects.add(dialect, adapter)
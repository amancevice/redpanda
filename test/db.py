""" Test setup. """


import datetime
import random
import redpanda.mixins
import sqlalchemy
import sqlalchemy.ext.declarative


# Create an in-memory SQLite engine
ENGINE = sqlalchemy.create_engine('sqlite://', echo=True)


# SQLAlchemy declarative base
Base = sqlalchemy.ext.declarative.declarative_base()


class MyRedPanda(redpanda.orm.RedPanda):
    pass


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


def create_db():
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
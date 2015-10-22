import datetime
import pandas
import random
import sqlalchemy
import sqlalchemy.ext.declarative
import random_words
import redpanda.mixins

# Create an in-memory SQLite engine
engine = sqlalchemy.create_engine('sqlite://', echo=True)

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
    wordgen = random_words.RandomWords()
    kinds   = 'fizzer', 'buzzer', 'bopper'
    for i in range(0,25):
        for kind in kinds:
            name      = wordgen.random_word()
            timestamp = randdate()
            units     = random.randint(0,100)
            yield Widget(timestamp=timestamp, name=name, kind=kind, units=units)

# Set up our database
Base.metadata.create_all(engine)
sessionmaker = sqlalchemy.orm.sessionmaker(bind=engine)
sessiongen   = sqlalchemy.orm.scoped_session(sessionmaker)
session      = sessiongen()
map(session.add, sorted(widgetgen(), key=lambda x: x.timestamp))
session.commit()

# RedPanda Example usage
frame = Widget.redpanda().frame(engine)
# redpanda.query(Widget, engine).frame()
print "\n\n" + "="*60 + "\n\n"
print frame
print "\n\n" + "="*60 + "\n\n"

# Use redpanda.query()
frame = redpanda.query(Widget).frame(engine)
print "\n\n" + "="*60 + "\n\n"
print frame
print "\n\n" + "="*60 + "\n\n"

# Limit results to November 2015
frame = Widget.redpanda()\
    .filter(Widget.timestamp.between('2015-11-01', '2015-11-30 23:59:59'))\
    .frame(engine)
print "\n\n" + "="*60 + "\n\n"
print frame
print "\n\n" + "="*60 + "\n\n"

# Flatten table into the sum of units across timegroup vs. kind
frame = Widget.redpanda().frame(engine)\
    .groupby([pandas.TimeGrouper("B"), "kind"]).units.sum()\
    .unstack().fillna(0)
print "\n\n" + "="*60 + "\n\n"
print frame
print "\n\n" + "="*60 + "\n\n"

# Parse dataframe back into models
frame = Widget.redpanda().frame(engine)
modlegen = Widget.redparse(frame, parse_index=True)
print "\n\n" + "="*60 + "\n\n"
for model in modlegen:
    print model
print "\n\n" + "="*60 + "\n\n"

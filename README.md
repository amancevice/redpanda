# RedPanda: Pandas & SQLAlchemy

Two great tastes that taste great together. Use RedPanda to add simple pandas integration into your declarative models.


## Installation

```bash
pip install redpanda
```


## Basic Use

Use the `redpanda.mixins.RedPandaMixin` class to add the `redpanda()` method to your declarative model classes:

```python
MyModel.redpanda(engine)
```

Use the `RedPanda` instance to transform SQLAlchemy queries into DataFrames or parse a DataFrame into SQLAlchemy models:

```python
frame    = MyModel.redpanda(engine).frame()
modelgen = MyModel.redpanda(engine).parse(frame)
```


## Extended Use

Follow these steps to create an in-memory example.


### Create SQLAlchemy Engine

```python
engine = sqlalchemy.create_engine("sqlite://", echo=True)
```


### Define Models

```python
# SQLAlchemy declarative base
Base = sqlalchemy.ext.declarative.declarative_base()

# Declare our model with mixin
class Widget(redpanda.mixins.RedPandaMixin, Base):
    __tablename__ = "widgets"
    id            = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    created_at    = sqlalchemy.Column(sqlalchemy.DateTime)
    name          = sqlalchemy.Column(sqlalchemy.String)
    kind          = sqlalchemy.Column(sqlalchemy.String)
    units         = sqlalchemy.Column(sqlalchemy.Integer)
```

*See [Populating Example Database](#populating-example-database) for more detail*


### Accessing Data

Pass an `engine` into the `redpanda()` class method of your models to create a `RedPanda` instance.

```python
Widget.redpanda(engine)
```


#### Custom Query

By default the query passed to the engine is `sqlalchemy.orm.Query(Widget)` (or whichever caller initiated the process). You can override this by passing a custom query as the second argument to `redpanda()`:

```python
query = sqlalchemy.orm.Query(Widget).filter(Widget.kind=="fizzer")
Widget.redpanda(engine, query)
```


#### Configure `read_sql()**

The `pandas.read_sql()` method accepts a number of keyword-arguments (see `help()` for details). These keyword-arguments may also be passed into the `redpanda()` method:

```python
Widget.redpanda(engine, index_col="id", parse_dates="created_at")
```


#### Class Defaults

You can further refine default behavior of the `redpanda` method on a per-class basis by defining class attributes:
* `__redpanda__` defines the RedPanda class returned by the `redpanda()` class-method
* `__read_sql__` is a dict of default values passed into `pandas.read_sql()`. These can be overriden at run-time.


##### \__read_sql__
```python
class Widget(redpanda.mixins.RedPandaMixin, Base):
    # ... see above for full definition

    # Class-defined RedPanda read_sql() arguments
    # This allows us to forego passing these into Widget.redpanda()
    __read_sql__ = {
        "index_col"   : ["created_at"],
        "parse_dates" : ["created_at"] }
```


##### \__redpanda__
```python
class MyRedPanda(redpanda.orm.RedPanda):
    pass

class Widget(redpanda.mixins.RedPandaMixin, Base):
    # ... see above for full definition
    
    __redpanda__ = MyRedPanda
```


### Timeboxing Data

RedPanda instances can further refine themselves using the `between()` method to limit query results by time:

```python
Widget.redpanda(engine).between(
    "created_at", "2015-11-01", "2015-11-30", how="[)")
```

The above will add the filters `Widget.created_at>='2015-11-01'` and `Widget.created_at<'2015-11-30` to the default query. Notice the string `"[)"` is translated as start-inclusive/end-exclusive. You can also use bitwise-or comparisons with the constants:
* `redpanda.timebox.START_INCLUSIVE`
* `redpanda.timebox.START_EXCLUSIVE`
* `redpanda.timebox.END_INCLUSIVE`
* `redpanda.timebox.END_EXCLUSIVE`


### Transforming DataFrames

The `frame()` method of a RedPanda instance accepts an arbitrary number of transformation operations. Some convenience transformations are provided in the `redpanda.utils` module:

```python
flattener = redpanda.utils.flatten(
    pandas.TimeGrouper('B'), 'kind', 'units', sum)
frame     = widgets.frame(flattener).unstack() 
#        or widgets.frame(flattener, lambda x: x.unstack())

print frame.head()
kind        bopper  buzzer  fizzer
created_at                        
2015-01-02      37     NaN     NaN
2015-01-06      70     NaN     NaN
2015-01-07     NaN      16      67
2015-01-09     NaN     NaN       6
2015-01-13     NaN     NaN      73
```


## Populating Example Database

```python
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

# Set up our database with dogfood data
Base.metadata.create_all(engine)
sessionmaker = sqlalchemy.orm.sessionmaker(bind=engine)
sessiongen   = sqlalchemy.orm.scoped_session(sessionmaker)
session      = sessiongen()
map(session.add, sorted(widgetgen(), key=lambda x: x.created_at))
session.commit()
```
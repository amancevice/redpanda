# RedPanda: Pandas & SQLAlchemy

Two great tastes that taste great together.

Use RedPanda to add simple pandas integration into your declarative models.

View [example.py](./example.py) for extended usage.


## Installation

```bash
pip install redpanda
```


## Basic Use

RedPanda wraps the `pandas.read_sql()` function into a dialect-agnostic class-method for declarative SQLAlchemy models. Use mixins to add the `redpanda()` method to your declarative model classes:

```python
engine = sqlalchemy.create_engine("sqlite://", echo=True)

class MyModel(redpanda.mixins.RedPandaMixin, Base):
    # ...

MyModel.redpanda(engine)
```

Use the resulting `RedPanda` instance to transform SQLAlchemy queries into DataFrames:

```python
MyModel.redpanda(engine).frame()
```

Or parse a DataFrame into SQLAlchemy model list-generator:

```python
MyModel.redpanda(engine).parse(frame)
```


## Dialects

The `pandas.read_sql()` function accepts (among other arguments) a SQLAlchemy database engine, SQL query string, and any parameters of the SQL string that are required. The format of the SQL string and the accompanying parameter data structure is dialect-dependent.

RedPanda supports some SQLAlchemy dialects out of the box (MySQL, Postgres, and SQLite are supported). You can add you own dialect by constructing a function to extract a parameter data-struct (eg, tuple, dict) from a compiled query statement:

```python
engine = sqlalchemy.create_engine("example://host/db")
func   = lambda statement: statement.items()
redpanda.dialects.add(type(engine.dialect), func)
```


## Extended Use

View [example.py](./example.py) for extended usage.


### Create SQLAlchemy Engine

```python
# Create an in-memory SQLite database engine
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
    timestamp     = sqlalchemy.Column(sqlalchemy.DateTime)
    name          = sqlalchemy.Column(sqlalchemy.String)
    kind          = sqlalchemy.Column(sqlalchemy.String)
    units         = sqlalchemy.Column(sqlalchemy.Integer)
```


## Accessing Data

The `redpanda()` class-method takes three arguments: a SQLAlchemy engine, an optional SQLAlchemy query, and optional keyword-arguments to be passed through to the `pandas.read_sql()` function. If omitted, the default query object is to select all from the model's table:

```python
# Default select-all
Widget.redpanda(engine)

# Custom query
query = sqlalchemy.orm.Query(Widget).filter(Widget.kind=="fizzer")
Widget.redpanda(engine, query)

# Adding parse_sql() keyword-args
Widget.redpanda(engine, query, index_col="id", parse_dates="timestamp")
```


### Timeboxing Data

RedPanda instances can further refine themselves using the `between()` method to limit query results by time:

```python
Widget.redpanda(engine).between(
    "created_at", "2015-11-01", "2015-11-30", how="[)")
```

The above will add the filters `Widget.created_at>='2015-11-01'` and `Widget.created_at<'2015-11-30` to the default query. Notice the string `"[)"` is translated as `START_INCLUSIVE|END_EXCLUSIVE`. You can also use bitwise-or operations with the constants:
* `redpanda.timebox.START_INCLUSIVE`
* `redpanda.timebox.START_EXCLUSIVE`
* `redpanda.timebox.END_INCLUSIVE`
* `redpanda.timebox.END_EXCLUSIVE`


### Class Defaults

You can further refine default behavior of the `redpanda` method on a per-class basis by defining class attributes:
* `__redpanda__` defines the RedPanda class returned by the `redpanda()` class-method
* `__read_sql__` is a dict of default values passed into `pandas.read_sql()`. These can be overriden at run-time.


#### \__read_sql__
```python
class Widget(redpanda.mixins.RedPandaMixin, Base):
    # ... see above for full definition

    # Class-defined RedPanda read_sql() arguments
    # This allows us to forego passing these into Widget.redpanda()
    __read_sql__ = {
        "index_col"   : ["created_at"],
        "parse_dates" : ["created_at"] }
```


#### \__redpanda__
```python
class MyRedPanda(redpanda.orm.RedPanda):
    # ... overrides in here

class Widget(redpanda.mixins.RedPandaMixin, Base):
    # ... see above for full definition
    __redpanda__ = MyRedPanda
```

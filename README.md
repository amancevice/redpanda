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

View [example.py](./example.py) for extended usage examples.


## RedPanda Declarative Mixin

Use the `redpanda.minxins.RedPandaMixin` mixin to add redpanda to your declarative SQLAlchemy models.

```python
# Create an in-memory SQLite database engine
engine = sqlalchemy.create_engine("sqlite://", echo=True)

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

## Mixin Customization

Add model-level behavior customization by overriding the default class attributes:


#### \__redpanda__

If you wish to use your own custom `RedPanda` class, you can override the `__redpanda__` class attribute:

```python
class MyRedPanda(redpanda.orm.RedPanda):
    # ... custom logic here

class Widget(redpanda.mixins.RedPandaMixin, Base):
    # ... see above for full definition
    __redpanda__ = MyRedPanda
```


#### \__read_sql__

Set the `__read_sql__` attribute to control the defualt behavior of `pandas.read_sql()`

```python
class Widget(redpanda.mixins.RedPandaMixin, Base):
    # ... see above for full definition

    # Class-defined RedPanda read_sql() arguments
    # This allows us to forego passing these into Widget.redpanda()
    __read_sql__ = {
        "index_col"   : ["created_at"],
        "parse_dates" : ["created_at"] }
```


## Accessing Data

The `redpanda()` class-method accepts the following arguments:
* `engine`: A SQLAlchemy engine
* `query`: An optional SQLAlchemy query to refine the data returned by the engine
* `**read_sql`: An optional keyword-argument dict to be passed through to the `pandas.read_sql()` function. 

If the `query` argument is omitted, the default behavior is to select the entire table.

If the `**read_sql` keyword-argument dict is omitted the value is read from the class-attribute `__read_sql__` (which is empty by default).

```python
# Default select-all
Widget.redpanda(engine)

# Supply a custom query to refine data set
query = sqlalchemy.orm.Query(Widget).filter(Widget.kind=="fizzer")
Widget.redpanda(engine, query)

# Supply **read_sql keyword-args to alter returned DataFrame
Widget.redpanda(engine, query, index_col="id", parse_dates="timestamp")
```

# RedPanda: Pandas & SQLAlchemy

![pypi](https://img.shields.io/pypi/v/redpanda?color=yellow&logo=python&logoColor=eee&style=flat-square)
![python](https://img.shields.io/pypi/pyversions/redpanda?logo=python&logoColor=eee&style=flat-square)
[![pytest](https://img.shields.io/github/workflow/status/amancevice/redpanda/pytest?logo=github&style=flat-square)](https://github.com/amancevice/redpanda/actions)
[![coverage](https://img.shields.io/codeclimate/coverage/amancevice/redpanda?logo=code-climate&style=flat-square)](https://codeclimate.com/github/amancevice/redpanda/test_coverage)
[![maintainability](https://img.shields.io/codeclimate/maintainability/amancevice/redpanda?logo=code-climate&style=flat-square)](https://codeclimate.com/github/amancevice/redpanda/maintainability)

Two great tastes that taste great together.

Use RedPanda to add simple pandas integration into your declarative models.


## Installation

```bash
pip install redpanda
```


## Basic Use

Create a session from a SQLAlchemy engine:

```python
import redpanda

engine = redpanda.create_engine("sqlite://")
# => Engine(sqlite://)

Session = redpanda.orm.sessionmaker(bind=engine)
session = Session()
# => <sqlalchemy.orm.session.Session>
```


## Querying

Use the `frame()` method of RedPanda queries to return a DataFrame representation of the results instead of a collection of models.

```python
query = session.query(MyModel)
# => <redpanda.orm.Query>

query.frame()
# => <pandas.DataFrame>
```


### Querying with Filters

The `frame()` method that wraps the `pandas.read_sql()` function into a dialect-agnostic class-method for declarative SQLAlchemy models and can accept the same keyword arguments as `pandas.read_sql()`:

```python
query = session.query(MyModel).filter_by(my_attr="my_val")

query.frame(index_col="time")
```

Additionally, a `within()` method is added to SQLAlchemy's InstrumentedAttribute class that accepts a pandas Index object:

```python
index = pandas.period_range("2016-11-01", "2016-11-30", freq="W")
query = session.query(MyModel).filter(MyModel.timestamp.within(index))
```

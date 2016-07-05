# RedPanda: Pandas & SQLAlchemy

[![Build Status](https://travis-ci.org/amancevice/redpanda.svg?branch=master)](https://travis-ci.org/amancevice/redpanda)
[![PyPI version](https://badge.fury.io/py/redpanda.svg)](https://badge.fury.io/py/redpanda)

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

session = redpanda.Session(bind=engine)
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
query = session.query(MyModel).filter(MyModel.my_attr=="my_val")

query.frame(index_col="time")
```


## More Examples

See the IPython Notebooks in the [`examples`](./examples) directory for examples using [`Python 2.7`](./examples/python27/notebook.ipynb) and [`Python 3.5`](./examples/python35/notebook.ipynb)

Additionally, if you have `docker-compose` installed you may view these notebooks directly by cloning this repo and starting the containers:

```bash
git clone git@github.com:amancevice/redpanda.git
cd redpanda
docker-compose up
```

Navigate to [http://localhost:2700](http://localhost:2700/tree) to view the `Python 2.7` notebook, or [http://localhost:3500](http://localhost:3500/tree) for `Python 3.5`.
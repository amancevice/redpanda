""" Pandas-ORM Integration. """


__author__  = "amancevice"
__email__   = "smallweirdnum@gmail.com"
__version__ = "0.0.7"



def query(entities, engine=None, **read_sql):
    """ Construct RedPanda """
    from . import orm
    return orm.RedPanda(entities, engine=engine, **read_sql)

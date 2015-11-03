""" Pandas-ORM Integration. """


__author__  = "amancevice"
__email__   = "smallweirdnum@gmail.com"
__version__ = "0.1.3"


from . import orm


def query(entities, session=None, **read_sql):
    """ Construct RedPanda """
    return orm.RedPanda(entities, session=session, **read_sql)

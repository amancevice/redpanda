""" RedPanda SQLAlchemy Mixins. """


from sqlalchemy.ext.declarative import declared_attr
from . import orm


class RedPandaMixin(object):
    """ Basic RedPanda Mixin. Gives access to <Model>.redpanda.frame() """

    @declared_attr
    def redpanda(cls):
        return orm.RedPanda(cls)


class TimestampedMixin(RedPandaMixin):
    """ RedPanda Mixin for transforming datetime-indexable SQLAlchemy data. """
    timestamp_col = 'timestamp'

    @declared_attr
    def redpanda(cls):
        return orm.TimestampedRedPanda(cls, cls.timestamp_col)


class PeriodicMixin(RedPandaMixin):
    """ RedPanda Mixin for transforming period-indexable SQLAlchemy data. """
    period_start_col = 'asof'
    period_end_col   = 'until'

    @declared_attr
    def redpanda(cls):
        return orm.PeriodicRedPanda(cls, cls.period_start_col, cls.period_end_col)
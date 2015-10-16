""" RedPanda engine binding. """


global ENGINE


def bind(engine):
    """ Bind an engine to RedPanda. """
    globals()['ENGINE'] = engine

""" RedPanda utility functions. """


def dictcombine(*dicts):
    """ Combine dictionaries favoring the right-most in args.

        Arguments:
            dicts   (tuple):    Dictionaries to merge

        Returns:
            Merged dictionary. """
    return { k:v for d in dicts for k,v in d.items() }


def flatten(grouper, minor_axis, items, func):
    groupby = lambda x: x.groupby([grouper, minor_axis])
    mapper  = lambda x: x[items]
    reducer = lambda x: x.apply(func)
    return lambda x: reducer(mapper(groupby(x)))

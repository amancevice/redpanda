""" RedPanda utility functions. """


def dictcombine(*dicts):
    """ Combine dictionaries favoring the right-most in args. """
    return { k:v for d in dicts for k,v in d.items() }

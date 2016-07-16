""" RedPanda Utils. """


def dictcombine(*dicts):
    """ Combine dictionaries in order. """
    return {k: v for d in dicts for k, v in d.items()}

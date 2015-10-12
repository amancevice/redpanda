""" RedPanda utility functions. """


def dictcombine(*dicts):
    """ Combine dictionaries favoring the right-most in args.

        Arguments:
            dicts   (tuple):    Dictionaries to merge

        Returns:
            Merged dictionary. """
    return { k:v for d in dicts for k,v in d.items() }

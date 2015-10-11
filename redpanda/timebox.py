""" Timeboxing helpers. """


START_INCLUSIVE = 2
END_INCLUSIVE   = 4
START_EXCLUSIVE = 8
END_EXCLUSIVE   = 16

def parse(timebox_str):
    """ Parse timebox string into integer.

        Examples:
            parse("()") # => START_EXCLUSIVE|END_EXCLUSIVE
            parse("[)") # => START_INCLUSIVE|END_EXCLUSIVE

        Arguments:
            timebox_str (str):  String representing timebox

        Returns:
            Bitwise-or of timebox. """
    mapper = {
        '[]' : START_INCLUSIVE|END_INCLUSIVE,
        '[)' : START_INCLUSIVE|END_EXCLUSIVE,
        '(]' : START_EXCLUSIVE|END_INCLUSIVE,
        '()' : START_EXCLUSIVE|END_EXCLUSIVE }
    try:
        return mapper[timebox_str]
    except KeyError:
        raise KeyError("Timebox string must contain exactly one open+close paren/bracket.")



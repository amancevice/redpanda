""" Test for utils module. """

import redpanda.utils
from nose.tools import assert_equal


def test_dictcombine():
    dict1 = {'foo' : 'bar', 'flip' : 'flop'}
    dict2 = {'foo' : 'baz', 'fizz' : 'buzz'}
    returned = redpanda.utils.dictcombine(dict1, dict2)
    expected = {'foo' : 'baz', 'fizz' : 'buzz', 'flip' : 'flop'}
    assert_equal(returned, expected)

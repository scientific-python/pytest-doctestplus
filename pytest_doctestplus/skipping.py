# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Defines the doctest_skip decorator.
"""

SHOULD_SKIP = {}

def doctest_skip(reason=None):
    '''Mark a function/class so that doctests are skipped.

    An optional reason can be given.
    '''
    # Reason is currently ignored. Maybe there's a way to report it somehow...
    def decorator(obj):
        SHOULD_SKIP[obj] = True
        return obj

    return decorator

def doctest_skipif(condition, reason=None):
    '''Mark a function/class so that doctests are skipped conditionally.

    condition can be bool or a callable (returning bool).
    An optional reason can be given
    '''
    # Reason is currently ignored. Maybe there's a way to report it somehow...

    if not (condition in (True, False) or callable(condition)):
        raise ValueError('condition should be bool or callable')

    def decorator(obj):
        SHOULD_SKIP[obj] = condition
        return obj

    return decorator

def get_should_skip(obj):
    '''Check if obj has been marked with doctest_skip or doctest_skipif.

    In the case of doctest_skipif this will return the result of the skipif
    condition.
    '''
    condition = SHOULD_SKIP.get(obj, False)
    if condition in (True, False):
        return condition
    elif callable(condition):
        return condition()
    else:
        raise ValueError('condition should be bool or callable')

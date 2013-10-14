import collections


def listify(arg):
    """Make arg iterable, if it's not already.

    I'm sure there's some other iterable object besides a string that you
    would want to listify, but I can't think of them right now.
    """
    if (((not isinstance(arg, collections.Iterable))
         or isinstance(arg, basestring))):
        return [arg]
    else:
        return arg

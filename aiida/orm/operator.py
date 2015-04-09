# -*- coding: utf-8 -*-


# Using new to have immutable operator (subclass tuple ?).
# Unwrap method, returning a list maybe ? Or a way to recursivly apply a
# function to each one ? Not to overkill ?
# Something like apply(func), which recursivly apply a function. Or a function
# per type. A loop that unfold everything.

class Operator(object):
    def __new__(self, *args, **kwargs):
        pass


class Or_(Operator):
    pass

class And_(Operator):
    pass

class Not_(Operator):
    pass


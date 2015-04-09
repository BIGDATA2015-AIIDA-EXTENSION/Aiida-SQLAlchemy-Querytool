# -*- coding: utf-8 -*-

from collections import namedtuple
from inspect import isclass

attr_type_to_column = {
    int: "ival",
    float: "fval",
    basestring: "tval",
    str: "tval",
    # TODO: add other python subtype of basestring.
    bool: "bval",
}

_op_val_typecheck = {
    "==": [basestring, int, float, bool],
    "=": [basestring, int, float, bool],
    "!=": [basestring, int, float, bool],
    "<=": [int, float],
    ">=": [int, float],
    ">": [int, float],
    "<": [int, float],
}

def valid_op_val(op, val):
    return any(map(lambda t: isinstance(val, t), _op_val_typecheck[op]))

class Attribute(namedtuple('Attribute', ['key', 'op', 'value'])):
    def __new__(cls, key, op=None, value=None):
        # xor to see if either op or value alone wasn't provided.
        if bool(op is None) ^ bool(value is None):
            raise ValueError("You need to supply both the operator and the "
                             + "value as parameters or none of them.")

        check_args(key, instance=basestring, exception=True)
        if op and value and not valid_op_val(op, value):
            raise ValueError("Incompatiblity between op {} and value {}.".
                             format(op, value))

        inst = super(Attribute, cls).__new__(cls, key, op, value)

        if value is not None:
            column = attr_type_to_column[type(value)]
            setattr(inst, 'column', column)

        return inst


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def check_args(arguments, instance=[], subclass=[], exception=False):

    if not isinstance(arguments, (list, tuple)):
        arguments = [arguments]
    if not isinstance(instance, list):
        instance = [instance]
    if not isinstance(subclass, list):
        subclass = [subclass]

    def checker(var):
        instance_check = map(lambda instance: isinstance(var, instance),
                             instance)
        subclass_check = []
        if isclass(var):
            subclass_check = map(lambda sub: issubclass(var, sub), subclass)

        return any(instance_check + subclass_check)

    results = map(checker, arguments)
    correct = all(results)

    if not correct and exception:
        error_string = ", ".join(map(lambda e: e.__name__, instance + subclass))
        raise TypeError("The arguments need to be of the following type: {}".
                        format(error_string))

    return correct

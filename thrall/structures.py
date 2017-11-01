# coding: utf-8
import collections


class Singleton(type):
    __instances__ = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances__:
            cls.__instances__[cls] = super(Singleton, cls).__call__(*args,
                                                                    **kwargs)
        return cls.__instances__[cls]


def namedtuple_with_defaults(typename, field_names, default_values=()):
    """ Code from stack overflow: https://stackoverflow.com/a/18348004"""
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T

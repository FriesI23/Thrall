# coding: utf-8
from six import iteritems

from .utils import is_func_bound

try:
    from functools32 import (
        update_wrapper,
        wraps,
    )
except ImportError:
    from functools import (
        update_wrapper,
        wraps,
    )


__all__ = ['SetDefault']


class _SetDefault(object):
    def __init__(self, func):
        self.func = func
        self.default_kwargs = {}

        self._own_instance = None
        update_wrapper(self, func)

        if is_func_bound(func):
            self.__self__ = func.__self__

    def __call__(self, *args, **kwargs):
        for k, v in iteritems(self.default_kwargs):
            if k not in kwargs:
                kwargs[k] = v
        if self._own_instance:
            return self.func(self._own_instance, *args, **kwargs)
        else:
            return self.func(*args, **kwargs)

    def __get__(self, instance, owner):
        self._own_instance = instance
        return self

    def set_default(self, **kwargs):
        for k, v in iteritems(kwargs):
            self.default_kwargs[k] = v


class _SetDefaultWithParams(object):
    def __init__(self, **kwargs):
        self.default_kwargs = kwargs

    def __call__(self, fn):
        @wraps(fn)
        def __wrapper(*args, **kwargs):
            for k, v in iteritems(self.default_kwargs):
                if k not in kwargs:
                    kwargs[k] = v
            return fn(*args, **kwargs)

        return __wrapper

    def set_default(self, **kwargs):
        for k, v in iteritems(kwargs):
            self.default_kwargs[k] = v


class SetD(_SetDefault, _SetDefaultWithParams):
    def __init__(self, *args, **kwargs):
        if self.is_func_direct(args):
            _SetDefault.__init__(self, args[0])
            self._d = True
        else:
            _SetDefaultWithParams.__init__(self, **kwargs)
            self._d = False

    def __call__(self, *args, **kwargs):
        if self._d:
            return _SetDefault.__call__(self, *args, **kwargs)
        else:
            return _SetDefaultWithParams.__call__(self, args[0])

    @staticmethod
    def is_func_direct(args):
        if args and callable(args[0]):
            return True


SetDefault = SetD

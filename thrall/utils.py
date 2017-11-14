# coding: utf-8
import functools
import re
from operator import itemgetter

from six import iteritems

from thrall.compat import __builtin__, unicode
from future.utils import python_2_unicode_compatible

builtin_names = frozenset(
    name for name in dir(__builtin__)
    if name.islower() and not name.startswith('_')
)


def required_params(*params):
    """ decorator to check functions params required, exception raised if
    checked param is None.

    :param params: checked params
    :type params: list params
    """
    import inspect

    def _required_params(fn):

        def __check_param(param, arg2value, kw):
            if arg2value.get(param) is not None:
                return
            elif kw.get(param) is not None:
                return
            else:
                raise RuntimeError(
                    "Checked param '{}' not found".format(param))

        @functools.wraps(fn)
        def __wrapper(*args, **kwargs):
            d = inspect.getcallargs(fn, *args, **kwargs)
            kw = d.get('kwargs', {})

            for p in params:
                __check_param(p, d, kw)

            return fn(*args, **kwargs)

        return __wrapper

    return _required_params


def check_params_type(enforce=False, **types):
    """ decorator to check functions params type, exception raise if checked
    param not found or err type.

    :param enforce: raise exception if checked params not found
    :param types: checked param and typed
    :type types: dict params
    """
    import inspect

    def _check_params_type(fn):
        def __enforce_check_type(key, type_list, arg2value, kw):
            if key not in arg2value:
                if not isinstance(kw.get(key), tuple(type_list)):
                    raise TypeError(
                        'Check params "{}" type failed'.format(key))

            elif not isinstance(arg2value.get(key), tuple(type_list)):
                raise TypeError('Check params "{}" type failed'.format(key))

        def __check_type(key, type_list, arg2value, kw):
            if (key not in arg2value and kw.get(key) is None) or (
                        arg2value.get(key) is None):
                return

            __enforce_check_type(key, type_list, arg2value, kw)

        @functools.wraps(fn)
        def __wrapper(*args, **kwargs):
            d = inspect.getcallargs(fn, *args, **kwargs)
            kw = d.get('kwargs', {})

            for key, checked_types in iteritems(types):
                if enforce:
                    __enforce_check_type(key, checked_types, d, kw)
                else:
                    __check_type(key, checked_types, d, kw)

            return fn(*args, **kwargs)

        return __wrapper

    return _check_params_type


@python_2_unicode_compatible
class NamedURL(tuple):
    """ Named url structure.

    >>> NamedURL.from_args(name='name', url='url')
    ('name', 'url', None, None)
    >>> NamedURL.from_args('name', 'url', desp='xxx')
    ('name', 'url', None, 'xxx')
    >>> NamedURL.from_args('name', 'url', 'v1', 'xxx')
    ('name', 'url', 'v1', 'xxx')
    """
    name = property(itemgetter(0))
    url = property(itemgetter(1))
    version = property(itemgetter(2))
    desp = property(itemgetter(3))

    @classmethod
    def from_args(cls, name, url, version=None, desp=None):
        return cls((name, url, version, desp))

    def __str__(self):
        return unicode(getattr(self, 'url'))


def is_func_bound(method, instance=None):
    """ check function is bound in class instance.
    >>> is_func_bound(lambda :None)
    False
    >>> is_func_bound(dict().get)
    True
    >>> x = dict(a=1)
    >>> is_func_bound(x.get, x)
    True
    >>> y = dict(a=1)
    >>> is_func_bound(x.get, y)
    False

    :param method: checked method.
    :param instance: checked instance, not None to enable instance bound check.
    :return: True if is bound in an instance.
    """
    if instance is None:
        return hasattr(method, '__self__')
    else:
        return getattr(method, '__self__', None) is instance


def get_func_name(fn):
    """ get func-name in decorate method/function

        Note: decorated method/function must have `fn_name` param.
    """

    @functools.wraps(fn)
    def __get_fn_name(*args, **kwargs):
        return fn(*args, func_name=fn.__name__, **kwargs)

    return __get_fn_name


class MapStatusMessage(tuple):
    """ Amap error message """
    code = property(itemgetter(0))
    msg = property(itemgetter(1))
    detail = property(itemgetter(2))

    @classmethod
    def from_args(cls, code, msg=None, detail=None):
        return cls((code, msg, detail))


def is_list_empty(in_list):
    """ Code from stack overflow: https://stackoverflow.com/a/1605679"""
    if isinstance(in_list, list):
        return all(map(is_list_empty, in_list))
    return False


def camelcase_to_snakecase(name):
    """Converts the CamelCase name into snake_case style.

    From http://stackoverflow.com/a/1176023/718453

    :param name: The input name.
    :returns: The converted name.
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    s3 = s2.lower().replace('__', '_')
    if s3 in builtin_names:
        return '%s_' % s3
    return s3


class _PartialMethod(functools.partial):
    """ partial method in instance of object. """

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return functools.partial(
            self.func, instance,
            *(self.args or ()), **(self.keywords or {}))


partialmethod = _PartialMethod

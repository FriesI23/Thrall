# coding: utf-8
# coding: utf-8
from __future__ import absolute_import

from contextlib import contextmanager

from requests.adapters import HTTPAdapter
from requests.sessions import Session
from requests.exceptions import (
    RequestException,
    ConnectionError,
    Timeout,
    HTTPError
)

from thrall.compat import basestring
from thrall.exceptions import (
    VendorRequestError,
    VendorConnectionError,
    VendorHTTPError,
)

from .hooks import SetDefault
from .utils import builtin_names, is_func_bound, repr_params

set_default = SetDefault


class BaseRequest(object):
    def __init__(self, session=None):
        if not isinstance(session, Session):
            self.session = Session()
            self.session.mount('http://', HTTPAdapter(max_retries=1,
                                                      pool_maxsize=50))
            self.session.mount('http://', HTTPAdapter(max_retries=1,
                                                      pool_maxsize=50))
        else:
            self.session = session

    @set_default
    def get(self, url, params, timeout=1, callback=None, **kwargs):
        with self.catch_exception():
            r = self._get_result(url, params, timeout, **kwargs)

        if callable(callback):
            callback(r)

        return r

    @set_default
    def post(self, url, data, timeout=1, callback=None, **kwargs):
        with self.catch_exception():
            r = self._post_result(url, data, timeout, **kwargs)

        if callable(callback):
            callback(r)

        return r

    def _get_result(self, url, params, timeout, **kwargs):
        r = self.session.get(url, params=params, timeout=timeout, **kwargs)
        r.raise_for_status()

        return r

    def _post_result(self, url, data, timeout, **kwargs):
        r = self.session.post(url, data, timeout=timeout, **kwargs)
        r.raise_for_status()

        return r

    @contextmanager
    def catch_exception(self):
        try:
            yield
        except(ConnectionError, Timeout) as err:
            raise VendorConnectionError(str(err), data=err)
        except HTTPError as err:
            raise VendorHTTPError(str(err), data=err)
        except RequestException as err:
            raise VendorRequestError(str(err), data=err)


class BaseData(object):
    _properties = ()

    def __init__(self, unpacked_data, static=False):
        self._data = unpacked_data or {}
        self._static = static

        if self._static:
            self._static_decode()

    def __unicode__(self):
        return repr_params(self._properties, self.__class__.__name__, self)

    def __repr__(self):
        return self.__unicode__()

    def __getattr__(self, name):
        try:
            return self._decode(name)
        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))

    def _decode(self, p):
        if p not in self._properties:
            raise KeyError(p)

        if p in builtin_names:
            p += u'_'

        r = self.decode_param(p, self._data)
        return r if r is not None else self._data.get(p)

    def _static_decode(self):
        for i in self._properties:
            setattr(self, i, self._decode(i))

    def decode_param(self, p, data):
        """ Decode data param.

            override example:

                def decode_param(self, p, data):
                    # do something from data
                    # raise KeyError when not found in data
                    # default handle:
                    return self._data.get(p)

        :param p: data param
        :param data: raw data pair
        :return: data value
        """
        pass

    @property
    def attrs(self):
        return self._properties


class BaseAdapterMixin(object):
    _TYPE_ENCODE = 'encode'
    _TYPE_DECODE = 'decode'

    def __init__(self):
        self._registered_coders = {}

    @property
    def all_registered_coders(self):
        return self._registered_coders

    def query(self, q):
        try:
            return self._query(q)
        except KeyError:
            msg = "'{0}' has no registered function '{1}'"
            raise AttributeError(msg.format(type(self).__name__, q))

    def _query(self, func):
        if is_func_bound(func, self):
            return self._registered_coders[func.__name__]
        else:
            return self._registered_coders[func]

    def registry(self, func, coder):
        try:
            if is_func_bound(func, self):
                self._registered_coders[func.__name__] = coder
            else:
                raise KeyError
        except Exception:
            raise AttributeError(
                'un-support registry function {}'.format(func))

    def un_registry(self, func):
        try:
            if isinstance(func, basestring):
                self._registered_coders.pop(func)
            elif is_func_bound(func, self):
                self._registered_coders.pop(func.__name__)
            else:
                raise KeyError
        except Exception:
            raise AttributeError(
                "can't un-registry function {}".format(func))


class BaseAdapter(BaseAdapterMixin):
    def __init__(self):
        super(BaseAdapter, self).__init__()
        self.registry_coders()

    def registry_coders(self):
        raise NotImplementedError


class BaseEncoderAdapter(BaseAdapter):

    def registry_coders(self):
        return self.registry_encoders()

    def registry_encoders(self):
        raise NotImplementedError


class BaseDecoderAdapter(BaseAdapter):

    def registry_coders(self):
        return self.registry_decoders()

    def registry_decoders(self):
        raise NotImplementedError

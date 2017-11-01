# coding: utf-8
# coding: utf-8
from __future__ import absolute_import

from requests.adapters import HTTPAdapter
from requests.sessions import Session

from .hooks import SetDefault
from .utils import builtin_names, is_func_bound

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
        r = self._get_result(url, params, timeout, **kwargs)

        if callable(callback):
            callback(r)

        return r

    @set_default
    def post(self, url, data, timeout=1, callback=None, **kwargs):
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


class BaseData(object):
    _properties = ()

    def __init__(self, unpacked_data):
        self._data = unpacked_data or {}

    def __getattr__(self, name):
        try:
            if name not in self._properties:
                raise KeyError(name)

            if name in builtin_names:
                name += u'_'

            return self._decode(name)
        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))

    def _decode(self, p):
        r = self.decode_param(p, self._data)
        return r or self._data.get(p)

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
            return self._registered_coders[func.func_name]
        else:
            return self._registered_coders[func]

    def registry(self, func, coder):
        if is_func_bound(func, self):
            self._registered_coders[func.func_name] = coder
        else:
            raise RuntimeError('un-support registry function {}'.format(func))

    def un_registry(self, func):
        if isinstance(func, (str, unicode)):
            self._registered_coders.pop(func)
        elif is_func_bound(func, self):
            self._registered_coders.pop(func.func_name)
        else:
            raise RuntimeError("can't un-registry function {}".format(func))


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

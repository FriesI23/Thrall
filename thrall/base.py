# coding: utf-8
# coding: utf-8
from __future__ import absolute_import

import logging
from six import iteritems

import functools
from contextlib import contextmanager

from requests.adapters import HTTPAdapter
from requests.sessions import Session
from requests.exceptions import (
    RequestException,
    ConnectionError,
    Timeout,
    HTTPError
)

from thrall.utils import required_params
from thrall.consts import RouteKey, OutputFmt, FORMAT_JSON, FORMAT_XML
from thrall.compat import basestring, urlparse
from thrall.exceptions import (
    VendorRequestError,
    VendorConnectionError,
    VendorHTTPError,
    VendorError,
)

from .hooks import SetDefault
from .utils import builtin_names, is_func_bound, repr_params

set_default = SetDefault


class BaseRequestParams(object):
    ROUTE_KEY = RouteKey.UNKNOWN

    @required_params('key')
    def __init__(self, key=None, output=None, private_key=None, callback=None,
                 raw_params=None):
        self.key = key
        self.output = output
        self.callback = callback
        self.private_key = private_key
        self._raw_params = raw_params

    def prepare(self):
        try:
            return self.prepare_data()
        except VendorError as err:
            err.data = self
            raise err

    def prepare_data(self):
        """ package request params

            input  --> Nothing
            output --> prepared object, type_extend: BasePreparedRequestParams

            override example:

                def prepare(self):
                    p = BasePreparedRequestParams()
                    p.prepare(**some_kwargs)
                    return p

            :raise NotImplementedError: this function need to be implement.
        """
        raise NotImplementedError

    @contextmanager
    def prepare_basic(self, p):
        org_fun = p.prepare
        new_fun = functools.partial(p.prepare, key=self.key,
                                    pkey=self.private_key,
                                    output=self.output,
                                    callback=self.callback,
                                    raw_params=self._raw_params)
        p.prepare = new_fun
        yield p
        p.prepare = org_fun


class BasePreparedRequestParams(object):
    DEFAULT_URL = None
    ROUTE_KEY = RouteKey.UNKNOWN
    PARAMS_MAP = {
        'key': 'key',
        'output': 'output',
        'callback': 'callback',
        'sig': 'sig'
    }

    _logger = logging.getLogger(__name__)

    def __init__(self):
        self.key = None
        self._pkey = None
        self.output = None
        self.callback = None
        self._raw_params = None

    def __unicode__(self):
        params = [k for k, v in iteritems(self.__dict__) if
                  not hasattr(v, '__call__')]
        params.append('sig')
        return repr_params(params, self.__class__.__name__, self)

    def __repr__(self):
        return self.__unicode__()

    def generate_params(self):
        """ generate prepared params without sig

            input  --> self
            output --> prepared params dict without `sig`.

            override example:

                def generate_params(self):
                    optional_params = {..}
                    with self.init_basic_params({}, optional_params) as p:
                        # add required params
                        return p

            :raise NotImplementedError: this function need to be implement.
        """
        raise NotImplementedError

    @property
    def params(self):
        p = self.generate_params()
        p.update(
            {self.PARAMS_MAP['sig']: self.prepared_sig} if self._pkey else {})
        return p

    def prepare(self, **kwargs):
        """ called prepare data functions

            input  --> kwargs witch need be package to dict
            output --> Any

            override example:

                def prepare(self, a=1, b=2, c=3, key='xx'):
                    # do custom prepare function
                    # self.prepare_something(a=a, b=b, c=c)
                    self.prepare_base(key=key)

            :raise NotImplementedError: this function need to be implement.
        """
        raise NotImplementedError

    def prepare_base(self, key=None, pkey=None, output=None, callback=None,
                     raw_params=None):
        self._pkey = pkey
        self._raw_params = raw_params
        self.prepare_key(key)
        self.prepare_output(output)
        self.prepare_callback(callback)

    def prepare_key(self, key):
        self.key = key

    def prepare_output(self, output):
        # if output is None:
        #     return
        #
        # if isinstance(output, OutputFmt):
        #     self.output = output
        # else:
        #     if output.lower() == FORMAT_JSON:
        #         self.output = OutputFmt.JSON
        #     elif output.lower() == FORMAT_XML:
        #         self.output = OutputFmt.XML
        self._logger.warning(
            'output param deprecated, mandatory use json in output param.')
        if output:
            self.output = OutputFmt.JSON

    def prepare_callback(self, callback):
        if callback is None:
            return

        self.callback = urlparse(callback)

    @property
    def prepared_key(self):
        return self.key

    @property
    def prepared_output(self):
        if self.output == OutputFmt.JSON:
            return FORMAT_JSON
        elif self.output == OutputFmt.XML:
            return FORMAT_XML

    @property
    def prepared_callback(self):
        if self.callback is not None:
            return self.callback.geturl()

    @property
    def sig(self):
        """Achieve calibration function"""

    @property
    def prepared_sig(self):
        """Achieve calibration function"""

    @contextmanager
    def init_basic_params(self, params, optionals=None):
        new_params = self._init_basic_params(params)
        self._init_optional_params(params, optionals)
        # init raw_params
        self._init_optional_params(params, self._raw_params)

        yield new_params

    def _init_basic_params(self, params):
        params[self.PARAMS_MAP['key']] = self.prepared_key

        params.update(
            {self.PARAMS_MAP['output']: self.prepared_output}
            if self.prepared_output else {})
        params.update(
            {self.PARAMS_MAP['callback']: self.prepared_callback}
            if self.prepared_callback else {})

        return params

    @staticmethod
    def _init_optional_params(params, optionals):

        if optionals:
            for opt, opt_v in iteritems(optionals):
                params.update({opt: opt_v} if opt_v is not None else {})

        return params


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

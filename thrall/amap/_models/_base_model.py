# coding: utf-8
from __future__ import absolute_import

import contextlib
import functools
from hashlib import md5

from six import iteritems

from thrall.compat import unicode, urlparse
from thrall.consts import FORMAT_JSON, FORMAT_XML, RouteKey
from thrall.exceptions import VendorError, amap_status_exception
from thrall.utils import MapStatusMessage, required_params, repr_params

from ..common import json_load_and_fix_amap_empty, parse_location
from ..consts import AMapVersion, ExtensionFlag, OutputFmt, StatusFlag


class Extensions(object):
    """ AMap extension control class """

    def __init__(self, flag=False, **opt_options):
        """ get an instance of extensions.

        :param flag: extension flag, True if wan't enable extensions.
        :param opt_options: k, w pair of options.
        """
        self._flag = flag
        self._opt_options = opt_options

    def __getattr__(self, prop):
        return self._opt_options.get(prop)

    @property
    def status(self):
        return ExtensionFlag.ALL if self._flag else ExtensionFlag.BASE


class Sig(object):
    """ AMap sig generator """

    def __init__(self, pkey, hash_fn=md5, kwargs=None):
        """ get an instance of sig

            Note: sig must be enable in amap online control panel, please
                enable sig and got and pkey first.

            Please see: http://lbs.amap.com/faq/account/key/72

        :param pkey: amap private key.
        :param hash_fn: hash function, default by md5, custom hash function
        must implement digest function.
        :param kwargs: request params, same as request params.
        """
        self.private_key = pkey
        self.hash_func = hash_fn
        self.kw = kwargs if kwargs is not None else {}

    def __repr__(self):
        return repr_params(['method', 'sig'],
                           "AMap{}".format(self.__class__.__name__),
                           self, default_value={
                "method": self.hash_func.__name__.upper(),
                "sig": u"'{}'".format(self.unhash_sig)})

    @property
    def hashed_sig(self):
        sig = (self.unhash_sig.encode('utf-8') if isinstance(
            self.unhash_sig, unicode) else self.unhash_sig)

        return self.hash_func(sig).digest()

    @property
    def unhash_sig(self):
        kw_pairs = sorted(iteritems(self.kw), key=lambda d: d[0])
        prepared_sig = u"{kw}{sig}".format(
            sig=self.private_key,
            kw=u"&".join([u"{k}={v}".format(k=k, v=v) for k, v in kw_pairs])
        )
        return prepared_sig


class BaseRequestParams(object):
    ROUTE_KEY = RouteKey.UNKNOWN

    @required_params('key')
    def __init__(self, key=None, output=None, private_key=None, callback=None):
        self.key = key
        self.output = output
        self.callback = callback
        self.private_key = private_key

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

    @contextlib.contextmanager
    def prepare_basic(self, p):
        org_fun = p.prepare
        new_fun = functools.partial(p.prepare, key=self.key,
                                    pkey=self.private_key,
                                    output=self.output,
                                    callback=self.callback, )
        p.prepare = new_fun
        yield p
        p.prepare = org_fun


class BasePreparedRequestParams(object):
    DEFAULT_URL = None
    ROUTE_KEY = RouteKey.UNKNOWN

    def __init__(self):
        self.key = None
        self._pkey = None
        self.output = None
        self.callback = None

    def __unicode__(self):
        params = list(self.__dict__)
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
        p.update({'sig': self.prepared_sig} if self._pkey else {})
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

    def prepare_base(self, key=None, pkey=None, output=None, callback=None):
        self._pkey = pkey
        self.prepare_key(key)
        self.prepare_output(output)
        self.prepare_callback(callback)

    def prepare_key(self, key):
        self.key = key

    def prepare_output(self, output):
        if output is None:
            return

        if isinstance(output, OutputFmt):
            self.output = output
        else:
            if output.lower() == FORMAT_JSON:
                self.output = OutputFmt.JSON
            elif output.lower() == FORMAT_XML:
                self.output = OutputFmt.XML

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
        if self._pkey:
            return Sig(pkey=self._pkey, kwargs=self.generate_params())

    @property
    def prepared_sig(self):
        if self._pkey:
            return self.sig.hashed_sig

    @contextlib.contextmanager
    def init_basic_params(self, params, optionals=None):
        new_params = self._init_basic_params(params)
        yield new_params

        self._init_optional_params(params, optionals)

    def _init_basic_params(self, params):
        params['key'] = self.prepared_key

        params.update(
            {'output': self.prepared_output}
            if self.prepared_output else {})
        params.update(
            {'callback': self.prepared_callback}
            if self.prepared_callback else {})

        return params

    @staticmethod
    def _init_optional_params(params, optionals):

        if optionals:
            for opt, opt_v in iteritems(optionals):
                params.update({opt: opt_v} if opt_v is not None else {})

        return params


class BaseResponseData(object):
    ROUTE_KEY = RouteKey.UNKNOWN

    def __init__(self, raw_data, version=AMapVersion.V3,
                 auto_version=False, static_mode=False, raw_mode=False):

        if raw_mode:
            self._raw_data = raw_data
        else:
            self._raw_data = json_load_and_fix_amap_empty(raw_data)
        self.version = version
        self._data = None

        if auto_version:
            self.version = self.auto_check_version(
                self._raw_data, self.version)

        if static_mode:
            self._data = self._get_static_data()

    def __unicode__(self):
        return repr_params(('status', 'status_msg', 'count', 'version'),
                           self.__class__.__name__, self)

    def __repr__(self):
        return self.__unicode__()

    @property
    def status(self):
        return self._get_status()

    @property
    def status_msg(self):
        return self._get_status_msg()

    @property
    def count(self):
        return self._get_count()

    @property
    def data(self):
        return self._data or self._get_data()

    @staticmethod
    def auto_check_version(data, default_version=AMapVersion.V3):
        if 'errcode' in data:
            return AMapVersion.V4
        else:
            return default_version

    def raise_for_status(self):
        if self.status == StatusFlag.ERR:
            err_status = self.status_msg
            raise amap_status_exception(
                err_code=err_status.code,
                err_msg=err_status.msg or err_status.detail,
                data=self)

    def _get_status(self):
        if self.version == AMapVersion.V3:
            return self._get_status_v3(self._raw_data.get('status'))
        elif self.version == AMapVersion.V4:
            return self._get_status_v4(self._raw_data.get('errcode'))

    @staticmethod
    def _get_status_v3(status_code):
        return StatusFlag.OK if status_code == '1' else StatusFlag.ERR

    @staticmethod
    def _get_status_v4(status_code):
        return StatusFlag.OK if status_code == 0 else StatusFlag.ERR

    def _get_status_msg(self):
        if self.version == AMapVersion.V3:
            return MapStatusMessage.from_args(
                code=int(self._raw_data.get('infocode', -1)),
                msg=self._raw_data.get('info'),
                detail='')
        elif self.version == AMapVersion.V4:
            return MapStatusMessage.from_args(
                code=self._raw_data.get('errcode'),
                msg=self._raw_data.get('errmsg'),
                detail=self._raw_data.get('errdetail'))

    def _get_count(self):
        if self.version == AMapVersion.V3:
            return int(self._raw_data.get('count', 0))
        elif self.version == AMapVersion.V4:
            return 0

    def _get_data(self):
        return self.get_data(self._raw_data)

    def _get_static_data(self):
        return self.get_data(self._raw_data, static=True)

    def get_data(self, raw_data, static=False):
        raise NotImplementedError


class LocationMixin(object):
    @property
    def latitude(self):
        try:
            return parse_location(getattr(self, 'location'))[1]
        except Exception:
            return None

    @property
    def longitude(self):
        try:
            return parse_location(getattr(self, 'location'))[0]
        except Exception:
            return None

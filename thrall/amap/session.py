# coding: utf-8
from __future__ import absolute_import

from ..base import BaseDecoderAdapter, BaseEncoderAdapter, BaseRequest
from ..hooks import SetDefault
from ..settings import GLOBAL_CONFIG
from ..utils import check_params_type
from .adapters import AMapEncodeAdapter, AMapJsonDecoderAdapter
from .request import AMapRequest
from .urls import GEO_CODING_URL, REGEO_CODING_URL

_set_default = SetDefault()


class AMapSession(object):
    _ENCODE = 'encode'
    _DECODE = 'decode'
    _REQUEST = 'request'

    def __init__(self, default_key=None, default_private_key=None):
        self.encoder = None
        self.decoder = None
        self.request = None
        self.defaults = _set_default
        self.mount(self._ENCODE, AMapEncodeAdapter())
        self.mount(self._DECODE, AMapJsonDecoderAdapter())
        self.mount(self._REQUEST, AMapRequest())
        _set_default.set_default(key=default_key,
                                 private_key=default_private_key)

    def mount(self, schema, adapter):
        if schema == self._ENCODE:
            self._mount_encoder(adapter)
        elif schema == self._DECODE:
            self._mount_decoder(adapter)
        elif schema == self._REQUEST:
            self._mount_request(adapter)
        else:
            raise TypeError(
                'Error adapter got, must extend from base adapter')

    @check_params_type(adapter=(BaseEncoderAdapter,))
    def _mount_encoder(self, adapter):
        self.encoder = adapter

    @check_params_type(adapter=(BaseDecoderAdapter,))
    def _mount_decoder(self, adapter):
        self.decoder = adapter

    @check_params_type(adapter=(BaseRequest,))
    def _mount_request(self, request):
        self.request = request

    @_set_default
    def geo_code(self, address, city=None, **kwargs):
        p = self.encoder.encode_geo_code(address=address,
                                         city=city,
                                         **kwargs)
        r = self.request.get(GEO_CODING_URL.url, params=p.params)

        d = self.decoder.decode_geo_code(raw_data=r.content,
                                         version=GEO_CODING_URL.version)

        return d

    @_set_default
    def regeo_code(self, location, radius=None, batch=None,
                   extensions=None, **kwargs):
        p = self.encoder.encode_regeo_code(location=location,
                                           radius=radius,
                                           extensions=extensions,
                                           batch=batch,
                                           **kwargs)

        r = self.request.get(REGEO_CODING_URL.url, params=p.params)

        d = self.decoder.decode_regeo_code(raw_data=r.content,
                                           version=REGEO_CODING_URL.version)

        return d


amap_session = AMapSession(default_key=GLOBAL_CONFIG.AMAP_TEST_KEY)

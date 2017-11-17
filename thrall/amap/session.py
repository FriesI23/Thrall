# coding: utf-8
from __future__ import absolute_import

from ..base import BaseDecoderAdapter, BaseEncoderAdapter, BaseRequest
from ..hooks import SetDefault
from ..settings import GLOBAL_CONFIG
from ..utils import check_params_type
from .adapters import AMapEncodeAdapter, AMapJsonDecoderAdapter
from .request import AMapRequest
from .urls import (
    DISRANCE_URL,
    GEO_CODING_URL,
    POI_SEARCH_AROUND_URL,
    POI_SEARCH_TEXT_URL,
    POI_SUGGEST_URL,
    REGEO_CODING_URL
)

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
        self.mount(self._DECODE, AMapJsonDecoderAdapter(static_mode=True))
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

    @_set_default
    def search_text(self, keywords=None, types=None, city=None,
                    city_limit=None, children=None, offset=None, page=None,
                    building=None, floor=None, extensions=None, **kwargs):
        p = self.encoder.encode_search_text(keywords=keywords,
                                            types=types,
                                            city=city,
                                            city_limit=city_limit,
                                            children=children,
                                            offset=offset,
                                            page=page,
                                            building=building,
                                            floor=floor,
                                            extensions=extensions,
                                            **kwargs)
        r = self.request.get(POI_SEARCH_TEXT_URL.url, params=p.params)

        d = self.decoder.decode_search_text(
            raw_data=r.content,
            version=POI_SEARCH_TEXT_URL.version)
        return d

    @_set_default
    def search_around(self, location=None, keywords=None, types=None,
                      city=None,
                      radius=None, sort_rule=None, offset=None, page=None,
                      extensions=None, **kwargs):
        p = self.encoder.encode_search_around(location=location,
                                              keywords=keywords,
                                              types=types,
                                              city=city,
                                              radius=radius,
                                              sort_rule=sort_rule,
                                              offset=offset,
                                              page=page,
                                              extensions=extensions,
                                              **kwargs)
        r = self.request.get(POI_SEARCH_AROUND_URL.url, params=p.params)

        d = self.decoder.decode_search_around(
            raw_data=r.content,
            version=POI_SEARCH_TEXT_URL.version)
        return d

    @_set_default
    def suggest(self, keyword=None, types=None, location=None, city=None,
                city_limit=None, data_type=None, **kwargs):
        p = self.encoder.encode_suggest(keyword=keyword,
                                        types=types,
                                        location=location,
                                        city=city,
                                        city_limit=city_limit,
                                        data_type=data_type,
                                        **kwargs)
        r = self.request.get(POI_SUGGEST_URL.url, params=p.params)

        d = self.decoder.decode_suggest(raw_data=r.content,
                                        version=POI_SUGGEST_URL.version)
        return d

    @_set_default
    def distance(self, origins=None, destination=None, type=None, **kwargs):
        p = self.encoder.encode_distance(origins=origins,
                                         destination=destination,
                                         type=type,
                                         **kwargs)
        r = self.request.get(DISRANCE_URL.url, params=p.params)

        d = self.decoder.decode_distance(raw_data=r.content,
                                         version=DISRANCE_URL.version)

        return d


amap_session = AMapSession(default_key=GLOBAL_CONFIG.AMAP_TEST_KEY)

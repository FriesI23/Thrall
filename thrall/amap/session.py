# coding: utf-8
from __future__ import absolute_import

from ..base import BaseDecoderAdapter, BaseEncoderAdapter, BaseRequest
from ..hooks import SetDefault
from ..settings import GLOBAL_CONFIG
from ..utils import check_params_type
from .adapters import AMapEncodeAdapter, AMapJsonDecoderAdapter
from .request import AMapRequest

_set_default = SetDefault()


class SessionHookMixin(object):

    def DEFAULT_HOOK(self, *args, **kwargs):
        """ empty hook, return nothing """

    def __init__(self):
        self.hooks = {}

    def add_hook(self, func, prefix, hook):
        if not callable(hook):
            raise TypeError('{} object is not callable'.format(type(hook)))

        if callable(func):
            self.hooks['{}_{}'.format(prefix, func.__name__)] = hook
        else:
            self.hooks['{}_{}'.format(prefix, func)] = hook

    def get_hook(self, func_name, prefix, override_func=None):
        if callable(override_func):
            return override_func

        fn = self.hooks.get('{}_{}'.format(prefix, func_name))
        return fn or self.DEFAULT_HOOK


class AMapSession(SessionHookMixin):
    _ENCODE = 'encode'
    _DECODE = 'decode'
    _REQUEST = 'request'

    _PREPARED_HOOK_PREFIX = 'prepared'
    _RESPONSE_HOOK_PREFIX = 'response'

    def _run_prepared_hook(self, route_key, p, override_func=None):
        hook = self.get_hook(route_key, self._PREPARED_HOOK_PREFIX,
                             override_func=override_func)
        return hook(p)

    def _run_response_hook(self, route_Key, r, override_func=None):
        hook = self.get_hook(route_Key, self._RESPONSE_HOOK_PREFIX,
                             override_func=override_func)
        return hook(r)

    def __init__(self, default_key=None, default_private_key=None):
        super(AMapSession, self).__init__()
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
    def geo_code(self, address, city=None, prepared_hook=None,
                 response_hook=None, **kwargs):
        route_key = 'geo_code'

        p = self.encoder.encode_geo_code(address=address,
                                         city=city,
                                         **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_geo_code(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_geo_code(raw_data=r.content)

        return d

    @_set_default
    def regeo_code(self, location, radius=None, batch=None, extensions=None,
                   prepared_hook=None, response_hook=None, **kwargs):
        route_key = 'regeo_code'

        p = self.encoder.encode_regeo_code(location=location,
                                           radius=radius,
                                           extensions=extensions,
                                           batch=batch,
                                           **kwargs)

        self._run_prepared_hook(route_key, p, prepared_hook)
        r = self.request.get_regeo_code(p)
        self._run_response_hook(route_key, p, response_hook)

        d = self.decoder.decode_regeo_code(raw_data=r.content)

        return d

    @_set_default
    def search_text(self, keywords=None, types=None, city=None,
                    city_limit=None, children=None, offset=None, page=None,
                    building=None, floor=None, extensions=None,
                    prepared_hook=None, response_hook=None, **kwargs):
        route_key = 'search_text'

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
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_search_text(p)
        self._run_response_hook(route_key, p, response_hook)

        d = self.decoder.decode_search_text(raw_data=r.content)
        return d

    @_set_default
    def search_around(self, location=None, keywords=None, types=None,
                      city=None, radius=None, sort_rule=None, offset=None,
                      page=None, extensions=None, prepared_hook=None,
                      response_hook=None, **kwargs):
        route_key = 'search_around'

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
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_search_around(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_search_around(raw_data=r.content)
        return d

    @_set_default
    def suggest(self, keyword=None, types=None, location=None, city=None,
                city_limit=None, data_type=None, prepared_hook=None,
                response_hook=None, **kwargs):
        route_key = 'suggest'

        p = self.encoder.encode_suggest(keyword=keyword,
                                        types=types,
                                        location=location,
                                        city=city,
                                        city_limit=city_limit,
                                        data_type=data_type,
                                        **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_suggest(p)
        self._run_response_hook(route_key, p, response_hook)

        d = self.decoder.decode_suggest(raw_data=r.content)
        return d

    @_set_default
    def distance(self, origins=None, destination=None, type=None,
                 prepared_hook=None, response_hook=None, **kwargs):
        route_key = 'distance'

        p = self.encoder.encode_distance(origins=origins,
                                         destination=destination,
                                         type=type,
                                         **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_distance(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_distance(raw_data=r.content)

        return d


amap_session = AMapSession(default_key=GLOBAL_CONFIG.AMAP_TEST_KEY)

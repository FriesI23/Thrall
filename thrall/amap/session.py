# coding: utf-8
from __future__ import absolute_import

from ..base import BaseDecoderAdapter, BaseEncoderAdapter, BaseRequest
from ..hooks import SetDefault
from ..settings import GLOBAL_CONFIG
from ..utils import check_params_type
from ..consts import RouteKey
from .adapters import AMapEncodeAdapter, AMapJsonDecoderAdapter
from .request import AMapRequest, AMapBatchRequest
from . import urls, models

_set_default = SetDefault()
_set_batch_default = SetDefault()

BATCH_URL_DEFAULT_PAIRS = {
    RouteKey.GEO_CODE: urls.GEO_CODING_URL,
    RouteKey.REGEO_CODE: urls.REGEO_CODING_URL,
    RouteKey.SEARCH_TEXT: urls.POI_SEARCH_TEXT_URL,
    RouteKey.SEARCH_AROUND: urls.POI_SEARCH_AROUND_URL,
    RouteKey.SUGGEST: urls.POI_SUGGEST_URL,
    RouteKey.DISTANCE: urls.DISRANCE_URL,
    RouteKey.NAVI_RIDING: urls.NAVI_RIDING_URL,
    RouteKey.NAVI_DRIVING: urls.NAVI_DRIVING_URL,
    RouteKey.NAVI_WAKLING: urls.NAVI_WALKING_URL,
    RouteKey.DISTRICT: urls.DISTRICT_URL,
}

BATCH_DECODE_DEFAULT_PAIRS = {
    RouteKey.GEO_CODE: models.GeoCodeResponseData,
    RouteKey.REGEO_CODE: models.ReGeoCodeResponseData,
    RouteKey.SEARCH_TEXT: models.SearchResponseData,
    RouteKey.SEARCH_AROUND: models.SearchResponseData,
    RouteKey.SEARCH: models.SearchResponseData,
    RouteKey.SUGGEST: models.SuggestResponseData,
    RouteKey.DISTANCE: models.DistanceResponseData,
    RouteKey.NAVI_RIDING: models.NaviRidingResponseData,
    RouteKey.NAVI_WAKLING: models.NaviWalkingResponseData,
    RouteKey.NAVI_DRIVING: models.NaviDrivingResponseData,
    RouteKey.DISTRICT: models.DistrictResponseData,
}


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
    _B_REQUEST = 'batch_request'

    _PREPARED_HOOK_PREFIX = 'prepared'
    _RESPONSE_HOOK_PREFIX = 'response'

    def _run_prepared_hook(self, route_key, p, override_func=None):
        hook = self.get_hook(route_key, self._PREPARED_HOOK_PREFIX,
                             override_func=override_func)
        return hook(p)

    def _run_response_hook(self, route_key, r, override_func=None):
        hook = self.get_hook(route_key, self._RESPONSE_HOOK_PREFIX,
                             override_func=override_func)
        return hook(r)

    def __init__(self, default_key=None, default_private_key=None,
                 default_batch_urls=BATCH_URL_DEFAULT_PAIRS,
                 default_batch_decoders=BATCH_DECODE_DEFAULT_PAIRS):
        super(AMapSession, self).__init__()
        self.encoder = None
        self.decoder = None
        self.request = None
        self.brequest = None

        self._defaults = SetDefault()
        self._batch_default = SetDefault()

        self.mount(self._ENCODE, AMapEncodeAdapter())
        self.mount(self._DECODE, AMapJsonDecoderAdapter(static_mode=True))
        self.mount(self._REQUEST, AMapRequest())
        self.mount(self._B_REQUEST, AMapBatchRequest())

        self._defaults.set_default(key=default_key,
                                   private_key=default_private_key,
                                   response_hook=None,
                                   prepared_hook=None)
        self._batch_default.set_default(key=default_key,
                                        url_pairs=default_batch_urls,
                                        decode_pairs=default_batch_decoders,
                                        prepared_hook=None,
                                        response_hook=None)

    def mount(self, schema, adapter):
        if schema == self._ENCODE:
            self._mount_encoder(adapter)
        elif schema == self._DECODE:
            self._mount_decoder(adapter)
        elif schema == self._REQUEST:
            self._mount_request(adapter)
        elif schema == self._B_REQUEST:
            self._mount_batch_request(adapter)
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
    def _mount_request(self, adapter):
        self.request = adapter

    @check_params_type(adapter=(BaseRequest,))
    def _mount_batch_request(self, adapter):
        self.brequest = adapter

    def batch(self, *args, **kwargs):
        return self._batch_default(self._batch)(*args, **kwargs)

    def _batch(self, *args, **kwargs):
        route_key = RouteKey.BATCH.value
        decode_pairs = kwargs.pop('decode_pairs')
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_batch(*args, **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.brequest.get_batch(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_batch(raw_data=r.content, p=p,
                                      decode_pairs=decode_pairs)

        return d

    def geo_code(self, *args, **kwargs):
        return self._defaults(self._geo_code)(*args, **kwargs)

    def _geo_code(self, *args, **kwargs):
        route_key = 'geo_code'
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_geo_code(*args, **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_geo_code(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_geo_code(raw_data=r.content)

        return d

    def regeo_code(self, *args, **kwargs):
        return self._defaults(self._regeo_code)(*args, **kwargs)

    def _regeo_code(self, *args, **kwargs):
        route_key = RouteKey.REGEO_CODE.value
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_regeo_code(*args, **kwargs)

        self._run_prepared_hook(route_key, p, prepared_hook)
        r = self.request.get_regeo_code(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_regeo_code(raw_data=r.content)

        return d

    def search_text(self, *args, **kwargs):
        return self._defaults(self._search_text)(*args, **kwargs)

    def _search_text(self, *args, **kwargs):
        route_key = RouteKey.SEARCH_TEXT.value
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_search_text(*args, **kwargs)

        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_search_text(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_search_text(raw_data=r.content)
        return d

    def search_around(self, *args, **kwargs):
        return self._defaults(self._search_around)(*args, **kwargs)

    def _search_around(self, *args, **kwargs):
        route_key = RouteKey.SEARCH_AROUND.value
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_search_around(*args, **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_search_around(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_search_around(raw_data=r.content)
        return d

    def suggest(self, *args, **kwargs):
        return self._defaults(self._suggest)(*args, **kwargs)

    def _suggest(self, *args, **kwargs):
        route_key = RouteKey.SUGGEST.value
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_suggest(*args, **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_suggest(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_suggest(raw_data=r.content)
        return d

    def district(self, *args, **kwargs):
        return self._defaults(self._district)(*args, **kwargs)

    def _district(self, *args, **kwargs):
        route_key = RouteKey.DISTRICT.value
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_district(*args, **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_district(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_district(raw_data=r.content)
        return d

    def distance(self, *args, **kwargs):
        return self._defaults(self._distance)(*args, **kwargs)

    def _distance(self, *args, **kwargs):
        route_key = RouteKey.DISTANCE.value
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_distance(*args, **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_distance(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_distance(raw_data=r.content)

        return d

    def riding(self, *args, **kwargs):
        return self._defaults(self._riding)(*args, **kwargs)

    def _riding(self, *args, **kwargs):
        route_key = RouteKey.NAVI_RIDING.value
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_riding(*args, **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_riding(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_riding(raw_data=r.content, auto_version=True)

        return d

    def walking(self, *args, **kwargs):
        return self._defaults(self._walking)(*args, **kwargs)

    def _walking(self, *args, **kwargs):
        route_key = RouteKey.NAVI_WAKLING.value
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_walking(*args, **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_walking(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_walking(raw_data=r.content)

        return d

    def driving(self, *args, **kwargs):
        return self._defaults(self._driving)(*args, **kwargs)

    def _driving(self, *args, **kwargs):
        route_key = RouteKey.NAVI_DRIVING.value
        prepared_hook = kwargs.pop('prepared_hook', None)
        response_hook = kwargs.pop('response_hook', None)

        p = self.encoder.encode_driving(*args, **kwargs)
        self._run_prepared_hook(route_key, p, prepared_hook)

        r = self.request.get_driving(p)
        self._run_response_hook(route_key, r, response_hook)

        d = self.decoder.decode_driving(raw_data=r.content)

        return d


amap_session = AMapSession(default_key=GLOBAL_CONFIG.AMAP_TEST_KEY)

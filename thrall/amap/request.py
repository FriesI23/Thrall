# coding: utf-8
from __future__ import absolute_import

from six import iteritems
import json

from thrall.compat import urlencode, unicode

from .urls import (
    DISRANCE_URL,
    GEO_CODING_URL,
    POI_SEARCH_AROUND_URL,
    POI_SEARCH_TEXT_URL,
    POI_SUGGEST_URL,
    REGEO_CODING_URL,
    NAVI_RIDING_URL,
    NAVI_DRIVING_URL,
    NAVI_WALKING_URL,
)
from ..base import BaseRequest


class AMapRequest(BaseRequest):
    def __init__(self, session=None, enable_https=False):
        super(AMapRequest, self).__init__(session=session)
        self._is_https = enable_https

    def _url_swith(self, oru, dfu, url):
        if oru:
            return oru
        else:
            return url or dfu

    def get_data(self, p, default_url, url=None, **kwargs):
        params = p.params
        url = self._url_swith(url, default_url, p.DEFAULT_URL)
        return self.get(url.https_url if self._is_https else url.url,
                        params=params, **kwargs)

    def get_geo_code(self, p, **kwargs):
        return self.get_data(p, default_url=GEO_CODING_URL, **kwargs)

    def get_regeo_code(self, p, **kwargs):
        return self.get_data(p, default_url=REGEO_CODING_URL, **kwargs)

    def get_search_text(self, p, **kwargs):
        return self.get_data(p, default_url=POI_SEARCH_TEXT_URL, **kwargs)

    def get_search_around(self, p, **kwargs):
        return self.get_data(p, default_url=POI_SEARCH_AROUND_URL, **kwargs)

    def get_suggest(self, p, **kwargs):
        return self.get_data(p, default_url=POI_SUGGEST_URL, **kwargs)

    def get_distance(self, p, **kwargs):
        return self.get_data(p, default_url=DISRANCE_URL, **kwargs)

    def get_riding(self, p, **kwargs):
        return self.get_data(p, default_url=NAVI_RIDING_URL, **kwargs)

    def get_walking(self, p, **kwargs):
        return self.get_data(p, default_url=NAVI_WALKING_URL, **kwargs)

    def get_driving(self, p, **kwargs):
        return self.get_data(p, default_url=NAVI_DRIVING_URL, **kwargs)


class AMapBatchRequest(BaseRequest):
    _POST_URL = 'http://restapi.amap.com/v3/batch'
    _HTTPS_POST_URL = 'https://restapi.amap.com/v3/batch'

    def __init__(self, session=None, enable_https=False):
        super(AMapBatchRequest, self).__init__(session=session)
        self._is_https = enable_https

    def get_batch_data(self, request_list, key=None, **kwargs):
        """ AMap batch request

        :param request_list: [{'url': ..., 'params': ...}, ...]
        :param key: amap request key
        :return: response
        """
        ops_params = {
            'ops': [{'url': self._construct_ops(r['url'], r['params'])}
                    for r in request_list]}

        return self.post(
            url="{}?key={}".format(
                self._HTTPS_POST_URL if self._is_https else self._POST_URL,
                key),
            data=json.dumps(ops_params),
            headers={'Content-Type': 'application/json'},
            **kwargs)

    def _construct_ops(self, url, params):
        return '{}?{}'.format(url, urlencode(
            {k: unicode(v).encode('utf-8') for k, v in iteritems(params)}
        ))

    def get_batch(self, p, **kwargs):
        params = p.params
        return self.get_batch_data(params['batch'], params['key'], **kwargs)

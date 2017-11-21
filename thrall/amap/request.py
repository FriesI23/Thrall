# coding: utf-8
from __future__ import absolute_import

from six import iteritems
import json

from thrall.compat import urlencode, unicode
from thrall.utils import partialmethod

from .urls import (
    DISRANCE_URL,
    GEO_CODING_URL,
    POI_SEARCH_AROUND_URL,
    POI_SEARCH_TEXT_URL,
    POI_SUGGEST_URL,
    REGEO_CODING_URL,
    NAVI_RIDING_URL,
)
from ..base import BaseRequest


class AMapRequest(BaseRequest):

    def _url_swith(self, oru, dfu, url):
        if oru:
            return oru
        else:
            return url or dfu

    def get_data(self, p, default_url, url=None, **kwargs):
        params = p.params
        url = self._url_swith(url, default_url, p.DEFAULT_URL)
        return self.get(url.url, params=params, **kwargs)

    get_geo_code = partialmethod(get_data, default_url=GEO_CODING_URL)

    get_regeo_code = partialmethod(get_data, default_url=REGEO_CODING_URL)

    get_search_text = partialmethod(get_data, default_url=POI_SEARCH_TEXT_URL)

    get_search_around = partialmethod(get_data,
                                      default_url=POI_SEARCH_AROUND_URL)

    get_suggest = partialmethod(get_data, default_url=POI_SUGGEST_URL)

    get_distance = partialmethod(get_data, default_url=DISRANCE_URL)

    get_riding = partialmethod(get_data, default_url=NAVI_RIDING_URL)


class AMapBatchRequest(BaseRequest):
    _POST_URL = 'http://restapi.amap.com/v3/batch'

    def get_batch_data(self, request_list, key=None, **kwargs):
        """ AMap batch request

        :param request_list: [{'url': ..., 'params': ...}, ...]
        :param key: amap request key
        :return: response
        """
        ops_params = {
            'ops': [{'url': self._construct_ops(r['url'], r['params'])}
                    for r in request_list]}

        return self.post(url="{}?key={}".format(self._POST_URL, key),
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

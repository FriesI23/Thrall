# coding: utf-8
from __future__ import absolute_import

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

# coding: utf-8
from __future__ import absolute_import

from enum import IntEnum, Enum


class MapSource(IntEnum):
    A_MAP = 1
    QQ_MAP = 2
    BAIDU_MAP = 3


FORMAT_JSON = 'json'
FORMAT_XML = 'xml'

AMAP = 'AMAP'
QQMAP = 'QQMAP'
BAIDUMAP = 'BDMAP'


class RouteKey(Enum):
    UNKNOWN = 'unknown'
    GEO_CODE = 'geo_code'
    REGEO_CODE = 'regeo_code'
    SEARCH = 'search'
    SEARCH_TEXT = 'search_text'
    SEARCH_AROUND = 'search_around'
    SUGGEST = 'suggest'
    DISTANCE = 'distance'
    NAVI_RIDING = 'navi_riding'
    NAVI_WAKLING = 'navi_walking'
    NAVI_DRIVING = 'navi_driving'
    BATCH = 'batch'

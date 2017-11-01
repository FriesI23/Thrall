# coding: utf-8
"""
>>> print(GEO_CODING_URL)
http://restapi.amap.com/v3/geocode/geo
>>> print(REGEO_CODING_URL)
http://restapi.amap.com/v3/geocode/regeo
>>> print(POI_SEARCH_AROUND_URL)
http://restapi.amap.com/v3/place/around
>>> print(POI_SEARCH_TEXT_URL)
http://restapi.amap.com/v3/place/text
>>> print(POI_SUGGEST_URL)
http://restapi.amap.com/v3/assistant/inputtips
>>> print(NAVI_WALKING_URL)
http://restapi.amap.com/v3/direction/walking
>>> print(NAVI_DRIVING_URL)
http://restapi.amap.com/v3/direction/driving
>>> print(NAVI_RIDING_URL)
http://restapi.amap.com/v4/direction/bicycling
"""
from __future__ import absolute_import

from ..utils import NamedURL
from .consts import AMapVersion

GEO_CODING_URL = NamedURL.from_args(
    name='geocode_geo',
    url='http://restapi.amap.com/v3/geocode/geo',
    version=AMapVersion.V3,
)

REGEO_CODING_URL = NamedURL.from_args(
    name='geocode_regeo',
    url='http://restapi.amap.com/v3/geocode/regeo',
    version=AMapVersion.V3,
)

POI_SUGGEST_URL = NamedURL.from_args(
    name='assistant_inputtips',
    url='http://restapi.amap.com/v3/assistant/inputtips',
    version=AMapVersion.V3,
)

POI_SEARCH_TEXT_URL = NamedURL.from_args(
    name='place_text',
    url='http://restapi.amap.com/v3/place/text',
    version=AMapVersion.V3,
)

POI_SEARCH_AROUND_URL = NamedURL.from_args(
    name='place_around',
    url='http://restapi.amap.com/v3/place/around',
    version=AMapVersion.V3,
)

NAVI_WALKING_URL = NamedURL.from_args(
    name='direction_walking',
    url='http://restapi.amap.com/v3/direction/walking',
    version=AMapVersion.V3,
)

NAVI_DRIVING_URL = NamedURL.from_args(
    name='direction_driving',
    url='http://restapi.amap.com/v3/direction/driving',
    version=AMapVersion.V3,
)

NAVI_RIDING_URL = NamedURL.from_args(
    name='direction_riding',
    url='http://restapi.amap.com/v4/direction/bicycling',
    version=AMapVersion.V4,
)

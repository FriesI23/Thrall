# coding: utf-8
from __future__ import absolute_import

from enum import IntEnum


class MapSource(IntEnum):
    A_MAP = 1
    QQ_MAP = 2
    BAIDU_MAP = 3


FORMAT_JSON = 'json'
FORMAT_XML = 'xml'

AMAP = 'AMAP'
QQMAP = 'QQMAP'
BAIDUMAP = 'BDMAP'

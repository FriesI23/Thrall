# coding: utf-8
from __future__ import absolute_import

from six import with_metaclass

from .structures import Singleton


class _GlobalConfigs(with_metaclass(Singleton)):
    AMAP_TEST_KEY = u'26885a28149a9869440c89def18d09f6'


GLOBAL_CONFIG = _GlobalConfigs()

# coding: utf-8
from __future__ import absolute_import

from ..base import BaseRequest


class AMapRequest(BaseRequest):

    def get(self, url, params, timeout=1, callback=None, **kwargs):
        return super(AMapRequest, self).get(
            url, params, timeout, callback, **kwargs)

    def post(self, url, data, timeout=1, callback=None, **kwargs):
        return super(AMapRequest, self).post(
            url, data, timeout, callback, **kwargs)

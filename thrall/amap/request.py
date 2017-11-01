# coding: utf-8
from __future__ import absolute_import

from thrall.compat import unicode
from thrall.utils import check_params_type

from ..base import BaseRequest
from .models import BasePreparedRequestParams


class AMapRequest(BaseRequest):

    @check_params_type(
        enforce=True,
        url=(str, unicode),
        params=(BasePreparedRequestParams, dict)
    )
    def get(self, url, params, timeout=1, callback=None, **kwargs):
        return super(AMapRequest, self).get(
            url, params, timeout, callback, **kwargs)

    @check_params_type(
        enforce=True,
        url=(str, unicode),
        data=(object,),
    )
    def post(self, url, data, timeout=1, callback=None, **kwargs):
        return super(AMapRequest, self).post(
            url, data, timeout, callback, **kwargs)

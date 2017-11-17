# coding: utf-8
from __future__ import absolute_import

from functools import partial

from .consts import AMAP


class VendorError(Exception):
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response', None)
        self.data = kwargs.pop('data', None)
        super(VendorError, self).__init__(*args, **kwargs)


class VendorStatusError(VendorError):
    """raise this error when vendor status check error"""


class AMapStatusError(VendorStatusError):
    """amap status error"""


class VendorParamError(VendorError):
    """raise this error when vendor type/value check error"""


class AMapBatchStatusError(VendorStatusError):
    """raise this error when amap batch request status error"""

    def __init__(self, *args, **kwargs):
        self.errors = kwargs.pop('errors', None)
        super(AMapBatchStatusError, self).__init__(*args, **kwargs)


def map_status_exception(err_msg=u'', map_source='UNKNOWN', err_code=-1,
                         response=None, data=None, exc=VendorStatusError):
    msg = u"{source}-ERROR: {err_code}-{err_msg}".format(
        source=map_source,
        err_code=err_code,
        err_msg=err_msg)

    return exc(msg, response=response, data=data)


def map_batch_status_exception(err_msg=u'', map_source='UNKNOWN', err_code=-1,
                               response=None, data=None, errors=None,
                               exc=VendorStatusError):
    msg = u"{source}-ERROR: {err_code}-{err_msg}".format(
        source=map_source,
        err_code=err_code,
        err_msg=err_msg)

    return exc(msg, response=response, data=data, errors=errors)


def map_params_exception(msg=u'', map_source='UNKNOWN', data=None,
                         exc=VendorParamError):
    _msg = u"{}-ERROR: {}".format(map_source, msg)

    return exc(_msg, data=data)


amap_status_exception = partial(
    map_status_exception, map_source=AMAP, exc=AMapStatusError)

amap_batch_status_exception = partial(
    map_batch_status_exception, map_source=AMAP, err_code=30001,
    exc=AMapBatchStatusError, err_msg='ENGINE_RESPONSE_DATA_ERROR')

amap_params_exception = partial(
    map_params_exception, map_source=AMAP)

# coding: utf-8
from __future__ import absolute_import

from hashlib import md5

from six import iteritems

from thrall.base import (
    BaseRequestParams as B_RP,
    BasePreparedRequestParams as BP_RP,
    BaseResponseData as B_RD,
    Sig as S,
)
from thrall.compat import unicode
from thrall.exceptions import amap_status_exception
from thrall.utils import MapStatusMessage, repr_params

from ..common import json_load_and_fix_amap_empty, parse_location
from ..consts import AMapVersion, ExtensionFlag, StatusFlag


class Extensions(object):
    """ AMap extension control class """

    def __init__(self, flag=False, **opt_options):
        """ get an instance of extensions.

        :param flag: extension flag, True if wan't enable extensions.
        :param opt_options: k, w pair of options.
        """
        self._flag = flag
        self._opt_options = opt_options

    def __getattr__(self, prop):
        return self._opt_options.get(prop)

    @property
    def status(self):
        return ExtensionFlag.ALL if self._flag else ExtensionFlag.BASE


class AMapSig(S):
    """ AMap sig generator """

    def __init__(self, pkey, hash_fn=md5, kwargs=None):
        """ get an instance of sig

            Note: sig must be enable in amap online control panel, please
                enable sig and got and pkey first.

            Please see: http://lbs.amap.com/faq/account/key/72

        :param pkey: amap private key.
        :param hash_fn: hash function, default by md5, custom hash function
        must implement digest function.
        :param kwargs: request params, same as request params.
        """
        super(AMapSig, self).__init__(pkey=pkey, hash_fn=hash_fn)
        self.kw = kwargs if kwargs is not None else {}

    @property
    def hashed_sig(self):
        sig = (self.unhash_sig.encode('utf-8') if isinstance(
            self.unhash_sig, unicode) else self.unhash_sig)

        return self.hash_func(sig).hexdigest()

    @property
    def unhash_sig(self):
        kw_pairs = sorted(iteritems(self.kw), key=lambda d: d[0])
        prepared_sig = u"{kw}{sig}".format(
            sig=self.private_key,
            kw=u"&".join([u"{k}={v}".format(k=k, v=v) for k, v in kw_pairs])
        )
        return prepared_sig


class AMapBaseRequestParams(B_RP):
    """amap base request params --> same as base request params"""

    def prepare_data(self):
        raise super(AMapBaseRequestParams, self).prepare_data()


class AMapBasePreparedRequestParams(BP_RP):

    def prepare(self, **kwargs):
        return super(AMapBasePreparedRequestParams, self).prepare(**kwargs)

    def generate_params(self):
        return super(AMapBasePreparedRequestParams, self).generate_params()

    @property
    def sig(self):
        if self._pkey:
            return AMapSig(pkey=self._pkey, kwargs=self.generate_params())

    @property
    def prepared_sig(self):
        if self._pkey:
            return self.sig.hashed_sig


class AmapBaseResponseData(B_RD):
    def __init__(self, raw_data, version=AMapVersion.V3,
                 auto_version=False, static_mode=False, raw_mode=False):
        super(AmapBaseResponseData, self).__init__(raw_data=raw_data,
                                                   version=version)

        if not raw_mode:
            self._raw_data = json_load_and_fix_amap_empty(raw_data)

        self._data = None

        if auto_version:
            self.version = self.auto_check_version(
                self._raw_data, self.version)

        if static_mode:
            self._data = self._get_static_data()

    @property
    def status(self):
        return self._get_status()

    @property
    def status_msg(self):
        return self._get_status_msg()

    @property
    def count(self):
        return self._get_count()

    @property
    def data(self):
        return self._data or self._get_data()

    @staticmethod
    def auto_check_version(data, default_version=AMapVersion.V3):
        if 'errcode' in data:
            return AMapVersion.V4
        else:
            return default_version

    def raise_for_status(self):
        if self.status == StatusFlag.ERR:
            err_status = self.status_msg
            raise amap_status_exception(
                err_code=err_status.code,
                err_msg=err_status.msg or err_status.detail,
                data=self)

    def _get_status(self):
        if self.version == AMapVersion.V3:
            return self._get_status_v3(self._raw_data.get('status'))
        elif self.version == AMapVersion.V4:
            return self._get_status_v4(self._raw_data.get('errcode'))

    @staticmethod
    def _get_status_v3(status_code):
        return StatusFlag.OK if status_code == '1' else StatusFlag.ERR

    @staticmethod
    def _get_status_v4(status_code):
        return StatusFlag.OK if status_code == 0 else StatusFlag.ERR

    def _get_status_msg(self):
        if self.version == AMapVersion.V3:
            return MapStatusMessage.from_args(
                code=int(self._raw_data.get('infocode', -1)),
                msg=self._raw_data.get('info'),
                detail='')
        elif self.version == AMapVersion.V4:
            return MapStatusMessage.from_args(
                code=self._raw_data.get('errcode'),
                msg=self._raw_data.get('errmsg'),
                detail=self._raw_data.get('errdetail'))

    def _get_count(self):
        if self.version == AMapVersion.V3:
            return int(self._raw_data.get('count', 0))
        elif self.version == AMapVersion.V4:
            return 0

    def _get_data(self):
        return self.get_data(self._raw_data)

    def _get_static_data(self):
        return self.get_data(self._raw_data, static=True)

    def get_data(self, raw_data, static=False):
        raise NotImplementedError


class LocationMixin(object):
    @property
    def latitude(self):
        try:
            return parse_location(getattr(self, 'location'))[1]
        except Exception:
            return None

    @property
    def longitude(self):
        try:
            return parse_location(getattr(self, 'location'))[0]
        except Exception:
            return None

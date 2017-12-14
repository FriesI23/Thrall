# coding: utf-8
from __future__ import absolute_import

from thrall.exceptions import amap_batch_status_exception

from ._base_model import (
    AMapBasePreparedRequestParams,
    AMapBaseRequestParams,
    BaseResponseData,
)

from thrall.utils import MapStatusMessage


class BatchRequestParams(AMapBaseRequestParams):
    def __init__(self, batch_list=None, key=None, url_pairs=None):
        if batch_list is None:
            batch_list = []
        if url_pairs is None:
            url_pairs = {}

        self.batch_list = batch_list
        self.url_pairs = url_pairs
        super(BatchRequestParams, self).__init__(key=key)

    def prepare_data(self):
        _p = PreparedBatchParams(url_pairs=self.url_pairs)
        with self.prepare_basic(_p) as p:
            p.prepare(batch_list=self.batch_list, key=self.key)

        return p


class BatchExcMixin(object):
    def do_list_batch(self, iter_data, inside_func=lambda i: i):
        result_list = []
        errors_list = []
        err_count = 0

        for i in iter_data:
            try:
                result_list.append(inside_func(i))
            except Exception as err:
                errors_list.append(err)
                err_count += 1
            else:
                errors_list.append(None)

        if err_count:
            raise amap_batch_status_exception(errors=errors_list, data=self)

        return result_list


class PreparedBatchParams(AMapBasePreparedRequestParams, BatchExcMixin):
    def __init__(self, url_pairs=None):
        self.batch_list = []
        self.url_pairs = url_pairs
        super(PreparedBatchParams, self).__init__()

    def prepare(self, batch_list=None, key=None, **kwargs):
        self.prepare_batch_list(batch_list)
        self.prepare_base(key=key)

    def prepare_batch_list(self, batch_list):
        if batch_list is not None:
            self.batch_list = [i for i in batch_list]

    def prepared_batch_list(self):
        def prepare(i):
            return i.prepare()

        return self.do_list_batch(self.batch_list, prepare)

    def generate_params(self):
        prepared_list = self.prepared_batch_list()

        with self.init_basic_params({}) as params:
            params['batch'] = self.package_all_params(prepared_list)

        return params

    def package_all_params(self, prepared_list):
        return self.do_list_batch(prepared_list, self.package_param)

    def package_param(self, prepared_struc):
        route_key = prepared_struc.ROUTE_KEY

        params = prepared_struc.params
        url = self.url_pairs[route_key]

        return {'url': url.path, 'params': params}


class BatchResponseData(BaseResponseData, BatchExcMixin):
    def __init__(self, raw_data, p, decode_pairs, static_mode=False):
        self.prepared_data = p
        self.decode_pairs = decode_pairs or {}
        super(BatchResponseData, self).__init__(raw_data,
                                                static_mode=static_mode)

    @property
    def status(self):
        if isinstance(self._raw_data, list):
            return self._get_status_v3('1')
        else:
            return super(BatchResponseData, self).status

    @property
    def count(self):
        if isinstance(self._raw_data, list):
            return len(self._raw_data)
        else:
            return super(BatchResponseData, self).count

    @property
    def status_msg(self):
        if isinstance(self._raw_data, list):
            return MapStatusMessage.from_args(
                code=10000,
                msg='OK',
                detail='')
        else:
            return super(BatchResponseData, self).status_msg

    @property
    def batch_status(self):
        data = self.data
        return [i.status for i in data]

    @property
    def batch_status_msg(self):
        data = self.data
        return [i.status_msg for i in data]

    def raise_for_status(self):
        def _raise_each_status(data):
            data.raise_for_status()

        super(BatchResponseData, self).raise_for_status()
        data = self.data

        self.do_list_batch(data, _raise_each_status)

    def get_data(self, raw_data, static=False):
        return [i for i in self._iter_get_data(raw_data, static) or []]

    def _iter_get_data(self, raw_data, static):
        if isinstance(raw_data, list):
            for param, data in zip(self.prepared_data.batch_list, raw_data):
                decoder = self.decode_pairs[param.ROUTE_KEY]

                yield decoder(data.get('body', {}),
                              static_mode=static, raw_mode=True)

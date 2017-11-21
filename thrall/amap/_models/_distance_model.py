# coding: utf-8
from __future__ import absolute_import

from thrall.base import BaseData
from thrall.exceptions import (
    amap_batch_status_exception,
    amap_status_exception
)
from thrall.consts import RouteKey
from thrall.utils import required_params

from ..common import (
    merge_location,
    merge_multi_locations,
    prepare_multi_locations
)
from ..consts import DistanceType
from ._base_model import (
    BasePreparedRequestParams,
    BaseRequestParams,
    BaseResponseData
)


class DistanceRequestParams(BaseRequestParams):
    ROUTE_KEY = RouteKey.DISTANCE

    @required_params('origins', 'destination')
    def __init__(self, origins=None, destination=None, type=None, **kwargs):
        self.origins = origins
        self.destination = destination
        self.type = type
        super(DistanceRequestParams, self).__init__(**kwargs)

    def prepare_data(self):
        _p = PreparedDistanceRequestParams()

        with self.prepare_basic(_p) as p:
            p.prepare(
                origins=self.origins,
                destination=self.destination,
                type=self.type,
            )

        return p


class PreparedDistanceRequestParams(BasePreparedRequestParams):
    ROUTE_KEY = RouteKey.DISTANCE

    def __init__(self):
        self.origins = None
        self.destination = None
        self.type = None
        super(PreparedDistanceRequestParams, self).__init__()

    def prepare(self, origins=None, destination=None, type=None, **kwargs):
        self.prepare_origins(origins)
        self.prepare_destination(destination)
        self.prepare_type(type)
        self.prepare_base(**kwargs)

    def prepare_origins(self, origins):
        if origins is not None:
            self.origins = prepare_multi_locations(origins)

    def prepare_destination(self, destination):
        if destination is None:
            return

        r = prepare_multi_locations(destination)

        if r:
            self.destination = r[0]

    def prepare_type(self, type_):
        if type_ is not None:
            self.type = DistanceType.choose(type_)

    @property
    def prepared_origins(self):
        if self.origins is not None:
            return merge_multi_locations(self.origins)

    @property
    def prepared_destination(self):
        if self.destination is not None:
            return merge_location(*self.destination)

    @property
    def prepared_type(self):
        if self.type is not None:
            return self.type

    def generate_params(self):
        _p = {}
        optional_params = {'type': self.prepared_type}
        with self.init_basic_params(_p, optionals=optional_params) as params:
            params['origins'] = self.prepared_origins
            params['destination'] = self.prepared_destination
            return params


class DistanceResponseData(BaseResponseData):
    ROUTE_KEY = RouteKey.DISTANCE
    _ROUTE = 'results'

    def get_data(self, raw_data, static=False):
        data = raw_data.get(self._ROUTE)
        return [DistanceData(d, static) for d in data] if data else []

    def raise_for_status(self):
        super(DistanceResponseData, self).raise_for_status()
        exc_raise = self._get_each_exceptions()
        if any(exc_raise):
            raise amap_batch_status_exception(errors=exc_raise, data=self)

    def _get_each_exceptions(self):
        _exc_list = []
        for i in self.data:
            if i.info is not None:
                exc = amap_status_exception(
                    err_code=i.code, err_msg=i.info, data=self)
                _exc_list.append(exc)
            else:
                _exc_list.append(None)

        return _exc_list


class DistanceData(BaseData):
    _properties = ('origin_id',
                   'dest_id',
                   'distance',
                   'duration',
                   'info',
                   'code')

    def decode_param(self, p, data):
        if p in ('origin_id', 'dest_id'):
            return int(data.get(p))
        elif p in ('distance', 'duration'):
            return float(data.get(p))

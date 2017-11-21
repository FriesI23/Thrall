# coding: utf-8
from __future__ import absolute_import

from thrall.base import BaseData
from thrall.utils import required_params
from thrall.consts import RouteKey

from ..common import (
    merge_location,
    prepare_first_location,
)
from ._base_model import (
    BasePreparedRequestParams,
    BaseRequestParams,
    BaseResponseData,
)


class NaviRidingRequestParams(BaseRequestParams):
    ROUTE_KEY = RouteKey.NAVI_RIDING

    @required_params('origin', 'destination')
    def __init__(self, origin=None, destination=None, **kwargs):
        self.origin = origin
        self.destination = destination
        super(NaviRidingRequestParams, self).__init__(**kwargs)

    def prepare_data(self):
        with self.prepare_basic(PreparedNaviRidingRequestParams()) as p:
            p.prepare(
                origin=self.origin,
                destination=self.destination,
            )

        return p


class PreparedNaviRidingRequestParams(BasePreparedRequestParams):
    ROUTE_KEY = RouteKey.NAVI_RIDING

    def __init__(self):
        self.origin = None
        self.destination = None
        super(PreparedNaviRidingRequestParams, self).__init__()

    def prepare(self, origin=None, destination=None, **kwargs):
        self.prepare_origin(origin)
        self.prepare_destination(destination)
        self.prepare_base(**kwargs)

    def prepare_origin(self, origin):
        if origin is None:
            return

        self.origin = prepare_first_location(origin)

    def prepare_destination(self, destination):
        if destination is None:
            return

        self.destination = prepare_first_location(destination)

    @property
    def prepared_origin(self):
        if self.origin is not None:
            return merge_location(*self.origin)

    @property
    def prepared_destination(self):
        if self.destination is not None:
            return merge_location(*self.destination)

    def generate_params(self):
        with self.init_basic_params({}) as params:
            params['origin'] = self.prepared_origin
            params['destination'] = self.prepared_destination
            return params


class NaviRidingResponseData(BaseResponseData):
    ROUTE_KEY = RouteKey.NAVI_RIDING
    _ROUTE = 'data'

    def get_data(self, raw_data, static=False):
        data = raw_data.get(self._ROUTE)
        return NaviRidingData(data, static=static)


class NaviRidingData(BaseData):
    _properties = ('destination', 'origin', 'paths')

    def decode_param(self, p, data):
        if p == 'paths':
            return self.decode_paths(data)

    def decode_paths(self, data):
        ds = data.get('paths')
        return [RidingPath(d, self._static) for d in ds] if ds else []


class RidingPath(BaseData):
    _properties = ('distance', 'duration', 'steps')

    def decode_param(self, p, data):
        if p == 'steps':
            return self.decode_steps(data.get('steps'))

    def decode_steps(self, data):
        return [RidingSteps(d, self._static) for d in data] if data else []


class RidingSteps(BaseData):
    _properties = ('instruction',
                   'road',
                   'distance',
                   'orientation',
                   'duration',
                   'polyline',
                   'action',
                   'assistant_action')

    def decode_param(self, p, data):
        if p == 'polyline':
            return self.decode_polyline(data.get('polyline'))

    def decode_polyline(self, polyline):
        if polyline:
            return [tuple(map(float, i.split(u',')))
                    for i in polyline.split(u';')]

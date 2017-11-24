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


class NavRequestParams(BaseRequestParams):

    @required_params('origin', 'destination')
    def __init__(self, origin=None, destination=None, **kwargs):
        self.origin = origin
        self.destination = destination
        super(NavRequestParams, self).__init__(**kwargs)


class NaviRidingRequestParams(NavRequestParams):
    ROUTE_KEY = RouteKey.NAVI_RIDING

    def prepare_data(self):
        with self.prepare_basic(PreparedNaviRidingRequestParams()) as p:
            p.prepare(
                origin=self.origin,
                destination=self.destination,
            )

        return p


class NaviWalkingRequestParams(NavRequestParams):
    ROUTE_KEY = RouteKey.NAVI_WAKLING

    def prepare_data(self):
        with self.prepare_basic(PreparedNaviWalkingRequestParams()) as p:
            p.prepare(
                origin=self.origin,
                destination=self.destination,
            )

        return p


class NaviDrivingRequestParams(NavRequestParams):
    # TODO: add more params support
    ROUTE_KEY = RouteKey.NAVI_DRIVING

    def prepare_data(self):
        with self.prepare_basic(PreparedNaviDrivingRequestParams()) as p:
            p.prepare(
                origin=self.origin,
                destination=self.destination,
            )

        return p


class PreparedNaviRAndWRequestParams(BasePreparedRequestParams):
    def __init__(self):
        self.origin = None
        self.destination = None
        super(PreparedNaviRAndWRequestParams, self).__init__()

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


class PreparedNaviRidingRequestParams(PreparedNaviRAndWRequestParams):
    ROUTE_KEY = RouteKey.NAVI_RIDING


class PreparedNaviWalkingRequestParams(PreparedNaviRAndWRequestParams):
    ROUTE_KEY = RouteKey.NAVI_WAKLING


class PreparedNaviDrivingRequestParams(PreparedNaviRidingRequestParams):
    # TODO: add more params support
    ROUTE_KEY = RouteKey.NAVI_DRIVING


class NaviDataBasic(BaseData):
    _properties = ('destination', 'origin', 'paths')

    def decode_param(self, p, data):
        if p == 'paths':
            return self.decode_paths(data)

    def decode_paths(self, data):
        raise NotImplementedError


class NaviPathBasic(BaseData):
    _properties = ('distance', 'duration', 'steps')

    def decode_param(self, p, data):
        if p == 'steps':
            return self.decode_steps(data.get('steps'))

    def decode_steps(self, data):
        raise NotImplementedError


class NaviStepsBasic(BaseData):
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


class NaviRidingResponseData(BaseResponseData):
    ROUTE_KEY = RouteKey.NAVI_RIDING
    _ROUTE = 'data'

    def get_data(self, raw_data, static=False):
        data = raw_data.get(self._ROUTE)
        return NaviRidingData(data, static=static)


class NaviRidingData(NaviDataBasic):

    def decode_paths(self, data):
        ds = data.get('paths')
        return [RidingPath(d, self._static) for d in ds] if ds else []


class RidingPath(NaviPathBasic):

    def decode_steps(self, data):
        return [RidingSteps(d, self._static) for d in data] if data else []


class RidingSteps(NaviStepsBasic):
    _properties = ('instruction',
                   'road',
                   'distance',
                   'orientation',
                   'duration',
                   'polyline',
                   'action',
                   'assistant_action')


class NaviWalkingResponseData(BaseResponseData):
    ROUTE_KEY = RouteKey.NAVI_WAKLING
    _ROUTE = 'route'

    def get_data(self, raw_data, static=False):
        data = raw_data.get(self._ROUTE)
        return NaviWalkingData(data, static=static)


class NaviWalkingData(NaviDataBasic):

    def decode_paths(self, data):
        ds = data.get('paths')
        return [WalkingPath(d, self._static) for d in ds] if ds else []


class WalkingPath(NaviPathBasic):

    def decode_steps(self, data):
        return [WalkingSteps(d, self._static) for d in data] if data else []


class WalkingSteps(NaviStepsBasic):
    _properties = ('instruction',
                   'orientation',
                   'road',
                   'distance',
                   'duration',
                   'polyline',
                   'action',
                   'assistant_action',
                   'walk_type')


class NaviDrivingResponseData(BaseResponseData):
    ROUTE_KEY = RouteKey.NAVI_DRIVING
    _ROUTE = 'route'

    def get_data(self, raw_data, static=False):
        data = raw_data.get(self._ROUTE)
        return NaviDrivingData(data, static=static)


class NaviDrivingData(NaviDataBasic):

    def decode_paths(self, data):
        ds = data.get('paths')
        return [DrivingPath(d, self._static) for d in ds] if ds else []


class DrivingPath(NaviPathBasic):
    _properties = ('distance',
                   'duration',
                   'strategy',
                   'tolls',
                   'toll_distance',
                   'restriction',
                   'traffic_lights',
                   'steps')

    def decode_steps(self, data):
        return [DrivingSteps(d, self._static) for d in data] if data else []


class DrivingSteps(NaviStepsBasic):
    _properties = ('instruction',
                   'orientation',
                   'distance',
                   'tolls',
                   'toll_distance',
                   'toll_road',
                   'duration',
                   'polyline',
                   'action',
                   'assistant_action')

# coding: utf-8
from __future__ import absolute_import

from thrall.base import BaseData
from thrall.utils import required_params

from ..common import (
    merge_location,
    merge_multi_poi,
    merge_poi_type,
    prepare_multi_locations,
    prepare_multi_pois
)
from ..consts import BatchFlag, ExtensionFlag, HomeOrCorpControl, RoadLevel
from ._base_model import (
    BasePreparedRequestParams,
    BaseRequestParams,
    BaseResponseData,
    Extensions,
    LocationMixin
)
from ._common_model import Building, BusinessArea, Neighborhood, StreetNumber


class ReGeoCodeRequestParams(BaseRequestParams):

    @required_params('location')
    def __init__(self, location=None, radius=None, extensions=None,
                 batch=None, **kwargs):
        """ Amap re geo code basic request param, amap document see:
        [re_geocode](http://lbs.amap.com/api/webservice/guide/api/georegeo)

        re_geo extensions optional params:
            poi_type --> str(amap origin split 'a|b') or list ['a', 'b']
            road_level --> int / `RoadLevel` Enum
            home_or_corp --> int / `HomeOrCorpControl` Enum

        Note: if `private_key` set, amap_sig will auto add in request params,
        make sure that your key enable this function in amap control panel.

        Note2: class::`Extensions` must set True to enable extensions params.

        :param location: pairs of lng,lat
        :type location: `str` like: "lng,lat", `tuple` like: (lng, lat), or
        `list` like [(lng,lat), (lng, lat), ...]
        :param radius: re_geo search radius
        :param extensions: extensions controller and options
        :type extensions: Extensions
        :param batch: batch option control
        :param kwargs: args include: key(r), sig, private_key, callback
        """
        self.location = location
        self.radius = radius
        self.batch = batch
        self.extensions = extensions or Extensions()
        super(ReGeoCodeRequestParams, self).__init__(**kwargs)

    def prepare_data(self):
        _p = PreparedReGeoCodeRequestParams()
        with self.prepare_basic(_p) as p:
            if self.extensions.status == ExtensionFlag.BASE:
                p.prepare(
                    location=self.location,
                    radius=self.radius,
                    batch=self.batch,
                    extensions=self.extensions.status,
                )
            else:
                p.prepare(
                    location=self.location,
                    radius=self.radius,
                    batch=self.batch,
                    extensions=self.extensions.status,
                    poi_type=(self.extensions.poi_type
                              or self.extensions.poitype),
                    road_level=(self.extensions.road_level
                                or self.extensions.roadlevel),
                    home_or_corp=(self.extensions.home_or_corp
                                  or self.extensions.homeorcorp),
                )
        return _p


class PreparedReGeoCodeRequestParams(BasePreparedRequestParams):
    def __init__(self):
        super(PreparedReGeoCodeRequestParams, self).__init__()
        self.location = None
        self.radius = None
        self.batch = None
        self.extensions = None
        self.poi_type = None
        self.road_level = None
        self.home_or_corp = None

    def prepare(self, location=None, radius=None, batch=None, extensions=None,
                poi_type=None, road_level=None, home_or_corp=None, **kwargs):
        self.prepare_location(location)
        self.prepare_radius(radius)
        self.prepare_batch(batch)
        self.prepare_extensions(extensions)
        self.prepare_base(**kwargs)

        self.prepare_poi_type(poi_type)
        self.prepare_road_level(road_level)
        self.prepare_home_or_corp(home_or_corp)

    def prepare_location(self, location):
        if location is not None:
            self.location = prepare_multi_locations(location)

    def prepare_radius(self, radius):
        # TODO: Add exc_mode to raise this exception
        # if radius is not None and (radius < 0 or radius > 3000):
        #     raise amap_params_exception(
        #         msg='re_geo radius range must in 0~3000m')
        self.radius = radius

    def prepare_batch(self, batch):
        if batch is None:
            return

        if isinstance(batch, BatchFlag):
            self.batch = batch
        else:
            self.batch = BatchFlag.ON if batch else BatchFlag.OFF

    def prepare_extensions(self, extensions):
        self.extensions = extensions

    def prepare_poi_type(self, poi_type):
        if poi_type is not None:
            self.poi_type = prepare_multi_pois(poi_type)

    def prepare_road_level(self, road_level):
        if road_level is None:
            return

        if isinstance(road_level, RoadLevel):
            self.road_level = road_level
        else:
            self.road_level = RoadLevel.DIRECT if road_level else RoadLevel.ALL

    def prepare_home_or_corp(self, home_or_corp):
        if home_or_corp is None:
            return

        if isinstance(home_or_corp, HomeOrCorpControl):
            self.home_or_corp = home_or_corp
        else:
            self.home_or_corp = HomeOrCorpControl.choose(home_or_corp)

    @property
    def prepared_location(self):
        if self.location is not None:
            return merge_multi_poi(
                (merge_location(*loc) for loc in self.location))

    @property
    def prepared_radius(self):
        return self.radius

    @property
    def prepared_batch(self):
        if self.batch is not None:
            return self.batch.param

    @property
    def prepared_extensions(self):
        if self.extensions is not None:
            return self.extensions.param

    @property
    def prepared_poi_type(self):
        if self.extensions == ExtensionFlag.ALL and self.poi_type is not None:
            return merge_poi_type(self.poi_type)

    @property
    def prepared_road_level(self):
        if self.road_level is not None and self.extensions:
            return self.road_level.param

    @property
    def prepared_home_or_corp(self):
        if self.home_or_corp is not None and self.extensions:
            return self.home_or_corp.param

    def generate_params(self):
        _p = {}
        optional_params = {'radius': self.prepared_radius,
                           'batch': self.prepared_batch,
                           'extensions': self.prepared_extensions,
                           'poitype': self.prepared_poi_type,
                           'roadlevel': self.prepared_road_level,
                           'homeorcorp': self.prepared_home_or_corp}

        with self.init_basic_params(_p, optionals=optional_params) as params:
            params['location'] = self.prepared_location

            return params


class ReGeoCodeResponseData(BaseResponseData):
    _ROUTE_SINGLE = 'regeocode'
    _ROUTE_MULTI = 'regeocodes'

    def get_data(self, raw_data, static=False):
        if self._ROUTE_SINGLE in raw_data:
            return self._get_single_data(raw_data, static)
        elif self._ROUTE_MULTI in raw_data:
            return self._get_multi_data(raw_data, static)

    def _get_single_data(self, raw_data, static):
        data = raw_data.get(self._ROUTE_SINGLE)
        return [ReGeoCodeData(data, static)] if data else []

    def _get_multi_data(self, raw_data, static):
        data = raw_data.get(self._ROUTE_MULTI)
        return [ReGeoCodeData(d, static) for d in data] if data else []


class ReGeoCodeData(BaseData):
    _properties = ("formatted_address",
                   "address_component",
                   "pois",
                   "roads",
                   "roadinters",
                   "aois")

    def decode_param(self, p, data):
        if p == 'address_component':
            return self.decode_address_component(data)
        elif p == 'pois':
            return self.decode_pois(data)
        elif p == 'roads':
            return self.decode_roads(data)
        elif p == 'roadinters':
            return self.decode_road_inters(data)
        elif p == 'aois':
            return self.decode_aois(data)

    def decode_address_component(self, data):
        address_component_data = data.get('address_component')
        return ReGeoAddressComponent(address_component_data, self._static)

    def decode_pois(self, data):
        return self._decode_to_list(data, 'pois', ReGeoPoi,
                                    static=self._static)

    def decode_roads(self, data):
        return self._decode_to_list(data, 'roads', ReGeoRoad,
                                    static=self._static)

    def decode_road_inters(self, data):
        return self._decode_to_list(data, 'roadinters', ReGeoRoadInter,
                                    static=self._static)

    def decode_aois(self, data):
        return self._decode_to_list(data, 'aois', ReGeoAOI,
                                    static=self._static)

    @staticmethod
    def _decode_to_list(data, route_key, package_class, **kwargs):
        """ decode list params
        >>> data = {'a':[1, 2, 3]}
        >>> route_key = 'a'
        >>> package_class = lambda x: x+1
        >>> ReGeoCodeData._decode_to_list(data, route_key, package_class)
        [2, 3, 4]
        >>> route_key = 'b'
        >>> ReGeoCodeData._decode_to_list(data, route_key, package_class)
        []
        """
        _data = data.get(route_key)
        return [package_class(d, **kwargs) for d in _data] if _data else []


class ReGeoAddressComponent(BaseData):
    _properties = ("province",
                   'city',
                   'citycode',
                   'district',
                   'adcode',
                   'township',
                   'towncode',
                   'neighborhood',
                   'building',
                   'street_number',
                   'sea_area',
                   'business_areas',
                   )

    def decode_param(self, p, data):
        if p == 'building':
            return self.decode_building_data(data)
        elif p == 'neighborhood':
            return self.decode_neighborhood_data(data)
        elif p == 'street_number':
            return self.decode_street_number(data)
        elif p == 'business_areas':
            return self.decode_business_areas(data)

    def decode_building_data(self, data):
        building_data = data.get('building')

        return Building(building_data, self._static)

    def decode_neighborhood_data(self, data):
        neighborhood_data = data.get('neighborhood')

        return Neighborhood(neighborhood_data, self._static)

    def decode_street_number(self, data):
        street_number_data = data.get('street_number')

        return StreetNumber(street_number_data, self._static)

    def decode_business_areas(self, data):
        ba_datas = data.get('business_areas')
        return [BusinessArea(d, self._static)
                for d in ba_datas] if ba_datas else []


class ReGeoPoi(BaseData, LocationMixin):
    _properties = ('id',
                   'name',
                   'type',
                   'tel',
                   'distance',
                   'direction',
                   'address',
                   'location',
                   'businessarea')


class ReGeoRoad(BaseData, LocationMixin):
    _properties = ('id',
                   'name',
                   'distance',
                   'direction',
                   'location')


class ReGeoRoadInter(BaseData, LocationMixin):
    _properties = ('distance',
                   'direction',
                   'location',
                   'first_id',
                   'first_name',
                   'second_id',
                   'second_name',)


class ReGeoAOI(BaseData):
    _properties = ('id',
                   'name',
                   'adcode',
                   'location',
                   'area',)

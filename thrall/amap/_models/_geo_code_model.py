# coding: utf-8
from __future__ import absolute_import

from thrall.amap.consts import BatchFlag
from thrall.base import BaseData
from thrall.compat import unicode
from thrall.utils import check_params_type, required_params

from ..common import merge_multi_address, prepare_multi_address
from ._base_model import (
    BasePreparedRequestParams,
    BaseRequestParams,
    BaseResponseData,
    LocationMixin
)
from ._common_model import Building, Neighborhood


class GeoCodeRequestParams(BaseRequestParams):

    @required_params('address')
    def __init__(self, address=None, city=None, batch=None, **kwargs):
        """ Amap geo code basic request param, amap document please see:
        [geocode](https://lbs.amap.com/api/webservice/guide/api/georegeo)

        Note: if `private_key` set, amap_sig will auto add in request params,
        make sure that your key enable this function in amap control panel.

        :param address: address param, need to be structured addresses like:
        `county + province + city + district + ...`
        :param city: city param, can be city_code(int), city_adcode(int),
        city_name(str) or city_alphabetic(str)
        :param batch: batch option control
        :param kwargs: args include: key(r), sig, private_key, callback
        """
        self.address = address
        self.city = city
        self.batch = batch
        super(GeoCodeRequestParams, self).__init__(**kwargs)

    def prepare_data(self):
        _p = PreparedGeoCodeRequestParams()
        with self.prepare_basic(_p) as p:
            p.prepare(
                address=self.address,
                city=self.city,
                batch=self.batch,
            )
        return _p


class PreparedGeoCodeRequestParams(BasePreparedRequestParams):
    def __init__(self):
        super(PreparedGeoCodeRequestParams, self).__init__()
        self.address = None
        self.city = None
        self.batch = None

    @property
    def prepared_address(self):
        if self.address is not None:
            return merge_multi_address(self.address)

    @property
    def prepared_city(self):
        if self.city is not None:
            return unicode(self.city)

    @property
    def prepared_batch(self):
        if self.batch == BatchFlag.ON:
            return True
        elif self.batch == BatchFlag.OFF:
            return False

    @check_params_type(
        address=(str, unicode, list, tuple),
        city=(str, unicode, int),
        batch=(bool, BatchFlag),
    )
    def prepare(self, address=None, city=None, batch=None, **kwargs):
        """ prepare geo code data to amap request params

        :param address: required param: geo code address.
        :param city: optional param: geo code city, this option can improve
         geo code accuracy.
        :param batch: optional param: control amap batch results.
        :param kwargs: args include key(r), pkey, output, callback.
        """
        self.prepare_address(address)
        self.prepare_city(city)
        self.prepare_batch(batch)
        self.prepare_base(**kwargs)

    def prepare_address(self, address):
        self.address = prepare_multi_address(address)

    def prepare_city(self, city):
        self.city = city

    def prepare_batch(self, batch):
        if isinstance(batch, bool):
            self.batch = BatchFlag.ON if batch else BatchFlag.OFF
        elif isinstance(batch, BatchFlag):
            self.batch = batch

    def generate_params(self):
        optional_params = {'city': self.prepared_city,
                           'batch': self.prepared_batch}

        with self.init_basic_params({}, optionals=optional_params) as params:
            params['address'] = self.prepared_address
            return params


class GeoCodeResponseData(BaseResponseData):
    _ROUTE = 'geocodes'

    def get_data(self, raw_data, static=False):
        geo_data = raw_data.get(self._ROUTE)
        return [GeoCodeData(d, static) for d in geo_data] if geo_data else []


class GeoCodeData(BaseData, LocationMixin):
    _properties = ("formatted_address",
                   "province",
                   "city",
                   "citycode",
                   "district",
                   "township",
                   "neighborhood",  # neighborhood params
                   "building",  # inside building params
                   "adcode",
                   "street",
                   "number",
                   "location",
                   "level",)

    def decode_param(self, p, data):
        if p == 'building':
            return self.decode_building_data(data)
        elif p == 'neighborhood':
            return self.decode_neighborhood_data(data)

    def decode_building_data(self, data):
        building_data = data.get('building')

        return Building(building_data, self._static)

    def decode_neighborhood_data(self, data):
        neighborhood_data = data.get('neighborhood')

        return Neighborhood(neighborhood_data, self._static)

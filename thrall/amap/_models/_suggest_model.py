# coding: utf-8
from __future__ import absolute_import

from thrall.base import BaseData
from thrall.compat import basestring, unicode
from thrall.utils import required_params
from thrall.consts import RouteKey

from ..common import (
    merge_location,
    merge_multi_address,
    merge_multi_poi,
    parse_multi_address,
    prepare_multi_locations,
    prepare_multi_pois
)
from ..consts import CityLimitFlag, DataType
from ._base_model import (
    BasePreparedRequestParams,
    BaseRequestParams,
    BaseResponseData,
    LocationMixin
)


class SuggestRequestParams(BaseRequestParams):
    ROUTE_KEY = RouteKey.SUGGEST

    @required_params('keyword')
    def __init__(self, keyword=None, types=None, location=None,
                 city=None, city_limit=None, data_type=None,
                 **kwargs):
        self.keyword = keyword
        self.types = types
        self.location = location
        self.city = city
        self.city_limit = city_limit
        self.data_type = data_type
        super(SuggestRequestParams, self).__init__(**kwargs)

    def prepare_data(self):
        _p = PreparedSuggestRequestParams()

        with self.prepare_basic(_p) as p:
            p.prepare(
                keyword=self.keyword,
                types=self.types,
                location=self.location,
                city=self.city,
                city_limit=self.city_limit,
                data_type=self.data_type
            )

        return p


class PreparedSuggestRequestParams(BasePreparedRequestParams):
    ROUTE_KEY = RouteKey.SUGGEST

    def __init__(self):
        super(PreparedSuggestRequestParams, self).__init__()
        self.keyword = None
        self.types = None
        self.location = None
        self.city = None
        self.city_limit = None
        self.data_type = None

    def prepare(self, keyword=None, types=None, location=None,
                city=None, city_limit=None, data_type=None, **kwargs):
        self.prepare_keyword(keyword)
        self.prepare_types(types)
        self.prepare_location(location)
        self.prepare_city(city)
        self.prepare_city_limit(city_limit)
        self.prepare_data_type(data_type)
        self.prepare_base(**kwargs)

    def prepare_keyword(self, keyword):
        if keyword is not None:
            self.keyword = unicode(keyword)

    def prepare_types(self, types):
        if types is not None:
            self.types = prepare_multi_pois(types)

    def prepare_location(self, location):
        if location is not None:
            rls = prepare_multi_locations(location)

            if rls:
                self.location = rls[0]

    def prepare_city(self, city):
        if city is not None:
            self.city = unicode(city)

    def prepare_city_limit(self, city_limit):
        if city_limit is None:
            return

        if isinstance(city_limit, CityLimitFlag):
            self.city_limit = city_limit
        else:
            self.city_limit = CityLimitFlag.choose(city_limit)

    @staticmethod
    def prepare_multi_data_types(data_types):
        """ prepare multi data types

        >>> P = PreparedSuggestRequestParams
        >>> P.prepare_multi_data_types(None) is None
        True
        >>> P.prepare_multi_data_types("all") == [DataType.ALL]
        True
        >>> P.prepare_multi_data_types('all|bus') \
        == [DataType.ALL, DataType.BUS]
        True
        >>> P.prepare_multi_data_types('a') is None
        True
        >>> P.prepare_multi_data_types('a|b') is None
        True
        >>> P.prepare_multi_data_types('alL|xxx') == [DataType.ALL]
        True
        >>> P.prepare_multi_data_types(['all']) == [DataType.ALL]
        True
        >>> P.prepare_multi_data_types(['all', 'bus']) \
        == [DataType.ALL, DataType.BUS]
        True
        >>> P.prepare_multi_data_types(['all', 'xxx']) \
        == [DataType.ALL]
        True
        >>> P.prepare_multi_data_types(['all', DataType.BUSLINE, 'xxx']) \
        == [DataType.ALL, DataType.BUSLINE]
        True
        >>> P.prepare_multi_data_types([DataType.BUSLINE, 'all', 'buslIne']) \
        == [DataType.BUSLINE, DataType.ALL]
        True

        :param data_types: multi data types
        :return: [DataTypes.ALL, ...]
        """
        if not data_types:
            return

        _tmp = []
        if isinstance(data_types, DataType):
            _tmp = [data_types]
        elif isinstance(data_types, basestring):
            x = parse_multi_address(data_types)
            for i in x:
                data_type = DataType.choose(i)
                if data_type:
                    _tmp.append(data_type)
        elif isinstance(data_types, (list, tuple)):
            for num, item in enumerate(data_types):
                if isinstance(item, basestring):
                    _types = parse_multi_address(item)
                    for j in _types:
                        data_type = DataType.choose(j)
                        if data_type:
                            _tmp.append(data_type)
                elif isinstance(item, DataType):
                    _tmp.append(item)

        if _tmp:
            return sorted(set(_tmp), key=_tmp.index)

    def prepare_data_type(self, data_types):
        if data_types is not None:
            self.data_type = self.prepare_multi_data_types(data_types)

    @property
    def prepared_keyword(self):
        return self.keyword

    @property
    def prepared_types(self):
        if self.types is not None:
            return merge_multi_poi(self.types)

    @property
    def prepared_location(self):
        if self.location is not None:
            return merge_location(*self.location)

    @property
    def prepared_city(self):
        return self.city

    @property
    def prepared_city_limit(self):
        if self.city_limit is not None:
            return self.city_limit.param

    @property
    def prepared_data_type(self):
        if self.data_type is not None:
            return merge_multi_address([i.param for i in self.data_type])

    def generate_params(self):
        _p = {}
        optional_params = {
            'type': self.prepared_types,
            'location': self.prepared_location,
            'city': self.prepared_city,
            'citylimit': self.prepared_city_limit,
            'datatype': self.prepared_data_type
        }

        with self.init_basic_params(_p, optionals=optional_params) as params:
            params['keywords'] = self.prepared_keyword
            return params


class SuggestResponseData(BaseResponseData):
    ROUTE_KEY = RouteKey.SUGGEST

    _ROUTE = 'tips'

    def get_data(self, raw_data, static=False):
        datas = raw_data.get(self._ROUTE)
        return [SuggestData(d, static) for d in datas] if datas else []


class SuggestData(BaseData, LocationMixin):
    _properties = ('id',
                   'name',
                   'district',
                   'adcode',
                   'location',
                   'address',
                   'typecode')

# coding: utf-8
from __future__ import absolute_import

from thrall.base import BaseData
from thrall.compat import unicode
from thrall.utils import required_params
from thrall.consts import RouteKey

from ..common import (
    merge_location,
    merge_multi_address,
    merge_multi_poi,
    prepare_multi_address,
    prepare_multi_locations,
    prepare_multi_pois
)
from ..consts import ChildrenFlag, CityLimitFlag, ExtensionFlag, SortRule
from ._base_model import (
    BasePreparedRequestParams,
    BaseRequestParams,
    BaseResponseData,
    Extensions,
    LocationMixin,
)
from ._common_model import BizExt, IndoorData, Photos, Children


class SearchTextRequestParams(BaseRequestParams):
    ROUTE_KEY = RouteKey.SEARCH_TEXT

    def __init__(self, keywords=None, types=None, city=None, city_limit=None,
                 children=None, offset=None, page=None, building=None,
                 floor=None, sort_rule=None, extensions=None,
                 location=None, **kwargs):
        self.keywords = keywords
        self.location = location
        self.types = types
        self.city = city
        self.city_limit = city_limit
        self.children = children
        self.offset = offset
        self.page = page
        self.building = building
        self.floor = floor
        self.sort_rule = sort_rule
        self.extensions = extensions
        super(SearchTextRequestParams, self).__init__(**kwargs)

    def _no_keywords_and_types(self):
        if self.keywords is None and self.types is None:
            return 1

    def prepare_data(self):

        if self._no_keywords_and_types():
            # TODO: add raise mode to raise this exc
            #     raise amap_params_exception(
            #         'keywords and types must be required one at least.')
            pass

        _p = PreparedSearchTextRequestParams()

        with self.prepare_basic(_p) as p:
            p.prepare(
                keywords=self.keywords,
                location=self.location,
                types=self.types,
                city=self.city,
                city_limit=self.city_limit,
                children=self.children,
                offset=self.offset,
                page=self.page,
                building=self.building,
                floor=self.floor,
                sort_rule=self.sort_rule,
                extensions=self.extensions.status if isinstance(
                    self.extensions, Extensions) else self.extensions,
            )

        return p


class SearchAroundRequestParams(BaseRequestParams):
    ROUTE_KEY = RouteKey.SEARCH_AROUND

    @required_params('location')
    def __init__(self, location=None, keywords=None, types=None, city=None,
                 radius=None, sort_rule=None, offset=None, page=None,
                 extensions=None, **kwargs):
        self.location = location
        self.keywords = keywords
        self.types = types
        self.city = city
        self.radius = radius
        self.sort_rule = sort_rule
        self.offset = offset
        self.page = page
        self.extensions = extensions
        super(SearchAroundRequestParams, self).__init__(**kwargs)

    def prepare_data(self):
        _p = PreparedSearchAroundRequestParams()

        with self.prepare_basic(_p) as p:
            p.prepare(
                location=self.location,
                keywords=self.keywords,
                types=self.types,
                city=self.city,
                radius=self.radius,
                sort_rule=self.sort_rule,
                offset=self.offset,
                page=self.page,
                extensions=self.extensions.status if isinstance(
                    self.extensions, Extensions) else self.extensions,
            )

        return p


class PreparedSearchMixin(object):
    def __init__(self):
        self.keywords = None
        self.location = None
        self.types = None
        self.offset = None
        self.page = None
        self.sort_rule = None
        self.extensions = None

    def prepare_keywords(self, keywords):
        if keywords is not None:
            self.keywords = prepare_multi_address(keywords)

    def prepare_location(self, location):
        if location is not None:
            r = prepare_multi_locations(location)

            if r:
                self.location = r[0]

    def prepare_types(self, types):
        if types is not None:
            self.types = prepare_multi_pois(types)

    def prepare_offset(self, offset):
        # TODO: add raise mode to raise this exc
        # if offset is not None and (offset > 25 or offset < 0):
        #     raise amap_params_exception('offset must in range 0 - 25.')
        self.offset = offset

    def prepare_page(self, page):
        # TODO: add raise mode to raise this exc
        # if page is not None and (page > 100 or page < 0):
        #     raise amap_params_exception('page must in range 0 - 100.')
        self.page = page

    def prepare_sort_rule(self, sort_rule):
        if sort_rule is None:
            return

        if isinstance(sort_rule, SortRule):
            self.sort_rule = sort_rule
        else:
            self.sort_rule = SortRule.choose(sort_rule)

    def prepare_extension(self, extension):
        if isinstance(extension, bool):
            self.extensions = ExtensionFlag.choose(extension)
        elif isinstance(extension, ExtensionFlag):
            self.extensions = extension

    @property
    def prepared_keywords(self):
        if self.keywords is not None:
            return merge_multi_address(self.keywords)

    @property
    def prepared_location(self):
        if self.location is not None:
            return merge_location(*self.location)

    @property
    def prepared_types(self):
        if self.types is not None:
            return merge_multi_poi(self.types)

    @property
    def prepared_page(self):
        return self.page

    @property
    def prepared_offset(self):
        return self.offset

    @property
    def prepared_sort_rule(self):
        if self.sort_rule is not None:
            return self.sort_rule.param

    @property
    def prepared_extension(self):
        if self.extensions is not None:
            return self.extensions.param


class PreparedSearchTextRequestParams(BasePreparedRequestParams,
                                      PreparedSearchMixin):
    ROUTE_KEY = RouteKey.SEARCH_TEXT

    def __init__(self):
        super(PreparedSearchTextRequestParams, self).__init__()
        self.keywords = None
        self.location = None
        self.types = None
        self.city = None
        self.city_limit = None
        self.children = None
        self.offset = None
        self.page = None
        self.building = None
        self.floor = None
        self.sort_rule = None
        self.extensions = None

    def prepare(self, keywords=None, types=None, city=None, city_limit=None,
                children=None, offset=None, page=None, building=None,
                floor=None, sort_rule=None, extensions=None,
                location=None, **kwargs):
        self.prepare_keywords(keywords)
        self.prepare_location(location)
        self.prepare_types(types)
        self.prepare_city(city)
        self.prepare_city_limit(city_limit)
        self.prepare_children(children)
        self.prepare_offset(offset)
        self.prepare_page(page)
        self.prepare_building(building)
        self.prepare_floor(floor)
        self.prepare_extension(extensions)
        self.prepare_sort_rule(sort_rule)
        self.prepare_base(**kwargs)

    def prepare_city(self, city):
        if city is not None:
            self.city = unicode(city)

    def prepare_city_limit(self, city_limit):
        if city_limit is None:
            return

        if isinstance(city_limit, CityLimitFlag):
            self.city_limit = city_limit
        else:
            self.city_limit = (
                CityLimitFlag.ON if city_limit else CityLimitFlag.OFF)

    def prepare_children(self, children):
        if children is None:
            return

        if isinstance(children, ChildrenFlag):
            self.children = children
        else:
            self.children = ChildrenFlag.ON if children else ChildrenFlag.OFF

    def prepare_building(self, building):
        self.building = building

    def prepare_floor(self, floor):
        self.floor = floor

    @property
    def prepared_city(self):
        return self.city

    @property
    def prepared_city_limit(self):
        if self.city_limit is not None:
            return self.city_limit.param

    @property
    def prepared_children(self):
        if self.children is not None:
            return self.children.param

    @property
    def prepared_building(self):
        return self.building

    @property
    def prepared_floor(self):
        return self.floor

    def generate_params(self):
        _p = {}
        optional_params = {
            'keywords': self.prepared_keywords,
            'location': self.prepared_location,
            'types': self.prepared_types,
            'city': self.prepared_city,
            'citylimit': self.prepared_city_limit,
            'children': self.prepared_children,
            'offset': self.prepared_offset,
            'page': self.prepared_page,
            'building': self.prepared_building,
            'floor': self.prepared_floor,
            'sortrule': self.prepared_sort_rule,
            'extensions': self.prepared_extension,
        }
        with self.init_basic_params(_p, optionals=optional_params) as params:
            return params


class PreparedSearchAroundRequestParams(BasePreparedRequestParams,
                                        PreparedSearchMixin):
    ROUTE_KEY = RouteKey.SEARCH_AROUND

    def __init__(self):
        super(PreparedSearchAroundRequestParams, self).__init__()
        self.location = None
        self.keywords = None
        self.types = None
        self.city = None
        self.radius = None
        self.sort_rule = None
        self.offset = None
        self.page = None
        self.extensions = None

    def prepare(self, location=None, keywords=None, types=None, city=None,
                radius=None, sort_rule=None, offset=None, page=None,
                extensions=None, **kwargs):
        self.prepare_location(location)
        self.prepare_keywords(keywords)
        self.prepare_types(types)
        self.prepare_city(city)
        self.prepare_radius(radius)
        self.prepare_sort_rule(sort_rule)
        self.prepare_offset(offset)
        self.prepare_page(page)
        self.prepare_extension(extensions)
        self.prepare_base(**kwargs)

    def prepare_city(self, city):
        if city is not None:
            self.city = unicode(city)

    def prepare_radius(self, radius):
        # TODO: add raise mode to raise this exc
        # if radius is not None and (radius < 0 or radius > 50000):
        #     raise amap_params_exception(
        #         msg='re_geo radius range must in 0~50000m')

        self.radius = radius

    @property
    def prepared_city(self):
        return self.city

    @property
    def prepared_radius(self):
        return self.radius

    def generate_params(self):
        _p = {}
        optional_params = {
            'keywords': self.prepared_keywords,
            'types': self.prepared_types,
            'city': self.prepared_city,
            'radius': self.prepared_radius,
            'sortrule': self.prepared_sort_rule,
            'offset': self.prepared_offset,
            'page': self.prepared_page,
            'extensions': self.prepared_extension,
        }

        with self.init_basic_params(_p, optionals=optional_params) as params:
            _p['location'] = self.prepared_location
            return params


class SearchResponseData(BaseResponseData):
    ROUTE_KEY = RouteKey.SEARCH

    _SUGGESTION_ROUTE = 'suggestion'
    _POIS_ROUTE = 'pois'

    def __init__(self, raw_data, *args, **kwargs):
        super(SearchResponseData, self).__init__(raw_data, *args, **kwargs)

        self._suggestions = None
        static = kwargs.get('static_mode')

        if static:
            self._suggestions = self.get_suggestions(self._raw_data)

    @property
    def suggestions(self):
        return self._suggestions or self.get_suggestions(self._raw_data)

    def get_suggestions(self, data):
        return SearchSuggestion(data.get(self._SUGGESTION_ROUTE))

    def get_data(self, data, static=False):
        datas = data.get(self._POIS_ROUTE)
        return [SearchData(d, static) for d in datas] if datas else []


class SearchSuggestion(BaseData):
    _properties = ('keywords', 'cities')

    def decode_param(self, p, data):
        if p == 'cities':
            return self.decode_city_params(data)

    def decode_city_params(self, data):
        datas = data.get('cities')
        return [SearchSuggestionCity(d, self._static)
                for d in datas] if datas else []


class SearchSuggestionCity(BaseData):
    _properties = ('name', 'num', 'citycode', 'adcode')


class SearchData(BaseData, LocationMixin):
    _properties = ('id', 'tag', 'name', 'type', 'typecode', 'biz_type',
                   'address', 'location', 'distance', 'tel', 'postcode',
                   'website', 'email', 'pcode', 'pname', 'citycode',
                   'cityname', 'adcode', 'adname', 'entr_location',
                   'exit_location', 'navi_poiid', 'gridcode', 'alias',
                   'business_area', 'parking_type', 'indoor_map',
                   'indoor_data', 'business_area', 'biz_ext', 'photos',
                   'children')

    def decode_param(self, p, data):
        if p == 'indoor_data':
            return self.decode_indoor_data(data)
        elif p == 'biz_ext':
            return self.decode_biz_ext(data)
        elif p == 'photos':
            return self.decode_photos(data)
        elif p == 'children':
            return self.decode_children(data)

    def decode_indoor_data(self, data):
        return IndoorData(data.get('indoor_data'), static=self._static)

    def decode_children(self, data):
        datas = data.get('children')
        return [Children(d, self._static) for d in datas] if datas else []

    def decode_biz_ext(self, data):
        return BizExt(data.get('biz_ext'), static=self._static)

    def decode_photos(self, data):
        datas = data.get('photos')
        return [Photos(d, self._static) for d in datas] if datas else []

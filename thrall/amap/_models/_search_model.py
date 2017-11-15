# coding: utf-8
from __future__ import absolute_import

from thrall.utils import check_params_type
from thrall.exceptions import amap_params_exception
from thrall.compat import unicode
from thrall.base import BaseData

from ..consts import (
    ExtensionFlag,
    CityLimitFlag,
    ChildrenFlag,
    EXTENSION_BASE,
    EXTENSION_ALL,
)
from ..common import (
    prepare_multi_address,
    prepare_multi_pois,
    merge_multi_address,
    merge_multi_poi,
)

from ._base_model import (
    BaseRequestParams,
    BasePreparedRequestParams,
    BaseResponseData,
    Extensions,
)
from ._common_model import (
    IndoorData,
    BizExt,
    Photos,
)


class SearchTextRequestParams(BaseRequestParams):
    def __init__(self, keywords=None, types=None, city=None, city_limit=None,
                 children=None, offset=None, page=None, building=None,
                 floor=None, extensions=None, **kwargs):
        self.keywords = keywords
        self.types = types
        self.city = city
        self.city_limit = city_limit
        self.children = children
        self.offset = offset
        self.page = page
        self.building = building
        self.floor = floor
        self.extensions = extensions
        super(SearchTextRequestParams, self).__init__(**kwargs)

    def _no_keywords_and_types(self):
        if self.keywords is None and self.types is None:
            return 1

    def prepare_data(self):
        if self._no_keywords_and_types():
            raise amap_params_exception(
                'keywords and types must be required one at least.')

        _p = PreparedSearchTextRequestParams()

        with self.prepare_basic(_p) as p:
            p.prepare(
                keywords=self.keywords,
                types=self.types,
                city=self.city,
                city_limit=self.city_limit,
                children=self.children,
                offset=self.offset,
                page=self.page,
                building=self.building,
                floor=self.floor,
                extensions=self.extensions.status if isinstance(
                    self.extensions, Extensions) else self.extensions,
            )

        return p


class PreparedSearchTextRequestParams(BasePreparedRequestParams):
    def __init__(self):
        super(PreparedSearchTextRequestParams, self).__init__()
        self.keywords = None
        self.types = None
        self.city = None
        self.city_limit = None
        self.children = None
        self.offset = None
        self.page = None
        self.building = None
        self.floor = None
        self.extensions = None

    @check_params_type(
        keywords=(str, unicode, list, tuple),
        types=(str, unicode, list, tuple),
        city=(str, unicode, int),
        city_limit=(bool, CityLimitFlag),
        children=(bool, int, ChildrenFlag),
        offset=(int,),
        page=(int,),
        building=(str, unicode),
        floor=(str, unicode),
        extensions=(bool, ExtensionFlag),
    )
    def prepare(self, keywords=None, types=None, city=None, city_limit=None,
                children=None, offset=None, page=None, building=None,
                floor=None, extensions=None, **kwargs):
        self.prepare_keywords(keywords)
        self.prepare_types(types)
        self.prepare_city(city)
        self.prepare_city_limit(city_limit)
        self.prepare_children(children)
        self.prepare_offset(offset)
        self.prepare_page(page)
        self.prepare_building(building)
        self.prepare_floor(floor)
        self.prepare_extension(extensions)
        self.prepare_base(**kwargs)

    def prepare_keywords(self, keywords):
        self.keywords = prepare_multi_address(keywords)

    def prepare_types(self, types):
        self.types = prepare_multi_pois(types)

    def prepare_city(self, city):
        if city is not None:
            self.city = unicode(city)

    def prepare_city_limit(self, city_limit):
        if isinstance(city_limit, bool):
            self.city_limit = (CityLimitFlag.ON if city_limit
                               else CityLimitFlag.OFF)
        elif isinstance(city_limit, CityLimitFlag):
            self.city_limit = city_limit

    def prepare_children(self, children):
        if isinstance(children, (int, bool)):
            self.children = ChildrenFlag.ON if children else ChildrenFlag.OFF
        elif isinstance(children, ChildrenFlag):
            self.children = children

    def prepare_offset(self, offset):
        if offset is not None and (offset > 25 or offset < 0):
            raise amap_params_exception('offset must in range 0 - 25.')
        self.offset = offset

    def prepare_page(self, page):
        if page is not None and (page > 100 or page < 0):
            raise amap_params_exception('page must in range 0 - 100.')
        self.page = page

    def prepare_building(self, building):
        self.building = building

    def prepare_floor(self, floor):
        self.floor = floor

    def prepare_extension(self, extension):
        if isinstance(extension, bool):
            self.extensions = (ExtensionFlag.ALL if extension
                               else ExtensionFlag.BASE)
        elif isinstance(extension, ExtensionFlag):
            self.extensions = extension

    @property
    def prepared_keywords(self):
        if self.keywords is not None:
            return merge_multi_address(self.keywords)

    @property
    def prepared_types(self):
        if self.types is not None:
            return merge_multi_poi(self.types)

    @property
    def prepared_city(self):
        return self.city

    @property
    def prepared_city_limit(self):
        if self.city_limit == CityLimitFlag.ON:
            return 'true'
        elif self.city_limit == CityLimitFlag.OFF:
            return 'false'

    @property
    def prepared_children(self):
        if self.children == ChildrenFlag.ON:
            return 1
        elif self.children == ChildrenFlag.OFF:
            return 0

    @property
    def prepared_page(self):
        return self.page

    @property
    def prepared_offset(self):
        return self.offset

    @property
    def prepared_building(self):
        return self.building

    @property
    def prepared_floor(self):
        return self.floor

    @property
    def prepared_extension(self):
        if self.extensions == ExtensionFlag.ALL:
            return EXTENSION_ALL
        elif self.extensions == ExtensionFlag.BASE:
            return EXTENSION_BASE

    def generate_params(self):
        _p = {}
        optional_params = {
            'keywords': self.prepared_keywords,
            'types': self.prepared_types,
            'city': self.prepared_city,
            'citylimit': self.prepared_city_limit,
            'children': self.prepared_children,
            'offset': self.prepared_offset,
            'page': self.prepared_page,
            'building': self.prepared_building,
            'floor': self.prepared_floor,
            'extensions': self.prepared_extension,
        }
        with self.init_basic_params(_p, optionals=optional_params) as params:
            return params


class SearchResponseData(BaseResponseData):
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


class SearchData(BaseData):
    _properties = ('id', 'tag', 'name', 'type', 'typecode', 'biz_type',
                   'address', 'location', 'distance', 'tel', 'postcode',
                   'website', 'email', 'pcode', 'pname', 'citycode',
                   'cityname', 'adcode', 'adname', 'entr_location',
                   'exit_location', 'navi_poiid', 'gridcode', 'alias',
                   'business_area', 'parking_type', 'indoor_map',
                   'indoor_data', 'business_area', 'biz_ext', 'photos')

    def decode_param(self, p, data):
        if p == 'indoor_data':
            return self.decode_indoor_data(data)
        elif p == 'biz_ext':
            return self.decode_biz_ext(data)
        elif p == 'photos':
            return self.decode_photos(data)

    def decode_indoor_data(self, data):
        return IndoorData(data.get('indoor_data'), static=self._static)

    def decode_biz_ext(self, data):
        return BizExt(data.get('biz_ext'), static=self._static)

    def decode_photos(self, data):
        datas = data.get('photos')
        return [Photos(d, self._static) for d in datas] if datas else []

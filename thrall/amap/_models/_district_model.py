# coding: utf-8
from __future__ import absolute_import

from thrall.compat import unicode, str

from thrall.base import BaseData
from thrall.consts import RouteKey

from ..consts import ExtensionFlag

from ._base_model import (
    BaseRequestParams,
    BasePreparedRequestParams,
    BaseResponseData,
    LocationMixin,
)


class DistrictRequestParams(BaseRequestParams):
    ROUTE_KEY = RouteKey.DISTRICT

    def __init__(self, keyword=None, sub_district=None, page=None, offset=None,
                 extensions=None, filter=None, **kwargs):
        """ Amap district code basic request param, document ses:
        [district](http://lbs.amap.com/api/webservice/guide/api/district)
        """
        self.keyword = keyword
        self.sub_district = sub_district
        self.page = page
        self.offset = offset
        self.filter = filter
        self.extensions = extensions
        super(DistrictRequestParams, self).__init__(**kwargs)

    def prepare_data(self):
        _p = PreparedDistrictRequestParams()

        with self.prepare_basic(_p) as p:
            p.prepare(
                keyword=self.keyword,
                sub_district=self.sub_district,
                page=self.page,
                offset=self.offset,
                filter=self.filter,
                extensions=self.extensions,
            )

        return p


class PreparedDistrictRequestParams(BasePreparedRequestParams):
    ROUTE_KEY = RouteKey.DISTRICT

    def __init__(self):
        super(PreparedDistrictRequestParams, self).__init__()
        self.keyword = None
        self.sub_district = None
        self.page = None
        self.offset = None
        self.filter = None
        self.extensions = None

    def prepare(self, keyword=None, sub_district=None, page=None, offset=None,
                extensions=None, filter=None, **kwargs):
        self.prepare_keyword(keyword)
        self.prepare_sub_district(sub_district)
        self.prepare_page_and_offset(page, offset)
        self.prepare_extensions(extensions)
        self.prepare_filter(filter)
        self.prepare_base(**kwargs)

    def prepare_keyword(self, keyword):
        if keyword is not None:
            self.keyword = unicode(keyword)

    def prepare_sub_district(self, sub_district):
        if sub_district is not None:
            self.sub_district = int(sub_district)

    def prepare_page_and_offset(self, page, offset):
        self.page = page
        self.offset = offset

    def prepare_filter(self, filter_):
        self.filter = filter_

    def prepare_extensions(self, extension):
        if isinstance(extension, bool):
            self.extensions = ExtensionFlag.choose(extension)
        elif isinstance(extension, ExtensionFlag):
            self.extensions = extension

    @property
    def prepared_keyword(self):
        return self.keyword

    @property
    def prepared_sub_district(self):
        return self.sub_district

    @property
    def prepared_page(self):
        return self.page

    @property
    def prepared_offset(self):
        return self.offset

    @property
    def prepared_filter(self):
        return self.filter

    @property
    def prepared_extensions(self):
        if self.extensions is not None:
            return self.extensions.param

    def generate_params(self):
        optional_params = {'keywords': self.prepared_keyword,
                           'subdistrict': self.prepared_sub_district,
                           'page': self.prepared_page,
                           'offset': self.prepared_offset,
                           'extensions': self.prepared_extensions,
                           'filter': self.prepared_filter}

        with self.init_basic_params({}, optionals=optional_params) as params:
            return params


class DistrictResponseData(BaseResponseData):
    ROUTE_KEY = RouteKey.DISTRICT

    _ROUTE = 'districts'

    def get_data(self, raw_data, static=False):
        data = raw_data.get(self._ROUTE)

        return [DistrictData(d, static) for d in data] if data else []


class DistrictData(BaseData, LocationMixin):
    _properties = ('citycode',
                   'adcode',
                   'name',
                   'center',
                   'level',
                   'polyline',
                   'districts')

    LOCATION_KEY = 'center'

    def decode_param(self, p, data):
        if p == 'districts':
            return self.decode_subself(data)

    def decode_subself(self, data):
        sub_districts = data.get('districts')
        return [self.__class__(d, self._static)
                for d in sub_districts] if sub_districts else []

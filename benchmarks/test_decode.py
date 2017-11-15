# coding: utf-8
from __future__ import absolute_import

from thrall.amap.models import (
    GeoCodeResponseData,
    ReGeoCodeResponseData,
)


class TestGeoCodeDecode(object):
    """url: http://restapi.amap.com/v3/geocode/geo?
    address=%E6%96%B9%E6%81%92%E5%9B%BD%E9%99%85%E4%B8%AD%E5%BF%83A%E5%BA%A7
    |%E6%96%B9%E6%81%92%E5%9B%BD%E9%99%85%E4%B8%AD%E5%BF%83
    &city=%E5%8C%97%E4%BA%AC&batch=True"""

    RAW_DATA = """{"status":"1","info":"OK","infocode":"10000","count":"2",
    "geocodes":[{"formatted_address":"北京市朝阳区方恒国际中心|A座",
    "province":"北京市","citycode":"010","city":"北京市",
    "district":"朝阳区","township":[],
    "neighborhood":{"name":[],"type":[]},
    "building":{"name":[],"type":[]},
    "adcode":"110105","street":[],"number":[],
    "location":"116.480724,39.989584","level":"门牌号"},
    {"formatted_address":"方恒国际中心","province":"北京市",
    "citycode":"010","city":"北京市","district":"朝阳区","township":[],
    "neighborhood":{"name":[],"type":[]},
    "building":{"name":[],"type":[]},"adcode":"110105","street":[],
    "number":[],"location":"116.481232,39.990398","level":"兴趣点"}]}"""

    def test_geo_code(self, benchmark):
        r = GeoCodeResponseData(self.RAW_DATA)

        def get():
            return r.data[0]

        benchmark(get)

    def test_geo_code_origin(self, benchmark):
        r = GeoCodeResponseData(self.RAW_DATA)

        def get():
            return r._raw_data['geocodes'][0]

        benchmark(get)

    def test_geo_code_static(self, benchmark):
        r = GeoCodeResponseData(self.RAW_DATA, static_mode=True)

        def get():
            return r.data[0]

        benchmark(get)


class TestReGeoDecode(object):
    """http://restapi.amap.com/v3/geocode/regeo?location=116.307490,39.984154
    &radius=1000&extensions=base"""

    RAW_DATA = """{"status":"1","info":"OK","infocode":"10000",
    "regeocodes":[
    {"formatted_address":"北京市海淀区海淀街道中国技术交易大厦B座中国技术交易大厦",
    "addressComponent":{"country":"中国","province":"北京市","city":[],
    "citycode":"010","district":"海淀区","adcode":"110108","township":"海淀街道",
    "towncode":"110108012000","neighborhood":{"name":[],"type":[]},
    "building":{"name":"中国技术交易大厦B座","type":"商务住宅;楼宇;商务写字楼"},
    "streetNumber":{"street":"北四环西路","number":"66号",
    "location":"116.30747,39.9843189","direction":"北","distance":"18.427"},
    "businessAreas":[{"location":"116.32013920092481,39.97507461118122",
    "name":"中关村","id":"110108"},
    {"location":"116.30624890692334,39.975150066024774","name":"苏州街",
    "id":"110108"},{"location":"116.31060892521111,39.99231773703259",
    "name":"北京大学","id":"110108"}]}}]}"""

    def test_re_geo_code(self, benchmark):
        r = ReGeoCodeResponseData(self.RAW_DATA)

        def get():
            return r.data[0].address_component.business_areas[0].location

        benchmark(get)

    def test_re_geo_code_origin(self, benchmark):
        r = ReGeoCodeResponseData(self.RAW_DATA)

        def get():
            return r._raw_data['regeocodes'][0][
                'address_component']['business_areas'][0]['location']

        benchmark(get)

    def test_re_geo_code_static(self, benchmark):
        r = ReGeoCodeResponseData(self.RAW_DATA, static_mode=True)

        def get():
            return r.data[0].address_component.business_areas[0].location

        benchmark(get)
# coding: utf-8
from __future__ import absolute_import

from thrall.amap.models import GeoCodeResponseData


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

# coding: utf-8
from __future__ import absolute_import

from thrall.amap.models import (
    GeoCodeResponseData,
    ReGeoCodeResponseData,
    SearchResponseData,
    SuggestResponseData,
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

    def test_geo_code_origin(self, benchmark):
        r = GeoCodeResponseData(self.RAW_DATA)

        def get():
            return r._raw_data['geocodes'][0]

        benchmark(get)

    def test_geo_code_dynamic(self, benchmark):
        r = GeoCodeResponseData(self.RAW_DATA)

        def get():
            return r.data[0]

        benchmark(get)

    def test_geo_code_static(self, benchmark):
        r = GeoCodeResponseData(self.RAW_DATA, static_mode=True)

        def get():
            return r.data[0]

        benchmark(get)


class TestGeoCodeDecodeInit(object):
    RAW_DATA = TestGeoCodeDecode.RAW_DATA

    def test_init(self, benchmark):
        benchmark(GeoCodeResponseData, self.RAW_DATA, static_mode=False)

    def test_static_init(self, benchmark):
        benchmark(GeoCodeResponseData, self.RAW_DATA, static_mode=True)


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

    def test_re_geo_code_origin(self, benchmark):
        r = ReGeoCodeResponseData(self.RAW_DATA)

        def get():
            return r._raw_data['regeocodes'][0][
                'address_component']['business_areas'][0]['location']

        benchmark(get)

    def test_re_geo_code_dynamic(self, benchmark):
        r = ReGeoCodeResponseData(self.RAW_DATA)

        def get():
            return r.data[0].address_component.business_areas[0].location

        benchmark(get)

    def test_re_geo_code_static(self, benchmark):
        r = ReGeoCodeResponseData(self.RAW_DATA, static_mode=True)

        def get():
            return r.data[0].address_component.business_areas[0].location

        benchmark(get)


class TestReGeoDecodeInit(object):
    RAW_DATA = TestReGeoDecode.RAW_DATA

    def test_init(self, benchmark):
        benchmark(ReGeoCodeResponseData, self.RAW_DATA, static_mode=False)

    def test_static_init(self, benchmark):
        benchmark(ReGeoCodeResponseData, self.RAW_DATA, static_mode=True)


class TestSearchDecode(object):
    """http://restapi.amap.com/v3/place/text?
    keywords=%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6&types=&city=&children=1
    &offset=1&page=2&extensions=all&citylimit=True"""

    RAW_DATA = """{"status":"1","count":"271","info":"OK","infocode":"10000",
    "suggestion":{"keywords":[],"cities":[]},"pois":[{"id":"BV10013409",
    "name":"北京大学东门(地铁站)","tag":[],"type":"交通设施服务;地铁站;地铁站",
    "typecode":"150500","biz_type":[],"address":"4号线/大兴线",
    "location":"116.315842,39.992212","tel":[],"postcode":[],"website":[],
    "email":[],"pcode":"110000","pname":"北京市","citycode":"010",
    "cityname":"北京市","adcode":"110108","adname":"海淀区","importance":[],
    "shopid":[],"shopinfo":"2","poiweight":[],"gridcode":"5916729500",
    "distance":[],"navi_poiid":[],"entr_location":[],"business_area":[],
    "exit_location":[],"match":"0","recommend":"3","timestamp":[],"alias":[],
    "indoor_map":"0","indoor_data":{"cpid":[],"floor":[],"truefloor":[],
    "cmsid":[]},"groupbuy_num":"0","discount_num":"0","biz_ext":{"rating":[],
    "cost":[]},"event":[],"children":[],"photos":[{"title":[],
    "url":"http://store.is.autonavi.com/showpic/24abc43bd32dc"},
    {"title":[], "url":"http://store.is.autonavi.com/showpic"}]}]}"""

    def test_search_origin(self, benchmark):
        r = SearchResponseData(self.RAW_DATA)

        def get():
            return r._raw_data['pois'][0]['photos'][0]['url']

        benchmark(get)

    def test_search_dynamic(self, benchmark):
        r = SearchResponseData(self.RAW_DATA)

        def get():
            return r.data[0].photos[0].url

        benchmark(get)

    def test_search_static(self, benchmark):
        r = SearchResponseData(self.RAW_DATA, static_mode=True)

        def get():
            return r.data[0].photos[0].url

        benchmark(get)


class TestSearchDecodeInit(object):
    RAW_DATA = TestSearchDecode.RAW_DATA

    def test_init(self, benchmark):
        benchmark(SearchResponseData, self.RAW_DATA, static_mode=False)

    def test_static_init(self, benchmark):
        benchmark(SearchResponseData, self.RAW_DATA, static_mode=True)


class TestSuggestDecode(object):
    """http://restapi.amap.com/v3/assistant/inputtips?
    keywords=%E8%82%AF%E5%BE%B7%E5%9F%BA&type=050301
    &location=116.481488,39.990464
    &city=%E5%8C%97%E4%BA%AC&datatype=all"""

    RAW_DATA = """{"status":"1","count":"10","info":"OK","infocode":"10000",
    "tips":[{"id":[],"name":"肯德基","district":[],"adcode":[],"location":[],
    "address":[],"typecode":[]},
    {"id":"B000A7BM4H","name":"肯德基(花家地店)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.469271,39.985568",
    "address":"花家地小区1号商业楼","typecode":"050301"},
    {"id":"B000A7C99U","name":"肯德基(酒仙桥店)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.490377,39.975437",
    "address":"酒仙桥路12号新华联丽港乐天玛特1层","typecode":"050301"},
    {"id":"B000A7FVJQ","name":"肯德基(中福百货店)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.463384,40.000466",
    "address":"望京南湖东园201号楼1层","typecode":"050301"},
    {"id":"B000A875MK","name":"肯德基(来广营店)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.464233,40.016454",
    "address":"香宾路66-1号","typecode":"050301"},
    {"id":"B000A80GPM","name":"肯德基(酒仙桥二店)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.495544,39.961983",
    "address":"酒仙桥路39号久隆百货B1层","typecode":"050301"},
    {"id":"B000A9P8KT","name":"肯德基(太阳宫店)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.448512,39.971335",
    "address":"太阳宫中路12号1层01-13A-14-15B","typecode":"050301"},
    {"id":"B000A80HAN","name":"肯德基(霄云路店)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.464882,39.959215",
    "address":"霄云路27号中国庆安大厦1层","typecode":"050301"},
    {"id":"B0FFF3DEDV","name":"肯德基(凤凰汇购物中心)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.456296,39.962578",
    "address":"曙光西里甲5号院24号楼凤凰汇购物中心B1层104号","typecode":"050301"},
    {"id":"B000A8ZIKF","name":"肯德基(西坝河店)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.436102,39.969056",
    "address":"西坝河西里","typecode":"050301"}]}"""

    def test_suggest_origin(self, benchmark):
        r = SuggestResponseData(self.RAW_DATA)

        def get():
            return r._raw_data['tips'][1]['address']

        benchmark(get)

    def test_suggest_dynamic(self, benchmark):
        r = SuggestResponseData(self.RAW_DATA)

        def get():
            return r.data[1].address

        benchmark(get)

    def test_suggest_static(self, benchmark):
        r = SuggestResponseData(self.RAW_DATA, static_mode=True)

        def get():
            return r.data[1].address

        benchmark(get)


class TestSuggestDecodeInit(object):
    RAW_DATA = TestSuggestDecode.RAW_DATA

    def test_init(self, benchmark):
        benchmark(SuggestResponseData, self.RAW_DATA, static_mode=False)

    def test_static_init(self, benchmark):
        benchmark(SuggestResponseData, self.RAW_DATA, static_mode=True)

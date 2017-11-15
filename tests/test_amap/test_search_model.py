# coding: utf-8
from __future__ import absolute_import
from six import iteritems
from thrall.utils import unicode

import pytest

from thrall.amap._models import _search_model

from thrall.exceptions import VendorParamError


class TestSearchTextRequestParams(object):
    def test_init_ok(self):
        model = _search_model.SearchTextRequestParams(key=u'xx')
        assert model.key == 'xx'

    @pytest.mark.parametrize('keywords, types, result', [
        (None, None, 1), (None, 'xxx', None), ('xxx', None, None),
        ('xxx', 'xxx', None),
    ])
    def test_check_keywords_and_types(self, keywords, types, result):
        model = _search_model.SearchTextRequestParams(keywords=keywords,
                                                      types=types,
                                                      key='xxx')

        assert model._no_keywords_and_types() is result

    def test_prepare_data_ok(self):
        model = _search_model.SearchTextRequestParams(key=u'xx',
                                                      keywords=u'xxx|中国')

        p = model.prepare()

        assert isinstance(p, _search_model.PreparedSearchTextRequestParams)

        assert p.keywords == [u'xxx', u'中国']
        assert p.key == 'xx'

    def test_prepare_data_ok_2(self):
        model = _search_model.SearchTextRequestParams(key=u'xx',
                                                      types=u'xxx|中国|001')

        p = model.prepare()

        assert isinstance(p, _search_model.PreparedSearchTextRequestParams)

        assert p.types == [u'xxx', u'中国', u'001']
        assert p.key == 'xx'

    def test_preapre_data_no_keywords_and_types_err(self):
        model = _search_model.SearchTextRequestParams(key=u'xx')

        with pytest.raises(VendorParamError) as err:
            model.prepare()

        assert isinstance(err.value.data,
                          _search_model.SearchTextRequestParams)

        assert 'keywords and types' in str(err.value)


class TestPreparedSearchTextRequestParams(object):
    def test_init_ok(self):
        model = _search_model.PreparedSearchTextRequestParams()

        assert model.key is None

    def test_prepare_ok(self, mocker):
        model = _search_model.PreparedSearchTextRequestParams()

        model.prepare_keywords = lambda x: 'keywords'
        model.prepare_types = lambda x: 'types'
        model.prepare_city = lambda x: 'city'
        model.prepare_city_limit = lambda x: 'city_limit'
        model.prepare_children = lambda x: 'children'
        model.prepare_offset = lambda x: 'offset'
        model.prepare_page = lambda x: 'page'
        model.prepare_building = lambda x: 'building'
        model.prepare_floor = lambda x: 'floor'
        model.prepare_extension = lambda x: 'extensions'

        for i in ['prepare_keywords', 'prepare_types', 'prepare_city',
                  'prepare_city_limit', 'prepare_children', 'prepare_offset',
                  'prepare_page', 'prepare_building', 'prepare_floor',
                  'prepare_extension']:
            mocker.spy(model, i)

        model.prepare('keywords', 'types', 'city', True, True,
                      1, 1, 'building', 'floor', True)

        model.prepare_keywords.assert_called_once_with('keywords')
        model.prepare_types.assert_called_once_with('types')
        model.prepare_city.assert_called_once_with('city')
        model.prepare_city_limit.assert_called_once_with(True)
        model.prepare_children.assert_called_once_with(True)
        model.prepare_offset.assert_called_once_with(1)
        model.prepare_page.assert_called_once_with(1)
        model.prepare_building.assert_called_once_with('building')
        model.prepare_floor.assert_called_once_with('floor')
        model.prepare_extension.assert_called_once_with(True)

    def test_prepare_keywords(self, mocker):
        model = _search_model.PreparedSearchTextRequestParams()

        mocker.spy(_search_model, 'prepare_multi_address')
        mocker.spy(_search_model, 'merge_multi_address')

        model.prepare_keywords(u'aaa|你')

        assert model.keywords == ['aaa', u'你']
        _search_model.prepare_multi_address.assert_called_once_with(u'aaa|你')

        assert model.prepared_keywords == u'aaa|你'
        _search_model.merge_multi_address.assert_called_once_with(
            ['aaa', u'你'])

    def test_prepare_none_keywods(self, mocker):
        model = _search_model.PreparedSearchTextRequestParams()

        mocker.spy(_search_model, 'prepare_multi_address')
        mocker.spy(_search_model, 'merge_multi_address')

        model.prepare_keywords(None)

        assert model.keywords is None
        _search_model.prepare_multi_address.assert_called_once_with(None)

        assert model.prepared_keywords is None
        assert _search_model.merge_multi_address.call_count == 0

    def test_prepare_types(self, mocker):
        model = _search_model.PreparedSearchTextRequestParams()

        mocker.spy(_search_model, 'prepare_multi_pois')
        mocker.spy(_search_model, 'merge_multi_poi')

        model.prepare_types(u'aaa|你')

        assert model.types == ['aaa', u'你']
        _search_model.prepare_multi_pois.assert_called_once_with(u'aaa|你')

        assert model.prepared_types == u'aaa|你'
        _search_model.merge_multi_poi.assert_called_once_with(['aaa', u'你'])

    def test_prepare_none_types(self, mocker):
        model = _search_model.PreparedSearchTextRequestParams()

        mocker.spy(_search_model, 'prepare_multi_pois')
        mocker.spy(_search_model, 'merge_multi_poi')

        model.prepare_types(None)

        assert model.types is None
        _search_model.prepare_multi_pois.assert_called_once_with(None)

        assert model.prepared_keywords is None
        assert _search_model.merge_multi_poi.call_count == 0

    @pytest.mark.parametrize('input, output', [
        ('xxx', u'xxx'), (123, u'123'), (u'上海', u'上海'), (None, None),
        ('', u'')
    ])
    def test_prepare_city(self, input, output):
        model = _search_model.PreparedSearchTextRequestParams()

        model.prepare_city(input)

        if input is None:
            assert model.city is None
            assert model.prepared_city is None
        else:
            assert model.city == model.prepared_city == output
            assert isinstance(model.city, unicode)
            assert isinstance(model.prepared_city, unicode)

    @pytest.mark.parametrize('input, output, p_output', [
        (True, _search_model.CityLimitFlag.ON, 'true'),
        (False, _search_model.CityLimitFlag.OFF, 'false'),
        (_search_model.CityLimitFlag.ON, _search_model.CityLimitFlag.ON,
         'true'),
        (_search_model.CityLimitFlag.OFF, _search_model.CityLimitFlag.OFF,
         'false'),
    ])
    def test_prepare_city_limit(self, input, output, p_output):
        model = _search_model.PreparedSearchTextRequestParams()

        model.prepare_city_limit(input)

        assert model.city_limit == output
        assert model.prepared_city_limit == p_output

    @pytest.mark.parametrize('input, output, p_output', [
        (True, _search_model.ChildrenFlag.ON, 1),
        (False, _search_model.ChildrenFlag.OFF, 0),
        (0, _search_model.ChildrenFlag.OFF, 0),
        (1, _search_model.ChildrenFlag.ON, 1),
        (_search_model.ChildrenFlag.ON, _search_model.ChildrenFlag.ON, 1),
        (_search_model.ChildrenFlag.OFF, _search_model.ChildrenFlag.OFF, 0),
        (None, None, None)
    ])
    def test_prepare_children(self, input, output, p_output):
        model = _search_model.PreparedSearchTextRequestParams()

        model.prepare_children(input)

        assert model.children == output
        assert model.prepared_children == p_output

    @pytest.mark.parametrize('data', [0, 1, 10, 25])
    def test_offset(self, data):
        model = _search_model.PreparedSearchTextRequestParams()

        model.prepare_offset(data)

        assert model.offset == data
        assert model.prepared_offset == data

    @pytest.mark.parametrize('data', [-1, 26, 100, -10])
    def test_offset_out_of_range(self, data):
        model = _search_model.PreparedSearchTextRequestParams()

        with pytest.raises(VendorParamError) as err:
            model.prepare_offset(data)

        assert 'offset must in range 0 - 25.' in str(err.value)
        assert model.prepared_offset is None

    @pytest.mark.parametrize('data', [0, 1, 10, 50, 100])
    def test_page(self, data):
        model = _search_model.PreparedSearchTextRequestParams()

        model.prepare_page(data)

        assert model.page == data
        assert model.prepared_page == data

    @pytest.mark.parametrize('data', [-1, 101, 1000, -10])
    def test_page_out_of_range(self, data):
        model = _search_model.PreparedSearchTextRequestParams()

        with pytest.raises(VendorParamError) as err:
            model.prepare_page(data)

        assert 'page must in range 0 - 100.' in str(err.value)
        assert model.prepared_page is None

    @pytest.mark.parametrize('input, output, p_output', [
        (True, _search_model.ExtensionFlag.ALL, _search_model.EXTENSION_ALL),
        (False, _search_model.ExtensionFlag.BASE,
         _search_model.EXTENSION_BASE),
        (_search_model.ExtensionFlag.BASE, _search_model.ExtensionFlag.BASE,
         _search_model.EXTENSION_BASE),
        (_search_model.ExtensionFlag.ALL, _search_model.ExtensionFlag.ALL,
         _search_model.EXTENSION_ALL),
    ])
    def test_prepare_extensions(self, input, output, p_output):
        model = _search_model.PreparedSearchTextRequestParams()

        model.prepare_extension(input)

        assert model.extensions == output
        assert model.prepared_extension == p_output

    def test_prepare_others(self):
        model = _search_model.PreparedSearchTextRequestParams()

        model.prepare_building('building')
        model.prepare_floor('floor')

        assert model.building == model.prepared_building == 'building'
        assert model.floor == model.prepared_floor == 'floor'

    @pytest.mark.parametrize('input, output', [
        (dict(keywords=u'瓷器', types=[u'饮食', 'www'], city='',
              city_limit=False, children=True, offset=10, page=1,
              building='xxxx', floor='5', extensions=False),
         {'keywords': u'瓷器', 'types': u'饮食|www', 'city': '',
          'citylimit': 'false', 'children': 1, 'offset': 10, 'page': 1,
          'building': 'xxxx', 'floor': '5', 'extensions': 'base'}),
        (dict(keywords=u'瓷器', types=[u'饮食', 'www'], city='',
              city_limit=False, children=True, offset=10, page=1,
              building='xxxx', extensions=None),
         {'keywords': u'瓷器', 'types': u'饮食|www', 'city': '',
          'citylimit': 'false', 'children': 1, 'offset': 10, 'page': 1,
          'building': 'xxxx'}),
        (dict(keywords=None, types=None, city=None,
              city_limit=None, children=None, offset=None, page=None,
              building=None, floor=None, extensions=None, key='xxx'),
         {'key': 'xxx'}),
    ])
    def test_generate_params(self, input, output):
        model = _search_model.PreparedSearchTextRequestParams()
        model.prepare(**input)

        for k, v in iteritems(output):
            assert model.params[k] == v


class TestSearchResponseData(object):
    RAW_DATA = '''
            {
                "status": "1",
                "count": "100",
                "info": "OK",
                "infocode": "10000",
                "suggestion": {
                    "keywords": [],
                    "cities": [
                        {
                            "name": "南阳市",
                            "num": "4678",
                            "citycode": "0377",
                            "adcode": "411300"
                        }
                    ]
                },
                "pois": [{}]
            }'''

    def test_get_suggestion(self, mocker):
        model = _search_model.SearchResponseData(self.RAW_DATA)

        mocker.spy(model, 'get_suggestions')
        data = model.suggestions

        assert isinstance(data, _search_model.SearchSuggestion)
        model.get_suggestions.assert_called_once_with(model._raw_data)

    def test_get_data(self, mocker):
        model = _search_model.SearchResponseData(self.RAW_DATA)

        mocker.spy(model, 'get_data')
        data = model.data

        for i in data:
            assert isinstance(i, _search_model.SearchData)

        model.get_data.assert_called_once_with(model._raw_data)

    def test_static_mode_enabled(self, mocker):
        model = _search_model.SearchResponseData(self.RAW_DATA,
                                                 static_mode=True)

        mocker.spy(model, 'get_suggestions')
        mocker.spy(model, 'get_data')

        _ = model.suggestions
        _ = model.data

        assert model.get_suggestions.call_count == 0
        assert model.get_data.call_count == 0


class TestSearchSuggestion(object):
    def test_init(self):
        model = _search_model.SearchSuggestion({})

        assert model.keywords is None
        assert isinstance(model.cities, list)
        assert not model.cities

    def test_decode_cities(self):
        raw_data = {'cities': [{}, {}, {}]}
        model = _search_model.SearchSuggestion(raw_data)

        assert model.keywords is None
        assert isinstance(model.cities, list)
        assert len(model.cities) == 3

    def test_decode_in_static(self):
        raw_data = {'cities': [{}, {}, {}]}
        model = _search_model.SearchSuggestion(raw_data, static=True)

        assert model.cities is model.cities


class TestSearchData(object):
    def test_init(self):
        model = _search_model.SearchData({})

        for m in model._properties:
            o = getattr(model, m)
            if m == 'photos':
                assert o is not getattr(model, m)
                assert isinstance(o, list)
                assert not o
            elif m == 'indoor_data':
                assert o is not getattr(model, m)
                assert isinstance(o, _search_model.IndoorData)
            elif m == 'biz_ext':
                assert o is not getattr(model, m)
                assert isinstance(o, _search_model.BizExt)
            else:
                assert o is None

    def test_init_in_static(self):
        model = _search_model.SearchData({}, static=True)

        for m in model._properties:
            o = getattr(model, m)
            assert o is getattr(model, m)


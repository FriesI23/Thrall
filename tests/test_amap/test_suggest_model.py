# coding: utf-8
from __future__ import absolute_import
from six import iteritems
from thrall.compat import unicode

import pytest

from thrall.amap._models import _suggest_model


class TestSuggestRequestParams(object):
    def test_init_ok(self):
        model = _suggest_model.SuggestRequestParams(keyword='keyword',
                                                    key='key')
        assert model.keyword == 'keyword'
        assert model.key == 'key'

    def test_prepare_data_ok(self):
        model = _suggest_model.SuggestRequestParams(keyword='keyword',
                                                    key='xxx')

        p = model.prepare()

        assert isinstance(p, _suggest_model.PreparedSuggestRequestParams)


class TestPreparedSuggestRequestParams(object):
    def test_init_ok(self):
        model = _suggest_model.PreparedSuggestRequestParams()

        assert (model.types == model.keyword == model.location == model.city
                == model.city_limit == model.data_type is None)

    def test_prepare(self, mocker):
        model = _suggest_model.PreparedSuggestRequestParams()

        model.prepare_keyword = lambda x: 'keyword'
        model.prepare_types = lambda x: 'types'
        model.prepare_location = lambda x: 'location'
        model.prepare_city = lambda x: 'city'
        model.prepare_city_limit = lambda x: 'city_limit'
        model.prepare_data_type = lambda x: 'data_type'

        mocker.spy(model, 'prepare_keyword')
        mocker.spy(model, 'prepare_types')
        mocker.spy(model, 'prepare_location')
        mocker.spy(model, 'prepare_city')
        mocker.spy(model, 'prepare_city_limit')
        mocker.spy(model, 'prepare_data_type')

        model.prepare(key='xxx', keyword='keyword', types='types',
                      location='location', city='city',
                      city_limit=True, data_type='data_type')

        model.prepare_keyword.assert_called_once_with('keyword')
        model.prepare_types.assert_called_once_with('types')
        model.prepare_location.assert_called_once_with('location')
        model.prepare_city.assert_called_once_with('city')
        model.prepare_city_limit.assert_called_once_with(True)
        model.prepare_data_type.assert_called_once_with('data_type')

    @pytest.mark.parametrize('data, result', [
        ('test', 'test'), (u'中国', u'中国'), (123, u'123'), (None, None)
    ])
    def test_prepare_keyword(self, data, result):
        model = _suggest_model.PreparedSuggestRequestParams()

        model.prepare_keyword(data)

        assert model.keyword == result
        assert model.prepared_keyword == result
        if data:
            assert isinstance(model.prepared_keyword, unicode)

    def test_prepare_types(self, mocker):
        model = _suggest_model.PreparedSuggestRequestParams()

        mocker.spy(_suggest_model, 'prepare_multi_pois')
        model.prepare_types('xxx')

        assert model.types == ['xxx']
        assert model.prepared_types == 'xxx'

        _suggest_model.prepare_multi_pois.assert_called_once_with('xxx')

    @pytest.mark.parametrize('data, result, p_result', [
        ('123,45', (123, 45), '123.000000,45.000000'),
        ('123,45|223,34', (123, 45), '123.000000,45.000000'),
        (['123,45'], (123, 45), '123.000000,45.000000'),
        ([(123, 45)], (123, 45), '123.000000,45.000000'),
    ])
    def test_prepare_location(self, mocker, data, result, p_result):
        model = _suggest_model.PreparedSuggestRequestParams()

        mocker.spy(_suggest_model, 'prepare_multi_locations')
        model.prepare_location(data)

        assert model.location == result
        assert model.prepared_location == p_result

        _suggest_model.prepare_multi_locations.assert_called_once_with(data)

    @pytest.mark.parametrize('data, result', [
        ('xx', 'xx'), (u'上海', u'上海'), (123, u'123'), (None, None),
    ])
    def test_prepare_city(self, data, result):
        model = _suggest_model.PreparedSuggestRequestParams()

        model.prepare_city(data)

        assert model.city == result
        assert model.prepared_city == result
        if data:
            assert isinstance(model.prepared_city, unicode)

    @pytest.mark.parametrize('data, result, p_result', [
        (True, _suggest_model.CityLimitFlag.ON, 'true'),
        (False, _suggest_model.CityLimitFlag.OFF, 'false'),
        (_suggest_model.CityLimitFlag.ON,
         _suggest_model.CityLimitFlag.ON, 'true'),
        (_suggest_model.CityLimitFlag.OFF,
         _suggest_model.CityLimitFlag.OFF, 'false'),
    ])
    def test_prepare_city_limit(self, data, result, p_result):
        model = _suggest_model.PreparedSuggestRequestParams()

        model.prepare_city_limit(data)

        assert model.city_limit == result
        assert model.prepared_city_limit == p_result

    def test_prepare_data_type(self, mocker):
        model = _suggest_model.PreparedSuggestRequestParams()

        mocker.spy(model, 'prepare_multi_data_types')
        model.prepare_data_type('alL')

        assert model.data_type == [_suggest_model.DataType.ALL]
        assert model.prepared_data_type == 'all'

        model.prepare_multi_data_types.assert_called_once_with('alL')

    @pytest.mark.parametrize('input, output', [
        (dict(keyword='xxx', key='key'),
         dict(keywords='xxx', key='key')),
        (dict(keyword='xxx', key='key', data_type=['all', 'poi']),
         dict(keywords='xxx', key='key', datatype='all|poi')),
        (dict(keyword='xxx', key='key', city_limit=True),
         dict(keywords='xxx', key='key', citylimit='true')),
    ])
    def test_generate_params(self, input, output):
        model = _suggest_model.PreparedSuggestRequestParams()
        model.prepare(**input)

        for k, v in iteritems(output):
            assert model.params[k] == v


class TestSuggestResponseData(object):
    RAW_DATA = """{"status":"1","count":"10","info":"OK","infocode":"10000",
    "tips":[{"id":[],"name":"肯德基","district":[],"adcode":[],
    "location":[],"address":[],"typecode":[]},
    {"id":"B000A7BM4H","name":"肯德基(花家地店)","district":"北京市朝阳区",
    "adcode":"110105","location":"116.469271,39.985568",
    "address":"花家地小区1号商业楼","typecode":"050301"}]}"""

    def test_data(self, mocker):
        model = _suggest_model.SuggestResponseData(self.RAW_DATA)

        mocker.spy(model, 'get_data')

        assert isinstance(model.data, list)
        assert isinstance(model.data[0], _suggest_model.SuggestData)

        assert model.get_data.call_count == 2

        for i, j in zip(model.data, model.data):
            assert i is not j

    def test_data_in_static(self, mocker):
        model = _suggest_model.SuggestResponseData(self.RAW_DATA,
                                                   static_mode=True)

        mocker.spy(model, 'get_data')

        assert isinstance(model.data, list)
        assert isinstance(model.data[0], _suggest_model.SuggestData)

        assert model.get_data.call_count == 0

        for i, j in zip(model.data, model.data):
            assert i is j

        assert model.data[1].typecode is not None

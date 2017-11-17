# coding: utf-8
# flake8: noqa

from six import iteritems

import pytest

from thrall.exceptions import VendorParamError
from thrall.amap.consts import (
    BatchFlag, RoadLevel, HomeOrCorpControl, ExtensionFlag,
    EXTENSION_BASE, EXTENSION_ALL)

from thrall.amap._models import _regeo_code_model


class TestReGeoCodeRequestParams(object):
    def test_params_init_ok(self):
        model = _regeo_code_model.ReGeoCodeRequestParams('125,25', key='key')

        assert model.location == '125,25'
        assert model.key == 'key'
        assert isinstance(model.extensions, _regeo_code_model.Extensions)

    def test_params_init_extensions_ok(self):
        model = _regeo_code_model.ReGeoCodeRequestParams(
            '125,25', extensions=_regeo_code_model.Extensions(True),
            key='key')

        assert model.extensions.status == _regeo_code_model.ExtensionFlag.ALL

    def test_prepare(self):
        model = _regeo_code_model.ReGeoCodeRequestParams('125,25', key='key')

        p = model.prepare()

        assert p.location == [(125, 25)]
        assert p.key == 'key'
        assert p.extensions == _regeo_code_model.ExtensionFlag.BASE

    def test_prepare_with_extensions(self):
        model = _regeo_code_model.ReGeoCodeRequestParams(
            '125,25', key='key',
            extensions=_regeo_code_model.Extensions(
                True,
                road_level=_regeo_code_model.RoadLevel.DIRECT,
                poi_type="xxx|yyy",
                home_or_corp=_regeo_code_model.HomeOrCorpControl.HOME))

        p = model.prepare()

        assert p.poi_type == ['xxx', 'yyy']
        assert p.road_level == _regeo_code_model.RoadLevel.DIRECT
        assert p.home_or_corp == _regeo_code_model.HomeOrCorpControl.HOME

    def test_prepare_with_extensions_no_space_name(self):
        model = _regeo_code_model.ReGeoCodeRequestParams(
            '125,25', key='key',
            extensions=_regeo_code_model.Extensions(
                True,
                roadlevel=_regeo_code_model.RoadLevel.DIRECT,
                poitype="xxx|yyy",
                homeorcorp=_regeo_code_model.HomeOrCorpControl.HOME))

        p = model.prepare()

        assert p.poi_type == ['xxx', 'yyy']
        assert p.road_level == _regeo_code_model.RoadLevel.DIRECT
        assert p.home_or_corp == _regeo_code_model.HomeOrCorpControl.HOME


class TestPreparedReGeoCodeRequestParams(object):
    def test_init_ok(self):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()

        assert (model.location == model.radius == model.batch ==
                model.extensions == model.poi_type == model.road_level ==
                model.home_or_corp is None)

    @pytest.mark.parametrize('data, result, p_result', [
        ('125,25', [(125, 25)],
         '125.000000,25.000000'),
        ('125,25|111,22', [(125, 25), (111, 22)],
         '125.000000,25.000000|111.000000,22.000000'),
        ((125, 25), [(125, 25)],
         '125.000000,25.000000'),
        ([(125, 25)], [(125, 25)],
         '125.000000,25.000000'),
        ([(111, 11), (222, 22)], [(111, 11), (222, 22)],
         '111.000000,11.000000|222.000000,22.000000'),
        ([(111, 11), "222,22"], [(111, 11), (222, 22)],
         '111.000000,11.000000|222.000000,22.000000'),
        (["111.0,11|222,22", (333, 33)], [(111, 11), (222, 22), (333, 33)],
         '111.000000,11.000000|222.000000,22.000000|333.000000,33.000000')
    ])
    def test_prepare_location(self, data, result, p_result):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()
        model.prepare_location(data)

        assert model.location == result
        assert model.prepared_location == p_result

    @pytest.mark.parametrize('data', [0, 100, 200, 500, 1000, 3000])
    def test_prepare_radius(self, data):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()
        model.prepare_radius(data)

        assert model.radius == data
        assert model.prepared_radius == data

    # @pytest.mark.parametrize('data', [-1, 4000, 3001])
    # def test_prepare_radius_out_of_range(self, data):
    #     model = _regeo_code_model.PreparedReGeoCodeRequestParams()
    #     with pytest.raises(VendorParamError) as e:
    #         model.prepare_radius(data)
    #
    #     assert 'in 0~3000m' in str(e.value)

    @pytest.mark.parametrize('data, result, p_result', [
        (True, BatchFlag.ON, 'true'),
        (False, BatchFlag.OFF, 'false'),
        (BatchFlag.ON, BatchFlag.ON, 'true'),
        (BatchFlag.OFF, BatchFlag.OFF, 'false'),
    ])
    def test_prepare_batch(self, data, result, p_result):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()

        model.prepare_batch(data)

        assert model.batch == result
        assert model.prepared_batch == p_result

    @pytest.mark.parametrize('data, p_result', [
        (ExtensionFlag.ALL, EXTENSION_ALL),
        (ExtensionFlag.BASE, EXTENSION_BASE)
    ])
    def test_prepare_extensions(self, data, p_result):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()

        model.prepare_extensions(data)

        assert model.extensions == data
        assert model.prepared_extensions == p_result

    @pytest.mark.parametrize('data, result, p_result', [
        ("aaa|bbb", ['aaa', 'bbb'], 'aaa|bbb'),
        (['aaa', 'bbb'], ['aaa', 'bbb'], 'aaa|bbb'),
        (('aaa', 'bbb'), ['aaa', 'bbb'], 'aaa|bbb'),
        (('aaa|ddd', 'ccc'), ['aaa', 'ddd', 'ccc'], 'aaa|ddd|ccc')
    ])
    def test_prepare_poi_type(self, data, result, p_result):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()

        model.prepare_poi_type(data)
        model.extensions = ExtensionFlag.ALL

        assert model.poi_type == result
        assert model.prepared_poi_type == p_result

    @pytest.mark.parametrize('data, result, p_result', [
        (0, RoadLevel.ALL, 0),
        (1, RoadLevel.DIRECT, 1),
        (RoadLevel.ALL, RoadLevel.ALL, 0),
        (RoadLevel.DIRECT, RoadLevel.DIRECT, 1),
    ])
    def test_prepare_road_level(self, data, result, p_result):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()

        model.prepare_road_level(data)
        model.extensions = ExtensionFlag.ALL

        assert model.road_level == result
        assert model.prepared_road_level == p_result

    @pytest.mark.parametrize('data, result, p_result', [
        (0, HomeOrCorpControl.OFF, 0),
        (1, HomeOrCorpControl.HOME, 1),
        (2, HomeOrCorpControl.CORP, 2),
        (HomeOrCorpControl.OFF, HomeOrCorpControl.OFF, 0),
        (HomeOrCorpControl.HOME, HomeOrCorpControl.HOME, 1),
        (HomeOrCorpControl.CORP, HomeOrCorpControl.CORP, 2),
    ])
    def test_preapre_home_or_corp(self, data, result, p_result):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()

        model.prepare_home_or_corp(data)
        model.extensions = ExtensionFlag.ALL

        assert model.home_or_corp == result
        assert model.prepared_home_or_corp == p_result

    def test_prepare(self):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()
        model.prepare(
            location='123,45',
            radius=1000,
            batch=True,
            extensions=ExtensionFlag.ALL,
            poi_type='bbb|ccc',
            road_level=RoadLevel.ALL,
            home_or_corp=HomeOrCorpControl.OFF,
        )

        assert model.location == [(123, 45)]
        assert model.radius == 1000
        assert model.batch == BatchFlag.ON
        assert model.extensions == ExtensionFlag.ALL
        assert model.poi_type == ['bbb', 'ccc']
        assert model.road_level == RoadLevel.ALL
        assert model.home_or_corp == HomeOrCorpControl.OFF

    def test_prepared_no_extensions(self):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()
        model.prepare(
            location='123,45',
            radius=1000,
            batch=True,
            extensions=ExtensionFlag.BASE,
            poi_type='bbb|ccc',
            road_level=RoadLevel.ALL,
            home_or_corp=HomeOrCorpControl.OFF,
        )

        assert model.prepared_home_or_corp is None
        assert model.prepared_road_level is None
        assert model.prepared_poi_type is None
        assert model.prepared_extensions is 'base'

    @pytest.mark.parametrize('data, result', [
        (dict(location='123,45', radius=1000, batch=True,
              extensions=ExtensionFlag.BASE, key='xxx', poi_type='xxxxx'),
         dict(location='123.000000,45.000000', key='xxx', extensions='base',
              radius=1000, batch='true')),
        (dict(location='123,45', radius=1000, batch=True,
              extensions=ExtensionFlag.ALL, key='xxx', poi_type='xxxxx'),
         dict(location='123.000000,45.000000', key='xxx', extensions='all',
              radius=1000, batch='true', poitype='xxxxx')),
    ])
    def test_generate_params(self, data, result):
        model = _regeo_code_model.PreparedReGeoCodeRequestParams()
        model.prepare(**data)
        for k, v in iteritems(result):
            assert model.params[k] == v

        assert len(model.params) == len(result)


class TestReGeoCodeResponseData(object):
    def test_get_single_data(self, mocker):
        raw_data = '{"status": "1","info": "OK","infocode": "10000",' \
                   ' "regeocode": {}}'
        model = _regeo_code_model.ReGeoCodeResponseData(raw_data)

        mocker.spy(_regeo_code_model.ReGeoCodeResponseData, '_get_single_data')
        mocker.spy(_regeo_code_model.ReGeoCodeResponseData, '_get_multi_data')

        assert model.data == model._get_data() == []

        assert model._get_single_data.call_count == 1 + 1
        assert model._get_multi_data.call_count == 0

        for i in model.data:
            assert isinstance(i, _regeo_code_model.ReGeoCodeData)

    def test_get_single_data_with_result(self):
        raw_data = '{"status": "1","info": "OK","infocode": "10000",' \
                   ' "regeocode": {"formatted_address": "xxx"}}'
        model = _regeo_code_model.ReGeoCodeResponseData(raw_data)

        assert model.data[0].formatted_address == 'xxx'
        assert model._data is None

        for i, j in zip(model.data, model.data):
            assert isinstance(i, _regeo_code_model.ReGeoCodeData)
            assert i != j
            assert id(i) != id(j)

    def test_get_single_data_in_static(self):
        raw_data = '{"status": "1","info": "OK","infocode": "10000",' \
                   ' "regeocode": {"formatted_address": "xxx"}}'
        model = _regeo_code_model.ReGeoCodeResponseData(raw_data,
                                                        static_mode=True)

        assert model.data[0].formatted_address == 'xxx'
        assert model._data is not None

        for i, j in zip(model.data, model.data):
            assert isinstance(i, _regeo_code_model.ReGeoCodeData)
            assert i == j
            assert id(i) == id(j)

    def test_get_multi_data(self, mocker):
        raw_data = '{"status": "1","info": "OK","infocode": "10000",' \
                   ' "regeocodes": []}'
        model = _regeo_code_model.ReGeoCodeResponseData(raw_data)

        mocker.spy(_regeo_code_model.ReGeoCodeResponseData, '_get_single_data')
        mocker.spy(_regeo_code_model.ReGeoCodeResponseData, '_get_multi_data')

        assert model.data == model._get_data() == []

        assert model._get_single_data.call_count == 0
        assert model._get_multi_data.call_count == 2

        for i in model.data:
            assert isinstance(i, _regeo_code_model.ReGeoCodeData)

    def test_get_multi_data_with_result(self):
        raw_data = '{"status": "1","info": "OK","infocode": "10000",' \
                   ' "regeocodes": [{"formatted_address": "xxx"}]}'
        model = _regeo_code_model.ReGeoCodeResponseData(raw_data)

        assert model.data[0].formatted_address == 'xxx'
        assert model._data is None

        for i, j in zip(model.data, model.data):
            assert isinstance(i, _regeo_code_model.ReGeoCodeData)
            assert i != j
            assert id(i) != id(j)

    def test_get_multi_data_in_static(self):
        raw_data = '{"status": "1","info": "OK","infocode": "10000",' \
                   ' "regeocodes": [{"formatted_address": "xxx"}]}'
        model = _regeo_code_model.ReGeoCodeResponseData(raw_data,
                                                        static_mode=True)

        assert model.data[0].formatted_address == 'xxx'
        assert model._data is not None

        for i, j in zip(model.data, model.data):
            assert isinstance(i, _regeo_code_model.ReGeoCodeData)
            assert i == j
            assert id(i) == id(j)


class TestReGeoCodeData(object):
    def test_decode_params(self):
        raw_data = {'formatted_address': 'xxx', 'address_component': None,
                    'pois': None, 'roads': None, 'roadinters': None,
                    'aois': None}
        model = _regeo_code_model.ReGeoCodeData(raw_data)

        model.decode_aois = lambda x: 'aois'
        model.decode_road_inters = lambda x: 'roadinters'
        model.decode_roads = lambda x: 'roads'
        model.decode_pois = lambda x: 'pois'
        model.decode_address_component = lambda x: 'address_component'

        assert model.aois == 'aois'
        assert model.roadinters == 'roadinters'
        assert model.roads == 'roads'
        assert model.address_component == 'address_component'
        assert model.pois == 'pois'

    def test_static_code_enable(self):
        raw_data = {'formatted_address': 'xxx', 'address_component': None,
                    'pois': None, 'roads': None, 'roadinters': None,
                    'aois': None}
        model = _regeo_code_model.ReGeoCodeData(raw_data, static=True)

        for i in raw_data:
            assert id(getattr(model, i)) == id(getattr(model, i))
            assert i in model.__dict__

    @pytest.mark.parametrize('fn, param, decode', [
        ('decode_pois', 'pois', _regeo_code_model.ReGeoPoi),
        ('decode_roads', 'roads', _regeo_code_model.ReGeoRoad),
        ('decode_road_inters', 'roadinters', _regeo_code_model.ReGeoRoadInter),
        ('decode_aois', 'aois', _regeo_code_model.ReGeoAOI),
    ])
    def test_decode_list_params(self, mocker, fn, param, decode):
        raw_data = {'formatted_address': 'xxx', 'address_component': None,
                    'pois': None, 'roads': None, 'roadinters': None,
                    'aois': None}

        model = _regeo_code_model.ReGeoCodeData(raw_data)

        mocker.spy(_regeo_code_model.ReGeoCodeData, fn)
        mocker.spy(_regeo_code_model.ReGeoCodeData, '_decode_to_list')

        r = getattr(model, fn)(raw_data)

        assert isinstance(r, list)

        # assert
        model._decode_to_list.assert_called_once_with(
            raw_data, param, decode, static=False)

        getattr(model, fn).assert_called_once_with(model, raw_data)

    def test_decode_address_component_params(self, mocker):
        raw_data = {'formatted_address': 'xxx', 'address_component': None,
                    'pois': None, 'roads': None, 'roadinters': None,
                    'aois': None}

        model = _regeo_code_model.ReGeoCodeData(raw_data)

        mocker.spy(_regeo_code_model.ReGeoCodeData, 'decode_address_component')

        r = model.decode_address_component(raw_data)

        assert isinstance(r, _regeo_code_model.ReGeoAddressComponent)

        model.decode_address_component.assert_called_once_with(model, raw_data)


class TestReGeoAddressComponent(object):
    def test_decode_params(self):
        raw_data = {'adcode': None, 'building': None, 'business_areas': None,
                    'city': None, 'citycode': None, 'district': None,
                    'neighborhood': None, 'province': None, 'sea_area': None,
                    'street_number': None, 'towncode': None, 'township': None}

        model = _regeo_code_model.ReGeoAddressComponent(raw_data)

        model.decode_business_areas = lambda x: 'decode_business_areas'
        model.decode_street_number = lambda x: 'decode_street_number'
        model.decode_neighborhood_data = lambda x: 'decode_neighborhood_data'
        model.decode_building_data = lambda x: 'decode_building_data'

        assert model.business_areas == 'decode_business_areas'
        assert model.street_number == 'decode_street_number'
        assert model.neighborhood == 'decode_neighborhood_data'
        assert model.building == 'decode_building_data'
        assert model.adcode is None

    def test_static_mode_enable(self):
        raw_data = {'adcode': None, 'building': None, 'business_areas': None,
                    'city': None, 'citycode': None, 'district': None,
                    'neighborhood': None, 'province': None, 'sea_area': None,
                    'street_number': None, 'towncode': None, 'township': None}

        model = _regeo_code_model.ReGeoAddressComponent(raw_data,
                                                        static=True)

        assert id(model.neighborhood) == id(model.neighborhood)

        for i in raw_data:
            assert id(getattr(model, i)) == id(getattr(model, i))
            assert i in model.__dict__

    @pytest.mark.parametrize('raw_data, result', [
        ({'building': {'name': 'namef', 'type_': 'type_f'}},
         {'name': 'namef', 'type': 'type_f'}),
        ({'building': []},
         {'name': None, 'type': None}),
        ({},
         {'name': None, 'type': None}),

    ])
    def test_decode_building(self, mocker, raw_data, result):
        model = _regeo_code_model.ReGeoAddressComponent(raw_data)

        mocker.spy(_regeo_code_model.ReGeoAddressComponent,
                   'decode_building_data')

        t = model.decode_building_data(raw_data)

        model.decode_building_data.assert_called_once_with(model, raw_data)

        assert isinstance(t, _regeo_code_model.Building)

        for k, v in iteritems(result):
            assert getattr(t, k) == v

    @pytest.mark.parametrize('raw_data, result', [
        ({'neighborhood': {'name': 'namef', 'type_': 'type_f'}},
         {'name': 'namef', 'type': 'type_f'}),
        ({'neighborhood': []},
         {'name': None, 'type': None}),
        ({},
         {'name': None, 'type': None}),

    ])
    def test_decode_neighborhood_data(self, mocker, raw_data, result):
        model = _regeo_code_model.ReGeoAddressComponent(raw_data)

        mocker.spy(_regeo_code_model.ReGeoAddressComponent,
                   'decode_neighborhood_data')

        t = model.decode_neighborhood_data(raw_data)

        model.decode_neighborhood_data.assert_called_once_with(model, raw_data)

        assert isinstance(t, _regeo_code_model.Neighborhood)

        for k, v in iteritems(result):
            assert getattr(t, k) == v

    @pytest.mark.parametrize('raw_data, result', [
        ({'street_number': {
            'distance': 1, 'direction': None, 'street': 'xxx',
            'number': None, 'location': None}},
         {'distance': 1, 'direction': None, 'street': 'xxx', 'number': None,
          'location': None}),
        ({'street_number': {
            'distance': 1, 'street': 'xxx'}},
         {'distance': 1, 'direction': None, 'street': 'xxx', 'number': None,
          'location': None}),
        ({'street_number': []},
         {'distance': None, 'direction': None, 'street': None, 'number': None,
          'location': None}),
        ({},
         {'distance': None, 'direction': None, 'street': None, 'number': None,
          'location': None}),

    ])
    def test_decode_street_number(self, mocker, raw_data, result):
        model = _regeo_code_model.ReGeoAddressComponent(raw_data)

        mocker.spy(_regeo_code_model.ReGeoAddressComponent,
                   'decode_street_number')

        t = model.decode_street_number(raw_data)

        model.decode_street_number.assert_called_once_with(model, raw_data)

        assert isinstance(t, _regeo_code_model.StreetNumber)

        for k, v in iteritems(result):
            assert getattr(t, k) == v

    @pytest.mark.parametrize('raw_data', [
        {}, {'business_areas': None}, {'business_areas': []}])
    def test_decode_business_areas_empty(self, mocker, raw_data):
        model = _regeo_code_model.ReGeoAddressComponent(raw_data)

        mocker.spy(_regeo_code_model.ReGeoAddressComponent,
                   'decode_business_areas')

        t = model.decode_business_areas(raw_data)

        model.decode_business_areas.assert_called_once_with(model, raw_data)

        assert t == []

    @pytest.mark.parametrize('raw_data, result', [
        ({'business_areas': [{}]},
         [{'location': None, 'id': None, 'name': None}]),
    ])
    def test_decode_business_areas_ok(self, mocker, raw_data, result):
        model = _regeo_code_model.ReGeoAddressComponent(raw_data)

        mocker.spy(_regeo_code_model.ReGeoAddressComponent,
                   'decode_business_areas')

        t = model.decode_business_areas(raw_data)

        model.decode_business_areas.assert_called_once_with(model, raw_data)

        assert isinstance(t, list)

        assert len(result) == len(t)
        for num, kv in enumerate(result):
            for k, v in iteritems(kv):
                assert getattr(t[num], k) == v

            assert isinstance(t[num], _regeo_code_model.BusinessArea)

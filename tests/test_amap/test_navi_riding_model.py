# coding: utf-8
# flake8: noqa
from __future__ import absolute_import

import pytest

from thrall.compat import basestring
from thrall.amap._models import _navi_model


class TestNaviRidingRequestParams(object):
    def test_init_ok(self):
        model = _navi_model.NaviRidingRequestParams(origin='aaa',
                                                    destination='vvv',
                                                    key='xxx')

        assert model.origin == 'aaa'
        assert model.destination == 'vvv'
        assert model.key == 'xxx'

    def test_prepare_data_ok(self):
        model = _navi_model.NaviRidingRequestParams(origin='123,45',
                                                    destination='234,56',
                                                    key='xxx')

        p = model.prepare_data()

        assert isinstance(p, _navi_model.PreparedNaviRidingRequestParams)


class TestPreparedNaviRidingRequestParams(object):
    def test_init_ok(self):
        model = _navi_model.PreparedNaviRidingRequestParams()

        assert model.origin == model.destination is None

    def test_prepare_ok(self, mocker):
        model = _navi_model.PreparedNaviRidingRequestParams()

        model.prepare_origin = lambda x: 'origin'
        model.prepare_destination = lambda x: 'destiantion'

        mocker.spy(model, 'prepare_origin')
        mocker.spy(model, 'prepare_destination')
        mocker.spy(model, 'prepare_base')

        model.prepare(origin='11', destination=22, key='xxx')

        model.prepare_origin.assert_called_once_with('11')
        model.prepare_destination.assert_called_once_with(22)
        assert model.prepare_base.call_count == 1

    @pytest.mark.parametrize('data, result, p_result', [
        ('111,22', (111, 22), u'111.000000,22.000000'),
        (['111,22', '333,44'], (111, 22), u'111.000000,22.000000'),
        ('111,22|333,44', (111, 22), u'111.000000,22.000000'),
        (None, None, None),
    ])
    def test_prepare_location_input(self, data, result, p_result):
        model = _navi_model.PreparedNaviRidingRequestParams()

        model.prepare_origin(data)
        model.prepare_destination(data)

        assert model.origin == model.destination == result
        assert model.prepared_origin == model.prepared_destination == p_result

    def test_generate_params(self):
        model = _navi_model.PreparedNaviRidingRequestParams()

        model.prepare(
            origin='111,22', destination=[(222, 33), "111,22|2,3"], key='xx')

        assert model.params['origin'] == '111.000000,22.000000'
        assert model.params['destination'] == '222.000000,33.000000'
        assert model.params['key'] == 'xx'


class TestNaviRidingResponseData(object):
    RAW_DATA = """{"data":{
    "destination":"116.434446,39.90816|116.434446,39.90816",
    "origin":"116.434307,39.90909","paths":[
    {"distance":217,"duration":52,"steps":[
    {"action":"右转","assistant_action":"","distance":54,"duration":13,
    "instruction":"骑行54米右转","orientation":"",
    "polyline":"116.434319,39.90905;116.434967,39.90905","road":""},
    {"action":"右转","assistant_action":"","distance":115,"duration":28,
    "instruction":"沿建国门北大街向南骑行115米右转","orientation":"南",
    "polyline":"116.434959,39.90905;116.434952,39.908985",
    "road":"建国门北大街"},{"action":"","assistant_action":"到达目的地",
    "distance":48,"duration":12,"instruction":"骑行48米到达目的地",
    "orientation":"","polyline":"116.435005,39.90807;116.434456,39.90807",
    "road":""}]}]},"errcode":0,"errdetail":null,"errmsg":"OK"}"""

    def test_get_data(self):
        model = _navi_model.NaviRidingResponseData(self.RAW_DATA)

        assert isinstance(model.data, _navi_model.NaviRidingData)

    def test_riding_data(self):
        model = _navi_model.NaviRidingResponseData(self.RAW_DATA,
                                                   static_mode=True)

        assert isinstance(model.data.paths, list)
        assert len(model.data.paths) == 1

        assert model.data.origin == "116.434307,39.90909"
        assert (model.data.destination
                == "116.434446,39.90816|116.434446,39.90816")

    def test_riding_path(self):
        model = _navi_model.NaviRidingResponseData(self.RAW_DATA,
                                                   static_mode=True)

        steps = model.data.paths[0].steps

        assert isinstance(steps, list)

        for step in steps:
            assert isinstance(step, _navi_model.RidingSteps)

    def test_riding_step_polyline(self):
        model = _navi_model.NaviRidingResponseData(self.RAW_DATA,
                                                   static_mode=True)

        step = model.data.paths[0].steps[0]

        assert not isinstance(step, basestring)

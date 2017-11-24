# coding: utf-8
# flake8: noqa
from __future__ import absolute_import

import pytest

from thrall.compat import basestring
from thrall.amap._models import _navi_model


class TestNaviWalkingResponseData(object):
    @pytest.fixture()
    def raw_data(self, data_dir):
        return open(str(data_dir.join('walking_result.json'))).read()

    def test_get_data(self, raw_data):
        model = _navi_model.NaviWalkingResponseData(raw_data)

        assert isinstance(model.data, _navi_model.NaviWalkingData)

    def test_data(self, raw_data):
        model = _navi_model.NaviWalkingResponseData(raw_data,
                                                    static_mode=True)

        assert isinstance(model.data.paths, list)
        assert len(model.data.paths) == 1

        for i in model.data.paths:
            assert isinstance(i, _navi_model.WalkingPath)

    def test_path(self, raw_data):
        model = _navi_model.NaviWalkingResponseData(raw_data,
                                                    static_mode=True)

        steps = model.data.paths[0].steps

        assert isinstance(steps, list)

        for step in steps:
            assert isinstance(step, _navi_model.WalkingSteps)

    def test_step_polyline(self, raw_data):
        model = _navi_model.NaviWalkingResponseData(raw_data,
                                                    static_mode=True)

        step = model.data.paths[0].steps[0]

        assert not isinstance(step, basestring)


class TestNaviDrivingResponseData(object):
    @pytest.fixture()
    def raw_data(self, data_dir):
        return open(str(data_dir.join('driving_result.json'))).read()

    def test_get_data(self, raw_data):
        model = _navi_model.NaviDrivingResponseData(raw_data)

        assert isinstance(model.data, _navi_model.NaviDrivingData)

    def test_data(self, raw_data):
        model = _navi_model.NaviDrivingResponseData(raw_data,
                                                    static_mode=True)

        assert isinstance(model.data.paths, list)
        assert len(model.data.paths) == 1

        for i in model.data.paths:
            assert isinstance(i, _navi_model.DrivingPath)

    def test_path(self, raw_data):
        model = _navi_model.NaviDrivingResponseData(raw_data,
                                                    static_mode=True)

        steps = model.data.paths[0].steps

        assert isinstance(steps, list)

        for step in steps:
            assert isinstance(step, _navi_model.DrivingSteps)

    def test_step_polyline(self, raw_data):
        model = _navi_model.NaviDrivingResponseData(raw_data,
                                                    static_mode=True)

        step = model.data.paths[0].steps[0]

        assert not isinstance(step, basestring)

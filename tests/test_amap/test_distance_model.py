# coding: utf-8
# flake8: noqa
from __future__ import absolute_import

import pytest

from thrall.exceptions import AMapBatchStatusError, AMapStatusError
from thrall.amap._models import _distance_model


class TestDistanceRequestParams(object):
    def test_init_ok(self):
        model = _distance_model.DistanceRequestParams(origins='123,45',
                                                      destination='123,45',
                                                      key='xxx')

        assert model.origins == '123,45'

    def test_prepare_ok(self):
        model = _distance_model.DistanceRequestParams(origins='123,45',
                                                      destination='123,45',
                                                      key='xxx')
        p = model.prepare()

        assert isinstance(p, _distance_model.PreparedDistanceRequestParams)

        assert p.origins == [(123, 45)]


class TestPreparedDistanceRequestParams(object):
    def test_init_ok(self):
        model = _distance_model.PreparedDistanceRequestParams()

        assert model.origins == model.destination == model.type is None

    @pytest.mark.parametrize('data, result, p_result', [
        (None, None, None),
        ((123, 34), [(123, 34)], '123.000000,34.000000'),
        ([(123, 34), '111,222'],
         [(123, 34), (111, 222)],
         '123.000000,34.000000|111.000000,222.000000'),
    ])
    def test_prepare_origins(self, data, result, p_result):
        model = _distance_model.PreparedDistanceRequestParams()

        model.prepare_origins(data)

        assert result == model.origins
        assert p_result == model.prepared_origins

    @pytest.mark.parametrize('data, result, p_result', [
        (None, None, None),
        ((123, 34), (123, 34), '123.000000,34.000000'),
        ([(123, 34), '111,222'], (123, 34), '123.000000,34.000000'),
    ])
    def test_prepare_destination(self, data, result, p_result):
        model = _distance_model.PreparedDistanceRequestParams()

        model.prepare_destination(data)

        assert result == model.destination
        assert p_result == model.prepared_destination

    @pytest.mark.parametrize('data, result, p_result', [
        (0, _distance_model.DistanceType.DIRECT, 0),
        (1, _distance_model.DistanceType.DRIVING, 1),
        (2, _distance_model.DistanceType.BUSLINE, 2),
        (3, _distance_model.DistanceType.WALKING, 3),
        (_distance_model.DistanceType.WALKING,
         _distance_model.DistanceType.WALKING,
         3),
    ])
    def test_prepare_type(self, data, result, p_result):
        model = _distance_model.PreparedDistanceRequestParams()

        model.prepare_type(data)

        assert result == model.type
        assert p_result == model.prepared_type

    @pytest.mark.parametrize('input, output', [
        (dict(origins=[(123, 34), (124, 45)], destination='123,12', key='def'),
         dict(origins='123.000000,34.000000|124.000000,45.000000',
              destination='123.000000,12.000000',
              key='def')),
        (dict(origins=[(123, 34), (124, 45)], destination='123,12',
              type=0, key='def'),
         dict(origins='123.000000,34.000000|124.000000,45.000000',
              destination='123.000000,12.000000',
              key='def', type=0)),
    ])
    def test_generate_params(self, input, output):
        model = _distance_model.PreparedDistanceRequestParams()

        model.prepare(**input)

        for k, v in model.params.items():
            assert output[k] == v

        assert len(model.params) == len(output)


class TestDistanceResponseData(object):
    def test_get_data(self, mocker):
        raw_data = """{"status":"1","info":"OK","infocode":"10000",
        "results":[{"origin_id":"1","dest_id":"1",
        "distance":"-1","duration":"-1"},
        {"origin_id":"2","dest_id":"1","distance":"62398","duration":"53484"},
        {"origin_id":"3","dest_id":"1","distance":"-1","duration":"-1"}]}"""

        model = _distance_model.DistanceResponseData(raw_data)

        mocker.spy(model, 'get_data')

        assert model.data[0].origin_id == 1
        assert model.data is not model.data

        assert model.get_data.call_count == 3

    def test_get_data_static(self, mocker):
        raw_data = """{"status":"1","info":"OK","infocode":"10000",
        "results":[{"origin_id":"1","dest_id":"1",
        "distance":"-1","duration":"-1"},
        {"origin_id":"2","dest_id":"1","distance":"62398","duration":"53484"},
        {"origin_id":"3","dest_id":"1","distance":"-1","duration":"-1"}]}"""

        model = _distance_model.DistanceResponseData(raw_data,
                                                     static_mode=True)

        mocker.spy(model, 'get_data')

        assert model.data[0].origin_id == 1
        assert model.data is model.data

        assert model.get_data.call_count == 0

    def test_raise_batch_exception(self):
        raw_data = """{"status":"1","info":"OK","infocode":"10000","results":
        [{"origin_id":"1","dest_id":"1","distance":"0",
        "duration":"0","info":"不支持的坐标点","code":"3"},
        {"origin_id":"2","dest_id":"1","distance":"98418","duration":"6660"},
        {"origin_id":"3","dest_id":"1","distance":"211649",
        "duration":"11220"}]}"""

        model = _distance_model.DistanceResponseData(raw_data,
                                                     static_mode=True)

        with pytest.raises(AMapBatchStatusError) as err:
            model.raise_for_status()

        assert isinstance(err.value.errors[0], AMapStatusError)
        assert err.value.errors[1] == err.value.errors[2] is None

        assert err.value.errors[0].data == model


class TestDistanceData(object):
    def test_decode(self):
        model = _distance_model.DistanceData({u'dest_id': u'1',
                                              u'distance': u'98418',
                                              u'duration': u'6660',
                                              u'origin_id': u'2'})

        assert model.dest_id == 1
        assert model.origin_id == 2
        assert model.distance == 98418 and isinstance(model.distance, float)
        assert model.duration == 6660 and isinstance(model.distance, float)

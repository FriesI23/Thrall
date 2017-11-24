# coding: utf-8
# flake8: noqa
from __future__ import absolute_import

import pytest

from thrall.amap._models import _batch_model
from thrall.exceptions import AMapBatchStatusError
from thrall.amap.session import BATCH_DECODE_DEFAULT_PAIRS


class TestBatchRequestParams(object):
    @pytest.mark.parametrize('batch_list, url_pairs, key, result', [
        (None, None, 'xx', ([], {}, 'xx')),
        ([1, 2], {1: 1}, 'x', ([1, 2], {1: 1}, 'x')),
    ])
    def test_init_ok(self, batch_list, url_pairs, key, result):
        model = _batch_model.BatchRequestParams(batch_list=batch_list,
                                                url_pairs=url_pairs,
                                                key=key)

        assert model.batch_list == result[0]
        assert model.url_pairs == result[1]
        assert model.key == result[2]

    def test_prepare_data(self):
        model = _batch_model.BatchRequestParams(key='xxx')

        p = model.prepare()

        assert isinstance(p, _batch_model.PreparedBatchParams)
        assert p.key == 'xxx'


def test_batch_exc_mixin():
    model = _batch_model.BatchExcMixin()

    def inside_func(i):
        if i == 5:
            raise RuntimeError

    with pytest.raises(AMapBatchStatusError) as err:
        model.do_list_batch(range(10), inside_func)

    assert len(err.value.errors) == 10
    assert isinstance(err.value.errors[5], RuntimeError)


class TestPreparedBatchParams(object):
    def test_init_ok(self):
        model = _batch_model.PreparedBatchParams()

        assert model.batch_list == []
        assert model.url_pairs is None

    def test_prepare(self, mocker):
        model = _batch_model.PreparedBatchParams()

        model.prepare_batch_list = lambda x: 'list'

        mocker.spy(model, 'prepare_batch_list')
        mocker.spy(model, 'prepare_base')

        model.prepare(key='xxx')

        model.prepare_base.assert_called_once_with(key='xxx')
        assert model.prepare_batch_list.call_count == 1

    def test_prepare_batch_list(self, mocker):
        from thrall.amap.models import (GeoCodeRequestParams,
                                        ReGeoCodeRequestParams,
                                        PreparedGeoCodeRequestParams,
                                        PreparedReGeoCodeRequestParams)

        model = _batch_model.PreparedBatchParams()

        mocker.spy(GeoCodeRequestParams, 'prepare')
        mocker.spy(ReGeoCodeRequestParams, 'prepare')

        model.prepare_batch_list([
            GeoCodeRequestParams(address='xx', key='xxx'),
            ReGeoCodeRequestParams(location='12,12', key='xxx')
        ])

        assert isinstance(model.batch_list[0], GeoCodeRequestParams)
        assert isinstance(model.batch_list[1], ReGeoCodeRequestParams)
        assert len(model.batch_list) == 2

        pl = model.prepared_batch_list()
        assert isinstance(pl[0], PreparedGeoCodeRequestParams)
        assert isinstance(pl[1], PreparedReGeoCodeRequestParams)

        assert GeoCodeRequestParams.prepare.call_count == 1
        assert ReGeoCodeRequestParams.prepare.call_count == 1
        assert len(pl) == 2

    def test_package_param(self):
        from thrall.amap._models._geo_code_model import GeoCodeRequestParams
        from thrall.amap.urls import GEO_CODING_URL
        from thrall.consts import RouteKey

        model = _batch_model.PreparedBatchParams(
            url_pairs={RouteKey.GEO_CODE: GEO_CODING_URL})
        mock_p = GeoCodeRequestParams(address='xx', key='xxx').prepare()

        r = model.package_param(mock_p)

        assert r['url'] == GEO_CODING_URL.path
        assert r['params']['key'] == 'xxx'
        assert r['params']['address'] == 'xx'
        assert len(r.keys()) == 2

    def test_package_all_params(self, mocker):
        from thrall.amap._models._geo_code_model import GeoCodeRequestParams
        from thrall.amap.urls import GEO_CODING_URL
        from thrall.consts import RouteKey

        model = _batch_model.PreparedBatchParams(
            url_pairs={RouteKey.GEO_CODE: GEO_CODING_URL})
        mocker.spy(model, 'do_list_batch')

        mock_p = GeoCodeRequestParams(address='xx', key='xxx').prepare()

        _ = model.package_all_params([mock_p])

        assert model.do_list_batch.call_count == 1

    def test_generate_params(self, mocker):
        from thrall.amap.models import (GeoCodeRequestParams,
                                        ReGeoCodeRequestParams)
        from thrall.amap.urls import GEO_CODING_URL, REGEO_CODING_URL
        from thrall.consts import RouteKey

        model = _batch_model.PreparedBatchParams(
            url_pairs={RouteKey.GEO_CODE: GEO_CODING_URL,
                       RouteKey.REGEO_CODE: REGEO_CODING_URL})

        mocker.spy(model, 'init_basic_params')

        model.prepare(batch_list=[
            GeoCodeRequestParams(address='xx', key='xxx'),
            ReGeoCodeRequestParams(location='12,12', key='xxx')
        ], key='1234')
        p = model.params

        assert model.init_basic_params.call_count == 1

        assert p['key'] == '1234'
        assert isinstance(p['batch'], list)

        assert p['batch'][0]['url'] == GEO_CODING_URL.path
        assert p['batch'][1]['url'] == REGEO_CODING_URL.path


class TestBatchResponseData(object):
    RAW_DATA = ('[{"status":200,"body":{"info":"OK","status":"1",'
                '"count":"1","geocodes":[{"level":"兴趣点","city":"上海市",'
                '"province":"上海市","neighborhood":{"name":{},"type":{}},'
                '"building":{"name":{},"type":{}},"street":{},"number":{'
                '},"township":{},"formatted_address":"上海市普陀区近铁城市广场",'
                '"location":"121.380638,31.231571","adcode":"310107",'
                '"district":"普陀区","citycode":"021"}],'
                '"infocode":"10000"},"header":{'
                '"gsid":"011131017043151133046613500271795012135",'
                '"Content-Type":"application\/json;charset=UTF-8",'
                '"Access-Control-Allow-Methods":"*",'
                '"Access-Control-Allow-Origin":"*","sc":"0.038",'
                '"Content-Length":393,'
                '"Access-Control-Allow-Headers":"DNT,X-CustomHeader,'
                'Keep-Alive,User-Agent,X-Requested-With,'
                'If-Modified-Since,Cache-Control,Content-Type,key,x-biz,'
                'x-info,platinfo,encr,enginever,gzipped,poiid",'
                '"X-Powered-By":"ring\/1.0.0"}},{"status":200,"body":{'
                '"status":"1","regeocode":{"addressComponent":{'
                '"city":"廊坊市","province":"河北省","adcode":"131023",'
                '"district":"永清县","towncode":"131023100000",'
                '"streetNumber":{"number":{},"direction":{},"distance":{'
                '},"street":{}},"country":"中国","township":"永清镇",'
                '"businessAreas":[{}],"building":{"name":{},"type":{}},'
                '"neighborhood":{"name":{},"type":{}},'
                '"citycode":"0316"},'
                '"formatted_address":"河北省廊坊市永清县永清镇永信线"},"info":"OK",'
                '"infocode":"10000"},"header":{'
                '"gsid":"011131017043151133046613500271795012135",'
                '"Content-Type":"application\/json;charset=UTF-8",'
                '"Access-Control-Allow-Methods":"*",'
                '"Access-Control-Allow-Origin":"*","sc":"0.011",'
                '"Content-Length":478,'
                '"Access-Control-Allow-Headers":"DNT,X-CustomHeader,'
                'Keep-Alive,User-Agent,X-Requested-With,'
                'If-Modified-Since,Cache-Control,Content-Type,key,x-biz,'
                'x-info,platinfo,encr,enginever,gzipped,poiid",'
                '"X-Powered-By":"ring\/1.0.0"}}]')

    def test_init_ok(self):
        raw_data = "{}"
        model = _batch_model.BatchResponseData(raw_data, None, None)

        assert model.prepared_data is None
        assert model.decode_pairs == {}
        assert model._raw_data is None

    @pytest.mark.parametrize('raw_data, status', [
        ('{"status": "0", "info": "INVALID_BATCH_PARAM", "infocode": "20005"}',
         0),
        ('[]', 1),

    ])
    def test_status(self, raw_data, status):
        model = _batch_model.BatchResponseData(raw_data, None, None)

        assert model.status == status

    @pytest.mark.parametrize('raw_data, count', [
        ('{"status": "0", "info": "INVALID_BATCH_PARAM", "infocode": "20005"}',
         0),
        ('[]', 0), ('[{}, {}]', 2)
    ])
    def test_count(self, raw_data, count):
        model = _batch_model.BatchResponseData(raw_data, None, None)

        assert model.count == count

    @pytest.mark.parametrize('raw_data, status_msg', [
        ('{"status": "0", "info": "INVALID_BATCH_PARAM", "infocode": "20005"}',
         (20005, 'INVALID_BATCH_PARAM', '')),
        ('[]',
         (10000, 'OK', '')),
        ('[{}, {}]',
         (10000, 'OK', ''))
    ])
    def test_status_msg(self, raw_data, status_msg):
        model = _batch_model.BatchResponseData(raw_data, None, None)

        assert model.status_msg == status_msg

    @pytest.fixture
    def mock_prepared_data(self):
        from thrall.amap.session import BATCH_URL_DEFAULT_PAIRS
        from thrall.amap.models import (GeoCodeRequestParams,
                                        ReGeoCodeRequestParams)

        return _batch_model.BatchRequestParams(
            [GeoCodeRequestParams(address='xx', key='xxx'),
             ReGeoCodeRequestParams(location='12,12', key='xxx')],
            url_pairs=BATCH_URL_DEFAULT_PAIRS, key='xxx')

    def test_get_data(self, mock_prepared_data):
        model = _batch_model.BatchResponseData(
            p=mock_prepared_data, raw_data=self.RAW_DATA,
            decode_pairs=BATCH_DECODE_DEFAULT_PAIRS,
            static_mode=True)

        assert len(model.data) == 2

        assert model.data is model.data

        assert model.data[0].status == model.data[1].status == 1

    def test_get_batch_status(self, mock_prepared_data):
        model = _batch_model.BatchResponseData(
            p=mock_prepared_data, raw_data=self.RAW_DATA,
            decode_pairs=BATCH_DECODE_DEFAULT_PAIRS,
            static_mode=True)

        assert len(model.batch_status) == 2
        assert model.batch_status[0] is model.data[0].status
        assert model.batch_status[1] is model.data[1].status

    def test_get_batch_status_msg(self, mock_prepared_data):
        model = _batch_model.BatchResponseData(
            p=mock_prepared_data, raw_data=self.RAW_DATA,
            decode_pairs=BATCH_DECODE_DEFAULT_PAIRS,
            static_mode=True)

        assert len(model.batch_status_msg) == 2
        assert model.batch_status_msg[0] == model.data[0].status_msg
        assert model.batch_status_msg[1] == model.data[1].status_msg

    def test_raise_for_status_ok(self, mock_prepared_data):
        model = _batch_model.BatchResponseData(
            p=mock_prepared_data, raw_data=self.RAW_DATA,
            decode_pairs=BATCH_DECODE_DEFAULT_PAIRS,
            static_mode=True)

        model.raise_for_status()

    def test_raise_for_status_request_err(self):
        raw_data = """{"status":"0","info":"INVALID_BATCH_PARAM",
        "infocode":"20005"}"""
        model = _batch_model.BatchResponseData(
            p=None, raw_data=raw_data,
            decode_pairs=BATCH_DECODE_DEFAULT_PAIRS,
            static_mode=True)

        from thrall.exceptions import AMapStatusError

        with pytest.raises(AMapStatusError) as err:
            model.raise_for_status()

        assert '20005-INVALID_BATCH_PARAM' in str(err.value)

    def test_raise_for_status_batch_params_err(self, mock_prepared_data):
        raw_data = (
            '[{"status":200,"body":{"info":"OK","status":"1","count":"1",'
            '"geocodes":[{"level":"兴趣点","city":"上海市","province":"上海市",'
            '"neighborhood":{"name":{},"type":{}},"building":{"name":{},"type":{'
            '}},"street":{},"number":{},"township":{},'
            '"formatted_address":"上海市普陀区近铁城市广场","location":"121.380638,'
            '31.231571","adcode":"310107","district":"普陀区","citycode":"021"}],'
            '"infocode":"10000"},"header":{'
            '"gsid":"011131017040151133202135800187559487341",'
            '"Content-Type":"application\/json;charset=UTF-8",'
            '"Access-Control-Allow-Methods":"*",'
            '"Access-Control-Allow-Origin":"*","sc":"0.010",'
            '"Content-Length":393,"Access-Control-Allow-Headers":"DNT,'
            'X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,'
            'If-Modified-Since,Cache-Control,Content-Type,key,x-biz,x-info,'
            'platinfo,encr,enginever,gzipped,poiid",'
            '"X-Powered-By":"ring\/1.0.0"}},{"status":200,"body":{"status":"0",'
            '"info":"INVALID_USER_KEY","infocode":"10001"},"header":{'
            '"gsid":"011131017040151133202135800187559487341",'
            '"Content-Type":"application\/json",'
            '"Access-Control-Allow-Methods":"*",'
            '"Access-Control-Allow-Origin":"*","sc":"0.000","Content-Length":59,'
            '"Access-Control-Allow-Headers":"DNT,X-CustomHeader,Keep-Alive,'
            'User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,'
            'Content-Type,key,x-biz,x-info,platinfo,encr,enginever,gzipped,'
            'poiid","X-Powered-By":"ring\/1.0.0"}}]')
        model = _batch_model.BatchResponseData(
            p=mock_prepared_data, raw_data=raw_data,
            decode_pairs=BATCH_DECODE_DEFAULT_PAIRS,
            static_mode=True)

        from thrall.exceptions import AMapStatusError

        with pytest.raises(AMapBatchStatusError) as e:
            model.raise_for_status()

        assert e.value.errors[0] is None
        assert isinstance(e.value.errors[1], AMapStatusError)

# coding: utf-8
# flake8: noqa
from __future__ import absolute_import

import pytest

from thrall.amap.adapters import (
    AMapEncodeAdapter,
    AMapJsonDecoderAdapter,
    BaseEncoderAdapter,
    BaseDecoderAdapter,
)

from thrall.amap.models import (
    GeoCodeResponseData,
    GeoCodeRequestParams,
    PreparedGeoCodeRequestParams,
    ReGeoCodeResponseData,
    PreparedReGeoCodeRequestParams,
    SearchResponseData,
    PreparedSearchTextRequestParams,
    PreparedSearchAroundRequestParams,
    SuggestResponseData,
    PreparedSuggestRequestParams,
    DistanceResponseData,
    PreparedDistanceRequestParams,
    NaviRidingResponseData,
    PreparedNaviRidingRequestParams,
    BatchResponseData,
    PreparedBatchParams,
    NaviWalkingResponseData,
    PreparedNaviWalkingRequestParams,
    NaviDrivingResponseData,
    PreparedNaviDrivingRequestParams,
)


class TestAMapEncodeAdapter(object):
    def test_init_ok(self, mocker):
        mocker.spy(AMapEncodeAdapter, 'registry_encoders')

        model = AMapEncodeAdapter()

        assert model.all_registered_coders is not None
        assert model.registry_encoders.call_count == 1

    def test_registry_encoders_ok(self):
        model = AMapEncodeAdapter()

        assert model.all_registered_coders[
                   'encode_geo_code'] == GeoCodeRequestParams

    def test_registry_ok(self, mocker):
        model = AMapEncodeAdapter()

        mocker.spy(BaseEncoderAdapter, 'registry')
        model.registry(model.encode_geo_code, GeoCodeRequestParams)

        assert BaseEncoderAdapter.registry.call_count == 1

    def test_encoder_context(self, mocker):
        model = AMapEncodeAdapter()
        model.registry(model.encode_geo_code, GeoCodeRequestParams)

        mocker.spy(GeoCodeRequestParams, 'prepare')

        model.get_encoder('encode_geo_code', address='xx', key='')

        assert GeoCodeRequestParams.prepare.call_count == 1

    def test_encoder_context_err(self):
        model = AMapEncodeAdapter()
        model.registry(model.encode_geo_code, GeoCodeRequestParams)

        with pytest.raises(KeyError):
            model.get_encoder('encode_xgeo_code', address='', key='')


class TestAMapJsonDecoderAdapter(object):
    def test_init_ok(self, mocker):
        mocker.spy(AMapJsonDecoderAdapter, 'registry_decoders')

        model = AMapJsonDecoderAdapter()

        assert model.all_registered_coders is not None
        assert model.registry_decoders.call_count == 1

    def test_registry_decoders_ok(self):
        model = AMapJsonDecoderAdapter()

        assert model.all_registered_coders[
                   'decode_geo_code'] == GeoCodeResponseData

    def test_registry_ok(self, mocker):
        model = AMapJsonDecoderAdapter()

        mocker.spy(BaseDecoderAdapter, 'registry')
        model.registry(model.decode_geo_code, GeoCodeRequestParams)

        assert BaseDecoderAdapter.registry.call_count == 1

    def test_decoder_context(self, mocker):
        model = AMapJsonDecoderAdapter()
        model.registry(model.decode_geo_code, GeoCodeResponseData)

        mocker.spy(GeoCodeResponseData, '__init__')

        model.get_decoder('decode_geo_code', raw_data='{}')

        assert GeoCodeResponseData.__init__.call_count == 1

    def test_decoder_context_err(self):
        model = AMapJsonDecoderAdapter()
        model.registry(model.decode_geo_code, GeoCodeResponseData)

        with pytest.raises(KeyError):
            model.get_decoder('encode_xgeo_code', raw_data={})


@pytest.mark.parametrize('func, params, result, instance', [
    ('encode_geo_code',
     dict(address='abc', key='def'),
     dict(address=['abc'], key='def'),
     PreparedGeoCodeRequestParams),
    ('encode_regeo_code',
     dict(location='125,25', key='def'),
     dict(location=[(125, 25)], key='def'),
     PreparedReGeoCodeRequestParams),
    ('encode_search_text',
     dict(keywords=u'北京大学|xxx', key='def'),
     dict(keywords=[u'北京大学', 'xxx'], key='def'),
     PreparedSearchTextRequestParams),
    ('encode_search_around',
     dict(location='123,45|322,33', key='def'),
     dict(location=(123, 45), key='def'),
     PreparedSearchAroundRequestParams),
    ('encode_suggest',
     dict(keyword=u'北京大学', key='def'),
     dict(keyword=u'北京大学', key='def'),
     PreparedSuggestRequestParams),
    ('encode_distance',
     dict(origins='111,222.0', destination='111.1,333.0', type=0, key='xxx'),
     dict(origins=[(111, 222.0)], destination=(111.1, 333.0), type=0,
          key='xxx'),
     PreparedDistanceRequestParams),
    ('encode_riding',
     dict(origin='111.0,22', destination='1,2.0', key='xxx'),
     dict(origin=(111.0, 22), destination=(1, 2.0), key='xxx'),
     PreparedNaviRidingRequestParams),
    ('encode_walking',
     dict(origin='111.0,22', destination='1,2.0', key='xxx'),
     dict(origin=(111.0, 22), destination=(1, 2.0), key='xxx'),
     PreparedNaviWalkingRequestParams),
    ('encode_driving',
     dict(origin='111.0,22', destination='1,2.0', key='xxx'),
     dict(origin=(111.0, 22), destination=(1, 2.0), key='xxx'),
     PreparedNaviDrivingRequestParams),
    ('encode_batch',
     dict(key='xxx'),
     dict(key='xxx'),
     PreparedBatchParams)
])
def test_amap_encode_adapter_func(func, params, result, instance):
    model = AMapEncodeAdapter()

    r = getattr(model, func)(**params)

    for k, v in result.items():
        assert getattr(r, k) == v

    assert isinstance(r, instance)


@pytest.mark.parametrize("func, instance", [
    ('decode_geo_code', GeoCodeResponseData),
    ('decode_regeo_code', ReGeoCodeResponseData),
    ('decode_search_text', SearchResponseData),
    ('decode_search_around', SearchResponseData),
    ('decode_suggest', SuggestResponseData),
    ('decode_distance', DistanceResponseData),
    ('decode_riding', NaviRidingResponseData),
    ('decode_walking', NaviWalkingResponseData),
    ('decode_driving', NaviDrivingResponseData),
])
def test_amap_json_decode_adapter_func(func, instance):
    model = AMapJsonDecoderAdapter()

    r = getattr(model, func)(raw_data='{"status": "1"}')

    assert r.status == 1

    assert isinstance(r, instance)


def test_amap_json_batch_decode_adapter_func():
    model = AMapJsonDecoderAdapter()

    r = model.decode_batch('{"status": "1"}', None, None)

    assert r.status == 1

    assert isinstance(r, BatchResponseData)

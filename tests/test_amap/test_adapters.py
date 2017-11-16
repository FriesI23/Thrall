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
    SuggestResponseData,
    PreparedSuggestRequestParams,
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

    def test_registry_type_err(self):
        model = AMapEncodeAdapter()

        with pytest.raises(TypeError):
            model.registry(model.encode_geo_code, 'GeoCodeRequestParams')

    def test_encoder_context(self, mocker):
        model = AMapEncodeAdapter()
        model.registry(model.encode_geo_code, GeoCodeRequestParams)

        mocker.spy(GeoCodeRequestParams, 'prepare')

        with model.encoder_context('encode_geo_code', address='xx', key=''):
            pass

        assert GeoCodeRequestParams.prepare.call_count == 1

    def test_encoder_context_err(self):
        model = AMapEncodeAdapter()
        model.registry(model.encode_geo_code, GeoCodeRequestParams)

        with pytest.raises(KeyError):
            with model.encoder_context('encode_xgeo_code', address='', key=''):
                pass


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

    def test_registry_type_err(self):
        model = AMapJsonDecoderAdapter()

        with pytest.raises(TypeError):
            model.registry(model.decode_geo_code, 'GeoCodeResponseData')

    def test_decoder_context(self, mocker):
        model = AMapJsonDecoderAdapter()
        model.registry(model.decode_geo_code, GeoCodeResponseData)

        mocker.spy(GeoCodeResponseData, '__init__')

        with model.decoder_context('decode_geo_code', raw_data='{}'):
            pass

        assert GeoCodeResponseData.__init__.call_count == 1

    def test_decoder_context_err(self):
        model = AMapJsonDecoderAdapter()
        model.registry(model.decode_geo_code, GeoCodeResponseData)

        with pytest.raises(KeyError):
            with model.decoder_context('encode_xgeo_code', raw_data={}):
                pass


class TestAMapEncodeAdapterFunc(object):
    def test_encode_geo_code(self):
        model = AMapEncodeAdapter()

        r = model.encode_geo_code(address='abc', key='def')

        assert r.address == ['abc']
        assert r.key == 'def'

        assert isinstance(r, PreparedGeoCodeRequestParams)

    def test_encode_regeo_code(self):
        model = AMapEncodeAdapter()

        r = model.encode_regeo_code('125,25', key='def')

        assert r.location == [(125, 25)]
        assert r.key == 'def'

        assert isinstance(r, PreparedReGeoCodeRequestParams)

    def test_encode_search_text(self):
        model = AMapEncodeAdapter()

        r = model.encode_search_text(keywords=u'北京大学|xxx', key='def')

        assert r.keywords == [u'北京大学', 'xxx']
        assert r.key == 'def'

        assert isinstance(r, PreparedSearchTextRequestParams)

    def test_encode_suggest(self):
        model = AMapEncodeAdapter()

        r = model.encode_suggest(keyword=u'北京大学', key='def')

        assert r.keyword == u'北京大学'
        assert r.key == 'def'

        assert isinstance(r, PreparedSuggestRequestParams)


class TestAMapJsonDecoderAdapterFunc(object):
    def test_decode_geo_code(self):
        model = AMapJsonDecoderAdapter()

        r = model.decode_geo_code(raw_data='{"status": "1"}')

        assert r.status == 1

        assert isinstance(r, GeoCodeResponseData)

    def test_decode_regeo_code(self):
        model = AMapJsonDecoderAdapter()

        r = model.decode_regeo_code(raw_data='{"status": "1"}')

        assert r.status == 1

        assert isinstance(r, ReGeoCodeResponseData)

    def test_decode_search(self):
        model = AMapJsonDecoderAdapter()

        r = model.decode_search(raw_data='{"status": "1"}')

        assert r.status == 1

        assert isinstance(r, SearchResponseData)

    def test_decode_suggest(self):
        model = AMapJsonDecoderAdapter()

        r = model.decode_suggest(raw_data='{"status": "1"}')

        assert r.status == 1
        assert isinstance(r, SuggestResponseData)

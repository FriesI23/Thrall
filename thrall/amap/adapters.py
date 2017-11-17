# coding: utf-8
from __future__ import absolute_import

from contextlib import contextmanager

from ..base import BaseDecoderAdapter, BaseEncoderAdapter
from ..utils import check_params_type
from .models import (
    DistanceRequestParams,
    DistanceResponseData,
    GeoCodeRequestParams,
    GeoCodeResponseData,
    ReGeoCodeRequestParams,
    ReGeoCodeResponseData,
    SearchAroundRequestParams,
    SearchResponseData,
    SearchTextRequestParams,
    SuggestRequestParams,
    SuggestResponseData
)


class AMapEncodeAdapter(BaseEncoderAdapter):

    @contextmanager
    def encoder_context(self, func_name, *args, **kwargs):
        encoder = self.all_registered_coders[func_name]
        p_encoder = encoder(*args, **kwargs).prepare()
        yield p_encoder

    def registry_encoders(self):
        self.registry(self.encode_geo_code, GeoCodeRequestParams)
        self.registry(self.encode_regeo_code, ReGeoCodeRequestParams)
        self.registry(self.encode_search_text, SearchTextRequestParams)
        self.registry(self.encode_search_around, SearchAroundRequestParams)
        self.registry(self.encode_suggest, SuggestRequestParams)
        self.registry(self.encode_distance, DistanceRequestParams)

    @check_params_type(coder=(type,))
    def registry(self, func, coder):
        return super(AMapEncodeAdapter, self).registry(func, coder)

    def encode_geo_code(self, *args, **kwargs):
        with self.encoder_context('encode_geo_code', *args, **kwargs) as p:
            return p

    def encode_regeo_code(self, *args, **kwargs):
        with self.encoder_context('encode_regeo_code', *args, **kwargs) as p:
            return p

    def encode_search_text(self, *args, **kwargs):
        with self.encoder_context('encode_search_text',
                                  *args, **kwargs) as p:
            return p

    def encode_search_around(self, *args, **kwargs):
        with self.encoder_context('encode_search_around',
                                  *args, **kwargs) as p:
            return p

    def encode_suggest(self, *args, **kwargs):
        with self.encoder_context('encode_suggest', *args, **kwargs) as p:
            return p

    def encode_distance(self, *args, **kwargs):
        with self.encoder_context('encode_distance', *args, **kwargs) as p:
            return p


class AMapJsonDecoderAdapter(BaseDecoderAdapter):

    def __init__(self, static_mode=False):
        super(AMapJsonDecoderAdapter, self).__init__()
        self._static = static_mode

    @contextmanager
    def decoder_context(self, func_name, *args, **kwargs):
        decoder = self.all_registered_coders[func_name]
        if self._static:
            kwargs['static_mode'] = True

        p_decoder = decoder(*args, **kwargs)
        yield p_decoder

    def registry_decoders(self):
        self.registry(self.decode_geo_code, GeoCodeResponseData)
        self.registry(self.decode_regeo_code, ReGeoCodeResponseData)
        self.registry(self.decode_search_text, SearchResponseData)
        self.registry(self.decode_search_around, SearchResponseData)
        self.registry(self.decode_suggest, SuggestResponseData)
        self.registry(self.decode_distance, DistanceResponseData)

    @check_params_type(coder=(type,))
    def registry(self, func, coder):
        return super(AMapJsonDecoderAdapter, self).registry(func, coder)

    def decode_geo_code(self, *args, **kwargs):
        with self.decoder_context('decode_geo_code', *args, **kwargs) as p:
            return p

    def decode_regeo_code(self, *args, **kwargs):
        with self.decoder_context('decode_regeo_code', *args, **kwargs) as p:
            return p

    def decode_search_text(self, *args, **kwargs):
        with self.decoder_context('decode_search_text',
                                  *args, **kwargs) as p:
            return p

    def decode_search_around(self, *args, **kwargs):
        with self.decoder_context('decode_search_around',
                                  *args, **kwargs) as p:
            return p

    def decode_suggest(self, *args, **kwargs):
        with self.decoder_context('decode_suggest', *args, **kwargs) as p:
            return p

    def decode_distance(self, *args, **kwargs):
        with self.decoder_context('decode_distance', *args, **kwargs) as p:
            return p

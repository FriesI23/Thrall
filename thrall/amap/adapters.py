# coding: utf-8
from __future__ import absolute_import

from ..base import BaseDecoderAdapter, BaseEncoderAdapter
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
    SuggestResponseData,
    DistrictRequestParams,
    DistrictResponseData,
    NaviRidingRequestParams,
    NaviRidingResponseData,
    NaviWalkingRequestParams,
    NaviWalkingResponseData,
    NaviDrivingRequestParams,
    NaviDrivingResponseData,
    BatchRequestParams,
    BatchResponseData,
)


class AMapEncodeAdapter(BaseEncoderAdapter):

    def get_encoder(self, func_name, *args, **kwargs):
        encoder = self.all_registered_coders[func_name]
        p_encoder = encoder(*args, **kwargs).prepare()
        return p_encoder

    def registry_encoders(self):
        self.registry(self.encode_geo_code, GeoCodeRequestParams)
        self.registry(self.encode_regeo_code, ReGeoCodeRequestParams)
        self.registry(self.encode_search_text, SearchTextRequestParams)
        self.registry(self.encode_search_around, SearchAroundRequestParams)
        self.registry(self.encode_suggest, SuggestRequestParams)
        self.registry(self.encode_district, DistrictRequestParams)
        self.registry(self.encode_distance, DistanceRequestParams)
        self.registry(self.encode_riding, NaviRidingRequestParams)
        self.registry(self.encode_walking, NaviWalkingRequestParams)
        self.registry(self.encode_driving, NaviDrivingRequestParams)
        self.registry(self.encode_batch, BatchRequestParams)

    def registry(self, func, coder):
        return super(AMapEncodeAdapter, self).registry(func, coder)

    def encode_geo_code(self, *args, **kwargs):
        return self.get_encoder('encode_geo_code', *args, **kwargs)

    def encode_regeo_code(self, *args, **kwargs):
        return self.get_encoder('encode_regeo_code', *args, **kwargs)

    def encode_search_text(self, *args, **kwargs):
        return self.get_encoder('encode_search_text', *args, **kwargs)

    def encode_search_around(self, *args, **kwargs):
        return self.get_encoder('encode_search_around', *args, **kwargs)

    def encode_suggest(self, *args, **kwargs):
        return self.get_encoder('encode_suggest', *args, **kwargs)

    def encode_district(self, *args, **kwargs):
        return self.get_encoder('encode_district', *args, **kwargs)

    def encode_distance(self, *args, **kwargs):
        return self.get_encoder('encode_distance', *args, **kwargs)

    def encode_riding(self, *args, **kwargs):
        return self.get_encoder('encode_riding', *args, **kwargs)

    def encode_walking(self, *args, **kwargs):
        return self.get_encoder('encode_walking', *args, **kwargs)

    def encode_driving(self, *args, **kwargs):
        return self.get_encoder('encode_driving', *args, **kwargs)

    def encode_batch(self, *args, **kwargs):
        return self.get_encoder('encode_batch', *args, **kwargs)


class AMapJsonDecoderAdapter(BaseDecoderAdapter):

    def __init__(self, static_mode=False):
        super(AMapJsonDecoderAdapter, self).__init__()
        self._static = static_mode

    def get_decoder(self, func_name, *args, **kwargs):
        decoder = self.all_registered_coders[func_name]
        if self._static:
            kwargs['static_mode'] = True

        p_decoder = decoder(*args, **kwargs)
        return p_decoder

    def registry_decoders(self):
        self.registry(self.decode_geo_code, GeoCodeResponseData)
        self.registry(self.decode_regeo_code, ReGeoCodeResponseData)
        self.registry(self.decode_search_text, SearchResponseData)
        self.registry(self.decode_search_around, SearchResponseData)
        self.registry(self.decode_suggest, SuggestResponseData)
        self.registry(self.decode_district, DistrictResponseData)
        self.registry(self.decode_distance, DistanceResponseData)
        self.registry(self.decode_riding, NaviRidingResponseData)
        self.registry(self.decode_walking, NaviWalkingResponseData)
        self.registry(self.decode_driving, NaviDrivingResponseData)
        self.registry(self.decode_batch, BatchResponseData)

    def registry(self, func, coder):
        return super(AMapJsonDecoderAdapter, self).registry(func, coder)

    def decode_geo_code(self, *args, **kwargs):
        return self.get_decoder('decode_geo_code', *args, **kwargs)

    def decode_regeo_code(self, *args, **kwargs):
        return self.get_decoder('decode_regeo_code', *args, **kwargs)

    def decode_search_text(self, *args, **kwargs):
        return self.get_decoder('decode_search_text', *args, **kwargs)

    def decode_search_around(self, *args, **kwargs):
        return self.get_decoder('decode_search_around', *args, **kwargs)

    def decode_suggest(self, *args, **kwargs):
        return self.get_decoder('decode_suggest', *args, **kwargs)

    def decode_district(self, *args, **kwargs):
        return self.get_decoder('decode_district', *args, **kwargs)

    def decode_distance(self, *args, **kwargs):
        return self.get_decoder('decode_distance', *args, **kwargs)

    def decode_riding(self, *args, **kwargs):
        return self.get_decoder('decode_riding', *args, **kwargs)

    def decode_walking(self, *args, **kwargs):
        return self.get_decoder('decode_walking', *args, **kwargs)

    def decode_driving(self, *args, **kwargs):
        return self.get_decoder('decode_driving', *args, **kwargs)

    def decode_batch(self, *args, **kwargs):
        return self.get_decoder('decode_batch', *args, **kwargs)

# coding: utf-8
from __future__ import absolute_import

import logging as _logging

from ._base_model import (
    AMapSig,
    Extensions,
    AMapBaseRequestParams,
    AMapBasePreparedRequestParams,
    AmapBaseResponseData,
)
from ._common_model import (
    Neighborhood,
    StreetNumber,
    BusinessArea,
    Building,
    IndoorData,
    BizExt,
    Photos,
)

from ._geo_code_model import (
    GeoCodeRequestParams,
    PreparedGeoCodeRequestParams,
    GeoCodeResponseData,
    GeoCodeData,
)
from ._regeo_code_model import (
    ReGeoCodeRequestParams,
    PreparedReGeoCodeRequestParams,
    ReGeoCodeResponseData,
    ReGeoCodeData,
)
from ._search_model import (
    SearchTextRequestParams,
    PreparedSearchTextRequestParams,
    SearchAroundRequestParams,
    PreparedSearchAroundRequestParams,
    SearchResponseData,
    SearchSuggestion,
    SearchSuggestionCity,
    SearchData,
)
from ._suggest_model import (
    SuggestRequestParams,
    PreparedSuggestRequestParams,
    SuggestResponseData,
    SuggestData,
)
from ._distance_model import (
    DistanceRequestParams,
    PreparedDistanceRequestParams,
    DistanceResponseData,
    DistanceData,
)
from ._navi_model import (
    NaviRidingRequestParams,
    PreparedNaviRidingRequestParams,
    NaviRidingResponseData,
    NaviRidingData,
    RidingPath,
    RidingSteps,
    NaviWalkingRequestParams,
    PreparedNaviWalkingRequestParams,
    NaviWalkingResponseData,
    NaviWalkingData,
    WalkingPath,
    WalkingSteps,
    NaviDrivingRequestParams,
    PreparedNaviDrivingRequestParams,
    NaviDrivingResponseData,
    NaviDrivingData,
    DrivingPath,
    DrivingSteps,
)
from ._batch_model import (
    BatchRequestParams,
    PreparedBatchParams,
    BatchResponseData,
)

__all__ = [
    # base
    "AMapSig", "AMapBaseRequestParams", "AMapBasePreparedRequestParams",
    "AmapBaseResponseData", "Extensions",
    # batch
    "BatchRequestParams", "PreparedBatchParams", "BatchResponseData",
    # common
    "Neighborhood", "StreetNumber", "BusinessArea", "Building",
    "IndoorData", "BizExt", "Photos",
    # geo_code
    "GeoCodeRequestParams", "PreparedGeoCodeRequestParams",
    "GeoCodeResponseData", "GeoCodeData",
    # re_geo_code
    "ReGeoCodeRequestParams", "PreparedReGeoCodeRequestParams",
    "ReGeoCodeResponseData", "ReGeoCodeData",
    # search
    "SearchTextRequestParams", "PreparedSearchTextRequestParams",
    "SearchAroundRequestParams", "PreparedSearchAroundRequestParams",
    "SearchResponseData", "SearchSuggestion", "SearchSuggestionCity",
    "SearchData",
    # suggest
    "SuggestRequestParams", "PreparedSuggestRequestParams",
    "SuggestResponseData", "SuggestData",
    # distance
    "DistanceRequestParams", "PreparedDistanceRequestParams",
    "DistanceResponseData", "DistanceData",
    # navi-riding
    "NaviRidingRequestParams", "PreparedNaviRidingRequestParams",
    "NaviRidingResponseData", "NaviRidingData", "RidingSteps", "RidingPath",
    # navi-walking
    "NaviWalkingRequestParams", "PreparedNaviWalkingRequestParams",
    "NaviWalkingResponseData", "NaviWalkingData", "WalkingPath",
    "WalkingSteps",
    # navi-driving
    "NaviDrivingRequestParams", "PreparedNaviDrivingRequestParams",
    "NaviDrivingResponseData", "NaviDrivingData", "DrivingPath",
    "DrivingSteps",
    # deprecated module
    "BaseRequestParams", "BasePreparedRequestParams",
]

_TEMPATE = ("'{origin_module}' rename to '{this}' and origin name "
            "will be deprecate and reuse in more basic module, "
            "please import new module: {this}")

_log = _logging.getLogger(__name__)


class BaseRequestParams(AMapBaseRequestParams):
    def __new__(cls, *args, **kwargs):
        _log.warning(_TEMPATE.format(origin_module='BasePreparedRequestParams',
                                     this='AMapBaseRequestParams'))


class BasePreparedRequestParams(AMapBasePreparedRequestParams):
    def __new__(cls, *args, **kwargs):
        _log.warning(_TEMPATE.format(origin_module='BasePreparedRequestParams',
                                     this='AMapBasePreparedRequestParams'))


class BaseResponseData(AmapBaseResponseData):
    def __new__(cls, *args, **kwargs):
        _log.warning(_TEMPATE.format(origin_module='BaseResponseData',
                                     this='AmapBaseResponseData'))


class Sig(AMapSig):
    def __new__(cls, *args, **kwargs):
        _log.warning(_TEMPATE.format(origin_module='Sig', this='AmapSig'))
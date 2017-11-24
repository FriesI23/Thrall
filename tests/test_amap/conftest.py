# coding: utf-8
# flake8: noqa
from __future__ import absolute_import

import re

import responses
import pytest
import py

from thrall.amap.urls import (
    GEO_CODING_URL,
    REGEO_CODING_URL,
    POI_SEARCH_AROUND_URL,
    POI_SEARCH_TEXT_URL,
    POI_SUGGEST_URL,
    DISRANCE_URL,
    NAVI_RIDING_URL,
)


def request_amap_result_dir():
    return py.path.local(__file__).dirpath('mock_data')


@pytest.fixture
def mock_geo_code_result():
    return responses.Response(
        method='GET',
        url=re.compile('{}.*'.format(GEO_CODING_URL.url)),
        body=open(str(
            request_amap_result_dir().join('geo_code_result.json'))).read(),
        status=200,
    )


@pytest.fixture
def mock_regeo_code_result():
    return responses.Response(
        method='GET',
        url=re.compile('{}.*'.format(REGEO_CODING_URL.url)),
        body=open(str(
            request_amap_result_dir().join('regeo_code_result.json'))).read(),
        status=200,
    )


@pytest.fixture
def mock_search_text_result():
    return responses.Response(
        method='GET',
        url=re.compile('{}.*'.format(POI_SEARCH_TEXT_URL.url)),
        body=open(str(
            request_amap_result_dir().join('search_text_result.json'))).read(),
        status=200,
    )


@pytest.fixture
def mock_search_around_result():
    return responses.Response(
        method='GET',
        url=re.compile('{}.*'.format(POI_SEARCH_AROUND_URL.url)),
        body=open(str(
            request_amap_result_dir().join(
                'search_around_result.json'))).read(),
        status=200,
    )


@pytest.fixture
def mock_suggest_result():
    return responses.Response(
        method='GET',
        url=re.compile('{}.*'.format(POI_SUGGEST_URL.url)),
        body=open(str(
            request_amap_result_dir().join('suggest_result.json'))).read(),
        status=200,
    )


@pytest.fixture
def mock_distance_result():
    return responses.Response(
        method='GET',
        url=re.compile('{}.*'.format(DISRANCE_URL.url)),
        body=open(str(
            request_amap_result_dir().join('distance_result.json'))).read(),
        status=200,
    )


@pytest.fixture
def mock_riding_result():
    return responses.Response(
        method='GET',
        url=re.compile('{}.*'.format(NAVI_RIDING_URL.url)),
        body=open(str(
            request_amap_result_dir().join('riding_result.json'))).read(),
        status=200,
    )


@pytest.fixture
def mock_batch_result():
    return responses.Response(
        method='POST',
        url=re.compile('{}.*'.format('http://restapi.amap.com/v3/batch')),
        body=open(str(
            request_amap_result_dir().join('batch_result.json'))).read(),
        status=200,
    )

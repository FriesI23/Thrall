# coding: utf-8
from __future__ import absolute_import

import pytest

from six import iteritems

from thrall.amap.consts import EXTENSION_BASE, EXTENSION_ALL
from thrall.amap._models import _district_model


class TestDistrictRequestParams(object):
    def test_init_ok(self):
        model = _district_model.DistrictRequestParams(keyword='keywords',
                                                      sub_district='sub',
                                                      page='page',
                                                      offset='offset',
                                                      extensions='extensions',
                                                      filter='filter',
                                                      key='yy')

        assert model.keyword == 'keywords'
        assert model.sub_district == 'sub'
        assert model.page == 'page'
        assert model.offset == 'offset'
        assert model.extensions == 'extensions'
        assert model.filter == 'filter'
        assert model.key == 'yy'

    def test_prepare_ok(self):
        model = _district_model.DistrictRequestParams(keyword='xxx', key='key')

        p = model.prepare()

        assert isinstance(p, _district_model.PreparedDistrictRequestParams)

        assert p.keyword is not None
        assert p.key == 'key'


class TestPreparedDistrictRequestParams(object):
    def test_init_ok(self):
        model = _district_model.PreparedDistrictRequestParams()

        assert model.keyword is None

    def test_prepare(self, mocker):
        model = _district_model.PreparedDistrictRequestParams()

        model.prepare_keyword = model.prepare_sub_district = lambda x: None
        model.prepare_page_and_offset = lambda x, y: None
        model.prepare_extensions = model.prepare_filter = lambda x: None
        model.prepare_base = lambda *args, **kwargs: None

        mocker.spy(model, 'prepare_keyword')
        mocker.spy(model, 'prepare_sub_district')
        mocker.spy(model, 'prepare_page_and_offset')
        mocker.spy(model, 'prepare_extensions')
        mocker.spy(model, 'prepare_filter')
        mocker.spy(model, 'prepare_base')

        model.prepare(keyword='keywords',
                      sub_district='sub',
                      page='page',
                      offset='offset',
                      extensions='extensions',
                      filter='filter',
                      key='yy')

        model.prepare_keyword.assert_called_once_with('keywords')
        model.prepare_sub_district.assert_called_once_with('sub')
        model.prepare_page_and_offset.assert_called_once_with('page', 'offset')
        model.prepare_filter.assert_called_once_with('filter')
        model.prepare_extensions.assert_called_once_with('extensions')
        model.prepare_base.assert_called_once_with(key='yy')

    @pytest.mark.parametrize('data, result, presult', [
        ('keyword', 'keyword', 'keyword'), (None, None, None), ('', '', '')
    ])
    def test_prepare_keyword(self, data, result, presult):
        model = _district_model.PreparedDistrictRequestParams()

        model.prepare_keyword(data)

        assert model.keyword == result
        assert model.prepared_keyword == presult

    @pytest.mark.parametrize('data, result, presult', [
        (0, 0, 0), (1, 1, 1), (2, 2, 2), (None, None, None), ('1', 1, 1)
    ])
    def test_prepare_sub_district(self, data, result, presult):
        model = _district_model.PreparedDistrictRequestParams()

        model.prepare_sub_district(data)

        assert model.sub_district == result
        assert model.prepared_sub_district == presult

    def test_prepare_page_and_offset(self):
        model = _district_model.PreparedDistrictRequestParams()

        model.prepare_page_and_offset(1, 1)

        assert model.page == 1
        assert model.offset == 1
        assert model.prepared_page == model.prepared_offset == 1

    def test_prepare_filter(self):
        model = _district_model.PreparedDistrictRequestParams()

        model.prepare_filter('xxx')

        assert model.filter == model.prepared_filter == 'xxx'

    @pytest.mark.parametrize('input, output, p_output', [
        (True, _district_model.ExtensionFlag.ALL, EXTENSION_ALL),
        (False, _district_model.ExtensionFlag.BASE, EXTENSION_BASE),
        (_district_model.ExtensionFlag.BASE,
         _district_model.ExtensionFlag.BASE,
         EXTENSION_BASE),
        (_district_model.ExtensionFlag.ALL,
         _district_model.ExtensionFlag.ALL,
         EXTENSION_ALL),
    ])
    def test_prepare_extensions(self, input, output, p_output):
        model = _district_model.PreparedDistrictRequestParams()

        model.prepare_extensions(input)

        assert model.extensions == output
        assert model.prepared_extensions == p_output

    @pytest.mark.parametrize('input, output', [
        (dict(), dict(key=None)),
        (dict(keyword='kw', key='no'), dict(keywords='kw', key='no')),
        (dict(keyword='keywords', sub_district=1, page=2, offset=10,
              extensions=True, filter=123456, key='yy'),
         dict(keywords='keywords', subdistrict=1, page=2, offset=10,
              extensions='all', filter=123456, key='yy'))
    ])
    def test_generate_params(self, input, output):
        model = _district_model.PreparedDistrictRequestParams()
        model.prepare(**input)

        for k, v in iteritems(output):
            assert model.params[k] == v

        assert len(model.params) == len(output)


class TestDistrictResponseData(object):

    def test_get_data(self):
        raw_data = """{"status":"1","info":"OK","infocode":"10000","count":"1",
        "suggestion":{"keywords":[],"cities":[]},
        "districts":[{"citycode":"010","adcode":"110000","name":"北京市",
        "center":"116.407394,39.904211","level":"province",
        "districts":[{"citycode":"010","adcode":"110100","name":"北京城区",
        "center":"116.407394,39.904211","level":"city","districts":[]}]}]}"""

        model = _district_model.DistrictResponseData(raw_data=raw_data,
                                                     static_mode=True)
        from thrall.amap.consts import StatusFlag
        assert model.status == StatusFlag.OK
        assert isinstance(model.data[0].districts, list)

        assert len(model.data[0].districts) == 1
        assert model.data[0].districts[0].level == 'city'

        assert model.data[0].latitude == 39.904211
        assert model.data[0].longitude == 116.407394

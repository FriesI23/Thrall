# coding: utf-8
# flake8: noqa
import pytest
import responses

from thrall.amap.session import AMapSession, SessionHookMixin
from thrall.amap.adapters import AMapEncodeAdapter, AMapJsonDecoderAdapter
from thrall.amap.request import AMapRequest


class TestHookMixin(object):
    @pytest.mark.parametrize('func_name, prefix, hook', [
        ('mock', 'p', lambda x: 1),
        ('mock_xxx', 'xx', lambda *args: 'xxx')
    ])
    def test_add_hook_with_func_name(self, func_name, prefix, hook):
        model = SessionHookMixin()
        model.add_hook(func_name, prefix, hook)

        assert model.hooks[prefix + '_' + func_name] == hook

    def mock_func(self):
        return

    @pytest.mark.parametrize('func, prefix, hook', [
        (mock_func, 'p', lambda x: 1),
        (mock_func, 'xxxx', lambda x: 222)
    ])
    def test_add_hook_with_func(self, func, prefix, hook):
        model = SessionHookMixin()
        model.add_hook(func, prefix, hook)

        assert model.hooks[prefix + '_' + func.__name__] == hook

    def test_hook_is_not_callable(self):
        model = SessionHookMixin()
        with pytest.raises(TypeError) as e:
            model.add_hook(self.mock_func, 'p', 'xxx')

        assert 'object is not callable' in str(e.value)

    def test_get_hook(self):
        model = SessionHookMixin()
        model.add_hook('xxx', 'p', hook=self.mock_func)
        assert model.get_hook('xxx', 'p') == self.mock_func

    def test_get_no_hook(self):
        model = SessionHookMixin()
        assert model.get_hook('xxx', 'p') == model.DEFAULT_HOOK

    def test_get_hook_overrided(self):
        model = SessionHookMixin()
        oh = lambda x: 1
        model.add_hook('xxx', 'p', self.mock_func)
        assert model.get_hook('xxx', 'p', oh) == oh


class TestAMapSession(object):
    @pytest.mark.parametrize('default_key, default_pkey', [
        ('xxx', 'xxxx'), ('123', '234'), (None, None)
    ])
    def test_init(self, mocker, default_key, default_pkey):
        mocker.spy(AMapSession, 'mount')
        model = AMapSession(default_key=default_key,
                            default_private_key=default_pkey)

        assert model.encoder is not None
        assert model.decoder is not None
        assert model.request is not None
        assert model.brequest is not None

        assert model.mount.call_count == 4

    @pytest.mark.parametrize('schema, coder', [
        ('encode', AMapEncodeAdapter()),
        ('decode', AMapJsonDecoderAdapter()),
        ('request', AMapRequest()),
    ])
    def test_mount(self, schema, coder):
        model = AMapSession()
        model.mount(schema, coder)

        if schema == 'encode':
            assert model.encoder == coder
        elif schema == 'decode':
            assert model.decoder == coder
        elif schema == 'request':
            assert model.request == coder

    @pytest.mark.parametrize('encoder', ['xxx', 123, AMapRequest()])
    def test_mount_error(self, encoder):
        model = AMapSession()
        with pytest.raises(TypeError):
            model.mount('encode', encoder)

    def test_mount_schema_error(self):
        model = AMapSession()
        with pytest.raises(TypeError):
            model.mount('code', AMapEncodeAdapter)

    def test_geo_code(self, mock_geo_code_result):
        with responses.RequestsMock() as rsps:
            rsps.add(mock_geo_code_result)
            result = AMapSession(default_key='xxx').geo_code(address='xxxx')
            result.raise_for_status()

    def test_regeo_code(self, mock_regeo_code_result):
        with responses.RequestsMock() as rsps:
            rsps.add(mock_regeo_code_result)
            result = AMapSession(default_key='xxx').regeo_code(location='1,2')
            result.raise_for_status()

    def test_search_text(self, mock_search_text_result):
        with responses.RequestsMock() as rsps:
            rsps.add(mock_search_text_result)
            result = AMapSession(default_key='xxx').search_text()
            result.raise_for_status()

    def test_search_around(self, mock_search_around_result):
        with responses.RequestsMock() as rsps:
            rsps.add(mock_search_around_result)
            result = AMapSession(default_key='x').search_around(location='1,2')
            result.raise_for_status()

    def test_suggest(self, mock_suggest_result):
        with responses.RequestsMock() as rsps:
            rsps.add(mock_suggest_result)
            result = AMapSession(default_key='x').suggest(keyword='x')
            result.raise_for_status()

    def test_distance(self, mock_distance_result):
        with responses.RequestsMock() as rsps:
            rsps.add(mock_distance_result)
            result = AMapSession(default_key='x').distance(origins='1,2',
                                                           destination='1,2')
            result.raise_for_status()

    def test_riding(self, mock_riding_result):
        with responses.RequestsMock() as rsps:
            rsps.add(mock_riding_result)
            result = AMapSession(default_key='x').riding(origin='1,2',
                                                         destination='1,2')
            result.raise_for_status()

    def test_walking(self, mock_walking_result):
        with responses.RequestsMock() as rsps:
            rsps.add(mock_walking_result)
            result = AMapSession(default_key='x').walking(origin='1,2',
                                                          destination='1,2')
            result.raise_for_status()

    def test_driving(self, mock_driving_result):
        with responses.RequestsMock() as rsps:
            rsps.add(mock_driving_result)
            result = AMapSession(default_key='x').driving(origin='1,2',
                                                          destination='1,2')
            result.raise_for_status()

    def test_batch(self, mock_batch_result):
        from thrall.amap.models import (GeoCodeRequestParams,
                                        ReGeoCodeRequestParams)
        from thrall.amap.session import (BATCH_URL_DEFAULT_PAIRS,
                                         BATCH_DECODE_DEFAULT_PAIRS)
        with responses.RequestsMock() as rsps:
            rsps.add(mock_batch_result)
            result = AMapSession(default_key='x').batch(
                batch_list=[
                    GeoCodeRequestParams(address='xx', key='xxx'),
                    ReGeoCodeRequestParams(location='1,2', key='xss')
                ],
                url_pairs=BATCH_URL_DEFAULT_PAIRS,
                decode_pairs=BATCH_DECODE_DEFAULT_PAIRS,
                key='x'
            )
            result.raise_for_status()

# coding: utf-8
# flake8: noqa
import pytest

from thrall.amap._models import _base_model
from thrall.amap.consts import (StatusFlag, AMapVersion, ExtensionFlag)
from thrall.utils import MapStatusMessage
from thrall.exceptions import AMapStatusError


class TestSig(object):
    def test_sig(self):
        sig = _base_model.Sig('key', kwargs=dict(b=1, a=2, d=4, c=3))

        assert sig.unhash_sig == 'a=2&b=1&c=3&d=4key'
        assert sig.hashed_sig is not None

    def test_repr(self):
        sig = _base_model.Sig('key', kwargs=dict(b=1, a=2, d=4, c=3))

        for i in ['AMapSig(', 'method=OPENSSL_MD5',
                  "sig='a=2&b=1&c=3&d=4key'"]:
            assert i in repr(sig)


class TestExtensions(object):
    def test_init_ok(self):
        model = _base_model.Extensions()

        assert model.status == ExtensionFlag.BASE

        model_2 = _base_model.Extensions(True)

        assert model_2.status == ExtensionFlag.ALL

    def test_optionals(self):
        model = _base_model.Extensions(a=1, b=2, c='3', d=[])

        assert model._flag is False
        assert model.status == ExtensionFlag.BASE
        assert model.a == model._opt_options['a'] == 1
        assert model.b == model._opt_options['b'] == 2
        assert model.c == model._opt_options['c'] == '3'
        assert model.d == model._opt_options['d'] == []


class TestAMapBaseModelNoEmplement(object):
    def test_prepare(self):
        with pytest.raises(NotImplementedError):
            model = _base_model.AMapBaseRequestParams(key='xxx')
            model.prepare()


class TestAMapBasePrepareModelNoEmplement(object):
    def test_generate_params(self):
        with pytest.raises(NotImplementedError):
            model = _base_model.AMapBasePreparedRequestParams()
            model.generate_params()

    def test_prepare(self):
        with pytest.raises(NotImplementedError):
            model = _base_model.AMapBasePreparedRequestParams()
            model.prepare(a=1, b=2)


class TestBasePrepareModel(object):
    class _MockModel(_base_model.AMapBasePreparedRequestParams):

        def generate_params(self):
            with self.init_basic_params({}) as p:
                return p

        def prepare(self, **kwargs):
            self.prepare_base(**kwargs)

    def test_basic(self):
        _base_model.AMapBasePreparedRequestParams()

    def test_repr(self):
        model = self._MockModel()
        model.prepare(key='xxx', output='json', pkey='aaa',
                      raw_params={'a': 1})

        for i in ['_MockModel(', 'key=xxx', 'output=1', 'sig=AMa',
                  "_raw_params={'a': 1}", 'output=json']:
            assert i in repr(model)

    def test_sig(self):
        model = self._MockModel()
        model.prepare_key('xxx')
        model._pkey = 'hahaha'
        model.prepare_output('json')

        assert isinstance(model.sig, _base_model.Sig)

        assert model.sig.private_key == model._pkey
        assert model.sig.unhash_sig == 'key=xxx&output=jsonhahaha'
        assert model.prepared_sig is not None


class TestBaseResponseDataNoImplement(object):
    def test_get_data(self):
        with pytest.raises(NotImplementedError):
            raw_data = """{"status": "1", "info": "OK", "infocode": "10000",
             "count": "1", "geocodes":[]}"""
            model = _base_model.BaseResponseData(raw_data)
            model._get_data()


class TestBaseResponseData(object):
    def test_init_ok(self):
        raw_data = """{"status": "1", "info": "OK", "infocode": "10000",
         "count": "1", "geocodes":[]}"""
        model = _base_model.BaseResponseData(raw_data)
        assert model.status == 1
        assert isinstance(model.status, StatusFlag)
        assert model.status_msg.code == 10000
        assert model.status_msg.msg == 'OK'
        assert model.status_msg.detail == ''
        assert isinstance(model.status_msg, MapStatusMessage)
        assert model.count == 1
        assert model.version == 3

        model.raise_for_status()

    def test_repr(self):
        raw_data = """{"status": "1", "info": "OK", "infocode": "10000",
         "count": "1", "geocodes":[]}"""
        model = _base_model.BaseResponseData(raw_data)

        for i in ['status=', 'status_msg=', 'count=', 'version=']:
            assert i in repr(model)

    def test_init_no_count(self):
        raw_data = """{"status": "1", "info": "OK", "infocode": "10000",
         "geocodes":[]}"""
        model = _base_model.BaseResponseData(raw_data)
        assert model.status == 1
        assert model.status_msg.code == 10000
        assert model.status_msg.msg == 'OK'
        assert model.status_msg.detail == ''
        assert model.version == 3
        assert model.count == 0

        model.raise_for_status()

    def test_init_err(self):
        raw_data = """{"status": "0", "info": "INVALID_USER_KEY",
         "infocode": "10001"}"""
        model = _base_model.BaseResponseData(raw_data)
        assert model.status == 0
        assert model.status_msg.code == 10001
        assert model.status_msg.msg == 'INVALID_USER_KEY'
        assert model.status_msg.detail == ''
        assert model.count == 0
        assert model.version == 3

        with pytest.raises(AMapStatusError):
            model.raise_for_status()

    def test_init_v4_ok(self):
        raw_data = '{"errcode": 0, "errdetail": null, "errmsg": "OK"}'
        model = _base_model.BaseResponseData(raw_data, AMapVersion.V4)
        assert model.status == 1
        assert model.status_msg.code == 0
        assert model.status_msg.msg == 'OK'
        assert model.status_msg.detail is None
        assert model.version == 4
        assert model.count == 0

    def test_init_v4_err(self):
        raw_data = """{"errcode": 30006,
        "errdetail": "您输入的起点信息有误,请检验是否符合接口使用规范",
        "errmsg": "INVALID_PARAMETER_VALUE"}"""
        model = _base_model.BaseResponseData(raw_data, AMapVersion.V4)
        assert model.status == 0
        assert model.status_msg.code == 30006
        assert model.status_msg.msg == 'INVALID_PARAMETER_VALUE'
        assert model.status_msg.detail == u"您输入的起点信息有误,请检验是否符合接口使用规范"
        assert model.count == 0
        assert model.version == 4

    def test_auto_check_version(self):
        raw_data = '{"errcode": 0, "errdetail": null, "errmsg": "OK"}'
        meta_model = _base_model.BaseResponseData

        version = meta_model.auto_check_version(raw_data, AMapVersion.V3)

        assert version == AMapVersion.V4

    def test_auto_check_version_init(self):
        raw_data = """{"status": "1", "info": "OK", "infocode": "10000",
         "count": "1", "geocodes":[]}"""
        model = _base_model.BaseResponseData(raw_data, auto_version=True)
        assert model.status == 1
        assert model.status_msg.code == 10000
        assert model.status_msg.msg == 'OK'
        assert model.status_msg.detail == ''
        assert model.version == 3
        assert model.count == 1

    def test_auto_check_version_v4_init(self):
        raw_data = '{"errcode": 0, "errdetail": null, "errmsg": "OK"}'
        model = _base_model.BaseResponseData(raw_data, auto_version=True)
        assert model.status == 1
        assert model.status_msg.code == 0
        assert model.status_msg.msg == 'OK'
        assert model.status_msg.detail is None
        assert model.version == 4
        assert model.count == 0

    def test_init_with_static_mode(self, mocker):
        class Mock(_base_model.BaseResponseData):
            def get_data(self, raw_data, static=False): return 123

        data = """{"status": "1", "info": "OK", "infocode": "10000",
         "count": "1", "geocodes":[]}"""

        model = Mock(data, static_mode=True)

        mocker.spy(model, '_get_data')

        x = model.data

        assert model._get_data.call_count == 0


class TestLocationMixin(object):
    def test_location(self):
        model = _base_model.LocationMixin()
        model.location = '125,25'

        assert model.latitude == 25.000000
        assert model.longitude == 125.000000

    def test_get_location_err(self):
        model = _base_model.LocationMixin()

        assert model.latitude is None
        assert model.longitude is None

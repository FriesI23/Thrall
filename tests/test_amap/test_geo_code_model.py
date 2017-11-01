# coding: utf-8
# flake8: noqa
import json
import copy

import pytest

from six import iteritems

from thrall.amap._models import _geo_code_model
from thrall.amap.consts import BatchFlag


class TestGeoCodeModel(object):
    def test_request_params(self):
        model = _geo_code_model.GeoCodeRequestParams(address='xx', key='yy')

        assert model.address == 'xx'
        assert model.key == 'yy'

    def test_request_params_no_address(self):
        with pytest.raises(RuntimeError):
            _geo_code_model.GeoCodeRequestParams(address=None, key='x')

        with pytest.raises(RuntimeError):
            _geo_code_model.GeoCodeRequestParams(key='x')

    def test_prepare(self):
        model = _geo_code_model.GeoCodeRequestParams(address='xx', key='yy')
        pm = model.prepare()
        assert isinstance(pm, _geo_code_model.PreparedGeoCodeRequestParams)


class TestGeoCodePrepareModel(object):
    def test_geo_code_init(self):
        model = _geo_code_model.PreparedGeoCodeRequestParams()

        assert model.address == model.city == model.batch == model.key is None



    def test_prepare_single_address(self):
        model = _geo_code_model.PreparedGeoCodeRequestParams()
        model.prepare_address('address')

        assert model.address == ['address']
        assert model.prepared_address == 'address'

    @pytest.mark.parametrize('addresses', [['a', 'b'], ('a', 'b')])
    def test_prepare_list_address(self, addresses):
        model = _geo_code_model.PreparedGeoCodeRequestParams()
        model.prepare_address(addresses)

        assert list(model.address) == ['a', 'b']
        assert model.prepared_address == 'a|b'

    def test_prepare_city(self):
        model = _geo_code_model.PreparedGeoCodeRequestParams()
        model.prepare_city('city')

        assert model.city == 'city'
        assert model.prepared_city == 'city'

    def test_prepare_city_by_code(self):
        model = _geo_code_model.PreparedGeoCodeRequestParams()
        model.prepare_city(123)

        assert model.city == 123
        assert model.prepared_city == '123'

    @pytest.mark.parametrize('flag', [True, BatchFlag.ON])
    def test_prepare_batch(self, flag):
        model = _geo_code_model.PreparedGeoCodeRequestParams()
        model.prepare_batch(flag)

        assert model.batch == 1
        assert isinstance(model.batch, BatchFlag)
        assert model.prepared_batch is True

    @pytest.mark.parametrize('flag', [False, BatchFlag.OFF])
    def test_prepare_batch_false(self, flag):
        model = _geo_code_model.PreparedGeoCodeRequestParams()
        model.prepare_batch(flag)

        assert model.batch == 0
        assert isinstance(model.batch, BatchFlag)
        assert model.prepared_batch is False

    def test_prepare_batch_none(self):
        model = _geo_code_model.PreparedGeoCodeRequestParams()
        model.prepare_batch(None)

        assert model.batch is None
        assert model.prepared_batch is None

    def test_prepare(self):
        model = _geo_code_model.PreparedGeoCodeRequestParams()
        model.prepare(address='abx', key='xxx')

        assert model.address == ['abx']
        assert model.key == 'xxx'

    @pytest.mark.parametrize('kwargs, params', [
        (dict(address='abc', key='xxx', output='json'),
         {'address': 'abc', 'key': 'xxx', 'output': 'json'}),
        (dict(address='abc', city='city', key='xxx', output='json'),
         {'address': 'abc', 'key': 'xxx', 'output': 'json', 'city': 'city'}),
        (dict(address='abc', city=111, key='xxx', output='json'),
         {'address': 'abc', 'key': 'xxx', 'output': 'json', 'city': '111'}),
        (dict(address='abc', city=0, key='xxx', output='json'),
         {'address': 'abc', 'key': 'xxx', 'output': 'json', 'city': '0'}),
        (dict(address='abc', batch=True, key='xxx', output='json'),
         {'address': 'abc', 'key': 'xxx', 'output': 'json', 'batch': True}),
        (dict(address='abc', batch=BatchFlag.OFF, key='xxx', output='json'),
         {'address': 'abc', 'key': 'xxx', 'output': 'json', 'batch': False}),
    ])
    def test_params(self, kwargs, params):
        model = _geo_code_model.PreparedGeoCodeRequestParams()
        model.prepare(**kwargs)

        for k, v in iteritems(params):
            assert model.params[k] == v


class TestGeoCodeResponseData(object):
    RAW_DATA = """
{
    "count": "1",
    "geocodes": [
        {
            "adcode": "310000",
            "building": {
                "name": null,
                "type": null
            },
            "city": "\u4e0a\u6d77\u5e02",
            "citycode": "021",
            "district": null,
            "formatted_address": "\u4e0a\u6d77\u5e02",
            "level": "\u7701",
            "location": "121.473701,31.230416",
            "neighborhood": {
                "name": null,
                "type": null
            },
            "number": null,
            "province": "\u4e0a\u6d77\u5e02",
            "street": null,
            "township": null
        }
    ],
    "info": "OK",
    "infocode": "10000",
    "status": "1"
}
    """
    RAW_DATA_NO_RESULT = """
    {
        "count": "0",
        "geocodes": [],
        "info": "OK",
        "infocode": "10000",
        "status": "1"
    }
        """

    def test_get_data(self):
        model = _geo_code_model.GeoCodeResponseData(self.RAW_DATA)

        assert isinstance(model.data, list)

        for i in model.data:
            assert isinstance(i, _geo_code_model.GeoCodeData)

    def test_get_no_data(self):
        model = _geo_code_model.GeoCodeResponseData(self.RAW_DATA_NO_RESULT)

        assert model.data == []


class TestGeoCodeData(object):
    RAW_DATA = json.loads(TestGeoCodeResponseData.RAW_DATA)['geocodes'][0]

    def test_init(self):
        model = _geo_code_model.GeoCodeData(self.RAW_DATA)
        assert model._data == self.RAW_DATA

    def test_decode_param(self):
        model = _geo_code_model.GeoCodeData(self.RAW_DATA)
        params = copy.deepcopy(model._properties)

        for p in params:
            if p == '_data':
                continue

            if p == 'building':
                assert isinstance(getattr(model, p), _geo_code_model.Building)
            elif p == 'neighborhood':
                assert isinstance(getattr(model, p),
                                  _geo_code_model.Neighborhood)
            else:
                assert self.RAW_DATA[p] == getattr(model, p)

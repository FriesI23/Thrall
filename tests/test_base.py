# coding: utf-8
# flake8: noqa

import pytest
import responses

from requests.sessions import Session

from thrall.exceptions import VendorHTTPError, VendorParamError
from thrall.base import (
    BaseRequest,
    BaseAdapterMixin,
    BaseData,
    BaseRequestParams
)


class TestBaseModelNoEmplement(object):
    def test_prepare(self):
        with pytest.raises(NotImplementedError):
            model = BaseRequestParams(key='xxx')
            model.prepare()


class TestBaseModel(object):
    def test_base_request_params(self):
        model = BaseRequestParams(key='xxx')

        assert model.key == 'xxx'
        assert model.output == model.callback == model.private_key == model._raw_params is None

    def test_base_request_params_no_key(self):
        with pytest.raises(RuntimeError):
            BaseRequestParams(key=None)

        with pytest.raises(RuntimeError):
            BaseRequestParams()

    def test_base_request_catch_vendor_err(self):
        class Mock(BaseRequestParams):
            def prepare_data(self):
                raise VendorParamError('123')

        model = Mock(key='xxx')

        with pytest.raises(VendorParamError) as err:
            model.prepare()

        assert isinstance(err.value.data, model.__class__)
        assert '123' in str(err.value)


class TestBaseRequest(object):
    def test_request_init(self):
        model = BaseRequest()
        assert isinstance(model.session, Session)

    def test_request_init_with_session(self):
        session = Session()

        model = BaseRequest(session=session)

        assert id(model.session) == id(session)

    @responses.activate
    def test_get(self):
        responses.add(
            responses.Response(
                method='GET',
                url='http://example.com',
                status=200,
                json={"a": "a"},
            ),
        )

        model = BaseRequest()
        r = model.get('http://example.com', None)
        assert r.json()['a'] == 'a'

    @responses.activate
    def test_get_with_callback(self):
        responses.add(
            responses.Response(
                method='GET',
                url='http://example.com',
                status=200,
                json={"a": "a"},
            ),
        )

        def call_back(_r):
            assert _r.json()['a'] == 'a'

        model = BaseRequest()
        r = model.get('http://example.com', None, callback=call_back)
        assert r.json()['a'] == 'a'

    @responses.activate
    def test_get_and_raise_status(self):
        responses.add(
            responses.Response(
                method='GET',
                url='http://example.com',
                status=400,
                json={"a": "a"},
            ),
        )

        model = BaseRequest()

        with pytest.raises(VendorHTTPError):
            model.get('http://example.com', None)


class TestBaseData(object):
    def test_init(self):
        raw_data = {'a': 1, 'b': '2', 'c': [], 'd': [1, 2]}

        model = BaseData(raw_data)

        assert model._data == raw_data

    def test_repr(self):
        class MockRepr(BaseData):
            _properties = ('a', 'b', 'c', 'd', 'f')

        model = MockRepr({'a': 1, 'b': '2', 'c': [1], 'd': u'杰克',
                          'f': MockRepr(
                              {'a': 1, 'b': '2', 'c': [1], 'd': u'杰克'})})

        for i in ['MockRepr(', 'a=1', 'b=2', 'c=[1]', 'd=杰克', 'f=MockRepr(']:
            assert i in repr(model)

    def test_get_attr(self, mocker):
        raw_data = {'a': 1, 'b': '2', 'c': [], 'd': [1, 2]}

        model = BaseData(raw_data)
        model._properties = raw_data

        mocker.spy(BaseData, 'decode_param')

        assert model._data
        assert BaseData.decode_param.call_count == 0

        assert model.a == 1
        assert BaseData.decode_param.call_count == 1

        with pytest.raises(AttributeError):
            print(model.xx)

        assert model.c == []
        assert model.d == [1, 2]

    def test_static_data(self, mocker):
        class Mock(BaseData):
            _properties = ('a', 'b', 'c', 'd')

        raw_data = {'a': 1, 'b': '2', 'c': [], 'd': [1, 2]}

        model = Mock(raw_data, static=True)
        model._properties = raw_data

        mocker.spy(model, 'decode_param')

        for i in model._properties:
            hasattr(model, i)

        assert model.a == 1
        assert model.b == '2'
        assert model.c == []
        assert model.d == [1, 2]

        assert model.decode_param.call_count == 0


class TestBaseAdapterMixin(object):
    class MockAdapter(BaseAdapterMixin):
        def mock_coder(self):
            pass

    def mock_coder(self): pass

    def test_init(self):
        mixin = BaseAdapterMixin()

        assert mixin._registered_coders == {}

    def test_registry_ok(self):
        mock_adapter = self.MockAdapter()
        mock_adapter.registry(mock_adapter.mock_coder, 'mock')

        assert mock_adapter.all_registered_coders['mock_coder'] == 'mock'

    def test_registry_unbound(self):
        mock_adapter = self.MockAdapter()
        with pytest.raises(AttributeError):
            mock_adapter.registry(self.mock_coder, 'mock')

    def test_registry_not_fn(self):
        mock_adapter = self.MockAdapter()
        with pytest.raises(AttributeError):
            mock_adapter.registry('mock_coder', 'mock')

    def test_un_registry(self):
        mock_adapter = self.MockAdapter()
        mock_adapter.registry(mock_adapter.mock_coder, 'mock')

        mock_adapter.un_registry(mock_adapter.mock_coder)

        assert mock_adapter.all_registered_coders == {}

    def test_un_registry_with_func_name(self):
        mock_adapter = self.MockAdapter()
        mock_adapter.registry(mock_adapter.mock_coder, 'mock')

        mock_adapter.un_registry('mock_coder')

        assert mock_adapter.all_registered_coders == {}

    def test_un_registry_not_bound(self):
        mock_adapter = self.MockAdapter()
        mock_adapter.registry(mock_adapter.mock_coder, 'mock')

        with pytest.raises(AttributeError):
            mock_adapter.un_registry(self.mock_coder)

    def test_un_registry_not_register(self):
        mock_adapter = self.MockAdapter()

        with pytest.raises(AttributeError):
            mock_adapter.un_registry(mock_adapter.mock_coder)

    def test_un_registry_unknown_str(self):
        mock_adapter = self.MockAdapter()
        mock_adapter.registry(mock_adapter.mock_coder, 'mock')

        with pytest.raises(AttributeError):
            mock_adapter.un_registry('mock_coderss')

    def test_query_ok(self):
        mock_adapter = self.MockAdapter()
        mock_adapter.registry(mock_adapter.mock_coder, 'mock')

        assert mock_adapter.query('mock_coder') == 'mock'
        assert mock_adapter.query(mock_adapter.mock_coder) == 'mock'

    def test_query_err_func_name(self):
        mock_adapter = self.MockAdapter()
        mock_adapter.registry(mock_adapter.mock_coder, 'mock')

        with pytest.raises(AttributeError):
            mock_adapter.query('mock_coderss')

    def test_query_err_unbound_func(self):
        mock_adapter = self.MockAdapter()
        mock_adapter.registry(mock_adapter.mock_coder, 'mock')

        with pytest.raises(AttributeError):
            mock_adapter.query(self.mock_coder())

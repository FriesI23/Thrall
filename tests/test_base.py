# coding: utf-8
# flake8: noqa

from six import iteritems

import pytest
import responses

from requests.sessions import Session

from thrall.exceptions import VendorHTTPError, VendorParamError
from thrall.base import (
    BaseRequest,
    BaseAdapterMixin,
    BaseData,
    BaseRequestParams,
    BasePreparedRequestParams,
)
from thrall.consts import OutputFmt, FORMAT_XML, FORMAT_JSON


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


class TestBasePrepareModelNoEmplement(object):
    def test_generate_params(self):
        with pytest.raises(NotImplementedError):
            model = BasePreparedRequestParams()
            model.generate_params()

    def test_prepare(self):
        with pytest.raises(NotImplementedError):
            model = BasePreparedRequestParams()
            model.prepare(a=1, b=2)


class TestBasePrepareModel(object):
    class _MockModel(BasePreparedRequestParams):

        def generate_params(self):
            with self.init_basic_params({}) as p:
                return p

        def prepare(self, **kwargs):
            self.prepare_base(**kwargs)

    def test_basic(self):
        BasePreparedRequestParams()

    def test_repr(self):
        model = self._MockModel()
        model.prepare(key='xxx', output='json', pkey='aaa',
                      raw_params={'a': 1})

        for i in ['_MockModel(', 'key=xxx', 'output=1', 'sig=',
                  "_raw_params={'a': 1}"]:
            assert i in repr(model)

    def test_prepare_key(self):
        model = BasePreparedRequestParams()

        model.prepare_key('key')
        assert model.key == 'key'
        assert model.prepared_key == 'key'

    @pytest.mark.parametrize(
        'output', ['json', 'Json', 'jSoN', OutputFmt.JSON])
    def test_prepare_output_json(self, output):
        model = BasePreparedRequestParams()

        model.prepare_output(output)
        assert model.output == OutputFmt.JSON
        assert model.prepared_output == 'json'

    @pytest.mark.parametrize(
        'output', ['xml', 'Xml', 'xMl', OutputFmt.XML])
    def test_prepare_output_xml(self, output):
        model = BasePreparedRequestParams()

        model.prepare_output(output)
        assert model.output == OutputFmt.JSON
        assert model.prepared_output == 'json'

    def test_prepare_callback(self):
        try:
            from urlparse import ParseResult
        except ImportError:
            from urllib.parse import ParseResult

        model = BasePreparedRequestParams()

        model.prepare_callback('http://www.google.com')
        assert isinstance(model.callback, ParseResult)

    @pytest.mark.parametrize('kwargs, params', [
        (dict(key='xxx'),
         {'key': 'xxx'}),
        (dict(key='x', output='json', pkey='xxx', callback='http://localhost'),
         {'callback': 'http://localhost', 'key': 'x', 'output': 'json'}),
        (dict(key='x', output='json', callback=None),
         {'key': 'x', 'output': 'json'}),
        (dict(key='x', output='json', callback=None, raw_params={'a': 1}),
         {'key': 'x', 'output': 'json', 'a': 1}),
        (dict(key='x', output='json', callback=None, raw_params={'key': '1'}),
         {'key': '1', 'output': 'json'}),
    ])
    def test_init_basic_params(self, kwargs, params):
        model = self._MockModel()

        model.prepare_base(key=kwargs.get('key'),
                           pkey=kwargs.get('pkey'),
                           output=kwargs.get('output'),
                           callback=kwargs.get('callback'),
                           raw_params=kwargs.get('raw_params'))

        with model.init_basic_params({}) as result:
            for k, v in iteritems(params):
                assert result[k] == v

            assert len(result) == len(params)

        if kwargs.get('pkey'):
            assert model._pkey == kwargs['pkey']

    def test_init_basic_params_with_optionals(self):
        model = self._MockModel()

        model.prepare_base(key='key',
                           pkey='pkey',
                           output='json',
                           callback='http://localhost',
                           raw_params={'xxx': 'yyy', 'hh': None})

        optional_params = {
            'have_it': 1,
            'have_zero': 0,
            'oh_no': None,
            'ept_list': [],
        }

        with model.init_basic_params({}, optional_params) as result:
            pass

        assert result['key'] == 'key'
        assert result['output'] == 'json'
        assert result['callback'] == 'http://localhost'
        assert result['have_it'] == 1
        assert result['have_zero'] == 0
        assert result['ept_list'] == []
        assert result['xxx'] == 'yyy'
        assert 'oh_no' not in result
        assert 'hh' not in result


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

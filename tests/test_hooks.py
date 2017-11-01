# coding: utf-8
# flake8: noqa

from thrall.hooks import _SetDefault, _SetDefaultWithParams, SetD


class TestSetDefault(object):
    @_SetDefault
    def mock(self, **kwargs):
        return kwargs

    @_SetDefault
    def mock2(self, a=1, b=2):
        return a, b

    def test_set_ok(self):
        self.mock.set_default(a=1, b=2)

        r = self.mock(c=3)

        assert r['a'] == 1
        assert r['b'] == 2
        assert r['c'] == 3

    def test_set_default_ok(self):
        self.mock.set_default(a=1, b=3)

        r = self.mock(a=3)

        assert r['a'] == 3
        assert r['b'] == 3

    def test_series_ok(self):
        self.mock.set_default(a=1)

        r = self.mock(a=3)

        assert r['a'] == 3
        assert r.get('b') == 3

    def test_kwargs_override_ok(self):
        self.mock2.set_default(a=3)

        r = self.mock2(b=2)
        assert r == (3, 2)


def test_outside_ok():
    @_SetDefault
    def mock(a=1, b=2):
        return a, b

    mock.set_default(a=3)

    r = mock(a=2, b=2)
    assert r == (2, 2)


class TestSetDefaultWithParams(object):
    @_SetDefaultWithParams(a=1)
    def mock(self, **kwargs):
        return kwargs

    def test_set_ok(self):
        r = self.mock(b=2)

        assert r['a'] == 1
        assert r['b'] == 2

    def test_set_default_ok(self):
        r = self.mock(a=2, b=2)

        assert r['a'] == 2
        assert r['b'] == 2

    def test_tests(self):
        r = self.mock()

        assert r['a'] == 1
        assert r.get('b') is None


class TestSetD(object):
    def test_no_params(self, mocker):
        mocker.spy(_SetDefault, '__init__')
        mocker.spy(_SetDefault, '__call__')
        mocker.spy(_SetDefaultWithParams, '__init__')
        mocker.spy(_SetDefaultWithParams, '__call__')

        @SetD
        def mock(**kwargs): pass

        mock(a=1)

        assert _SetDefault.__init__.call_count == 1
        assert _SetDefault.__call__.call_count == 1
        assert _SetDefaultWithParams.__init__.call_count == 0
        assert _SetDefaultWithParams.__call__.call_count == 0

    def test_wth_params(self, mocker):
        mocker.spy(_SetDefault, '__init__')
        mocker.spy(_SetDefault, '__call__')
        mocker.spy(_SetDefaultWithParams, '__init__')
        mocker.spy(_SetDefaultWithParams, '__call__')

        @SetD(a=1)
        def mock(**kwargs): pass

        mock(a=2)

        assert _SetDefault.__init__.call_count == 0
        assert _SetDefault.__call__.call_count == 0
        assert _SetDefaultWithParams.__init__.call_count == 1
        assert _SetDefaultWithParams.__call__.call_count == 1

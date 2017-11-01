# coding: utf-8
# flake8: noqa
import pytest

from thrall.utils import (
    required_params,
    check_params_type,
    partialmethod,
)


def test_required_params():
    fn = required_params('a', 'b')(lambda a, b: {})

    fn(1, 2)
    fn('', 2)
    fn([], 2)
    fn(1, b=2)
    fn(a=1, b=2)

    with pytest.raises(RuntimeError):
        fn(None, 1)

    with pytest.raises(RuntimeError):
        fn(a=1, b=None)

    with pytest.raises(RuntimeError):
        fn(1, b=None)


def test_required_params_2():
    fn_1 = required_params('a')(lambda a, **kwargs: {})
    fn_2 = required_params('a')(lambda b, **kwargs: {})

    fn_1(1, b=1, c=None)
    fn_1(b=1, c=None, a=1)

    fn_2(1, a=1, c=2)
    fn_2(a=1, b=2, c=None)

    with pytest.raises(RuntimeError):
        fn_2(1, a=None)

    with pytest.raises(RuntimeError):
        fn_2(1, c=3)


def test_check_params_type():
    fn = check_params_type(a=(list, dict))(lambda a, **kwargs: {})

    fn(a=[])
    fn(a={})

    with pytest.raises(TypeError):
        fn(a=1)

    with pytest.raises(TypeError):
        fn(a='')

    with pytest.raises(TypeError):
        fn(a=())


def test_check_params_type_2():
    fn = check_params_type(a=(list, dict))(lambda **kwargs: {})
    fn2 = check_params_type(
        enforce=True, a=(list, dict))(lambda **kwargs: {})

    fn(a=[])
    fn(a={}, b=1)
    fn(b=1)
    fn(a=None)

    with pytest.raises(TypeError):
        fn2(b=1)

    with pytest.raises(TypeError):
        fn2(a=None)


def test_partialmethod():
    class Mock(object):
        def a(self, x=1):
            return x

        b = partialmethod(a, x=2)

    assert Mock().b() == 2

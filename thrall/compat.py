# coding: utf-8
# flake8: noqa
from __future__ import absolute_import

from six import PY2, PY3

if PY3:
    from past.builtins import (
        unicode,
        str,
        basestring as basestring,
        xrange,
        long
    )
    from urllib.parse import urlparse, urlencode
    import builtins as __builtin__
elif PY2:
    from urllib import urlencode
    from urlparse import urlparse
    import __builtin__

    basestring = basestring
    unicode = unicode
    str = str
    xrange = xrange
    long = long

# coding: utf-8
# flake8: noqa
from __future__ import absolute_import

import six

if six.PY3:
    from urllib.parse import urlparse
elif six.PY2:
    from urlparse import urlparse

if six.PY3:
    unicode = str
    xrange = range
elif six.PY2:
    unicode = unicode
    xrange = xrange

if six.PY2:
    import __builtin__
elif six.PY3:
    import builtins as __builtin__

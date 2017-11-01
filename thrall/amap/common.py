# coding: utf-8
import json

from six import iteritems

from thrall.compat import unicode
from thrall.utils import camelcase_to_snakecase, is_list_empty


def parse_multi_address(mixed_addresses):
    u""" split amap multi address by '|'

    >>> parse_multi_address('aaa|bbb')
    [u'aaa', u'bbb']
    >>> parse_multi_address('aaa')
    [u'aaa']
    >>> parse_multi_address(u'中国|美国')
    [u'\\u4e2d\\u56fd', u'\\u7f8e\\u56fd']
    """
    return mixed_addresses.split(u'|')


def merge_multi_address(addresses):
    u"""merge amap multi addresses into single

    >>> merge_multi_address(['aaa', 'bbb'])
    u'aaa|bbb'
    >>> merge_multi_address([u'aaaa'])
    u'aaaa'
    >>> merge_multi_address([u'中国', 'bbb'])
    u'\\u4e2d\\u56fd|bbb'
    >>> merge_multi_address([u'中国', u'美国', u'新加波'])
    u'\\u4e2d\\u56fd|\\u7f8e\\u56fd|\\u65b0\\u52a0\\u6ce2'
    """
    return u'|'.join(addresses)


parse_multi_poi = parse_poi_type = parse_multi_address
merge_multi_poi = merge_poi_type = merge_multi_address


def parse_location(location):
    """ parse amap location to latitude and longitude

    >>> parse_location('111.111,22.22')
    (111.111, 22.22)
    >>> parse_location('111.11111111111, 22.2222222222222222')
    (111.111111, 22.222222)

    :param location: location info, like "123,45"
    :return: latitude, longitude
    """
    longitude, latitude = location.split(',', 1)
    longitude = round(float(longitude), 6)
    latitude = round(float(latitude), 6)
    return longitude, latitude


def merge_location(lng, lat):
    """ merge location to amap str

    >>> merge_location(111.1, 22.22)
    u'111.100000,22.220000'
    >>> merge_location(111.1111112324234234, 22.222222123141251351)
    u'111.111111,22.222222'

    :param lng: longitude,
    :param lat: latitude
    :return formatted location
    """
    return u'%.6f,%.6f' % (lng, lat)


def prepare_multi_locations(location):
    """ prepare locations to lng, lat pairs.

    >>> prepare_multi_locations(None) is None
    True
    >>> prepare_multi_locations('125,25') == [(125, 25)]
    True
    >>> prepare_multi_locations('125,25|111,22') == [(125, 25), (111, 22)]
    True
    >>> prepare_multi_locations((125, 25)) ==  [(125, 25)]
    True
    >>> prepare_multi_locations([(125, 25)]) == [(125, 25)]
    True
    >>> prepare_multi_locations([(111, 11), (222, 22)])\
     == [(111, 11), (222, 22)]
    True
    >>> prepare_multi_locations([(111, 11), "222,22"])\
     == [(111, 11), (222, 22)]
    True
    >>> prepare_multi_locations(["111,11|222,22", (333, 33)])\
     == [(111, 11), (222, 22), (333, 33)]
    True
    >>> prepare_multi_locations(["111,11|222,22", (333, 33), {}])\
     == [(111, 11), (222, 22), (333, 33)]
    True

    :param location: mixed locations
    :return: [(lng, lat), ...]
    """
    if isinstance(location, (str, unicode)):
        _locations = parse_multi_poi(location)
        return [parse_location(loc) for loc in _locations]
    elif isinstance(location, tuple):
        return [location]
    elif isinstance(location, list):
        _tmp = []
        for num, item in enumerate(location):
            if isinstance(item, (str, unicode)):
                _locations = parse_multi_poi(item)
                _tmp.extend((parse_location(j) for j in _locations))
            elif isinstance(item, tuple):
                _tmp.append(item)

        return _tmp


def prepare_multi_string(pois):
    """ prepare pois to list.

    >>> prepare_multi_string(None) is None
    True
    >>> prepare_multi_string('aaa') == ['aaa']
    True
    >>> prepare_multi_string('aaa|bbb') == ['aaa', 'bbb']
    True
    >>> prepare_multi_string(['aaa']) == ['aaa']
    True
    >>> prepare_multi_string(['aaa', 'bbb']) == ['aaa', 'bbb']
    True
    >>> prepare_multi_string(['aaa|ccc', 'bbb']) == ['aaa', 'ccc', 'bbb']
    True
    >>> prepare_multi_string(u'中国|xx') == [u'中国', 'xx']
    True

    :param pois: mixed pois
    :return: ['a', 'b', ...]
    """
    if isinstance(pois, (str, unicode)):
        return parse_poi_type(pois)
    elif isinstance(pois, (tuple, list)):
        _tmp = []
        for num, item in enumerate(pois):
            _pois = parse_multi_poi(item)
            _tmp.extend(j for j in _pois)

        return _tmp


prepare_multi_address = prepare_multi_pois = prepare_multi_string


def json_load_and_fix_amap_empty(raw_data):
    u""" Fix amap json empty value problem

        before: xxx: []
        after: xxx: <`fixed_empty_value`> --> default: None

    >>> json_load_and_fix_amap_empty('{"a": "b", "c": []}')
    {u'a': u'b', u'c': None}
    >>> data = '{"a": {"b": [], "c": {"d": [1], "e": [], "f": {}}}}'
    >>> json_load_and_fix_amap_empty(data)
    {u'a': {u'c': {u'e': None, u'd': [1], u'f': {}}, u'b': None}}
    >>> json_load_and_fix_amap_empty('{"a": "b", "CdE": []}')
    {u'a': u'b', u'cd_e': None}
    """

    def _json_load_hook(obj):
        for k, w in iteritems(obj):
            if is_list_empty(w):
                obj[k] = None

            obj[camelcase_to_snakecase(k)] = obj.pop(k)

        return obj

    return json.loads(raw_data, object_hook=_json_load_hook)

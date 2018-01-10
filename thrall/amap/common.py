# coding: utf-8
import json

from six import iteritems

from thrall.compat import basestring, long
from thrall.utils import camelcase_to_snakecase, is_list_empty


def parse_multi_address(mixed_addresses):
    u""" split amap multi address by '|'

    >>> assert parse_multi_address('aaa|bbb') == [u'aaa', u'bbb']
    >>> assert parse_multi_address('aaa') == [u'aaa']
    >>> assert parse_multi_address(u'中国|美国') == \
    [u'\u4e2d\u56fd', u'\u7f8e\u56fd']
    """
    return mixed_addresses.split(u'|')


def merge_multi_address(addresses):
    u"""merge amap multi addresses into single

    >>> assert merge_multi_address(['aaa', 'bbb']) == u'aaa|bbb'
    >>> assert merge_multi_address([u'aaaa']) == u'aaaa'
    >>> assert merge_multi_address([u'中国', 'bbb']) == u'\u4e2d\u56fd|bbb'
    >>> assert merge_multi_address([u'中国', u'美国', u'新加波']) == \
    u'\u4e2d\u56fd|\u7f8e\u56fd|\u65b0\u52a0\u6ce2'
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

    >>> merge_location(111.1, 22.22) == u'111.100000,22.220000'
    True
    >>> merge_location(111.11111123242, 22.22222212) == u'111.111111,22.222222'
    True

    :param lng: longitude,
    :param lat: latitude
    :return formatted location
    """
    return u'%.6f,%.6f' % (lng, lat)


def merge_multi_locations(locations):
    """ merge multi locations to single string

    >>> merge_multi_locations([(123,34), (12345,67)]) \
    == u'123.000000,34.000000|12345.000000,67.000000'
    True
    >>> merge_multi_locations([(123,34)]) == u'123.000000,34.000000'
    True

    :param locations: locations like: [(lng1, lat1), ...]
    :return: mixed string
    """
    return merge_multi_poi((merge_location(*loc) for loc in locations))


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
    >>> prepare_multi_locations((125.0, 25)) ==  [(125, 25)]
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
    >>> prepare_multi_locations([125, 25]) ==  [(125, 25)]
    True
    >>> prepare_multi_locations([[125, 25]]) == [(125, 25)]
    True
    >>> prepare_multi_locations(["111,11|222,22", [333, 33]])\
     == [(111, 11), (222, 22), (333, 33)]
    True

    :param location: mixed locations
    :return: [(lng, lat), ...]
    """
    if not location:
        return

    if isinstance(location, basestring):
        _locations = parse_multi_poi(location)
        return [parse_location(loc) for loc in _locations]
    else:
        return _prepare_multi_location_from_list(location)


def _prepare_multi_location_from_list(locations):
    tmp_list = []

    for num, data in enumerate(locations):
        if isinstance(data, basestring):
            _locations = parse_multi_poi(data)
            tmp_list.extend((parse_location(j) for j in _locations))
        elif isinstance(data, (int, long, float)):
            return [(data, locations[num + 1]), ]
        elif data:
            tmp_list.append(tuple(data))

    return tmp_list


def prepare_first_location(locations):
    r = prepare_multi_locations(location=locations)
    return r[0] if r else None


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
    if not pois:
        return

    if isinstance(pois, basestring):
        return parse_poi_type(pois)
    else:
        _tmp = []
        for num, item in enumerate(pois):
            _pois = parse_multi_poi(item)
            _tmp.extend(j for j in _pois)

        return _tmp


prepare_multi_address = prepare_multi_pois = prepare_multi_string

_EMPTY_DICT = {}


def json_load_and_fix_amap_empty(raw_data):
    u""" Fix amap json empty value problem

        before: xxx: []
        after: xxx: <`fixed_empty_value`> --> default: None

    >>> x = json_load_and_fix_amap_empty('{"a": "b", "c": []}')
    >>> x['a'] == 'b' and x['c'] is None
    True
    >>> data = '{"a": {"b": [], "c": {"d": [1], "e": [], "f": {}}}}'
    >>> x = json_load_and_fix_amap_empty(data)
    >>> x['a'] is not None and x['a']['b'] is None and x['a']['c'] is not None\
    and x['a']['c']['d'] == [1] and x['a']['c']['e'] is None and \
    x['a']['c']['f'] is None
    True
    >>> x = json_load_and_fix_amap_empty('{"a": "b", "CdE": []}')
    >>> x['a'] == 'b' and x['cd_e'] is None
    True
    """
    def _json_load_hook(obj):
        if obj == _EMPTY_DICT:
            return

        new_obj = {}
        poped_items = []

        for k, w in iteritems(obj):
            if is_list_empty(w):
                obj[k] = None

            renamed_k = camelcase_to_snakecase(k)

            if renamed_k != k:
                new_obj[renamed_k] = obj.get(k)
                poped_items.append(k)

        obj.update(new_obj)

        for i in poped_items:
            obj.pop(i)

        return obj

    return json.loads(raw_data, object_hook=_json_load_hook)

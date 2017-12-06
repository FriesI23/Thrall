# coding: utf-8
from __future__ import absolute_import

from thrall.base import BaseData

from ._base_model import LocationMixin


class Building(BaseData):
    _properties = ('name', 'type')


class Neighborhood(BaseData):
    _properties = ('name', 'type')


class StreetNumber(BaseData, LocationMixin):
    _properties = ('street', 'number', 'location', 'direction', 'distance')


class BusinessArea(BaseData, LocationMixin):
    _properties = ('id', 'name', 'location')


class Children(BaseData, LocationMixin):
    _properties = ('id', 'name', 'sname', 'location', 'address',
                   'distance', 'subtype')


class IndoorData(BaseData):
    _properties = ('cpid', 'floor', 'truefloor')


class BizExt(BaseData):
    _properties = ('rating', 'cost')


class Photos(BaseData):
    _properties = ('title', 'url')

# coding: utf-8
from __future__ import absolute_import

from thrall.base import BaseData


class Building(BaseData):
    _properties = ('name', 'type')


class Neighborhood(BaseData):
    _properties = ('name', 'type')


class StreetNumber(BaseData):
    _properties = ('street', 'number', 'location', 'direction', 'distance')


class BusinessArea(BaseData):
    _properties = ('id', 'name', 'location')


class IndoorData(BaseData):
    _properties = ('cpid', 'floor', 'truefloor')


class BizExt(BaseData):
    _properties = ('rating', 'cost')


class Photos(BaseData):
    _properties = ('title', 'url')

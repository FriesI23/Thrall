# coding: utf-8
from enum import IntEnum


class OutputFmt(IntEnum):
    JSON = 1
    XML = 2


class BatchFlag(IntEnum):
    OFF = 0
    ON = 1

    @property
    def param(self):
        if self == self.ON:
            return 'true'
        else:
            return 'false'


class AMapVersion(IntEnum):
    V3 = 3
    V4 = 4


class StatusFlag(IntEnum):
    ERR = 0
    OK = 1


class ExtensionFlag(IntEnum):
    BASE = 0
    ALL = 1

    @classmethod
    def choose(cls, data):
        if data:
            return cls.ALL
        else:
            return cls.BASE

    @property
    def param(self):
        if self == self.ALL:
            return EXTENSION_ALL
        else:
            return EXTENSION_BASE


class RoadLevel(IntEnum):
    ALL = 0
    DIRECT = 1

    @property
    def param(self):
        return self


class HomeOrCorpControl(IntEnum):
    OFF = 0
    HOME = 1
    CORP = 2

    @classmethod
    def choose(cls, data):
        if data == 0:
            return cls.OFF
        elif data == 1:
            return cls.HOME
        elif data == 2:
            return cls.CORP

    @property
    def param(self):
        return self.value


class SortRule(IntEnum):
    DISTANCE = 0
    WEIGHT = 1

    @classmethod
    def choose(cls, data):
        _d = data.lower()
        if _d == SORT_DISTANCE:
            return cls.DISTANCE
        elif _d == SORT_WEIGHT:
            return cls.WEIGHT

    @property
    def param(self):
        if self == self.WEIGHT:
            return SORT_WEIGHT
        else:
            return SORT_DISTANCE


class CityLimitFlag(IntEnum):
    OFF = 0
    ON = 1

    @classmethod
    def choose(cls, data):
        if data:
            return cls.ON
        else:
            return cls.OFF

    @property
    def param(self):
        if self == self.ON:
            return 'true'
        else:
            return 'false'


class ChildrenFlag(IntEnum):
    OFF = 0
    ON = 1

    @property
    def param(self):
        return self.value


class DataType(IntEnum):
    ALL = 1
    POI = 2
    BUS = 3
    BUSLINE = 4

    @classmethod
    def choose(cls, data):
        _d = data.lower()
        if _d == DATATYPE_ALL:
            return cls.ALL
        elif _d == DATATYPE_BUS:
            return cls.BUS
        elif _d == DATATYPE_BUSLINE:
            return cls.BUSLINE
        elif _d == DATATYPE_POI:
            return cls.POI

    @property
    def param(self):
        if self == self.POI:
            return DATATYPE_POI
        elif self == self.BUSLINE:
            return DATATYPE_BUSLINE
        elif self == self.BUS:
            return DATATYPE_BUS
        else:
            return DATATYPE_ALL


class DistanceType(IntEnum):
    DIRECT = 0
    DRIVING = 1
    BUSLINE = 2
    WALKING = 3

    @classmethod
    def choose(cls, data):
        if data == 0:
            return cls.DIRECT
        elif data == 1:
            return cls.DRIVING
        elif data == 2:
            return cls.BUSLINE
        elif data == 3:
            return cls.WALKING


EXTENSION_BASE = 'base'
EXTENSION_ALL = 'all'

DATATYPE_ALL = 'all'
DATATYPE_POI = 'poi'
DATATYPE_BUS = 'bus'
DATATYPE_BUSLINE = 'busline'

SORT_DISTANCE = 'distance'
SORT_WEIGHT = 'weight'

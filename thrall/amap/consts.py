# coding: utf-8
from enum import IntEnum


class OutputFmt(IntEnum):
    JSON = 1
    XML = 2


class BatchFlag(IntEnum):
    OFF = 0
    ON = 1


class AMapVersion(IntEnum):
    V3 = 3
    V4 = 4


class StatusFlag(IntEnum):
    ERR = 0
    OK = 1


class ExtensionFlag(IntEnum):
    BASE = 0
    ALL = 1


class RoadLevel(IntEnum):
    ALL = 0
    DIRECT = 1


class HomeOrCorpControl(IntEnum):
    OFF = 0
    HOME = 1
    CORP = 2


class CityLimitFlag(IntEnum):
    OFF = 0
    ON = 1


class ChildrenFlag(IntEnum):
    OFF = 0
    ON = 1


EXTENSION_BASE = 'base'
EXTENSION_ALL = 'all'

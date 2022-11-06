from enum import IntEnum
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET

LOGGING_LEVELS = {
    "NotSet": NOTSET,
    "Critical": CRITICAL,
    "Error": ERROR,
    "Warning": WARNING,
    "Info": INFO,
    "Debug": DEBUG,
}


class LogLevel(IntEnum):
    NOTSET = NOTSET
    CRITICAL = CRITICAL
    ERROR = ERROR
    WARNING = WARNING
    INFO = INFO
    DEBUG = DEBUG

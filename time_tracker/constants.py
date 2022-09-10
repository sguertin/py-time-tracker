from enum import IntEnum
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
from os import getenv
from pathlib import Path
from enum import Enum

try:
    WORKING_DIR: Path = Path(getenv("USERPROFILE"), "TimeTracking")
except:
    WORKING_DIR: Path = Path(getenv("HOME"), "TimeTracking")

ACTIVE_ISSUES_FILE: Path = Path(WORKING_DIR, "issues.json")
DELETED_ISSUES_FILE: Path = Path(WORKING_DIR, "deletedIssues.json")


HOUR_RANGE: range = range(24)
MINUTE_RANGE: range = range(60)

DAYS_OF_WEEK = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}
LOGGING_LEVELS = {
    "NotSet": NOTSET,
    "Critical": CRITICAL,
    "Error": ERROR,
    "Warning": WARNING,
    "Info": INFO,
    "Debug": DEBUG,
}

EMPTY = ""


class LogLevel(IntEnum):
    NOTSET = NOTSET
    CRITICAL = CRITICAL
    ERROR = ERROR
    WARNING = WARNING
    INFO = INFO
    DEBUG = DEBUG


class StringEnum(Enum):
    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


class Events(StringEnum):
    ADD = "-ADD-"
    ANOTHER = "-ANOTHER-"
    CANCEL = "-CANCEL-"
    CLOSE = "-CLOSE-"
    OK = "-OK-"
    SAVE = "-SAVE-"
    SKIP = "-SKIP-"
    SUBMIT = "-SUBMIT-"
    REFRESH = "-REFRESH-"
    REMOVE = "-REMOVE-"
    RESTORE = "-RESTORE-"
    RETRY = "-RETRY-"

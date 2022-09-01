from enum import IntEnum
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
from os import getenv
from pathlib import Path

try:
    WORKING_DIR: Path = Path(getenv("USERPROFILE"), "TimeTracking")
except:
    WORKING_DIR: Path = Path(getenv("HOME"), "TimeTracking")

JIRA_NEEDS_AUTH_CODE = 901
JIRA_FAILED_AUTH = 403
JIRA_SUCCESS_RESPONSE = 201

ISSUES_LIST: Path = Path(WORKING_DIR, "issues.json")
DELETED_ISSUES_LIST: Path = Path(WORKING_DIR, "deletedIssues.json")
SETTINGS_FILE: Path = Path(WORKING_DIR, "settings.json")

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


class LogLevel(IntEnum):
    NOTSET = NOTSET
    CRITICAL = CRITICAL
    ERROR = ERROR
    WARNING = WARNING
    INFO = INFO
    DEBUG = DEBUG

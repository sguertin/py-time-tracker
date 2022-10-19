from dataclasses import dataclass, field
from datetime import datetime
from sqlite3 import Time
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from time_tracker.enum import StringEnum
from time_tracker.issue.models import Issue


class TimeEntryResponseDisposition(StringEnum):
    SUCCESS = "success"
    NO_AUTH = "no credentials"
    FAILURE = "failure"


@dataclass(slots=True)
class TimeEntryResponse(DataClassJsonMixin):
    success: bool
    message: Optional[str] = None
    disposition: Optional[TimeEntryResponseDisposition] = None


class TimeEntryKeys(StringEnum):
    COMMENT = "-COMMENT-"
    ENTRY = "-ENTRY-"
    TEXT = "-TEXT-"


class TimeEntryEvents(StringEnum):
    MANAGE_ISSUES = "-MANAGE_ISSUES-"
    REFRESH = "-REFRESH-"
    SKIP = "-SKIP-"
    SUBMIT = "-SUBMIT-"


@dataclass(slots=True)
class TimeEntry(DataClassJsonMixin):
    issue: Issue
    comment: Optional[str] = None


@dataclass(slots=True)
class TimeEntryLog(DataClassJsonMixin):
    date: datetime = field(default_factory=datetime.now)
    entries: list[TimeEntry] = field(default_factory=list)

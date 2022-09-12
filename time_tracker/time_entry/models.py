from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from time_tracker.enum import StringEnum
from time_tracker.issue.models import Issue


class JiraStatusCodes(IntEnum):
    NEEDS_AUTH = 901
    FAILED_AUTH = 403
    SUCCESS = 201


@dataclass(slots=True)
class JiraResponse(DataClassJsonMixin):
    status_code: JiraStatusCodes
    message: Optional[str] = None


class JiraCredentialViewEvents(StringEnum):
    SUBMIT = "-SUBMIT-"
    CANCEL = "-CANCEL-"


class JiraCredentialViewKeys(StringEnum):
    USER = "-USER-"
    PASSWORD = "-PASSWORD-"


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

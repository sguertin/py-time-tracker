from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from time_tracker.enum import StringEnum


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

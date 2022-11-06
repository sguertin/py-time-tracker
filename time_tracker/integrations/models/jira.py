from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from dataclasses_json import DataClassJsonMixin


class JiraStatusCodes(IntEnum):
    NEEDS_AUTH = 901
    FAILED_AUTH = 403
    SUCCESS = 201


@dataclass(slots=True)
class JiraResponse(DataClassJsonMixin):
    status_code: JiraStatusCodes
    message: Optional[str] = None

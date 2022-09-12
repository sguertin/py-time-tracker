from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable

from dataclasses_json import DataClassJsonMixin

from time_tracker.enum import StringEnum
from time_tracker.settings.models import WORKING_DIR

ACTIVE_ISSUES_FILE: Path = WORKING_DIR.joinpath("issues.json")
DELETED_ISSUES_FILE: Path = WORKING_DIR.joinpath("deletedIssues.json")


class NewIssueViewKeys(StringEnum):
    ISSUE = "Issue"
    DESCRIPTION = "Description"
    RESULT = "Result"


class NewIssueViewEvents(StringEnum):
    ANOTHER = "-ANOTHER-"
    CANCEL = "-CANCEL-"
    CLOSE = "-CLOSE-"
    SAVE = "-SAVE-"


class IssueManagementViewKeys(StringEnum):
    ACTIVE_ISSUES = "ActiveIssues"
    DELETED_ISSUES = "DeletedIssues"


class IssueManagementViewEvents(StringEnum):
    CANCEL = "-CANCEL-"
    DELETE = "-DELETE-"
    NEW = "-NEW-"
    RESTORE = "-RESTORE-"
    SAVE = "-SAVE-"


@dataclass(slots=True)
class Issue(DataClassJsonMixin):
    issue_number: str
    description: str
    created: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return f"{self.issue_number} - {self.description}"

    def __ne__(self, issue: "Issue") -> bool:
        return self.issue_number != issue.issue_number

    def __eq__(self, issue: "Issue") -> bool:
        return self.issue_number == issue.issue_number

    def __gt__(self, issue: "Issue") -> bool:
        return self.issue_number > issue.issue_number

    def __gte__(self, issue: "Issue") -> bool:
        return self.issue_number >= issue.issue_number

    def __lt__(self, issue: "Issue") -> bool:
        return self.issue_number < issue.issue_number

    def __lte__(self, issue: "Issue") -> bool:
        return self.issue_number <= issue.issue_number


@dataclass(slots=True)
class IssueList(DataClassJsonMixin):
    filepath: Path
    issues: list[Issue] = field(default_factory=list)
    updated: datetime = field(default_factory=datetime.now)

    def append(self, issue: Issue) -> None:
        self.issues.append(issue)
        self.updated = datetime.now()

    def copy(self):
        return IssueList(self.filepath, self.issues.copy(), self.updated)

    def clear(self):
        self.issues.clear()
        self.updated = datetime.now()

    def count(self, issue: Issue) -> int:
        return self.issues.count(issue)

    def extend(self, issues: Iterable[Issue]):
        self.issues.extend(issues)
        self.updated = datetime.now()

    def index(self, issue: Issue) -> int:
        return self.issues.index(issue)

    def insert(self, index: int, issue: Issue):
        self.issues.insert(index, issue)
        self.updated = datetime.now()

    def pop(self, index: int = None) -> Issue:
        return self.issues.pop(index)

    def remove(self, issue: Issue):
        self.issues.remove(issue)
        self.updated = datetime.now()

    def reverse(self):
        self.issues.reverse()

    def sort(
        self,
        key: Callable[[Issue], None] = None,
        reverse: bool = False,
    ):
        self.issues.sort(key=key, reverse=reverse)

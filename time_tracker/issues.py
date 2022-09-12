from logging import Logger
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Iterable

from dataclasses_json import DataClassJsonMixin
import PySimpleGUI as sg

from time_tracker.constants import (
    ACTIVE_ISSUES_FILE,
    DELETED_ISSUES_FILE,
    EMPTY,
    StringEnum,
)
from time_tracker.logging import LoggingProvider
from time_tracker.prompts import PromptEvents, RetryPrompt


@dataclass(slots=True)
class Issue(DataClassJsonMixin):
    issue_number: str
    description: str
    created: datetime = datetime.now()

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
    issues: list[Issue] = []
    updated: datetime = datetime.now()

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


class IssueService:
    log: Logger

    def __init__(self, log_provider: LoggingProvider):
        self.log = log_provider.get_logger("IssueService")

    def load_list(self, path: Path) -> IssueList:
        try:
            if not path.exists():
                self.log.info(f"Issue List at '{path}' not found, creating new list")
                new_list = IssueList(path)
                with open(path, "w") as f:
                    f.write(new_list.to_json())
                return new_list
            with open(path, "r") as f:
                return IssueList.from_json(f.read(), many=True).issues
        except FileNotFoundError as e:
            self.log.error(e)
            new_list = IssueList(path, [])
            self.save_list(new_list)
            return new_list
        except Exception as e:
            self.log.error(e)
            event = RetryPrompt(
                f"An error occurred while loading {path}\nError: {e}"
            ).run()
            if event == PromptEvents.RETRY:
                return self.load_list(path)

    def load_active_issues(self) -> IssueList:
        return self.load_list(ACTIVE_ISSUES_FILE)

    def load_deleted_issues(self) -> IssueList:
        return self.load_list(DELETED_ISSUES_FILE)

    def load_lists(self) -> tuple[IssueList, IssueList]:
        return self.load_active_issues(), self.load_deleted_issues()

    def save_list(self, issue_list: IssueList, filepath: Path = None) -> IssueList:
        if filepath is None:
            filepath = issue_list.filepath
        try:
            updated_list = IssueList(filepath, issue_list.issues)
            with open(updated_list.filepath, "w") as f:
                f.write(
                    updated_list.to_json(),
                    many=True,
                )
            return updated_list
        except Exception as e:
            self.log.error(e)
            event = RetryPrompt(
                f"An error occurred while saving file '{filepath}'\nError: {e}"
            ).run()
            if event == PromptEvents.RETRY:
                return self.save_list(issue_list, filepath)

    def save_active_list(self, active_list: IssueList) -> IssueList:
        active_list.filepath = ACTIVE_ISSUES_FILE
        return self.save_list(active_list)

    def save_deleted_list(self, deleted_list: IssueList) -> IssueList:
        now = datetime.now()
        deleted_list.filepath = DELETED_ISSUES_FILE
        deleted_list.issues = [
            issue
            for issue in deleted_list.issues
            if now - issue.created >= timedelta(days=30)
        ]
        return self.save_list(deleted_list, DELETED_ISSUES_FILE)

    def save_lists(
        self,
        *issue_lists: tuple[
            IssueList,
        ],
    ) -> set[IssueList]:
        {self.save_list(issue_list) for issue_list in issue_lists}

    def new_issue(self, issue: Issue) -> IssueList:
        active_list = self.load_active_issues()
        active_list.append(issue)
        return self.save_active_list(active_list)


def move_issue(issue: Issue, from_list: IssueList, to_list: IssueList):
    from_list.remove(issue)
    to_list.append(issue)


class NewIssueViewKeys(StringEnum):
    ISSUE = "Issue"
    DESCRIPTION = "Description"
    RESULT = "Result"


class NewIssueViewEvents(StringEnum):
    ANOTHER = "-ANOTHER-"
    CANCEL = "-CANCEL-"
    CLOSE = "-CLOSE-"
    SAVE = "-SAVE-"


class NewIssueView:
    issue_service: IssueService

    def __init__(self, issue_service: IssueService):
        self.issue_service = issue_service
        self.title = "Time Tracking - Add New Entry"
        self.layout = [
            [sg.Text(f"Please provide the Issue information")],
            [
                sg.Text(
                    self.result_text(),
                    key=NewIssueViewKeys.RESULT,
                    visible=False,
                )
            ],
            [sg.Text(f"Issue Number: "), sg.Input(key=NewIssueViewKeys.ISSUE)],
            [
                sg.Text(f"Description:  "),
                sg.Input(key=NewIssueViewKeys.DESCRIPTION),
            ],
            [
                sg.Button("Save", key=NewIssueViewEvents.ANOTHER, bind_return_key=True),
                sg.Button("Save and Close", key=NewIssueViewEvents.SAVE),
                sg.Button("Close", key=NewIssueViewEvents.CLOSE),
            ],
        ]

    def result_text(self, issue: str = "PRODSUP-00000000") -> str:
        return f"Issue {issue} was successfully added"

    def run(self) -> IssueList:
        window = sg.Window(self.title, self.layout)
        while True:
            event, values = window.read(close=True)
            issue = Issue(
                values[NewIssueViewKeys.ISSUE],
                values[NewIssueViewKeys.DESCRIPTION],
            )
            match event:
                case NewIssueViewEvents.ANOTHER:
                    self.issue_service.new_issue(issue)
                    window[NewIssueViewKeys.RESULT].update(self.result_text(issue))
                    window[NewIssueViewKeys.ISSUE].update(EMPTY)
                    window[NewIssueViewKeys.DESCRIPTION].update(EMPTY)
                case NewIssueViewEvents.SAVE:
                    result = self.issue_service.new_issue(issue)
                    window.close()
                    return result
                case NewIssueViewEvents.CANCEL | sg.WIN_CLOSED:
                    window.close()
                    return self.issue_service.load_active_issues()


class IssueManagementViewKeys(StringEnum):
    ACTIVE_ISSUES = "ActiveIssues"
    DELETED_ISSUES = "DeletedIssues"


class IssueManagementViewEvents(StringEnum):
    CANCEL = "-CANCEL-"
    DELETE = "-DELETE-"
    NEW = "-NEW-"
    RESTORE = "-RESTORE-"
    SAVE = "-SAVE-"


class IssueManagementView:
    issue_service: IssueService

    def run(self):
        event = None
        window = sg.Window(self.title, self.layout, size=self.size)
        active_issues, deleted_issues = self.issue_service.load_lists()

        while event not in [
            IssueManagementViewEvents.SAVE,
            IssueManagementViewEvents.CANCEL,
            sg.WIN_CLOSED,
        ]:
            event, values = window.read()
            match event:
                case IssueManagementViewEvents.NEW:
                    active_issues = NewIssueView.run()
                case IssueManagementViewEvents.DELETE:
                    move_issue(
                        issue=values[IssueManagementViewKeys.ACTIVE_ISSUES],
                        from_list=active_issues,
                        to_list=deleted_issues,
                    )
                case IssueManagementViewEvents.RESTORE:
                    active_issues, deleted_issues = self.issue_service.load_lists()
                case IssueManagementViewEvents.SAVE:
                    self.issue_service.save_lists(active_issues, deleted_issues)
                    break
                case IssueManagementViewEvents.CANCEL | sg.WIN_CLOSED:
                    break
            window[IssueManagementViewKeys.ACTIVE_ISSUES].update(active_issues.issues)
            window[IssueManagementViewKeys.DELETED_ISSUES].update(deleted_issues.issues)
            window.refresh()
        window.close()

    def __init__(self, issue_service: IssueService):
        self.issue_service = issue_service
        self.title = "Time Tracking - Manage Issues"
        self.size = (550, 775)
        self.layout = [
            [
                sg.Text("Active Issues", size=(30, 1)),
                sg.Text(EMPTY, size=(5, 1)),
                sg.Text("Deleted Issues", size=(30, 1)),
            ],
            [
                sg.Listbox(
                    issue_service.load_active_issues(),
                    key=IssueManagementViewKeys.ACTIVE_ISSUES,
                    size=(30, 40),
                ),
                sg.Frame(
                    EMPTY,
                    [
                        [
                            sg.Button(
                                " + ",
                                key=IssueManagementViewEvents.NEW,
                                size=(5, 1),
                                tooltip="Create New Issue(s)",
                            )
                        ],
                        [
                            sg.Button(
                                " <- ",
                                key=IssueManagementViewEvents.RESTORE,
                                size=(5, 1),
                                tooltip="Restore Selected Issues",
                            )
                        ],
                        [
                            sg.Button(
                                " -> ",
                                key=IssueManagementViewEvents.DELETE,
                                size=(5, 1),
                                tooltip="Delete Selected Issues",
                            )
                        ],
                    ],
                ),
                sg.Listbox(
                    issue_service.load_deleted_issues(),
                    key=IssueManagementViewKeys.DELETED_ISSUES,
                    size=(30, 40),
                ),
            ],
            [
                sg.Button("Save and Close", key=IssueManagementViewEvents.SAVE),
                sg.Cancel(key=IssueManagementViewEvents.CANCEL),
            ],
        ]


class IssueViewFactory:
    def __init__(self, log_provider: LoggingProvider):
        self.log_provider = log_provider

    def get_issue_view(self):
        if self.issue_service is None:
            self.issue_service = IssueService(self.log_provider)
        return IssueManagementView(self.issue_service)

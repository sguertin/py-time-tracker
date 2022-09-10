from enum import Enum
from logging import Logger
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
import PySimpleGUI as sg
from rich import print

from time_tracker.constants import (
    ACTIVE_ISSUES_FILE,
    DELETED_ISSUES_FILE,
    EMPTY,
    Events,
    StringEnum,
)

from time_tracker.logging import ILoggingFactory
from time_tracker.prompts import RetryPrompt


@dataclass(slots=True)
class Issue(DataClassJsonMixin):
    issue_number: str
    description: str
    disabled: bool = False

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


class IssueService:
    log: Logger

    def __init__(self, log_factory: ILoggingFactory):
        self.log = log_factory.get_logger("IssueService")
        if not ACTIVE_ISSUES_FILE.exists():
            self.log.info(f"Issues list not found, creating new list")
            with open(ACTIVE_ISSUES_FILE, "w") as f:
                f.write(IssueList(ACTIVE_ISSUES_FILE).to_json())

        if not DELETED_ISSUES_FILE.exists():
            self.log.info(f"Deleted Issues list not found, creating new list")
            with open(DELETED_ISSUES_FILE, "w") as f:
                f.write(IssueList(DELETED_ISSUES_FILE).to_json())

    def load_list(self, path: Path) -> list[Issue]:
        try:
            with open(path, "r") as f:
                return IssueList.from_json(f.read(), many=True).issues
        except FileNotFoundError as e:
            self.log.error(e)
            new_list = []
            self.save_list(new_list, path)
            return new_list
        except Exception as e:
            self.log.error(e)
            event = RetryPrompt(
                f"An error occurred while loading {path}\nError: {e}"
            ).run()
            if event == Events.RETRY:
                return self.load_list(path)

    def load_active_issues(self) -> IssueList:
        return self.load_list(ACTIVE_ISSUES_FILE)

    def load_deleted_issues(self) -> IssueList:
        return [
            issue
            for issue in self.load_list(DELETED_ISSUES_FILE)
            if issue.disabled == False
        ]

    def load_lists(self) -> tuple[IssueList, IssueList]:
        return self.load_active_issues(), self.load_deleted_issues()

    def save_list(self, issue_list: IssueList) -> None:
        try:
            with open(issue_list.filepath, "w") as f:
                f.write(issue_list.to_json(), many=True)
        except Exception as e:
            self.log.error(e)
            event = RetryPrompt(
                f"An error occurred while saving {issue_list.filepath}\nError: {e}"
            ).run()
            if event == Events.RETRY:
                return self.save_list(issue_list, issue_list.filepath)

    def save_active_list(self, issues: IssueList) -> None:
        self.save_list(issues, ACTIVE_ISSUES_FILE)

    def save_deleted_list(self, issues: IssueList) -> None:
        self.save_list(issues, DELETED_ISSUES_FILE)

    def save_lists(
        self,
        *issue_lists: tuple[
            IssueList,
        ],
    ) -> None:
        for issue_list in issue_lists:
            self.save_list(issue_list)

    def add_issue(self, issue: Issue) -> IssueList:
        issues_list = self.load_active_issues()
        issues_list.issues.append(issue)
        self.save_list(issues_list)
        return issues_list

    def move_issue(self, issue: Issue, from_list: IssueList, to_list: IssueList):
        from_list.issues.remove(issue)
        to_list.issues.append(issue)
        self.save_lists(from_list, to_list)


class IssueManagementKeys(StringEnum):
    ACTIVE_ISSUES = "ActiveIssues"
    DELETED_ISSUES = "DeletedIssues"


class NewIssueKeys(Enum):
    ISSUE = "Issue"
    DESCRIPTION = "Description"
    RESULT = "Result"


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
                    key=NewIssueKeys.RESULT,
                    visible=False,
                )
            ],
            [sg.Text(f"Issue Number: "), sg.Input(key=NewIssueKeys.ISSUE)],
            [
                sg.Text(f"Description:  "),
                sg.Input(key=NewIssueKeys.DESCRIPTION),
            ],
            [
                sg.Button("Save", key=Events.ANOTHER, bind_return_key=True),
                sg.Button("Save and Close", key=Events.SAVE),
                sg.Button("Close", key=Events.CLOSE),
            ],
        ]

    def result_text(self, issue: str = "PRODSUP-00000000") -> str:
        return f"Issue {issue} was successfully added"

    def run(self) -> list[Issue]:
        window = sg.Window(self.title, self.layout)
        while True:
            event, values = window.read(close=True)
            issue, description = (
                values[NewIssueKeys.ISSUE],
                values[NewIssueKeys.DESCRIPTION],
            )
            match event:
                case Events.ANOTHER:
                    self.issue_service.add_issue(Issue(issue, description))
                    window[NewIssueKeys.RESULT].update(self.result_text(issue))
                case Events.SAVE:
                    result = self.issue_service.add_issue(Issue(issue, description))
                    window.close()
                    return result
                case sg.WIN_CLOSED:
                    return self.issue_service.load_active_issues()
                case Events.CANCEL | Events.SAVE:
                    window.close()
                    return self.issue_service.load_active_issues()


class IssueManagementView:
    issue_service: IssueService
    active_issues: list[Issue]
    deleted_issues: list[Issue]

    def run(self):
        window = sg.Window(self.title, self.layout, size=self.size)
        while True:
            event, _ = window.read()
            match event:
                case Events.ADD:
                    # Show GetIssueInfo view
                    # Update active issues list
                    window[IssueManagementKeys.ACTIVE_ISSUES].update(NewIssueView.run())
                case Events.REMOVE:
                    # Update active issues list
                    # Update deleted issues list
                    print("remove")
                case Events.RESTORE:
                    # Reload active issues list from file
                    # Reload deleted issues list from file
                    pass
                case Events.SAVE:
                    # Save active issues list to file
                    # Save deleted issues list to file
                    window.close()
                    break
                case Events.CANCEL | Events.SAVE:
                    window.close()
                    break

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
                    key=IssueManagementKeys.ACTIVE_ISSUES,
                    size=(30, 40),
                ),
                sg.Frame(
                    EMPTY,
                    [
                        [
                            sg.Button(
                                " + ",
                                key=Events.ADD,
                                size=(5, 1),
                                tooltip="Add New Issue",
                            )
                        ],
                        [
                            sg.Button(
                                " <- ",
                                key=Events.RESTORE,
                                size=(5, 1),
                                tooltip="Restore Selected Issues",
                            )
                        ],
                        [
                            sg.Button(
                                " -> ",
                                key=Events.REMOVE,
                                size=(5, 1),
                                tooltip="Delete Selected Issues",
                            )
                        ],
                    ],
                ),
                sg.Listbox(
                    issue_service.load_deleted_issues(),
                    key=IssueManagementKeys.DELETED_ISSUES,
                    size=(30, 40),
                ),
            ],
            [
                sg.Button("Save and Close", key=Events.SAVE),
                sg.Cancel(key=Events.CANCEL),
            ],
        ]

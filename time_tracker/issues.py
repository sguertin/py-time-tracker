from enum import Enum
from logging import Logger
from dataclasses import dataclass

from dataclasses_json import dataclass_json
import PySimpleGUI as sg

from time_tracker.constants import ISSUES_LIST, DELETED_ISSUES_LIST
from time_tracker.enum import StringEnum
from time_tracker.logging import ILoggingFactory



@dataclass_json
@dataclass(slots=True)
class Issue:
    issue_num: str
    description: str
    disabled: bool = False

    def __str__(self):
        return f"{self.issue_num} - {self.description}"

class IssueService:
    log: Logger

    def __init__(self, log_factory: ILoggingFactory):
        self.log = log_factory.get_logger("IssueService")
        if not ISSUES_LIST.exists():
            self.log.info(f"Issues list not found, creating new list")
            with open(ISSUES_LIST, "w") as f:
                f.write("[]")

        if not DELETED_ISSUES_LIST.exists():
            self.log.info(f"Deleted Issues list not found, creating new list")
            with open(DELETED_ISSUES_LIST, "w") as f:
                f.write("[]")

    def get_issues_list(self) -> list[Issue]:
        with open(ISSUES_LIST, "r") as f:
            return Issue.schema().loads(f.read(), many=True)

    def get_deleted_issues(self) -> list[Issue]:
        with open(DELETED_ISSUES_LIST, "r") as f:
            return Issue.schema().loads(f.read(), many=True)

    def save_issues_list(
        self, issues_list: list[Issue], deleted_issues_list: list[Issue] = None
    ):
        with open(ISSUES_LIST, "w") as f:
            f.write(Issue.schema().dumps(issues_list, many=True))

        if deleted_issues_list:
            with open(DELETED_ISSUES_LIST, "w") as f:
                f.write(Issue.schema().dumps(deleted_issues_list, many=True))

    def add_issue(self, issue: Issue) -> "list[Issue]":
        issues_list = self.get_issues_list()
        issues_list.append(issue)
        self.save_issues_list(issues_list)
        return issues_list

SPACER = ""
class IssueManagementKeys(StringEnum):    
    ACTIVE_ISSUES = "ActiveIssues"
    ADD = "-ADD-"
    CANCEL = "Cancel"
    RESTORE = "-RESTORE-"
    REMOVE = "-REMOVE-"
    DELETED_ISSUES = "DeletedIssues"
    SAVE = "Save"
    
class IssueManagementView:
    
    def run(self):
        window = sg.Window(self.title, self.layout, size=self.size)
        while True:
            event, values = window.read()
            match event:
                case IssueManagementKeys.ADD:
                    # Show GetIssueInfo view                    
                    # Update active issues list                    
                    print("Add")
                case IssueManagementKeys.REMOVE:
                    # Update active issues list
                    # Update deleted issues list
                    print("remove")
                case IssueManagementKeys.RESTORE:
                    # Reload active issues list from file
                    # Reload deleted issues list from file
                    pass
                case IssueManagementKeys.SAVE:
                    # Save active issues list to file
                    # Save deleted issues list to file
                    window.close()
                    break
                case IssueManagementKeys.CANCEL | IssueManagementKeys.SAVE:
                    window.close()
                    break
                
    def __init__(self, active_issues: list[Issue] = [], deleted_issues: list[Issue] = []):
        self.active_issues = active_issues
        self.deleted_issues = deleted_issues
        self.title = "Time Tracking - Manage Issues"
        self.size = (550, 775)        
        self.layout = [
            [
                sg.Text("Active Issues", size=(30, 1)),
                sg.Text(SPACER, size=(5, 1)),
                sg.Text("Deleted Issues", size=(30, 1)),
            ],
            [
                sg.Listbox(active_issues, key=IssueManagementKeys.ACTIVE_ISSUES, size=(30, 40)),
                sg.Frame(
                    SPACER,
                    [
                        [
                            sg.Button(
                                " + ",
                                key=IssueManagementKeys.ADD,
                                size=(5, 1),
                                tooltip="Add New Issue",
                            )
                        ],
                        [
                            sg.Button(
                                " <- ",
                                key=IssueManagementKeys.RESTORE,
                                size=(5, 1),
                                tooltip="Restore Selected Issues",
                            )
                        ],
                        [
                            sg.Button(
                                " -> ",
                                key=IssueManagementKeys.REMOVE,
                                size=(5, 1),
                                tooltip="Delete Selected Issues",
                            )
                        ],
                    ],
                ),
                sg.Listbox(deleted_issues, key=IssueManagementKeys.DELETED_ISSUES, size=(30, 40)),
            ],
            [
                sg.Button("Save and Close", key=IssueManagementKeys.SAVE),
                sg.Cancel(key=IssueManagementKeys.CANCEL),
            ],
        ]
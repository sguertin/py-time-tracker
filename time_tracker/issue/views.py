import PySimpleGUI as sg

from time_tracker.issue.models import (
    Issue,
    IssueList,
    IssueManagementViewEvents,
    IssueManagementViewKeys,
    NewIssueViewEvents,
    NewIssueViewKeys,
)
from time_tracker.issue.services import IssueService
from time_tracker.view import EMPTY, View


class NewIssueView(View):
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
            event, values = window.read()
            issue = Issue(
                values[NewIssueViewKeys.ISSUE],
                values[NewIssueViewKeys.DESCRIPTION],
            )
            match event:
                case NewIssueViewEvents.ANOTHER:
                    result = self.issue_service.new_issue(issue)
                    window[NewIssueViewKeys.RESULT].update(self.result_text(issue))
                    window[NewIssueViewKeys.ISSUE].update(EMPTY)
                    window[NewIssueViewKeys.DESCRIPTION].update(EMPTY)
                case NewIssueViewEvents.SAVE:
                    result = self.issue_service.new_issue(issue)
                    break
                case NewIssueViewEvents.CANCEL | sg.WIN_CLOSED:
                    result = self.issue_service.load_active_issues()
                    break
        window.close()
        return result


class IssueManagementView(View):
    issue_service: IssueService

    def move_issue(self, issue: Issue, from_list: IssueList, to_list: IssueList):
        from_list.remove(issue)
        to_list.append(issue)

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
                    self.move_issue(
                        issue=values[IssueManagementViewKeys.ACTIVE_ISSUES],
                        from_list=active_issues,
                        to_list=deleted_issues,
                    )
                case IssueManagementViewEvents.RESTORE:
                    active_issues, deleted_issues = self.issue_service.load_lists()
                case IssueManagementViewEvents.SAVE:
                    self.issue_service.save_all_lists(active_issues, deleted_issues)
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

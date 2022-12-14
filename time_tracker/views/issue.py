import PySimpleGUI as sg
from time_tracker.constants import EMPTY
from time_tracker.interfaces.issue import IIssueService
from time_tracker.interfaces.views import IView, IViewFactory
from time_tracker.models.issue import (
    Issue,
    IssueList,
    IssueManagementViewEvents,
    IssueManagementViewKeys,
    NewIssueViewEvents,
    NewIssueViewKeys,
)


class NewIssueView(IView):
    issue_service: IIssueService

    def __init__(self, issue_service: IIssueService):
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
        while True:
            window = sg.Window(self.title, self.layout)
            event, values = window.read(close=True)
            issue = Issue(
                values[NewIssueViewKeys.ISSUE],
                values[NewIssueViewKeys.DESCRIPTION],
            )
            match event:
                case [NewIssueViewEvents.ANOTHER]:
                    self.issue_service.new_issue(issue)
                    window[NewIssueViewKeys.RESULT].update(self.result_text(issue))
                    window[NewIssueViewKeys.ISSUE].update(EMPTY)
                    window[NewIssueViewKeys.DESCRIPTION].update(EMPTY)
                case [NewIssueViewEvents.SAVE]:
                    return self.issue_service.new_issue(issue)
                case [NewIssueViewEvents.CANCEL | sg.WIN_CLOSED]:
                    return self.issue_service.load_active_issues()


class IssueManagementView(IView):
    issue_service: IIssueService
    view_factory: IViewFactory

    def move_issue(self, issue: Issue, from_list: IssueList, to_list: IssueList):
        from_list.remove(issue)
        to_list.append(issue)

    def run(self):
        event = None
        window = None
        active_issues, deleted_issues = self.issue_service.load_lists()
        while event not in [
            IssueManagementViewEvents.SAVE,
            IssueManagementViewEvents.CANCEL,
            sg.WIN_CLOSED,
        ]:
            if window is None:
                window = sg.Window(self.title, self.layout, size=self.size)
            window[IssueManagementViewKeys.ACTIVE_ISSUES].update(active_issues.issues)
            window[IssueManagementViewKeys.DELETED_ISSUES].update(deleted_issues.issues)
            event, values = window.read()
            match event:
                case [IssueManagementViewEvents.NEW]:
                    window = window.close()
                    active_issues = self.view_factory.make_new_issue_view().run()
                case [IssueManagementViewEvents.DELETE]:
                    self.move_issue(
                        issue=values[IssueManagementViewKeys.ACTIVE_ISSUES],
                        from_list=active_issues,
                        to_list=deleted_issues,
                    )
                case [IssueManagementViewEvents.RESTORE]:
                    active_issues, deleted_issues = self.issue_service.load_lists()
                case [IssueManagementViewEvents.SAVE]:
                    window = window.close()
                    self.issue_service.save_all_lists(active_issues, deleted_issues)
                    return event
                case [IssueManagementViewEvents.CANCEL | sg.WIN_CLOSED]:
                    return IssueManagementViewEvents.CANCEL

    def __init__(self, issue_service: IIssueService, view_factory: IViewFactory):
        self.issue_service = issue_service
        self.view_factory = view_factory
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

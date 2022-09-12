from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from typing import Optional

from dataclasses_json import DataClassJsonMixin
import PySimpleGUI as sg


from time_tracker.enum import StringEnum
from time_tracker.issue.models import Issue, IssueList
from time_tracker.issue.services import IssueService
from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.view import View


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


class TimeEntryPrompt(View):
    log: Logger
    issue_service: IssueService

    def __init__(self, log_provider: ILoggingProvider):
        self.log = log_provider.get_logger("TimeEntryPrompt")
        self.issue_service = IssueService(log_provider)
        self.title = "Time Tracking Entry"
        self.layout = [
            [
                sg.Text(
                    f"What have you been working on for 00:00 - 00:00?",
                    key=TimeEntryKeys.TEXT,
                )
            ],
            [
                sg.Combo([], key=TimeEntryKeys.ENTRY),
                sg.Button(
                    button_text="Manage Issues", key=TimeEntryEvents.MANAGE_ISSUES
                ),
            ],
            [sg.Text("Comment (Optional): "), sg.In(key=TimeEntryKeys.COMMENT)],
            [
                sg.Submit(key=TimeEntryEvents.SUBMIT),
                sg.Button("Skip", key=TimeEntryEvents.SKIP),
                sg.Button("Refresh", key=TimeEntryEvents.REFRESH),
            ],
        ]

    def run(
        self, from_time: datetime, to_time: datetime
    ) -> tuple[TimeEntryEvents, Optional[TimeEntry]]:
        issue_list = self.issue_service.load_active_issues()
        window = sg.Window(self.title, self.layout)
        window[TimeEntryKeys.TEXT].update(
            f"What have you been working on for "
            + f"{from_time.hour:02}:{from_time.minute:02} - {to_time.hour:02}:{to_time.minute:02}?"
        )
        time_entry = None
        window[TimeEntryKeys.ENTRY].update(issue_list.issues)

        event, values = window.read()
        if event == TimeEntryEvents.SUBMIT:
            time_entry = TimeEntry(
                values[TimeEntryKeys.ENTRY], values[TimeEntryKeys.COMMENT]
            )
        window.close()
        return event, time_entry

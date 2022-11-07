from datetime import datetime
from logging import Logger
from typing import Optional

import PySimpleGUI as sg
from time_tracker.interfaces.issue import IIssueService

from time_tracker.services.issue import IssueService
from time_tracker.views.issue import IssueManagementView
from time_tracker.interfaces.logging import ILoggingProvider
from time_tracker.models.time_entry import (
    TimeEntry,
    TimeEntryKeys,
    TimeEntryEvents,
)
from time_tracker.interfaces.views import ITimeEntryView


class TimeEntryView(ITimeEntryView):
    log: Logger
    issue_service: IssueService

    def __init__(self, log_provider: ILoggingProvider, issue_service: IIssueService):
        self.log_provider = log_provider
        self.log = log_provider.get_logger("TimeEntryPrompt")
        self.issue_service = issue_service
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

        def _make_window(from_time: datetime, to_time: datetime):
            text = (
                f"What have you been working on for "
                + f"{from_time.hour:02}:{from_time.minute:02} - {to_time.hour:02}:{to_time.minute:02}?"
            )
            window = sg.Window(self.title, self.layout)
            window[TimeEntryKeys.TEXT].update(text)
            window[TimeEntryKeys.ENTRY].update(issue_list.issues)
            return window

        time_entry = None
        event = None
        while event not in [
            sg.WIN_CLOSED,
            TimeEntryEvents.SKIP,
            TimeEntryEvents.SUBMIT,
        ]:
            window = _make_window(from_time, to_time)
            event, values = window.read(close=True)
            match event:
                case TimeEntryEvents.SUBMIT:
                    time_entry = TimeEntry(
                        values[TimeEntryKeys.ENTRY],
                        from_time,
                        to_time,
                        values[TimeEntryKeys.COMMENT],
                    )
                case TimeEntryEvents.MANAGE_ISSUES:
                    IssueManagementView(self.issue_service).run()
                case [sg.WIN_CLOSED, TimeEntryEvents.SKIP]:
                    event = TimeEntryEvents.SKIP
        return event, time_entry

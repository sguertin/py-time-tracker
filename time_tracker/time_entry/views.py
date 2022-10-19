from datetime import datetime
from logging import Logger
from typing import Optional

import PySimpleGUI as sg

from time_tracker.issue.services import IssueService
from time_tracker.issue.views import IssueManagementView
from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.time_entry.models import (
    TimeEntry,
    TimeEntryKeys,
    TimeEntryEvents,
)
from time_tracker.view import EMPTY, View


class TimeEntryView(View):
    log: Logger
    issue_service: IssueService

    def __init__(self, log_provider: ILoggingProvider):
        self.log_provider = log_provider
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
        window = sg.Window(self.title, self.layout)
        window[TimeEntryKeys.TEXT].update(
            f"What have you been working on for "
            + f"{from_time.hour:02}:{from_time.minute:02} - {to_time.hour:02}:{to_time.minute:02}?"
        )
        time_entry = None
        event = None
        while event not in [
            sg.WIN_CLOSED,
            TimeEntryEvents.SKIP,
            TimeEntryEvents.SUBMIT,
        ]:
            issue_list = self.issue_service.load_active_issues()
            window[TimeEntryKeys.ENTRY].update(issue_list.issues)
            event, values = window.read()
            if event == TimeEntryEvents.SUBMIT:
                time_entry = TimeEntry(
                    values[TimeEntryKeys.ENTRY],
                    from_time,
                    to_time,
                    values[TimeEntryKeys.COMMENT],
                )
            elif event == TimeEntryEvents.MANAGE_ISSUES:
                IssueManagementView(self.issue_service).run()
        window.close()
        if event == sg.WIN_CLOSED:
            event = TimeEntryEvents.SKIP
        return event, time_entry

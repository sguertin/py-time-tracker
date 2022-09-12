from datetime import datetime

import PySimpleGUI as sg

from time_tracker.enum import StringEnum
from time_tracker.time_entry.services import JiraService
from time_tracker.issue.views import IssueManagementView, IssueService
from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.settings.models import Settings, SettingsViewEvents
from time_tracker.settings.views import SettingsView
from time_tracker.time_entry.views import TimeEntryEvents, TimeEntryView
from time_tracker.view import View

BUTTON_SIZE: tuple[int, int] = (35, 1)


class MenuViewEvents(StringEnum):
    RECORD = "-RECORD-"
    MANAGE = "-MANAGE-"
    THEME = "-THEME-"
    SETTINGS = "-SETTINGS-"
    CLOSE = "-CLOSE-"


class MenuView(View):
    last_recorded: datetime

    @property
    def next_time_entry(self) -> datetime:
        return self.last_recorded + self.settings.time_interval

    def __init__(self, log_provider: ILoggingProvider, settings: Settings):
        self.last_recorded = settings.start_time
        self.settings = settings
        self.log_provider = log_provider
        self.log = log_provider.get_logger("MainMenu")
        self.title = "Time Tracker"
        self.layout = [
            [sg.Button("Record Time Now", key=MenuViewEvents.RECORD, size=BUTTON_SIZE)],
            [sg.Button("Manage Issues", key=MenuViewEvents.MANAGE, size=BUTTON_SIZE)],
            [sg.Button("Settings", key=MenuViewEvents.SETTINGS, size=BUTTON_SIZE)],
            [sg.Button("Close", key=MenuViewEvents.CLOSE, size=BUTTON_SIZE)],
        ]
        if settings.enable_jira:
            self.jira_service = JiraService(log_provider, settings)

    def run(self) -> MenuViewEvents:
        event = None
        while True:
            window = sg.Window(self.title, self.layout)
            event, _ = window.read(timeout=30000)
            self.log.info("Event %s received", event)
            if event == MenuViewEvents.MANAGE:
                event, _ = IssueManagementView(IssueService(self.log_provider)).run()
            elif event == MenuViewEvents.SETTINGS:
                event, settings = SettingsView(self.log_provider, self.settings).run()
                if event == SettingsViewEvents.SAVE:
                    self.settings = settings
                    sg.theme(settings.theme)
                window.close()
                break
                # self.ui_provider.change_settings(self.settings)
            elif event in (sg.WIN_CLOSED, MenuViewEvents.CLOSE):
                window.close()
                break
            elif event in {sg.TIMEOUT_EVENT, sg.TIMEOUT_KEY}:
                self.record_time(self.last_recorded, self.next_time_entry)

            if event == MenuViewEvents.RECORD or datetime.now() >= self.next_time_entry:
                event, entry = TimeEntryView(self.log_provider).run()
                if event == TimeEntryEvents.SUBMIT:
                    # record to file
                    if self.settings.enable_jira:
                        self.jira_service.try_log_work(
                            entry, self.settings.time_interval
                        )
                window.close()
        return event

    def record_time(self, from_time: datetime, to_time: datetime):
        event, entry = TimeEntryView(self.log_provider).run(from_time, to_time)
        if event == TimeEntryEvents.SUBMIT:
            # record to file
            if self.settings.enable_jira:
                self.jira_service.try_log_work(entry, self.settings.time_interval)

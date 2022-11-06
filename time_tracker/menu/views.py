from datetime import datetime

import PySimpleGUI as sg

from time_tracker.issue.views import IssueManagementView, IssueService
from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.menu.models import MenuViewEvents
from time_tracker.settings.models import Settings, SettingsViewEvents
from time_tracker.settings.views import SettingsView
from time_tracker.time_entry.interfaces import ITimeEntryService
from time_tracker.time_entry.views import TimeEntryEvents, TimeEntryView
from time_tracker.view import View

BUTTON_SIZE: tuple[int, int] = (35, 1)


class MenuView(View):
    last_time_entry: datetime

    @property
    def next_time_entry(self) -> datetime:
        return self.last_time_entry + self.settings.time_interval

    def __init__(
        self,
        log_provider: ILoggingProvider,
        time_entry_services: list[ITimeEntryService],
        settings: Settings,
    ):
        self.settings = settings
        self.log_provider = log_provider
        self.time_entry_services = time_entry_services
        self.last_time_entry = settings.start_time
        self.log = log_provider.get_logger(type(self).__name__)
        self.title = "Time Tracker"
        self.layout = [
            [sg.Button("Record Time Now", key=MenuViewEvents.RECORD, size=BUTTON_SIZE)],
            [sg.Button("Manage Issues", key=MenuViewEvents.MANAGE, size=BUTTON_SIZE)],
            [sg.Button("Settings", key=MenuViewEvents.SETTINGS, size=BUTTON_SIZE)],
            [sg.Button("Close", key=MenuViewEvents.CLOSE, size=BUTTON_SIZE)],
        ]

    def run(self) -> MenuViewEvents:
        event = None
        while True:
            window = sg.Window(self.title, self.layout)
            event, _ = window.read(timeout=30000)
            self.log.debug("Event %s received", event)
            window.close()
            if event in (sg.WIN_CLOSED, MenuViewEvents.CLOSE):
                break
            elif event == MenuViewEvents.MANAGE:
                event, _ = IssueManagementView(IssueService(self.log_provider)).run()
            elif event == MenuViewEvents.SETTINGS:
                settings_event, settings = SettingsView(
                    self.log_provider, self.settings
                ).run()
                if settings_event == SettingsViewEvents.SAVE:
                    self.settings = settings
                    sg.theme(settings.theme)
                break
            if event == MenuViewEvents.RECORD:
                time_entry_event, entry = TimeEntryView(self.log_provider).run(
                    self.last_time_entry, datetime.now()
                )
                if time_entry_event == TimeEntryEvents.SUBMIT:
                    self.last_time_entry = datetime.now()
                    for time_entry_service in self.time_entry_services:
                        time_entry_service.log_work(entry)

            if datetime.now() >= self.next_time_entry:
                while self.next_time_entry <= datetime.now():
                    event, entry = TimeEntryView(self.log_provider).run(
                        self.last_time_entry, self.next_time_entry
                    )
                    self.last_time_entry = self.next_time_entry
                    if event == TimeEntryEvents.SUBMIT:
                        for time_entry_service in self.time_entry_services:
                            time_entry_service.log_work(entry)
        return event

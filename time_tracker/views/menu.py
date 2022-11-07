from datetime import datetime

import PySimpleGUI as sg

from time_tracker.interfaces.logging import ILoggingProvider
from time_tracker.models.menu import MenuViewEvents
from time_tracker.models.settings import Settings, SettingsViewEvents
from time_tracker.interfaces.time_entry import ITimeEntryService
from time_tracker.models.time_entry import TimeEntryEvents
from time_tracker.interfaces.views import IView, IViewFactory

BUTTON_SIZE: tuple[int, int] = (35, 1)


class MenuView(IView):
    last_time_entry: datetime

    @property
    def next_time_entry(self) -> datetime:
        return self.last_time_entry + self.settings.time_interval

    def __init__(
        self,
        log_provider: ILoggingProvider,
        time_entry_services: list[ITimeEntryService],
        settings: Settings,
        view_factory: IViewFactory,
    ):
        self.settings = settings
        self.log_provider = log_provider
        self.time_entry_services = time_entry_services
        self.last_time_entry = settings.start_time
        self.log = log_provider.get_logger(type(self).__name__)
        self.view_factory = view_factory
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
            event, _ = window.read(close=True, timeout=30000)
            self.log.debug("Event %s received", event)
            if event in (sg.WIN_CLOSED, MenuViewEvents.CLOSE):
                break
            elif event == MenuViewEvents.MANAGE:
                event, _ = self.view_factory.make_issue_management_view().run()
            elif event == MenuViewEvents.SETTINGS:
                settings_event, settings = self.view_factory.make_settings_view().run()
                if settings_event == SettingsViewEvents.SAVE:
                    self.settings = settings
                    sg.theme(settings.theme)
                break
            if event == MenuViewEvents.RECORD:
                time_entry_event, entry = self.view_factory.make_time_entry_view().run(
                    self.last_time_entry, datetime.now()
                )
                if time_entry_event == TimeEntryEvents.SUBMIT:
                    self.last_time_entry = datetime.now()
                    for time_entry_service in self.time_entry_services:
                        time_entry_service.log_work(entry)

            if datetime.now() >= self.next_time_entry:
                while self.next_time_entry <= datetime.now():
                    event, entry = self.view_factory.make_time_entry_view().run(
                        self.last_time_entry, self.next_time_entry
                    )
                    self.last_time_entry = self.next_time_entry
                    if event == TimeEntryEvents.SUBMIT:
                        for time_entry_service in self.time_entry_services:
                            time_entry_service.log_work(entry)
        return event

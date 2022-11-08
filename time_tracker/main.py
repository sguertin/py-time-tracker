import PySimpleGUI as sg

from time_tracker.factories.issue import IssueServiceFactory
from time_tracker.factories.time_entry import TimeEntryServiceFactory
from time_tracker.factories.views import ViewFactory
from time_tracker.interfaces.issue import IIssueServiceFactory
from time_tracker.interfaces.logging import ILoggingProvider
from time_tracker.interfaces.settings import ISettingsProvider
from time_tracker.interfaces.time_entry import ITimeEntryServiceFactory
from time_tracker.interfaces.views import IViewFactory
from time_tracker.providers.settings import SettingsProvider
from time_tracker.models.menu import MenuViewEvents
from time_tracker.providers.logging import LoggingProvider

settings_provider: ISettingsProvider = SettingsProvider()
settings = settings_provider.get_settings()
log_provider: ILoggingProvider = LoggingProvider(settings)
issue_service_factory: IIssueServiceFactory = IssueServiceFactory(log_provider)
time_entry_service_factory: ITimeEntryServiceFactory = TimeEntryServiceFactory(
    log_provider
)
view_factory: IViewFactory = ViewFactory(
    log_provider, issue_service_factory, time_entry_service_factory
)
log = log_provider.get_logger("Main")
log.info("Starting py-time-tracker...")
running = True

while running:
    menu_view = view_factory.make_menu_view()
    event = menu_view.run(close=True)
    log.info(f"Event: %s received!", event)
    running = event not in [MenuViewEvents.CLOSE, sg.WIN_CLOSED]

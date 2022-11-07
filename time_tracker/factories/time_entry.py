from time_tracker.integrations.services.jira import JiraService
from time_tracker.interfaces.logging import ILoggingProvider
from time_tracker.interfaces.time_entry import (
    ITimeEntryServiceFactory,
    ITimeEntryService,
)
from time_tracker.models.settings import Settings
from time_tracker.services.time_entry import TimeEntryFileService


class TimeEntryServiceFactory(ITimeEntryServiceFactory):
    def __init__(self, log_provider: ILoggingProvider):
        self.log_provider = log_provider

    def make_time_entry_file_service(self) -> ITimeEntryService:
        return TimeEntryFileService(self.log_provider)

    def make_time_entry_jira_service(self) -> ITimeEntryService:
        return JiraService(self.log_provider, Settings.load())

    def make_time_entry_services(self) -> list[ITimeEntryService]:
        return [
            self.make_time_entry_file_service(),
            self.make_time_entry_jira_service(),
        ]

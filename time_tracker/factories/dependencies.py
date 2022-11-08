from time_tracker.factories.issue import IssueServiceFactory
from time_tracker.factories.time_entry import TimeEntryServiceFactory
from time_tracker.factories.views import ViewFactory
from time_tracker.interfaces.logging import ILoggingProvider
from time_tracker.interfaces.views import IViewFactory
from time_tracker.providers.logging import LoggingProvider
from time_tracker.providers.settings import SettingsProvider


class DependencyFactory:
    @staticmethod
    def make_dependencies() -> tuple[IViewFactory, ILoggingProvider]:
        settings_provider = SettingsProvider()
        settings = settings_provider.get_settings()
        log_provider = LoggingProvider(settings)
        issue_service_factory = IssueServiceFactory(log_provider)
        time_entry_service_factory = TimeEntryServiceFactory(log_provider)
        return ViewFactory(
            log_provider, issue_service_factory, time_entry_service_factory
        )

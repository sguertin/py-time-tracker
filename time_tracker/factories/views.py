from time_tracker.interfaces.issue import IIssueServiceFactory
from time_tracker.interfaces.logging import ILoggingProvider
from time_tracker.interfaces.time_entry import ITimeEntryServiceFactory
from time_tracker.interfaces.views import (
    IPromptView,
    IPromptViewFactory,
    ITimeEntryView,
    IUserCredentialView,
    IView,
    IViewFactory,
)
from time_tracker.models.settings import Settings
from time_tracker.views.issue import IssueManagementView, NewIssueView
from time_tracker.views.menu import MenuView
from time_tracker.views.prompt import (
    OkCancelPromptView,
    RetryPromptView,
    UserNamePasswordPrompt,
    WarningPromptView,
)
from time_tracker.views.settings import SettingsView
from time_tracker.views.time_entry import TimeEntryView


class ViewFactory(IViewFactory):
    def __init__(
        self,
        log_provider: ILoggingProvider,
        issue_service_factory: IIssueServiceFactory,
        time_entry_service_factory: ITimeEntryServiceFactory,
    ):
        self.log_provider = log_provider
        self.issue_service = issue_service_factory.make_issue_service()
        self.time_entry_services = time_entry_service_factory.make_time_entry_services()

    def make_issue_management_view(self) -> IView:
        return IssueManagementView(self.issue_service)

    def make_menu_view(self) -> IView:
        return MenuView(
            self.log_provider,
            self.time_entry_services,
            Settings.load(),
        )

    def make_new_issue_view(self) -> IView:
        return NewIssueView(self.issue_service)

    def make_time_entry_view(self) -> ITimeEntryView:
        return TimeEntryView(self.log_provider, self.issue_service)

    def make_settings_view(self) -> IView:
        return SettingsView(self.log_provider, Settings.load())


class PromptViewFactory(IPromptViewFactory):
    def __init__(self, log_provider: ILoggingProvider):
        self.log_provider = log_provider

    def make_ok_cancel_prompt(self, msg: str) -> IPromptView:
        return OkCancelPromptView(msg, self.log_provider)

    def make_warning_prompt(self, msg: str) -> IPromptView:
        return WarningPromptView(msg, self.log_provider)

    def make_retry_prompt(self, msg: str) -> IPromptView:
        return RetryPromptView(msg, self.log_provider)

    def make_user_credential_prompt(
        self, msg: str = "Please provide your username and password"
    ) -> IUserCredentialView:
        return UserNamePasswordPrompt(msg, self.log_provider)

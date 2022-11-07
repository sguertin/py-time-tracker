from time_tracker.interfaces.issue import IIssueService
from time_tracker.interfaces.logging import ILoggingProvider
from time_tracker.services.issue import IssueService


class IssueServiceFactory:
    def __init__(self, log_provider: ILoggingProvider):
        self.log_provider = log_provider

    def make_issue_service(self) -> IIssueService:
        return IssueService(self.log_provider)

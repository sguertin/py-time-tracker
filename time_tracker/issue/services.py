from datetime import datetime, timedelta
from logging import Logger
from pathlib import Path

from time_tracker.issue.interfaces import IIssueService
from time_tracker.issue.models import (
    ACTIVE_ISSUES_FILE,
    DELETED_ISSUES_FILE,
    Issue,
    IssueList,
)
from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.prompts.models import PromptEvents
from time_tracker.prompts.views import RetryPromptView


class IssueService(IIssueService):
    log: Logger

    def __init__(self, log_provider: ILoggingProvider):
        self.log = log_provider.get_logger("IssueService")

    def load_list(self, path: Path) -> IssueList:
        try:
            if not path.exists():
                self.log.info(f"Issue List at '{path}' not found, creating new list")
                new_list = IssueList(path)
                with open(path, "w") as f:
                    f.write(new_list.to_json())
                return new_list
            with open(path, "r") as f:
                return IssueList.from_json(f.read(), many=True).issues
        except FileNotFoundError as e:
            self.log.error(e)
            new_list = IssueList(path, [])
            self.save_list(new_list)
            return new_list
        except Exception as e:
            self.log.error(e)
            event = RetryPromptView(
                f"An error occurred while loading {path}\nError: {e}"
            ).run()
            if event == PromptEvents.RETRY:
                return self.load_list(path)

    def load_active_issues(self) -> IssueList:
        return self.load_list(ACTIVE_ISSUES_FILE)

    def load_deleted_issues(self) -> IssueList:
        return self.load_list(DELETED_ISSUES_FILE)

    def load_lists(self) -> tuple[IssueList, IssueList]:
        return self.load_active_issues(), self.load_deleted_issues()

    def save_list(self, issue_list: IssueList, filepath: Path = None) -> None:
        if filepath is None:
            filepath = issue_list.filepath
        else:
            issue_list.filepath = filepath
        try:
            updated_list = IssueList(filepath, issue_list.issues)
            with open(updated_list.filepath, "w") as f:
                f.write(
                    updated_list.to_json(),
                    many=True,
                )
            updated_list
        except Exception as e:
            self.log.error(e)
            event = RetryPromptView(
                f"An error occurred while saving file '{filepath}'\nError: {e}"
            ).run()
            if event == PromptEvents.RETRY:
                self.save_list(issue_list, filepath)

    def save_active_list(self, active_list: IssueList) -> None:
        active_list.filepath = ACTIVE_ISSUES_FILE
        self.save_list(active_list, ACTIVE_ISSUES_FILE)

    def save_deleted_list(self, deleted_list: IssueList) -> None:
        now = datetime.now()
        deleted_list.filepath = DELETED_ISSUES_FILE
        deleted_list.issues = [
            issue
            for issue in deleted_list.issues
            if now - issue.created >= timedelta(days=30)
        ]
        self.save_list(deleted_list, DELETED_ISSUES_FILE)

    def save_all_lists(
        self, active_issue_list: IssueList, deleted_issue_list: IssueList
    ) -> None:
        self.save_active_list(active_issue_list)
        self.save_deleted_list(deleted_issue_list)

    def new_issue(self, issue: Issue) -> IssueList:
        active_list = self.load_active_issues()
        active_list.append(issue)
        self.save_active_list(active_list)
        return active_list

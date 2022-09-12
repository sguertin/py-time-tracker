from datetime import datetime, timedelta
from logging import Logger
from pathlib import Path


from time_tracker.issues.models import (
    ACTIVE_ISSUES_FILE,
    DELETED_ISSUES_FILE,
    Issue,
    IssueList,
)
from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.prompts import PromptEvents, RetryPrompt


class IssueService:
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
            event = RetryPrompt(
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

    def save_list(self, issue_list: IssueList, filepath: Path = None) -> IssueList:
        if filepath is None:
            filepath = issue_list.filepath
        try:
            updated_list = IssueList(filepath, issue_list.issues)
            with open(updated_list.filepath, "w") as f:
                f.write(
                    updated_list.to_json(),
                    many=True,
                )
            return updated_list
        except Exception as e:
            self.log.error(e)
            event = RetryPrompt(
                f"An error occurred while saving file '{filepath}'\nError: {e}"
            ).run()
            if event == PromptEvents.RETRY:
                return self.save_list(issue_list, filepath)

    def save_active_list(self, active_list: IssueList) -> IssueList:
        active_list.filepath = ACTIVE_ISSUES_FILE
        return self.save_list(active_list)

    def save_deleted_list(self, deleted_list: IssueList) -> IssueList:
        now = datetime.now()
        deleted_list.filepath = DELETED_ISSUES_FILE
        deleted_list.issues = [
            issue
            for issue in deleted_list.issues
            if now - issue.created >= timedelta(days=30)
        ]
        return self.save_list(deleted_list, DELETED_ISSUES_FILE)

    def save_lists(
        self,
        *issue_lists: tuple[
            IssueList,
        ],
    ) -> set[IssueList]:
        {self.save_list(issue_list) for issue_list in issue_lists}

    def new_issue(self, issue: Issue) -> IssueList:
        active_list = self.load_active_issues()
        active_list.append(issue)
        return self.save_active_list(active_list)

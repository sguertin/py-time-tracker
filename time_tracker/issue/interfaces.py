from abc import ABCMeta
from pathlib import Path


from time_tracker.issue.models import (
    Issue,
    IssueList,
)


class IIssueService(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "IIssueService"):
        return (
            (hasattr(subclass, "load_list") and callable(subclass.load_list))
            and (hasattr(subclass, "load_lists") and callable(subclass.load_lists))
            and (
                hasattr(subclass, "load_active_issues")
                and callable(subclass.load_active_issues)
            )
            and (
                hasattr(subclass, "load_deleted_issues")
                and callable(subclass.load_deleted_issues)
            )
            and (hasattr(subclass, "save_list") and callable(subclass.save_list))
            and (hasattr(subclass, "save_lists") and callable(subclass.save_lists))
            and (
                hasattr(subclass, "save_active_issues")
                and callable(subclass.save_active_issues)
            )
            and (
                hasattr(subclass, "save_deleted_issues")
                and callable(subclass.save_deleted_issues)
            )
            and (hasattr(subclass, "new_issue") and callable(subclass.new_issue))
            or NotImplemented
        )

    def load_list(self, path: Path) -> IssueList:
        pass

    def load_active_issues(self) -> IssueList:
        pass

    def load_deleted_issues(self) -> IssueList:
        pass

    def load_lists(self) -> tuple[IssueList, IssueList]:
        pass

    def save_list(self, issue_list: IssueList, filepath: Path = None) -> IssueList:
        pass

    def save_active_issues(self, active_list: IssueList) -> IssueList:
        pass

    def save_deleted_issues(self, deleted_list: IssueList) -> IssueList:
        pass

    def save_lists(
        self,
        *issue_lists: tuple[
            IssueList,
        ],
    ) -> set[IssueList]:
        pass

    def new_issue(self, issue: Issue) -> IssueList:
        pass

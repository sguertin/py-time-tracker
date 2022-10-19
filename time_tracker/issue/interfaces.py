from abc import ABCMeta


from time_tracker.issue.models import (
    Issue,
    IssueList,
)


class IIssueService(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "IIssueService"):
        return (
            (hasattr(subclass, "load_lists") and callable(subclass.load_lists))
            and (
                hasattr(subclass, "load_active_issues")
                and callable(subclass.load_active_issues)
            )
            and (
                hasattr(subclass, "load_deleted_issues")
                and callable(subclass.load_deleted_issues)
            )
            and (
                hasattr(subclass, "save_active_issues")
                and callable(subclass.save_active_issues)
            )
            and (
                hasattr(subclass, "save_deleted_issues")
                and callable(subclass.save_deleted_issues)
            )
            and (
                hasattr(subclass, "save_all_lists")
                and callable(subclass.save_deleted_issues)
            )
            and (hasattr(subclass, "new_issue") and callable(subclass.new_issue))
            or NotImplemented
        )

    def load_active_issues(self) -> IssueList:
        """Loads and returns the active issue list

        Returns:
            IssueList: the active issue list
        """
        raise NotImplementedError(self.load_active_issues)

    def load_deleted_issues(self) -> IssueList:
        """Loads and returns the deleted issue list

        Returns:
            IssueList: the deleted issue list
        """
        raise NotImplementedError(self.load_deleted_issues)

    def load_lists(self) -> tuple[IssueList, IssueList]:
        """Loads and returns the active and deleted issue lists

        Returns:
            tuple[IssueList, IssueList]: The active and deleted issue lists respectively
        """
        raise NotImplementedError(self.load_lists)

    def save_active_issues(self, active_list: IssueList) -> None:
        """Saves the list of issues to the active issues file

        Args:
            active_list (IssueList): The active issue list to save

        """
        raise NotImplementedError(self.save_active_issues)

    def save_deleted_issues(self, deleted_list: IssueList) -> None:
        """Saves the list of issues to the deleted issues file

        Args:
            deleted_list (IssueList): The deleted issue list to save

        """
        raise NotImplementedError(self.save_deleted_issues)

    def save_all_lists(self, active_list: IssueList, deleted_list: IssueList) -> None:
        """Save both the active and deleted issue lists

        Args:
            active_list (IssueList): The list of active issues
            deleted_list (IssueList): The list of deleted issues

        """
        raise NotImplementedError(self.save_all_lists)

    def new_issue(self, issue: Issue) -> IssueList:
        """Add a new issue to the active issue list

        Args:
            issue (Issue): The issue to be added

        Returns:
            IssueList: The updated active issue list
        """
        raise NotImplementedError(self.new_issue)

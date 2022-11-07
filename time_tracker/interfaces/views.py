from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Any, Optional
from time_tracker.models.prompts import PromptEvents
from time_tracker.models.time_entry import TimeEntry, TimeEntryEvents


class IView(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "IView"):
        return (hasattr(subclass, "run") and callable(subclass.run)) or NotImplemented

    @abstractmethod
    def run(self) -> Any:
        raise NotImplementedError(self.run)


class IPromptView(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "IPromptView"):
        return (hasattr(subclass, "run") and callable(subclass.run)) or NotImplemented

    @abstractmethod
    def run(self) -> PromptEvents:
        raise NotImplementedError(self.run)


class IUserCredentialView(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "IUserCredentialView"):
        return (hasattr(subclass, "run") and callable(subclass.run)) or NotImplemented

    @abstractmethod
    def run(self) -> tuple[str, str]:
        raise NotImplementedError(self.run)


class ITimeEntryView(metaclass=ABCMeta):
    title: str
    layout: list
    size: tuple[int, int] = None

    @classmethod
    def __subclasshook__(cls, subclass: "ITimeEntryView"):
        return (hasattr(subclass, "run") and callable(subclass.run)) or NotImplemented

    @abstractmethod
    def run(
        self, from_time: datetime, to_time: datetime
    ) -> tuple[TimeEntryEvents, Optional[TimeEntry]]:
        """Display a view that will capture user input for a time entry

        Args:
            from_time (datetime): the start time for the entry
            to_time (datetime): the end time for the entry

        Returns:
            tuple[TimeEntryEvents, Optional[TimeEntry]]: The user event and an entry if one was provided
        """
        raise NotImplementedError(self.run)


class IViewFactory(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "IViewFactory"):
        return (
            (
                hasattr(subclass, "make_time_entry_view")
                and callable(subclass.make_time_entry_view)
            )
            and (
                hasattr(subclass, "make_new_issue_view")
                and callable(subclass.make_new_issue_view)
            )
            and (
                hasattr(subclass, "make_issue_management_view")
                and callable(subclass.make_issue_management_view)
            )
            and (
                hasattr(subclass, "make_settings_view")
                and callable(subclass.make_settings_view)
            )
            or NotImplemented
        )

    @abstractmethod
    def make_time_entry_view(self) -> ITimeEntryView:
        raise NotImplementedError(self.make_time_entry_view)

    @abstractmethod
    def make_new_issue_view(self) -> IView:
        """Initializes a view for capturing issue information

        Returns:
            IView: the initialized view
        """
        raise NotImplementedError(self.make_new_issue_view)

    @abstractmethod
    def make_issue_management_view(self) -> IView:
        """Initializes a view for managing active and inactive issue lists

        Returns:
            IView: the initialized view
        """
        raise NotImplementedError(self.make_issue_management_view)

    @abstractmethod
    def make_settings_view(self) -> IView:
        """Initializes a view for viewing and editing applications settings

        Returns:
            IView: the initialized view
        """
        raise NotImplementedError(self.make_settings_view)


class IPromptViewFactory:
    @classmethod
    def __subclasshook__(cls, subclass: "IPromptViewFactory"):
        return (
            (
                hasattr(subclass, "make_ok_cancel_prompt")
                and callable(subclass.make_ok_cancel_prompt)
            )
            and (
                hasattr(subclass, "make_warning_prompt")
                and callable(subclass.make_warning_prompt)
            )
            and (
                hasattr(subclass, "make_retry_prompt")
                and callable(subclass.make_retry_prompt)
            )
            and (
                hasattr(subclass, "make_user_credential_prompt")
                and callable(subclass.make_user_credential_prompt)
            )
            or NotImplemented
        )

    @abstractmethod
    def make_ok_cancel_prompt(self, msg: str) -> IPromptView:
        """Initializes a prompt view with a message that gives Ok and Cancel buttons

        Args:
            msg (str): The message to display in the prompt

        Returns:
            PromptView: the initialized prompt view
        """
        raise NotImplementedError(self.make_ok_cancel_prompt)

    @abstractmethod
    def make_warning_prompt(self, msg: str) -> IPromptView:
        """Initializes a prompt view with a message that gives an Ok button

        Args:
            msg (str): The message to display in the prompt

        Returns:
            PromptView: the initialized prompt view
        """
        raise NotImplementedError(self.make_warning_prompt)

    @abstractmethod
    def make_retry_prompt(self, msg: str) -> IPromptView:
        """Initializes a prompt view with a message that gives Retry and Cancel buttons

        Args:
            msg (str): The message to display in the prompt

        Returns:
            PromptView: the initialized prompt view
        """
        raise NotImplementedError(self.make_retry_prompt)

    @abstractmethod
    def make_user_credential_prompt(self, msg: str) -> IUserCredentialView:
        """Initializes a PromptView that allows the user to enter their credentials

        Args:
            msg (str, optional): message to display to the user. Defaults to "Please provide your username and password".

        Returns:
            PromptView: the initialized view
        """
        raise NotImplementedError(self.make_user_credential_prompt)

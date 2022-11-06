from abc import ABCMeta

from time_tracker.models.time_entry import TimeEntry, TimeEntryResponse


class IAuthenticationProvider(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "IAuthenticationProvider"):
        return (
            (hasattr(subclass, "clear_auth") and callable(subclass.clear_auth))
            and (hasattr(subclass, "get_auth") and callable(subclass.get_auth))
            and (hasattr(subclass, "set_auth") and callable(subclass.set_auth))
            or NotImplemented
        )

    def clear_auth(self) -> None:
        """Clears the current stored authentication token"""
        raise NotImplementedError(self.clear_auth)

    def get_auth(self) -> str:
        """Retrieves the authentication token

        Returns:
            str: The authentication token
        """
        raise NotImplementedError(self.get_auth)

    def set_auth(self, user_name: str, password: str) -> None:
        """Generates authentication token from the username and password provided

        Args:
            user_name (str): The username for the token
            password (str): The password for the token

        """
        raise NotImplementedError(self.set_auth)


class ITimeEntryService(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: "ITimeEntryService"):
        return (
            hasattr(subclass, "log_work") and callable(subclass.log_work)
        ) or NotImplemented

    def log_work(self, time_entry: TimeEntry) -> TimeEntryResponse:
        """Creates a work entry log in a time entry system

        Args:
            entry (TimeEntry): The entry to be logged
            from_time (datetime): The starting time of the entry
            to_time (datetime): The end time of the entry

        Returns:
            TimeEntryResponse: The results of the logging call
        """
        raise NotImplementedError(self.log_work)

from abc import ABCMeta
from logging import Logger

from time_tracker.models.logging import LogLevel


class ILoggingProvider(metaclass=ABCMeta):
    log_level: LogLevel

    @classmethod
    def __subclasshook__(cls, subclass: "ILoggingProvider"):
        return (
            (hasattr(subclass, "update_level") and callable(subclass.update_level))
            and (hasattr(subclass, "get_logger") and callable(subclass.get_logger))
            or NotImplemented
        )

    def update_level(self, log_Level: LogLevel) -> None:
        """Updates the level of logging

        Args:
            log_Level (LogLevel): The new log level

        """
        raise NotImplementedError(self.update_level)

    def get_logger(self, name: str) -> Logger:
        """Retrieves the logger for the name provided

        Args:
            name (str): The name of the logger being retrieved

        Returns:
            Logger: The logger with the matching name
        """
        raise NotImplementedError(self.get_logger)

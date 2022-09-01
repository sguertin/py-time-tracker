import logging
from logging import Logger
from abc import ABCMeta, abstractmethod

from rich.logging import RichHandler

from time_tracker.constants import LogLevel


class ILoggingFactory(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            (hasattr(subclass, "get_logger") and callable(subclass.get_logger))
            and (hasattr(subclass, "update_level") and callable(subclass.update_level))
            or NotImplemented
        )

    @abstractmethod
    def get_logger(self, name: str) -> Logger:
        """Retrieves a configured instance of the Logger class with the appropriate name

        Args:
            name (str): The name for the logger

        Returns:
            Logger: The configured logger
        """
        raise NotImplementedError()

    @abstractmethod
    def update_level(self, log_level: LogLevel) -> None:
        """Updates the default log level for the factory

        Args:
            log_level (LogLevel): The new log level to be used as the default

        """
        raise NotImplementedError()

class LoggingFactory(ILoggingFactory):
    _log_level: LogLevel

    def __init__(self, log_level: LogLevel):
        self._log_level = log_level
        logging.basicConfig(
            datefmt="[%Y-%m-%d %H:%M:%S]",
            format="%(name)20s - %(message)s",
            handlers=[RichHandler(rich_tracebacks=True)],
            level=LogLevel.NOTSET,
        )

    def update_level(self, log_Level: LogLevel):
        self._log_level = log_Level

    def get_logger(self, name: str) -> Logger:
        log = logging.getLogger(name)
        log.setLevel(self._log_level)
        return log
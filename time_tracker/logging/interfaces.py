from abc import ABCMeta
from logging import Logger

from time_tracker.logging.models import LogLevel


class ILoggingProvider(metaclass=ABCMeta):
    log_level: LogLevel

    @classmethod
    def __subclasshook__(cls, subclass: "ILoggingProvider"):
        return (
            (hasattr(subclass, "update_level") and callable(subclass.update_level))
            and (hasattr(subclass, "get_logger") and callable(subclass.get_logger))
            or NotImplemented
        )

    def update_level(self, log_Level: LogLevel):
        raise NotImplementedError(self.update_level)

    def get_logger(self, name: str) -> Logger:
        raise NotImplementedError(self.get_logger)

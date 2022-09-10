import logging
from logging import Logger
from abc import ABCMeta, abstractmethod

from rich.logging import RichHandler

from time_tracker.constants import LogLevel


class LoggingProvider:
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

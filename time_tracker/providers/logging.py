import logging
from logging import Logger, FileHandler

from rich.logging import RichHandler
from time_tracker.interfaces.logging import ILoggingProvider

from time_tracker.models.settings import Settings
from time_tracker.models.logging import LogLevel


class LoggingProvider(ILoggingProvider):
    log_level: LogLevel

    def __init__(self, settings: Settings):
        self.log_level = settings.log_level
        handlers = [RichHandler(rich_tracebacks=True)]
        if settings.log_file_path:
            handlers.append(
                FileHandler(str(settings.log_file_path), mode="w+", encoding="utf-8")
            )
        logging.basicConfig(
            datefmt="[%Y-%m-%d %H:%M:%S]",
            format="%(levelname)7s %(date)s - %(name)20s - %(message)s",
            handlers=handlers,
            level=LogLevel.NOTSET,
        )

    def update_level(self, log_Level: LogLevel):
        self.log_level = log_Level

    def get_logger(self, name: str = None) -> Logger:
        """Return a logger with the specified name, creating it if necessary.

        If no name is specified, return the root logger.
        """
        log = logging.getLogger(name)
        log.setLevel(self.log_level)
        return log

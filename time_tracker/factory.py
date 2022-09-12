from time_tracker.logging.provider import LoggingProvider
from time_tracker.settings.models import Settings


class Factory:
    @classmethod
    def settings(cls) -> Settings:
        return Settings.load()

    @classmethod
    def log_provider(cls) -> LoggingProvider:
        return LoggingProvider(cls.settings())

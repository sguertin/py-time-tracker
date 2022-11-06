from dataclasses import dataclass, field
from datetime import timedelta, datetime

from os import getenv
from pathlib import Path

from dataclasses_json import DataClassJsonMixin

from time_tracker.models.enum import StringEnum
from time_tracker.models.logging import LogLevel

try:
    WORKING_DIR: Path = Path(getenv("USERPROFILE"), "TimeTracking")
except:
    WORKING_DIR: Path = Path(getenv("HOME"), "TimeTracking")

SETTINGS_FILE: Path = Path(WORKING_DIR, "settings.json")


@dataclass(slots=True)
class Settings(DataClassJsonMixin):
    theme: str = "DarkBlue3"
    base_url: str = None
    start_hour: int = 8
    start_minute: int = 0
    end_hour: int = 17
    end_minute: int = 0
    interval_hours: int = 1
    interval_minutes: int = 0
    enable_jira: bool = False
    log_level: LogLevel = LogLevel.INFO
    _log_file_path: str = None
    days_of_week: frozenset[int] = field(
        default_factory=lambda: frozenset({0, 1, 2, 3, 4})
    )

    @property
    def log_file_path(self) -> Path:
        if self._log_file_path:
            return Path(self._log_file_path)
        return None

    @property
    def time_interval(self) -> timedelta:
        return timedelta(hours=self.interval_hours, minutes=self.interval_minutes)

    @property
    def start_time(self) -> datetime:
        now = datetime.now()
        if self.start_hour > self.end_hour >= now.hour:
            return datetime(
                now.year, now.day, now.month, self.start_hour, self.start_minute, 0
            ) - timedelta(days=1)
        return datetime(
            now.year, now.day, now.month, self.start_hour, self.start_minute, 0
        )

    @property
    def end_time(self) -> datetime:
        now = datetime.now()
        if self.start_hour > self.end_hour >= now.hour:
            return datetime(
                now.year, now.day, now.month, self.end_hour, self.end_minute, 0
            )
        return datetime(
            now.year, now.day, now.month, self.end_hour, self.end_minute, 0
        ) + timedelta(days=1)

    @property
    def work_day(self) -> timedelta:
        """The duration of a workday

        Returns:
            timedelta: time between start_time and end_time
        """
        return self.end_time - self.start_time

    def __str__(self):
        return self.to_json()

    @classmethod
    def load(cls) -> "Settings":
        try:
            with open(SETTINGS_FILE, "r") as f:
                return cls.from_json(f.read())
        except FileNotFoundError:
            settings = Settings()
            settings.save()
            return settings.save()

    def save(self) -> "Settings":
        try:
            with open(SETTINGS_FILE, "w+") as f:
                f.write(self.to_json())
        except Exception as e:
            return None
        return self


class SettingsViewEvents(StringEnum):
    SAVE = "-SAVE-"
    CANCEL = "-CANCEL-"


class SettingsViewKeys(StringEnum):
    BASE_URL = "-BASE_URL-"
    ENABLE_JIRA = "-ENABLE_JIRA-"
    END_HOUR = "-END_HOUR-"
    END_MINUTE = "-END_MINUTES-"
    INTERVAL_HOURS = "-INTERVAL_HOURS-"
    INTERVAL_MINUTES = "-INTERVAL_MINUTES-"
    LOG_LEVEL = "-LOG_LEVEL-"
    START_HOUR = "-START_HOUR-"
    START_MINUTE = "-START_MINUTES-"
    THEME = "-THEME-"

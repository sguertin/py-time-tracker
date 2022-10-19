from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from time_tracker.time_entry.interfaces import ITimeEntryService
from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.settings.models import Settings, WORKING_DIR
from time_tracker.time_entry.models import TimeEntryLog, TimeEntry, TimeEntryResponse


class MockTimeEntryService(ITimeEntryService):
    def log_work(
        self, entry: TimeEntry, time_interval: Optional[timedelta]
    ) -> TimeEntryResponse:
        return TimeEntryResponse(True)


class TimeEntryFileService(ITimeEntryService):
    settings: Settings

    def __init__(self, log_provider: ILoggingProvider, settings: Settings):
        self.log = log_provider.get_logger("TimeEntryFileService")
        self.settings = settings

    def log_work(self, time_entry: TimeEntry):
        if self.time_entry_file_path.exists():
            with open(self.time_entry_file_path, "r") as f:
                entry_log = TimeEntryLog.from_json(f.read())
        else:
            entry_log = TimeEntryLog()
        entry_log.entries.append(time_entry)
        try:
            with open(self.time_entry_file_path, "w") as f:
                f.write(entry_log.to_json())
        except Exception as e:
            self.log.error(e)

    @property
    def time_entry_file_path(self) -> Path:
        now = datetime.now()
        return WORKING_DIR / f"TimeEntryLog-{now.month:02}-{now.day:02}-{now.year}"

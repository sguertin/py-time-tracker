import PySimpleGUI as sg

from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.logging.models import LOGGING_LEVELS
from time_tracker.settings.models import (
    DAYS_OF_WEEK,
    HOUR_RANGE,
    MINUTE_RANGE,
    Settings,
    SettingsViewKeys,
    SettingsViewEvents,
)
from time_tracker.view import View


class SettingsView(View):
    def __init__(self, log_provider: ILoggingProvider, settings: Settings):
        self.current_settings = settings
        self.log = log_provider.get_logger("SettingsView")
        self.title = f"Settings"
        hours_of_day = [f"{hour:02}" for hour in HOUR_RANGE]
        minutes_of_day = [f"{minute:02}" for minute in MINUTE_RANGE]
        self.layout = (
            [
                [
                    sg.Text("Theme :"),
                    sg.Combo(
                        sg.theme_list(),
                        key=SettingsViewKeys.THEME,
                        default_value=settings.theme,
                    ),
                ],
                [
                    sg.Text("Jira Url (e.g. https://jira.yourcompany.com):"),
                    sg.Input(settings.base_url, key=SettingsViewKeys.BASE_URL),
                ],
                [
                    sg.Text("Start Time of Day:"),
                    sg.Combo(
                        hours_of_day,
                        default_value=settings.start_hour,
                        key=SettingsViewKeys.START_HOUR,
                    ),
                    sg.Text(":"),
                    sg.Combo(
                        minutes_of_day,
                        default_value=settings.start_minute,
                        key=SettingsViewKeys.START_MINUTE,
                    ),
                ],
                [
                    sg.Text("End Time of Day:"),
                    sg.Combo(
                        hours_of_day,
                        default_value=settings.end_hour,
                        key=SettingsViewKeys.END_HOUR,
                    ),
                    sg.Text(":"),
                    sg.Combo(
                        minutes_of_day,
                        default_value=settings.end_minute,
                        key=SettingsViewKeys.END_MINUTE,
                    ),
                ],
                [
                    sg.Text("Time Recording Interval:"),
                    sg.Combo(
                        [0, 1, 2, 3, 4, 5, 6, 7, 8], key=SettingsViewKeys.INTERVAL_HOURS
                    ),
                    sg.Text("h "),
                    sg.Combo(
                        ["00", "15", "30", "45"], key=SettingsViewKeys.INTERVAL_MINUTES
                    ),
                    sg.Text("m"),
                ],
                [sg.Checkbox("Enable Jira", key=SettingsViewKeys.ENABLE_JIRA)],
                [
                    sg.Checkbox(day, key=day, default=number in settings.days_of_week)
                    for day, number in DAYS_OF_WEEK.items()
                ],
                [
                    sg.Text("Logging Level:"),
                    sg.Combo(
                        [level for level in LOGGING_LEVELS.keys()],
                        key=SettingsViewKeys.LOG_LEVEL,
                    ),
                ][
                    sg.Button("Save", key=SettingsViewEvents.SAVE),
                    sg.Cancel("Cancel", key=SettingsViewEvents.CANCEL),
                ],
            ],
        )

    def run(self) -> tuple[SettingsViewEvents, Settings]:
        window = sg.Window(title=self.title, layout=self.layout)
        while True:
            event, values = window.read(close=True)
            self.log.debug("Event %s received", event)
            if event == SettingsViewEvents.SAVE:
                new_settings = Settings(
                    base_url=values[SettingsViewKeys.BASE_URL],
                    days_of_week=frozenset(
                        number
                        for day, number in DAYS_OF_WEEK.items()
                        if values[day] == True
                    ),
                    end_hour=values[SettingsViewKeys.END_HOUR],
                    end_minute=values[SettingsViewKeys.END_MINUTE],
                    enable_jira=values[SettingsViewKeys.ENABLE_JIRA],
                    interval_hours=values[SettingsViewKeys.INTERVAL_HOURS],
                    interval_minutes=values[SettingsViewKeys.INTERVAL_MINUTES],
                    log_level=LOGGING_LEVELS[values[SettingsViewKeys.LOG_LEVEL]],
                    start_hour=values[SettingsViewKeys.START_HOUR],
                    start_minute=values[SettingsViewKeys.START_MINUTE],
                    theme=values[SettingsViewKeys.THEME],
                ).save()
                return event, new_settings
            return event, None

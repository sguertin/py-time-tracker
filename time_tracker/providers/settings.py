from time_tracker.models.settings import Settings


class SettingsProvider:
    def __init__(self):
        self.settings = None

    def get_settings(self) -> Settings:
        if self.settings is None:
            self.settings = Settings.load()
        else:
            return self.settings

from time_tracker.models.enums import StringEnum


BUTTON_SIZE: tuple[int, int] = (35, 1)


class MenuViewEvents(StringEnum):
    RECORD = "-RECORD-"
    MANAGE = "-MANAGE-"
    THEME = "-THEME-"
    SETTINGS = "-SETTINGS-"
    CLOSE = "-CLOSE-"

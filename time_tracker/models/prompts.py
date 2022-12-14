from time_tracker.models.enums import StringEnum


class PromptEvents(StringEnum):
    OK = "-OK-"
    CANCEL = "-CANCEL-"
    CLOSE = "-CLOSE-"
    RETRY = "-RETRY-"


class PromptKeys(StringEnum):
    USERNAME = "-USERNAME-"
    PASSWORD = "-PASSWORD-"

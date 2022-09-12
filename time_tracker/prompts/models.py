from time_tracker.enum import StringEnum


class PromptEvents(StringEnum):
    OK = "-OK-"
    CANCEL = "-CANCEL-"
    CLOSE = "-CLOSE-"
    RETRY = "-RETRY-"

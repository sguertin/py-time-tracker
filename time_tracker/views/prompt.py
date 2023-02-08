from abc import ABCMeta
from logging import Logger
import PySimpleGUI as sg

from time_tracker.constants import EMPTY
from time_tracker.interfaces.logging import ILoggingProvider
from time_tracker.models.prompts import PromptEvents, PromptKeys
from time_tracker.interfaces.views import IPromptView, IUserCredentialView


class PromptView(IPromptView):
    log: Logger
    title: str

    def run(self) -> PromptEvents:
        window = sg.Window(title=self.title, layout=self.layout, size=self.size)
        event, _ = window.read(close=True)
        self.log.info("Event %s received", event)
        if event == sg.WIN_CLOSED:
            event = PromptEvents.CLOSE
        return event


class OkCancelPromptView(PromptView):
    def __init__(self, msg: str, log_provider: ILoggingProvider):
        """OkCancelPrompt - When run, will display a message and include Ok and Cancel buttons

        Args:
            msg (str): The message to display
        """

        self.log = log_provider.get_logger("OkCancelPromptView")
        self.title = "Time Tracking - WARNING"
        self.layout = [
            [sg.Text(msg)],
            [
                sg.Button("Ok", key=PromptEvents.OK, bind_return_key=True),
                sg.Cancel(key=PromptEvents.CANCEL),
            ],
        ]


class WarningPromptView(PromptView):
    def __init__(self, msg: str, log_provider: ILoggingProvider):
        """WarningPrompt - When run, will display a message with a Close button

        Args:
            msg (str): The message to display
        """
        self.log = log_provider.get_logger("OkCancelPromptView")
        self.title = "Time Tracking - WARNING"
        self.layout = (
            [
                [sg.Text(msg)],
                [sg.Button("Close", key=PromptEvents.CLOSE, bind_return_key=True)],
            ],
        )


class RetryPromptView(PromptView):
    def __init__(self, msg: str, log_provider: ILoggingProvider):
        """RetryPrompt - When run, will display a message and include Retry and Cancel buttons

        Args:
            msg (str): The message to display
        """
        self.log = log_provider.get_logger("OkCancelPromptView")
        self.title = "Time Tracking - WARNING"
        self.layout = [
            [sg.Text(msg)],
            [sg.Text("Do you want to retry?")],
        ]


class UserNamePasswordPrompt(IUserCredentialView):
    def __init__(
        self,
        msg: str,
        log_provider: ILoggingProvider,
    ):
        self.log = log_provider.get_logger("UserNamePasswordPrompt")
        self.title = (f"Time Tracking - Credentials",)
        self.layout = [
            [sg.Text(msg)],
            [sg.Text(f"Username:"), sg.Input(key=PromptKeys.USERNAME)],
            [
                sg.Text(f"Password:"),
                sg.Input(key=PromptKeys.PASSWORD, password_char="•"),
            ],
            [
                sg.Submit(key=PromptEvents.OK),
                sg.Cancel(key=PromptEvents.CANCEL),
            ],
        ]

    def run(self) -> tuple[str, str]:
        window = sg.Window(self.title, self.layout)
        while True:
            event, values = window.read(close=True)
            self.log.info("Event %s received", event)
            self.log.debug(
                "EVENT %s USERNAME: %s",
                event,
                values[PromptKeys.USERNAME],
            )
            match event:
                case [PromptEvents.OK]:
                    return (
                        values[PromptKeys.USERNAME],
                        values[PromptKeys.PASSWORD],
                    )
                case [PromptEvents.CANCEL | sg.WIN_CLOSED]:
                    return EMPTY, EMPTY

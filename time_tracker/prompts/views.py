from abc import ABCMeta
from logging import Logger
import PySimpleGUI as sg

from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.prompts.models import PromptEvents
from time_tracker.view import View

class BasePromptView(View,metaclass=ABCMeta):
    log: Logger

    def run(self) -> PromptEvents:
        window = sg.Window(title=self.title, layout=self.layout, size=self.size)
        event, _ = window.read(close=True)
        self.log.debug(event)
        if event == sg.WIN_CLOSED:
            event = PromptEvents.CLOSE        
        return event


class OkCancelPromptView(BasePromptView):
    def __init__(self, msg: str, log_provider: ILoggingProvider):
        """OkCancelPrompt - When run, will display a message and include Ok and Cancel buttons

        Args:
            msg (str): The message to display
        """

        self.log_provider = log_provider
        self.title = "Time Tracking - WARNING"
        self.layout = [
            [sg.Text(msg)],
            [
                sg.Button("Ok", key=PromptEvents.OK, bind_return_key=True),
                sg.Cancel(key=PromptEvents.CANCEL),
            ],
        ]


class WarningPromptView(BasePromptView):
    def __init__(self, msg: str, log_provider: ILoggingProvider):
        """WarningPrompt - When run, will display a message with a Close button

        Args:
            msg (str): The message to display
        """
        self.log_provider = log_provider
        self.title = "Time Tracking - WARNING"
        self.layout = (
            [
                [sg.Text(msg)],
                [sg.Button("Close", key=PromptEvents.CLOSE, bind_return_key=True)],
            ],
        )


class RetryPromptView(BasePromptView):
    def __init__(self, msg: str, log_provider: ILoggingProvider):
        """RetryPrompt - When run, will display a message and include Retry and Cancel buttons

        Args:
            msg (str): The message to display
        """
        self.log_provider = log_provider
        self.title = "Time Tracking - WARNING"
        self.layout = [
            [sg.Text(msg)],
            [sg.Text("Do you want to retry?")],
        ]
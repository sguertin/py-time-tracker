from logging import Logger
import PySimpleGUI as sg

from constants import Events
from time_tracker.constants import EMPTY
from time_tracker.logging import ILoggingFactory
from time_tracker.view import View


class Prompt(View):
    def run(self) -> Events:
        window = sg.Window(title=self.title, layout=self.layout, size=self.size)
        event, _ = window.run(close=True)
        return event


class OkCancelPrompt(Prompt):
    def __init__(self, msg: str):
        self.title = f"Time Tracking - WARNING"
        self.layout = [
            [sg.Text(msg)],
            [
                sg.Button("Ok", key=Events.OK, bind_return_key=True),
                sg.Cancel(key=Events.CANCEL),
            ],
        ]


class WarningPrompt(Prompt):
    def __init__(self, msg: str):
        self.title = ("Time Tracking - WARNING",)
        self.layout = (
            [
                [sg.Text(msg)],
                [sg.Button("Close", key=Events.CLOSE, bind_return_key=True)],
            ],
        )


class RetryPrompt(Prompt):
    def __init__(self, msg: str):
        """RetryPrompt - When run, will display a message and include Retry and Cancel buttons

        Args:
            msg (str): The message to display
        """
        self.title = f"Time Tracking - WARNING"
        self.layout = [
            [sg.Text(msg)],
            [sg.Text("Do you want to retry?")],
            [
                sg.Button("Retry", key=Events.RETRY, bind_return_key=True),
                sg.Cancel(key=Events.CANCEL),
            ],
        ]


class CredentialsPrompt:
    log: Logger

    def __init__(self, log_factory: ILoggingFactory):
        self.log = log_factory.get_logger("UICredentialsService")
        self.title = (f"Time Tracking - Enter Your Credentials",)
        self.layout = [
            [sg.T(f"Please provide your username and password")],
            [sg.T(f"Username:"), sg.In(key="-USER-")],
            [sg.T(f"Password:"), sg.In(key="-PASSWORD-", password_char="•")],
            [sg.Submit(key=Events.SUBMIT), sg.Cancel(key=Events.CANCEL)],
        ]

    def run(self) -> tuple[str, str]:
        window = sg.Window(self.title, self.layout)
        while True:
            event, values = window.read(close=True)
            self.log.info("Event %s received", event)
            match event:
                case Events.SUBMIT:
                    return values["-USER-"], values["-PASSWORD-"]
                case Events.CANCEL | sg.WIN_CLOSED:
                    return EMPTY, EMPTY

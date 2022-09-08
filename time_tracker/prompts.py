import PySimpleGUI as sg

from constants import Events
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

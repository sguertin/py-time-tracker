import base64
from dataclasses import dataclass
from datetime import timedelta
from enum import IntEnum
import json
from logging import Logger
from typing import Optional

import requests
from dataclasses_json import DataClassJsonMixin
import PySimpleGUI as sg

from time_tracker.enum import StringEnum
from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.prompts import PromptEvents, RetryPrompt
from time_tracker.settings.models import Settings
from time_tracker.time_entry import TimeEntry
from time_tracker.view import EMPTY


class JiraStatusCodes(IntEnum):
    NEEDS_AUTH = 901
    FAILED_AUTH = 403
    SUCCESS = 201


@dataclass(slots=True)
class JiraResponse(DataClassJsonMixin):
    status_code: JiraStatusCodes
    message: Optional[str] = None


class BasicAuthenticationProvider:
    _auth: bytes = None

    def clear_auth(self) -> None:
        self._auth = None

    def get_auth(self) -> str:
        if self._auth is not None:
            return f"Basic {self._auth.decode()}"
        return None

    def set_auth(self, user_name: str, password: str):
        encoding = base64.b64encode(f"{user_name}:{password}".encode("utf-8"))
        self._auth = encoding


class JiraCredentialViewEvents(StringEnum):
    SUBMIT = "-SUBMIT-"
    CANCEL = "-CANCEL-"


class JiraCredentialViewKeys(StringEnum):
    USER = "-USER-"
    PASSWORD = "-PASSWORD-"


class JiraCredentialView:
    log: Logger

    def __init__(self, log_provider: ILoggingProvider):
        self.log = log_provider.get_logger("JiraCredentialView")
        self.title = (f"Time Tracking - Jira Credentials",)
        self.layout = [
            [sg.Text(f"Please provide your username and password")],
            [sg.Text(f"Username:"), sg.Input(key=JiraCredentialViewKeys.USER)],
            [
                sg.Text(f"Password:"),
                sg.Input(key=JiraCredentialViewKeys.PASSWORD, password_char="•"),
            ],
            [
                sg.Submit(key=JiraCredentialViewEvents.SUBMIT),
                sg.Cancel(key=JiraCredentialViewEvents.CANCEL),
            ],
        ]

    def run(self) -> tuple[str, str]:
        window = sg.Window(self.title, self.layout)
        while True:
            event, values = window.read(close=True)
            self.log.info("Event %s received", event)
            match event:
                case JiraCredentialViewEvents.SUBMIT:
                    return (
                        values[JiraCredentialViewKeys.USER],
                        values[JiraCredentialViewKeys.PASSWORD],
                    )
                case JiraCredentialViewEvents.CANCEL | sg.WIN_CLOSED:
                    return EMPTY, EMPTY


class JiraService:
    def __init__(
        self,
        log_provider: ILoggingProvider,
        settings: Settings,
    ):
        self.auth_provider = BasicAuthenticationProvider()
        self.credentials_prompt = JiraCredentialView(log_provider)
        self.last_status = 0
        self.log = log_provider.get_logger("JiraService")
        self.settings = settings
        self.auth_provider.set_auth(self.credentials_prompt.run())

    @property
    def base_url(self) -> str:
        return self.settings.base_url

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": self.auth_provider.get_auth(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @property
    def clean_headers(self) -> dict[str, str]:
        return {
            "Authorization": "Basic *******",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def try_log_work(
        self,
        entry: TimeEntry,
        time_interval: Optional[timedelta] = None,
    ) -> None:
        retry = PromptEvents.RETRY
        if time_interval is None:
            time_interval = self.settings.time_interval
        while retry == PromptEvents.RETRY:
            response = self.log_hours(entry, time_interval)
            self.log.debug(response)
            if response.status_code != JiraStatusCodes.SUCCESS:
                self.log.warning(
                    f"Received Response Code: {response.status_code} Message: '{response.message}'"
                )
                retry = RetryPrompt(
                    f"Received unexpected response from Jira: "
                    + "HttpStatusCode: {response.status_code} Message: '{response.message}'"
                    + "\nDo you want to retry?"
                ).run()
                if retry == PromptEvents.RETRY and response.status_code in [
                    JiraStatusCodes.NEEDS_AUTH,
                    JiraStatusCodes.FAILED_AUTH,
                ]:
                    self.auth_provider.set_auth(self.credentials_prompt.run())

    def log_hours(
        self,
        entry: TimeEntry,
        time_interval: timedelta = None,
    ) -> JiraResponse:
        if not time_interval:
            time_interval = timedelta(
                hours=self.settings.interval_hours,
                minutes=self.settings.interval_minutes,
            )
        if not self.auth_provider.get_auth():
            self.log.debug("Credentials not found")
            return JiraResponse(
                JiraStatusCodes.NEEDS_AUTH, "Need to reauthenticate with Jira"
            )

        url = self.worklog_url(entry.issue)

        exists, status_code = self.issue_exists(entry.issue)
        if exists:
            data = {"timeSpentSeconds": {time_interval.seconds}}
            if entry.comment:
                data["comment"] = entry.comment
            self.log.debug(
                "POST(%s, headers=%s, data=%s)",
                url,
                str(self.clean_headers),
                str(data),
            )
            response = requests.post(url, headers=self.headers, data=json.dumps(data))

            if response.status_code == JiraStatusCodes.FAILED_AUTH:
                self.auth_provider.clear_auth()
                return JiraResponse(
                    response.status_code, "Authentication with Jira failed!"
                )
            elif response.status_code != JiraStatusCodes.SUCCESS:
                return JiraResponse(
                    response.status_code,
                    f"Expected status code of {JiraStatusCodes.SUCCESS}, got {response.status_code}",
                )
            return JiraResponse(response.status_code)
        else:
            warning_msg = f"Jira encountered an error attempting to access {entry.issue} with a Status Code of {status_code}"
            self.log.warning(
                "Jira encountered an error attempting to access %s with a Status Code of %s",
                entry.issue,
                status_code,
            )
            return JiraResponse(status_code, warning_msg)

    def issue_url(self, issue):
        return f"{self.base_url}/rest/api/2/issue/{issue}"

    def worklog_url(self, issue):
        return f"{self.issue_url(issue)}/worklog"

    def issue_exists(self, issue: str) -> tuple[bool, int]:
        url = self.issue_url(issue)
        self.log.debug(f"GET({url}, headers={self.clean_headers})")
        response = requests.get(url, headers=self.headers)

        return response.status_code == 200, response.status_code

from datetime import timedelta
from typing import Optional

import requests
from time_tracker.integrations.jira.models import JiraResponse, JiraStatusCodes
from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.settings.models import Settings
from time_tracker.time_entry.interfaces import (
    ITimeEntryService,
)
from time_tracker.time_entry.models import (
    TimeEntry,
    TimeEntryResponse,
    TimeEntryResponseDisposition,
)
from time_tracker.time_entry.providers import BasicAuthenticationProvider


class JiraService(ITimeEntryService):
    def __init__(
        self,
        log_provider: ILoggingProvider,
        settings: Settings,
    ):
        self.auth_provider = BasicAuthenticationProvider()
        self.last_status = 0
        self.log = log_provider.get_logger("JiraService")
        self.settings = settings

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

    def log_work(self, entry: TimeEntry) -> TimeEntryResponse:
        time_interval = entry.to_time - entry.from_time
        if not self.auth_provider.get_auth():
            self.log.debug("Credentials not found")
            return self.create_response(
                JiraResponse(
                    JiraStatusCodes.NEEDS_AUTH, "Need to reauthenticate with Jira"
                )
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
            response = requests.post(url, headers=self.headers, data=data)
            if response.status_code == JiraStatusCodes.SUCCESS:
                result = JiraResponse(response.status_code)
            elif response.status_code == JiraStatusCodes.FAILED_AUTH:
                self.auth_provider.clear_auth()
                result = JiraResponse(
                    response.status_code, "Authentication with Jira failed!"
                )
            else:
                result = JiraResponse(
                    response.status_code,
                    f"Expected status code of {JiraStatusCodes.SUCCESS}, got {response.status_code}",
                )

        else:
            message = (
                f"Jira encountered an unexpected error attempting to access {entry.issue} "
                + f"with a Status Code of {status_code}"
            )
            if status_code == 404:
                message = f"Jira was unable to locate issue {entry.issue} with a status code of {status_code}"
            self.log.warning(
                message,
            )
            result = JiraResponse(
                status_code,
                message,
            )
        self.log.debug("%s", result)
        return self.create_response(result)

    def create_response(self, response: JiraResponse):
        return TimeEntryResponse(
            response.status_code == JiraStatusCodes.SUCCESS,
            response.message,
            self.get_disposition(response.status_code),
        )

    def get_disposition(
        self, status_code: JiraStatusCodes
    ) -> TimeEntryResponseDisposition:
        if status_code == JiraStatusCodes.NEEDS_AUTH:
            return TimeEntryResponseDisposition.NO_AUTH
        if status_code == JiraStatusCodes.SUCCESS:
            return TimeEntryResponseDisposition.SUCCESS
        return TimeEntryResponseDisposition.FAILURE

    def issue_url(self, issue):
        return f"{self.base_url}/rest/api/2/issue/{issue}"

    def worklog_url(self, issue):
        return f"{self.issue_url(issue)}/worklog"

    def issue_exists(self, issue: str) -> tuple[bool, int]:
        url = self.issue_url(issue)
        self.log.debug(f"GET({url}, headers={self.clean_headers})")
        response = requests.get(url, headers=self.headers)

        return response.status_code == 200, response.status_code

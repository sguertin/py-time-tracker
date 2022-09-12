from datetime import timedelta
import json
from typing import Optional

import requests
from time_tracker.time_entry.interfaces import IAuthenticationProvider
from time_tracker.time_entry.models import JiraResponse, JiraStatusCodes

from time_tracker.logging.interfaces import ILoggingProvider
from time_tracker.settings.models import Settings
from time_tracker.time_entry import TimeEntry


class JiraService:
    def __init__(
        self,
        log_provider: ILoggingProvider,
        auth_provider: IAuthenticationProvider,
        settings: Settings,
    ):
        self.auth_provider = auth_provider
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

    def log_hours(
        self,
        entry: TimeEntry,
        time_interval: Optional[timedelta] = None,
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
            self.log.warning(
                "Jira encountered an error attempting to access %s with a Status Code of %s",
                entry.issue,
                status_code,
            )
            result = JiraResponse(
                status_code,
                f"Jira encountered an error attempting to access {entry.issue} with a Status Code of {status_code}",
            )
        self.log.debug("%s", result)
        return result

    def issue_url(self, issue):
        return f"{self.base_url}/rest/api/2/issue/{issue}"

    def worklog_url(self, issue):
        return f"{self.issue_url(issue)}/worklog"

    def issue_exists(self, issue: str) -> tuple[bool, int]:
        url = self.issue_url(issue)
        self.log.debug(f"GET({url}, headers={self.clean_headers})")
        response = requests.get(url, headers=self.headers)

        return response.status_code == 200, response.status_code

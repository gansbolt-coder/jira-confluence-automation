"""Retrieve Jira Cloud issues for project keys supplied on the command line."""

import argparse
import base64
import json
import re
import sys
import time
from datetime import datetime, timezone
from http.client import HTTPException
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)


PAGE_SIZE = 100
REQUEST_TIMEOUT_SECONDS = 30
MAX_RATE_LIMIT_RETRIES = 4
MAX_RETRY_DELAY_SECONDS = 60
PROJECT_KEY_PATTERN = re.compile(r"[A-Z][A-Z0-9_]{0,254}\Z")
ISSUE_KEY_PATTERN = re.compile(r"[A-Z][A-Z0-9_]{0,254}-[0-9]+\Z")
REQUESTED_FIELDS = [
    "project",
    "summary",
    "status",
    "resolution",
    "priority",
    "duedate",
    "updated",
    "issuelinks",
]


class ConfigurationError(Exception):
    """Raised when the local Jira configuration is missing or invalid."""


class JiraRetrievalError(Exception):
    """Raised when a Jira project cannot be retrieved completely."""


class RejectRedirectHandler(HTTPRedirectHandler):
    """Prevent forwarding Jira credentials to a redirect destination."""

    def redirect_request(self, request, response, code, message, headers, url):
        return None


def load_dotenv(path: Path) -> dict[str, str]:
    """Read simple KEY=VALUE entries without exposing their values."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        raise ConfigurationError(
            f"Unable to read the required .env file at {path}."
        ) from None
    except UnicodeError:
        raise ConfigurationError("The .env file is not valid UTF-8.") from None

    values: dict[str, str] = {}
    for line_number, line in enumerate(lines, start=1):
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        if entry.startswith("export "):
            entry = entry[len("export ") :].strip()
        if "=" not in entry:
            raise ConfigurationError(
                f"Invalid .env entry on line {line_number}; expected KEY=VALUE."
            )

        name, raw_value = entry.split("=", maxsplit=1)
        name = name.strip()
        raw_value = raw_value.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise ConfigurationError(
                f"Invalid variable name in .env on line {line_number}."
            )
        if name in values:
            raise ConfigurationError(
                f"Duplicate variable {name} in .env on line {line_number}."
            )
        if raw_value.startswith(("'", '"')):
            quote = raw_value[0]
            if len(raw_value) < 2 or raw_value[-1] != quote:
                raise ConfigurationError(
                    f"Unclosed quoted value for {name} in .env on line "
                    f"{line_number}."
                )
            raw_value = raw_value[1:-1]
        values[name] = raw_value
    return values


def get_connection_settings(env_path: Path) -> tuple[str, str, str]:
    values = load_dotenv(env_path)
    required = ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")
    missing = [name for name in required if not values.get(name)]
    if missing:
        names = ", ".join(missing)
        raise ConfigurationError(
            f"Missing required .env variable(s): {names}. "
            "Set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN."
        )

    base_url = values["JIRA_BASE_URL"].rstrip("/")
    try:
        parsed_url = urlsplit(base_url)
        _ = parsed_url.port
    except ValueError:
        raise ConfigurationError("JIRA_BASE_URL is not a valid URL.") from None
    if (
        parsed_url.scheme != "https"
        or not parsed_url.hostname
        or parsed_url.username is not None
        or parsed_url.password is not None
        or parsed_url.query
        or parsed_url.fragment
    ):
        raise ConfigurationError(
            "JIRA_BASE_URL must be an HTTPS URL without embedded credentials, "
            "a query, or a fragment."
        )
    if not values["JIRA_EMAIL"].strip():
        raise ConfigurationError("JIRA_EMAIL must not be empty.")
    if not values["JIRA_API_TOKEN"]:
        raise ConfigurationError("JIRA_API_TOKEN must not be empty.")
    return base_url, values["JIRA_EMAIL"].strip(), values["JIRA_API_TOKEN"]


def validate_project_key(project_key: str) -> None:
    if not PROJECT_KEY_PATTERN.fullmatch(project_key):
        raise JiraRetrievalError(
            f"Invalid project key {project_key!r}; use an uppercase Jira "
            "project key containing letters, digits, or underscores."
        )


def relation_name(value: Any, field_name: str, issue_key: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, dict) or not isinstance(value.get("name"), str):
        raise JiraRetrievalError(
            f"Malformed {field_name} data for issue {issue_key}."
        )
    return value["name"]


def jira_issue_url(base_url: str, issue_key: str) -> str:
    if not ISSUE_KEY_PATTERN.fullmatch(issue_key):
        raise JiraRetrievalError("Jira returned an invalid issue key.")
    return f"{base_url}/browse/{issue_key}"


def normalize_issue_links(
    raw_links: Any, base_url: str, issue_key: str
) -> list[dict[str, str]]:
    if not isinstance(raw_links, list):
        raise JiraRetrievalError(f"Malformed issue-link data for {issue_key}.")

    links: list[dict[str, str]] = []
    for link in raw_links:
        if not isinstance(link, dict):
            raise JiraRetrievalError(f"Malformed issue-link data for {issue_key}.")
        link_type = link.get("type")
        if not isinstance(link_type, dict) or not isinstance(
            link_type.get("name"), str
        ):
            raise JiraRetrievalError(f"Malformed issue-link type for {issue_key}.")
        for direction in ("inwardIssue", "outwardIssue"):
            linked_issue = link.get(direction)
            if linked_issue is None:
                continue
            if not isinstance(linked_issue, dict) or not isinstance(
                linked_issue.get("key"), str
            ):
                raise JiraRetrievalError(
                    f"Malformed linked issue data for {issue_key}."
                )
            linked_key = linked_issue["key"]
            links.append(
                {
                    "type": link_type["name"],
                    "direction": direction.removesuffix("Issue"),
                    "issue_key": linked_key,
                    "url": jira_issue_url(base_url, linked_key),
                }
            )
    return links


def normalize_issue(
    raw_issue: Any, project_key: str, base_url: str
) -> dict[str, Any]:
    if not isinstance(raw_issue, dict):
        raise JiraRetrievalError(f"Malformed issue data for project {project_key}.")
    issue_key = raw_issue.get("key")
    if not isinstance(issue_key, str) or not ISSUE_KEY_PATTERN.fullmatch(issue_key):
        raise JiraRetrievalError(f"Jira returned an invalid issue key for {project_key}.")
    if not issue_key.startswith(f"{project_key}-"):
        raise JiraRetrievalError(
            f"Jira returned an issue outside project {project_key}."
        )

    fields = raw_issue.get("fields")
    if not isinstance(fields, dict):
        raise JiraRetrievalError(f"Malformed fields for issue {issue_key}.")
    missing_fields = [name for name in REQUESTED_FIELDS if name not in fields]
    if missing_fields:
        names = ", ".join(missing_fields)
        raise JiraRetrievalError(
            f"Jira response omitted requested field(s) for {issue_key}: {names}."
        )

    project = fields["project"]
    if not isinstance(project, dict) or project.get("key") != project_key:
        raise JiraRetrievalError(
            f"Jira returned an issue with unexpected project data for {issue_key}."
        )
    summary = fields["summary"]
    if not isinstance(summary, str):
        raise JiraRetrievalError(f"Malformed summary data for issue {issue_key}.")
    updated = fields["updated"]
    due_date = fields["duedate"]
    if not isinstance(updated, str) or (due_date is not None and not isinstance(due_date, str)):
        raise JiraRetrievalError(f"Malformed date data for issue {issue_key}.")

    return {
        "key": issue_key,
        "summary": summary,
        "url": jira_issue_url(base_url, issue_key),
        "status": relation_name(fields["status"], "status", issue_key),
        "resolution": relation_name(fields["resolution"], "resolution", issue_key),
        "priority": relation_name(fields["priority"], "priority", issue_key),
        "due_date": due_date,
        "updated": updated,
        "links": normalize_issue_links(fields["issuelinks"], base_url, issue_key),
    }


class JiraCloudClient:
    """Read issue data from Jira Cloud's paginated REST API v3 search endpoint."""

    def __init__(
        self, base_url: str, email: str, api_token: str, timeout: int
    ) -> None:
        self.base_url = base_url
        credentials = f"{email}:{api_token}".encode("utf-8")
        encoded_credentials = base64.b64encode(credentials).decode("ascii")
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }
        self.timeout = timeout
        self.opener = build_opener(RejectRedirectHandler())

    def _retry_delay(self, error: HTTPError, retry_number: int) -> int:
        retry_after = error.headers.get("Retry-After") if error.headers else None
        try:
            delay = int(retry_after) if retry_after is not None else 2**retry_number
        except ValueError:
            delay = 2**retry_number
        return min(max(delay, 1), MAX_RETRY_DELAY_SECONDS)

    def _fetch_page(
        self, project_key: str, page_token: str | None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "jql": f"project = {project_key} ORDER BY key ASC",
            "maxResults": PAGE_SIZE,
            "fields": REQUESTED_FIELDS,
        }
        if page_token is not None:
            payload["nextPageToken"] = page_token
        request = Request(
            f"{self.base_url}/rest/api/3/search/jql",
            data=json.dumps(payload).encode("utf-8"),
            headers=self.headers,
            method="POST",
        )

        for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
            try:
                with self.opener.open(request, timeout=self.timeout) as response:
                    response_body = response.read()
                try:
                    decoded = json.loads(response_body.decode("utf-8"))
                except (UnicodeError, json.JSONDecodeError):
                    raise JiraRetrievalError(
                        f"Jira returned an invalid JSON response for project "
                        f"{project_key}."
                    ) from None
                if not isinstance(decoded, dict):
                    raise JiraRetrievalError(
                        f"Jira returned an unexpected response for project "
                        f"{project_key}."
                    )
                return decoded
            except HTTPError as error:
                if error.code == 429 and attempt < MAX_RATE_LIMIT_RETRIES:
                    time.sleep(self._retry_delay(error, attempt))
                    continue
                if error.code == 401:
                    detail = "authentication failed; verify JIRA_EMAIL and JIRA_API_TOKEN"
                elif error.code == 403:
                    detail = "access was denied; verify the account's project permissions"
                elif error.code == 404:
                    detail = "the Jira search endpoint or project was not found"
                elif error.code == 429:
                    detail = "Jira rate-limited the request after retries"
                else:
                    detail = f"Jira returned HTTP {error.code}"
                raise JiraRetrievalError(
                    f"Unable to retrieve project {project_key}: {detail}."
                ) from None
            except (HTTPException, TimeoutError, URLError, OSError):
                raise JiraRetrievalError(
                    f"Network error while retrieving project {project_key}."
                ) from None

        raise JiraRetrievalError(
            f"Unable to retrieve project {project_key} after rate-limit retries."
        )

    def retrieve_project(self, project_key: str) -> list[dict[str, Any]]:
        validate_project_key(project_key)
        issues: list[dict[str, Any]] = []
        issue_keys: set[str] = set()
        requested_tokens: set[str] = set()
        page_token: str | None = None

        while True:
            response = self._fetch_page(project_key, page_token)
            raw_issues = response.get("issues")
            if not isinstance(raw_issues, list):
                raise JiraRetrievalError(
                    f"Jira response for project {project_key} omitted its issues list."
                )
            for raw_issue in raw_issues:
                issue = normalize_issue(raw_issue, project_key, self.base_url)
                if issue["key"] in issue_keys:
                    raise JiraRetrievalError(
                        f"Jira returned duplicate issue {issue['key']} for project "
                        f"{project_key}; refusing an incomplete or inconsistent result."
                    )
                issue_keys.add(issue["key"])
                issues.append(issue)

            is_last = response.get("isLast")
            if is_last is not None and not isinstance(is_last, bool):
                raise JiraRetrievalError(
                    f"Jira returned invalid pagination status for project {project_key}."
                )
            next_token = response.get("nextPageToken")
            if next_token is not None and (
                not isinstance(next_token, str) or not next_token
            ):
                raise JiraRetrievalError(
                    f"Jira returned an invalid pagination token for project "
                    f"{project_key}."
                )
            if is_last is True:
                break
            if next_token is None:
                if is_last is False:
                    raise JiraRetrievalError(
                        f"Jira reported more pages but provided no pagination token "
                        f"for project {project_key}."
                    )
                break
            if next_token in requested_tokens:
                raise JiraRetrievalError(
                    f"Jira repeated a pagination token for project {project_key}."
                )
            requested_tokens.add(next_token)
            page_token = next_token

        return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Retrieve Jira Cloud issues for one or more project keys. "
            "Reads JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN from the "
            "module's .env file."
        )
    )
    parser.add_argument(
        "project_keys",
        metavar="PROJECT_KEY",
        nargs="+",
        help="uppercase Jira project key(s), for example PROJ",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_keys: list[str] = []
    try:
        for project_key in args.project_keys:
            validate_project_key(project_key)
            if project_key not in project_keys:
                project_keys.append(project_key)

        env_path = Path(__file__).resolve().parents[1] / ".env"
        base_url, email, api_token = get_connection_settings(env_path)
        client = JiraCloudClient(
            base_url, email, api_token, REQUEST_TIMEOUT_SECONDS
        )
        projects = []
        for project_key in project_keys:
            issues = client.retrieve_project(project_key)
            projects.append(
                {
                    "key": project_key,
                    "issue_count": len(issues),
                    "pagination_complete": True,
                    "issues": issues,
                }
            )
    except (ConfigurationError, JiraRetrievalError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    result = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "jira_base_url": base_url,
        "projects": projects,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
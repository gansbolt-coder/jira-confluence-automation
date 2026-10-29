"""Count retrieved Jira issues by status for command-line project keys."""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from retrieve_jira_issues import (
    ConfigurationError,
    JiraCloudClient,
    JiraRetrievalError,
    REQUEST_TIMEOUT_SECONDS,
    get_connection_settings,
    validate_project_key,
)


def count_project_statuses(
    project_key: str, issues: list[dict[str, Any]]
) -> dict[str, Any]:
    """Count statuses and verify every retrieved issue is accounted for."""
    status_counts: Counter[str] = Counter()
    missing_status_count = 0

    for issue in issues:
        status = issue.get("status")
        if status is None or status == "":
            missing_status_count += 1
        elif isinstance(status, str):
            status_counts[status] += 1
        else:
            raise JiraRetrievalError(
                f"Invalid status data in a retrieved {project_key} issue."
            )

    retrieved_issue_count = len(issues)
    counted_issue_total = sum(status_counts.values()) + missing_status_count
    totals_match = counted_issue_total == retrieved_issue_count
    if not totals_match:
        raise JiraRetrievalError(
            f"Status counts for project {project_key} do not reconcile with "
            "the retrieved issue total."
        )

    return {
        "project_key": project_key,
        "retrieved_issue_count": retrieved_issue_count,
        "status_counts": dict(sorted(status_counts.items())),
        "issues_with_missing_status": missing_status_count,
        "counted_issue_total": counted_issue_total,
        "totals_match": totals_match,
        "status_counts_complete": missing_status_count == 0,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Retrieve Jira issues for the specified project keys and count "
            "them by Jira status. Connection settings are read from .env."
        )
    )
    parser.add_argument(
        "project_keys",
        metavar="PROJECT_CODE",
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
            projects.append(count_project_statuses(project_key, issues))
    except (ConfigurationError, JiraRetrievalError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    result = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "projects": projects,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

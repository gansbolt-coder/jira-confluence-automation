---
name: Count Jira Issues by Status
description: "Use when calculating per-project Jira issue counts grouped by status and validating counts against the retrieved issue total."
tools: []
---
Use `tools/calc_issue_counts.py` when a user requests Jira issue counts by status for one or more projects.

## Usage
- Run from the `work/module08-task` directory:
  - `python tools/calc_issue_counts.py PROJECT_CODE [OTHER_PROJECT_CODE ...]`
  - On Windows, use `py` if `python` is unavailable.
- Supply one or more uppercase Jira project keys as positional arguments.
- The script retrieves a fresh issue set for each project using `tools/retrieve_jira_issues.py`'s Jira client and reads connection settings from `work/module08-task/.env`.
- This uses Jira Cloud REST API v3. Never inspect, print, or request the API token in chat.

## Results and Errors
- On success, the script prints JSON with a UTC retrieval timestamp and each project's status counts, retrieved issue count, counted total, and reconciliation result.
- Report `issues_with_missing_status` separately. If `status_counts_complete` is false, make clear that some retrieved issues had no status and are excluded from named status groups.
- Confirm `totals_match` is true before presenting the counts as reconciled. Do not invent status labels or treat missing statuses as zero.
- Treat any non-zero exit or error on stderr as a failed calculation/retrieval; do not present partial results as complete.
- Report configuration, permission, API, or network failures without exposing credentials. Retrieval and counting are read-only; do not create or update Jira issues.

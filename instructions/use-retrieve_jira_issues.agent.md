---
name: Retrieve Jira Issues
description: "Use when retrieving Jira Cloud issues for one or more project keys, using the retrieve_jira_issues.py command-line tool."
tools: []
---
Use `tools/retrieve_jira_issues.py` to retrieve a complete, read-only snapshot of Jira issues for specified projects.

## Usage
- Run from the `work/module08-task` directory:
  - `python tools/retrieve_jira_issues.py PROJECT_KEY [OTHER_PROJECT_KEY ...]`
  - On Windows, use `py` if `python` is unavailable.
- Supply one or more uppercase Jira project keys as positional arguments.
- The script loads `JIRA_BASE_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN` from `work/module08-task/.env`. Never inspect, print, or request the API token in chat.
- The script uses Jira Cloud REST API v3 with email/API-token authentication. Do not use it for Jira Data Center/Server.

## Results and Errors
- On success, the script prints JSON containing the UTC retrieval time, each requested project, issue count, pagination-complete indicator, and issue details. Each issue includes its Jira summary/title, key, URL, status, resolution, priority, due date, updated timestamp, and links.
- Include the issue summary/title alongside its key and current fields when presenting retrieved issues. Do not infer extra context from the summary.
- Use the JSON as the evidence for downstream summaries and calculations; do not claim a project is complete unless retrieval succeeded and `pagination_complete` is true.
- The script handles pagination and rate-limit retries. Treat any non-zero exit or error on stderr as a failed retrieval; do not present partial results as complete.
- Report configuration, permission, API, and network failures without exposing credentials. Do not retry indefinitely or substitute invented data.
- Retrieval is read-only. Do not create or update Jira issues as part of this workflow.

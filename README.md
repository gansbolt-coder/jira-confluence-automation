# Jira / Confluence Automation

Utilities and project documentation for read-only Jira automation. The current
Jira tools retrieve issues from Jira Cloud and summarize issue counts by
status. The repository also includes a compound-interest command-line
calculator and stdio MCP server.

> **Project status:** The planned Development-wide Weekly Project Health Brief
> is described in [`project_spec.md`](project_spec.md) and
> [`backlog.md`](backlog.md). The full brief, Confluence integration, and a
> scheduled daily refresh are not implemented yet.

## Requirements

- Python 3.10 or newer
- Jira Cloud access for the projects you want to query
- A Jira account and API token with read-only access to those projects

The scripts use the Python standard library; no third-party packages are
required.

## Jira configuration

Create a `.env` file in the repository root with your Jira Cloud connection
settings:

```dotenv
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=replace-with-your-api-token
```

Keep the real `.env` file and API token private. `.env` is ignored by Git; do
not commit credentials or paste them into reports, logs, or source files.

## Jira tools

Run commands from the repository root. Supply one or more uppercase Jira
project keys:

```console
python tools/retrieve_jira_issues.py PROJECT
python tools/retrieve_jira_issues.py PROJECT OTHER
python tools/calc_issue_counts.py PROJECT
```

`retrieve_jira_issues.py` prints JSON containing the retrieval timestamp,
project keys, issue counts, and normalized issue data. It follows Jira
pagination and reports retrieval or configuration errors instead of presenting
an incomplete result as successful.

`calc_issue_counts.py` prints JSON with each project's retrieved issue count,
counts grouped by Jira status, and an explicit count of issues with missing
status data.

Both tools use the same `.env` settings and make no Jira changes.

## Compound-interest tools

Calculate compound interest from the command line:

```console
python tools/compound_interest.py 1000 5 12 3
```

Arguments are principal, annual rate (as a percentage), compounding periods per
year, and duration in years.

The same calculation is available as a stdio MCP server:

```console
python tools/compound_interest_mcp.py
```

Configure an MCP client to launch that command using its standard input/output
transport.

## Project documentation

- [`project_spec.md`](project_spec.md) describes the intended Weekly Project
  Health Brief, its scope, data handling, and acceptance criteria.
- [`backlog.md`](backlog.md) tracks implementation work and prerequisites.
- [`instructions/`](instructions/) contains project-specific agent
  instructions and workflows.

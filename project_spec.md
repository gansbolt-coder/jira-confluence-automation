# Technical Specification: Weekly Project Health Brief

## 1. Purpose

Create a read-only weekly brief that helps the Project Coordinator responsible
for an 80-person Development organization understand delivery health across its
Jira projects. Project leads and team managers are the primary readers.

The brief is intended to make project status and delivery risks easier to
review and coordinate. It is not a performance-monitoring tool and must not
present an unapproved health score as authoritative.

## 2. Scope and decisions

| Area | Requirement |
| --- | --- |
| Organization | Development, approximately 80 people |
| Project scope | All Development projects, identified by an explicit, configured allowlist of Jira project keys |
| Expected scale | Approximately 1–5 Jira projects |
| Data source | Jira only; Confluence is excluded |
| Reporting period | Previous seven days plus a current-state snapshot |
| Reporting timezone | UTC |
| Data refresh frequency | Daily; fetch the latest Jira data at least once per day |
| Delivery | Generate a Markdown file on demand |
| Output location | `reports/`, with a timestamped filename |
| Retention | Follow the organization's retention policy; do not delete reports automatically until that policy is specified |
| Audience | Project leads and team managers |
| Person-level detail | Do not include individual names, workload metrics, or completion rankings |
| Jira access | Dedicated read-only integration account; retrieve its API key from a local environment variable |
| Jira mutations | None. Report and link only; do not create or update Jira issues |
| Existing report | Replace the existing KAN weekly report with this Development-wide brief |
| Legacy sections | Do not carry over the existing recently resolved, recently updated, or Jira version-list sections unless separately requested |
| Health labels | Use explicit risk flags only until Development leadership approves Green/Amber/Red thresholds |

## 3. Report contents

Generate a structured Markdown report with these sections:

1. **Executive summary**
   - Concise organization-wide summary of the observed project state and
     significant changes during the reporting period.
   - Distinguish observed Jira facts from interpretation.
2. **Project-by-project health**
   - One subsection per configured Development project.
   - Include project key/name, issue counts by status, and a concise project
     health summary.
   - Do not calculate or display a Green/Amber/Red label until an approved
     threshold rubric is supplied.
3. **Milestones and progress changes**
   - Report milestone status and target dates.
   - Summarize relevant changes observed during the previous seven days.
4. **Risks, blockers, and dependencies**
   - Flag blocked issues, overdue issues, unresolved dependencies, missed or
     at-risk milestones, and stale high-priority work.
   - For staleness, use the agreed seven-day threshold: open high-priority work
     with no Jira update in seven days is a review prompt, not proof that the
     project is stalled.
5. **Decisions and actions needed**
   - Surface decision or follow-up candidates supported by Jira data and link
     to the existing Jira issue or milestone where available.
   - The report is read-only. It must not imply that a suggested action has
     been assigned or recorded in Jira.

The initial brief is summary-metrics-only: do not include a full issue list,
individual names, or workload/completion statistics. Jira source links may be
included where they support a reported fact or action candidate.

## 3.1 Data refresh frequency

Refresh Jira data daily at minimum. Every report generation must fetch current
Jira data rather than reuse an older report as the current snapshot. On-demand
generation remains supported and must fetch fresh data when invoked.

The daily run time and scheduling mechanism have not been selected. Configure
the daily refresh in the approved execution environment after those operational
details are confirmed. Refresh failures must be surfaced; previously generated
reports must not be presented as a successful current refresh.

## 4. Data requirements

Use only data available to the integration account for project keys on the
configured allowlist. Retrieve only fields required for the selected report
sections, including as available:

- Project key and project name.
- Issue key, summary, status, status category, issue type, priority, and
  resolution state.
- Created, updated, due, and resolution dates.
- Blocker indicators and issue links/dependencies.
- Milestone or release name, target date, and status.

Do not include assignee display names or individual-level metrics in report
output. Any Jira links must use the configured Jira base URL and a validated
issue or project key.

The report must clearly identify missing or unavailable Jira fields. Do not
silently treat missing values as zero, healthy, or complete.

## 5. Health and risk interpretation

- Until an approved health rubric is provided, report signal-level facts rather
  than an aggregate health color, score, or prediction.
- Each risk flag must explain its trigger and link to its Jira source when
  possible.
- An overdue issue is an unresolved issue whose due date is earlier than the
  report date in UTC.
- A blocked issue is identified from a Jira blocked/impeded status or an
  explicitly represented blocker relationship. Do not infer blocked status
  solely from issue text.
- An unresolved dependency is based on a Jira issue link or other explicitly
  configured Jira relationship. The exact link types to treat as dependencies
  must be verified against the organization's Jira configuration.
- A missed milestone is an unreleased milestone whose target date is before
  the report date. The exact rule for “at risk” is not yet defined and must be
  agreed before implementation.
- Stale work is open, high-priority work with no update in the preceding seven
  days. If Jira priority or update data is missing, report that the signal
  could not be evaluated.
- Risk flags are prompts for review, not assertions about team or individual
  performance.

## 6. User workflow

1. The authorized operator configures Jira connection details and the
   Development project-key allowlist outside source code.
2. The daily run, or an operator invoking the entry point on demand, starts a
   fresh Jira data retrieval.
3. The tool validates configuration and read-only Jira access.
4. The tool retrieves and paginates data for each configured project.
5. The tool builds the Markdown brief for the seven-day window and current
   snapshot in UTC.
6. The tool writes a timestamped report under `reports/` and prints the output
   path.
7. The operator shares and retains the generated report under organizational
   data-handling and retention policies.

Email distribution, chat posting, web dashboard, and Confluence ingestion are
not in scope. The daily refresh is required, but its scheduler and run time
remain operational decisions.

## 7. Technical approach

- Extend the existing Python `weekly_status_report.py` entry point rather than
  introduce a separate application.
- Preserve the existing project's dependency-light approach and use the Python
  standard library unless a concrete requirement justifies a new dependency.
- Replace the existing KAN-specific report behavior with the Development-wide
  brief, including removal of the hard-coded single-project scope.
- Make the allowlist, Jira base URL, and secret source explicit configuration;
  do not infer that KAN is in scope.
- Use the Jira REST API supported by the organization's deployment. The
  deployment is not yet known, so endpoint selection and authentication headers
  must be confirmed before implementation.
- Handle API pagination, rate limits, permission errors, invalid responses,
  and network failures explicitly. Never emit a success-shaped partial report
  when required project data could not be retrieved.
- Generate timestamped files using UTC. Avoid overwriting an earlier report.
- Do not log API keys, authorization headers, or other credentials.

## 8. Security and data handling

- Use the dedicated read-only integration account and restrict its Jira
  permissions to the approved Development project allowlist.
- Store the API key only in a local environment variable or an organization
  approved secret manager. Never commit it, print it, include it in the report,
  or put it in browser/client-side code.
- The API key must not be copied from any existing `.env` file into source
  code, documentation, tests, or generated reports.
- Validate the Jira base URL and project/issue identifiers before constructing
  requests or links.
- Treat generated reports as internal project data. Follow the organization's
  approved storage, sharing, and retention policies.
- Keep the report read-only with respect to Jira.

## 9. Error handling and observability

The command must fail with a clear, actionable error and a non-zero exit status
when required configuration is absent or Jira data cannot be retrieved
reliably. Errors should identify the affected operation/project without
disclosing credentials.

Examples of conditions that must be surfaced:

- Missing API key, Jira base URL, or project allowlist.
- Unsupported or unconfirmed Jira deployment/authentication configuration.
- A project key that is invalid or inaccessible to the integration account.
- Pagination failure, rate limiting, malformed Jira responses, or network
  failure.
- Missing required fields or invalid dates.
- Failure to create or write the output file.

If a project fails to load, do not silently omit it and present the report as
complete. Either fail the report or mark it prominently as incomplete according
to a behavior agreed before implementation.

## 10. Acceptance criteria

1. A local, on-demand command generates a Markdown brief in `reports/` with a
   UTC timestamped filename.
2. Jira data is refreshed at least once each day, and each report run fetches
   fresh data rather than treating an older report as current.
3. The report covers every configured project key and no project outside the
    allowlist.
4. The report represents the previous seven days and a current-state snapshot.
5. The report contains the five sections defined in Section 3.
6. Issue counts by status and milestone status/target dates are calculated
    from Jira data and are not fabricated when data is missing.
7. Blocked, overdue, dependency, missed/at-risk milestone, and stale-work
    signals explain their triggering facts and include source links when
    available.
8. No Green/Amber/Red health color or aggregate health score is emitted before
    the approved rubric is configured.
9. Output contains no individual names, workload metrics, or completion
    rankings.
10. Running the report performs no Jira writes and does not send or publish the
    report.
11. Credentials are not present in source, output, or logs.
12. A failed or incomplete Jira retrieval is surfaced clearly and cannot be
    mistaken for a complete successful report.
13. Tests cover project allowlisting, pagination, status counts, seven-day
    boundaries, UTC date handling, risk-signal rules, missing data, output
    naming, and explicit failure behavior.

## 11. Open questions and prerequisites

Resolve these with the Jira administrator or Development leadership before
implementing a live integration:

1. Confirm whether the Jira deployment is Cloud or Data Center/Server.
2. Confirm the Jira base URL and the API-key authentication scheme supported by
   that deployment and the dedicated integration account.
3. Provide the Development project-key allowlist and confirm which projects
   belong in the brief.
4. Confirm the Jira issue-link types that represent blockers and unresolved
   dependencies.
5. Define how a milestone is represented in Jira and agree what qualifies as
   “at risk.”
6. Identify the source of decision/action candidates in Jira; the report must
   not invent decisions or imply a Jira assignment.
7. Confirm behavior when one project is inaccessible or fails to load: fail
   the full report or produce an explicitly incomplete report.
8. Obtain the approved Green/Amber/Red rubric if color labels are to be added
   later.
9. Confirm the organization's report retention and sharing policy.

Until these prerequisites are resolved, use sample fixtures or a dry-run
approach and do not request, store, or use live Jira credentials.

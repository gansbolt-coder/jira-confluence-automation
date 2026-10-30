# Weekly Project Health Brief — Implementation Backlog

Source: [`project_spec.md`](./project_spec.md)

The phases below remain in the requested order. Tasks within a phase may be
worked in parallel when their dependencies permit. Complete the live-integration
gates in Setup before using real Jira credentials or querying live project data.
All checkboxes start unchecked; mark an item complete only after its work and
verification are done.

## MCP and Custom Skill Classification

The current connected MCP tools and repository `.vscode/mcp.json` expose only
the `echo-windows` server for this workflow; no Jira or Confluence server is
currently configured. Existing options found include the
[official Atlassian MCP server](https://github.com/atlassian/atlassian-mcp-server),
a cloud-hosted Jira/Confluence and other Atlassian products server, and the
community [mcp-atlassian server](https://github.com/sooperset/mcp-atlassian),
which supports Jira and Confluence Cloud and Data Center/Server.

The tags below are recommendations, not claims that an Atlassian server is
already installed or authorized. `MCP` marks tasks that can use an Atlassian
MCP server for Jira data access or retrieval. `custom skill` marks
project-specific decisions, calculations, report rules, orchestration,
testing, scheduling, and documentation that still need custom implementation
or guidance even when MCP supplies Jira data.

## Setup

- [ ] Inspect the existing `weekly_status_report.py`, its tests, report output,
  configuration, and the repository boundaries; record which files are in the
  Module 08 Git repository and which are outside it. (custom skill)
- [ ] Confirm the target deployment is Jira Cloud or Jira Data Center/Server. (MCP)
- [ ] Confirm the Jira base URL and the API authentication scheme supported by
  that deployment and the dedicated read-only integration account. (MCP)
- [ ] Obtain and review the Development project-key allowlist; verify it covers
  every in-scope project and no out-of-scope project. (MCP)
- [ ] Verify that the dedicated integration account has read-only access only
  to the approved project scope and the fields needed for the report. (MCP)
- [ ] Confirm Jira issue-link types that represent blockers and unresolved
  dependencies; document the exact inward/outward relationships. (MCP)
- [ ] Confirm how milestones are represented in Jira and agree any rule for
  identifying an “at-risk” milestone. Preserve the specified missed-milestone
  rule: unreleased with a target date earlier than the report date. (MCP)
- [ ] Agree how the “Decisions and actions needed” section will derive
  candidates from Jira facts without inventing decisions or implying an action
  was assigned. (custom skill)
- [ ] Decide whether a failed project retrieval fails the whole report or
  produces a prominently marked incomplete report; document the chosen
  behavior. (custom skill)
- [ ] Confirm the organization’s report sharing and retention policy; do not
  implement automatic deletion until a concrete retention rule is approved. (custom skill)
- [ ] Select the approved daily execution environment, run time, and scheduling
  mechanism. Keep on-demand generation available; do not treat a scheduler as
  configured until it is deployed and verified. (custom skill)
- [ ] Define required configuration names and formats for the Jira base URL,
  project-key allowlist, and API key. Keep secrets outside source code and
  generated reports. (MCP)
- [ ] Review the existing KAN report’s consumers and make a migration/back-up
  plan before replacing its behavior, as required by the specification. (custom skill)

**Gate:** Do not use live Jira credentials or live Jira data until deployment,
authentication, project allowlist, and least-privilege access are confirmed.
Resolve the remaining Jira semantics and incomplete-report behavior before
releasing a production brief.

## Core Features

- [ ] Replace the hard-coded single-project scope with validated configuration
  for the approved Development project-key allowlist; reject an empty or
  malformed allowlist and never infer that KAN is in scope. (MCP)
- [ ] Implement configuration loading and validation for the Jira base URL,
  project keys, and API key; report missing configuration with a clear error
  that does not reveal secret values. (MCP)
- [ ] Implement or adapt a Jira client for the confirmed deployment and
  authentication scheme, using the Python standard library unless a verified
  requirement justifies another dependency. (MCP)
- [ ] Implement Jira issue retrieval for every configured project with
  pagination, required fields only, and the existing explicit handling pattern
  for network/API errors. (MCP)
- [ ] Fetch a current Jira snapshot on every invocation; calculate the
  reporting window as the preceding seven days and use UTC consistently for
  window boundaries, dates, and timestamps. (custom skill)
- [ ] Calculate per-project issue counts grouped by actual Jira status names;
  validate totals against the retrieved issue set and disclose missing status
  data instead of treating it as zero. (custom skill)
- [ ] Retrieve project metadata and milestone/release status and target dates
  using the Jira representation confirmed during Setup. (MCP)
- [ ] Summarize material milestone and progress changes observed in the
  reporting window without presenting unsupported interpretations as facts. (custom skill)
- [ ] Implement risk-signal rules for unresolved overdue issues, explicitly
  blocked issues or blocker relationships, confirmed unresolved dependency
  link types, missed milestones, and open high-priority issues not updated in
  the preceding seven days. (custom skill)
- [ ] For every emitted risk signal, include the factual trigger and a
  validated Jira source link when available; label stale work as a review
  prompt, not proof of stalled delivery. (custom skill)
- [ ] When required signal inputs are missing, disclose that the signal could
  not be evaluated; do not silently classify it as clear. (custom skill)
- [ ] Generate the five required Markdown sections: executive summary,
  project-by-project health, milestones and progress changes, risks/blockers/
  dependencies, and decisions/actions needed. (custom skill)
- [ ] Keep the output summary-metrics-only: exclude full issue lists, assignee
  names, workload metrics, completion rankings, unsupported health colors,
  scores, and delivery predictions. (custom skill)
- [ ] Until Development leadership approves explicit health thresholds, emit
  risk facts only and no Green/Amber/Red classification. (custom skill)
- [ ] Generate a UTC-timestamped Markdown file under `reports/`, avoiding
  accidental overwrite, and print the saved path. (custom skill)
- [ ] Preserve the report as read-only: do not create or update Jira issues,
  send email, post to chat, or publish to a dashboard. (MCP)
- [ ] Replace the KAN-specific report behavior with the Development-wide brief
  only after the migration plan is approved; remove legacy resolved/updated
  issue lists and version sections unless separately requested. (custom skill)

**Dependencies:** Jira client and all report sections depend on the Setup
deployment, authentication, and project-scope decisions. Blocker/dependency
signals depend on confirmed Jira link semantics. Milestone-risk interpretation
depends on the agreed Jira milestone representation and “at risk” rule.

## Integration

- [ ] Wire the configured project allowlist into the existing report entry
  point and ensure every configured project is queried exactly within scope. (MCP)
- [ ] Wire the confirmed Jira client into the report-generation workflow;
  ensure all required pages of results are retrieved before rendering. (MCP)
- [ ] Implement the Setup decision for project retrieval failures; prevent a
  partial result from appearing complete. (custom skill)
- [ ] Validate the configured Jira base URL and project/issue identifiers
  before making requests or constructing report links. (custom skill)
- [ ] Load the API key from the approved local environment variable or approved
  secret source; never print it, log it, commit it, or copy it to the report.
  (MCP)
- [ ] Ensure authorization headers and secret values are excluded from
  exception messages and diagnostic output. (custom skill)
- [ ] Create the `reports/` output directory safely when absent; surface
  directory creation and file-write failures with actionable errors. (custom skill)
- [ ] Implement and deploy the approved daily trigger in the selected execution
  environment; verify its timezone, schedule, permissions, and output path.
  (custom skill)
- [ ] Ensure scheduled and on-demand runs both fetch fresh Jira data, produce
  UTC timestamps, and report failures explicitly. (custom skill)
- [ ] Verify the daily trigger does not distribute or publish reports and
  follows the approved storage, sharing, and retention policy. (custom skill)

**Dependencies:** Live integration and daily scheduling are gated by the Setup
decisions and the Core Features for validated configuration, fresh retrieval,
and report generation. Do not configure production scheduling with placeholder
credentials or an unapproved execution environment.

## Testing

- [ ] Add unit tests for required configuration, malformed project keys,
  invalid Jira base URLs, and missing API keys; assert errors do not disclose
  secret values. (custom skill)
- [ ] Add tests for allowlist behavior: every configured project is queried,
  unlisted projects are excluded, and KAN is not implicitly included. (custom skill)
- [ ] Add tests for Jira pagination, including multiple pages, empty final
  page, API/network errors, repeated pagination tokens where applicable, and
  malformed responses. (custom skill)
- [ ] Add tests for exact UTC seven-day boundaries, current snapshot timestamps,
  due-date comparisons, and missed milestone comparisons. (custom skill)
- [ ] Add tests for issue counts by status, total-count consistency, empty
  projects, and missing status values. (custom skill)
- [ ] Add tests for each risk rule: blocked status/relationship, overdue
  unresolved issues, configured dependency link direction, missed milestone,
  and stale open high-priority issue at the seven-day boundary. (custom skill)
- [ ] Add tests proving resolved overdue issues are not flagged and missing
  priority/update/due-date data is surfaced rather than silently treated as
  no risk. (custom skill)
- [ ] Add tests for report sections, source links, timestamped filename,
  no-overwrite behavior, output directory creation, and output write failures. (custom skill)
- [ ] Add tests proving no individual names, workload/completion metrics,
  unsupported health colors/scores, credentials, or Jira write requests appear
  in output or logs. (custom skill)
- [ ] Add tests for the selected failed-project policy so output cannot be
  mistaken as complete after a retrieval failure. (custom skill)
- [ ] Add a mocked end-to-end report-generation test covering multiple
  allowlisted projects, the five report sections, and risk evidence.
  (custom skill)
- [ ] Run the focused test suite and existing regression tests; fix failures
  caused by replacing the KAN report behavior. (custom skill)
- [ ] Perform a non-production integration smoke test with the dedicated
  read-only account after the Setup gate is satisfied; verify returned scope,
  pagination, links, output, and absence of Jira writes. (MCP)
- [ ] Verify the scheduled daily run operationally after deployment and
  confirm its refresh timestamp and failure reporting. (custom skill)

**Dependencies:** Unit tests can be developed alongside Core Features using
fixtures. Live integration and scheduler tests require the Setup gate and
approved credentials/environment.

## Documentation

- [ ] Update the existing report README or equivalent usage documentation to
  describe the Development-wide scope, required configuration, and on-demand
  command. (custom skill)
- [ ] Document Jira deployment/authentication configuration without recording
  real credentials; include safe environment-variable setup instructions. (custom skill)
- [ ] Document how to maintain and validate the project-key allowlist. (custom skill)
- [ ] Document the seven-day reporting window, UTC rules, status counts, each
  risk trigger, known limitations, and the absence of an approved
  Green/Amber/Red rubric. (custom skill)
- [ ] Document the confirmed Jira blocker/dependency link types, milestone
  representation, and decision/action candidate source. (custom skill)
- [ ] Document the incomplete-report behavior and how operators recognize
  retrieval, refresh, and output-write failures. (custom skill)
- [ ] Document on-demand use, the approved daily schedule/run time, where
  timestamped reports are written, and who may access them.
  (custom skill)
- [ ] Document report sharing and retention requirements after the organization
  confirms the policy; do not invent a retention duration. (custom skill)
- [ ] Remove or update KAN-only instructions and explicitly note that legacy
  resolved/updated issue lists and version sections are no longer included.
  (custom skill)
- [ ] Review documentation and sample outputs for secrets, personal details,
  unapproved health labels, or claims unsupported by Jira data.
  (custom skill)

**Dependencies:** Final operating instructions depend on the Integration
schedule, approved retention/sharing policy, and the Setup decisions recorded
for Jira and report semantics.

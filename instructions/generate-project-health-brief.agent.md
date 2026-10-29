---
name: Generate Project Health Brief
description: "Use when generating the weekly Development-wide Jira project health brief from a fresh Jira data snapshot."
tools: []
---
- **Input format:** Use a structured JSON payload where possible. Include the UTC report timestamp and seven-day window; configured Jira base URL and project-key allowlist; every project's key, name, retrieval and pagination status; current issue records with required status, resolution, priority, due, updated, and link data; milestone status and target dates; and changes observed during the window.
- Follow `./instructions/protect-sensitive-data-and-report-evidence.agent.md`.
- Include the confirmed Jira status/resolution semantics, blocker and dependency link types, and any approved milestone at-risk rule.
- Verify that the snapshot is fresh, the reporting window ends at the report timestamp and begins exactly seven days earlier, and the retrieved project set exactly matches the configured allowlist.
- If any project or required page failed to load, do not present the report as complete. Apply the previously agreed failed-project policy; if none is recorded, stop and surface the unresolved decision.
- Calculate issue counts from retrieved records grouped by actual Jira status names, and verify that the counts reconcile with the retrieved issue set.
- Identify overdue work only when an issue is unresolved and its due date is earlier than the report date in UTC. Identify blocked work only from an explicit blocked/impeded status or configured blocker relationship.
- Identify dependencies only from configured Jira link types. Identify missed milestones only when unreleased and the target date is earlier than the report date. Apply an at-risk milestone rule only when one has been approved.
- Flag stale work only for open, high-priority issues with no Jira update in the preceding seven days; describe this as a review prompt, not proof of stalled delivery.
- When a required field or signal definition is missing, state that the signal could not be evaluated; do not treat missing data as zero, clear, healthy, or complete.
- Separate observed Jira facts from interpretation. Base every interpretation and decision/action candidate on supplied Jira evidence; present follow-ups as suggestions, never as assigned or recorded actions.
- Produce a Markdown report with exactly these top-level sections, in order: `Executive summary`, `Project-by-project health`, `Milestones and progress changes`, `Risks, blockers, and dependencies`, and `Decisions and actions needed`.
- Under `Project-by-project health`, include one subsection for each allowlisted project with its key/name, status counts, and concise evidence-based summary.
- Include validated Jira source links where they support a reported fact or follow-up candidate. Construct links only from the configured Jira base URL and validated project or issue keys.
- Save the report under `reports/` with a UTC timestamped filename, avoiding overwrites, and report the saved path. Do not claim a daily schedule is configured unless it has been deployed and verified.
- Keep the report summary-metrics-only: do not include a full issue list, individual names, workload metrics, completion rankings, unsupported predictions, or unapproved Green/Amber/Red labels or aggregate scores.
- Do not create or update Jira issues, or distribute or publish the report.
- Return the saved report path after successful generation; surface retrieval, validation, or write failures explicitly rather than returning a success-shaped partial report.

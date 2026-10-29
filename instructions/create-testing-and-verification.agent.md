---
name: Create Testing and Verification
description: "Use when planning or running tests, validating implementation changes, or verifying the weekly Jira project health brief."
tools: []
---
- **Input format:** Accept a test request as natural language or structured JSON/YAML. When available, use these fields: `objective`, `changed_files`, `requirements`, `acceptance_criteria`, `test_commands`, `environment`, and `verification_gates`.
- **Processing steps:** Follow `./instructions/protect-sensitive-data-and-report-evidence.agent.md`. Read the applicable project specification, backlog, instruction catalog, changed code, and existing tests before choosing checks.
- Map each applicable acceptance criterion to an existing or planned test. Separate unit, integration, end-to-end, and operational/scheduler checks.
- Inspect the repository's test framework, configuration, and established patterns. Prefer the narrowest existing command that verifies the change; add or update focused tests when requested or needed to verify the requirement.
- Use deterministic fixtures and mocks for Jira API responses, pagination, failures, timestamps, and report output. Tests must not require live Jira access or credentials by default.
- For Jira report behavior, verify configuration validation without secret disclosure; exact allowlist scope with no implicit KAN inclusion; pagination and retrieval failures; UTC seven-day boundaries; status-count reconciliation; missing-data handling; each configured risk trigger; report section order and source links; timestamp uniqueness and no-overwrite behavior; output-write errors; and absence of Jira writes, personal details, credentials, or unsupported health labels.
- Add a mocked end-to-end test when verifying the report workflow across multiple allowlisted projects. Use temporary directories for file-output tests and clean up only files created by the test.
- Run the focused tests first, then relevant regression tests. Report the exact commands and their outcomes; investigate failures caused by the change.
- Run a non-production integration smoke test only after the setup gate, endpoint, dedicated read-only access, and explicit authorization are confirmed. Never use live credentials or live Jira data before those prerequisites are satisfied.
- Verify a scheduled daily run operationally only after the approved scheduler is deployed; do not infer schedule success from unit tests or configuration files.
- **Output format:** Return a concise Markdown verification report with `Summary`, `Checks`, and `Unverified or blocked` sections. In `Checks`, list each command or verification area with `PASS`, `FAIL`, or `NOT RUN` and a brief result. Include the relevant evidence and failure details without secret values.
- State clearly whether the requested acceptance criteria are verified, partially verified, or not verified. Explain every `FAIL` or `NOT RUN`; do not present skipped live or scheduled checks as passing.
- Keep output scoped to the request; do not include individual Jira names, full issue lists, or sensitive report contents.

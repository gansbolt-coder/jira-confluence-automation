---
name: Protect Sensitive Data and Report Evidence
description: "Use when handling credentials, environment files, project data, or claims about implementation, tests, reports, and approvals."
tools: []
---
- Do not inspect `.env` files or ask users to paste credentials. Use only the non-secret information required for the task.
- Never include credentials, tokens, authorization headers, or other secret values in source code, documentation, examples, tests, reports, logs, or error messages.
- Base claims on repository evidence, supplied source data, command output, or confirmed user decisions. Distinguish observed facts from interpretation and identify missing evidence.
- State clearly when work, tests, approvals, or operational checks are unverified, skipped, or blocked. Never claim a result, approval, backup, or deployment that did not occur.

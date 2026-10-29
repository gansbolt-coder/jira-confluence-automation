---
name: Create Instructions
description: "Use when creating or updating project instructions, instruction catalogs, or Copilot prompt wrappers."
tools: []
---
Source: [Creating Instructions guide](https://github.com/codenjoyme/vibecoding-training/blob/main/instructions/creating-instructions.agent.md)

- Keep workflow guidance platform-agnostic in `instructions/[verb-first-name].agent.md`; use short platform-specific files only to load it.
- Give each instruction one clear workflow or concern. Split large or mixed instructions into focused files and reference shared guidance rather than duplicating it.
- Write concise, specific, actionable bullet points in English. Use sub-bullets for related details and minimal examples only when they clarify an action.
- Before creating or changing an instruction, read the relevant instruction and `instructions/main.agent.md`; preserve useful existing guidance and make targeted edits.
- Use a verb-first, hyphen-separated filename, such as `create-release-notes.agent.md`.
- Add every instruction to `instructions/main.agent.md` with a one-line summary and keywords that help match likely user requests.
- For reusable workflows that need executable scripts, reference material, or bundled assets, create a skill rather than expanding a prose-only instruction.
- For GitHub Copilot, use `.github/copilot-instructions.md` as the always-loaded entry point to `instructions/main.agent.md`, and add a `.github/prompts/to-[name].prompt.md` wrapper for each instruction users should invoke directly.
- Keep each prompt wrapper minimal: set `agent: agent` and direct the agent to the corresponding instruction file.
- Enable Copilot instruction files in `.vscode/settings.json`; include the workspace settings required by the project's chosen workflow.
- Check that every catalog and wrapper path resolves, the YAML frontmatter parses, and the entry point asks Copilot to load the complete catalog on each prompt.
- Use this workflow for this workspace's GitHub Copilot setup; do not create configuration for another IDE unless requested.

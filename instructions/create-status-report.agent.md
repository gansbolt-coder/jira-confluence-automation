---
name: Create Status Report
description: "Use when generating a weekly status report from supplied project updates, accomplishments, blockers, and plans."
tools: []
---
Generate a concise weekly status report from the information provided by the user.

## Requirements
- Output Markdown only.
- Use exactly these sections, in this order: Accomplishments, Blockers, Next Week.
- Use Markdown headings for the three section names.
- Write report content as bullet points only; do not use paragraphs, tables, or numbered lists.
- Keep the entire report, including title and headings, to a maximum of 20 lines.
- Use a professional, direct tone.
- Remove fluff words, filler, repetition, and vague claims.
- Preserve factual meaning; do not invent accomplishments, blockers, owners, dates, metrics, or commitments.
- If a section has no supplied information, include one bullet stating "No updates provided."
- Prefer specific outcomes, impact, and measurable progress when supplied.
- Keep blockers concise and state impact or needed resolution only when provided.
- Phrase next-week items as planned work, not completed work.
- Return only the finished report; do not add commentary or an explanation.

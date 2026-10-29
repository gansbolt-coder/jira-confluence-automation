---
name: Calculate Compound Interest
description: "Use when a user asks to calculate compound interest or compare a principal, annual rate, compounding frequency, and investment duration."
tools: []
---
Calculate compound interest by running `tools/compound_interest.py` from the `work/module08-task` directory.

## Workflow
- Use the tool when the user requests a compound-interest calculation and provides, or can reasonably clarify, all four inputs:
  - `principal`: initial amount of money.
  - `annual_rate`: annual percentage rate, such as `7.34` for 7.34% (not `0.0734`).
  - `compounds_per_year`: positive integer frequency, such as `12` for monthly.
  - `years`: total duration in years; use a decimal for partial years.
- Invoke it with positional arguments in this exact order:
  - `python tools/compound_interest.py <principal> <annual_rate> <compounds_per_year> <years>`
  - On Windows, use `py` instead of `python` if needed.
- Do not estimate or invent missing inputs. Ask for information needed to run the calculation.
- Surface command errors rather than presenting a result if the inputs are invalid or execution fails.

## Present Results
- Report both values printed by the tool: **Final amount** and **Interest earned**.
- Preserve the tool's two-decimal currency formatting and clearly identify the input assumptions, including the annual rate, compounding frequency, and duration.
- Do not describe the result as guaranteed investment growth; it is the mathematical result for the supplied assumptions.

---
name: utb-code-enricher
description: Extract LWC/Apex logic from source code and merge it into design-derived rules. Use when user needs branch conditions, API behavior, required/format checks, and error-message expectations from code.
---

# UTB Code Enricher

Combine design and implementation logic.

## Inputs
- `design_enriched.json`
- code zip/folder

## Output
Write `merged_rules.json` including:
- ui_actions_with_code_links
- server_validations
- api_calls
- branch_conditions
- error_messages

## Rules
- Keep file path + line references for every inferred rule.
- If design and code conflict, record both and mark confidence.
- Prefer deterministic extraction over free-form summarization.

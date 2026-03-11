---
name: utb-design-parser
description: Parse screen detailed design Excel into normalized design rules. Use when extracting pages, fields, control IDs, labels, required flags, validation notes, and screen actions from design workbooks.
---

# UTB Design Parser

Extract structured rules from design workbook.

## Output
Write `design_core.json` with:
- pages
- fields
- controls
- validation_notes
- action_candidates

## Rules
- Preserve original sheet/cell coordinates for traceability.
- Keep Japanese source text in raw fields; add normalized keys separately.
- Do not infer code logic in this stage.

---
name: utb-image-checksheet-parser
description: Parse embedded images and check-sheet pages in design Excel to enrich test conditions and operation steps. Use when design docs include screenshots, annotations, OCR text, and checklist sheets.
---

# UTB Image + Checksheet Parser

Enrich design rules with screenshot/checksheet evidence.

## Output
Write `design_enriched.json` from `design_core.json` plus:
- image_ocr_blocks
- screenshot_annotations
- checksheet_conditions
- checksheet_expected_results

## Rules
- Keep image-to-sheet and row-range linkage.
- Mark OCR confidence; keep low-confidence text as optional hints.
- Never overwrite original `design_core` fields; append enrichment.

---
name: utb-excel-exporter
description: Fill the target unit-test-book Excel template with generated cases using strict schema mapping. Use when exporting final deliverables and preserving template layout, merged cells, and formatting constraints.
---

# UTB Excel Exporter

Export final workbook from cases.

## Inputs
- `template.xlsx`
- `template_schema.json`
- `cases.json`

## Output
- `unit_test_book_generated.xlsx`

## Rules
- Preserve original workbook style and non-target sheets.
- Apply step/condition/expected-result mapping exactly.
- Validate required columns and non-empty mandatory cells.
- Emit `export_report.json` (filled rows, skipped rows, warnings).

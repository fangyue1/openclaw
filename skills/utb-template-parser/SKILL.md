---
name: utb-template-parser
description: Parse existing unit-test-book Excel template and build a strict column mapping schema. Use when identifying target sheets, header rows, required columns, and fill rules such as operation steps, test conditions, expected results, and step numbering.
---

# UTB Template Parser

Understand template structure before generation.

## Output
Write `template_schema.json` with:
- target_sheet
- header_row
- column_map
- required_columns
- step_numbering_rules
- merge_cell_rules

## Rules
- Detect Japanese headers (e.g., 画面操作手順, テスト条件, 想定結果).
- Reject export when required columns are missing.
- Keep exact column letters/indexes for exporter.

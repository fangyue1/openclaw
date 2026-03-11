---
name: web-unit-testbook
description: Generate web page unit test books from detailed design Excel files, embedded images/OCR text, LWC/Apex source code, and a user-provided Excel template. Use when user asks to read design docs, extract field/API/check rules, parse code branches and data bindings, generate test cases, and fill a unit test book template (.xlsx).
---

# Web Unit Test Book Generator

Build and run a deterministic pipeline for unit test book generation.

## Positioning

- Keep this skill as a **single-skill fallback** for one-shot execution.
- In the new architecture, prefer multi-skill collaboration:
  - `utb-orchestrator`
  - `utb-design-parser`
  - `utb-image-checksheet-parser`
  - `utb-code-enricher`
  - `utb-template-parser`
  - `utb-case-generator`
  - `utb-excel-exporter`

## Workflow

1. Parse design Excel into `design_rules.json`.
2. Parse LWC/Apex code into `code_rules.json`.
3. Merge rules and generate markdown spec + normalized case JSON.
4. Fill the user template workbook and export final test book.

## Inputs

- Design workbook (`.xlsx`) with field definitions, API names, check notes, optional screenshots.
- Code folder or zip with LWC/Apex files.
- Unit test template workbook (`.xlsx`) — recommended: `workspace/inputs/template/template_v3_confirmed.xlsx`.

## Commands

Run from this skill directory.

```powershell
python scripts/parse_design_excel.py --input <design.xlsx> --out design_rules.json --ocr-lang jpn+eng
python scripts/extract_code_rules.py --src <code_dir_or_zip> --out code_rules.json
python scripts/generate_ui_only_cases.py --design design_rules.json --out-md UnitTestSpec_UIOnly.md --out-cases cases.json
python scripts/export_to_excel.py --template <template.xlsx> --cases cases.json --out unit_test_book_v3_template_based.xlsx
```

Or run one-shot:

```powershell
python scripts/run_pipeline.py --design <design.xlsx> --code <code_dir_or_zip> --template <template.xlsx> --outdir out
```

## Notes

- OCR is optional: install Tesseract and pass `--ocr-lang`.
- If template headers are unknown, script performs best-effort column mapping by keyword.
- Keep all output artifacts in one run directory for traceability.

## Output Artifacts

- `design_rules.json`
- `code_rules.json`
- `cases.json`
- `UnitTestSpec_HighPrecision.md`
- `単体試験書_*.xlsx`

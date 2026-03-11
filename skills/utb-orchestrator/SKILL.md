---
name: utb-orchestrator
description: Orchestrate end-to-end unit test book generation from (1) screen detailed design Excel with images/check sheets, (2) LWC/Apex code package, and (3) existing unit-test-book Excel template. Use when user asks for one-shot generation, multi-skill coordination, stage-by-stage traceability, or rerun with the same run_id.
---

# UTB Orchestrator

Run the pipeline in strict order and keep all artifacts under one run folder.

## Inputs
- design.xlsx
- code.zip (or code folder)
- template.xlsx

## Execution order
1. `utb-design-parser` -> `design_core.json`
2. `utb-image-checksheet-parser` -> `design_enriched.json`
3. `utb-code-enricher` -> `merged_rules.json`
4. `utb-template-parser` -> `template_schema.json`
5. `utb-case-generator` -> `cases.json`, `UnitTestSpec.md`
6. `utb-excel-exporter` -> `unit_test_book_generated.xlsx`

## Required checks
- Validate all required columns in template schema before export.
- Fail fast if sheet mapping is ambiguous.
- Keep a `run_manifest.json` with input hashes and output paths.

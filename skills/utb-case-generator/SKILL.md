---
name: utb-case-generator
description: Generate normalized unit test cases from merged design+code rules and template schema. Use when building step-by-step test operations, conditions, expected results, normal/error branches, and stable case IDs.
---

# UTB Case Generator

Create template-ready case objects.

## Inputs
- `merged_rules.json`
- `template_schema.json`

## Output
- `cases.json`
- `UnitTestSpec.md`

## Rules
- Generate both normal and abnormal scenarios.
- Keep step order contiguous (1..N) per scenario.
- Emit explicit fields aligned with template columns.
- Include source trace (design sheet row / code line) per case.

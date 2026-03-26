---
name: self-evolution
description: Continuous self-improvement loop for task execution quality. Use when the user asks for self-evolving behavior, automatic retrospectives, learning from mistakes, or periodic optimization of prompts/workflows. After meaningful tasks, record what worked/failed, extract reusable rules, and update memory files safely.
---

# Self Evolution

Run a lightweight loop after meaningful tasks.

## 1) Capture

Write one entry to `memory/self-evolution-log.md` with:
- Date/time (JST)
- Task summary
- Outcome (success/partial/fail)
- Root cause of issues
- Fix used
- Reusable rule (one sentence)

Skip trivial chats.

## 2) Distill

When log has 5+ new entries, update `MEMORY.md` with only stable patterns:
- Keep evergreen rules
- Remove duplicates
- Keep each rule under 2 lines

## 3) Apply

Before similar future tasks:
- Search memory for matching pattern
- Apply the rule directly
- Mention assumptions briefly if confidence is low

## 4) Safety

- Never store secrets, tokens, or private personal data in learning notes
- Keep notes operational, not sensitive
- Prefer reversible/process rules over risky autonomy

## Output Template

Use this exact block in `memory/self-evolution-log.md`:

```markdown
## YYYY-MM-DD HH:mm JST — <task>
- Outcome: success | partial | fail
- What worked:
- What failed:
- Root cause:
- Fix applied:
- Reusable rule:
```

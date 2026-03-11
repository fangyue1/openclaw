import argparse
import json
from pathlib import Path


def _ocr_lines(design, max_lines=40):
    lines = []
    for o in design.get("ocr", []) or []:
        txt = (o.get("text") or "").strip()
        if not txt:
            continue
        for ln in txt.splitlines():
            s = ln.strip()
            if len(s) >= 3:
                lines.append(s)
    # de-dup keep order
    seen = set()
    uniq = []
    for s in lines:
        k = s.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(s)
        if len(uniq) >= max_lines:
            break
    return uniq


def build_cases(design, code):
    cases = []
    idx = 1

    for f in design.get("field_rules", [])[:300]:
        api = (f.get("api_names") or ["N/A"])[0]
        required = f.get("required_hint", False)
        checks = f.get("check_patterns", [])

        cases.append(
            {
                "case_id": f"TC-{idx:04d}",
                "category": "字段校验",
                "title": f"{api} 正常输入",
                "precondition": "页面可访问，用户已登录",
                "steps": f"输入 {api} 的合法值并提交",
                "expected": "提交成功，数据保存正确",
                "priority": "P1" if required else "P2",
            }
        )
        idx += 1

        if required:
            cases.append(
                {
                    "case_id": f"TC-{idx:04d}",
                    "category": "异常校验",
                    "title": f"{api} 必填校验",
                    "precondition": "页面可访问",
                    "steps": f"清空 {api} 后提交",
                    "expected": "出现必填错误提示，无法提交",
                    "priority": "P1",
                }
            )
            idx += 1

        if checks:
            cases.append(
                {
                    "case_id": f"TC-{idx:04d}",
                    "category": "边界校验",
                    "title": f"{api} 规则边界",
                    "precondition": "页面可访问",
                    "steps": f"按规则 {checks[0]} 构造边界值并提交",
                    "expected": "边界行为符合设计说明",
                    "priority": "P2",
                }
            )
            idx += 1

    # OCR-driven UI wording / screenshot checks from embedded design images
    ocr_lines = _ocr_lines(design)
    for ln in ocr_lines[:20]:
        cases.append(
            {
                "case_id": f"TC-{idx:04d}",
                "category": "画面文言確認",
                "title": f"画面表示文言: {ln[:24]}",
                "precondition": "対象画面を表示できること",
                "steps": "画面を開き、仕様書画像の文言と照合する",
                "expected": f"仕様書画像由来の文言『{ln[:80]}』が正しく表示される",
                "priority": "P1",
            }
        )
        idx += 1

    summary = code.get("summary", {})
    for _ in range(summary.get("branches", 0)):
        cases.append(
            {
                "case_id": f"TC-{idx:04d}",
                "category": "逻辑分支",
                "title": "代码分支覆盖",
                "precondition": "构造分支输入条件",
                "steps": "触发 if/else 或 switch 分支",
                "expected": "分支结果与预期一致",
                "priority": "P1",
            }
        )
        idx += 1

    return cases


def to_markdown(cases):
    lines = ["# Unit Test Spec (High Precision)", "", "| CaseID | Category | Title | Expected |", "|---|---|---|---|"]
    for c in cases:
        lines.append(f"| {c['case_id']} | {c['category']} | {c['title']} | {c['expected']} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--out-cases", required=True)
    args = ap.parse_args()

    design = json.loads(Path(args.design).read_text(encoding="utf-8"))
    code = json.loads(Path(args.code).read_text(encoding="utf-8"))

    cases = build_cases(design, code)
    Path(args.out_cases).write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.out_md).write_text(to_markdown(cases), encoding="utf-8")

    print(f"Wrote {args.out_cases} and {args.out_md}")


if __name__ == "__main__":
    main()

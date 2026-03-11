import argparse
import json
import re
from pathlib import Path


UI_VERBS = ["クリック", "入力", "選択", "押す", "表示", "遷移", "確認", "戻る", "次へ", "予約"]
BACKEND_HINTS = ["API", "Apex", "SOQL", "insert", "update", "delete", "backend", "DB", "DML"]


def norm(s):
    return str(s or "").strip()


def is_ui_line(s: str) -> bool:
    if not s:
        return False
    if any(k.lower() in s.lower() for k in BACKEND_HINTS):
        return False
    return any(v in s for v in UI_VERBS)


def collect_ui_lines(design):
    lines = []

    for fr in design.get("field_rules", []) or []:
        raw = norm(fr.get("raw"))
        if raw and is_ui_line(raw):
            lines.append(raw)

    for o in design.get("ocr", []) or []:
        txt = norm(o.get("text"))
        if not txt:
            continue
        for ln in txt.splitlines():
            s = norm(ln)
            if is_ui_line(s):
                lines.append(s)

    uniq = []
    seen = set()
    for s in lines:
        k = re.sub(r"\s+", "", s.lower())
        if k in seen:
            continue
        seen.add(k)
        uniq.append(s)
    return uniq


def build_cases(design):
    ui_lines = collect_ui_lines(design)

    cases = []

    # 正常系
    for s in ui_lines[:25]:
        cases.append({
            "case_id": f"TC-{len(cases)+1:04d}",
            "category": "正常系",
            "title": "画面操作フロー確認",
            "precondition": "画面を表示できること",
            "steps": s,
            "expected": "画面表示・操作結果が仕様どおりであること",
            "priority": "P2",
        })

    # 異常系（必須/形式）: design field hints only, no backend wording
    for fr in (design.get("field_rules") or [])[:120]:
        raw = norm(fr.get("raw"))
        required = bool(fr.get("required_hint"))
        apis = fr.get("api_names") or []
        label = apis[0] if apis else "入力項目"

        if required:
            cases.append({
                "case_id": f"TC-{len(cases)+1:04d}",
                "category": "異常系",
                "title": "必須未入力チェック",
                "precondition": "入力画面を表示できること",
                "steps": f"{label} を未入力のまま次へ進む",
                "expected": "必須入力エラーが画面に表示されること",
                "priority": "P1",
            })

        checks = fr.get("check_patterns") or []
        if checks:
            cases.append({
                "case_id": f"TC-{len(cases)+1:04d}",
                "category": "異常系",
                "title": "入力形式チェック",
                "precondition": "入力画面を表示できること",
                "steps": f"{label} に不正な形式の値を入力して次へ進む",
                "expected": "入力形式エラーが画面に表示されること",
                "priority": "P1",
            })

        if len(cases) >= 60:
            break

    return cases[:80]


def to_md(cases):
    lines = ["# UI only Unit Test Cases", "", "|No|分類|手順|期待結果|", "|---|---|---|---|"]
    for i, c in enumerate(cases, 1):
        lines.append(f"|{i}|{c['category']}|{c['steps'].replace('|','/')}|{c['expected'].replace('|','/')}|")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--out-cases", required=True)
    ap.add_argument("--out-md", required=True)
    args = ap.parse_args()

    design = json.loads(Path(args.design).read_text(encoding="utf-8"))
    cases = build_cases(design)

    Path(args.out_cases).write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.out_md).write_text(to_md(cases), encoding="utf-8")
    print(f"Wrote {args.out_cases} and {args.out_md}")


if __name__ == "__main__":
    main()

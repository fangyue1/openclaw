import argparse
import json
import re
from pathlib import Path


def pick_api(raw):
    m = re.findall(r"[A-Za-z_][A-Za-z0-9_]*(?:__c|__r)?", raw or "")
    return m[0] if m else "対象項目"


def build_cases(design, code):
    cases = []

    # 1) field rules from design
    for f in (design.get("field_rules") or [])[:120]:
        raw = f.get("raw", "")
        api = (f.get("api_names") or [pick_api(raw)])[0]
        required = bool(f.get("required_hint"))

        cases.append({
            "category": "入力確認",
            "title": f"{api} 正常入力",
            "precondition": "対象画面を表示できること",
            "steps": f"{api} に有効な値を入力し、次へ進む",
            "expected": "エラーなく次画面へ遷移できること",
            "priority": "P2",
        })

        if required:
            cases.append({
                "category": "異常系",
                "title": f"{api} 必須チェック",
                "precondition": "対象画面を表示できること",
                "steps": f"{api} を未入力のまま次へ進む",
                "expected": f"{api} の必須エラーメッセージが表示されること",
                "priority": "P1",
            })

    # 2) OCR-based wording/flow checks
    seen = set()
    for o in (design.get("ocr") or []):
        txt = (o.get("text") or "").strip()
        if not txt:
            continue
        for ln in txt.splitlines():
            s = ln.strip()
            if len(s) < 5:
                continue
            if not any(k in s for k in ["クリック", "入力", "確認", "遷移", "表示", "エラー", "予約", "ボタン"]):
                continue
            k = s.lower()
            if k in seen:
                continue
            seen.add(k)
            cases.append({
                "category": "画面確認",
                "title": "設計書画像の記載確認",
                "precondition": "対象画面を表示できること",
                "steps": f"設計書画像の記載に従い、次を操作/確認する: {s[:100]}",
                "expected": "設計書記載どおりに表示・遷移・入力チェックができること",
                "priority": "P2",
            })
            if len(seen) >= 40:
                break
        if len(seen) >= 40:
            break

    # 3) code branch coverage summary
    branches = int(((code.get("summary") or {}).get("branches") or 0))
    for _ in range(min(branches, 10)):
        cases.append({
            "category": "分岐確認",
            "title": "コード分岐の遷移確認",
            "precondition": "分岐条件に合うデータを準備",
            "steps": "条件を変えて画面操作を行う",
            "expected": "分岐ごとに期待した結果が表示されること",
            "priority": "P1",
        })

    # assign case ids
    out = []
    for i, c in enumerate(cases, 1):
        c2 = dict(c)
        c2["case_id"] = f"TC-{i:04d}"
        out.append(c2)
    return out


def to_md(cases):
    lines = ["# Design+Code Generated Unit Test Cases", "", "|No|分類|タイトル|手順|期待結果|", "|---|---|---|---|---|"]
    for i, c in enumerate(cases, 1):
        lines.append(f"|{i}|{c['category']}|{c['title']}|{c['steps'].replace('|','/')}|{c['expected'].replace('|','/')}|")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--design', required=True)
    ap.add_argument('--code', required=True)
    ap.add_argument('--out-cases', required=True)
    ap.add_argument('--out-md', required=True)
    args = ap.parse_args()

    design = json.loads(Path(args.design).read_text(encoding='utf-8'))
    code = json.loads(Path(args.code).read_text(encoding='utf-8'))
    cases = build_cases(design, code)

    Path(args.out_cases).write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding='utf-8')
    Path(args.out_md).write_text(to_md(cases), encoding='utf-8')
    print(f"Wrote {args.out_cases} and {args.out_md}")


if __name__ == '__main__':
    main()

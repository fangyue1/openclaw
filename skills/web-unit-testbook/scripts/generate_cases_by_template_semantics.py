import argparse
import json
import re
from pathlib import Path


def n(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def collect_error_messages_from_code(code):
    msgs = []
    pstr = re.compile(r"['\"]([^'\"]{3,120})['\"]")
    hint = re.compile(r"error|required|必須|未入力|形式|invalid|message|toast", re.I)
    for f in code.get("files", []) or []:
        fp = f.get("file")
        if not fp:
            continue
        p = Path(fp)
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for line in txt.splitlines():
            if hint.search(line):
                for m in pstr.findall(line):
                    s = n(m)
                    if len(s) >= 3:
                        msgs.append(s)
    uniq, seen = [], set()
    for m in msgs:
        k = m.lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(m)
    return uniq


def collect_design_items(design):
    items = []
    for fr in design.get("field_rules", []) or []:
        raw = n(fr.get("raw"))
        api = (fr.get("api_names") or ["入力項目"])[0]
        required = bool(fr.get("required_hint"))
        checks = fr.get("check_patterns") or []
        if raw or required or checks:
            items.append({"raw": raw, "api": api, "required": required, "checks": checks})
    return items


def split_step_condition(raw: str):
    raw = n(raw)
    if not raw:
        return None, None

    # common parser output joins with " | " -> first chunk as action, rest as concrete examples
    if " | " in raw:
        parts = [p.strip() for p in raw.split("|") if p.strip()]
        if len(parts) >= 2:
            step = parts[0]
            cond = " / ".join(parts[1:])
            return step, cond

    # Heuristic: when line contains concrete values/examples, keep them in test condition
    if any(k in raw for k in ["~", "（", "）", "○", "△", "×", "@", "http", "桁", "半角", "全角", "例", "1111", "202", "3/", "4/"]):
        return "対象画面で指定操作を実行する", raw

    return raw, "ー"


def build_cases(design, code, sem):
    items = collect_design_items(design)
    msgs = collect_error_messages_from_code(code)
    if not msgs:
        msgs = ["必須項目が未入力です", "入力形式が正しくありません"]

    cases = []

    # 1) screen-step rows: keep action in 確認手順, move concrete examples to テスト条件
    for it in items[:35]:
        raw = it["raw"]
        if not raw:
            continue
        if any(k in raw for k in ["クリック", "入力", "遷移", "表示", "確認", "選択", "ボタン"]):
            step, cond = split_step_condition(raw)
            if not step:
                continue
            cases.append({
                "category": "コールバック予約",
                "title": "（画面手順）操作確認",
                "steps": step,
                "precondition": cond or "ー",
                "expected": "画面設計書どおりに表示・遷移・操作できること",
            })

    # 2) exception-first rows with explicit message check
    i = 0
    for it in items[:80]:
        field = it["api"] or "入力項目"
        if it["required"]:
            msg = msgs[i % len(msgs)]
            cases.append({
                "category": "コールバック予約",
                "title": f"（異常系）{field} 未入力",
                "steps": f"{field} を未入力のまま「入力内容の確認」ボタンをクリックする",
                "precondition": f"{field} を空欄にする",
                "expected": f"エラーメッセージ「{msg}」が表示され、次画面へ遷移しないこと",
            })
            i += 1
        if it["checks"]:
            msg = msgs[i % len(msgs)]
            cases.append({
                "category": "コールバック予約",
                "title": f"（異常系）{field} 形式不正",
                "steps": f"{field} に不正な形式の値を入力して「入力内容の確認」ボタンをクリックする",
                "precondition": f"{field} に不正値を入力する（{it['checks'][0]}）",
                "expected": f"エラーメッセージ「{msg}」が表示されること",
            })
            i += 1

        if len(cases) >= 120:
            break

    # preserve only template-write fields
    out = []
    for idx, c in enumerate(cases, 1):
        out.append({
            "case_id": f"TC-{idx:04d}",
            "category": c["category"],
            "title": c["title"],
            "steps": c["steps"],
            "precondition": c["precondition"],
            "expected": c["expected"],
        })
    return out


def to_md(cases):
    lines = ["# Unit Test Spec (Template Semantic)", "", "|No|小分類|確認手順|テスト条件|想定結果|", "|---|---|---|---|---|"]
    for i, c in enumerate(cases, 1):
        lines.append(f"|{i}|{c['title']}|{c['steps']}|{c['precondition']}|{c['expected']}|")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--template-semantics", required=True)
    ap.add_argument("--out-cases", required=True)
    ap.add_argument("--out-md", required=True)
    args = ap.parse_args()

    design = load(args.design)
    code = load(args.code)
    sem = load(args.template_semantics)

    cases = build_cases(design, code, sem)
    Path(args.out_cases).write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.out_md).write_text(to_md(cases), encoding="utf-8")
    print(f"Wrote {args.out_cases} and {args.out_md}")


if __name__ == "__main__":
    main()

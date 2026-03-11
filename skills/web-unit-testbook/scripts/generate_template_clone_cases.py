import argparse
import json
import re
from pathlib import Path


def n(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def collect_error_messages(design, code):
    msgs = []

    # 1) prefer user-facing messages from design text: 「...」 or "..."
    qpat = re.compile(r"[「\"]([^」\"]{4,100})[」\"]")
    for fr in design.get("field_rules", []) or []:
        raw = n(fr.get("raw"))
        if any(k in raw for k in ["エラー", "未入力", "形式", "メッセージ", "必須"]):
            for m in qpat.findall(raw):
                s = n(m)
                if s:
                    msgs.append(s)

    # 2) fallback from code string literals, filtered to human-readable message-like text
    pstr = re.compile(r"['\"]([^'\"]{4,120})['\"]")
    hint = re.compile(r"error|required|必須|未入力|形式|invalid|message|toast|check", re.I)
    for f in code.get("files", []) or []:
        fp = f.get("file")
        if not fp:
            continue
        p = Path(fp)
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for line in txt.splitlines():
            if not hint.search(line):
                continue
            for m in pstr.findall(line):
                s = n(m)
                # skip css/class/id-like tokens
                if re.search(r"[.#_/]", s):
                    continue
                if s.lower() in {"error", "warning", "required"}:
                    continue
                if len(s) < 6:
                    continue
                msgs.append(s)

    out, seen = [], set()
    for m in msgs:
        k = m.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(m)
    return out


def collect_design_checks(design):
    items = []
    for fr in design.get("field_rules", []) or []:
        raw = n(fr.get("raw"))
        api = (fr.get("api_names") or ["入力項目"])[0]
        required = bool(fr.get("required_hint"))
        checks = fr.get("check_patterns") or []
        if required or checks or any(k in raw for k in ["未入力", "必須", "エラー", "形式", "桁", "半角", "全角"]):
            items.append({"api": api, "raw": raw, "required": required, "checks": checks})
    return items


def make_condition(raw, api, check):
    # User fills テスト条件 manually; keep blank by default
    return ""


def build_cases(design, code, max_cases=120):
    msgs = collect_error_messages(design, code)
    if not msgs:
        msgs = [""]

    items = collect_design_checks(design)
    cases = []
    mi = 0

    for it in items:
        api = it["api"] or "入力項目"

        if it["required"]:
            msg = msgs[mi % len(msgs)]
            mi += 1
            cases.append({
                "category": "コールバック予約",
                "title": f"（異常系）{api} 未入力",
                "steps": "入力内容の確認ボタンをクリックする",
                "precondition": make_condition(it["raw"], api, "required"),
                "expected": f"エラーメッセージ「{msg}」が表示されること",
            })

        if it["checks"] or any(k in it["raw"] for k in ["形式", "桁", "半角", "全角"]):
            msg = msgs[mi % len(msgs)]
            mi += 1
            cases.append({
                "category": "コールバック予約",
                "title": f"（異常系）{api} 形式不正",
                "steps": "入力内容の確認ボタンをクリックする",
                "precondition": make_condition(it["raw"], api, "format"),
                "expected": f"エラーメッセージ「{msg}」が表示されること",
            })

        if len(cases) >= max_cases:
            break

    out = []
    for i, c in enumerate(cases, 1):
        out.append({
            "case_id": f"TC-{i:04d}",
            "category": c["category"],
            "title": c["title"],
            "steps": c["steps"],
            "precondition": c["precondition"],
            "expected": c["expected"],
        })
    return out


def to_md(cases):
    lines = ["# Unit Test Spec (Template Clone Mode)", "", "|No|小分類|確認手順|テスト条件|想定結果|", "|---|---|---|---|---|"]
    for i, c in enumerate(cases, 1):
        lines.append(f"|{i}|{c['title']}|{c['steps']}|{c['precondition']}|{c['expected']}|")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--out-cases", required=True)
    ap.add_argument("--out-md", required=True)
    args = ap.parse_args()

    design = load(args.design)
    code = load(args.code)
    cases = build_cases(design, code)

    Path(args.out_cases).write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.out_md).write_text(to_md(cases), encoding="utf-8")
    print(f"Wrote {args.out_cases} and {args.out_md}")


if __name__ == "__main__":
    main()

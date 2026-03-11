import argparse
import json
import re
from pathlib import Path


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def collect_design_steps(design: dict):
    steps = []

    # 1) from sheet rows
    for fr in design.get("field_rules", []) or []:
        raw = _norm(fr.get("raw", ""))
        if not raw:
            continue
        if any(k in raw for k in ["クリック", "入力", "選択", "押", "遷移", "表示", "確認", "戻る", "次へ"]):
            steps.append(raw)

    # 2) from OCR lines
    for o in design.get("ocr", []) or []:
        txt = _norm(o.get("text", ""))
        if not txt:
            continue
        for ln in txt.split("\n"):
            s = _norm(ln)
            if not s:
                continue
            if any(k in s for k in ["クリック", "入力", "選択", "押", "遷移", "表示", "確認", "戻る", "次へ", "予約"]):
                steps.append(s)

    uniq = []
    seen = set()
    for s in steps:
        k = re.sub(r"\W+", "", s.lower())
        if k in seen:
            continue
        seen.add(k)
        uniq.append(s)
    return uniq


def collect_error_messages(code: dict):
    msgs = []

    pat_string = re.compile(r"['\"]([^'\"]{3,120})['\"]")
    err_hint = re.compile(r"error|required|必須|未入力|形式|invalid|toast|message|チェック", re.IGNORECASE)

    for f in code.get("files", []) or []:
        file_path = f.get("file")
        if not file_path:
            continue
        p = Path(file_path)
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore")

        # direct strings around error-ish lines
        for line in txt.splitlines():
            if err_hint.search(line):
                for m in pat_string.findall(line):
                    s = _norm(m)
                    if len(s) >= 3:
                        msgs.append(s)

        # fallback: common japanese UI strings
        for m in pat_string.findall(txt):
            s = _norm(m)
            if len(s) < 4:
                continue
            if any(k in s for k in ["必須", "入力", "不正", "エラー", "確認", "選択", "ください", "できません"]):
                msgs.append(s)

    uniq = []
    seen = set()
    for s in msgs:
        k = s.lower()
        if k in seen:
            continue
        seen.add(k)
        uniq.append(s)
    return uniq


def derive_field_hints(design: dict):
    hints = []
    for fr in design.get("field_rules", []) or []:
        api = (fr.get("api_names") or [None])[0]
        required = bool(fr.get("required_hint"))
        checks = fr.get("check_patterns") or []
        if api or required or checks:
            hints.append({"api": api or "入力項目", "required": required, "checks": checks})
    return hints


def build_cases(design: dict, code: dict, max_cases=120):
    steps = collect_design_steps(design)
    err_msgs = collect_error_messages(code)
    hints = derive_field_hints(design)

    if not err_msgs:
        err_msgs = ["必須項目が未入力です", "入力形式が正しくありません"]

    cases = []
    idx = 1

    # A. flow steps from design images/text
    for s in steps[:40]:
        cases.append({
            "category": "コールバック予約",
            "title": f"（画面手順）{s[:30]}",
            "steps": s,
            "precondition": "ー",
            "expected": "表示・遷移・操作結果が画面設計書どおりであること",
        })
        idx += 1

    # B. exception cases: empty input + invalid format with concrete message checks
    for i, h in enumerate(hints[:50]):
        field = h["api"]
        if h["required"]:
            msg = err_msgs[i % len(err_msgs)]
            cases.append({
                "category": "コールバック予約",
                "title": f"（異常系）{field} 必須未入力",
                "steps": f"{field} を未入力のまま次へ進む",
                "precondition": "対象項目を空欄で送信する",
                "expected": f"エラーメッセージ「{msg}」が表示され、次画面へ進まないこと",
            })
            idx += 1

        if h["checks"]:
            msg = err_msgs[(i + 3) % len(err_msgs)]
            cases.append({
                "category": "コールバック予約",
                "title": f"（異常系）{field} 入力形式不正",
                "steps": f"{field} に不正形式の値を入力して次へ進む",
                "precondition": f"不正値を入力する（pattern: {h['checks'][0]}）",
                "expected": f"エラーメッセージ「{msg}」が表示されること",
            })
            idx += 1

        if len(cases) >= max_cases:
            break

    # assign ids for traceability (exporter may ignore)
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


def to_markdown(cases):
    lines = ["# Unit Test Spec (Template-Exception Focus)", "", "|No|小分類|確認手順|テスト条件|想定結果|", "|---|---|---|---|---|"]
    for i, c in enumerate(cases, 1):
        lines.append(
            f"|{i}|{c['title'].replace('|','/')}|{c['steps'].replace('|','/')}|{c['precondition'].replace('|','/')}|{c['expected'].replace('|','/')}|"
        )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--out-cases", required=True)
    ap.add_argument("--out-md", required=True)
    args = ap.parse_args()

    design = load_json(args.design)
    code = load_json(args.code)

    cases = build_cases(design, code)
    Path(args.out_cases).write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.out_md).write_text(to_markdown(cases), encoding="utf-8")
    print(f"Wrote {args.out_cases} and {args.out_md}")


if __name__ == "__main__":
    main()

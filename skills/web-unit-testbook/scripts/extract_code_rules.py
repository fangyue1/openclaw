import argparse
import json
import re
import zipfile
from pathlib import Path


CODE_EXTS = {".js", ".ts", ".html", ".cls", ".apex"}


def collect_files(src: Path):
    if src.is_file() and src.suffix.lower() == ".zip":
        temp = src.parent / "_code_unzip"
        temp.mkdir(exist_ok=True)
        with zipfile.ZipFile(src, "r") as zf:
            zf.extractall(temp)
        base = temp
    else:
        base = src
    return [p for p in base.rglob("*") if p.suffix.lower() in CODE_EXTS]


def parse_js_ts(text: str):
    branches = re.findall(r"\bif\s*\(([^)]*)\)|\bswitch\s*\(([^)]*)\)", text)
    wire_methods = re.findall(r"@wire\s*\(([^)]+)\)", text)
    methods = re.findall(r"\n\s*(?:async\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{", text)
    return {
        "method_names": sorted(set(methods)),
        "branch_conditions": [a or b for a, b in branches if (a or b)],
        "wire_bindings": [w.strip() for w in wire_methods],
    }


def parse_apex(text: str):
    methods = re.findall(
        r"(?:public|private|global|protected)\s+(?:static\s+)?(?:[A-Za-z_][A-Za-z0-9_<>,.]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)",
        text,
        flags=re.IGNORECASE,
    )
    dml = re.findall(r"\b(insert|update|upsert|delete|merge|undelete)\b", text, flags=re.IGNORECASE)
    exceptions = re.findall(r"\bthrow\b|\btry\b|\bcatch\b|AuraHandledException|Exception", text)

    return {
        "method_names": sorted(set([m[0] for m in methods])),
        "dml_ops": [x.lower() for x in dml],
        "exception_paths": len(exceptions),
    }


def parse_text(path: Path, text: str):
    ext = path.suffix.lower()
    base = {
        "branch_count": len(re.findall(r"\bif\b|\belse\b|\bswitch\b", text)),
        "wire_bindings": [],
        "dml_ops": [],
        "exception_paths": 0,
        "method_names": [],
        "branch_conditions": [],
    }

    if ext in {".js", ".ts"}:
        js = parse_js_ts(text)
        base.update(
            {
                "wire_bindings": js["wire_bindings"],
                "method_names": js["method_names"],
                "branch_conditions": js["branch_conditions"],
            }
        )
    elif ext in {".cls", ".apex"}:
        apex = parse_apex(text)
        base.update(
            {
                "dml_ops": apex["dml_ops"],
                "exception_paths": apex["exception_paths"],
                "method_names": apex["method_names"],
            }
        )

    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    src = Path(args.src)
    files = collect_files(src)

    rules = []
    totals = {"branches": 0, "wires": 0, "dml": 0, "exceptions": 0, "methods": 0}
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_text(f, text)
        totals["branches"] += parsed["branch_count"]
        totals["wires"] += len(parsed["wire_bindings"])
        totals["dml"] += len(parsed["dml_ops"])
        totals["exceptions"] += parsed["exception_paths"]
        totals["methods"] += len(parsed["method_names"])
        rules.append({"file": str(f), **parsed})

    out = {"source": str(src), "files": rules, "summary": totals}
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

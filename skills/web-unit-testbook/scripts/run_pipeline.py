import argparse
import subprocess
from pathlib import Path


def run(cmd):
    print("[RUN]", " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--template", default="workspace/inputs/template/template_v3_confirmed.xlsx")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--ocr-lang", default="")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    design_json = outdir / "design_rules.json"
    code_json = outdir / "code_rules.json"
    cases_json = outdir / "cases.json"
    md = outdir / "UnitTestSpec_UIOnly.md"
    xlsx = outdir / "unit_test_book_v3_template_based.xlsx"

    cmd1 = ["python", "scripts/parse_design_excel.py", "--input", args.design, "--out", str(design_json)]
    if args.ocr_lang:
        cmd1 += ["--ocr-lang", args.ocr_lang]

    run(cmd1)
    run(["python", "scripts/extract_code_rules.py", "--src", args.code, "--out", str(code_json)])
    run([
        "python", "scripts/generate_ui_only_cases.py",
        "--design", str(design_json),
        "--out-md", str(md),
        "--out-cases", str(cases_json),
    ])
    run([
        "python", "scripts/export_to_excel.py",
        "--template", args.template,
        "--cases", str(cases_json),
        "--out", str(xlsx),
    ])

    print(f"Done. Outputs in: {outdir}")


if __name__ == "__main__":
    main()

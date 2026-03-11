#!/usr/bin/env python3
"""Legacy-compatible testbook generator.
Back-compat wrapper for the original 4-step flow.
"""
import argparse
import subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design_rules")
    ap.add_argument("code_rules")
    ap.add_argument("--out-md", default="UnitTestSpec_HighPrecision.md")
    ap.add_argument("--out-cases", default="cases.json")
    args = ap.parse_args()

    cmd = [
        "python", "scripts/generate_high_precision.py",
        "--design", args.design_rules,
        "--code", args.code_rules,
        "--out-md", args.out_md,
        "--out-cases", args.out_cases,
    ]
    subprocess.check_call(cmd)


if __name__ == "__main__":
    main()

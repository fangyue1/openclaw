import argparse, json, pathlib, subprocess

p = argparse.ArgumentParser()
p.add_argument('--merged-rules', required=True)
p.add_argument('--template-schema', required=True)
p.add_argument('--out-cases', required=True)
p.add_argument('--out-md', required=True)
a = p.parse_args()

merged = json.loads(pathlib.Path(a.merged_rules).read_text(encoding='utf-8'))
design_core = merged.get('design_enriched', {}).get('design_core', {})

tmp_design = pathlib.Path(a.out_cases).with_name('_design_for_generation.json')
tmp_design.write_text(json.dumps(design_core, ensure_ascii=False, indent=2), encoding='utf-8')

root = pathlib.Path(__file__).resolve().parents[2]
impl = root / 'web-unit-testbook' / 'scripts' / 'generate_ui_only_cases.py'
subprocess.run(['python', str(impl), '--design', str(tmp_design), '--out-md', a.out_md, '--out-cases', a.out_cases], check=True)
print(f'Wrote {a.out_cases} and {a.out_md}')

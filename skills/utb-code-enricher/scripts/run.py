import argparse, json, pathlib, subprocess

p = argparse.ArgumentParser()
p.add_argument('--design-enriched', required=True)
p.add_argument('--code', required=True)
p.add_argument('--out', required=True)
a = p.parse_args()

root = pathlib.Path(__file__).resolve().parents[2]
impl = root / 'web-unit-testbook' / 'scripts' / 'extract_code_rules.py'
code_rules_path = pathlib.Path(a.out).with_name('code_rules.json')
subprocess.run(['python', str(impl), '--src', a.code, '--out', str(code_rules_path)], check=True)

design = json.loads(pathlib.Path(a.design_enriched).read_text(encoding='utf-8'))
code = json.loads(code_rules_path.read_text(encoding='utf-8'))
merged = {
    'design_enriched': design,
    'code_rules': code,
    'ui_actions_with_code_links': [],
    'server_validations': code.get('validations', []) if isinstance(code, dict) else [],
    'api_calls': code.get('apis', []) if isinstance(code, dict) else [],
    'branch_conditions': code.get('branches', []) if isinstance(code, dict) else [],
    'error_messages': code.get('errors', []) if isinstance(code, dict) else []
}
pathlib.Path(a.out).write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wrote {code_rules_path}')
print(f'Wrote {a.out}')

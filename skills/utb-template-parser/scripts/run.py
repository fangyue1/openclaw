import argparse, subprocess, pathlib

p = argparse.ArgumentParser()
p.add_argument('--template', required=True)
p.add_argument('--out', required=True)
a = p.parse_args()

root = pathlib.Path(__file__).resolve().parents[2]
impl = root / 'web-unit-testbook' / 'scripts' / 'parse_template_semantics.py'
subprocess.run(['python', str(impl), '--template', a.template, '--out', a.out], check=True)
print(f'Wrote {a.out}')

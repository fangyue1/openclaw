import argparse, subprocess, pathlib

p = argparse.ArgumentParser()
p.add_argument('--template', required=True)
p.add_argument('--cases', required=True)
p.add_argument('--out', required=True)
a = p.parse_args()

root = pathlib.Path(__file__).resolve().parents[2]
impl = root / 'web-unit-testbook' / 'scripts' / 'export_to_excel.py'
subprocess.run(['python', str(impl), '--template', a.template, '--cases', a.cases, '--out', a.out], check=True)
print(f'Wrote {a.out}')

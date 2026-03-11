import argparse, subprocess, pathlib

p = argparse.ArgumentParser()
p.add_argument('--input', required=True)
p.add_argument('--out', required=True)
p.add_argument('--ocr-lang', default='jpn+eng')
a = p.parse_args()

root = pathlib.Path(__file__).resolve().parents[2]
impl = root / 'web-unit-testbook' / 'scripts' / 'parse_design_excel.py'
subprocess.run(['python', str(impl), '--input', a.input, '--out', a.out, '--ocr-lang', a.ocr_lang], check=True)
print(f'Wrote {a.out}')

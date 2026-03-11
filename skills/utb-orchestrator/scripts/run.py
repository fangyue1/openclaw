import argparse, json, pathlib, subprocess, hashlib

p = argparse.ArgumentParser()
p.add_argument('--design', required=True)
p.add_argument('--code', required=True)
p.add_argument('--template', required=True)
p.add_argument('--outdir', required=True)
a = p.parse_args()

outdir = pathlib.Path(a.outdir)
outdir.mkdir(parents=True, exist_ok=True)
root = pathlib.Path(__file__).resolve().parents[2]

def run(skill, args):
    script = root / skill / 'scripts' / 'run.py'
    subprocess.run(['python', str(script)] + args, check=True)

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(8192), b''):
            h.update(c)
    return h.hexdigest()

design_core = outdir / 'design_core.json'
design_enriched = outdir / 'design_enriched.json'
merged_rules = outdir / 'merged_rules.json'
template_schema = outdir / 'template_schema.json'
cases = outdir / 'cases.json'
spec = outdir / 'UnitTestSpec.md'
output = outdir / 'unit_test_book_generated.xlsx'

run('utb-design-parser', ['--input', a.design, '--out', str(design_core)])
run('utb-image-checksheet-parser', ['--design-core', str(design_core), '--out', str(design_enriched)])
run('utb-code-enricher', ['--design-enriched', str(design_enriched), '--code', a.code, '--out', str(merged_rules)])
run('utb-template-parser', ['--template', a.template, '--out', str(template_schema)])
run('utb-case-generator', ['--merged-rules', str(merged_rules), '--template-schema', str(template_schema), '--out-cases', str(cases), '--out-md', str(spec)])
run('utb-excel-exporter', ['--template', a.template, '--cases', str(cases), '--out', str(output)])

manifest = {
    'inputs': {
        'design': {'path': a.design, 'sha256': sha256(a.design)},
        'code': {'path': a.code, 'sha256': sha256(a.code)},
        'template': {'path': a.template, 'sha256': sha256(a.template)}
    },
    'outputs': {
        'design_core': str(design_core),
        'design_enriched': str(design_enriched),
        'merged_rules': str(merged_rules),
        'template_schema': str(template_schema),
        'cases': str(cases),
        'spec': str(spec),
        'workbook': str(output)
    }
}
(outdir / 'run_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Done. Outputs in: {outdir}')

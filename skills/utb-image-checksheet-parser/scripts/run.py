import argparse, json, pathlib

p = argparse.ArgumentParser()
p.add_argument('--design-core', required=True)
p.add_argument('--out', required=True)
a = p.parse_args()

src = json.loads(pathlib.Path(a.design_core).read_text(encoding='utf-8'))
enriched = {
    'design_core': src,
    'image_ocr_blocks': [],
    'screenshot_annotations': [],
    'checksheet_conditions': src.get('checks', []) if isinstance(src, dict) else [],
    'checksheet_expected_results': []
}
pathlib.Path(a.out).write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wrote {a.out}')

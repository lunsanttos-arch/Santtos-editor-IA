import json
from pathlib import Path

ROOT = Path('public') / 'brands'
OUT = Path('data') / 'brands-index.json'
EXT = {'.jpg', '.jpeg', '.png', '.webp', '.svg'}

ROOT.mkdir(parents=True, exist_ok=True)
assets = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path.suffix.lower() not in EXT:
        continue
    rel = path.relative_to(ROOT).as_posix()
    assets.append({
        'asset': rel,
        'stem': path.stem.replace('_', ' ').replace('-', ' '),
        'kind': 'svg' if path.suffix.lower() == '.svg' else 'image',
    })
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({'folder': 'public/brands', 'assets': assets}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Brands indexadas: {len(assets)} arquivo(s) -> {OUT}')

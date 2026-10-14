import json
import os
from pathlib import Path

ROOT = Path('public') / 'broll'
OUT = Path('data') / 'broll-index.json'
IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.webp'}
VIDEO_EXT = {'.mp4', '.mov', '.m4v', '.webm'}

ROOT.mkdir(parents=True, exist_ok=True)
assets = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file():
        continue
    ext = path.suffix.lower()
    if ext not in IMAGE_EXT | VIDEO_EXT:
        continue
    rel = path.relative_to(ROOT).as_posix()
    assets.append({
        'asset': rel,
        'kind': 'image' if ext in IMAGE_EXT else 'video',
        'stem': path.stem.replace('_', ' ').replace('-', ' '),
    })

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({'folder': 'public/broll', 'assets': assets}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'B-roll indexado: {len(assets)} arquivo(s) -> {OUT}')

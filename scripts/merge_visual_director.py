import json
from pathlib import Path

cues_path = Path('data/visual-cues.json')
placements_path = Path('data/visual-placements.json')
out = Path('data/visual-director.json')

cues = json.loads(cues_path.read_text(encoding='utf-8')).get('cues', []) if cues_path.exists() else []
placements = json.loads(placements_path.read_text(encoding='utf-8')).get('placements', []) if placements_path.exists() else []
by_id = {p.get('cueId'): p for p in placements}

merged=[]
for cue in cues:
    p = by_id.get(cue.get('id'), {})
    item = dict(cue)
    item['placement'] = {
        'x': p.get('x', 50),
        'y': p.get('y', 28),
        'scale': p.get('scale', 1.0),
        'mode': p.get('placement', cue.get('placementIntent', 'auto')),
        'confidence': p.get('confidence', 0.0),
        'notes': p.get('notes', ''),
    }
    merged.append(item)
out.write_text(json.dumps({'cues': merged}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Visual Director consolidado: {len(merged)} cue(s) -> {out}')

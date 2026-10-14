import json
from pathlib import Path
import av

CUES = Path('data/visual-cues.json')
VIDEO = Path('public/input.mp4')
OUTDIR = Path('output/cues')
MAP = Path('data/cue-frames.json')
LIST = Path('data/cue-images.txt')

if not CUES.exists():
    raise SystemExit('data/visual-cues.json nao encontrado')
if not VIDEO.exists():
    raise SystemExit('public/input.mp4 nao encontrado')

cues = json.loads(CUES.read_text(encoding='utf-8')).get('cues', [])
OUTDIR.mkdir(parents=True, exist_ok=True)
for p in OUTDIR.glob('cue_*.jpg'):
    p.unlink()

# Decode once and capture the first frame at/after each target.
targets = []
for i, cue in enumerate(cues):
    a = float(cue.get('sourceAt', 0))
    b = float(cue.get('sourceEnd', a))
    # Slightly inside the cue usually captures the gesture better than the first phoneme.
    t = a + max(0.08, min(0.45, max(0.0, b - a) * 0.35))
    targets.append((t, i, cue))
targets.sort(key=lambda x: x[0])

container = av.open(str(VIDEO))
stream = container.streams.video[0]
found = []
ti = 0
for frame in container.decode(stream):
    if ti >= len(targets):
        break
    if frame.pts is None:
        continue
    t = float(frame.pts * frame.time_base)
    target, idx, cue = targets[ti]
    if t + 1e-6 < target:
        continue
    out = OUTDIR / f"cue_{idx+1:02d}_{cue.get('id','cue')}.jpg"
    frame.to_image().convert('RGB').save(out, quality=90, optimize=True)
    found.append({
        'cueId': cue.get('id'),
        'sourceAt': cue.get('sourceAt'),
        'capturedAt': round(t, 3),
        'image': str(out.resolve()),
    })
    ti += 1
container.close()

MAP.write_text(json.dumps({'frames': found}, ensure_ascii=False, indent=2), encoding='utf-8')
LIST.write_text(','.join(item['image'] for item in found), encoding='utf-8')
print(f'Cue frames extraidos: {len(found)}/{len(cues)}')

import json
import sys
from pathlib import Path

PLAN = Path('data/edit-plan.json')
DIRECTOR = Path('data/visual-director.json')

if not PLAN.exists() or not DIRECTOR.exists():
    print('Cobertura visual: sem dados suficientes; pulando.')
    sys.exit(0)
plan = json.loads(PLAN.read_text(encoding='utf-8'))
director = json.loads(DIRECTOR.read_text(encoding='utf-8'))
segments = plan.get('segments') or []
visuals = plan.get('visuals') or []
motions = plan.get('motions') or []
broll = plan.get('broll') or []

# Convert a source timestamp to the final output timeline if that source moment survived the edit.
def map_source_to_output(t):
    cursor = 0.0
    for s in segments:
        a=float(s['sourceStart']); b=float(s['sourceEnd'])
        if a - 0.03 <= t <= b + 0.03:
            return cursor + max(0.0, min(t, b) - a)
        cursor += max(0.0, b-a)
    return None

def overlaps_time(item, t, radius=0.9):
    a=float(item.get('at', -999)); d=float(item.get('duration', 0))
    return a <= t + radius and a+d >= t-radius

missing=[]
covered=[]
for cue in director.get('cues', []):
    if cue.get('priority') != 'high':
        continue
    mapped = map_source_to_output(float(cue.get('sourceAt', 0)))
    if mapped is None:
        # The editor removed the source phrase; no visual is required.
        continue
    pool = visuals + motions + broll
    if any(overlaps_time(item, mapped) for item in pool):
        covered.append((cue.get('id'), mapped))
    else:
        missing.append((cue.get('id'), cue.get('subject'), mapped, cue.get('triggerText')))

if missing:
    print('FALHA DE COBERTURA VISUAL:')
    for cid, subject, t, trigger in missing:
        print(f' - {cid} ({subject}) em ~{t:.2f}s sem acao visual | fala: {trigger}')
    sys.exit(2)
print(f'Cobertura visual OK: {len(covered)} cue(s) high priority atendidos.')

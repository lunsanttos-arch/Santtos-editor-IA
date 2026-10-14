import json
import math
import os
import sys
from pathlib import Path

TRANSCRIPT = os.path.join('data', 'transcript.json')
PLAN = os.path.join('data', 'edit-plan.json')
STYLE = os.path.join('config', 'style.json')

with open(TRANSCRIPT, 'r', encoding='utf-8') as f:
    transcript = json.load(f)
with open(PLAN, 'r', encoding='utf-8') as f:
    plan = json.load(f)
style = json.load(open(STYLE, 'r', encoding='utf-8')) if os.path.exists(STYLE) else {}

duration = float(transcript.get('duration', 0))
errors = []
warnings = []
segments = plan.get('segments') or []
if not segments:
    errors.append('segments esta vazio')

output_cursor = 0.0
for i, s in enumerate(segments):
    try:
        a = float(s['sourceStart']); b = float(s['sourceEnd'])
    except Exception:
        errors.append(f'segmento {i}: sourceStart/sourceEnd invalidos'); continue
    if not math.isfinite(a) or not math.isfinite(b): errors.append(f'segmento {i}: valor nao-finito')
    if a < 0: errors.append(f'segmento {i}: sourceStart negativo')
    if b <= a: errors.append(f'segmento {i}: sourceEnd precisa ser maior que sourceStart')
    if b > duration + 0.05: errors.append(f'segmento {i}: ultrapassa a duracao do bruto ({duration:.3f}s)')
    z1 = float(s.get('zoom', 1.0)); z2 = float(s.get('zoomTo', z1))
    if not (0.95 <= z1 <= 1.25 and 0.95 <= z2 <= 1.25): errors.append(f'segmento {i}: zoom fora da faixa segura')
    output_cursor += max(0.0, b - a)

max_final = float(style.get('maxFinalSeconds', 0) or 0)
if max_final and output_cursor > max_final + 0.25:
    errors.append(f'duracao final {output_cursor:.2f}s excede maxFinalSeconds {max_final:.2f}s')

for bucket in ('captions', 'motions', 'overlays', 'broll', 'visuals'):
    for i, item in enumerate(plan.get(bucket) or []):
        try:
            at = float(item.get('at', -1)); dur = float(item.get('duration', 0))
        except Exception:
            errors.append(f'{bucket}[{i}]: at/duration invalidos'); continue
        if at < 0 or dur <= 0: errors.append(f'{bucket}[{i}]: at/duration invalidos')
        if at + dur > output_cursor + 0.25: warnings.append(f'{bucket}[{i}]: termina depois do fim da timeline')

for i, item in enumerate(plan.get('broll') or []):
    typ = item.get('type')
    if typ in ('image', 'video'):
        asset = str(item.get('asset', '')).strip()
        if not asset:
            errors.append(f'broll[{i}]: asset obrigatorio para type={typ}')
        else:
            path = Path('public') / 'broll' / asset
            if not path.is_file():
                errors.append(f'broll[{i}]: arquivo nao existe: {path}')


for i, item in enumerate(plan.get('visuals') or []):
    try:
        x=float(item.get('x',50)); y=float(item.get('y',30)); sc=float(item.get('scale',1))
    except Exception:
        errors.append(f'visuals[{i}]: x/y/scale invalidos'); continue
    if not (5 <= x <= 95 and 5 <= y <= 88): errors.append(f'visuals[{i}]: posicao fora da area segura')
    if not (0.5 <= sc <= 1.6): errors.append(f'visuals[{i}]: scale fora da faixa')
    asset=str(item.get('asset','')).strip()
    if item.get('type') == 'brand' and asset:
        path = Path('public') / 'brands' / asset
        if not path.is_file(): errors.append(f'visuals[{i}]: brand asset nao existe: {path}')

# Sinaliza excesso de elementos simultaneos, sem bloquear a edicao.
def overlaps(a, b):
    return a[0] < b[1] and b[0] < a[1]
visuals=[]
for bucket in ('motions','broll','visuals'):
    for i,item in enumerate(plan.get(bucket) or []):
        visuals.append((float(item['at']), float(item['at'])+float(item['duration']), bucket, i))
for i,a in enumerate(visuals):
    for b in visuals[i+1:]:
        if overlaps(a,b): warnings.append(f'colisao visual: {a[2]}[{a[3]}] com {b[2]}[{b[3]}]')

if errors:
    print('PLANO INVALIDO:')
    for e in errors: print(' -', e)
    sys.exit(1)
print(f'Plano valido. Duracao final aproximada: {output_cursor:.2f}s | {len(segments)} segmentos')
if warnings:
    print('AVISOS DE QUALIDADE:')
    for w in warnings[:20]: print(' -', w)

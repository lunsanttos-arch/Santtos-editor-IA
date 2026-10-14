import json
import os

TRANSCRIPT = os.path.join('data', 'transcript.json')
OUTPUT = os.path.join('data', 'edit-plan.json')

with open(TRANSCRIPT, 'r', encoding='utf-8') as f:
    transcript = json.load(f)

duration = float(transcript.get('duration', 0))
plan = {
    'fps': 30,
    'width': 1080,
    'height': 1920,
    'segments': [{
        'sourceStart': 0,
        'sourceEnd': round(duration, 3),
        'zoom': 1.0,
        'zoomTo': 1.0,
        'reason': 'baseline full take before AI editorial pass'
    }],
    'captions': [],
    'motions': [],
    'overlays': [],
    'broll': [],
    'visuals': []
}
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(plan, f, ensure_ascii=False, indent=2)
print(f'Plano neutro criado: {OUTPUT}. Agora o agente deve fazer a edicao editorial.')

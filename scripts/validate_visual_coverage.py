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
from check_edit import uncovered_cues

missing = uncovered_cues(plan, director)
if missing:
    print('FALHA DE COBERTURA VISUAL:')
    for item in missing:
        print(' -', item)
    sys.exit(2)
print('Cobertura visual OK: pedidos mantidos conferidos por assunto/asset.')

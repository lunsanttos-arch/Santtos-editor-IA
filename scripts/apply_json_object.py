import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--input', required=True)
ap.add_argument('--output', required=True)
args = ap.parse_args()
raw = Path(args.input).read_text(encoding='utf-8-sig').strip()
if raw.startswith('```'):
    lines = raw.splitlines()[1:]
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]
    raw = '\n'.join(lines).strip()
obj = json.loads(raw)
Path(args.output).parent.mkdir(parents=True, exist_ok=True)
Path(args.output).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'JSON aplicado: {args.output}')

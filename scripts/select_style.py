"""Choose a versioned preset/format before editing; never rewrites the edit plan."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', choices=sorted(p.stem for p in (ROOT / 'config/presets').glob('*.json')))
    ap.add_argument('--format', choices=['falado', 'mudo', 'narrado'])
    args = ap.parse_args()
    path = ROOT / 'config/workflow.json'
    selection = json.loads(path.read_text())
    if args.preset:
        selection['preset'] = args.preset
    if args.format:
        selection['format'] = args.format
    path.write_text(json.dumps(selection, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(selection, ensure_ascii=False))


if __name__ == '__main__':
    main()

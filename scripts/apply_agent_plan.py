import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=os.path.join('data', 'agent-plan.json'))
    parser.add_argument('--output', default=os.path.join('data', 'edit-plan.json'))
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f'Resposta do agente nao encontrada: {args.input}')
        sys.exit(1)

    raw = open(args.input, 'r', encoding='utf-8-sig').read().strip()
    if raw.startswith('```'):
        lines = raw.splitlines()
        if lines and lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        raw = '\n'.join(lines).strip()

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as exc:
        print('O Codex respondeu, mas o JSON nao pode ser lido.')
        print(f'Erro: {exc}')
        print(f'Veja o arquivo: {args.input}')
        sys.exit(1)

    required = ['fps', 'width', 'height', 'segments', 'captions', 'motions', 'overlays', 'broll', 'visuals']
    missing = [k for k in required if k not in plan]
    if missing:
        print('Plano do agente incompleto. Campos ausentes:', ', '.join(missing))
        sys.exit(1)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f'Plano editorial aplicado: {args.output}')


if __name__ == '__main__':
    main()

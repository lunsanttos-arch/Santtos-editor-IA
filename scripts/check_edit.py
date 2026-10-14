"""Fail closed on malformed plans and measurable editorial rules. No AI judgement."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parent.parent


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),
                      parse_constant=lambda v: (_ for _ in ()).throw(ValueError(f'Número inválido: {v}')))


def tokens(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    return set(re.findall(r'[a-z0-9]+', text))


def check_motion_tracks(data, plan, profile, source=None, expected_format=None):
    from jsonschema import Draft202012Validator
    errors = [f'tracking schema: {e.message}' for e in Draft202012Validator(load(ROOT / 'schemas/motion-tracks.schema.json')).iter_errors(data)]
    if errors or not data['tracks']:
        return errors
    signature = [[s['sourceStart'], s['sourceEnd'], s.get('zoom', 1), s.get('zoomTo', s.get('zoom', 1))] for s in plan['segments']]
    if data['sourceSegments'] != signature or data['zoomIntensity'] != profile['zoomIntensity']:
        errors.append('Tracking desatualizado após alteração de cortes ou câmera')
    if expected_format is not None and data.get('format') != expected_format:
        errors.append('Tracking desatualizado após alteração do formato/caption safe area')
    if source is not None and source.is_file():
        with source.open('rb') as f:
            if hashlib.file_digest(f, 'sha256').hexdigest() != data['sourceSha256']:
                errors.append('Tracking pertence a outro vídeo bruto')
    seen = set()
    for track in data['tracks']:
        key = (track['visualAt'], track['asset'])
        visual = next((v for v in plan.get('visuals', []) if (v['at'], v['asset']) == key), None)
        if key in seen or visual is None:
            errors.append('Tracking duplicado ou sem visual correspondente')
            continue
        seen.add(key)
        points = track['points']
        if any(a['at'] >= b['at'] for a, b in zip(points, points[1:])):
            errors.append('Timestamps do tracking precisam ser estritamente crescentes')
        if points[0]['at'] > visual['at'] or points[-1]['at'] < visual['at'] + visual['duration'] - 1 / plan['fps']:
            errors.append('Tracking não cobre o intervalo do visual')
        if sum(p['visibility'] > .5 for p in points) / len(points) < .65:
            errors.append('Tracking sem cobertura visível suficiente (mínimo 65%)')
    return errors


def uncovered_cues(plan, director, motion_tracks=None):
    missing = []
    for cue in director.get('cues', []):
        if cue.get('priority') != 'high':
            continue
        start = float(cue['sourceAt'])
        end = max(start + .03, float(cue.get('sourceEnd', start)))
        cursor = 0
        for segment in plan['segments']:
            a, b = segment['sourceStart'], segment['sourceEnd']
            left, right = max(a, start), min(b, end)
            if left < right:
                at, until = cursor + left - a, cursor + right - a
                subject = tokens(cue.get('subject', ''))
                hint = cue.get('assetHint', '')
                def represents(item, bucket):
                    track = next((t for t in (motion_tracks or {}).get('tracks', [])
                                  if t['visualAt'] == item['at'] and t['asset'] == item.get('asset')), None) if bucket == 'visuals' else None
                    if track is not None and not any(p['visibility'] > .5 and at - .35 <= p['at'] <= until + .35
                                                     for p in track['points']):
                        return False
                    # A headline mentioning a brand is not its requested logo.
                    if hint:
                        return bucket in ('visuals', 'broll') and item.get('asset') == hint
                    if bucket == 'motions':
                        return False
                    evidence = tokens(item.get('text', '') + ' ' + item.get('asset', ''))
                    return bool(subject) and subject <= evidence
                found = any(item['at'] < until + .35 and item['at'] + item['duration'] > at - .35
                            and represents(item, bucket)
                            for bucket in ('visuals', 'broll', 'motions')
                            for item in plan.get(bucket, []))
                if not found:
                    missing.append(f"{cue.get('id', 'cue')} ({cue.get('subject', '')}) em {at:.2f}s")
            cursor += b - a
    return missing


def check(plan, transcript, director, rules, profile, public, schema=None):
    errors = []
    if schema is not None:
        from jsonschema import Draft202012Validator
        errors.extend(f"schema {list(e.absolute_path)}: {e.message}" for e in Draft202012Validator(schema).iter_errors(plan))
        if errors:
            return errors
    duration = sum(s['sourceEnd'] - s['sourceStart'] for s in plan['segments'])
    if not math.isfinite(duration) or duration <= 0 or duration > rules['maxSeconds']:
        errors.append('Duração final fora do limite do formato')
    for i, s in enumerate(plan['segments']):
        if not 0 <= s['sourceStart'] < s['sourceEnd'] <= transcript['duration'] + .03:
            errors.append(f'segmento {i}: intervalo inválido no bruto')
        for boundary in (s['sourceStart'], s['sourceEnd']):
            if any(w['start'] + .04 < boundary < w['end'] - .04 for w in transcript.get('words', [])):
                errors.append(f'segmento {i}: corte dentro de palavra em {boundary:.3f}s')
    for bucket in ('captions', 'motions', 'overlays', 'broll', 'visuals'):
        for i, item in enumerate(plan.get(bucket, [])):
            a, d = item['at'], item['duration']
            if not math.isfinite(a + d) or a < 0 or d <= 0 or a + d > duration + 1 / plan['fps']:
                errors.append(f'{bucket}[{i}]: tempo fora da timeline')
            if bucket == 'captions':
                if len(item['text'].split()) > rules['maxCaptionWords']:
                    errors.append(f'caption {i}: palavras demais')
                if len(item.get('highlight', [])) > rules['maxCaptionHighlights']:
                    errors.append(f'caption {i}: destaques demais')
                if not tokens(' '.join(item.get('highlight', []))) <= tokens(item['text']):
                    errors.append(f'caption {i}: destaque ausente do texto')
            asset = item.get('asset', '')
            folder = 'brands' if bucket == 'visuals' else 'broll'
            requires_asset = bucket == 'visuals' and item.get('type') == 'brand' or bucket == 'broll' and item.get('type') in ('image', 'video')
            if requires_asset:
                base = (public / folder).resolve()
                target = (base / asset).resolve()
                if not asset or not target.is_relative_to(base) or not target.is_file():
                    errors.append(f'{bucket}[{i}]: asset local ausente ou inválido')
    visuals = [v for bucket in ('visuals', 'broll', 'motions') for v in plan.get(bucket, [])]
    events = sorted([(v['at'], 1) for v in visuals] + [(v['at'] + v['duration'], -1) for v in visuals])
    active = 0
    for _, delta in events:
        active += delta
        if active > profile['maxSimultaneousVisuals']:
            errors.append('Excesso de elementos visuais simultâneos; redistribua sem remover pedidos obrigatórios')
            break
    max_gap = rules.get('maxVisualGapSeconds')
    if max_gap is not None:
        cursor = 0
        for item in sorted(visuals, key=lambda v: v['at']):
            if item['at'] - cursor > max_gap:
                errors.append(f'Sem imagem/graphic por {item["at"] - cursor:.2f}s em {cursor:.2f}s')
            cursor = max(cursor, item['at'] + item['duration'])
        if duration - cursor > max_gap:
            errors.append(f'Sem imagem/graphic por {duration - cursor:.2f}s no final')
    if director is not None:
        errors.extend('Pedido visual sem representação: ' + s for s in uncovered_cues(plan, director))
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', default='data/edit-plan.json')
    ap.add_argument('--require-director', action='store_true')
    ap.add_argument('--require-media', action='store_true')
    args = ap.parse_args()
    try:
        selection = load(ROOT / 'config/workflow.json')
        # Select only known filenames, never accept arbitrary paths from config.
        if selection['preset'] not in [p.stem for p in (ROOT / 'config/presets').glob('*.json')] or selection['format'] not in ('falado', 'mudo', 'narrado'):
            raise ValueError('Preset/formato desconhecido')
        director_path = ROOT / 'data/visual-director.json'
        if args.require_director and not director_path.exists():
            raise ValueError('Visual Director ausente; execute a análise antes do render')
        if args.require_media and not (ROOT / 'public/input.mp4').is_file():
            raise ValueError('Bruto ausente em public/input.mp4')
        from jsonschema import Draft202012Validator
        for preset_file in (ROOT / 'config/presets').glob('*.json'):
            preset_errors = list(Draft202012Validator(load(ROOT / 'schemas/style-profile.schema.json')).iter_errors(load(preset_file)))
            if preset_errors:
                raise ValueError(f'{preset_file.name}: {preset_errors[0].message}')
        plan = load(ROOT / args.plan)
        errors = check(plan, load(ROOT / 'data/transcript.json'),
                       load(director_path) if director_path.exists() else None,
                       load(ROOT / f'config/formats/{selection["format"]}.json'),
                       load(ROOT / f'config/presets/{selection["preset"]}.json'),
                       ROOT / 'public', load(ROOT / 'schemas/edit-plan.schema.json'))
        tracking_path = ROOT / 'data/motion-tracks.json'
        if not errors and tracking_path.exists():
            motion_tracks = load(tracking_path)
            errors.extend(check_motion_tracks(motion_tracks, plan,
                          load(ROOT / f'config/presets/{selection["preset"]}.json'), ROOT / 'public/input.mp4', selection['format']))
            if not errors and director_path.exists():
                errors.extend('Pedido visual oculto no tracking: ' + item for item in uncovered_cues(plan, load(director_path), motion_tracks))
        if not director_path.exists():
            print('AVISO: Visual Director ausente; cobertura não avaliada.')
        if errors:
            print('REPROVADO:\n' + '\n'.join(' - ' + e for e in errors))
            return 2
        print(f"APROVADO nas regras automáticas: {selection['format']} / {selection['preset']}. Revisão estética ainda necessária.")
        return 0
    except (ValueError, OSError, KeyError, TypeError, ImportError) as exc:
        print(f'REPROVADO: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

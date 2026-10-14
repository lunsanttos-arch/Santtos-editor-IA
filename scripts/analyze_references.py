"""Measure reference metadata and candidate scene cuts, without claiming semantic vision."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def analyze(path):
    probe = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                            '-of', 'json', str(path)], capture_output=True, text=True, check=True)
    info = json.loads(probe.stdout)
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    duration = float(info['format']['duration'])
    if duration <= 0:
        raise ValueError(f'Duração inválida: {path.name}')
    scan = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-vf',
                           'scale=288:-2,select=gt(scene\\,0.3),showinfo',
                           '-an', '-f', 'null', '-'], capture_output=True, text=True, check=True)
    cuts = [round(float(t), 3) for t in re.findall(r'pts_time:([0-9.]+)', scan.stderr) if .1 < float(t) < duration - .1]
    with path.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    return {'file': path.name, 'sha256': digest,
            'duration': duration, 'width': video['width'], 'height': video['height'],
            'sceneCutCandidates': cuts, 'candidateCutsPerMinute': round(len(cuts) * 60 / duration, 2),
            'averageCandidateShotSeconds': round(duration / (len(cuts) + 1), 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('videos', nargs='*', type=Path)
    ap.add_argument('--output', type=Path, default=ROOT / 'data/reference-style.json')
    args = ap.parse_args()
    videos = args.videos or [p for p in (ROOT / 'references').iterdir() if p.suffix.lower() in ('.mp4', '.mov', '.webm')]
    if not 1 <= len(videos) <= 5:
        raise SystemExit('Forneça de 1 a 5 vídeos de referência.')
    results = [analyze(p) for p in videos]
    profile = {'version': 1, 'method': 'ffmpeg scene score > 0.3 at width 288; candidates, not confirmed editorial cuts',
               'references': results,
               'unmeasured': ['captionPosition', 'captionSize', 'captionDuration', 'visualDensity',
                              'zoomFrequency', 'zoomIntensity', 'motionFrequency', 'brollPresence', 'transitionStyle'],
               'editorialUse': 'Director/Editor devem confrontar estas medidas com a referência e o preset; não copiar identidade nem inferir métricas ausentes.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Análise salva: {args.output}; características sem medição estão explicitamente listadas.')


if __name__ == '__main__':
    main()

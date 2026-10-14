"""Reproducible synthetic integration render; restore all user plans/configuration."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--browser', default=None)
    ap.add_argument('--all-presets', action='store_true')
    args = ap.parse_args()
    media = ROOT / 'public/input.mp4'
    if media.exists():
        raise SystemExit('Smoke test requer public/input.mp4 ausente; preserve o bruto existente.')
    files = [ROOT / name for name in ('data/edit-plan.json', 'data/transcript.json',
                                      'data/visual-director.json', 'config/workflow.json', 'data/motion-tracks.json')]
    backups = {p: p.read_bytes() if p.exists() else None for p in files}
    npm = 'npm.cmd' if sys.platform == 'win32' else 'npm'
    npx = 'npx.cmd' if sys.platform == 'win32' else 'npx'
    def run(cmd):
        subprocess.run(cmd, cwd=ROOT, check=True)
    def write(p, obj):
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    try:
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i',
             'color=c=0x141820:size=1080x1920:rate=30', '-f', 'lavfi', '-i',
             'sine=frequency=220:sample_rate=48000', '-t', '5', '-c:v', 'libx264',
             '-preset', 'ultrafast', '-c:a', 'aac', '-shortest', str(media)])
        plan = {'fps': 30, 'width': 1080, 'height': 1920,
                'segments': [{'sourceStart': 0, 'sourceEnd': 5, 'zoom': 1, 'zoomTo': 1.08, 'reason': 'push motivado'}],
                'captions': [{'at': .2, 'duration': 2, 'text': 'O logo do ChatGPT aparece aqui.', 'highlight': ['ChatGPT']}],
                'motions': [{'at': 2.4, 'duration': 1.8, 'type': 'callout', 'text': 'Uma linguagem consistente', 'subtext': 'SanTTos · Style Engine', 'position': 'top'}],
                'overlays': [], 'broll': [],
                'visuals': [{'at': .2, 'duration': 2, 'type': 'brand', 'asset': 'chatgpt.svg', 'text': 'ChatGPT',
                             'x': 68, 'y': 34, 'scale': 1, 'enter': 'pop', 'reason': 'pedido explícito'}]}
        write(files[0], plan)
        write(files[1], {'sourceFile': 'synthetic', 'duration': 5, 'language': 'pt',
                         'words': [{'start': .2, 'end': .9, 'text': 'ChatGPT'}]})
        write(files[2], {'cues': [{'id': 'cue-001', 'priority': 'high', 'sourceAt': .2, 'sourceEnd': .9,
                                  'subject': 'ChatGPT', 'assetHint': 'chatgpt.svg'}]})
        write(files[3], {'preset': 'santtos-clean', 'format': 'falado'})
        write(files[4], {'tracks': []})
        run([npm, 'run', 'check:edit'])
        output = ROOT / 'output/smoke/alpha.mp4'
        output.parent.mkdir(parents=True, exist_ok=True)
        browser = ['--browser-executable=' + args.browser] if args.browser else []
        run([npx, '--no-install', 'remotion', 'render', 'src/index.ts', 'SanttosReel', str(output),
             '--scale=.5', '--concurrency=2', '--overwrite', *browser])
        info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(output)], text=True))
        video = next(s for s in info['streams'] if s['codec_type'] == 'video')
        assert int(video['nb_frames']) == 150, video
        assert (video['width'], video['height']) == (540, 960), video
        assert any(s['codec_type'] == 'audio' for s in info['streams']), 'Audio ausente'
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(output), '-f', 'null', '-'])
        if args.all_presets:
            for preset in sorted((ROOT / 'config/presets').glob('*.json')):
                write(files[3], {'preset': preset.stem, 'format': 'falado'})
                run([npx, '--no-install', 'remotion', 'still', 'src/index.ts', 'SanttosReel',
                     f'output/smoke/{preset.stem}.png', '--frame=40', '--scale=.5', '--overwrite', *browser])
        print('Smoke render aprovado: 150 frames, áudio, decode completo; material sintético.')
    finally:
        for path, original in backups.items():
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(original)
        media.unlink(missing_ok=True)


if __name__ == '__main__':
    main()

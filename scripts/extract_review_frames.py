import argparse
import json
from pathlib import Path
import av


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='output/review/draft.mp4')
    ap.add_argument('--outdir', default='output/review/frames')
    ap.add_argument('--count', type=int, default=6)
    args = ap.parse_args()

    src = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob('frame_*.jpg'):
        old.unlink()

    if not src.exists():
        raise SystemExit(f'Render de revisao nao encontrado: {src}')

    container = av.open(str(src))
    stream = container.streams.video[0]
    duration = float(stream.duration * stream.time_base) if stream.duration is not None else 0.0
    if duration <= 0 and container.duration:
        duration = float(container.duration / av.time_base)
    if duration <= 0:
        raise SystemExit('Nao foi possivel determinar a duracao do draft.')

    count = max(3, min(8, args.count))
    if duration < 3:
        targets = [duration * (i + 1) / (count + 1) for i in range(count)]
    else:
        # Amostra gancho + miolo + final, evitando exatamente o primeiro/ultimo frame.
        targets = [0.35 + (duration - 0.7) * i / (count - 1) for i in range(count)]

    paths = []
    target_i = 0
    for frame in container.decode(stream):
        if target_i >= len(targets):
            break
        t = float(frame.pts * frame.time_base) if frame.pts is not None else 0.0
        if t + 1e-6 < targets[target_i]:
            continue
        img = frame.to_image().convert('RGB')
        out = outdir / f'frame_{target_i + 1:02d}.jpg'
        img.save(out, quality=88, optimize=True)
        paths.append(out.resolve())
        target_i += 1

    container.close()
    if len(paths) < 3:
        raise SystemExit(f'Poucos frames extraidos: {len(paths)}')

    image_list = ','.join(str(p) for p in paths)
    Path('data/review-images.txt').write_text(image_list, encoding='utf-8')
    Path('data/review-frames.json').write_text(json.dumps({
        'draft': str(src.resolve()),
        'duration': round(duration, 3),
        'frames': [str(p) for p in paths],
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Revisao visual: {len(paths)} frames extraidos.')
    print('Lista salva em data/review-images.txt')


if __name__ == '__main__':
    main()

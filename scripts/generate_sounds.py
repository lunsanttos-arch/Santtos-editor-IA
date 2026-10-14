"""Small original synthetic motion cues; no external downloads or licensed samples."""
import argparse
import math
from pathlib import Path
import random
import struct
import wave

ROOT = Path(__file__).resolve().parent.parent / 'public/sounds'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--overwrite', action='store_true')
    args = ap.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    for index, (name, duration) in enumerate([('soft-pop', .13), ('whoosh', .28), ('tick', .06),
                                              ('impact', .22), ('swipe', .18), ('subtle-riser', .6)]):
        if (ROOT / f'{name}.wav').exists() and not args.overwrite:
            print(f'Preservado: {name}.wav')
            continue
        rng = random.Random(index)
        rate = 44100
        samples = []
        for i in range(int(rate * duration)):
            t = i / rate
            u = t / duration
            envelope = math.sin(math.pi * u) ** 2
            noise = rng.uniform(-1, 1)
            tone = math.sin(2 * math.pi * (190 * t - 55 * t * t / duration))
            if name in ('whoosh', 'swipe', 'subtle-riser'):
                value = noise * envelope * (.18 if name != 'subtle-riser' else .1 * u)
            else:
                value = (tone + noise * .08) * envelope * math.exp(-u * 6) * .7
            samples.append(struct.pack('<h', int(max(-1, min(1, value)) * 32767)))
        with wave.open(str(ROOT / f'{name}.wav'), 'wb') as out:
            out.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
            out.writeframes(b''.join(samples))
    print('Biblioteca de cues disponível em public/sounds')


if __name__ == '__main__':
    main()

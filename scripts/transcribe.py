import argparse
import json
import os
import shutil
import sys

from faster_whisper import WhisperModel
import av


def media_duration(path: str) -> float:
    with av.open(path) as container:
        if container.duration is not None:
            return float(container.duration / av.time_base)
        durations = []
        for stream in container.streams:
            if stream.duration is not None and stream.time_base is not None:
                durations.append(float(stream.duration * stream.time_base))
        return max(durations) if durations else 0.0


def transcribe(model_name: str, device: str, input_path: str, output_path: str):
    print(f"[1/4] Carregando Whisper {model_name} em {device}...")
    compute_type = "float16" if device == "cuda" else "int8"
    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
    except Exception as exc:
        if device == "cuda":
            print(f"GPU indisponivel ({exc}). Caindo para CPU int8...")
            device = "cpu"
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
        else:
            raise

    print("[2/4] Modelo carregado. Iniciando transcricao...")
    raw_segments, info = model.transcribe(
        input_path,
        language="pt",
        beam_size=5,
        vad_filter=True,
        word_timestamps=True,
        condition_on_previous_text=True,
    )

    print("[3/4] Processando fala, frases e timestamps...")
    words = []
    segments = []
    for segment in raw_segments:
        segment_words = []
        for word in segment.words or []:
            item = {
                "start": round(float(word.start), 3),
                "end": round(float(word.end), 3),
                "text": word.word.strip(),
                "probability": round(float(word.probability), 4),
            }
            words.append(item)
            segment_words.append(item)
        segments.append({
            "start": round(float(segment.start), 3),
            "end": round(float(segment.end), 3),
            "text": segment.text.strip(),
            "words": segment_words,
        })

    payload = {
        "sourceFile": os.path.basename(input_path),
        "language": info.language,
        "duration": round(media_duration(input_path), 3),
        "segments": segments,
        "words": words,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[4/4] Transcricao concluida: {output_path} | {len(words)} palavras | {len(segments)} frases")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--model", default="small")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--output", default=os.path.join("data", "transcript.json"))
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Arquivo nao encontrado: {args.input}", file=sys.stderr)
        sys.exit(2)

    os.makedirs("public", exist_ok=True)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    shutil.copy2(args.input, os.path.join("public", "input.mp4"))
    transcribe(args.model, args.device, args.input, args.output)


if __name__ == "__main__":
    main()

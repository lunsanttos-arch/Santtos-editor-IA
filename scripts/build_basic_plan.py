# DEPRECATED: prototipo mecanico v0.1. Nao usar para edicao editorial.
import json
import os

TRANSCRIPT = os.path.join("data", "transcript.json")
OUTPUT = os.path.join("data", "edit-plan.json")
MAX_SILENCE = 0.55
HANDLE = 0.08

with open(TRANSCRIPT, "r", encoding="utf-8") as f:
    transcript = json.load(f)

words = transcript.get("words", [])
duration = float(transcript.get("duration", 0))
segments = []

if words:
    start = max(0, words[0]["start"] - HANDLE)
    previous_end = words[0]["end"]
    for word in words[1:]:
        gap = word["start"] - previous_end
        if gap > MAX_SILENCE:
            end = min(duration, previous_end + HANDLE)
            if end - start >= 0.15:
                segments.append({"sourceStart": round(start, 3), "sourceEnd": round(end, 3), "zoom": 1.0})
            start = max(0, word["start"] - HANDLE)
        previous_end = word["end"]
    end = min(duration, previous_end + HANDLE)
    if end - start >= 0.15:
        segments.append({"sourceStart": round(start, 3), "sourceEnd": round(end, 3), "zoom": 1.0})
else:
    segments = [{"sourceStart": 0, "sourceEnd": duration, "zoom": 1.0}]

# Alternância discreta de enquadramento para tornar o primeiro teste visível.
for i, segment in enumerate(segments):
    segment["zoom"] = 1.0 if i % 3 else 1.06

plan = {
    "fps": 30,
    "width": 1080,
    "height": 1920,
    "captionWordsPerCard": 4,
    "captionMaxGap": 0.45,
    "segments": segments,
    "overlays": [],
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(plan, f, ensure_ascii=False, indent=2)

source_total = sum(max(0, s["sourceEnd"] - s["sourceStart"]) for s in segments)
print(f"Plano básico criado: {OUTPUT} | {len(segments)} cortes | duração final aprox. {source_total:.2f}s")

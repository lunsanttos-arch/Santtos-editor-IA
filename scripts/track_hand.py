"""Offline MediaPipe palm measurements → smoothed, output-timeline Remotion tracks.

No hand detection means no invented path: fade out after a short loss. The
selected hand is associated by distance; large jumps cannot switch identity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, default=ROOT / 'public/input.mp4')
    ap.add_argument('--plan', type=Path, default=ROOT / 'data/edit-plan.json')
    ap.add_argument('--output', type=Path, default=ROOT / 'data/motion-tracks.json')
    ap.add_argument('--workflow', type=Path, default=ROOT / 'config/workflow.json')
    ap.add_argument('--visual-at', type=float, required=True)
    ap.add_argument('--asset', required=True)
    ap.add_argument('--seed-x', type=float, default=45)
    ap.add_argument('--seed-y', type=float, default=85)
    ap.add_argument('--offset-y', type=float, default=-19)
    args = ap.parse_args()
    import cv2
    import mediapipe as mp
    import numpy as np

    plan = json.loads(args.plan.read_text())
    visual = next(v for v in plan['visuals'] if v['at'] == args.visual_at and v['asset'] == args.asset)
    selection = json.loads(args.workflow.read_text())
    profile = json.loads((ROOT / f'config/presets/{selection["preset"]}.json').read_text())
    format_rules = json.loads((ROOT / f'config/formats/{selection["format"]}.json').read_text())
    safe_bottom = 78 if format_rules['captions'] else 96
    cap = cv2.VideoCapture(str(args.input))
    input_fps = cap.get(cv2.CAP_PROP_FPS)
    if not cap.isOpened() or input_fps <= 0:
        raise SystemExit('Não foi possível abrir o vídeo local.')
    fps = plan['fps']
    start, end = visual['at'], visual['at'] + visual['duration']
    frames = []
    cursor_frames = 0
    previous = np.array([args.seed_x, args.seed_y], dtype=float)
    last_detected = -float('inf')
    last_tracked = -float('inf')
    previous_gray = None
    features = None
    with mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2,
                                 model_complexity=1, min_detection_confidence=.45,
                                 min_tracking_confidence=.5) as hands, \
         mp.solutions.face_detection.FaceDetection(model_selection=0, min_detection_confidence=.5) as faces:
        for segment_index, segment in enumerate(plan['segments']):
            # A cut is a discontinuity, never an optical-flow continuation.
            previous_gray = None
            features = None
            previous = np.array([args.seed_x, args.seed_y], dtype=float)
            last_detected = -float('inf')
            last_tracked = -float('inf')
            count = max(1, round((segment['sourceEnd'] - segment['sourceStart']) * fps))
            cap.set(cv2.CAP_PROP_POS_FRAMES, round(segment['sourceStart'] * input_fps))
            next_source = round(segment['sourceStart'] * input_fps)
            image = None
            for i in range(count):
                at = (cursor_frames + i) / fps
                source_at = segment['sourceStart'] + i / fps
                target_frame = round(source_at * input_fps)
                while next_source <= target_frame:
                    ok, image = cap.read()
                    if not ok:
                        raise SystemExit(f'Vídeo terminou antes de {source_at:.3f}s')
                    next_source += 1
                if at < start - 1 / fps or at > end + 1 / fps:
                    continue
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                h, w = gray.shape
                flow_palm = None
                if previous_gray is not None and features is not None and len(features) >= 6:
                    moved, status, _ = cv2.calcOpticalFlowPyrLK(previous_gray, gray, features, None,
                                                              winSize=(31, 31), maxLevel=3)
                    if moved is not None:
                        back, back_status, _ = cv2.calcOpticalFlowPyrLK(gray, previous_gray, moved, None,
                                                                      winSize=(31, 31), maxLevel=3)
                        if back is not None:
                            good = (status.ravel() == 1) & (back_status.ravel() == 1) & (np.linalg.norm(features - back, axis=2).ravel() < 1.5)
                            old, new = features[good], moved[good]
                            if len(old) >= 6:
                                matrix, inliers = cv2.estimateAffinePartial2D(old, new, method=cv2.RANSAC, ransacReprojThreshold=2)
                                if matrix is not None and inliers.sum() >= 6:
                                    # Use robust translation for the anchor. Projecting a
                                    # cropped palm through an affine scale can drift far
                                    # beyond the hand when only the wrist stays visible.
                                    delta = np.median((new - old)[inliers.ravel() == 1], axis=0).reshape(2)
                                    candidate_px = np.array([previous[0] * w / 100, previous[1] * h / 100]) + delta
                                    candidate_flow = candidate_px / np.array([w, h]) * 100
                                    if np.linalg.norm(candidate_flow - previous) < 10:
                                        flow_palm = candidate_flow
                            features = new
                detected = hands.process(rgb)
                face_result = faces.process(rgb)
                candidates = []
                for hand in detected.multi_hand_landmarks or []:
                    palm = np.array([[hand.landmark[j].x * 100, hand.landmark[j].y * 100]
                                     for j in [0, 5, 9, 13, 17]]).mean(axis=0)
                    if 0 <= palm[0] <= 100 and 45 <= palm[1] <= 100:
                        candidates.append((palm, hand))
                selected = min(candidates, key=lambda p: np.linalg.norm(p[0] - previous)) if candidates else None
                candidate = selected[0] if selected else None
                found = candidate is not None and np.linalg.norm(candidate - previous) < 25
                if found:
                    previous = .35 * candidate + .65 * flow_palm if flow_palm is not None and np.linalg.norm(candidate - flow_palm) < 10 else candidate
                    last_detected = at
                elif flow_palm is not None and at - last_detected <= .45:
                    previous = flow_palm
                tracked = found or (flow_palm is not None and at - last_detected <= .45)
                if tracked:
                    last_tracked = at
                gap = at - last_tracked
                visibility = max(0, min(1, 1 - gap / .18))
                if found and (features is None or len(features) < 15 or i % 3 == 0):
                    mask = np.zeros_like(gray)
                    polygon = np.array([[round(selected[1].landmark[j].x * w), round(selected[1].landmark[j].y * h)]
                                        for j in [0, 5, 9, 13, 17]], dtype=np.int32)
                    cv2.fillConvexPoly(mask, cv2.convexHull(polygon), 255)
                    mask = cv2.erode(mask, np.ones((5, 5), dtype=np.uint8))
                    features = cv2.goodFeaturesToTrack(gray, mask=mask, maxCorners=80, qualityLevel=.01, minDistance=5)
                previous_gray = gray
                progress = i / max(1, count - 1)
                ease = 4 * progress ** 3 if progress < .5 else 1 - (-2 * progress + 2) ** 3 / 2
                clamp = lambda z: max(1, min(1 + profile['zoomIntensity'], z))
                scale = clamp(segment.get('zoom', 1)) + (clamp(segment.get('zoomTo', segment.get('zoom', 1))) - clamp(segment.get('zoom', 1))) * ease
                x, y = (50 + (previous - 50) * scale).tolist()
                target_y = y + args.offset_y
                # Face boxes are measured, not inferred from the requested logo position.
                face_bottom = 0
                main_faces = [f for f in face_result.detections or []
                              if f.location_data.relative_bounding_box.ymin + f.location_data.relative_bounding_box.height / 2 < .6]
                main_faces = sorted(main_faces, key=lambda f: f.location_data.relative_bounding_box.width * f.location_data.relative_bounding_box.height, reverse=True)[:1]
                for face in main_faces:
                    box = face.location_data.relative_bounding_box
                    left = 50 + (box.xmin * 100 - 50) * scale
                    right = left + box.width * 100 * scale
                    if left - 10 < x < right + 10:
                        face_bottom = max(face_bottom, 50 + ((box.ymin + box.height) * 100 - 50) * scale)
                half_h = 8 * visual['scale']
                target_y = max(target_y, face_bottom + 5 + half_h)
                # Stay clear of default captions and screen edges. If no safe room,
                # hide instead of pinning a logo over the face/caption band.
                safe = target_y + half_h <= safe_bottom and 12 <= x <= 88
                frames.append({'at': round(at, 6), 'sourceAt': round(source_at, 6), 'segment': segment_index,
                               'palmX': round(float(previous[0]), 4), 'palmY': round(float(previous[1]), 4),
                               'x': round(x, 4), 'y': round(target_y, 4),
                               'visibility': visibility if safe else 0, 'detected': bool(found),
                               'measurement': 'landmarks' if found else 'optical-flow' if tracked else 'lost'})
            cursor_frames += count
    cap.release()
    if not frames or sum(p['detected'] for p in frames) / len(frames) < .65:
        raise SystemExit('Tracking insuficiente (<65% de detecções); revise o alvo, não use uma trajetória inventada.')
    # Symmetric five-frame filter: offline, no cumulative lag or per-render randomness.
    points = []
    for i, frame in enumerate(frames):
        window = [p for p in frames[max(0, i - 2):i + 3] if p['segment'] == frame['segment']]
        points.append({'at': frame['at'],
                       'x': round(sum(p['x'] for p in window) / len(window), 4),
                       'y': round(sum(p['y'] for p in window) / len(window), 4),
                       'visibility': round(min(p['visibility'] for p in window), 4)})
    if sum(p['visibility'] > .5 for p in points) / len(points) < .65:
        raise SystemExit('Menos de 65% do trecho tem posição segura e visível; revise o enquadramento.')
    with args.input.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    result = {'sourceSha256': digest, 'format': selection['format'], 'sourceSegments': [[s['sourceStart'], s['sourceEnd'], s.get('zoom', 1), s.get('zoomTo', s.get('zoom', 1))] for s in plan['segments']],
              'zoomIntensity': profile['zoomIntensity'],
              'method': 'MediaPipe Hands 0.10.21, palm 0/5/9/13/17, nearest-hand association; LK forward/backward + RANSAC bridges <=0.45s; centered 5-frame smoothing; main-face avoidance and fade on loss',
              'tracks': [{'visualAt': visual['at'], 'asset': visual['asset'], 'points': points}],
              'measurements': frames,
              'report': {'samples': len(frames), 'detected': sum(p['detected'] for p in frames),
                         'visible': sum(p['visibility'] > .5 for p in points),
                         'xRange': [min(p['x'] for p in points), max(p['x'] for p in points)],
                         'yRange': [min(p['y'] for p in points), max(p['y'] for p in points)]}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result['report'], ensure_ascii=False))


if __name__ == '__main__':
    main()

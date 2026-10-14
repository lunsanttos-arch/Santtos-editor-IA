import type {EditPlan, VisualItem} from './types';

export type TrackPoint = {at: number; x: number; y: number; visibility: number};
export type MotionTracks = {
  sourceSegments?: number[][];
  zoomIntensity?: number;
  format?: string;
  tracks: Array<{visualAt: number; asset: string; points: TrackPoint[]}>;
};
export const segmentSignature = (plan: EditPlan) => plan.segments.map(s =>
  [s.sourceStart, s.sourceEnd, s.zoom ?? 1, s.zoomTo ?? s.zoom ?? 1]);

export const validateTrackContext = (tracks: MotionTracks, plan: EditPlan, intensity: number, format?: string) => {
  if (!tracks.tracks.length) return;
  if (JSON.stringify(tracks.sourceSegments) !== JSON.stringify(segmentSignature(plan)) || tracks.zoomIntensity !== intensity || (format !== undefined && tracks.format !== format)) {
    throw new Error('Tracking desatualizado: regenere motion-tracks.json após mudar cortes, formato ou intensidade da câmera.');
  }
};

export const trackedPosition = (item: VisualItem, now: number, data: MotionTracks) => {
  const points = data.tracks.find(t => t.visualAt === item.at && t.asset === item.asset)?.points;
  if (!points) return {x: item.x, y: item.y, visibility: 1};
  if (!points.length || now < points[0].at || now > points[points.length - 1].at) {
    return {x: item.x, y: item.y, visibility: 0};
  }
  let lo = 0, hi = points.length - 1;
  while (hi - lo > 1) {
    const mid = Math.floor((lo + hi) / 2);
    if (points[mid].at <= now) lo = mid; else hi = mid;
  }
  const a = points[lo], b = points[hi];
  const t = a.at === b.at ? 0 : Math.max(0, Math.min(1, (now - a.at) / (b.at - a.at)));
  return {x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t,
    visibility: a.visibility + (b.visibility - a.visibility) * t};
};

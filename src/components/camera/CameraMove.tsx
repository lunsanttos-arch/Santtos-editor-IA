import {Easing, interpolate} from 'remotion';
import {style} from '../../style';

// Existing v0.4 zoom endpoints remain valid. Style caps intensity; no random moves.
export const cameraScale = (frame: number, duration: number, from: number, to: number) => {
  const bound = (v: number) => Math.max(1, Math.min(1 + style.zoomIntensity, v));
  return interpolate(frame, [0, Math.max(1, duration - 1)], [bound(from), bound(to)], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic),
  });
};

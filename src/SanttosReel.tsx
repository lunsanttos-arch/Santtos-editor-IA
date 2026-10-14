import {VisualElement} from './components/graphics/VisualElement';
import {Motion} from './components/titles/Motion';
import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import transcriptJson from '../data/transcript.json';
import planJson from '../data/edit-plan.json';
import type {BrollItem, EditPlan, TextOverlay, Transcript} from './types';
import {smartCaptionCards, timelineWords} from './timeline';
import {style, format} from './style';
import {Caption} from './components/captions/Caption';
import {cameraScale} from './components/camera/CameraMove';
import {SoundLayer} from './components/sound/SoundCue';

const transcript = transcriptJson as Transcript;
const plan = planJson as EditPlan;

const CaptionLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const now = frame / fps;
  if (!format.captions) return null;
  const explicit = (plan.captions ?? []).find((c) => now >= c.at && now < c.at + c.duration);
  if (explicit) return <Caption card={explicit} />;
  if ((plan.captions ?? []).length > 0) return null;
  const card = smartCaptionCards(timelineWords(transcript, plan)).find((c) => now >= c.start && now < c.end);
  return card ? <Caption card={{at: card.start, duration: card.end - card.start, text: card.text, highlight: []}} /> : null;
};

const MotionLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const now = frame / fps;
  const item = (plan.motions ?? []).find((m) => now >= m.at && now <= m.at + m.duration);
  return item ? <Motion item={item} /> : null;
};

const OverlayLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const now = frame / fps;
  const item: TextOverlay | undefined = (plan.overlays ?? []).find((o) => now >= o.at && now <= o.at + o.duration);
  if (!item) return null;
  const top = item.position === 'bottom' ? 1460 : item.position === 'center' ? 820 : 110;
  return <div style={{
    position: 'absolute', top, left: 90, right: 90, zIndex: 25,
    color: '#fff', fontFamily: 'Arial, Helvetica, sans-serif', fontSize: 42, fontWeight: 800,
    textAlign: 'center', padding: '12px 18px', borderRadius: 18, background: 'rgba(0,0,0,.56)',
  }}>{item.text}</div>;
};

const BrollVisual: React.FC<{item: BrollItem}> = ({item}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - Math.round(item.at * fps);
  const total = Math.max(1, Math.round(item.duration * fps));
  const enter = spring({fps, frame: Math.max(0, local), config: {damping: 18, stiffness: 150}});
  const opacity = interpolate(local, [0, 5, Math.max(6, total - 5), total], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const layout = item.layout ?? 'full';
  const box = layout === 'card'
    ? {left: 74, right: 74, top: 360, bottom: 500, borderRadius: 38}
    : layout === 'split'
      ? {left: 0, right: 0, top: 0, height: 900, borderRadius: 0}
      : {left: 0, right: 0, top: 0, bottom: 0, borderRadius: 0};
  const common: React.CSSProperties = {
    position: 'absolute', ...box, overflow: 'hidden', zIndex: 20, opacity,
    transform: `scale(${0.97 + enter * 0.03})`, boxShadow: layout === 'card' ? '0 30px 80px rgba(0,0,0,.45)' : undefined,
  };

  if (item.type === 'image' && item.asset) {
    return <div style={common}><Img src={staticFile(`broll/${item.asset}`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} /></div>;
  }
  if (item.type === 'video' && item.asset) {
    return <div style={common}><OffthreadVideo muted src={staticFile(`broll/${item.asset}`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} /></div>;
  }
  return (
    <div style={{...common, background: 'linear-gradient(145deg, rgba(12,12,12,.96), rgba(38,38,38,.94))', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 64}}>
      <div style={{width: '100%', textAlign: 'center'}}>
        <div style={{height: 8, width: 130, background: style.accent, borderRadius: 999, margin: '0 auto 28px'}} />
        <div style={{color: '#fff', fontFamily: 'Arial, Helvetica, sans-serif', fontSize: 92, fontWeight: 950, lineHeight: .95, textTransform: 'uppercase'}}>{item.text}</div>
        {item.subtext ? <div style={{marginTop: 26, color: 'rgba(255,255,255,.84)', fontFamily: 'Arial, Helvetica, sans-serif', fontSize: 40, fontWeight: 700, lineHeight: 1.15}}>{item.subtext}</div> : null}
      </div>
    </div>
  );
};

const BrollLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const now = frame / fps;
  const item = (plan.broll ?? []).find((b) => now >= b.at && now <= b.at + b.duration);
  return item ? <BrollVisual item={item} /> : null;
};

const VisualLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const now = frame / fps;
  const active = (plan.visuals ?? []).filter((v) => now >= v.at && now <= v.at + v.duration).slice(0, 2);
  return <>{active.map((item, i) => <VisualElement key={`${item.at}-${item.type}-${i}`} item={item} />)}</>;
};

const SegmentVideo: React.FC<{
  sourceStart: number; durationFrames: number; zoom: number; zoomTo: number; width: number; height: number; fps: number;
}> = ({sourceStart, durationFrames, zoom, zoomTo, width, height, fps}) => {
  const frame = useCurrentFrame();
  const scale = cameraScale(frame, durationFrames, zoom, zoomTo);
  return <OffthreadVideo
    muted={!format.sourceAudio} src={staticFile('input.mp4')} trimBefore={Math.round(sourceStart * fps)} durationInFrames={durationFrames}
    style={{width, height, objectFit: 'cover', transform: `scale(${scale})`}}
  />;
};

export const SanttosReel: React.FC = () => {
  const {fps, width, height} = useVideoConfig();
  let outputCursorFrames = 0;
  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      {plan.segments.map((segment, index) => {
        const durationFrames = Math.max(1, Math.round((segment.sourceEnd - segment.sourceStart) * fps));
        const from = outputCursorFrames;
        outputCursorFrames += durationFrames;
        const zoom = segment.zoom ?? 1;
        const zoomTo = segment.zoomTo ?? zoom;
        return (
          <Sequence key={index} from={from} durationInFrames={durationFrames}>
            <SegmentVideo sourceStart={segment.sourceStart} durationFrames={durationFrames} zoom={zoom} zoomTo={zoomTo} width={width} height={height} fps={fps} />
          </Sequence>
        );
      })}
      <SoundLayer plan={plan} />
      <BrollLayer />
      <VisualLayer />
      <MotionLayer />
      <OverlayLayer />
      <CaptionLayer />
    </AbsoluteFill>
  );
};

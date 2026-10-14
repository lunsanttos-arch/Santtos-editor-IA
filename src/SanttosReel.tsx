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
import type {BrollItem, CaptionCard, EditPlan, MotionGraphic, TextOverlay, Transcript, VisualItem} from './types';
import {smartCaptionCards, timelineWords} from './timeline';

const transcript = transcriptJson as Transcript;
const plan = planJson as EditPlan;

const normalize = (value: string) =>
  value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]/g, '').toLowerCase();

const ExplicitCaption: React.FC<{card: CaptionCard}> = ({card}) => {
  const {fps} = useVideoConfig();
  const frame = useCurrentFrame();
  const local = frame - Math.round(card.at * fps);
  const enter = spring({fps, frame: Math.max(0, local), config: {damping: 16, stiffness: 220}});
  const highlights = new Set((card.highlight ?? []).map(normalize));
  const words = card.text.split(/\s+/).filter(Boolean);
  return (
    <div style={{
      position: 'absolute', left: 72, right: 72, bottom: 225,
      display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 12,
      fontFamily: 'Arial, Helvetica, sans-serif', fontSize: 72, fontWeight: 900,
      lineHeight: 1.02, textTransform: 'uppercase', textAlign: 'center',
      textShadow: '0 5px 18px rgba(0,0,0,.9)',
      transform: `scale(${0.94 + enter * 0.06}) translateY(${(1 - enter) * 22}px)`, opacity: enter,
      zIndex: 40,
    }}>
      {words.map((word, index) => (
        <span key={`${word}-${index}`} style={{color: highlights.has(normalize(word)) ? '#ffe600' : '#ffffff'}}>{word}</span>
      ))}
    </div>
  );
};

const CaptionLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const now = frame / fps;
  const explicit = (plan.captions ?? []).find((c) => now >= c.at && now <= c.at + c.duration);
  if (explicit) return <ExplicitCaption card={explicit} />;
  if ((plan.captions ?? []).length > 0) return null;

  const words = timelineWords(transcript, plan);
  const cards = smartCaptionCards(words);
  const card = cards.find((c) => now >= c.start && now <= c.end);
  if (!card) return null;
  const activeIndex = card.words.findIndex((w) => now >= w.outputStart && now <= w.outputEnd + 0.03);
  return (
    <div style={{
      position: 'absolute', left: 72, right: 72, bottom: 225,
      display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 12,
      fontFamily: 'Arial, Helvetica, sans-serif', fontSize: 72, fontWeight: 900,
      lineHeight: 1.02, textTransform: 'uppercase', textAlign: 'center',
      textShadow: '0 5px 18px rgba(0,0,0,.9)', zIndex: 40,
    }}>
      {card.words.map((word, index) => (
        <span key={`${word.outputStart}-${index}`} style={{
          color: index === activeIndex ? '#ffe600' : '#ffffff',
          transform: index === activeIndex ? 'scale(1.045)' : 'scale(1)',
        }}>{word.text.trim()}</span>
      ))}
    </div>
  );
};

const Motion: React.FC<{item: MotionGraphic}> = ({item}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - Math.round(item.at * fps);
  const enter = spring({fps, frame: Math.max(0, local), config: {damping: 15, stiffness: 180}});
  const total = Math.max(1, Math.round(item.duration * fps));
  const opacity = interpolate(local, [0, 5, Math.max(6, total - 6), total], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const top = item.position === 'bottom' ? 1270 : item.position === 'center' ? 650 : 190;
  const isTag = item.type === 'tag';
  const isNumber = item.type === 'number';
  const isCallout = item.type === 'callout';
  const isSteps = item.type === 'steps';
  const isComparison = item.type === 'comparison';
  const steps = isSteps ? item.text.split('|').map((s) => s.trim()).filter(Boolean).slice(0, 3) : [];
  const comparison = isComparison ? item.text.split('|').map((s) => s.trim()).filter(Boolean).slice(0, 2) : [];

  return (
    <div style={{
      position: 'absolute', top, left: 80, right: 80, opacity, zIndex: 30,
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      transform: `translateY(${(1 - enter) * 45}px) scale(${0.9 + enter * 0.1})`, pointerEvents: 'none',
    }}>
      {isSteps ? (
        <div style={{display: 'flex', gap: 14, width: '100%', justifyContent: 'center'}}>
          {steps.map((step, i) => <div key={step} style={{
            background: 'rgba(0,0,0,.72)', borderRadius: 24, padding: '18px 20px', minWidth: 220,
            color: '#fff', fontFamily: 'Arial, Helvetica, sans-serif', fontWeight: 900, fontSize: 36,
            textAlign: 'center', boxShadow: '0 12px 34px rgba(0,0,0,.3)',
          }}><span style={{color: '#ffe600'}}>{i + 1}</span> {step}</div>)}
        </div>
      ) : isComparison ? (
        <div style={{display: 'flex', alignItems: 'center', gap: 18, width: '100%', justifyContent: 'center'}}>
          <div style={{background: 'rgba(0,0,0,.75)', borderRadius: 24, padding: '22px 28px', color: '#fff', fontSize: 46, fontWeight: 900}}>{comparison[0] ?? item.text}</div>
          <div style={{color: '#ffe600', fontSize: 42, fontWeight: 900}}>×</div>
          <div style={{background: 'rgba(0,0,0,.75)', borderRadius: 24, padding: '22px 28px', color: '#fff', fontSize: 46, fontWeight: 900}}>{comparison[1] ?? ''}</div>
        </div>
      ) : (
        <div style={{
          padding: isTag ? '12px 24px' : isCallout ? '20px 28px' : '10px 18px',
          borderRadius: isTag ? 999 : 20,
          background: isTag ? 'rgba(0,0,0,.68)' : isCallout ? 'rgba(0,0,0,.78)' : 'rgba(0,0,0,.35)',
          borderLeft: isCallout ? '8px solid #ffe600' : undefined,
          color: isNumber ? '#ffe600' : '#fff', fontFamily: 'Arial, Helvetica, sans-serif', fontWeight: 900,
          fontSize: isNumber ? 132 : isTag ? 46 : isCallout ? 58 : 86, lineHeight: 1,
          textAlign: 'center', textTransform: 'uppercase', textShadow: '0 6px 22px rgba(0,0,0,.75)',
        }}>{item.text}</div>
      )}
      {item.subtext ? <div style={{
        marginTop: 14, padding: '8px 16px', borderRadius: 14, background: 'rgba(0,0,0,.46)',
        color: '#fff', fontFamily: 'Arial, Helvetica, sans-serif', fontSize: 34, fontWeight: 700,
        textAlign: 'center', textShadow: '0 4px 16px rgba(0,0,0,.8)',
      }}>{item.subtext}</div> : null}
    </div>
  );
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
        <div style={{height: 8, width: 130, background: '#ffe600', borderRadius: 999, margin: '0 auto 28px'}} />
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

const VisualElement: React.FC<{item: VisualItem}> = ({item}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const local = frame - Math.round(item.at * fps);
  const total = Math.max(1, Math.round(item.duration * fps));
  const progress = spring({fps, frame: Math.max(0, local), config: {damping: item.enter === 'bounce' ? 10 : 16, stiffness: item.enter === 'bounce' ? 240 : 190}});
  const opacity = interpolate(local, [0, 4, Math.max(5, total - 5), total], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const baseScale = Math.max(0.5, Math.min(1.6, item.scale || 1));
  const enterScale = item.enter === 'fade' ? 1 : item.enter === 'slide' ? 1 : 0.72 + progress * 0.28;
  const slideY = item.enter === 'slide' ? (1 - progress) * 60 : 0;
  const left = `${item.x}%`;
  const top = `${item.y}%`;
  const common: React.CSSProperties = {
    position: 'absolute', left, top, zIndex: 35, opacity,
    transform: `translate(-50%, -50%) translateY(${slideY}px) scale(${baseScale * enterScale})`,
    transformOrigin: 'center center', pointerEvents: 'none',
  };

  if (item.type === 'brand') {
    return <div style={{...common, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
      <div style={{width: 196, height: 196, borderRadius: 42, background: '#fff', padding: 18, boxShadow: '0 18px 48px rgba(0,0,0,.38)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        {item.asset ? <Img src={staticFile(`brands/${item.asset}`)} style={{width: '100%', height: '100%', objectFit: 'contain'}} /> : <div style={{fontSize: 72, fontWeight: 950}}>AI</div>}
      </div>
      {item.text ? <div style={{background: 'rgba(0,0,0,.72)', color: '#fff', borderRadius: 999, padding: '8px 18px', fontFamily: 'Arial, Helvetica, sans-serif', fontWeight: 900, fontSize: 30, whiteSpace: 'nowrap', textShadow: '0 3px 12px rgba(0,0,0,.7)'}}>{item.text}</div> : null}
    </div>;
  }
  if (item.type === 'arrow') {
    return <div style={{...common, color: '#ffe600', fontSize: 130, fontWeight: 950, textShadow: '0 8px 24px rgba(0,0,0,.6)'}}>➜</div>;
  }
  if (item.type === 'circle') {
    return <div style={{...common, width: 210, height: 210, borderRadius: '50%', border: '14px solid #ffe600', boxShadow: '0 8px 28px rgba(0,0,0,.35)'}} />;
  }
  return <div style={{...common, background: item.type === 'badge' ? '#ffe600' : 'rgba(0,0,0,.78)', color: item.type === 'badge' ? '#111' : '#fff', borderRadius: item.type === 'badge' ? 999 : 22, padding: '14px 24px', fontFamily: 'Arial, Helvetica, sans-serif', fontSize: 46, fontWeight: 950, textAlign: 'center', whiteSpace: 'nowrap', boxShadow: '0 16px 40px rgba(0,0,0,.32)'}}>{item.text}</div>;
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
  const scale = interpolate(frame, [0, Math.max(1, durationFrames - 1)], [zoom, zoomTo], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return <OffthreadVideo
    src={staticFile('input.mp4')} trimBefore={Math.round(sourceStart * fps)} durationInFrames={durationFrames}
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
      <BrollLayer />
      <VisualLayer />
      <MotionLayer />
      <OverlayLayer />
      <CaptionLayer />
    </AbsoluteFill>
  );
};

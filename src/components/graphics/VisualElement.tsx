import React from 'react';
import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {style} from '../../style';
import type {VisualItem} from '../../types';

export const VisualElement: React.FC<{item: VisualItem}> = ({item}) => {
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
    return <div style={{...common, color: style.accent, fontSize: 130, fontWeight: 950, textShadow: '0 8px 24px rgba(0,0,0,.6)'}}>➜</div>;
  }
  if (item.type === 'circle') {
    return <div style={{...common, width: 210, height: 210, borderRadius: '50%', border: `14px solid ${style.accent}`, boxShadow: '0 8px 28px rgba(0,0,0,.35)'}} />;
  }
  return <div style={{...common, background: item.type === 'badge' ? style.accent : 'rgba(0,0,0,.78)', color: item.type === 'badge' ? '#111' : '#fff', borderRadius: item.type === 'badge' ? 999 : 22, padding: '14px 24px', fontFamily: 'Arial, Helvetica, sans-serif', fontSize: 46, fontWeight: 950, textAlign: 'center', whiteSpace: 'nowrap', boxShadow: '0 16px 40px rgba(0,0,0,.32)'}}>{item.text}</div>;
};


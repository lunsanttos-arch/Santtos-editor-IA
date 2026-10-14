import React from 'react';
import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {style} from '../../style';
import type {MotionGraphic} from '../../types';

export const Motion: React.FC<{item: MotionGraphic}> = ({item}) => {
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
          }}><span style={{color: style.accent}}>{i + 1}</span> {step}</div>)}
        </div>
      ) : isComparison ? (
        <div style={{display: 'flex', alignItems: 'center', gap: 18, width: '100%', justifyContent: 'center'}}>
          <div style={{background: 'rgba(0,0,0,.75)', borderRadius: 24, padding: '22px 28px', color: '#fff', fontSize: 46, fontWeight: 900}}>{comparison[0] ?? item.text}</div>
          <div style={{color: style.accent, fontSize: 42, fontWeight: 900}}>×</div>
          <div style={{background: 'rgba(0,0,0,.75)', borderRadius: 24, padding: '22px 28px', color: '#fff', fontSize: 46, fontWeight: 900}}>{comparison[1] ?? ''}</div>
        </div>
      ) : (
        <div style={{
          padding: isTag ? '12px 24px' : isCallout ? '20px 28px' : '10px 18px',
          borderRadius: isTag ? 999 : 20,
          background: isTag ? 'rgba(0,0,0,.68)' : isCallout ? 'rgba(0,0,0,.78)' : 'rgba(0,0,0,.35)',
          borderLeft: isCallout ? `8px solid ${style.accent}` : undefined,
          color: isNumber ? style.accent : '#fff', fontFamily: 'Arial, Helvetica, sans-serif', fontWeight: 900,
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


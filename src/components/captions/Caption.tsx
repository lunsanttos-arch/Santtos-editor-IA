import React from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {style} from '../../style';
import type {CaptionCard} from '../../types';

export const normalize = (s: string) => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/gi, '').toLowerCase();

type Props = {card: CaptionCard; mode?: string};
export const Caption: React.FC<Props> = ({card, mode = style.captionStyle}) => {
  const frame = useCurrentFrame();
  const {fps, width} = useVideoConfig();
  const local = frame - Math.round(card.at * fps);
  const total = Math.max(1, Math.round(card.duration * fps));
  const ramp = Math.min(7, total / 3);
  const enter = interpolate(local, [0, ramp], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
  const exit = interpolate(local, [total - ramp, total], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const highlights = new Set((card.highlight ?? []).slice(0, style.maxHighlights).map(normalize));
  return <div style={{position: 'absolute', left: width * .075, right: width * .075,
    bottom: style.captionBottom, zIndex: 40, display: 'flex', justifyContent: 'center'}}>
    <div style={{fontFamily: style.fontFamily, fontSize: style.captionSize, fontWeight: 750,
      lineHeight: 1.18, letterSpacing: '-0.025em', textAlign: 'center', textWrap: 'balance',
      padding: '16px 24px', borderRadius: 18, background: 'rgba(10,12,16,.77)',
      boxShadow: '0 8px 28px rgba(0,0,0,.20)', color: 'white', opacity: enter * exit,
      transform: `translateY(${(1 - enter) * 14}px)`}}>
      {card.text.split(/\s+/).map((word, i) => {
        const progress = mode === 'kinetic' ? interpolate(local - i * 1.5, [0, 5], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
        return <React.Fragment key={i}>{i > 0 ? ' ' : ''}<span style={{display: 'inline-block',
          color: mode !== 'clean' && highlights.has(normalize(word)) ? style.accent : 'white',
          opacity: progress, transform: `translateY(${(1 - progress) * 8}px)`}}>{word}</span></React.Fragment>;
      })}
    </div>
  </div>;
};

export const CleanCaption: React.FC<Props> = (p) => <Caption {...p} mode="clean" />;
export const EmphasisCaption: React.FC<Props> = (p) => <Caption {...p} mode="emphasis" />;
export const KineticCaption: React.FC<Props> = (p) => <Caption {...p} mode="kinetic" />;

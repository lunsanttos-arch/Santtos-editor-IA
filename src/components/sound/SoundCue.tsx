import React from 'react';
import {Audio, Sequence, staticFile, useVideoConfig} from 'remotion';
import {format, style} from '../../style';
import type {EditPlan} from '../../types';

export type SoundName = 'soft-pop' | 'whoosh' | 'tick' | 'impact' | 'swipe' | 'subtle-riser';
export const SoundCue: React.FC<{at: number; name: SoundName}> = ({at, name}) => {
  const {fps} = useVideoConfig();
  return <Sequence from={Math.round(at * fps)} durationInFrames={Math.ceil(.6 * fps)}>
    <Audio src={staticFile(`sounds/${name}.wav`)} volume={style.soundVolume} />
  </Sequence>;
};

export const SoundLayer: React.FC<{plan: EditPlan}> = ({plan}) => {
  if (style.soundDesign === 'off' || !format.sourceAudio) return null;
  let previous = -Infinity;
  const events = [...(plan.visuals ?? [])].sort((a, b) => a.at - b.at).filter((item) => {
    if (!item.reason.trim() || item.enter === 'fade' || item.at - previous < style.minSoundGap) return false;
    previous = item.at;
    return true;
  });
  return <>{events.map((item, i) => <SoundCue key={i} at={item.at} name={item.enter === 'slide' ? 'swipe' : 'soft-pop'} />)}</>;
};

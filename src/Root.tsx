import React from 'react';
import {Composition} from 'remotion';
import {SanttosReel} from './SanttosReel';
import planJson from '../data/edit-plan.json';
import type {EditPlan} from './types';
import {outputDuration} from './timeline';

const plan = planJson as EditPlan;
const durationInFrames = Math.max(1, Math.ceil(outputDuration(plan) * plan.fps));

export const RemotionRoot: React.FC = () => (
  <Composition
    id="SanttosReel"
    component={SanttosReel}
    fps={plan.fps}
    width={plan.width}
    height={plan.height}
    durationInFrames={durationInFrames}
  />
);

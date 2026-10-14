import {test} from 'node:test';
import assert from 'node:assert/strict';
import {trackedPosition, validateTrackContext, type MotionTracks} from '../src/tracking.ts';
import type {VisualItem, EditPlan} from '../src/types.ts';

const item: VisualItem = {at: 1, duration: 2, asset: 'chatgpt.svg', type: 'brand', text: '',
  x: 50, y: 50, scale: 1, enter: 'pop', reason: 'gesture'};
const data: MotionTracks = {tracks: [{visualAt: 1, asset: 'chatgpt.svg', points: [
  {at: 1, x: 20, y: 60, visibility: 1}, {at: 2, x: 40, y: 70, visibility: 0},
]}]};

test('tracked logo follows measured movement and fades on lost detection', () => {
  assert.deepEqual(trackedPosition(item, 1.5, data), {x: 30, y: 65, visibility: .5});
});
test('a tracked logo is hidden outside measured time rather than freezing', () => {
  assert.equal(trackedPosition(item, 3, data).visibility, 0);
});
test('legacy untracked visuals retain their static position', () => {
  assert.deepEqual(trackedPosition(item, 1.5, {tracks: []}), {x: 50, y: 50, visibility: 1});
});
test('editing cuts invalidates a track instead of moving it onto unrelated footage', () => {
  const plan = {segments: [{sourceStart: 0, sourceEnd: 3}]} as EditPlan;
  assert.throws(() => validateTrackContext({...data, sourceSegments: [[1, 4, 1, 1]], zoomIntensity: .08}, plan, .08));
  assert.doesNotThrow(() => validateTrackContext({...data, sourceSegments: [[0, 3, 1, 1]], zoomIntensity: .08}, plan, .08));
});

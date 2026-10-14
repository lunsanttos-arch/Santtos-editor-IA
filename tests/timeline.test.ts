import {test} from 'node:test';
import assert from 'node:assert/strict';
import {smartCaptionCards, type TimelineWord} from '../src/timeline.ts';

const words = (texts: string[]): TimelineWord[] => texts.map((text, i) => ({text,
  start: i * .18, end: i * .18 + .16, outputStart: i * .18, outputEnd: i * .18 + .16}));

test('a short phrase can exceed six words without a mechanical break', () => {
  const cards = smartCaptionCards(words(['Eu', 'vi', 'o', 'que', 'ele', 'fez', 'aqui.']));
  assert.equal(cards.length, 1);
});

test('sentence punctuation separates units even before three words', () => {
  const cards = smartCaptionCards(words(['Sim.', 'Vamos', 'começar.']));
  assert.deepEqual(cards.map(c => c.text), ['Sim.', 'Vamos começar.']);
});

test('a long pause starts another unit without losing any words', () => {
  const list = words(['Primeira', 'ideia.', 'Outra', 'ideia.']);
  list[2].outputStart += 1;
  list[2].outputEnd += 1;
  list[3].outputStart += 1;
  list[3].outputEnd += 1;
  assert.deepEqual(smartCaptionCards(list).flatMap(c => c.words), list);
  assert.equal(smartCaptionCards(list).length, 2);
});

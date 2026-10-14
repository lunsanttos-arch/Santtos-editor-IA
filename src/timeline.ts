import type {EditPlan, Transcript, Word} from './types';

export type TimelineWord = Word & {
  outputStart: number;
  outputEnd: number;
};

export const outputDuration = (plan: EditPlan) =>
  plan.segments.reduce((sum, segment) => sum + Math.max(0, segment.sourceEnd - segment.sourceStart), 0);

export const timelineWords = (transcript: Transcript, plan: EditPlan): TimelineWord[] => {
  const result: TimelineWord[] = [];
  let cursor = 0;

  for (const segment of plan.segments) {
    const duration = segment.sourceEnd - segment.sourceStart;
    for (const word of transcript.words) {
      if (word.end <= segment.sourceStart || word.start >= segment.sourceEnd) continue;
      const clippedStart = Math.max(word.start, segment.sourceStart);
      const clippedEnd = Math.min(word.end, segment.sourceEnd);
      result.push({
        ...word,
        outputStart: cursor + (clippedStart - segment.sourceStart),
        outputEnd: cursor + (clippedEnd - segment.sourceStart),
      });
    }
    cursor += duration;
  }
  return result;
};

export const smartCaptionCards = (words: TimelineWord[]) => {
  const cards: Array<{start: number; end: number; text: string; words: TimelineWord[]}> = [];
  let current: TimelineWord[] = [];

  const flush = () => {
    if (!current.length) return;
    cards.push({
      start: current[0].outputStart,
      end: current[current.length - 1].outputEnd + 0.08,
      text: current.map((w) => w.text.trim()).join(' ').replace(/\s+/g, ' ').trim(),
      words: current,
    });
    current = [];
  };

  for (const word of words) {
    const previous = current[current.length - 1];
    const gap = previous ? word.outputStart - previous.outputEnd : 0;
    const endsPhrase = previous ? /[.!?;:]$/.test(previous.text.trim()) : false;
    const commaBreak = previous ? /,$/.test(previous.text.trim()) && current.length >= 3 : false;
    const textLength = current.map((w) => w.text.trim()).join(' ').length;
    const readingWindow = previous && current.length ? previous.outputEnd - current[0].outputStart : 0;
    // Prefer phrasing and reading time over a fixed word count. Avoid leaving a
    // preposition/article dangling when a safety limit requires another card.
    const dangling = previous ? /^(a|o|as|os|de|do|da|dos|das|em|no|na|nos|nas|para|com|um|uma|e|que)$/i.test(previous.text.trim()) : false;
    const needsRoom = (textLength > 40 || readingWindow > 2.4) && !dangling;
    if (previous && (gap > 0.65 || endsPhrase || commaBreak || (gap > 0.3 && !dangling) || needsRoom || textLength > 64)) flush();
    current.push(word);
  }
  flush();
  return cards;
};

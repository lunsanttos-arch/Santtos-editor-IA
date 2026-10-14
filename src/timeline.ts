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
    const endsPhrase = previous ? /[.!?,;:]$/.test(previous.text.trim()) : false;
    const tooLong = current.length >= 6;
    const naturalBreak = current.length >= 3 && (gap > 0.3 || endsPhrase);
    if (previous && (gap > 0.65 || tooLong || naturalBreak)) flush();
    current.push(word);
  }
  flush();
  return cards;
};

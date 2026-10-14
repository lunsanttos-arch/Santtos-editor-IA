export type Word = {start: number; end: number; text: string; probability?: number};
export type TranscriptSegment = {start: number; end: number; text: string; words?: Word[]};
export type Transcript = {sourceFile: string; language: string; duration: number; segments?: TranscriptSegment[]; words: Word[]};

export type EditSegment = {
  sourceStart: number;
  sourceEnd: number;
  zoom?: number;
  zoomTo?: number;
  reason?: string;
};

export type CaptionCard = {at: number; duration: number; text: string; highlight?: string[]};
export type MotionType = 'headline' | 'tag' | 'quote' | 'number' | 'callout' | 'steps' | 'comparison';
export type MotionGraphic = {
  at: number;
  duration: number;
  type: MotionType;
  text: string;
  subtext?: string;
  position?: 'top' | 'center' | 'bottom';
};
export type TextOverlay = {at: number; duration: number; text: string; position?: 'top' | 'center' | 'bottom'};

export type BrollType = 'graphic' | 'image' | 'video';
export type BrollItem = {
  at: number;
  duration: number;
  type: BrollType;
  asset?: string;
  text: string;
  subtext?: string;
  layout?: 'full' | 'card' | 'split';
  reason?: string;
};

export type VisualType = 'brand' | 'badge' | 'icon' | 'arrow' | 'circle' | 'label';
export type VisualItem = {
  at: number;
  duration: number;
  type: VisualType;
  text: string;
  asset: string;
  x: number;
  y: number;
  scale: number;
  enter: 'pop' | 'fade' | 'slide' | 'bounce';
  reason: string;
};

export type EditPlan = {
  fps: number;
  width: number;
  height: number;
  segments: EditSegment[];
  captions?: CaptionCard[];
  motions?: MotionGraphic[];
  overlays?: TextOverlay[];
  broll?: BrollItem[];
  visuals?: VisualItem[];
};

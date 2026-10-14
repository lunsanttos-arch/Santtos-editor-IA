import selection from '../../config/workflow.json';
import clean from '../../config/presets/santtos-clean.json';
import fast from '../../config/presets/santtos-fast.json';
import cinematic from '../../config/presets/santtos-cinematic.json';
import journal from '../../config/presets/santtos-journal.json';
import sales from '../../config/presets/santtos-sales.json';
import falado from '../../config/formats/falado.json';
import mudo from '../../config/formats/mudo.json';
import narrado from '../../config/formats/narrado.json';

export const profiles = {'santtos-clean': clean, 'santtos-fast': fast,
  'santtos-cinematic': cinematic, 'santtos-journal': journal, 'santtos-sales': sales};
export type PresetName = keyof typeof profiles;
export const formats = {falado, mudo, narrado};
export type FormatName = keyof typeof formats;
export type StyleProfile = typeof clean;
export const style = profiles[selection.preset as PresetName];
export const format = formats[selection.format as FormatName];
if (!style || !format) throw new Error('Seleção inválida em config/workflow.json');

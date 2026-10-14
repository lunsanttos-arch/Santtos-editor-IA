import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('check_edit', ROOT / 'scripts/check_edit.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EditRules(unittest.TestCase):
    def setUp(self):
        self.plan = {'fps': 30, 'width': 1080, 'height': 1920}
        self.plan.update(segments=[{'sourceStart': 0, 'sourceEnd': 5, 'zoom': 1, 'zoomTo': 1, 'reason': 'test'}],
                         captions=[], motions=[], overlays=[], broll=[], visuals=[])
        self.transcript = {'duration': 5, 'words': [{'start': .2, 'end': .8, 'text': 'ChatGPT'}]}
        self.rules = module.load(ROOT / 'config/formats/falado.json')
        self.profile = module.load(ROOT / 'config/presets/santtos-clean.json')
        self.schema = module.load(ROOT / 'schemas/edit-plan.schema.json')
        self.director = {'cues': [{'id': 'cue-001', 'priority': 'high', 'sourceAt': .2,
                                  'sourceEnd': .8, 'subject': 'ChatGPT', 'assetHint': 'chatgpt.svg'}]}

    def errors(self, director=None):
        return module.check(self.plan, self.transcript, director, self.rules, self.profile, ROOT / 'public', self.schema)

    def logo(self, at=.2):
        return {'at': at, 'duration': 1, 'type': 'brand', 'asset': 'chatgpt.svg', 'text': 'ChatGPT',
                'x': 68, 'y': 34, 'scale': 1, 'enter': 'pop', 'reason': 'pedido explícito'}

    def test_v04_plan_remains_valid(self):
        self.assertEqual([], self.errors())

    def test_missing_logo_rejected_even_with_headline(self):
        self.plan['motions'] = [{'at': .2, 'duration': 1, 'type': 'headline', 'text': 'ChatGPT', 'subtext': '', 'position': 'top'}]
        self.assertTrue(any('Pedido visual' in e for e in self.errors(self.director)))

    def test_expected_logo_covers_request(self):
        self.plan['visuals'] = [self.logo()]
        self.assertEqual([], self.errors(self.director))

    def test_removed_phrase_does_not_require_logo(self):
        self.plan['segments'][0]['sourceStart'] = 1
        self.assertEqual([], self.errors(self.director))

    def test_repeated_source_requires_visual_twice(self):
        self.plan['segments'] *= 2
        self.plan['visuals'] = [self.logo()]
        self.assertEqual(1, len(module.uncovered_cues(self.plan, self.director)))
        self.plan['visuals'].append(self.logo(5.2))
        self.assertEqual([], module.uncovered_cues(self.plan, self.director))

    def test_asset_traversal_rejected(self):
        self.plan['visuals'] = [self.logo()]
        self.plan['visuals'][0]['asset'] = '../../package.json'
        self.assertTrue(any('asset local' in e for e in self.errors()))

    def test_timeline_overrun_rejected(self):
        self.plan['visuals'] = [self.logo(4.5)]
        self.assertTrue(any('timeline' in e for e in self.errors()))

    def test_cut_inside_word_rejected(self):
        self.plan['segments'][0]['sourceStart'] = .4
        self.assertTrue(any('dentro de palavra' in e for e in self.errors()))

    def test_schema_rejects_unknown_fields(self):
        self.plan['madeUp'] = True
        self.assertTrue(any('schema' in e for e in self.errors()))

    def test_narrated_visual_gap_rejected(self):
        self.rules = module.load(ROOT / 'config/formats/narrado.json')
        self.assertTrue(any('Sem imagem' in e for e in self.errors()))

    def test_density_rejected(self):
        self.plan['visuals'] = [self.logo(), self.logo(), self.logo()]
        self.assertTrue(any('simultâneos' in e for e in self.errors()))

    def test_highlight_not_in_caption_rejected(self):
        self.plan['captions'] = [{'at': 0, 'duration': 1, 'text': 'Uma ideia', 'highlight': ['venda']}]
        self.assertTrue(any('ausente do texto' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()

"""
Test REST API handlers and endpoint responses
"""

import sys
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.lexicon_manager import ShengLexiconManager
from src.normalizer import ShengNormalizerPipeline
from src.tokenizer import ShengCodeSwitchTokenizer

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.lexicon = ShengLexiconManager()
        self.pipeline = ShengNormalizerPipeline(self.lexicon)
        self.tokenizer = ShengCodeSwitchTokenizer(self.lexicon)

    def test_analyze_pipeline(self):
        text = "Niko mtaani na mayouth tukipiga luku safi."
        res = self.pipeline.process(text)
        self.assertIn("vijana", res.normalized_swahili)
        self.assertIn("youth", res.english_translation)
        self.assertGreater(res.token_efficiency["token_reduction_savings_pct"], 50.0)

    def test_add_word(self):
        new_word = {
            "sheng_term": "testterm254",
            "pos": "Noun",
            "standard_swahili": "neno la majaribio",
            "english": "test term",
            "category": "tech"
        }
        self.lexicon.add_entry(new_word, save=False)
        match = self.lexicon.lookup("testterm254")
        self.assertIsNotNone(match)
        self.assertEqual(match["standard_swahili"], "neno la majaribio")

if __name__ == "__main__":
    unittest.main()

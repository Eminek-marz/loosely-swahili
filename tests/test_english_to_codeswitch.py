"""
Unit tests for EnglishToKenyanCodeSwitcher & Bidirectional Code-Switching Pipeline
Verifies morphotactic loan passives, idiomatic predicates, discourse connectors,
and bidirectional pipeline execution.
"""

import unittest
from src.english_to_codeswitch import EnglishToKenyanCodeSwitcher
from src.normalizer import ShengNormalizerPipeline


class TestEnglishToKenyanCodeSwitcher(unittest.TestCase):

    def setUp(self):
        self.switcher = EnglishToKenyanCodeSwitcher()
        self.pipeline = ShengNormalizerPipeline()

    def test_rain_market_sentence(self):
        input_en = "Although the rain was pouring down heavily, the outdoor market was canceled."
        res = self.switcher.code_switch_sentence(input_en)
        self.assertIn("Hata kama", res.kenyan_codeswitch)
        self.assertIn("inanyesha heavy sana", res.kenyan_codeswitch)
        self.assertIn("market ya nje", res.kenyan_codeswitch)
        self.assertIn("ilicanceliwa", res.kenyan_codeswitch)

        self.assertIn("Ingawa", res.formal_swahili)
        self.assertIn("lilifutiliwa mbali", res.formal_swahili)

    def test_fired_delayed_sentence(self):
        input_en = "The boss fired the worker because the system was delayed."
        res = self.switcher.code_switch_sentence(input_en)
        self.assertIn("ilidelayiwa", res.kenyan_codeswitch)
        self.assertIn("coz", res.kenyan_codeswitch)

    def test_pipeline_bidirectional_detection(self):
        input_en = "Although the rain was pouring down heavily, the outdoor market was canceled."
        res = self.pipeline.process(input_en)
        self.assertTrue(res.is_english_input)
        self.assertEqual(res.code_switch_metrics["english"], 100.0)
        self.assertIn("ilicanceliwa", res.kenyan_codeswitch)
        self.assertIn("mvua", res.kenyan_codeswitch)
        self.assertIn("lilifutiliwa mbali", res.normalized_swahili)


if __name__ == "__main__":
    unittest.main()

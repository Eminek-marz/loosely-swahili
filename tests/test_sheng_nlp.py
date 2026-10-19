"""
Unit tests for Sheng-Sanifu NLP Toolkit
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.morphology import KenyanMorphologyEngine
from src.lexicon_manager import ShengLexiconManager
from src.tokenizer import ShengCodeSwitchTokenizer, StandardBPESimulator
from src.normalizer import ShengNormalizerPipeline

class TestShengNLP(unittest.TestCase):
    def setUp(self):
        self.morphology = KenyanMorphologyEngine()
        self.lexicon = ShengLexiconManager()
        self.tokenizer = ShengCodeSwitchTokenizer(self.lexicon)
        self.pipeline = ShengNormalizerPipeline(self.lexicon)

    def test_lexicon_loading(self):
        """Test that lexicon loads with entries."""
        terms = self.lexicon.get_all_terms()
        self.assertGreater(len(terms), 40)
        self.assertIn("mayouth", terms)
        self.assertIn("luku", terms)
        self.assertIn("rada", terms)

    def test_lexicon_lookup_and_variants(self):
        """Test exact and phonetic variant lookups."""
        entry = self.lexicon.lookup("chapaa")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["standard_swahili"], "pesa / fedha")

        # Test variant 'chapa'
        entry_var = self.lexicon.lookup("chapa")
        self.assertIsNotNone(entry_var)

        # Test idiom lookup
        entry_idiom = self.lexicon.lookup("kula fare")
        self.assertIsNotNone(entry_idiom)

    def test_morphological_hybrid_deconstruction(self):
        """Test intra-word code-switch deconstruction."""
        # 1. 'mayouth' -> ma- + youth
        res1 = self.morphology.deconstruct("mayouth")
        self.assertTrue(res1.is_hybrid)
        self.assertEqual(res1.prefix, "ma-")
        self.assertEqual(res1.stem, "youth")
        self.assertEqual(res1.swahili_normalized_stem, "vijana")

        # 2. 'kucome' -> ku- + come
        res2 = self.morphology.deconstruct("kucome")
        self.assertTrue(res2.is_hybrid)
        self.assertEqual(res2.prefix, "ku-")
        self.assertEqual(res2.stem, "come")

        # 3. 'unaniconfuse' -> u-na-ni- + confuse
        res3 = self.morphology.deconstruct("unaniconfuse")
        self.assertTrue(res3.is_hybrid)
        self.assertEqual(res3.stem, "confuse")
        self.assertIn("u-na-ni-", res3.prefix)

        # 4. 'alitughost' -> a-li-tu- + ghost
        res4 = self.morphology.deconstruct("alitughost")
        self.assertTrue(res4.is_hybrid)
        self.assertEqual(res4.stem, "ghost")

    def test_tokenizer_efficiency(self):
        """Test that Sheng-aware tokenizer prevents shattering and compresses token count."""
        test_sentence = "Niko mtaani na mayouth tukipiga luku safi."
        comp = self.tokenizer.compare_efficiency(test_sentence)
        
        self.assertGreater(comp["standard_bpe_count"], comp["sheng_aware_count"])
        self.assertGreater(comp["token_reduction_savings_pct"], 20.0)
        print(f"\n[Tokenizer Comparison] Sentence: '{test_sentence}'")
        print(f"Standard BPE ({comp['standard_bpe_count']} tokens): {comp['standard_bpe_tokens']}")
        print(f"Sheng-Aware  ({comp['sheng_aware_count']} tokens): {comp['sheng_aware_tokens']}")
        print(f"Token Savings: {comp['token_reduction_savings_pct']}%")

    def test_full_pipeline_normalization(self):
        """Test end-to-end normalization of Kenyan code-switched sentences."""
        test_sentences = [
            "Niko mtaani na mayouth.",
            "Bro unaniconfuse, hiyo form ilichoma kitambo.",
            "Kuja tao uchukue nduthi, niko na chapaa ya fare."
        ]

        for s in test_sentences:
            res = self.pipeline.process(s)
            self.assertIsNotNone(res.normalized_swahili)
            self.assertIsNotNone(res.english_translation)
            self.assertGreater(len(res.tokens), 0)
            print(f"\n[Pipeline] Input: '{s}'")
            print(f" -> Formal Swahili: {res.normalized_swahili}")
            print(f" -> English:        {res.english_translation}")
            print(f" -> Code-Switching: {res.code_switch_metrics}")

    def test_loanverb_derivation_and_vowel_elision(self):
        """Test English loan verbs with Bantu verbal extensions and silent 'e' vowel elision."""
        # 1. 'alifiriwa' -> fire + -iwa (silent 'e' elided)
        res1 = self.morphology.deconstruct("alifiriwa")
        self.assertTrue(res1.is_hybrid)
        self.assertEqual(res1.stem, "fire")
        self.assertEqual(res1.suffix, "-iwa")
        self.assertEqual(res1.swahili_normalized_stem, "alifutwa kazi")
        self.assertEqual(res1.english_translation, "he/she was fired from work")

        # 2. 'alifireiwa' -> spelling preservation + -iwa
        res2 = self.morphology.deconstruct("alifireiwa")
        self.assertTrue(res2.is_hybrid)
        self.assertEqual(res2.stem, "fire")
        self.assertEqual(res2.suffix, "-iwa")

        # 3. 'amecaniwa' -> cane + -iwa (silent 'e' elided)
        res3 = self.morphology.deconstruct("amecaniwa")
        self.assertTrue(res3.is_hybrid)
        self.assertEqual(res3.stem, "cane")
        self.assertEqual(res3.suffix, "-iwa")
        self.assertEqual(res3.swahili_normalized_stem, "amepigwa kwa bakora")
        self.assertEqual(res3.english_translation, "he/she has been caned")

        # 4. 'alimfire' -> active transitive with object infix -m-
        res4 = self.morphology.deconstruct("alimfire")
        self.assertTrue(res4.is_hybrid)
        self.assertEqual(res4.stem, "fire")
        self.assertEqual(res4.swahili_normalized_stem, "alimfuta kazi")
        self.assertEqual(res4.english_translation, "he/she fired him/her")

    def test_minyambuliko_ya_shika(self):
        """Test Swahili and Sheng verbal extensions for 'shika' (kutenda, kutendea, kutendesha)."""
        # 1. Kutenda (Inchoative / Kick in): 'Hiyo jaba imeanza kushika fiti'
        res1 = self.pipeline.process("Hiyo jaba imeanza kushika fiti.")
        self.assertIn("kick in", res1.english_translation.lower())
        print(f"\n[Minyambuliko 1 - Kutenda]: {res1.original_text} -> {res1.english_translation}")

        # 2. Kutendea (Applicative / Buy for someone): 'Utanishikia pombe?'
        res2 = self.pipeline.process("Utanishikia pombe?")
        self.assertIn("buy", res2.english_translation.lower())
        self.assertIn("alcohol", res2.english_translation.lower())
        print(f"[Minyambuliko 2 - Kutendea]: {res2.original_text} -> {res2.english_translation}")

        # 3. Kutendesha (Causative / Pass fire): 'Nishikishe kiberiti niwashe fegi.'
        res3 = self.pipeline.process("Nishikishe kiberiti niwashe fegi.")
        self.assertIn("matchbox", res3.english_translation.lower())
        print(f"[Minyambuliko 3 - Kutendesha]: {res3.original_text} -> {res3.english_translation}")

    def test_zero_mixed_words_kamusi_engine(self):
        """Test that Swahili sentences are translated into 100% pure fluent English with zero mixed words."""
        test_sent = "Dereva wa matatu alipongezwa sana kwa sababu ya kusaidia abiria."
        res = self.pipeline.process(test_sent)
        
        # Verify no Swahili grammatical conjunctions or verbs remained in English string
        self.assertNotIn("kwa sababu", res.english_translation)
        self.assertNotIn("alipongezwa", res.english_translation)
        self.assertNotIn("kusaidia", res.english_translation)
        self.assertIn("praised", res.english_translation.lower())
        print(f"\n[Pure Translation]: {test_sent}")
        print(f" -> Formal Sanifu: {res.normalized_swahili}")
        print(f" -> Pure English:  {res.english_translation}")

if __name__ == "__main__":
    unittest.main()

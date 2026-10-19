"""
Tests for Google Scholar Academic Paper Ingestion, Translation, & Model Training
Validates that academic research papers (Einstein 1905, Vaswani 2017, etc.)
are translated into authentic Kenyan Loosely Swahili using local morphotactics
without any external API dependencies, and that the K-CSLM model trains on them.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.scholar_paper_trainer import ScholarPaperTrainer, SEMINAL_PAPERS_LIBRARY
from src.concept_recreation_engine import ConceptRecreationEngine
from src.kenyan_lm_engine import KenyanCodeSwitchLM
from src.bpe_streaming_trainer import ShengStreamingBPETrainer

class TestScholarPaperTrainer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.trainer = ScholarPaperTrainer()
        cls.concept_engine = ConceptRecreationEngine()
        cls.cslm = KenyanCodeSwitchLM()
        cls.bpe = ShengStreamingBPETrainer(target_vocab_size=6000)

    def test_einstein_1905_all_sections_translation(self):
        """Validates that Einstein's 1905 paper sections translate into authentic Kenyan Loosely Swahili."""
        einstein_paper = SEMINAL_PAPERS_LIBRARY[0]
        self.assertEqual(einstein_paper["year"], 1905)
        
        translated = self.trainer.translate_entire_paper(einstein_paper)
        self.assertEqual(len(translated["translated_sections"]), 6)
        
        # Section 1: Title
        sec1 = translated["translated_sections"][0]
        self.assertIn("Kuhusu Heuristic Point of View", sec1["loosely_swahili"])
        self.assertIn("kuhusu Emission na Transformation ya Light", sec1["loosely_swahili"])
        
        # Section 2: Theoretical Discrepancy
        sec2 = translated["translated_sections"][1]
        self.assertIn("Kuna profound distinction rasmi", sec2["loosely_swahili"])
        self.assertIn("zenye maphysicist wame-form", sec2["loosely_swahili"])
        self.assertNotIn("zinaphysicist", sec2["loosely_swahili"])  # Must not have broken agglutination
        
        # Section 3: Atomic State vs Continuous Wave
        sec3 = translated["translated_sections"][2]
        self.assertIn("Wakati tuna-consider state ya body kuwa completely determined", sec3["loosely_swahili"])
        self.assertIn("ma-atom na ma-electron", sec3["loosely_swahili"])
        self.assertIn("sisi hu-use continuous spatial functions ku-describe", sec3["loosely_swahili"])
        
        # Section 4: Quanta Hypothesis
        sec4 = translated["translated_sections"][3]
        self.assertIn("Kulingana na assumption yenye tuna-consider hapa", sec4["loosely_swahili"])
        self.assertIn("energy haiko continuously distributed", sec4["loosely_swahili"])
        self.assertIn("energy quanta zenye ziko localized", sec4["loosely_swahili"])
        self.assertIn("zina-move bila ku-divide", sec4["loosely_swahili"])
        
        # Section 5: Photoelectric Effect
        sec5 = translated["translated_sections"][4]
        self.assertIn("Simplest conception ni kuwa light quantum moja hu-transfer energy yake yote", sec5["loosely_swahili"])
        self.assertIn("kila electron yenye ime-ejectiwa iko completely independent", sec5["loosely_swahili"])
        self.assertIn("ina-depend tu kwa frequency", sec5["loosely_swahili"])
        
        # Section 6: Synthesis
        sec6 = translated["translated_sections"][5]
        self.assertIn("in the 1905", sec6["loosely_swahili"])
        self.assertIn("ilichallenge classical wave theory", sec6["loosely_swahili"])
        self.assertIn("kwa ku-propose kuwa light iko spatially localized", sec6["loosely_swahili"])
        self.assertIn("discrete packages za energy", sec6["loosely_swahili"])
        self.assertIn("ikaintroduce core concept enye ili-lay", sec6["loosely_swahili"])

    def test_transformer_attention_paper_translation(self):
        """Validates that Vaswani 2017 Transformer paper translates naturally."""
        transformer_paper = SEMINAL_PAPERS_LIBRARY[2]
        self.assertEqual(transformer_paper["year"], 2017)
        translated = self.trainer.translate_entire_paper(transformer_paper)
        
        sec_proposal = translated["translated_sections"][2]
        self.assertIn("Tuna-propose network architecture mpya na simple", sec_proposal["loosely_swahili"])
        self.assertIn("Transformer", sec_proposal["loosely_swahili"])
        self.assertIn("bila ku-use recurrence na convolutions kabisa", sec_proposal["loosely_swahili"])

    def test_cslm_training_on_academic_sentences(self):
        """Verifies that the Kenyan Code-Switching LM learns academic transitions and reduces perplexity."""
        test_sentence = (
            "Kuhusu Heuristic Point of View kuhusu Emission na Transformation ya Light: "
            "Foundational physics research paper yenye ilipublishiwa na Albert Einstein in the 1905, "
            "hii groundbreaking Annalen der Physik article ilichallenge classical wave theory kwa ku-propose kuwa "
            "light iko spatially localized na inatransmitiwa kwa discrete packages za energy."
        )
        pre_score = self.cslm.score_sentence_perplexity(test_sentence)
        pre_ppl = pre_score["perplexity"]
        
        # Train on the sentence
        for _ in range(3):
            self.cslm.update_from_sentence(test_sentence)
            
        post_score = self.cslm.score_sentence_perplexity(test_sentence)
        post_ppl = post_score["perplexity"]
        
        self.assertLess(post_ppl, pre_ppl)
        self.assertGreater(pre_ppl - post_ppl, 50.0)

    def test_morpheme_aware_tokenizer_on_academic_loan_verbs(self):
        """Verifies that scientific loan verbs preserve their Bantu prefixes without shattering."""
        tokens = self.bpe.pre_tokenize_word_morpheme_aware("ilichallenge")
        # Bantu prefix 'ili@@' should be kept intact
        self.assertEqual(tokens[0], "ili@@")
        
        tokens_trans = self.bpe.pre_tokenize_word_morpheme_aware("inatransmit")
        self.assertEqual(tokens_trans[0], "ina@@")

if __name__ == "__main__":
    unittest.main()

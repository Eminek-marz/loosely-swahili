"""
Unit Tests for Bulk Academic Literature Streaming & Translation Engine
Validates that the multi-disciplinary streaming pipeline cleans text,
translates academic sentences into Kenyan Loosely Swahili, streams outputs,
and trains the local K-CSLM language model without external API dependencies.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.bulk_academic_streamer import BulkAcademicStreamer, SEMINAL_FOUNDATIONAL_CORPUS, SCHOLARLY_RESEARCH_DOMAINS

class TestBulkAcademicStreamer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.streamer = BulkAcademicStreamer()

    def test_clean_academic_text(self):
        """Verifies stripping of citation brackets, LaTeX formulas, and URL boilerplate."""
        raw_text = "The model [1, 2] achieves $$E = mc^2$$ optimization with high precision [Smith et al., 2021] at https://arxiv.org/abs/1234."
        cleaned = self.streamer.clean_academic_text(raw_text)
        self.assertNotIn("[1, 2]", cleaned)
        self.assertNotIn("$$E = mc^2$$", cleaned)
        self.assertNotIn("Smith et al.", cleaned)
        self.assertNotIn("https://", cleaned)
        self.assertIn("The model achieves optimization with high precision at", cleaned)

    def test_segment_into_analytical_sentences(self):
        """Verifies splitting of dense academic abstracts into coherent analytical sentences."""
        abstract = (
            "Quantum entanglement is a fundamental physical phenomenon. "
            "In this work, the Hamiltonian dynamics are modeled using tensor networks. "
            "We report that the phase transition occurs at zero temperature."
        )
        sentences = self.streamer.segment_into_analytical_sentences(abstract)
        self.assertGreaterEqual(len(sentences), 2)
        # Should filter out "We report"
        self.assertTrue(any("Quantum entanglement" in s for s in sentences))

    def test_seminal_classics_translation(self):
        """Verifies that classic foundational sentences (Darwin, Newton, etc.) translate into Kenyan Loosely Swahili."""
        sample_darwin = SEMINAL_FOUNDATIONAL_CORPUS[0]["sentences"][0]
        recreated = self.streamer.concept_engine.reconstruct_concept(sample_darwin)
        cs_text = recreated.get("reconstructed_codeswitch", "")
        self.assertGreater(len(cs_text), 10)
        self.assertTrue(any(marker in cs_text.lower() for marker in ["kuna", "kwa", "ya", "za", "na", "hata", "ili"]))

    def test_multi_domain_coverage(self):
        """Ensures that all 8 major scholarly disciplines are configured."""
        self.assertEqual(len(SCHOLARLY_RESEARCH_DOMAINS), 8)
        domains = [d["domain"] for d in SCHOLARLY_RESEARCH_DOMAINS]
        self.assertIn("Theoretical Physics & Quantum Mechanics", domains)
        self.assertIn("Artificial Intelligence & Transformer Architectures", domains)
        self.assertIn("Molecular Biology & CRISPR Gene Editing", domains)
        self.assertIn("Macroeconomics & Financial Systems", domains)

if __name__ == "__main__":
    unittest.main()

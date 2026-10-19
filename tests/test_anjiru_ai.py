"""
Unit test suite for Anjiru.AI engine and dual-track generation.
Validates zero-shot generation across both Way 1 (Academic Standard) and Way 2 (Colloquial Sheng).
"""

import unittest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.anjiru_engine import get_anjiru_engine


class TestAnjiruAI(unittest.TestCase):
    def setUp(self):
        self.engine = get_anjiru_engine()

    def test_cgmm_genomics_dual_track(self):
        prompt = "Our results show that CGMM outperforms four current state-of-the-art genomics generators on two different tasks."
        resp = self.engine.generate(prompt, mode="both")

        self.assertIn("Results zetu zinashow kuwa CGMM outperforms four state-of-the-art genomics generators ya sasa kwa tasks mbili tofauti.", resp.way1_academic)
        self.assertIn("Maresults zetu show kuwa CGMM outperforms four state-of-the-art genomics generators ya sasa kwa matasks mbili tofauti.", resp.way2_sheng)
        self.assertEqual(resp.domain, "Genomics & Molecular Biology")
        self.assertTrue(resp.latency_ms > 0)

    def test_quantum_entanglement_dual_track(self):
        prompt = "Entanglement and state distinguishability have long been central topics in quantum foundations. While each has developed into a rich subject in its own right, they can be connected through measurements in complementary bases."
        resp = self.engine.generate(prompt, mode="both")

        self.assertIn("Entanglement na state distinguishability zime-kuwa kwa muda mrefu kama central topics kwenye quantum foundations.", resp.way1_academic)
        self.assertIn("Entanglement na state distinguishability zime-kuwa kwa muda mrefu central topics kwenye quantum foundations.", resp.way2_sheng)
        self.assertEqual(resp.domain, "Quantum Mechanics & Foundations")

    def test_rlx_compiler_dual_track(self):
        prompt = "Production machine learning (ML) stacks often split graph compilation and kernel execution across different layers and languages, making backend behavior, deployment guarantees, and performance fallbacks hard to reason about end-to-end."
        resp = self.engine.generate(prompt, mode="both")

        self.assertIn("kwa layers tofauti na languages", resp.way1_academic)
        self.assertIn("kwa malayers tofauti na languages", resp.way2_sheng)
        self.assertEqual(resp.domain, "Distributed Systems & Compilers")

    def test_mckean_vlasov_locative_guard(self):
        prompt = "The scheme follows the single-ensemble paradigm, where particles interact across levels at each timestep."
        resp = self.engine.generate(prompt, mode="both")

        self.assertIn("katika levels at each timestep", resp.way1_academic)
        self.assertIn("kwa levels at each timestep", resp.way2_sheng)

    def test_molecular_dna_watson_crick(self):
        prompt = "This structure has novel features which are of considerable biological interest."
        resp = self.engine.generate(prompt, mode="both")

        self.assertIn("Hii structure has features mpya zenye ziko na considerable biological interest.", resp.way1_academic)
        self.assertIn("Hii structure has mafeatures mpya zenye ziko na considerable biological interest.", resp.way2_sheng)

    def test_telescopic_lm_compute_budgets(self):
        prompt = "One deployed language model must often serve many compute budgets, yet serving each budget still means a separate training or compression run per point."
        resp = self.engine.generate(prompt, mode="both")

        self.assertIn("compute budgets nyingi", resp.way1_academic)
        self.assertIn("compute nyingi budgets", resp.way2_sheng)


if __name__ == "__main__":
    unittest.main()

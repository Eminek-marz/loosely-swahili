"""
Unit Tests for the Official 125 Rules Specification of Loosely Swahili NLP.
Verifies registry population, category partitioning, rule retrieval, formula consistency,
and compliance auditing.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import src as ls
from src.loosely_swahili_engine import get_125_rules_registry, LooselySwahili125RulesRegistry


class Test125RulesSpecification(unittest.TestCase):

    def setUp(self):
        self.registry = get_125_rules_registry()

    def test_total_rule_count(self):
        """Verify that exactly 125 rules are codified."""
        self.assertEqual(len(self.registry.rules), 125)

    def test_all_categories_populated(self):
        """Verify that all 7 categories contain their designated rules."""
        cat1 = self.registry.get_rules_by_category("CAT_I")
        self.assertEqual(len(cat1), 25)

        cat2 = self.registry.get_rules_by_category("CAT_II")
        self.assertEqual(len(cat2), 20)

        cat3 = self.registry.get_rules_by_category("CAT_III")
        self.assertEqual(len(cat3), 20)

        cat4 = self.registry.get_rules_by_category("CAT_IV")
        self.assertEqual(len(cat4), 20)

        cat5 = self.registry.get_rules_by_category("CAT_V")
        self.assertEqual(len(cat5), 15)

        cat6 = self.registry.get_rules_by_category("CAT_VI")
        self.assertEqual(len(cat6), 15)

        cat7 = self.registry.get_rules_by_category("CAT_VII")
        self.assertEqual(len(cat7), 10)

        total_categorized = len(cat1) + len(cat2) + len(cat3) + len(cat4) + len(cat5) + len(cat6) + len(cat7)
        self.assertEqual(total_categorized, 125)

    def test_key_pillar_rules(self):
        """Verify specific crucial invariant rules."""
        # Rule 1: Bare Root Invariant
        r1 = self.registry.get_rule(1)
        self.assertIsNotNone(r1)
        self.assertEqual(r1.title, "The Bare Root Invariant")
        self.assertIn("alikuwa amepick", r1.example_valid)

        # Rule 10: Periphrastic Reciprocal (pamoja)
        r10 = self.registry.get_rule(10)
        self.assertIsNotNone(r10)
        self.assertIn("pamoja", r10.formula)

        # Rule 27: English -s double stack
        r27 = self.registry.get_rule(27)
        self.assertIsNotNone(r27)
        self.assertIn("maphones", r27.example_valid)

        # Rule 28: Food Plural Economy Constraint (chapos)
        r28 = self.registry.get_rule(28)
        self.assertIsNotNone(r28)
        self.assertIn("chapos", r28.example_valid)

        # Rule 66: Zero Preposition Locative
        r66 = self.registry.get_rule(66)
        self.assertIsNotNone(r66)
        self.assertIn("niko job", r66.example_valid)

        # Rule 125: Poplack-Bantu Boundary Invariant
        r125 = self.registry.get_rule(125)
        self.assertIsNotNone(r125)
        self.assertEqual(r125.title, "The Poplack-Bantu Boundary Invariant")

    def test_search_rules(self):
        """Verify rule keyword query capability."""
        results = self.registry.search_rules("bare root")
        self.assertTrue(any(r.id == 1 for r in results))

        results_mpesa = self.registry.search_rules("fuliza")
        self.assertTrue(any(r.id == 105 for r in results_mpesa))

    def test_sentence_audit_125(self):
        """Verify auditing sentence against 125 rules catalog."""
        sentence = "Enyewe manze niko job na maservers zote zimecrash, inabidi turesolve bana."
        audit = self.registry.audit_sentence_125(sentence)
        self.assertEqual(audit["rules_checked"], 125)
        matched_ids = [m["rule_id"] for m in audit["matched_rules"]]

        # Should match Rules 27 (maservers), 66 (niko job), 116 (bana), 117 (enyewe), 118 (manze), 121 (inabidi)
        self.assertIn(27, matched_ids)
        self.assertIn(66, matched_ids)
        self.assertIn(116, matched_ids)
        self.assertIn(117, matched_ids)
        self.assertIn(118, matched_ids)
        self.assertIn(121, matched_ids)

    def test_top_level_package_api(self):
        """Verify that loosely_swahili exports 125 rule methods directly."""
        self.assertEqual(ls.__version__, "0.3.0")
        r = ls.get_125_rule(1)
        self.assertEqual(r.id, 1)

        audit = ls.audit_125_rules("Niko job.")
        self.assertIn(66, [m["rule_id"] for m in audit["matched_rules"]])


if __name__ == "__main__":
    unittest.main()

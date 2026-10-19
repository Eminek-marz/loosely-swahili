"""
Unit Test Suite for Bantu-English Verbal Fusion Engine
Validates the dynamic morphotactic matrix for treating English loan verbs as Swahili vitenzi across:
1. WHO  (Nafsi subjects & object infixes)
2. WHEN (Nyakati tenses, aspects & polarity)
3. WHERE(Locatives & manner relatives -po-, -ko-, -mo-, -vyo-)
4. HOW  (Minyambuliko ya vitenzi - Kutenda, Kutendwa, Kutendea, Kutendesha, Kutendana, Kutendeka)
And ensures synchronization across Set A (Sanifu), Set B (English), and Set C (Kenyan Sheng).
"""

import unittest
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.fusion_engine import BantuEnglishFusionEngine

class TestBantuEnglishFusionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = BantuEnglishFusionEngine()

    def test_who_subjects_and_objects(self):
        """Test Nafsi (WHO) inflection: 1s, 2s, 3s, 1p, 2p, 3p and object infixes."""
        # 1s (Mimi): I will text
        res_1s = self.engine.fuse("text", who_subj="1s", when_tense="future")
        self.assertEqual(res_1s.fused_verb, "nitatext")
        self.assertEqual(res_1s.who_subject["pfx"], "ni")
        self.assertIn("nita", res_1s.formal_swahili)

        # 2s (Wewe): You are calling
        res_2s = self.engine.fuse("call", who_subj="2s", when_tense="present")
        self.assertEqual(res_2s.fused_verb, "unacall")
        self.assertEqual(res_2s.who_subject["pfx"], "u")

        # 1p (Sisi): We booked
        res_1p = self.engine.fuse("book", who_subj="1p", when_tense="past")
        self.assertEqual(res_1p.fused_verb, "tulibook")

        # 3p (Wao) + Object 1s (-ni-): They are confusing me
        res_obj = self.engine.fuse("confuse", who_subj="3p", who_obj="me", when_tense="present")
        self.assertEqual(res_obj.fused_verb, "wananiconfuse")
        self.assertIn("they", res_obj.pure_english.lower())
        self.assertIn("me", res_obj.pure_english.lower())

        # 3p (Wao) + Object 1p (-tu-): They booked for us
        res_appl_obj = self.engine.fuse("book", who_subj="3p", who_obj="us", when_tense="past", how_ext="kutendea")
        self.assertEqual(res_appl_obj.fused_verb, "walitubookia")
        self.assertIn("booked for us", res_appl_obj.pure_english.lower())

    def test_when_tenses_and_polarity(self):
        """Test Nyakati (WHEN) inflection: Past, Present, Future, Perfect, Conditional."""
        # Past (-li-)
        res_past = self.engine.fuse("work", who_subj="3s", when_tense="past")
        self.assertEqual(res_past.fused_verb, "aliwork")
        self.assertIn("worked", res_past.pure_english)

        # Present (-na-)
        res_pres = self.engine.fuse("work", who_subj="3s", when_tense="present")
        self.assertEqual(res_pres.fused_verb, "anawork")
        self.assertIn("working", res_pres.pure_english)

        # Future (-ta-)
        res_fut = self.engine.fuse("chill", who_subj="1p", when_tense="future")
        self.assertEqual(res_fut.fused_verb, "tutachill")
        self.assertIn("will chill", res_fut.pure_english)

        # Perfect (-me-)
        res_perf = self.engine.fuse("post", who_subj="1s", when_tense="perfect")
        self.assertEqual(res_perf.fused_verb, "nimepost")
        self.assertIn("have posted", res_perf.pure_english)

        # Conditional (-ki-)
        res_cond = self.engine.fuse("agree", who_subj="1p", when_tense="conditional")
        self.assertEqual(res_cond.fused_verb, "tukiagree")

    def test_where_locatives_and_manner(self):
        """Test Mahali/Vishazi (WHERE) markers: -po-, -ko-, -mo-, -vyo-."""
        # -po- (where / when at)
        res_po = self.engine.fuse("work", who_subj="3s", when_tense="present", where_loc="where_at")
        self.assertEqual(res_po.fused_verb, "anapowork")
        self.assertIn("where", res_po.where_locative["label"].lower())

        # -vyo- (how / manner)
        res_vyo = self.engine.fuse("feel", who_subj="1p", when_tense="present", where_loc="manner")
        self.assertEqual(res_vyo.fused_verb, "tunavyofeel")
        self.assertIn("manner", res_vyo.where_locative["label"].lower())

    def test_how_minyambuliko_verbal_extensions(self):
        """
        Test Kauli za Vitenzi (HOW) per rule:
        - If verb ends with a vowel: drop final vowel and use e-extensions (-ewa, -ea, -esha, -eka, -eana)
        - If verb ends with a consonant: use i-extensions (-iwa, -ia, -isha, -ika, -ana)
        """
        # Kutendwa (Passive): fire (vowel) -> fir + iwa = alifiriwa
        res_pass = self.engine.fuse("fire", who_subj="3s", when_tense="past", how_ext="kutendwa")
        self.assertEqual(res_pass.fused_verb, "alifiriwa")
        self.assertIn("was fired", res_pass.pure_english.lower())
        self.assertIn("kazi", res_pass.formal_swahili.lower())

        # Kutendwa: cane (vowel) -> can + iwa = alicaniwa
        res_cane = self.engine.fuse("cane", who_subj="3s", when_tense="past", how_ext="kutendwa")
        self.assertEqual(res_cane.fused_verb, "alicaniwa")

        # Kutendea (Applicative): text (consonant) -> text + ia = walitutextia
        res_appl = self.engine.fuse("text", who_subj="3p", who_obj="us", when_tense="past", how_ext="kutendea")
        self.assertEqual(res_appl.fused_verb, "walitutextia")
        self.assertIn("texted for us", res_appl.pure_english.lower())

        # Kutendea (Applicative): book (consonant) -> book + ia = walitubookia
        res_book = self.engine.fuse("book", who_subj="3p", who_obj="us", when_tense="past", how_ext="kutendea")
        self.assertEqual(res_book.fused_verb, "walitubookia")

        # Kutendana (Reciprocal / Mutual): vibe -> tulivibe pamoja
        res_recip = self.engine.fuse("vibe", who_subj="1p", when_tense="past", how_ext="kutendana")
        self.assertEqual(res_recip.fused_verb, "tulivibe pamoja")
        self.assertIn("together", res_recip.pure_english.lower())

        # Kutendana (Reciprocal / Mutual): date -> wanadate pamoja
        res_date = self.engine.fuse("date", who_subj="3p", when_tense="present", how_ext="kutendana")
        self.assertEqual(res_date.fused_verb, "wanadate pamoja")

        # Kutendeka (Stative): solve (vowel) -> solv + ika = inasolvika
        res_stat = self.engine.fuse("solve", who_subj="c9", when_tense="present", how_ext="kutendeka")
        self.assertEqual(res_stat.fused_verb, "inasolvika")
        self.assertIn("can be solved", res_stat.pure_english.lower())

        # Kutendesha (Causative): sign (consonant) -> sign + isha = anamsignisha
        res_caus = self.engine.fuse("sign", who_subj="3s", who_obj="him_her", when_tense="present", how_ext="kutendesha")
        self.assertEqual(res_caus.fused_verb, "anamsignisha")

    def test_deconstruction_of_kenyan_fused_verbs(self):
        """Test Reverse Analysis: Deconstructing real Kenyan surface forms into grammatical components."""
        # 1. 'walitubookia' -> book, 3p, past, us, kutendea
        dec_1 = self.engine.deconstruct_fused_verb("walitubookia")
        self.assertTrue(dec_1.is_fused_verb)
        self.assertEqual(dec_1.english_verb_root, "book")
        self.assertIn("us", dec_1.who.lower())
        self.assertIn("past", dec_1.when.lower())
        self.assertIn("kutendea", dec_1.how.lower())
        self.assertIn("booked for us", dec_1.pure_english_translation.lower())

        # 2. 'alifiriwa' -> fire, 3s, past, kutendwa
        dec_2 = self.engine.deconstruct_fused_verb("alifiriwa")
        self.assertTrue(dec_2.is_fused_verb)
        self.assertEqual(dec_2.english_verb_root, "fire")
        self.assertIn("kutendwa", dec_2.how.lower())
        self.assertIn("was fired", dec_2.pure_english_translation.lower())

        # 3. 'unaniconfuse' -> confuse, 2s, present, me, kutenda
        dec_3 = self.engine.deconstruct_fused_verb("unaniconfuse")
        self.assertTrue(dec_3.is_fused_verb)
        self.assertEqual(dec_3.english_verb_root, "confuse")
        self.assertIn("present", dec_3.when.lower())
        self.assertIn("me", dec_3.who.lower())
        self.assertIn("confusing me", dec_3.pure_english_translation.lower())

        # 4. 'inasolvika' -> solve, c9, present, kutendeka
        dec_4 = self.engine.deconstruct_fused_verb("inasolvika")
        self.assertTrue(dec_4.is_fused_verb)
        self.assertEqual(dec_4.english_verb_root, "solve")
        self.assertIn("kutendeka", dec_4.how.lower())
        self.assertIn("can be solved", dec_4.pure_english_translation.lower())

        # 5. 'tulivibiana' -> vibe, 1p, past, kutendana
        dec_5 = self.engine.deconstruct_fused_verb("tulivibiana")
        self.assertTrue(dec_5.is_fused_verb)
        self.assertEqual(dec_5.english_verb_root, "vibe")
        self.assertIn("kutendana", dec_5.how.lower())

        # 6. 'wanadatiana' -> date, 3p, present, kutendana
        dec_6 = self.engine.deconstruct_fused_verb("wanadatiana")
        self.assertTrue(dec_6.is_fused_verb)
        self.assertEqual(dec_6.english_verb_root, "date")
        self.assertIn("kutendana", dec_6.how.lower())

        # 7. 'tutashareriwa' -> share, 1p, future, kutendwa
        dec_7 = self.engine.deconstruct_fused_verb("tutashareriwa")
        self.assertTrue(dec_7.is_fused_verb)
        self.assertEqual(dec_7.english_verb_root, "share")
        self.assertIn("kutendwa", dec_7.how.lower())

        # 8. 'wanashareana' -> share, 3p, present, kutendana
        dec_8 = self.engine.deconstruct_fused_verb("wanashareana")
        self.assertTrue(dec_8.is_fused_verb)
        self.assertEqual(dec_8.english_verb_root, "share")
        self.assertIn("kutendana", dec_8.how.lower())

        # 9. 'tulivibe pamoja' -> vibe, 1p, past, kutendana
        dec_9 = self.engine.deconstruct_fused_verb("tulivibe pamoja")
        self.assertTrue(dec_9.is_fused_verb)
        self.assertEqual(dec_9.english_verb_root, "vibe")
        self.assertIn("kutendana", dec_9.how.lower())

        # 10. Non-fused regular word should return False
        dec_none = self.engine.deconstruct_fused_verb("chakula")
        self.assertFalse(dec_none.is_fused_verb)

    def test_share_syllabic_and_euphonic_rules(self):
        """Test r-diphthong loan verbs (share): anashare, wanashare pamoja, tutashareriwa."""
        # 1. Active: anashare
        res_act = self.engine.fuse("share", who_subj="3s", when_tense="present", how_ext="kutenda")
        self.assertEqual(res_act.fused_verb, "anashare")

        # 2. Reciprocal (pamoja): wanashare pamoja
        res_recip = self.engine.fuse("share", who_subj="3p", when_tense="present", how_ext="kutendana")
        self.assertEqual(res_recip.fused_verb, "wanashare pamoja")

        # 3. Passive (Euphonic 'r' epenthesis): tutashareriwa
        res_pass = self.engine.fuse("share", who_subj="1p", when_tense="future", how_ext="kutendwa")
        self.assertEqual(res_pass.fused_verb, "tutashareriwa")

    def test_transitivity_and_semantic_restrictions(self):
        """Test that intransitive verbs (e.g. chill) use 'pamoja' for mutual actions and disallow passive."""
        # Reciprocal with pamoja is fully natural and valid:
        res_chill = self.engine.fuse("chill", who_subj="1p", when_tense="present", how_ext="kutendana")
        self.assertTrue(res_chill.is_valid)
        self.assertEqual(res_chill.fused_verb, "tunachill pamoja")

        # Passive on intransitive verb is flagged as unnatural:
        res_pass = self.engine.fuse("chill", who_subj="3s", when_tense="past", how_ext="kutendwa")
        self.assertFalse(res_pass.is_valid)
        self.assertIn("passive", res_pass.semantic_warning.lower())

    def test_tri_set_synchronization(self):
        """Test that Set A (Sanifu), Set B (English), and Set C (Kenyan Sheng) are strictly coherent."""
        sample_verbs = ["work", "text", "fire", "post", "support", "chill"]
        for v in sample_verbs:
            res = self.engine.fuse(v, who_subj="1p", when_tense="future")
            # Set C
            self.assertTrue(res.fused_verb.startswith("tuta"))
            # Set A
            self.assertTrue(len(res.formal_swahili) > 0)
            self.assertIn("sisi", res.formal_swahili.lower())
            # Set B
            self.assertTrue(len(res.pure_english) > 0)
            self.assertIn("we will", res.pure_english.lower())
            # Morphemes
            self.assertTrue(len(res.morpheme_chain) >= 3)

if __name__ == "__main__":
    unittest.main()

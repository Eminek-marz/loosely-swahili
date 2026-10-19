"""
Unit Tests for the Official Master Blueprint for East African Hybrid Grammar (Sheng / Engsh)
Validates all 9 sections including morphosyntax, noun classes, food plural constraints,
prepositions, clock rules, currency value matrix, status/distress, and dialogue script.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.loosely_swahili_engine import (
    LooselySwahiliValidator,
    MorphosyntacticEngine,
    NounClassEngine,
    MannerModifierEngine,
    PossessiveEngine,
    PrepositionEngine,
    TimeCertaintyEngine,
    FinancialElectronicsEngine,
    ConversationalDistressEngine,
    MetathesisEngine,
    MetathesisEntry,
    MetathesisAnalysis
)
from src.morphology import KenyanMorphologyEngine

class TestLooselySwahiliMasterBlueprint(unittest.TestCase):
    def setUp(self):
        self.validator = LooselySwahiliValidator()
        self.morpho = MorphosyntacticEngine()
        self.nouns = NounClassEngine()
        self.manner = MannerModifierEngine()
        self.possessives = PossessiveEngine()
        self.prepositions = PrepositionEngine()
        self.time = TimeCertaintyEngine()
        self.financial = FinancialElectronicsEngine()
        self.conversational = ConversationalDistressEngine()
        self.metathesis = MetathesisEngine()
        self.morph_deconstructor = KenyanMorphologyEngine()

    # --------------------------------------------------------------------------
    # SECTION I: THE MORPHOSYNTACTIC ENGINE
    # --------------------------------------------------------------------------
    def test_bare_root_constraint(self):
        """Enforce pure infinitive base: Alikuwa amepick / Nimeshock. Reject -ed: amepicked, nimeshocked."""
        res_good1 = self.morpho.analyze_verb("amepick")
        self.assertTrue(res_good1.is_valid_plug_in)
        self.assertFalse(res_good1.has_double_conjugation_error)

        res_bad1 = self.morpho.analyze_verb("amepicked")
        self.assertFalse(res_bad1.is_valid_plug_in)
        self.assertTrue(res_bad1.has_double_conjugation_error)

        res_good2 = self.morpho.analyze_verb("nimeshock")
        self.assertTrue(res_good2.is_valid_plug_in)

        res_bad2 = self.morpho.analyze_verb("nimeshocked")
        self.assertTrue(res_bad2.has_double_conjugation_error)

    def test_verbal_plugin_matrix_and_ukiarrive(self):
        """Formula: [Subject] + [Tense] + [Object] + [Bare Verb]. Includes Ukiarrive."""
        # Ukiarrive: u- (2s) + ki- (conditional/when) + arrive
        v_arr = self.morpho.analyze_verb("Ukiarrive")
        self.assertTrue(v_arr.is_valid_plug_in)
        self.assertEqual(v_arr.subject_prefix, "u")
        self.assertEqual(v_arr.tense_marker, "ki")
        self.assertEqual(v_arr.bare_verb_root, "arrive")

        # Standard test set
        for surf, s, t, r in [
            ("Anatext", "a", "na", "text"),
            ("Tulicall", "tu", "li", "call"),
            ("Utaniclone", "u", "ta", "clone"),
            ("Wametublock", "wa", "me", "block")
        ]:
            v = self.morpho.analyze_verb(surf)
            self.assertTrue(v.is_valid_plug_in)
            self.assertEqual(v.subject_prefix, s)
            self.assertEqual(v.tense_marker, t)
            self.assertEqual(v.bare_verb_root, r)

    def test_negation_framework(self):
        """Simple present (Sicare, Hatumatch, Hawacare), Past -ku- (Sikucall, Haukureply), Not yet -ja- (Sijaclean, Sijaclear)."""
        # Present: Hawacare
        v_hawa = self.morpho.analyze_verb("Hawacare")
        self.assertTrue(v_hawa.is_negated)
        self.assertEqual(v_hawa.bare_verb_root, "care")

        # Not yet: Sijaclear
        v_clear = self.morpho.analyze_verb("Sijaclear")
        self.assertTrue(v_clear.is_negated)
        self.assertEqual(v_clear.negation_type, "not_yet")
        self.assertEqual(v_clear.bare_verb_root, "clear")

    def test_soft_target_modifier_infix_ka(self):
        """Bantu Class 12 Diminutive Infix (-ka-) inside verb complex frames the target as cute, delicate, or handled gently."""
        # 1. Alikasonga (a-li-ka-songa)
        v_songa = self.morpho.analyze_verb("alikasonga")
        self.assertTrue(v_songa.is_valid_plug_in)
        self.assertEqual(v_songa.subject_prefix, "a")
        self.assertEqual(v_songa.tense_marker, "li")
        self.assertEqual(v_songa.object_marker, "ka")
        self.assertEqual(v_songa.bare_verb_root, "songa")
        self.assertTrue(v_songa.is_soft_target)
        self.assertIn("Soft-Target", v_songa.emotional_affect)
        self.assertIn("delicate target", v_songa.english_translation)

        # 2. Amekaapproach (a-me-ka-approach)
        v_app = self.morpho.analyze_verb("Amekaapproach")
        self.assertTrue(v_app.is_valid_plug_in)
        self.assertEqual(v_app.subject_prefix, "a")
        self.assertEqual(v_app.tense_marker, "me")
        self.assertEqual(v_app.object_marker, "ka")
        self.assertEqual(v_app.bare_verb_root, "approach")
        self.assertTrue(v_app.is_soft_target)
        self.assertIn("cute target", v_app.english_translation)

        # 3. Alikashika (a-li-ka-shika)
        v_shika = self.morpho.analyze_verb("alikashika")
        self.assertTrue(v_shika.is_valid_plug_in)
        self.assertEqual(v_shika.object_marker, "ka")
        self.assertEqual(v_shika.bare_verb_root, "shika")
        self.assertTrue(v_shika.is_soft_target)

        # 4. End-to-end sentence audit
        report = self.validator.audit_sentence("Huyo msee alikasonga na askari stage.")
        self.assertTrue(report.is_fully_compliant)
        self.assertIn("Pillar I: Soft-Target Modifier (-ka-)", report.pillars_triggered)
        soft_issues = [iss for iss in report.issues if iss.rule_name == "The Soft-Target Modifier (-ka-)"]
        self.assertEqual(len(soft_issues), 1)
        self.assertEqual(soft_issues[0].severity, "INFO")
        self.assertIn("Class 12 Diminutive Infix", soft_issues[0].explanation)

        # 5. Morphology Deconstructor Check
        b = self.morph_deconstructor.deconstruct("alikasonga")
        self.assertTrue(b.is_hybrid)
        self.assertTrue(b.is_soft_target)
        self.assertEqual(b.prefix, "a-li-ka-")
        self.assertEqual(b.stem, "songa")
        self.assertIn("Soft-Target", b.emotional_affect)

    def test_disgust_depersonalization_and_mutual_exclusion_rule(self):
        """Forced Ki- class shift strips human dignity for disgust/sarcasm; strictly mutually exclusive with -ka-."""
        # 1. Neutral Human Class vs Forced Inanimate Ki-
        # Neutral: Anasay (Human)
        v_neutral = self.morpho.analyze_verb("Anasay")
        self.assertTrue(v_neutral.is_valid_plug_in)
        self.assertEqual(v_neutral.subject_prefix, "a")
        self.assertFalse(v_neutral.is_disgust_depersonalized)

        # Disgust/Sarcasm: Kinasay (Object / It)
        v_disgust = self.morpho.analyze_verb("Kinasay")
        self.assertTrue(v_disgust.is_valid_plug_in)
        self.assertEqual(v_disgust.subject_prefix, "ki")
        self.assertEqual(v_disgust.bare_verb_root, "say")
        self.assertTrue(v_disgust.is_disgust_depersonalized)
        self.assertIn("Disgust / Sarcastic Depersonalization", v_disgust.emotional_affect)

        # 2. Kinasarrender
        v_surr = self.morpho.analyze_verb("Kinasarrender")
        self.assertTrue(v_surr.is_valid_plug_in)
        self.assertTrue(v_surr.is_disgust_depersonalized)
        self.assertIn("pathetic thing", v_surr.english_translation)

        # 3. Valid Sentence Audit with Forced Ki-
        rep = self.validator.audit_sentence("Kinasay nini huyo msee?")
        self.assertTrue(rep.is_fully_compliant)
        self.assertIn("Pillar I: Disgust / Contempt Modifier (Forced Ki-)", rep.pillars_triggered)
        disgust_issues = [iss for iss in rep.issues if iss.rule_name == "The Disgust / Sarcasm Modifier (Forced Ki-)"]
        self.assertEqual(len(disgust_issues), 1)
        self.assertEqual(disgust_issues[0].severity, "INFO")

        # 4. Mutual Exclusion Rule Enforcement (Kinakasonga / Kinakaapproach)
        # Cannot stack Forced Ki- (Disgust) with -ka- (Endearing Soft-Target)
        v_conflict = self.morpho.analyze_verb("Kinakasonga")
        self.assertFalse(v_conflict.is_valid_plug_in)
        self.assertTrue(v_conflict.has_affect_conflict)
        self.assertIn("strictly mutually exclusive", v_conflict.error_message)

        b_conflict = self.morph_deconstructor.deconstruct("kinakasonga")
        self.assertTrue(b_conflict.has_affect_conflict)

        rep_conflict = self.validator.audit_sentence("Kinakasonga sana stage.")
        self.assertFalse(rep_conflict.is_fully_compliant)
        conflict_errors = [iss for iss in rep_conflict.issues if iss.rule_name == "Affective Polarity Mutual Exclusion Constraint"]
        self.assertEqual(len(conflict_errors), 1)
        self.assertEqual(conflict_errors[0].severity, "ERROR")

    # --------------------------------------------------------------------------
    # SECTION II: NOUN PLURALIZATION & CHAPOS EXCEPTION
    # --------------------------------------------------------------------------
    def test_noun_classes_and_chapos_rule(self):
        """A-WA (People), I-ZI (Everything else), Ma- -s double stack, and Chapos (NEVER Machapo)."""
        # A-WA
        ok_a, _ = self.nouns.validate_agreement("Msee", "amego")
        self.assertTrue(ok_a)
        ok_wa, _ = self.nouns.validate_agreement("Wasee", "wamego")
        self.assertTrue(ok_wa)

        # I-ZI
        ok_i, _ = self.nouns.validate_agreement("book", "imepotea")
        self.assertTrue(ok_i)
        ok_zi, _ = self.nouns.validate_agreement("books", "zimepotea")
        self.assertTrue(ok_zi)

        # Double stack: Maphones, Mabooks, Macomputers, Madrivers
        for w in ["Maphones", "Mabooks", "Macomputers", "Madrivers"]:
            res = self.nouns.analyze_noun(w)
            self.assertTrue(res.is_double_stack)

        # Food Plural Rule: Chapos is valid, Machapo is illegal!
        res_chapos = self.nouns.analyze_noun("Chapos")
        self.assertEqual(res_chapos.noun_class, "I-ZI")

        res_machapo = self.nouns.analyze_noun("Machapo")
        self.assertEqual(res_machapo.noun_class, "ILLEGAL_FOOD_PLURAL")

        report_bad_food = self.validator.audit_sentence("Tukule machapo.")
        self.assertFalse(report_bad_food.is_fully_compliant)
        self.assertTrue(any(i.rule_name == "Food Plural Constraint" for i in report_bad_food.issues))

    # --------------------------------------------------------------------------
    # SECTION III: MODIFIERS (KI- / VI-)
    # --------------------------------------------------------------------------
    def test_manner_modifiers(self):
        """Alishikwa vistupid, Alifanya kazi kihero, Anajicarry kiactor."""
        m1 = self.manner.analyze_manner("vistupid")
        self.assertTrue(m1.is_manner_modifier)
        self.assertEqual(m1.prefix, "vi")

        m2 = self.manner.analyze_manner("kihero")
        self.assertTrue(m2.is_manner_modifier)
        self.assertEqual(m2.prefix, "ki")

        m3 = self.manner.analyze_manner("kiactor")
        self.assertTrue(m3.is_manner_modifier)

    # --------------------------------------------------------------------------
    # SECTION IV: POSSESSIVES
    # --------------------------------------------------------------------------
    def test_possessives_including_human_system(self):
        """Track 1: Book yangu, Phone yako, Driver wangu, Maboyfriends wake. Track 2: My phones zimepotea, Your books ziko wapi?"""
        t1_driver = self.possessives.analyze_possessive_phrase(["Driver", "wangu"])
        self.assertEqual(t1_driver["track"], "Track 1 (Swahili Agreement Post-Noun)")
        self.assertEqual(t1_driver["concord"], "w")

        t1_boyfriends = self.possessives.analyze_possessive_phrase(["Maboyfriends", "wake"])
        self.assertEqual(t1_boyfriends["track"], "Track 1 (Swahili Agreement Post-Noun)")
        self.assertEqual(t1_boyfriends["concord"], "w")

        t2_books = self.possessives.analyze_possessive_phrase(["Your", "books", "ziko", "wapi?"])
        self.assertEqual(t2_books["track"], "Track 2 (English Structural Pre-Noun)")
        self.assertTrue(t2_books["triggers_swahili_verb"])

    # --------------------------------------------------------------------------
    # SECTION V: PREPOSITIONS
    # --------------------------------------------------------------------------
    def test_prepositions_and_idiomatic_exception(self):
        """Zero preposition (Niko class, Siwezi fika town). Exception: Ako out of town. Suffix ban: officeni."""
        # Zero preposition: Siwezi fika town
        r1 = self.validator.audit_sentence("Siwezi fika town.")
        self.assertTrue(r1.is_fully_compliant)

        # Idiomatic exception: Ako out of town
        r2 = self.validator.audit_sentence("Ako out of town.")
        self.assertTrue(r2.is_fully_compliant)

        # Suffix ban: officeni
        r3 = self.validator.audit_sentence("Simama officeni.")
        self.assertFalse(r3.is_fully_compliant)
        self.assertTrue(any(i.rule_name == "The Suffix Ban" for i in r3.issues))

    # --------------------------------------------------------------------------
    # SECTION VI: TIME & CERTAINTY
    # --------------------------------------------------------------------------
    def test_time_conventions(self):
        """Saa three (9:00), Saa ten (4:00), Tupatane three, around five."""
        # Saa ten: 10 + 6 = 16 % 12 = 4:00
        t_ten = self.time.analyze_time("Tupatane saa ten.")
        self.assertEqual(len(t_ten), 1)
        self.assertEqual(t_ten[0].digital_clock_meaning, "4:00")

        # Around five
        t_five = self.time.analyze_time("Nitaturn up huko base around five.")
        self.assertTrue(any(t.convention == "UNCERTAINTY_AROUND" and t.written_word == "five" for t in t_five))

    # --------------------------------------------------------------------------
    # SECTION VII: FINANCIAL & ELECTRONICS VALUE MATRIX
    # --------------------------------------------------------------------------
    def test_currency_and_counting_thousands(self):
        """
        - Ashu (10), Mbao (20), Finje (50), Soo (100), Rwabe (200), Punch (500), Thao/Kapa (1000), Mita (1M).
        - Banned redundancy: 'soo one'.
        - English Track: Two K, Five K.
        - Swahili Track: Thao mbili, Kapa tatu, kapa moja.
        - Illegal hybrid: 'two thao'.
        - Electronics: Tenje & 'vutia tenje'.
        """
        # Base currency
        res_ashu = self.financial.analyze_financial("Sina hata ashu.")
        self.assertTrue(any(r.raw_expression == "ashu" and r.value_kes == 10 for r in res_ashu))

        res_kapa = self.financial.analyze_financial("Niko na kapa moja hapa.")
        self.assertTrue(any(r.raw_expression == "kapa moja" and r.value_kes == 1000 for r in res_kapa))

        # Redundancy error: "soo one"
        res_soo_one = self.financial.analyze_financial("Nipatie soo one.")
        self.assertTrue(any(not r.is_valid and r.token_type == "BANNED_REDUNDANCY" for r in res_soo_one))

        # English track: "Two K"
        res_2k = self.financial.analyze_financial("Nililipa two k.")
        self.assertTrue(any(r.token_type == "ENGLISH_TRACK" and r.value_kes == 2000 for r in res_2k))

        # Swahili track: "Thao mbili"
        res_sw = self.financial.analyze_financial("Nililipa thao mbili.")
        self.assertTrue(any(r.token_type == "SWAHILI_TRACK" and r.value_kes == 2000 for r in res_sw))

        # Illegal hybrid track: "two thao"
        res_bad_hybrid = self.financial.analyze_financial("Nililipa two thao.")
        self.assertTrue(any(not r.is_valid and r.token_type == "ILLEGAL_HYBRID_TRACK" for r in res_bad_hybrid))

        # Electronics: Tenje & vutia tenje
        res_tenje = self.financial.analyze_financial("Nilikuvutia tenje asubuhi.")
        self.assertTrue(any(r.raw_expression == "vutia tenje" for r in res_tenje))

    # --------------------------------------------------------------------------
    # SECTION VIII: CONVERSATIONAL STATUS & DISTRESS SYSTEM
    # --------------------------------------------------------------------------
    def test_conversational_status_and_distress(self):
        """
        - Greetings & responses: Niaje?, Rada yako?, Form ni gani? -> Rada iko safi.
        - Security command: Wee kaa rada!
        - Distress: Nimesota, Nimekauka.
        """
        # Greetings & responses
        s1 = self.conversational.analyze_status("Niaje bana? Rada yako?")
        self.assertTrue(any(r.category == "GREETING" and "niaje" in r.raw_expression for r in s1))
        self.assertTrue(any(r.category == "GREETING" and "rada yako" in r.raw_expression for r in s1))

        # Security command
        s2 = self.conversational.analyze_status("Wee kaa rada basi!")
        self.assertTrue(any(r.category == "SECURITY_COMMAND" for r in s2))

        # Financial distress
        s3 = self.conversational.analyze_status("Nimesota na nimekauka mbaya!")
        self.assertTrue(any(r.category == "Financial Distress" for r in s3))

    # --------------------------------------------------------------------------
    # SECTION IX: MASTER CONTEXTUAL SCRIPT VERIFICATION
    # --------------------------------------------------------------------------
    def test_master_contextual_script_full_compliance(self):
        """
        The 5-line verified dialogue must lock together perfectly and achieve 100% compliance:
        Line 1: Msee A: "Niaje bana? Rada yako? Nilikuvutia tenje asubuhi."
        Line 2: Msee B: "Sasa? Rada iko safi, nilikuwa mbali na tenje. Form ni gani?"
        Line 3: Msee A: "Acha nichomoke town tukule chapo na madondo, niko na kapa moja hapa."
        Line 4: Msee B: "Manze siwezi fika town, nimesota na nimekauka mbaya! Sina hata ashu."
        Line 5: Msee A: "Haya poa, wee kaa rada basi. Nitaturn up huko base around five."
        """
        transcript = [
            'Msee A: "Niaje bana? Rada yako? Nilikuvutia tenje asubuhi."',
            'Msee B: "Sasa? Rada iko safi, nilikuwa mbali na tenje. Form ni gani?"',
            'Msee A: "Acha nichomoke town tukule chapo na madondo, niko na kapa moja hapa."',
            'Msee B: "Manze siwezi fika town, nimesota na nimekauka mbaya! Sina hata ashu."',
            'Msee A: "Haya poa, wee kaa rada basi. Nitaturn up huko base around five."'
        ]

        reports = self.validator.validate_dialogue(transcript)
        self.assertEqual(len(reports), 5)

        for i, rep in enumerate(reports, 1):
            self.assertTrue(
                rep.is_fully_compliant,
                f"Line {i} failed compliance: {[issue.explanation for issue in rep.issues]}"
            )

    # --------------------------------------------------------------------------
    # REAL-WORLD EMPIRICAL CORPORA TEST (LYRICS, SOCIAL MEDIA, PODCASTS)
    # --------------------------------------------------------------------------
    def test_real_world_corpora_compliance(self):
        """Validates authentic real-world utterances from Kenyan music, #KOT, TikTok, and podcasts."""
        from verify_blueprint_real_world import MUSIC_LYRICS_CORPUS, SOCIAL_MEDIA_CORPUS, PODCAST_CORPUS

        all_corpora = (
            [m["line"] for m in MUSIC_LYRICS_CORPUS] +
            [s["comment"] for s in SOCIAL_MEDIA_CORPUS] +
            [p["quote"] for p in PODCAST_CORPUS]
        )

        for text in all_corpora:
            rep = self.validator.audit_sentence(text)
            self.assertTrue(
                rep.is_fully_compliant,
                f"Empirical corpus failed compliance on: '{text}' -> {[i.explanation for i in rep.issues]}"
            )

    # --------------------------------------------------------------------------
    # EMERGENT RULES TEST (RULES X - XVII DISCOVERED FROM MASS DATA)
    # --------------------------------------------------------------------------
    def test_emergent_rules_discovery(self):
        """Verifies the 8 emergent rules discovered through the 2.3M-word mass audit."""
        # Rule X: Metathesis / Syllable Reversal
        rep_x = self.validator.audit_sentence("Niko na doba, lakini sina sape ya kubuy gomba.")
        self.assertIn("Pillar X: Metathesis Inversion", rep_x.pillars_triggered)

        # Rule XI: Demonstrative Compression
        rep_xi = self.validator.audit_sentence("Hii form inabamba, hiyo story nilisahau.")
        self.assertIn("Pillar XI: Demonstrative Compression", rep_xi.pillars_triggered)

        # Rule XII: Copula-Predicate Clitic Chains
        rep_xii = self.validator.audit_sentence("Niko down lakini tuko ready kuanza.")
        self.assertIn("Pillar XII: Copula-Predicate Fusion", rep_xii.pillars_triggered)

        # Rule XIII: Universal Genitives ('wa' and 'za')
        rep_xiii = self.validator.audit_sentence("Wasee wa mtaa wanapenda ngoma za Arbantone.")
        self.assertIn("Pillar XIII: Universal Genitives", rep_xiii.pillars_triggered)

        # Rule XIV: Discourse Solidarity Anchors
        rep_xiv = self.validator.audit_sentence("Manze nimeshangaa sana bana!")
        self.assertIn("Pillar XIV: Discourse Solidarity Anchors", rep_xiv.pillars_triggered)

        # Rule XV: Subjunctive Cohortative & Prohibitive Chains
        rep_xv1 = self.validator.audit_sentence("Acha nichomoke sasa.")
        self.assertIn("Pillar XV: Subjunctive Cohortative & Prohibitive Chains", rep_xv1.pillars_triggered)

        rep_xv2 = self.validator.audit_sentence("Wacha kuoverthink kila kitu.")
        self.assertIn("Pillar XV: Subjunctive Cohortative & Prohibitive Chains", rep_xv2.pillars_triggered)

        # Rule XVI: Bantu Open-Vowel Epenthesis / Paragoge
        rep_xvi = self.validator.audit_sentence("Cheki hiyo pasi, twende kwa klabu.")
        self.assertIn("Pillar XVI: Bantu Open-Vowel Epenthesis", rep_xvi.pillars_triggered)

        # Rule XVII: Reduplicative Intensification
        rep_xvii = self.validator.audit_sentence("Inabamba mbaya mbaya, kuja sasa sasa!")
        self.assertIn("Pillar XVII: Reduplicative Intensification", rep_xvii.pillars_triggered)

    # --------------------------------------------------------------------------
    # METATHESIS STRUCTURAL INSULATION LAYER TESTS (PILLAR X REFACTOR)
    # --------------------------------------------------------------------------
    def test_metathesis_generational_slider_and_metadata(self):
        """
        Validates the Generational/Locational Slider (Meta-Filter):
        - Cryptographic inversions are OFF by default (deep_street_slang=False).
        - Tokens have Inversion Index (0.0 - 1.0) and Socio-Economic Register metadata.
        - Slider activation toggles active status.
        """
        engine = MetathesisEngine(deep_street_slang=False)
        self.assertFalse(engine.deep_street_slang)

        # Off by default analysis
        res_default = engine.analyze_metathesis(["seemo", "sape", "doba"])
        self.assertEqual(len(res_default), 3)
        for item in res_default:
            self.assertFalse(item["slider_active"])
            self.assertGreaterEqual(item["inversion_index"], 0.60)
            self.assertTrue(len(item["socio_economic_layer"]) > 0)
            self.assertTrue(len(item["primary_risk_factor"]) > 0)

        # Explicitly activated slider (Deep Street Slang mode)
        engine_deep = MetathesisEngine(deep_street_slang=True)
        res_deep = engine_deep.analyze_metathesis(["seemo", "sape", "doba"])
        for item in res_deep:
            self.assertTrue(item["slider_active"])

    def test_inversion_decoder_routing_table_baseline_rewrites(self):
        """
        Validates the Inversion Decoder Routing Table:
        Every cryptographic token is bound to and rewritten to its standard baseline root:
          - seemo -> msee
          - sape -> pesa
          - gomba -> mboga
          - pachu -> chupa
          - manya -> nyama
          - tum -> mtu
          - ngeta -> chokehold
        """
        tokens = ["Seemo", "sape", "gomba", "pachu", "manya", "tum", "ngeta"]
        rewritten = self.metathesis.intercept_and_rewrite(tokens)
        expected = ["Msee", "pesa", "mboga", "chupa", "nyama", "mtu", "chokehold"]
        self.assertEqual(rewritten, expected)

    def test_semantic_shift_exception_engine_ndauwo_and_doba(self):
        """
        Validates Semantic Shift Overrides and Core Lexical Integrity:
          - Doba is MUSIC / BEAT / SONG (derived from dub/dancehall culture).
          - Dawa is MEDICINE (Standard Swahili healthcare/pharmaceutical).
          - In urban transit metathesis, 'ndauwo' diverged to denote BUS FARE,
            while 'dawa' itself unambiguously remains MEDICINE.
        """
        # 1. Dawa is medicine
        res_dawa = self.nouns.analyze_noun("dawa")
        self.assertEqual(res_dawa.noun_class, "I-ZI")
        self.assertIn("Medicine", res_dawa.gloss)

        # 2. Ndauwo denotes bus fare (divergent transit metathesis)
        entry_ndauwo = self.metathesis.get_routing_entry("ndauwo")
        self.assertIsNotNone(entry_ndauwo)
        self.assertTrue(entry_ndauwo.is_semantic_shift)
        self.assertEqual(entry_ndauwo.internal_rewrite, "fare")
        self.assertEqual(entry_ndauwo.safe_universal_equivalent, "Bus Fare")
        self.assertIn("High Risk", entry_ndauwo.primary_risk_factor)
        self.assertEqual(entry_ndauwo.standard_root, "dawa")

        # 3. Doba is music
        entry_doba = self.metathesis.get_routing_entry("doba")
        self.assertIsNotNone(entry_doba)
        self.assertTrue(entry_doba.is_semantic_shift)
        self.assertEqual(entry_doba.internal_rewrite, "music")
        self.assertEqual(entry_doba.safe_universal_equivalent, "Music / Song")
        self.assertEqual(entry_doba.bracket_label, "music")

        # 4. Bado is an authentic, standard Kiswahili word ('still / not yet')
        # It is NOT an inverted token and must never trigger metathesis or be altered
        self.assertIsNone(self.metathesis.get_routing_entry("bado"))
        rep_bado = self.validator.audit_sentence("Bado niko hapa, sijaarrive bado.")
        self.assertTrue(rep_bado.is_fully_compliant)
        self.assertNotIn("Pillar X: Metathesis Inversion", rep_bado.pillars_triggered)
        self.assertEqual(self.metathesis.normalize_silently("Bado niko hapa"), "Bado niko hapa")

    def test_failsafe_ux_output_modes(self):
        """
        Validates Method A (Silent Normalization for Parsers/Translators) and
        Method B (Visual Glancing with bracketed tooltips for Readers):
          - "Sina sape" -> "Sina pesa"
          - "Niko na doba, lakini sina sape ya kubuy gomba." ->
            Silent: "Niko na music, lakini sina pesa ya kubuy mboga."
            Glancing: "Niko na doba [music], lakini sina sape [pesa] ya kubuy gomba [mboga]."
          - "Nipe ndauwo ya msupa." ->
            Silent: "Nipe fare ya msupa."
            Glancing: "Nipe ndauwo [fare] ya msupa."
          - "Seemo amego." ->
            Silent: "Msee amego."
            Glancing: "Seemo [msee] amego."
        """
        # Method A: Silent Normalization
        self.assertEqual(
            self.metathesis.normalize_silently("Sina sape"),
            "Sina pesa"
        )
        self.assertEqual(
            self.metathesis.normalize_silently("Niko na doba, lakini sina sape ya kubuy gomba."),
            "Niko na music, lakini sina pesa ya kubuy mboga."
        )
        self.assertEqual(
            self.metathesis.normalize_silently("Nipe ndauwo ya msupa."),
            "Nipe fare ya msupa."
        )
        self.assertEqual(
            self.metathesis.normalize_silently("Seemo amego."),
            "Msee amego."
        )

        # Method B: Visual Glancing
        self.assertEqual(
            self.metathesis.glance_annotated("Niko na doba, lakini sina sape ya kubuy gomba."),
            "Niko na doba [music], lakini sina sape [pesa] ya kubuy gomba [mboga]."
        )
        self.assertEqual(
            self.metathesis.glance_annotated("Nipe ndauwo ya msupa."),
            "Nipe ndauwo [fare] ya msupa."
        )
        self.assertEqual(
            self.metathesis.glance_annotated("Seemo amego."),
            "Seemo [msee] amego."
        )

    def test_metathesis_validator_integration_and_modes(self):
        """
        Validates end-to-end integration into LooselySwahiliValidator:
        - Default mode: flags INFO about Generational Slider being OFF, internally rewrites tokens.
        - Deep street mode: recognizes deep street in-group authenticity.
        - Breakdown includes silent normalization and visual glancing.
        """
        sentence = "Niko na doba, lakini sina sape ya kubuy gomba."

        # Default mode (Generational Slider OFF -> Structural Insulation active)
        rep_standard = self.validator.audit_sentence(sentence, deep_street_slang=False)
        self.assertTrue(rep_standard.is_fully_compliant)
        self.assertIn("Pillar X: Metathesis Inversion", rep_standard.pillars_triggered)
        self.assertEqual(rep_standard.syntactic_breakdown["metathesis_slider_mode"], "STANDARD_INSULATED")
        self.assertEqual(
            rep_standard.syntactic_breakdown["silent_normalization"],
            "Niko na music, lakini sina pesa ya kubuy mboga."
        )
        self.assertEqual(
            rep_standard.syntactic_breakdown["visual_glancing"],
            "Niko na doba [music], lakini sina sape [pesa] ya kubuy gomba [mboga]."
        )
        # Should have INFO issue detailing insulation
        self.assertTrue(any(i.severity == "INFO" and "Structural Insulation" in i.rule_name for i in rep_standard.issues))

        # Deep street mode (Generational Slider ON)
        rep_deep = self.validator.audit_sentence(sentence, deep_street_slang=True)
        self.assertTrue(rep_deep.is_fully_compliant)
        self.assertEqual(rep_deep.syntactic_breakdown["metathesis_slider_mode"], "DEEP_STREET_AUTHENTICITY")
        # In deep street mode, no INFO advisory warning is required
        self.assertFalse(any("Generational Slider OFF" in i.rule_name for i in rep_deep.issues))

if __name__ == "__main__":
    unittest.main()



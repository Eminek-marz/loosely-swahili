"""
Stress-test Battery for Expanded Generative Grammar Rules (1 to 7)
Validates syntactic boundaries, aspect shifts, noun class concords, and dialect alternatives.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.english_to_codeswitch import EnglishToKenyanCodeSwitcher

class TestExpandedGrammarRules(unittest.TestCase):
    def setUp(self):
        self.switcher = EnglishToKenyanCodeSwitcher()

    def test_rule_1_wh_interrogative_past(self):
        res = self.switcher.code_switch_sentence("Who monitored the transactions?")
        self.assertIn("Nani ali-monitor", res.kenyan_codeswitch)

    def test_rule_1_wh_interrogative_future(self):
        res = self.switcher.code_switch_sentence("Who will control the market?")
        self.assertIn("Nani ata-control", res.kenyan_codeswitch)

    def test_rule_1_wh_interrogative_negative(self):
        res = self.switcher.code_switch_sentence("Who doesn't run the system?")
        self.assertIn("Nani ha-run", res.kenyan_codeswitch)

    def test_rule_2_demonstrative_plural_transformation(self):
        res = self.switcher.code_switch_sentence("The transactions were canceled.")
        self.assertTrue(res.kenyan_codeswitch.startswith("Hizi transactions"))

    def test_rule_2_demonstrative_abstract_vs_large_object(self):
        res_arch = self.switcher.code_switch_sentence("The architecture is modern.")
        self.assertTrue(res_arch.kenyan_codeswitch.startswith("Hii architecture"))

        res_complex = self.switcher.code_switch_sentence("The complex is large.")
        self.assertTrue(res_complex.kenyan_codeswitch.startswith("Hili complex"))

    def test_rule_2_distance_deixis(self):
        res = self.switcher.code_switch_sentence("That transaction was delayed.")
        self.assertTrue(res.kenyan_codeswitch.startswith("Iyo transaction"))

    def test_rule_3_distributive_plural_concord(self):
        res = self.switcher.code_switch_sentence("Every facet of their lives was examined.")
        self.assertIn("kila facet ya maisha zao", res.kenyan_codeswitch.lower())

    def test_rule_3_distributive_human_target(self):
        res = self.switcher.code_switch_sentence("Every member of the team attended.")
        self.assertIn("kila member wa team", res.kenyan_codeswitch.lower())

    def test_rule_4_negative_gerund_object_infix(self):
        res = self.switcher.code_switch_sentence("Without you noticing them, they accessed the database.")
        self.assertIn("bila wewe ku-wa-notice", res.kenyan_codeswitch.lower())

    def test_rule_4_negative_gerund_reflexive(self):
        res = self.switcher.code_switch_sentence("Without you hurting yourself, you can deploy the app.")
        self.assertIn("bila wewe ku-ji-hurt", res.kenyan_codeswitch.lower())

    def test_rule_5_rhetorical_negative(self):
        res = self.switcher.code_switch_sentence("Is such an attack not dangerous?")
        self.assertEqual(res.kenyan_codeswitch.strip(), "Attack kama hiyo si dangerous, kweli?")

    def test_rule_5_rhetorical_plural(self):
        res = self.switcher.code_switch_sentence("Are such attacks possible?")
        self.assertEqual(res.kenyan_codeswitch.strip(), "Attacks kama hizo ni possible, kweli?")

    def test_rule_6_locative_abstract_domain(self):
        res = self.switcher.code_switch_sentence("In international politics, alliances shift.")
        self.assertIn("kwa international politics", res.kenyan_codeswitch.lower())

    def test_rule_6_locative_physical_urban_vs_deep_sheng(self):
        res_urban = self.switcher.code_switch_sentence("In the office, people work hard.", dialect_mode="urban_standard")
        self.assertIn("kwa office", res_urban.kenyan_codeswitch.lower())
        self.assertIn("office-ini", res_urban.dialect_alternatives.get("office", ""))

        res_sheng = self.switcher.code_switch_sentence("In the office, people work hard.", dialect_mode="deep_sheng")
        self.assertIn("office-ini", res_sheng.kenyan_codeswitch.lower())

    def test_rule_7_modal_concord_singular_human(self):
        res = self.switcher.code_switch_sentence("An engineer could understand this code.")
        self.assertIn("engineer ange-understand", res.kenyan_codeswitch.lower())

    def test_rule_7_modal_concord_singular_system(self):
        res = self.switcher.code_switch_sentence("The software could fail under stress.")
        self.assertIn("software inge-fail", res.kenyan_codeswitch.lower())

    def test_rule_7_modal_concord_mass_noun(self):
        res = self.switcher.code_switch_sentence("Water could dry up in summer.")
        self.assertIn("maji yange-dry up", res.kenyan_codeswitch.lower())

    def test_rule_7_modal_concord_abstract_mass(self):
        res = self.switcher.code_switch_sentence("Liquidity could dry up during crisis.")
        self.assertIn("liquidity inge-dry up", res.kenyan_codeswitch.lower())

    def test_rule_7_modal_concord_plural_inanimate(self):
        res = self.switcher.code_switch_sentence("Networks could compute logical functions.")
        self.assertIn("zinge-compute", res.kenyan_codeswitch.lower())

    # --------------------------------------------------------------------------
    # 3-STEP DEPENDENCY ARCHITECTURE TESTS (5 CHECKPOINTS)
    # --------------------------------------------------------------------------
    def test_checkpoint_1_relative_clause_and_possessive_inversion(self):
        res = self.switcher.code_switch_sentence("The truth that shapes our reality is profound.")
        self.assertIn("truth enye inashape reality yetu", res.kenyan_codeswitch.lower())

    def test_checkpoint_2_habitual_consecutive_infinitive(self):
        res = self.switcher.code_switch_sentence("Secret societies that use symbols to veil the truth exist.")
        self.assertIn("secret societies enye hutumia symbols ku-veil", res.kenyan_codeswitch.lower())

    def test_checkpoint_3_subject_third_person_agglutination(self):
        res = self.switcher.code_switch_sentence("He challenges the standard model.")
        self.assertIn("yeye anachallenge", res.kenyan_codeswitch.lower())

    def test_checkpoint_4_genitive_associative_concord(self):
        res = self.switcher.code_switch_sentence("The view of consciousness is evolving.")
        self.assertIn("view ya consciousness", res.kenyan_codeswitch.lower())

    def test_checkpoint_5_present_passive_noun_class_agreement(self):
        res = self.switcher.code_switch_sentence("That reality is influenced by external factors.")
        self.assertIn("iyo reality inainfluenciwa na", res.kenyan_codeswitch.lower())

    def test_full_integrated_target_sentence(self):
        input_en = "He challenges the view of consciousness, suggesting that reality is influenced by secret societies that use symbols to veil the truth that shapes our reality."
        res = self.switcher.code_switch_sentence(input_en)
        expected = "Yeye anachallenge view ya consciousness, jambo linalosuggest kwamba reality inainfluenciwa na secret societies enye hutumia symbols ku-veil truth enye inashape reality yetu."
        self.assertEqual(res.kenyan_codeswitch.strip(), expected)

    # --------------------------------------------------------------------------
    # ZERO-SHOT GENERALIZATION ON PREVIOUSLY UNSEEN SENTENCES
    # --------------------------------------------------------------------------
    def test_unseen_virology_sentence(self):
        s = "The doctor noticed that the virus is transmitted by infected patients who use crowded clinics to treat the symptoms that threaten their health."
        res = self.switcher.code_switch_sentence(s)
        self.assertIn("iyo virus inatransmitiwa na", res.kenyan_codeswitch)
        self.assertIn("patients enye hutumia crowded clinics ku-treat", res.kenyan_codeswitch)
        self.assertIn("symptoms enye zinathreaten", res.kenyan_codeswitch)
        self.assertIn("health yao", res.kenyan_codeswitch)

    def test_unseen_astrophysics_sentence(self):
        s = "Astronomers believe that the telescope was launched by international agencies that use satellites to explore the galaxy that surrounds our planet."
        res = self.switcher.code_switch_sentence(s)
        self.assertIn("iyo telescope ililaunchiwa na", res.kenyan_codeswitch)
        self.assertIn("agencies enye hutumia satellites ku-explore", res.kenyan_codeswitch)
        self.assertIn("galaxy enye inasurround", res.kenyan_codeswitch)
        self.assertIn("planet yetu", res.kenyan_codeswitch)

    def test_unseen_cryptography_sentence(self):
        s = "The founder explained that the transaction is verified by decentralized validators who use cryptographic keys to protect the ledger that records our assets."
        res = self.switcher.code_switch_sentence(s)
        self.assertIn("iyo transaction inaverifyiwa na", res.kenyan_codeswitch)
        self.assertIn("validators enye hutumia cryptographic keys ku-protect", res.kenyan_codeswitch)
        self.assertIn("ledger enye inarecord", res.kenyan_codeswitch)
        self.assertIn("assets zetu", res.kenyan_codeswitch)

    def test_unseen_robotics_sentence(self):
        s = "Engineers observed that the robot is guided by deep neural models that use sensor feedback to optimize the trajectory that moves our mechanical arm."
        res = self.switcher.code_switch_sentence(s)
        self.assertIn("iyo robot inaguidiwa na", res.kenyan_codeswitch)
        self.assertIn("models enye hutumia sensor feedback ku-optimize", res.kenyan_codeswitch)
        self.assertIn("trajectory enye inamove", res.kenyan_codeswitch)
        self.assertIn("mechanical arm yetu", res.kenyan_codeswitch)

    # --------------------------------------------------------------------------
    # QUANTUM MODALS, FUTURE HYPOTHETICAL, AND PREPOSITION ALIGNMENT TESTS
    # --------------------------------------------------------------------------
    def test_quantum_universe_book_phrase(self):
        s = "Everything That Can Happen Does Happen is a 2011 book by Brian Cox."
        res = self.switcher.code_switch_sentence(s)
        expected = "Kila kitu enye inaweza happen inaweza kuHappen ni a 2011 book ya Brian Cox."
        self.assertEqual(res.kenyan_codeswitch.strip(), expected)

    def test_future_hypothetical_subgraph(self):
        res1 = self.switcher.code_switch_sentence("The network would have failed.")
        self.assertIn("network ingekuwa imefail", res1.kenyan_codeswitch.lower())

        res2 = self.switcher.code_switch_sentence("The engineers would have noticed.")
        self.assertIn("engineers wangekuwa wamenotice", res2.kenyan_codeswitch.lower())

        res3 = self.switcher.code_switch_sentence("The systems would have crashed.")
        self.assertIn("systems zingekuwa zimecrash", res3.kenyan_codeswitch.lower())

    def test_preposition_alignment_matrix(self):
        res_by = self.switcher.code_switch_sentence("This is a book by Brian Cox.")
        self.assertIn("book ya Brian Cox", res_by.kenyan_codeswitch)

        res_for = self.switcher.code_switch_sentence("A secure system for users.")
        self.assertIn("system ya users", res_for.kenyan_codeswitch)

        res_with = self.switcher.code_switch_sentence("She is working with engineers.")
        self.assertIn("na engineers", res_with.kenyan_codeswitch)

    def test_synthetic_generator(self):
        from src.synthetic_dataset_generator import SyntheticCodeSwitchGenerator
        gen = SyntheticCodeSwitchGenerator(seed=123)
        sample = gen.generate_sample()
        self.assertIn("english", sample)
        self.assertIn("kenyan_code_switch", sample)
        self.assertIn("scenario", sample)

        # Test prompt formats
        tagged = gen.format_sample(sample, fmt="tagged")
        self.assertIn("<|src_en|>", tagged["text"])
        self.assertIn("<|tgt_kcs|>", tagged["text"])

        llama3 = gen.format_sample(sample, fmt="llama3")
        self.assertIn("<|start_header_id|>assistant<|end_header_id|>", llama3["text"])

    # --------------------------------------------------------------------------
    # UNIVERSAL HIGH-FREQUENCY COMMON WORDS TESTS
    # --------------------------------------------------------------------------
    def test_high_frequency_common_words(self):
        # Test 1: Daily survival & domestic basics
        res1 = self.switcher.code_switch_sentence("The people need water and food at home today.")
        self.assertIn("watu wanahitaji maji", res1.kenyan_codeswitch.lower())
        self.assertIn("kwa keja leo", res1.kenyan_codeswitch.lower())

        # Test 2: Temporal & motion
        res2 = self.switcher.code_switch_sentence("Yesterday the doctor went to town to get money.")
        self.assertIn("jana doc alienda tao kupata chapaa", res2.kenyan_codeswitch.lower())

        # Test 3: Cognition & volition
        res3 = self.switcher.code_switch_sentence("He knows that the children want to eat now.")
        self.assertIn("anajua kuwa watoto wanataka kula sasa", res3.kenyan_codeswitch.lower())

        # Test 4: Future motion & commerce
        res4 = self.switcher.code_switch_sentence("Tomorrow they will go to the market to buy fresh food.")
        self.assertIn("kesho wataenda sokoni kununua", res4.kenyan_codeswitch.lower())

        # Test 5: Plural past motion & relational preposition
        res5 = self.switcher.code_switch_sentence("Yesterday they went to the market with their friends.")
        self.assertIn("jana walienda sokoni na mabeshte zao", res5.kenyan_codeswitch.lower())

    # --------------------------------------------------------------------------
    # MULTI-TIER REGISTER & INSTRUCTION CONTROL TOKENS TESTS
    # --------------------------------------------------------------------------
    def test_instruction_control_tokens_and_registers(self):
        # Formal register: [GENERATE_FORMAL] enforces formal/standard terms
        res_formal = self.switcher.code_switch_sentence("[GENERATE_FORMAL] My friend needs money for the house.")
        self.assertIn("pesa", res_formal.kenyan_codeswitch.lower())
        self.assertIn("nyumba", res_formal.kenyan_codeswitch.lower())
        self.assertNotIn("chapaa", res_formal.kenyan_codeswitch.lower())
        self.assertNotIn("keja", res_formal.kenyan_codeswitch.lower())

        # Street register: [GENERATE_STREET] enforces urban Sheng slang
        res_street = self.switcher.code_switch_sentence("[GENERATE_STREET] My friend needs money for the house.")
        self.assertIn("chapaa", res_street.kenyan_codeswitch.lower())
        self.assertIn("keja", res_street.kenyan_codeswitch.lower())
        self.assertIn("beste", res_street.kenyan_codeswitch.lower())

        # Casual register: [GENERATE_CASUAL] enforces standard conversational Swahili baseline
        res_casual = self.switcher.code_switch_sentence("[GENERATE_CASUAL] My friend needs money for the house.")
        self.assertIn("pesa", res_casual.kenyan_codeswitch.lower())
        self.assertIn("nyumba", res_casual.kenyan_codeswitch.lower())
        self.assertIn("rafiki", res_casual.kenyan_codeswitch.lower())

    # --------------------------------------------------------------------------
    # EVERYDAY VERB NEGATION FRAMEWORK ACROSS REGISTERS
    # --------------------------------------------------------------------------
    def test_everyday_verb_negation_across_registers(self):
        # 1. "I don't care": Formal -> Sijali, Street -> Sina shughuli
        neg_formal_1 = self.switcher.code_switch_sentence("[GENERATE_FORMAL] I don't care about the problem.")
        self.assertIn("sijali", neg_formal_1.kenyan_codeswitch.lower())

        neg_street_1 = self.switcher.code_switch_sentence("[GENERATE_STREET] I don't care about the problem.")
        self.assertIn("sina shughuli", neg_street_1.kenyan_codeswitch.lower())

        # 2. "We didn't agree": Formal -> Hatukukubaliana, Street -> Hatukuskizana
        neg_formal_2 = self.switcher.code_switch_sentence("[GENERATE_FORMAL] We didn't agree with the manager.")
        self.assertIn("hatukukubaliana", neg_formal_2.kenyan_codeswitch.lower())

        neg_street_2 = self.switcher.code_switch_sentence("[GENERATE_STREET] We didn't agree with the manager.")
        self.assertIn("hatukuskizana", neg_street_2.kenyan_codeswitch.lower())

        # 3. "He doesn't know": Formal -> Hajui, Street -> Hananga clue
        neg_formal_3 = self.switcher.code_switch_sentence("[GENERATE_FORMAL] He doesn't know that my friend needs money.")
        self.assertIn("hajui", neg_formal_3.kenyan_codeswitch.lower())

        neg_street_3 = self.switcher.code_switch_sentence("[GENERATE_STREET] He doesn't know that my friend needs money.")
        self.assertIn("hananga clue", neg_street_3.kenyan_codeswitch.lower())

        # 4. "I don't have money": Formal -> Sina pesa, Street -> Sina chapaa
        neg_formal_4 = self.switcher.code_switch_sentence("[GENERATE_FORMAL] I don't have money.")
        self.assertIn("sina pesa", neg_formal_4.kenyan_codeswitch.lower())

        neg_street_4 = self.switcher.code_switch_sentence("[GENERATE_STREET] I don't have money.")
        self.assertIn("sina chapaa", neg_street_4.kenyan_codeswitch.lower())

    # --------------------------------------------------------------------------
    # PROBABILISTIC CONTEXT-WEIGHTED GENERATOR TESTS
    # --------------------------------------------------------------------------
    def test_probabilistic_context_weighted_generation(self):
        from src.synthetic_dataset_generator import choose_weighted_token, choose_weighted_negation, generate_context_weighted_pair
        
        # Test weighted token sampling across registers
        formal_token = choose_weighted_token("money", "formal")
        self.assertIn(formal_token, ["money", "pesa"])

        street_token = choose_weighted_token("money", "street")
        self.assertIn(street_token, ["chapaa", "ganji", "pesa"])

        # Test weighted negation sampling
        neg_formal = choose_weighted_negation("i don't care", "formal")
        self.assertIn(neg_formal, ["sijali", "sina wasiwasi"])

        neg_street = choose_weighted_negation("i don't care", "street")
        self.assertIn(neg_street, ["sina shughuli", "sina time", "sina stress"])

        # Test contextual generation batch
        pair_street = generate_context_weighted_pair("My friend got a new job to make more money", context="street")
        self.assertEqual(pair_street["context_tag"], "street")
        self.assertEqual(pair_street["control_token"], "[GENERATE_STREET]")

        pair_formal = generate_context_weighted_pair("My friend got a new job to make more money", context="formal")
        self.assertEqual(pair_formal["context_tag"], "formal")
        self.assertEqual(pair_formal["control_token"], "[GENERATE_FORMAL]")

    # --------------------------------------------------------------------------
    # DEMONSTRATIVE OBJECT FRONTING & POINTING CONCORD TESTS
    # --------------------------------------------------------------------------
    def test_emphatic_pointing_concord_and_infixes(self):
        # 1. Street Food: "I don't have money to buy *food* today." -> Sina chapaa kununua iyo dish leo.
        res_street_food = self.switcher.code_switch_sentence("I don't have money to buy *food* today.", dialect_mode="street")
        self.assertEqual(res_street_food.kenyan_codeswitch, "Sina chapaa kununua iyo dish leo.")

        # 2. Formal System: "We cannot stop the *system* now." -> Hatuwezi ku-i-stop hii system sasa.
        res_formal_sys = self.switcher.code_switch_sentence("We cannot stop the *system* now.", dialect_mode="formal")
        self.assertEqual(res_formal_sys.kenyan_codeswitch, "Hatuwezi ku-i-stop hii system sasa.")

        # 3. Street System: "We cannot stop the *system* now." -> Hatuezi ku-i-stop hii system sasa.
        res_street_sys = self.switcher.code_switch_sentence("We cannot stop the *system* now.", dialect_mode="street")
        self.assertEqual(res_street_sys.kenyan_codeswitch, "Hatuezi ku-i-stop hii system sasa.")

    def test_demonstrative_object_fronting(self):
        # 1. Formal Fronting: [FRONT_FOCUS] We cannot stop the *system* now. -> Hii system, hatuwezi ku-i-stop sasa.
        res_front_formal = self.switcher.code_switch_sentence("[FRONT_FOCUS] We cannot stop the *system* now.", dialect_mode="formal")
        self.assertEqual(res_front_formal.kenyan_codeswitch, "Hii system, hatuwezi ku-i-stop sasa.")

        # 2. Street Fronting: [FRONT_FOCUS] We cannot stop the *system* now. -> Hii system, hatuezi ku-i-stop sasa.
        res_front_street = self.switcher.code_switch_sentence("[FRONT_FOCUS] We cannot stop the *system* now.", dialect_mode="street")
        self.assertEqual(res_front_street.kenyan_codeswitch, "Hii system, hatuezi ku-i-stop sasa.")

        # 3. Street Food Fronting: [FRONT_FOCUS] I don't have money to buy *food* today. -> Iyo dish, sina chapaa kununua leo.
        res_front_food = self.switcher.code_switch_sentence("[GENERATE_STREET] [FRONT_FOCUS] I don't have money to buy *food* today.")
        self.assertEqual(res_front_food.kenyan_codeswitch, "Iyo dish, sina chapaa kununua leo.")

    def test_plural_and_human_object_pointing_concord(self):
        # 1. Plural System (Class 10): "transactions" -> zi infix & hizi/izo
        res_tx_formal = self.switcher.code_switch_sentence("We must monitor *transactions* now.", dialect_mode="formal")
        self.assertEqual(res_tx_formal.kenyan_codeswitch, "Lazima tu-zi-monitor hizi transactions sasa.")

        res_tx_street = self.switcher.code_switch_sentence("We must monitor *transactions* now.", dialect_mode="street")
        self.assertEqual(res_tx_street.kenyan_codeswitch, "Lazima tu-zi-monitor izo transactions sasa.")

        res_tx_front = self.switcher.code_switch_sentence("[FRONT_FOCUS] We must monitor *transactions* now.", dialect_mode="formal")
        self.assertEqual(res_tx_front.kenyan_codeswitch, "Hizi transactions, lazima tu-zi-monitor sasa.")

        # 2. Plural Human (Class 2): "engineers" -> wa infix & hawa
        res_eng_formal = self.switcher.code_switch_sentence("We must call the *engineers* now.", dialect_mode="formal")
        self.assertEqual(res_eng_formal.kenyan_codeswitch, "Lazima tu-wa-call hawa engineers sasa.")

        res_eng_front = self.switcher.code_switch_sentence("[FRONT_FOCUS] We must call the *engineers* now.", dialect_mode="formal")
        self.assertEqual(res_eng_front.kenyan_codeswitch, "Hawa engineers, lazima tu-wa-call sasa.")

        # 3. Singular Human (Class 1): "manager" -> m infix & huyu
        res_mgr_formal = self.switcher.code_switch_sentence("We must call the *manager* now.", dialect_mode="formal")
        self.assertEqual(res_mgr_formal.kenyan_codeswitch, "Lazima tu-m-call huyu manager sasa.")

        res_mgr_front = self.switcher.code_switch_sentence("[FRONT_FOCUS] We must call the *manager* now.", dialect_mode="formal")
        self.assertEqual(res_mgr_front.kenyan_codeswitch, "Huyu manager, lazima tu-m-call sasa.")

    def test_explicit_focus_tags(self):
        # 1. (Emphasis on system)
        res_tag = self.switcher.code_switch_sentence("We cannot stop the system now (Emphasis on system)", dialect_mode="formal")
        self.assertIn("ku-i-stop hii system", res_tag.kenyan_codeswitch)

        # 2. [FOCUS: system]
        res_bracket = self.switcher.code_switch_sentence("[FOCUS: system] We cannot stop the system now.", dialect_mode="street")
        self.assertIn("ku-i-stop hii system", res_bracket.kenyan_codeswitch)

        # 3. [FRONT_FOCUS] with [FOCUS: system]
        res_both = self.switcher.code_switch_sentence("[FRONT_FOCUS] [FOCUS: system] We cannot stop the system now.", dialect_mode="formal")
        self.assertEqual(res_both.kenyan_codeswitch, "Hii system, hatuwezi ku-i-stop sasa.")

    def test_synthetic_dataset_emphatic_scenario(self):
        from src.synthetic_dataset_generator import (
            apply_emphatic_pointing,
            generate_emphatic_training_pair,
            SyntheticCodeSwitchGenerator
        )

        # Direct function tests
        out_street = apply_emphatic_pointing("I do not have money to buy food today.", "food", register="street")
        self.assertEqual(out_street, "Sina chapaa kununua iyo dish leo.")

        out_front = apply_emphatic_pointing("We cannot stop the system now.", "system", register="formal", front=True)
        self.assertEqual(out_front, "Hii system, hatuwezi ku-i-stop sasa.")

        # Generator scenario test
        pair = generate_emphatic_training_pair(register="street", front=True)
        self.assertEqual(pair["scenario"], "emphatic_pointing_and_fronting")
        self.assertTrue(pair["is_front_focus"])
        self.assertIn("Demonstrative Left-Dislocation Fronting", pair["rules"])

        gen = SyntheticCodeSwitchGenerator(seed=123)
        sample = gen._generate_emphatic_pointing_scenario(register="formal")
        self.assertEqual(sample["scenario"], "emphatic_pointing_and_fronting")

    def test_rule_1b_locative_interrogatives(self):
        # 1. Singular System (Class 9)
        res_mach = self.switcher.code_switch_sentence("Where is that machine?")
        self.assertEqual(res_mach.kenyan_codeswitch, "Iyo machine iko wapi?")

        res_sys = self.switcher.code_switch_sentence("Where is this system?")
        self.assertEqual(res_sys.kenyan_codeswitch, "Hii system iko wapi?")

        # 2. Plural Transactions (Class 10)
        res_tx_street = self.switcher.code_switch_sentence("Where are those transactions?", dialect_mode="street")
        self.assertEqual(res_tx_street.kenyan_codeswitch, "Izo transactions ziko wapi?")

        res_tx_formal = self.switcher.code_switch_sentence("Where are those transactions?", dialect_mode="formal")
        self.assertEqual(res_tx_formal.kenyan_codeswitch, "Hizo transactions ziko wapi?")

        # 3. Human Singular (Class 1)
        res_mgr_street = self.switcher.code_switch_sentence("Where is that manager?", dialect_mode="street")
        self.assertEqual(res_mgr_street.kenyan_codeswitch, "Uyo manager ako wapi?")

        res_mgr_formal = self.switcher.code_switch_sentence("Where is that manager?", dialect_mode="formal")
        self.assertEqual(res_mgr_formal.kenyan_codeswitch, "Yule manager ako wapi?")

        # 4. Human Plural (Class 2)
        res_eng_street = self.switcher.code_switch_sentence("Where are those engineers?", dialect_mode="street")
        self.assertEqual(res_eng_street.kenyan_codeswitch, "Hao engineers wako wapi?")

        res_eng_formal = self.switcher.code_switch_sentence("Where are those engineers?", dialect_mode="formal")
        self.assertEqual(res_eng_formal.kenyan_codeswitch, "Wale engineers wako wapi?")

    def test_native_agglutination_filter(self):
        from src.english_to_codeswitch import native_agglutination_filter

        # 1. Verb complex collapse
        out1 = native_agglutination_filter("Hii system, hatuezi ku-i-stop sasa.")
        self.assertEqual(out1, "Hii system, hatuezi kuistop sasa.")

        # 2. Bleeding typo correction
        out2 = native_agglutination_filter("Lazima tu-zitmonitor hizi transactions sasa.")
        self.assertEqual(out2, "Lazima tuzimonitor hizi transactions sasa.")

        # 3. Wa and M infixes
        out3 = native_agglutination_filter("Lazima tu-wa-call hawa engineers sasa.")
        self.assertEqual(out3, "Lazima tuwacall hawa engineers sasa.")

        out4 = native_agglutination_filter("Lazima tu-m-call huyu manager sasa.")
        self.assertEqual(out4, "Lazima tumcall huyu manager sasa.")

        # 4. Habitual and bare roots
        out5 = native_agglutination_filter("hu-work, ku-run, ku-change")
        self.assertEqual(out5, "huwork, kurun, kuchange")

    def test_informal_purpose_bridge_filter(self):
        from src.english_to_codeswitch import informal_purpose_bridge_filter

        # 1. Singular resource 'ya'
        out1 = informal_purpose_bridge_filter("Iyo dish, sina chapaa kununua leo.")
        self.assertEqual(out1, "Iyo dish, sina chapaa ya kununua leo.")

        out2 = informal_purpose_bridge_filter("Niko na time kurun leo.")
        self.assertEqual(out2, "Niko na time ya kurun leo.")

        out3 = informal_purpose_bridge_filter("Chance kuchange")
        self.assertEqual(out3, "Chance ya kuchange")

        # 2. Plural resource 'za'
        out4 = informal_purpose_bridge_filter("Hawana funds kuzimonitor.")
        self.assertEqual(out4, "Hawana funds za kuzimonitor.")

        out5 = informal_purpose_bridge_filter("Coins kuclear transactions")
        self.assertEqual(out5, "Coins za kuclear transactions")

    def test_case_preservation_proper_noun_and_acronym(self):
        from src.english_to_codeswitch import native_agglutination_filter

        # 1. Proper Noun preservation (Brian remains Brian, not brian)
        res_brian = self.switcher.code_switch_sentence("[FRONT_FOCUS] Brian cannot stop the *system* now.", dialect_mode="formal")
        self.assertTrue(res_brian.kenyan_codeswitch.startswith("Hii system, Brian "))
        self.assertIn("Brian hatuwezi ku-i-stop sasa.", res_brian.kenyan_codeswitch)

        # Seamless version
        seamless_brian = native_agglutination_filter(res_brian.kenyan_codeswitch)
        self.assertEqual(seamless_brian, "Hii system, Brian hatuwezi kuistop sasa.")

        # 2. Standard pronoun lowercasing (We becomes hatuwezi)
        res_we = self.switcher.code_switch_sentence("[FRONT_FOCUS] We cannot stop the *system* now.", dialect_mode="formal")
        self.assertEqual(res_we.kenyan_codeswitch, "Hii system, hatuwezi ku-i-stop sasa.")

    def test_possessive_inversion_singular_and_plural(self):
        res_sing = self.switcher.code_switch_sentence("This is our system.")
        self.assertIn("system yetu", res_sing.kenyan_codeswitch.lower())

        res_plur = self.switcher.code_switch_sentence("These are our systems.")
        self.assertIn("systems zetu", res_plur.kenyan_codeswitch.lower())

    def test_seamless_dataset_generator(self):
        from src.synthetic_dataset_generator import generate_emphatic_training_pair

        pair = generate_emphatic_training_pair(register="street", front=True, seamless=True)
        self.assertTrue(pair["is_front_focus"])
        # In seamless mode, hyphens in ku-i-, ku-zi-, tu-zi- should be collapsed
        self.assertNotIn("ku-i-", pair["kenyan_code_switch"])
        self.assertNotIn("ku-zi-", pair["kenyan_code_switch"])
        self.assertNotIn("tu-zi-", pair["kenyan_code_switch"])

    def test_einstein_academic_physics_sentence(self):
        s = (
            "Concerning a Heuristic Point of View Toward the Emission and Transformation of Light: "
            "Foundational physics research paper published by Albert Einstein in 1905, "
            "this groundbreaking Annalen der Physik article challenged classical wave theory "
            "by proposing that light is spatially localized and transmitted in discrete packages of energy, "
            "introducing the core concept that laid the structural foundation of quantum mechanics."
        )
        res = self.switcher.code_switch_sentence(s)
        expected = (
            "Kuhusu Heuristic Point of View kuhusu Emission na Transformation ya Light: "
            "Foundational physics research paper yenye ilipublishiwa na Albert Einstein in the 1905, "
            "hii groundbreaking Annalen der Physik article ilichallenge classical wave theory "
            "kwa ku-propose kuwa light iko spatially localized na inatransmitiwa kwa discrete packages za energy, "
            "ikaintroduce core concept enye ili-lay structural foundation ya quantum mechanics."
        )
        self.assertEqual(res.kenyan_codeswitch.strip(), expected)

    def test_fastapi_3d_assembly_sentence(self):
        s = "The task of 3D assembly requires translating an understanding of parts and their relationships into precise spatial arrangements."
        res_way1 = self.switcher.code_switch_sentence(s, dialect_mode="urban_standard")
        res_way2 = self.switcher.code_switch_sentence(s, dialect_mode="deep_sheng")

        # Way 1 (Academic Standard)
        expected_way1 = "Task ya 3D assembly inahitaji ku-translate understanding ya parts na relationships zao kuwa precise spatial arrangements."
        self.assertEqual(res_way1.kenyan_codeswitch.strip(), expected_way1)

        # Way 2 (Colloquial / Deep Sheng)
        expected_way2 = "Hii task ya 3D assembly ina-require ku-translate understanding ya maparts na marelationships zao kuwa precise spatial arrangements."
        self.assertEqual(res_way2.kenyan_codeswitch.strip(), expected_way2)

        # Ensure no broken adjective-sandwich like "spatial sahihi arrangements"
        self.assertNotIn("spatial sahihi arrangements", res_way1.kenyan_codeswitch)
        self.assertNotIn("spatial sahihi arrangements", res_way2.kenyan_codeswitch)

    def test_user_molecular_biology_golden(self):
        s = "This structure has novel features which are of considerable biological interest."
        res_w1 = self.switcher.code_switch_sentence(s, dialect_mode="urban_standard")
        res_w2 = self.switcher.code_switch_sentence(s, dialect_mode="deep_sheng")
        self.assertEqual(res_w1.kenyan_codeswitch.strip(), "Hii structure has features mpya zenye ziko na considerable biological interest.")
        self.assertEqual(res_w2.kenyan_codeswitch.strip(), "Hii structure has mafeatures mpya zenye ziko na considerable biological interest.")

    def test_user_telescopic_lm_continuum_golden(self):
        s = "We train a Telescopic Language Model (TLM) to be that continuum: a nested-capacity Transformer supervised by stochastic prefix supervision with a full anchor."
        res_w1 = self.switcher.code_switch_sentence(s, dialect_mode="urban_standard")
        res_w2 = self.switcher.code_switch_sentence(s, dialect_mode="deep_sheng")
        expected = "Tuna-train Telescopic Language Model (TLM) ndiyo ikuwe iyo continuum: nested-capacity Transformer enye iko supervised na stochastic prefix supervision na anchor kamili."
        self.assertEqual(res_w1.kenyan_codeswitch.strip(), expected)
        self.assertEqual(res_w2.kenyan_codeswitch.strip(), expected)

    def test_user_telescopic_lm_compute_budgets_golden(self):
        s = "One deployed language model must often serve many compute budgets, yet serving each budget still means a separate training or compression run per point."
        res_w1 = self.switcher.code_switch_sentence(s, dialect_mode="urban_standard")
        res_w2 = self.switcher.code_switch_sentence(s, dialect_mode="deep_sheng")
        self.assertEqual(res_w1.kenyan_codeswitch.strip(), "One deployed language model must often serve compute budgets nyingi, lakini ku-serve each budget bado inamaanisha ku-separate training au compression run per point.")
        self.assertEqual(res_w2.kenyan_codeswitch.strip(), "One deployed language model must often serve compute nyingi budgets, lakini ku-serve each budget bado inamaanisha ku-separate training au compression run per point.")

    def test_user_quantum_entanglement_golden(self):
        s = "Entanglement and state distinguishability have long been central topics in quantum foundations. While each has developed into a rich subject in its own right, they can be connected through measurements in complementary bases."
        res_w1 = self.switcher.code_switch_sentence(s, dialect_mode="urban_standard")
        res_w2 = self.switcher.code_switch_sentence(s, dialect_mode="deep_sheng")
        expected_w1 = "Entanglement na state distinguishability zime-kuwa kwa muda mrefu kama central topics kwenye quantum foundations. Wakati kila moja ime-develop kuwa rich subject kwenye its own right, zinaweza kuwa connected kupitia measurements kwenye complementary bases."
        expected_w2 = "Entanglement na state distinguishability zime-kuwa kwa muda mrefu central topics kwenye quantum foundations. Wakati kila moja ime-develop kuwa rich subject kwenye its own right, zinaweza kuwa connected kupitia measurements kwenye complementary bases."
        self.assertEqual(res_w1.kenyan_codeswitch.strip(), expected_w1)
        self.assertEqual(res_w2.kenyan_codeswitch.strip(), expected_w2)

    def test_user_rlx_compiler_golden(self):
        s = "Production machine learning (ML) stacks often split graph compilation and kernel execution across different layers and languages, making backend behavior, deployment guarantees, and performance fallbacks hard to reason about end-to-end."
        res_w1 = self.switcher.code_switch_sentence(s, dialect_mode="urban_standard")
        res_w2 = self.switcher.code_switch_sentence(s, dialect_mode="deep_sheng")
        expected_w1 = "Production machine learning (ML) stacks mara nyingi husplit graph compilation na kernel execution kwa layers tofauti na languages, making backend behavior, deployment guarantees, na performance fallbacks ngumu to reason kuhusu kuanzia mwanzo hadi mwisho."
        expected_w2 = "Production machine learning (ML) stacks mara nyingi husplit graph compilation na kernel execution kwa malayers tofauti na languages, making backend behavior, deployment guarantees, na performance fallbacks ngumu to reason kuhusu kuanzia mwanzo hadi mwisho."
        self.assertEqual(res_w1.kenyan_codeswitch.strip(), expected_w1)
        self.assertEqual(res_w2.kenyan_codeswitch.strip(), expected_w2)

    def test_user_particles_interact_levels_golden(self):
        s = "The scheme follows the single-ensemble paradigm, where particles interact across levels at each timestep."
        res_w1 = self.switcher.code_switch_sentence(s, dialect_mode="urban_standard")
        res_w2 = self.switcher.code_switch_sentence(s, dialect_mode="deep_sheng")
        expected_w1 = "Scheme follows single-ensemble paradigm, where particles zina-interact katika levels at each timestep."
        expected_w2 = "Scheme follows single-ensemble paradigm, where particles zina-interact kwa levels at each timestep."
        self.assertEqual(res_w1.kenyan_codeswitch.strip(), expected_w1)
        self.assertEqual(res_w2.kenyan_codeswitch.strip(), expected_w2)

    def test_user_genomics_generators_golden(self):
        s = "Our results show that CGMM outperforms four current state-of-the-art genomics generators on two different tasks..."
        res_w1 = self.switcher.code_switch_sentence(s, dialect_mode="urban_standard")
        res_w2 = self.switcher.code_switch_sentence(s, dialect_mode="deep_sheng")
        expected_w1 = "Results zetu zinashow kuwa CGMM outperforms four state-of-the-art genomics generators ya sasa kwa tasks mbili tofauti..."
        expected_w2 = "Maresults zetu show kuwa CGMM outperforms four state-of-the-art genomics generators ya sasa kwa matasks mbili tofauti..."
        self.assertEqual(res_w1.kenyan_codeswitch.strip(), expected_w1)
        self.assertEqual(res_w2.kenyan_codeswitch.strip(), expected_w2)

if __name__ == "__main__":
    unittest.main()



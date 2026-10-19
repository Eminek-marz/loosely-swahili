"""
Unit tests for Advanced Morphotactics in Kenyan Loosely Swahili:
1. Consecutive Narrative Aspect Chaining (-ka- infix: "tuli-X na tuka-Y", "ili-X na ika-Y")
2. Pronominal Object Clitics (-zi-, -i-, -wa-: "ku-i-optimize", "ku-zi-evaluate", "Tuli-zi-test")
3. Compound Noun Head-Initial Inversion ("research paper ya quantum mechanics", "intensity ya light")
4. Authorial 1st-Person Plural Subject Agreement ("We release" -> "Tuna-release", "We trained" -> "Tuli-train")
5. Scientific Epistemic Hedging ("Ni wazi kuwa", "Inakaa kama", "Inajulikana wazi kuwa")
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.english_to_codeswitch import EnglishToKenyanCodeSwitcher, MorphologicalRootStripper

class TestAdvancedMorphotactics(unittest.TestCase):
    def setUp(self):
        self.switcher = EnglishToKenyanCodeSwitcher()

    def test_authorial_present_subject_concord(self):
        """Validates that 'We [academic_verb]' becomes 'Tuna-[root]'."""
        res1 = self.switcher.code_switch_sentence("We release the pipeline, the fault injector and all records.")
        self.assertTrue(res1.kenyan_codeswitch.startswith("Tuna-release"))
        self.assertIn("records zote", res1.kenyan_codeswitch)

        res2 = self.switcher.code_switch_sentence("We propose a novel architecture for image generation.")
        self.assertTrue(res2.kenyan_codeswitch.startswith("Tuna-propose"))

        res3 = self.switcher.code_switch_sentence("We present our findings to the community.")
        self.assertTrue(res3.kenyan_codeswitch.startswith("Tuna-present"))

    def test_authorial_past_subject_concord(self):
        """Validates that 'We [past_verb]' becomes 'Tuli-[root]'."""
        res1 = self.switcher.code_switch_sentence("We trained the model for 50 epochs.")
        self.assertTrue(res1.kenyan_codeswitch.startswith("Tuli-train"))

        res2 = self.switcher.code_switch_sentence("We initialized the weights carefully.")
        self.assertTrue(res2.kenyan_codeswitch.startswith("Tuli-initialize"))

    def test_consecutive_narrative_aspect_chaining(self):
        """Validates that coordinated past actions take the consecutive marker -ka-."""
        res1 = self.switcher.code_switch_sentence("We trained the model for 50 epochs and evaluated the results.")
        self.assertIn("tuka-evaluate", res1.kenyan_codeswitch)

        res2 = self.switcher.code_switch_sentence("We initialized the weights, trained the network, and observed convergence.")
        self.assertIn("tuka-train", res2.kenyan_codeswitch)
        self.assertIn("tuka-observe", res2.kenyan_codeswitch)

        res3 = self.switcher.code_switch_sentence("The algorithm received the input, processed the batch, and converged.")
        self.assertIn("ika-process", res3.kenyan_codeswitch)
        self.assertIn("ika-converge", res3.kenyan_codeswitch)

    def test_pronominal_object_clitic_infixes(self):
        """Validates object clitic infixes (-i-, -zi-) inside verbs."""
        res1 = self.switcher.code_switch_sentence("We need to optimize it before deployment.")
        self.assertIn("ku-i-optimize", res1.kenyan_codeswitch)

        res2 = self.switcher.code_switch_sentence("Our team decided to evaluate them carefully.")
        self.assertIn("ku-zi-evaluate", res2.kenyan_codeswitch)

        res3 = self.switcher.code_switch_sentence("We tested them across multiple benchmarks.")
        self.assertIn("Tuli-zi-test", res3.kenyan_codeswitch)

    def test_compound_noun_head_initial_inversion(self):
        """Validates that English modifier-first compounds invert into Bantu head-first genitives."""
        res1 = self.switcher.code_switch_sentence("This quantum mechanics research paper explains light intensity.")
        self.assertIn("research paper ya quantum mechanics", res1.kenyan_codeswitch)
        self.assertIn("intensity ya light", res1.kenyan_codeswitch)

        res2 = self.switcher.code_switch_sentence("We analyzed the neural network architecture and system performance.")
        self.assertIn("architecture ya neural network", res2.kenyan_codeswitch)
        self.assertIn("performance ya system", res2.kenyan_codeswitch)

    def test_epistemic_scientific_hedging(self):
        """Validates scientific evidential hedging and discourse markers."""
        res1 = self.switcher.code_switch_sentence("It is clear that the energy is localized in discrete quanta.")
        self.assertTrue(res1.kenyan_codeswitch.startswith("Ni wazi kuwa"))
        self.assertIn("energy iko localized", res1.kenyan_codeswitch)

        res2 = self.switcher.code_switch_sentence("It seems that the model generalizes well to unseen datasets.")
        self.assertTrue(res2.kenyan_codeswitch.startswith("Inakaa kama"))
        self.assertIn("ina-generalize fiti kwa", res2.kenyan_codeswitch)

    def test_temporal_tense_aspect_modality(self):
        """Validates Kenyan Bantu TAM (Tense, Aspect, Modality) temporal grammar."""
        # 1. Passive Modal Infinitive: 'should be noted' -> 'inafaa ku-notiwa kuwa'
        res1 = self.switcher.code_switch_sentence("It should be noted that the energy is quantized.")
        self.assertTrue(res1.kenyan_codeswitch.startswith("Inafaa ku-notiwa kuwa"))
        self.assertIn("inaquantiziwa", res1.kenyan_codeswitch)

        # 2. Potentiality Modal Infinitive: 'can be observed' -> 'inaweza ku-observiwa kuwa'
        res2 = self.switcher.code_switch_sentence("It can be observed that light behaves as particles.")
        self.assertIn("Inaweza ku-observiwa kuwa", res2.kenyan_codeswitch)

        # 3. Present Perfect Anteriority: 'studies have demonstrated' -> 'studies zime-demonstrate'
        res3 = self.switcher.code_switch_sentence("Recent studies have demonstrated the effect.")
        self.assertIn("zime-demonstrate", res3.kenyan_codeswitch)

        # 4. Pluperfect / Past Anterior: 'had converged' -> 'ilikuwa ime-converge'
        res4 = self.switcher.code_switch_sentence("The system had converged before the timeout.")
        self.assertIn("ilikuwa ime-converge", res4.kenyan_codeswitch)

        # 5. Negative Inceptive Aspect: 'have not yet resolved' -> 'Hatuja-resolve'
        res5 = self.switcher.code_switch_sentence("We have not yet resolved this paradox.")
        self.assertIn("Hatuja-resolve", res5.kenyan_codeswitch)

        # 6. Future Prospective & Temporal Adverbial: 'will converge over time' -> 'ita-converge kwa muda'
        res6 = self.switcher.code_switch_sentence("The algorithm will converge over time.")
        self.assertIn("ita-converge", res6.kenyan_codeswitch)
        self.assertIn("kwa muda", res6.kenyan_codeswitch)

        # 7. Gnomic Scientific Laws & Adjective Protection: no 'ilispeed' bug
        res7 = self.switcher.code_switch_sentence("Electrons travel at high speed.")
        self.assertIn("zina-travel", res7.kenyan_codeswitch)
        self.assertIn("kwa speed ya juu", res7.kenyan_codeswitch)
        self.assertNotIn("ilispeed", res7.kenyan_codeswitch)

    def test_prepositional_and_relational_semantic_network(self):
        """Validates prepositional semantics (dyadic, causal, temporal limit, year locative, instrumental)."""
        # 1. Historical Year Locative: 'in 1905' -> 'Mnamo 1905'
        res1 = self.switcher.code_switch_sentence("In 1905, the paper was published in Annalen der Physik.")
        self.assertTrue(res1.kenyan_codeswitch.startswith("Mnamo 1905"))
        self.assertIn("ilipublishiwa kwa", res1.kenyan_codeswitch)

        # 2. Dyadic Relator & Identifier Protection: 'Between cluster A and cluster B' -> 'Kati ya cluster A na cluster B'
        res2 = self.switcher.code_switch_sentence("Between cluster A and cluster B, data transfers through high-speed fiber.")
        self.assertTrue(res2.kenyan_codeswitch.startswith("Kati ya cluster A na cluster B"))
        self.assertIn("kupitia high-speed fiber", res2.kenyan_codeswitch)

        # 3. Temporal Interval, Origin-Destination & Span: 'During training', 'from 1.5 to 0.1 within five minutes'
        res3 = self.switcher.code_switch_sentence("During training, the loss decreased from 1.5 to 0.1 within five minutes.")
        self.assertTrue(res3.kenyan_codeswitch.startswith("Wakati wa training"))
        self.assertIn("kutoka 1.5 hadi 0.1", res3.kenyan_codeswitch)
        self.assertIn("ndani ya five minutes", res3.kenyan_codeswitch)
        self.assertIn("hii loss", res3.kenyan_codeswitch)

        # 4. Evidential, Conditional & Deprivation: 'According to', 'under conditions', 'without wave properties'
        res4 = self.switcher.code_switch_sentence("According to Einstein, under certain conditions, light behaves without wave properties.")
        self.assertIn("Kulingana na Einstein", res4.kenyan_codeswitch)
        self.assertIn("chini ya certain conditions", res4.kenyan_codeswitch)
        self.assertIn("bila wave properties", res4.kenyan_codeswitch)

        # 5. Substitutive & Distributed Domain: 'Instead of recurrence', 'across all layers'
        res5 = self.switcher.code_switch_sentence("Instead of recurrence, we rely on attention across all layers.")
        self.assertIn("Badala ya recurrence", res5.kenyan_codeswitch)
        self.assertIn("kwa layers zote", res5.kenyan_codeswitch)

        # 6. Terminal Horizon & Causal Relator: 'By the end of', 'due to caching'
        res6 = self.switcher.code_switch_sentence("By the end of the experiment, performance improved due to caching.")
        self.assertIn("Kufikia mwisho wa experiment", res6.kenyan_codeswitch)
        self.assertIn("kutokana na caching", res6.kenyan_codeswitch)

        # 7. Agentive Passive & Durational Measure: 'by the researchers', 'for 50 epochs'
        res7 = self.switcher.code_switch_sentence("The model was trained by the researchers with a new optimizer for 50 epochs.")
        self.assertIn("ilitrainiwa na hao researchers", res7.kenyan_codeswitch)
        self.assertIn("na optimizer mpya", res7.kenyan_codeswitch)
        self.assertIn("kwa 50 epochs", res7.kenyan_codeswitch)

    def test_post_nominal_adjective_inversion(self):
        """Validates Bantu Head-Initial syntax (Noun + Adjective) and proper noun protection."""
        # 1. Exact user target: 'with a new optimizer' -> 'na optimizer mpya'
        res1 = self.switcher.code_switch_sentence("The model was trained by the researchers with a new optimizer for 50 epochs.")
        self.assertEqual(res1.kenyan_codeswitch, "Hii model ilitrainiwa na hao researchers na optimizer mpya kwa 50 epochs.")

        # 2. Novel architecture + good results -> architecture mpya + results fiti
        res2 = self.switcher.code_switch_sentence("We propose a novel architecture with good results.")
        self.assertEqual(res2.kenyan_codeswitch, "Tuna-propose architecture mpya na results fiti.")

        # 3. Different sources + different topics -> sources tofauti + topics tofauti
        res3 = self.switcher.code_switch_sentence("Books from different sources with different topics.")
        self.assertEqual(res3.kenyan_codeswitch, "Books kutoka sources tofauti na topics tofauti.")

        # 4. Proper noun protection: 'New York' must never become 'mpya York'
        res4 = self.switcher.code_switch_sentence("They lived in New York.")
        self.assertIn("New York", res4.kenyan_codeswitch)
        self.assertNotIn("mpya York", res4.kenyan_codeswitch)

        # 5. Class concord for 'old': singular 'system ya zamani' vs plural 'methods za zamani'
        res5 = self.switcher.code_switch_sentence("They used an old system and old methods.")
        self.assertIn("system ya zamani", res5.kenyan_codeswitch)
        self.assertIn("methods za zamani", res5.kenyan_codeswitch)

    def test_swahili_adjective_convention(self):
        """Validates authentic Swahili adjective convention: Bantu concord, invariable loans, relational genitives, and intensifiers."""
        # 1. Bantu Inflected Adjectives: '-zuri' -> 'wazuri' (Class 2), '-kubwa' -> 'kubwa' (Class 9)
        res1 = self.switcher.code_switch_sentence("The good researchers evaluated the model.")
        self.assertEqual(res1.kenyan_codeswitch, "Hao researchers wazuri walievaluate hii model.")

        res2 = self.switcher.code_switch_sentence("We tested on a large dataset.")
        self.assertIn("dataset kubwa", res2.kenyan_codeswitch)

        # 2. Invariable Loan Adjectives: 'kuu', 'mbalimbali', 'tofauti', 'muhimu', 'sahihi'
        res3 = self.switcher.code_switch_sentence("The main server processes various requests from different sources.")
        self.assertIn("server kuu", res3.kenyan_codeswitch)
        self.assertIn("requests mbalimbali", res3.kenyan_codeswitch)
        self.assertIn("sources tofauti", res3.kenyan_codeswitch)

        res4 = self.switcher.code_switch_sentence("They found important factors and accurate predictions.")
        self.assertIn("factors muhimu", res4.kenyan_codeswitch)
        self.assertIn("predictions sahihi", res4.kenyan_codeswitch)

        # 3. Relational Genitive Adjectives: 'ya/za' + noun base
        res5 = self.switcher.code_switch_sentence("We achieve low latency and fast convergence.")
        self.assertIn("latency ya chini", res5.kenyan_codeswitch)
        self.assertIn("convergence ya haraka", res5.kenyan_codeswitch)

        res6 = self.switcher.code_switch_sentence("The initial weights determine final results.")
        self.assertIn("weights za kwanza", res6.kenyan_codeswitch)
        self.assertIn("results za mwisho", res6.kenyan_codeswitch)

        # 4. Intensifiers & Superlatives: 'very small' -> '[adj] sana'
        res7 = self.switcher.code_switch_sentence("It showed a very small error and stable performance.")
        self.assertIn("error ndogo sana", res7.kenyan_codeswitch)
        self.assertIn("performance thabiti", res7.kenyan_codeswitch)

    def test_plural_sentence_concord(self):
        """Validates natural English plurals with Swahili clause-level concord (no forced ma- in formal register)."""
        # 1. Inanimate plural subject present: 'servers process' -> 'servers zina-process'
        res1 = self.switcher.code_switch_sentence("The servers process requests.")
        self.assertEqual(res1.kenyan_codeswitch, "Hizi servers zina-process requests.")

        # 2. Inanimate plural subject: 'databases store' -> 'databases zina-store'
        res2 = self.switcher.code_switch_sentence("These databases store data.")
        self.assertEqual(res2.kenyan_codeswitch, "Hizi databases zina-store data.")

        # 3. Human plural subject present: 'researchers explain' -> 'researchers wana-explain'
        res3 = self.switcher.code_switch_sentence("The researchers explain the results.")
        self.assertEqual(res3.kenyan_codeswitch, "Hao researchers wana-explain hizi results.")

        # 4. Human plural subject: 'authors propose' -> 'authors wana-propose'
        res4 = self.switcher.code_switch_sentence("The authors propose a novel architecture.")
        self.assertEqual(res4.kenyan_codeswitch, "Hao authors wana-propose architecture mpya.")

        # 5. Inanimate plural model agreement: 'models achieve' -> 'models zina-achieve'
        res5 = self.switcher.code_switch_sentence("These models achieve high accuracy.")
        self.assertEqual(res5.kenyan_codeswitch, "Hizi models zina-achieve accuracy ya juu.")

        # 6. Quantifier concord: inanimate 'files zote' vs human 'researchers wote'
        res6 = self.switcher.code_switch_sentence("All files were updated yesterday.")
        self.assertIn("Files zote ziliupdatiwa", res6.kenyan_codeswitch)

        # 7. Copula past: 'All researchers were present' -> 'Researchers wote walikuwa present.'
        res7 = self.switcher.code_switch_sentence("All researchers were present.")
        self.assertEqual(res7.kenyan_codeswitch, "Researchers wote walikuwa present.")

        # 8. Algorithm convergence with gnomic temporal: 'algorithms zina-converge kwa muda'
        res8 = self.switcher.code_switch_sentence("The algorithms converge over time.")
        self.assertEqual(res8.kenyan_codeswitch, "Hizi algorithms zina-converge kwa muda.")

    def test_bantu_object_concord_engine(self):
        """Validates mandatory Bantu object concord (-wa-, -m-, -i-, -zi-) and pronominal incorporation."""
        # 1. Mandatory Human Object Concord: plural -wa- and singular -m-
        res1 = self.switcher.code_switch_sentence("We called the engineers.")
        self.assertEqual(res1.kenyan_codeswitch, "Tuli-wa-call hao engineers.")

        res2 = self.switcher.code_switch_sentence("We contacted the manager.")
        self.assertEqual(res2.kenyan_codeswitch, "Tuli-m-contact huyo manager.")

        # 2. Pronominal Object Incorporation: drops standalone English pronoun
        res3 = self.switcher.code_switch_sentence("We called him.")
        self.assertEqual(res3.kenyan_codeswitch, "Tuli-m-call.")

        res4 = self.switcher.code_switch_sentence("We called them.")
        self.assertEqual(res4.kenyan_codeswitch, "Tuli-wa-call.")

        res5 = self.switcher.code_switch_sentence("We tested it.")
        self.assertEqual(res5.kenyan_codeswitch, "Tuli-i-test.")

        res6 = self.switcher.code_switch_sentence("We evaluated them.")
        self.assertEqual(res6.kenyan_codeswitch, "Tuli-zi-evaluate.")

        # 3. Present Tense Transitive Concord
        res7 = self.switcher.code_switch_sentence("We call the engineers.")
        self.assertEqual(res7.kenyan_codeswitch, "Tuna-wa-call hao engineers.")

        res8 = self.switcher.code_switch_sentence("We contact the manager.")
        self.assertEqual(res8.kenyan_codeswitch, "Tuna-m-contact huyo manager.")

        res9 = self.switcher.code_switch_sentence("We evaluate these algorithms.")
        self.assertEqual(res9.kenyan_codeswitch, "Tuna-zi-evaluate hizi algorithms.")

        res10 = self.switcher.code_switch_sentence("We optimize this model.")
        self.assertEqual(res10.kenyan_codeswitch, "Tuna-i-optimize hii model.")

        # 4. 3rd-Person Subject Concord with Human Objects
        res11 = self.switcher.code_switch_sentence("They called the engineers.")
        self.assertEqual(res11.kenyan_codeswitch, "Wali-wa-call hao engineers.")

        res12 = self.switcher.code_switch_sentence("He contacted the manager.")
        self.assertEqual(res12.kenyan_codeswitch, "Ali-m-contact huyo manager.")

        # 5. Infinitives with Human Objects & Pronouns
        res13 = self.switcher.code_switch_sentence("We need to call the engineers.")
        self.assertEqual(res13.kenyan_codeswitch, "Tunahitaji ku-wa-call hao engineers.")

        res14 = self.switcher.code_switch_sentence("They want to contact the manager.")
        self.assertEqual(res14.kenyan_codeswitch, "Wao wanataka ku-m-contact huyo manager.")

        res15 = self.switcher.code_switch_sentence("We want to evaluate them.")
        self.assertEqual(res15.kenyan_codeswitch, "Tunataka ku-zi-evaluate.")

    def test_three_degree_spatio_temporal_deixis(self):
        """Validates 3-degree spatio-temporal deixis: Proximal (Degree 1), Medial (Degree 2), and Distal (Degree 3)."""
        # 1. Degree 1 Proximal: 'these/this' -> 'hawa/hizi/hii/huyu' (speaker proximity, present space/time)
        res1 = self.switcher.code_switch_sentence("These models achieve high accuracy.")
        self.assertEqual(res1.kenyan_codeswitch, "Hizi models zina-achieve accuracy ya juu.")

        # 2. Degree 2 Medial / Referential: 'the [noun]' -> 'hao/huyo/hiyo' (discourse reference, not physically present in the room)
        res2 = self.switcher.code_switch_sentence("The good researchers evaluated the model.")
        self.assertEqual(res2.kenyan_codeswitch, "Hao researchers wazuri walievaluate hii model.")

        res3 = self.switcher.code_switch_sentence("The researchers explain the results.")
        self.assertEqual(res3.kenyan_codeswitch, "Hao researchers wana-explain hizi results.")

        res4 = self.switcher.code_switch_sentence("We contacted the manager.")
        self.assertEqual(res4.kenyan_codeswitch, "Tuli-m-contact huyo manager.")

        # 3. Degree 3 Distal: historical / remote past anchors ('In 1905', 'Mnamo 1905') -> 'wale/ile/zile/yule'
        res5 = self.switcher.code_switch_sentence("In 1905, the researchers published the paper.")
        self.assertEqual(res5.kenyan_codeswitch, "Mnamo 1905, wale researchers walipublish ile paper.")

    def test_negative_auxiliary_inversion(self):
        """Validates Negative Auxiliary Inversion with Bantu noun class concord and bare root preservation."""
        # 1. Class 9 Inanimate Singular Negative Present: 'does not [verb]' -> 'hai[root]'
        res1 = self.switcher.code_switch_sentence("The system does not process corrupted files.")
        self.assertEqual(res1.kenyan_codeswitch, "Hii system haiprocess corrupted files.")

        # 2. Class 10 Inanimate Plural Negative Present: 'do not [verb]' -> 'hazi[root]'
        res2 = self.switcher.code_switch_sentence("The servers do not respond to ping requests.")
        self.assertEqual(res2.kenyan_codeswitch, "Hizi servers hazirespond to ping requests.")

        # 3. Class 1 Human Singular Negative Past: 'did not [verb]' -> 'haku-[root]'
        res3 = self.switcher.code_switch_sentence("The researcher did not publish the paper.")
        self.assertEqual(res3.kenyan_codeswitch, "Huyo researcher haku-publish hii paper.")

        # 4. Class 2 Human Plural Negative Modal: 'cannot [verb]' -> 'hawawezi ku-[root]'
        res4 = self.switcher.code_switch_sentence("The engineers cannot deploy the update.")
        self.assertEqual(res4.kenyan_codeswitch, "Hao engineers hawawezi ku-deploy update.")

        # 5. 1st Person Plural Negative Future: 'We will not [verb]' -> 'Hatuta-[root]'
        res5 = self.switcher.code_switch_sentence("We will not support legacy protocols.")
        self.assertEqual(res5.kenyan_codeswitch, "Hatuta-support legacy protocols.")

        # 6. 1st Person Plural Negative Present: 'We do not [verb]' -> 'Hatu[root]'
        res6 = self.switcher.code_switch_sentence("We do not recommend this approach.")
        self.assertEqual(res6.kenyan_codeswitch, "Haturecommend hii approach.")

        # 7. Object Concord Incorporation in Negative Structures
        res7 = self.switcher.code_switch_sentence("We did not call them.")
        self.assertEqual(res7.kenyan_codeswitch, "Hatuku-wa-call.")

        res8 = self.switcher.code_switch_sentence("The manager does not contact them.")
        self.assertEqual(res8.kenyan_codeswitch, "Manager ha-wa-contact.")

    def test_register_aware_plurals(self):
        """Validates register-aware plurals: English technical plural with Class 10 Concord in standard mode vs ma- in deep sheng."""
        # 1. Standard / Enterprise register: preserves clean technical English plural
        res_std = self.switcher.code_switch_sentence("Our team will deploy the new servers tomorrow.", dialect_mode="urban_standard")
        self.assertEqual(res_std.kenyan_codeswitch, "Team yetu will deploy hizi servers mpya kesho.")
        self.assertIn("plural_servers", res_std.dialect_alternatives)
        self.assertEqual(res_std.dialect_alternatives["plural_servers"], "maserver")

        # 2. Deep Sheng register: applies double-stacked ma- prefix
        res_sheng = self.switcher.code_switch_sentence("Our team will deploy the new servers tomorrow.", dialect_mode="deep_sheng")
        self.assertEqual(res_sheng.kenyan_codeswitch, "Team yetu will deploy hizi maserver mpya kesho.")

    def test_participial_and_compound_subject_concord(self):
        """Validates generalized compound plural subjects and trailing participial clauses (-ki- aspect)."""
        # 1. Compound plural subject + present concord + trailing participle
        res1 = self.switcher.code_switch_sentence("Brownian dynamics simulations confirm this paradoxical effect, offering predictions.")
        self.assertEqual(res1.kenyan_codeswitch, "Brownian dynamics simulations zina-confirm hii paradoxical effect, ziki-offer predictions.")

        # 2. Multi-modifier plural subject + clause complementizer + embedded plural subject
        res2 = self.switcher.code_switch_sentence("Recent experimental observations demonstrate that quantum fluctuations alter the ground state.")
        self.assertEqual(res2.kenyan_codeswitch, "Recent experimental observations zina-demonstrate kuwa quantum fluctuations zina-alter ground state.")

        # 3. Biology subject + trailing negative preventative participle
        res3 = self.switcher.code_switch_sentence("These enzymes cleave the target DNA sequence, preventing viral replication.")
        self.assertEqual(res3.kenyan_codeswitch, "Hizi enzymes zina-cleave target DNA sequence, ziki-prevent viral replication.")

        # 4. Singular algorithm subject + trailing result participle with 'kwa'
        res4 = self.switcher.code_switch_sentence("The algorithm converges rapidly, resulting in lower latency.")
        self.assertEqual(res4.kenyan_codeswitch, "Hii algorithm inaconverge rapidly, iki-result kwa lower latency.")

    def test_equative_role_preposition_and_acronym_shield(self):
        """Validates 'as a' -> 'kama' role preposition and shields uppercase acronyms (IED, LED) from root stripping."""
        # 1. Scientific sentence with 'as a practical strategy' and 'IED classification'
        res1 = self.switcher.code_switch_sentence("These results support EEG-centric multimodal binding as a practical strategy for source-level IED classification.")
        self.assertEqual(res1.kenyan_codeswitch, "Hizi results zina-support EEG-centric multimodal binding kama strategy ya vitendo ya source-level IED classification.")

        # 2. General 'as a baseline' equative preposition
        res2 = self.switcher.code_switch_sentence("We use this model as a baseline for comparison.")
        self.assertIn("kama baseline", res2.kenyan_codeswitch)

        # 3. Uppercase acronyms protected from root truncation
        self.assertEqual(MorphologicalRootStripper.strip_to_bare_root("IED"), "IED")
        self.assertEqual(MorphologicalRootStripper.strip_to_bare_root("LED"), "LED")

if __name__ == "__main__":
    unittest.main()


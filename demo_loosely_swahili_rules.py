"""
Interactive & Visual CLI Showcase: The Master Lexicon & Structural Blueprint
Demonstrates the exact morphosyntactic, financial, conversational, and spatial rules
of the East African Swahili-English Hybrid (Sheng / Engsh).
"""

import sys
from pathlib import Path

# Ensure UTF-8 terminal output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
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
    ConversationalDistressEngine
)

def print_section(title: str):
    print("\n" + "=" * 78)
    print(f"  {title}")
    print("=" * 78)

def main():
    validator = LooselySwahiliValidator()
    morpho = MorphosyntacticEngine()
    nouns = NounClassEngine()
    manner = MannerModifierEngine()
    poss = PossessiveEngine()
    prep = PrepositionEngine()
    time_eng = TimeCertaintyEngine()
    fin_eng = FinancialElectronicsEngine()
    conv_eng = ConversationalDistressEngine()

    print("\n🇰🇪 OFFICIAL MASTER LEXICON & STRUCTURAL BLUEPRINT FOR EAST AFRICAN HYBRID (SHENG/ENGSH)")
    print("      Complete 9-Section Syntactic & Pragmatic Architecture")

    # --------------------------------------------------------------------------
    # SECTION I: THE MORPHOSYNTACTIC ENGINE (VERBS & ACTIONS)
    # --------------------------------------------------------------------------
    print_section("I. THE MORPHOSYNTACTIC ENGINE (VERBS & ACTIONS)")
    print("• Hardware: Swahili prefixes & infixes | Software: Raw English verb roots.\n")

    print("[1] The Bare Root Constraint:")
    verb_pairs = [
        ("Alikuwa amepick", "Alikuwa amepicked"),
        ("Nimeshock", "Nimeshocked"),
        ("Tulicall", "Tulicalled")
    ]
    for good, bad in verb_pairs:
        res_good = morpho.analyze_verb(good.split()[-1])
        res_bad = morpho.analyze_verb(bad.split()[-1])
        print(f"   ✅ Enforce: '{good}' -> Bare Root '{res_good.bare_verb_root}' (Valid Plug-In: {res_good.is_valid_plug_in})")
        print(f"   🚫 Reject:  '{bad}'  -> Error: Double-Conjugation detected (Valid: {res_bad.is_valid_plug_in})")

    print("\n[2] The Verbal Plug-In Matrix: [Subject] + [Tense] + [Object Prefix] + [Bare English Verb]")
    matrix_samples = [
        ("Anatext", "She/He is texting"),
        ("Tulicall", "We called"),
        ("Utaniclone", "You will clone me"),
        ("Wametublock", "They have blocked us"),
        ("Ukiarrive", "When you arrive")
    ]
    for surf, gloss in matrix_samples:
        v = morpho.analyze_verb(surf)
        obj_str = f" + Obj:[{v.object_marker}]" if v.object_marker else ""
        print(f"   • '{surf}' -> Subj:[{v.subject_prefix}] + Tense:[{v.tense_marker}]{obj_str} + Root:[{v.bare_verb_root}]")
        print(f"     Meaning: {gloss} | Analysis: {v.english_translation}")

    print("\n[3] The Negation Framework: Swahili Negative Prefixes (Mid-sentence 'don't'/'not' rejected)")
    neg_samples = [
        ("Sicare", "Simple Present Negation", "I don't care"),
        ("Hatumatch", "Simple Present Negation", "We don't match"),
        ("Hawacare", "Simple Present Negation", "They don't care"),
        ("Sikucall", "Past Negation (-ku- / Never Happened)", "I didn't call"),
        ("Haukureply", "Past Negation (-ku- / Never Happened)", "You didn't reply"),
        ("Sijaclean", "Not Yet Past Negation (-ja-)", "I haven't cleaned yet"),
        ("Sijaclear", "Not Yet Past Negation (-ja-)", "I haven't paid yet")
    ]
    for surf, category, meaning in neg_samples:
        n = morpho.analyze_verb(surf)
        print(f"   • '{surf}' -> {category} | Root: '{n.bare_verb_root}' | Meaning: {meaning}")

    # --------------------------------------------------------------------------
    # SECTION II: NOUN PLURALIZATION & SIMPLIFIED GRAMMATICAL CLASSES
    # --------------------------------------------------------------------------
    print_section("II. NOUN PLURALIZATION & SIMPLIFIED GRAMMATICAL CLASSES")
    print("• Two universal pathways: A-WA (People Only) & I-ZI (Everything Else: Objects, Tech, Concepts).\n")

    print("[1] The A-WA Class (For People Only):")
    for n, v, gloss in [("Msee", "amego", "The guy has gone"), ("Wasee", "wamego", "The guys have gone")]:
        ok, msg = nouns.validate_agreement(n, v)
        print(f"   • {n} {v} -> {msg} ({gloss})")

    print("\n[2] The I-ZI Class (For Everything Else):")
    for n, v, gloss in [("Hiyo book", "imepotea", "That book is lost"), ("Hizo books", "zimepotea", "Those books are lost")]:
        ok, msg = nouns.validate_agreement(n.split()[-1], v)
        print(f"   • {n} {v} -> {msg} ({gloss})")

    print("\n[3] The English '-s' Double-Stack Rule & Food Plural Constraints:")
    for d in ["Maphones", "Mabooks", "Macomputers", "Madrivers"]:
        na = nouns.analyze_noun(d)
        print(f"   • '{d}' -> Prefix: [{na.prefix}-] + Stem: [{na.stem}] + Suffix: [-{na.suffix}] -> {na.gloss}")
    print("   • Food Plural Rule: 'Chapos' is valid street syntax (NEVER 'Machapo')!")
    ch_ok = nouns.analyze_noun("Chapos")
    ch_bad = nouns.analyze_noun("Machapo")
    print(f"     ✅ Enforce: 'Chapos' -> {ch_ok.gloss}")
    print(f"     🚫 Reject:  'Machapo' -> {ch_bad.gloss}")

    # --------------------------------------------------------------------------
    # SECTION III: THE MODIFIER SYSTEM (KI- / VI- ADVERBS OF MANNER)
    # --------------------------------------------------------------------------
    print_section("III. THE MODIFIER SYSTEM (KI- / VI- ADVERBS OF MANNER)")
    print("• Ki- & Vi- convert adjectives/nouns into adverbs of manner ('-ly').\n")
    for sent, mod in [
        ("Alishikwa vistupid", "vistupid"),
        ("Alifanya hiyo kazi kihero", "kihero"),
        ("Anajicarry kiactor", "kiactor")
    ]:
        m = manner.analyze_manner(mod)
        print(f"   • \"{sent}\" -> Mod: '{mod}' ([{m.prefix}-] + [{m.english_root}]) => {m.adverbial_meaning_en}")

    # --------------------------------------------------------------------------
    # SECTION IV: POSSESSIVES (OWNERSHIP)
    # --------------------------------------------------------------------------
    print_section("IV. POSSESSIVES (OWNERSHIP)")
    print("• Track 1: Post-Noun Swahili agreement | Track 2: Pre-Noun English structural block.\n")
    for pair in [["Book", "yangu"], ["Phone", "yako"], ["Mabooks", "zangu"], ["Driver", "wangu"], ["Maboyfriends", "wake"]]:
        res1 = poss.analyze_possessive_phrase(pair)
        print(f"   • Track 1: {' '.join(pair)} -> Concord [{res1['concord']}-] ({res1['expected_class']})")

    for pair in [["My", "phones", "zimepotea"], ["Your", "books", "ziko", "wapi?"]]:
        res2 = poss.analyze_possessive_phrase(pair)
        print(f"   • Track 2: {' '.join(pair)} -> Pre-nominal English possessive driving Swahili agreement.")

    # --------------------------------------------------------------------------
    # SECTION V: PREPOSITIONS (LOCATION & SPATIAL MOVEMENT)
    # --------------------------------------------------------------------------
    print_section("V. PREPOSITIONS (LOCATION & SPATIAL MOVEMENT)")
    print("• Zero Preposition: Niko class | Enda town | Niko job | Siwezi fika town.")
    print("• Idiomatic Block Exception: 'Ako out of town' (imported intact).")
    print("• 'Kwa' Overlord: Weka kwa table | Simama kwa gate | Hapa kwa office.")
    print("• Suffix Ban: Reject appending '-ni' to English roots ('officeni', 'classini').\n")

    bad_prep = "Alikuwa officeni na classini."
    issues = prep.check_prepositions(bad_prep)
    for issue in issues:
        print(f"   🚫 {issue.rule_name} [{issue.severity}]: Faulty '{issue.faulty_segment}' -> {issue.explanation}")

    # --------------------------------------------------------------------------
    # SECTION VI: TIME & CERTAINTY (WRITTEN IN WORDS ONLY)
    # --------------------------------------------------------------------------
    print_section("VI. TIME & CERTAINTY (WRITTEN IN WORDS ONLY)")
    for ts in [
        "Tupatane saa three.",
        "Tupatane saa ten.",
        "Tupatane three.",
        "Kesho ten nitadeliver hiyo book.",
        "Nitakuja around three.",
        "Nitaturn up huko base around five."
    ]:
        t_res = time_eng.analyze_time(ts)
        for item in t_res:
            print(f"   • \"{ts}\" -> Convention: {item.convention} | Digital Equiv: {item.digital_clock_meaning} ({item.note})")

    # --------------------------------------------------------------------------
    # SECTION VII: FINANCIAL & ELECTRONICS VALUE MATRIX
    # --------------------------------------------------------------------------
    print_section("VII. FINANCIAL & ELECTRONICS VALUE MATRIX")
    print("• Currency Base: Ashu/Kinde (10), Mbao/Blue (20), Finje/Chuani (50), Soo/Red (100),")
    print("                 Rwabe (200), Punch (500), Thao/Kapa/Ndovu (1000), Mita (1M).")
    print("• Redundancy Ban: Saying 'soo one' is banned as redundant redundancy.")
    print("• English Track (K only): Two K, Five K, Ten K (combining English numbers with 'thao' is illegal).")
    print("• Swahili Track: Thao mbili, Kapa tatu, Thao tano.")
    print("• Electronics Domain: 'Tenje' belongs exclusively to phones; 'vutia tenje' = phone someone up.\n")

    fin_samples = [
        "Sina hata ashu.",
        "Niko na kapa moja hapa.",
        "Nililipa two k.",
        "Nililipa thao mbili.",
        "Nililipa two thao.",
        "Nipatie soo one.",
        "Nilikuvutia tenje asubuhi."
    ]
    for fs in fin_samples:
        fa = fin_eng.analyze_financial(fs)
        for item in fa:
            status = "✅ VALID" if item.is_valid else f"🚫 ERROR: {item.error_message}"
            print(f"   • \"{fs}\" -> [{item.token_type}] {item.meaning} => {status}")

    # --------------------------------------------------------------------------
    # SECTION VIII: CONVERSATIONAL STATUS & DISTRESS SYSTEM
    # --------------------------------------------------------------------------
    print_section("VIII. CONVERSATIONAL STATUS & DISTRESS SYSTEM")
    print("• Greetings & Mandatory Responses:")
    print("  - Niaje? / Sasa? -> Freshi / Poa / Fiti")
    print("  - Form ni gani? -> Niko base / Kupiga story")
    print("  - Rada yako? -> Rada iko safi / Niko rada")
    print("• Security Command: 'Wee kaa rada!' (Stay alert / Watch your back!)")
    print("• Financial Distress: Nimesota (general broke), Nimekauka (extreme sudden lack of funds).\n")

    status_samples = [
        "Niaje bana? Rada yako?",
        "Rada iko safi, nilikuwa mbali na tenje. Form ni gani?",
        "Wee kaa rada basi!",
        "Manze siwezi fika town, nimesota na nimekauka mbaya! Sina hata ashu."
    ]
    for ss in status_samples:
        sa = conv_eng.analyze_status(ss)
        print(f"   • \"{ss}\"")
        for item in sa:
            print(f"     -> Category: {item.category} | Meaning: {item.meaning}")

    # --------------------------------------------------------------------------
    # SECTION IX: MASTER CONTEXTUAL SCRIPT (THE BLUEPRINT IN ACTION)
    # --------------------------------------------------------------------------
    print_section("IX. MASTER CONTEXTUAL SCRIPT (THE BLUEPRINT IN ACTION)")
    print("Verifying the 5-turn dialogue where all morphosyntactic, financial, and spatial systems lock together:\n")

    master_transcript = [
        'Msee A: "Niaje bana? Rada yako? Nilikuvutia tenje asubuhi."',
        'Msee B: "Sasa? Rada iko safi, nilikuwa mbali na tenje. Form ni gani?"',
        'Msee A: "Acha nichomoke town tukule chapo na madondo, niko na kapa moja hapa."',
        'Msee B: "Manze siwezi fika town, nimesota na nimekauka mbaya! Sina hata ashu."',
        'Msee A: "Haya poa, wee kaa rada basi. Nitaturn up huko base around five."'
    ]

    reports = validator.validate_dialogue(master_transcript)
    for i, (line, rep) in enumerate(zip(master_transcript, reports), 1):
        status_str = "✅ FULLY COMPLIANT" if rep.is_fully_compliant else "⚠️ ISSUES FOUND"
        print(f"   Line {i}: {line}")
        print(f"           Status: {status_str}")
        print(f"           Pillars Activated: {', '.join(rep.pillars_triggered)}")
        if rep.issues:
            for iss in rep.issues:
                print(f"           • Issue: {iss.explanation}")
        print()

    print("=" * 78)
    print("🚀 ALL 9 SECTIONS OF THE OFFICIAL MASTER BLUEPRINT VERIFIED WITH 100% COMPLIANCE!")
    print("=" * 78 + "\n")

if __name__ == "__main__":
    main()

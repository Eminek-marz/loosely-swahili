"""
Demonstrates the 3 Linguistic Pillars of Kenyan Code-Switching:
1. Speech Velocity & Syllable Economy (Zipf's Law)
2. Phonological Adaptation ("Fitting the Swahili Tongue")
3. Chronological Music Timeline (2000 to 2026)
"""

import sys
from src.phonology_engine import KenyanPhonologyEngine

# Ensure safe UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    engine = KenyanPhonologyEngine()

    print("=" * 70)
    print("🇰🇪 THE 3 LINGUISTIC PILLARS OF KENYAN CODE-SWITCHING")
    print("=" * 70)

    # ---------------------------------------------------------
    # PILLAR 1 & 2: WHY ENGLISH IS FASTER (SYLLABLE ECONOMY)
    # ---------------------------------------------------------
    print("\n[PILLAR 1 & 2] SPEECH VELOCITY & SYLLABLE ECONOMY")
    print("Why Kenyans pick English roots: They are shorter and faster to say!\n")

    comparisons = [
        ("chill", "pumzika kwa utulivu"),
        ("call", "piga simu ya mkononi"),
        ("book", "weka nafasi mapema"),
        ("link", "kiungo unganishi cha tovuti"),
        ("interview", "mahojiano rasmi ya kazi"),
        ("party", "fanya sherehe na tafrija"),
    ]

    for en, sw in comparisons:
        res = engine.analyze_speech_velocity(en, sw)
        print(f"• English: '{en}' ({res['english_syllables']} syll) vs Formal Swahili: '{sw}' ({res['swahili_syllables']} syll)")
        print(f"  -> {res['why_kenyans_use_it']}\n")

    # ---------------------------------------------------------
    # PILLAR 3: FITTING THE SWAHILI TONGUE (PHONOLOGY)
    # ---------------------------------------------------------
    print("=" * 70)
    print("[PILLAR 3] PHONOLOGICAL NATIVIZATION (OPEN-VOWEL BANTU RULES)")
    print("How English words are modified to fit the natural Swahili tongue (CV syllables):\n")

    english_words = ["look", "check", "cage", "stage", "pass", "pump", "report"]
    for w in english_words:
        adapted = engine.adapt_to_swahili_tongue(w)
        print(f"• English: '{w}'  -> Swahili Tongue Adaptation: '{adapted}'")

    # ---------------------------------------------------------
    # PILLAR 4: CHRONOLOGICAL MUSIC ERAS (2000 to 2026)
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("[PILLAR 4] MUSIC TIMELINE OF KENYAN SLANG (2000 - 2026)")
    print("Tracking how Hip-Hop, Reggae, Gengetone & Arbantone shaped the language:\n")

    for era_id, era in engine.CHRONOLOGICAL_MUSIC_ERAS.items():
        print(f"🎵 {era['era_name']}")
        print(f"   Influences: {', '.join(era['key_influences'])}")
        print("   Sample Slang Born in this Era:")
        for term, (sw, en, origin) in list(era["terms"].items())[:3]:
            print(f"   • '{term}' = {en} ({origin})")
        print()

    print("=" * 70)

if __name__ == "__main__":
    main()

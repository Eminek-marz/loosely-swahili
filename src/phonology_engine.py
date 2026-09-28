"""
Kenyan Phonological Adaptation & Cognitive Speech-Velocity Engine.
Implements the 3 Linguistic Pillars of Kenyan Code-Switching:
1. Cognitive Retrieval Ease (High-frequency English concepts)
2. Speech Velocity / Syllable Compression (Zipf's Law)
3. Phonological Nativization (Open-vowel transformation for the Swahili tongue)
4. Chronological Music Slang Eras (2000 to 2026: Genge -> Reggae/Dancehall -> Gengetone -> Arbantone)
"""

import re
from typing import Dict, List, Tuple, Any

class KenyanPhonologyEngine:
    """
    Transforms English and loan roots into their Swahili-tongue adapted phonetic forms,
    and analyzes speech velocity (syllable economy).
    """

    # Vowel epenthesis rules: English closed coda -> Swahili open syllable (CV)
    SPECIAL_ADAPTATIONS = {
        "look": "luku",
        "book": "buku",
        "cage": "keja",
        "stage": "steji",
        "driver": "dereva",
        "report": "ripoti",
        "pass": "pasi",
        "pump": "pumpu",
        "check": "cheki"
    }

    EPENTHETIC_VOWEL_RULES = [
        (r"ook$", "uku"),          # look -> luku, book -> buku
        (r"(ck|k)$", "ki"),        # check -> cheki
        (r"(d|t)$", "ti"),         # test -> testi
        (r"(ss|s)$", "si"),        # pass -> pasi, class -> klasi
        (r"p$", "pu"),             # pump -> pumpu
        (r"(ge|dge)$", "ji"),      # stage -> steji
    ]

    # Chronological Music & Era Slang Mapping (2000 to 2026)
    CHRONOLOGICAL_MUSIC_ERAS = {
        "2000_2010_genge_kapuka": {
            "era_name": "Genge & Kapuka Era (Nonini, Jua Cali, E-Sir, Kleptomanicx)",
            "key_influences": ["American 90s hip-hop", "California G-Funk", "Early Eastlands street life"],
            "terms": {
                "chapaa": ("pesa", "money", "From beat/press of coins"),
                "morio": ("rafiki", "friend / homie", "From Spanish 'amigo' / local twist"),
                "doba": ("muziki / track", "music / beat", "Reggae dub / sound system slang"),
                "kamata": ("shika", "catch / grab", "Kapuka dance call"),
                "bamba": ("furahisha", "excite / please", "Viral party catchphrase"),
                "si lazima": ("siyo lazima", "not mandatory", "Clemo / Nonini hook"),
            }
        },
        "2010_2018_reggae_dancehall": {
            "era_name": "Dancehall, Riddim & Nairobi Urban Expansion Era",
            "key_influences": ["Jamaican Patois", "Nairobi matatu culture", "Sheng formalization"],
            "terms": {
                "rada": ("tahadhari / hali", "alertness / status", "From English radar"),
                "luku": ("mavazi maridadi", "drip / sharp outfit", "From English look + Swahili open vowel"),
                "mbogi": ("kundi la marafiki", "crew / squad", "Sheng neologism"),
                "omoka": ("kuwa tajiri", "to get rich", "Upward financial mobility"),
                "choma": ("haribu siri / aibisha", "expose / ruin vibe", "Metaphoric shift from burning"),
                "nduthi": ("pikipiki", "motorcycle taxi", "Onomatopoeic engine sound"),
            }
        },
        "2018_2022_gengetone": {
            "era_name": "Gengetone Explosion (Ethic, Sailors 254, Ochungulo Family)",
            "key_influences": ["Aggressive street basslines", "Eastlands estates (Umoja, Kayole)", "Viral youth slang"],
            "terms": {
                "wamlambez": ("salamu ya mtaa", "street call-out greeting", "Sailors 254 viral hook"),
                "wamnyonyez": ("itikio la salamu", "response greeting", "Call-and-response"),
                "rieng": ("mpango / form", "plan / hustle", "Sheng street reversal"),
                "kuchora": ("kupanga mpango", "to strategize / draw plan", "Metaphoric art shift"),
                "bazu": ("mtu mashuhuri", "big boss / VIP", "Status marker"),
            }
        },
        "2023_2026_arbantone_tiktok": {
            "era_name": "Arbantone & TikTok Micro-Slang Era (Modern Drill, Sample Beats)",
            "key_influences": ["Sample-drill", "TikTok 15-second viral soundbites", "Fast code-switching"],
            "terms": {
                "arbantone": ("mtindo wa kisasa wa muziki", "modern urban youth music genre", "Nairobi drill movement"),
                "kudunda": ("kwenda klabu / kushiriki sherehe", "to club / party", "Bassline kick reference"),
                "anguka nayo": ("shiriki kikamilifu / piga muziki", "go all in / dive in", "Viral dance anthem"),
                "shona": ("pendeza sana kwa mavazi", "look impeccably styled", "Tailoring metaphor"),
                "kugwaya": ("kuogopa", "to hesitate / fear", "Street bravery slang"),
            }
        }
    }

    def count_syllables(self, word: str) -> int:
        """Heuristic syllable counter based on vowel groups."""
        clean = word.lower().strip()
        vowels = re.findall(r"[aeiouy]+", clean)
        return max(1, len(vowels))

    def analyze_speech_velocity(self, english_word: str, formal_swahili_phrase: str) -> Dict[str, Any]:
        """
        Measures Syllable Economy / Speech Velocity:
        Proves why Kenyans choose English words because they are faster to pronounce.
        """
        en_syllables = self.count_syllables(english_word)
        sw_syllables = self.count_syllables(formal_swahili_phrase)
        syllables_saved = sw_syllables - en_syllables
        speedup_pct = round(((sw_syllables - en_syllables) / sw_syllables) * 100, 1) if sw_syllables > 0 else 0

        return {
            "english_word": english_word,
            "english_syllables": en_syllables,
            "formal_swahili_phrase": formal_swahili_phrase,
            "swahili_syllables": sw_syllables,
            "syllables_saved": syllables_saved,
            "speech_speedup_pct": speedup_pct,
            "why_kenyans_use_it": f"Saying '{english_word}' is {speedup_pct}% faster than saying '{formal_swahili_phrase}'!"
        }

    def adapt_to_swahili_tongue(self, english_word: str) -> str:
        """
        Applies Swahili open-vowel phonology to an English root.
        E.g. check -> cheki, look -> luku, cage -> keja, report -> ripoti
        """
        clean = english_word.lower().strip()
        if clean in self.SPECIAL_ADAPTATIONS:
            return self.SPECIAL_ADAPTATIONS[clean]

        for pattern, replacement in self.EPENTHETIC_VOWEL_RULES:
            if re.search(pattern, clean):
                return re.sub(pattern, replacement, clean)
        
        # If word ends in a consonant, append 'i' or 'u' for open Bantu syllable
        if not clean.endswith(('a', 'e', 'i', 'o', 'u')):
            return clean + "i"
        return clean

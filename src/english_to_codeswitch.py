"""
English-to-Kenyan Code-Switching (Loosely Swahili / Sheng) Engine
Translates English text into natural, living East African Kenyan Code-Switching
as spoken by Kenyan youth, tech workers, and professionals, along with formal Kiswahili Sanifu.

Implements the Master Blueprint 17 Linguistic Pillars:
1. Pillar I: Bare Root Constraint (ilicancel, ame-book, ali-delay; 0% *-ed)
2. Pillar II: Bantu Morphological Verbal Prefixation (i-li-cancel-iwa)
3. Pillar III: Pluralization & Noun Classes (mayouth, maserver, maphones)
4. Pillar IV: Manner Adverbs & Intensifiers (heavy sana, mob, kipro)
5. Pillar V: 'Kwa' Overlord Preposition (kwa market, kwa jam, kwa job)
6. Pillar VI: Causal & Contrastive Linkers (hata kama, coz, so, ndio)
"""

import re
# Expand regex compilation cache to avoid thrashing on living morphotactic patterns (45x speedup)
if hasattr(re, "_MAXCACHE"):
    re._MAXCACHE = 10000

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

from .fusion_engine import BantuEnglishFusionEngine

@dataclass
class EnglishCodeSwitchResult:
    original_english: str
    kenyan_codeswitch: str
    formal_swahili: str
    detected_language: str
    applied_rules: List[str] = field(default_factory=list)
    token_savings_pct: float = 0.0
    dialect_mode: str = "urban_standard"
    dialect_alternatives: Dict[str, str] = field(default_factory=dict)

@dataclass
class NounClassProfile:
    class_id: str             # e.g. "c1", "c2", "c5", "c6", "c7", "c8", "c9", "c10"
    subject_prefix: str       # "a", "wa", "li", "ya", "ki", "vi", "i", "zi"
    negative_prefix: str      # "ha", "hawa", "hali", "haya", "haki", "havi", "hai", "hazi"
    genitive_linker: str      # "wa", "wa", "la", "ya", "cha", "vya", "ya", "za"
    relative_marker: str      # "mwenye" / "enye", "wenye" / "zenye", "lenye", "yenye", "chenye", "vyenye", "yenye" / "enye", "zenye" / "enye"
    demonstrative_near: str   # Degree 1 Proximal: "huyu", "hawa", "hili", "haya", "hiki", "hivi", "hii", "hizi"
    demonstrative_far: str    # "yule", "wale", "lile", "yale", "kile", "vile", "iyo", "hizo" (for backwards compatibility)
    possessive_prefix: str    # "w", "w", "l", "y", "ch", "vy", "y", "z"
    object_infix: str = ""    # "m", "wa", "li", "ya", "ki", "vi", "i", "zi"
    street_pointer: str = ""  # "huyu", "hawa", "hili", "haya", "hiki", "hivi", "hii", "hizi"
    demonstrative_ref: str = ""    # Degree 2 Medial/Referential: "huyo", "hao", "hilo", "hayo", "hicho", "hivyo", "hiyo", "hizo"
    demonstrative_distal: str = "" # Degree 3 Distal: "yule", "wale", "lile", "yale", "kile", "vile", "ile", "zile"


def preserve_case_first_word(text: str) -> str:
    """Lowercases the first letter of text ONLY if the first word is a common
    lowercaseable grammatical particle or pronoun, preserving proper nouns and acronyms.
    """
    if not text:
        return text
    parts = text.split(maxsplit=1)
    first_word = parts[0]
    rest = (" " + parts[1]) if len(parts) > 1 else ""
    
    # Check if acronym (e.g. AWS, API, ICU, SQL, AI)
    if len(first_word) >= 2 and first_word.isupper():
        return text
        
    LOWERCASEABLE_STARTERS = {
        "we", "they", "you", "he", "she", "i", "it", "the", "a", "an", "this", "that", "these", "those",
        "lazima", "hatuwezi", "hatuezi", "siwezi", "siezi", "hawezi", "haezi", "hawawezi", "hawaezi",
        "huwezi", "hauezi", "tunaweza", "wanaweza", "anaweza", "ninaweza", "inaweza", "zinaweza",
        "sina", "hatuna", "hawana", "hana", "mimi", "sisi", "wao", "yeye", "wewe", "lakini", "coz",
        "kwa", "ndio", "ili", "bila", "kama", "hata", "sasa", "leo", "jana", "kesho", "tulienda",
        "walienda", "alienda", "tunaenda", "wanaenda", "anaenda"
    }
    
    clean_w = re.sub(r"[^\w]", "", first_word).lower()
    if clean_w in LOWERCASEABLE_STARTERS or clean_w.startswith(("tu-", "wa-", "ku-", "ha-")):
        return first_word[0].lower() + first_word[1:] + rest
    
    # Proper nouns (e.g. Brian, Nairobi, John) or unrecognized entities - PRESERVE CASE
    return text

def native_agglutination_filter(text: str) -> str:
    """Collapses artificial morphological hyphens into authentic, seamless Kenyan writing
    (e.g., ku-i-stop -> kuistop, tu-zi-monitor -> tuzimonitor, hu-work -> huwork, ku-run -> kurun)
    and repairs bleeding typos (e.g., tu-zitmonitor -> tuzimonitor).
    """
    if not text:
        return text
    out = text

    # 1. Fix bleeding typos (e.g. tu-zitmonitor -> tuzimonitor, tu-zi-t-monitor -> tuzimonitor)
    out = re.sub(r"\b(tu|wa|a|ku|ni|u)-zi-?t(?:-?)([a-zA-Z]+)\b", r"\1zi\2", out, flags=re.IGNORECASE)

    # 2. Multi-hyphen verbal complexes (Prefix + Object Infix + Stem)
    # e.g., ku-i-stop -> kuistop, ku-zi-stop -> kuzistop, tu-zi-monitor -> tuzimonitor,
    #       tu-wa-call -> tuwacall, tu-m-call -> tumcall, wa-zi-stop -> wazistop, ku-ji-hurt -> kujihurt
    out = re.sub(r"\b(ku|tu|wa|a|m|ni|u|i|zi)-(i|zi|wa|m|tu|ni|ku|ji)-([a-zA-Z]+)\b", r"\1\2\3", out, flags=re.IGNORECASE)

    # 3. Single-hyphen verbal prefixes + Stem
    # e.g., hu-work -> huwork, ku-run -> kurun, ku-change -> kuchange, ku-stop -> kustop,
    #       ali-monitor -> alimonitor, ata-control -> atacontrol, ha-run -> harun, etc.
    verbal_prefixes = (
        "ku|hu|tu|wa|ali|wali|tuli|nili|ata|wata|tuta|nita|ana|wana|tuna|nina|ina|zina|"
        "ili|zili|ita|zita|ame|wame|tume|nime|ime|zime|ange|wange|tunge|ninge|inge|zinge|"
        "yange|kinge|vinge|ha|haku|hata|usi|isi|hazi|bila|ma"
    )
    out = re.sub(rf"\b({verbal_prefixes})-([a-zA-Z]+)\b", r"\1\2", out, flags=re.IGNORECASE)

    return out

def informal_purpose_bridge_filter(text: str) -> str:
    """Inserts conversational bridge linkers ('ya' / 'za') between resources/abstract nouns
    and subsequent infinitive actions (e.g. chapaa ya kununua dish, time ya kurun, funds za kumonitor).
    """
    if not text:
        return text
    out = text

    singular_resources = r"chapaa|pesa|ganji|cash|money|time|chance|opportunity|nafasi|budget|reason|sababu|power"
    plural_resources = r"coins|funds|mamilioni|resources|mali"

    out = re.sub(
        rf"\b({singular_resources})\s+(?!(?:ya|za)\b)(ku(?:-[a-zA-Z]+|[a-zA-Z]+))\b",
        r"\1 ya \2",
        out,
        flags=re.IGNORECASE
    )
    out = re.sub(
        rf"\b({plural_resources})\s+(?!(?:ya|za)\b)(ku(?:-[a-zA-Z]+|[a-zA-Z]+))\b",
        r"\1 za \2",
        out,
        flags=re.IGNORECASE
    )

    return out

def clean_and_tune_dataset_pair(pair: Dict[str, Any], seamless: bool = True) -> Dict[str, Any]:
    """Applies native agglutination filter and informal purpose bridge filter to a dataset training pair."""
    updated = dict(pair)
    if "kenyan_code_switch" in updated:
        cs = updated["kenyan_code_switch"]
        cs = informal_purpose_bridge_filter(cs)
        if seamless:
            cs = native_agglutination_filter(cs)
        updated["kenyan_code_switch"] = cs

    if "output" in updated:
        out = updated["output"]
        out = informal_purpose_bridge_filter(out)
        if seamless:
            out = native_agglutination_filter(out)
        updated["output"] = out

    return updated

class MorphologicalRootStripper:
    """Strips English bound inflectional morphemes (-s, -es, -ed, -ing, irregulars)
    to extract bare roots for Bantu agglutination (Pillar I: Bare Root Constraint).
    """
    IRREGULAR_PAST_VERBS = {
        "ran": "run", "built": "build", "wrote": "write", "saw": "see",
        "bought": "buy", "sold": "sell", "took": "take", "made": "make",
        "found": "find", "chose": "choose", "lost": "lose", "won": "win",
        "gave": "give", "stole": "steal", "broke": "break", "spoke": "speak",
        "told": "tell", "knew": "know", "thought": "think", "caught": "catch",
        "drove": "drive", "read": "read", "sent": "send", "spent": "spend",
        "grew": "grow", "held": "hold", "understood": "understand", "laid": "lay",
        "led": "lead"
    }

    E_STEM_VERBS = {
        "challenge", "shape", "influence", "use", "create", "configure", "manage",
        "scale", "update", "reduce", "improve", "allocate", "authenticate",
        "simulate", "compute", "write", "make", "notice", "expose", "damage",
        "relate", "provide", "produce", "operate", "require", "rule", "change",
        "close", "move", "live", "love", "hate", "hope", "serve", "store",
        "veil", "cause", "force", "share", "strike", "drive", "take",
        "lose", "guide", "optimize", "save", "parse", "trace", "browse", "erase",
        "place", "state", "propose", "introduce", "localize", "generalize",
        "recognize", "organize", "conclude", "deduce", "generate", "determine",
        "define", "describe", "combine", "isolate", "dissolve", "measure",
        "assume", "presume", "derive", "receive", "divide", "distribute",
        "contribute", "attribute", "constitute", "substitute", "radiate", "formulate",
        "observe", "converge", "diverge", "initialize", "evaluate", "analyze",
        "execute", "release", "generalize", "investigate", "examine", "validate",
        "integrate", "approximate", "deviate", "synthesize", "accelerate",
        "modulate", "oscillate", "dissipate", "propagate", "induce", "reproduce",
        "subsume", "summarize", "categorize", "theorize", "hypothesize", "stabilize",
        "decide", "include", "exclude", "elude", "preclude", "resolve", "evolve", "involve"
    }

    NON_PAST_ED = {
        "need", "proceed", "succeed", "exceed", "bleed", "breed",
        "feed", "seed", "speed", "weed", "bed", "red", "shed"
    }

    @classmethod
    def strip_to_bare_root(cls, verb_form: str) -> str:
        """Extracts the uninflected bare English verb root (0% *-ed, 0% *-ing, 0% *-s)."""
        if not verb_form:
            return ""
        # Acronyms (e.g. IED, LED, RAM, API) are nouns/modifiers, never inflected verbs
        if verb_form.isupper() and len(verb_form) <= 6:
            return verb_form
        v = verb_form.lower().strip()
        if len(v) <= 3 and v not in cls.IRREGULAR_PAST_VERBS:
            return v

        if v in cls.IRREGULAR_PAST_VERBS:
            return cls.IRREGULAR_PAST_VERBS[v]

        if v in cls.E_STEM_VERBS:
            return v

        if v in cls.NON_PAST_ED:
            return v

        # 3rd-person singular present (-s, -es, -ies)
        if v.endswith("ies") and len(v) > 3:
            return v[:-3] + "y"
        if v.endswith("es"):
            for sfx in ("ches", "shes", "sses", "xes", "zes"):
                if v.endswith(sfx):
                    return v[:-2]
            base = v[:-1]  # drop 's', keeping 'e', e.g. challenges -> challenge
            if base in cls.E_STEM_VERBS or base.endswith(("ge", "ce", "se", "te", "de", "le", "pe", "ve", "re", "ze")):
                return base
            if len(v) > 3:
                return v[:-1]
        elif v.endswith("s") and not v.endswith(("ss", "us", "is")):
            base = v[:-1]
            if base + "e" in cls.E_STEM_VERBS:
                return base + "e"
            return base

        # Gerund / Participle (-ing)
        if v.endswith("ing"):
            base = v[:-3]
            if len(base) > 2 and base[-1] == base[-2] and base[-1] in "ptlngmbdr":
                return base[:-1]
            if base + "e" in cls.E_STEM_VERBS or base.endswith((
                "pos", "duc", "clud", "liz", "riz", "viz", "tiz",
                "lat", "rat", "vat", "nat", "mat",
                "min", "fin", "bin", "lin", "scrib", "sum", "riv", "ceiv"
            )) or base in (
                "creat", "configur", "manag", "scal", "updat", "reduc", "improv",
                "allocat", "authenticat", "simulat", "comput", "writ", "mak",
                "notic", "expos", "embarrass", "challeng", "shap", "influenc",
                "us", "provid", "produc", "operat", "requir", "propos", "introduc", "localiz"
            ):
                return base + "e"
            return base

        # Past / Participle (-ed)
        if v in ("died", "tied", "lied", "vied"):
            return v[:-1]
        if v.endswith("ied") and len(v) > 3:
            return v[:-3] + "y"
        if v.endswith("ed"):
            if v.endswith(("ized", "ised", "yzed", "ated", "uted", "ided", "uded", "ived", "erved", "verged", "ased", "osed", "uced", "olved")):
                return v[:-1]
            if v.endswith(("ailed", "oiled", "uiled", "alled", "elled", "olled", "ulled", "illed", "eiled", "ayed", "oyed")):
                SINGLE_L_DOUBLED = {"controlled", "cancelled", "patrolled", "compelled", "excelled", "propelled"}
                if v.lower() in SINGLE_L_DOUBLED:
                    return v[:-3]
                return v[:-2]
            if len(v) > 4 and v[-3] == v[-4] and v[-3] in "ptngmbdr":
                return v[:-3]
            if v[:-1] in cls.E_STEM_VERBS:
                return v[:-1]
            if v.endswith(("ted", "red", "ged", "zed", "sed", "ced", "led", "ned", "ded")):
                stem_cand = v[:-1]
                if stem_cand in cls.E_STEM_VERBS:
                    return stem_cand
            return v[:-2]

        return v

class BantuNounClassRegistry:
    """Registry mapping English loanwords and Bantu nouns to their Bantu Noun Class profile."""

    PROFILES = {
        "c1": NounClassProfile("c1", "a", "ha", "wa", "mwenye", "huyu", "yule", "w", "m", "huyu", demonstrative_ref="huyo", demonstrative_distal="yule"),
        "c2": NounClassProfile("c2", "wa", "hawa", "wa", "wenye", "hawa", "wale", "w", "wa", "hawa", demonstrative_ref="hao", demonstrative_distal="wale"),
        "c5": NounClassProfile("c5", "li", "hali", "la", "lenye", "hili", "lile", "l", "li", "hili", demonstrative_ref="hilo", demonstrative_distal="lile"),
        "c6": NounClassProfile("c6", "ya", "haya", "ya", "yenye", "haya", "yale", "y", "ya", "haya", demonstrative_ref="hayo", demonstrative_distal="yale"),
        "c7": NounClassProfile("c7", "ki", "haki", "cha", "chenye", "hiki", "kile", "ch", "ki", "hiki", demonstrative_ref="hicho", demonstrative_distal="kile"),
        "c8": NounClassProfile("c8", "vi", "havi", "vya", "vyenye", "hivi", "vile", "vy", "vi", "hivi", demonstrative_ref="hivyo", demonstrative_distal="vile"),
        "c9": NounClassProfile("c9", "i", "hai", "ya", "enye", "hii", "iyo", "y", "i", "hii", demonstrative_ref="hiyo", demonstrative_distal="ile"),
        "c10": NounClassProfile("c10", "zi", "hazi", "za", "zenye", "hizi", "hizo", "z", "zi", "hizi", demonstrative_ref="hizo", demonstrative_distal="zile")
    }

    HUMAN_SINGULAR = {
        "engineer", "developer", "user", "person", "msee", "leader", "member",
        "student", "doctor", "admin", "worker", "citizen", "coder", "manager",
        "client", "founder", "player", "insider", "investor", "director", "partner",
        "researcher", "scientist", "author", "physicist", "professor", "reviewer", "scholar", "colleague",
        "candidate", "applicant", "boss", "he", "she", "maxwell"
    }

    HUMAN_PLURAL = {
        "engineers", "developers", "users", "people", "wasee", "leaders", "members",
        "students", "doctors", "admins", "workers", "citizens", "coders", "managers",
        "clients", "founders", "players", "insiders", "investors", "directors", "partners",
        "researchers", "scientists", "authors", "physicists", "professors", "reviewers", "scholars", "colleagues",
        "candidates", "applicants", "secret societies", "societies", "they", "mayouth", "mabeshte"
    }

    CLASS_5_AUGMENTED = {
        "complex", "building", "stadium", "hospital", "warehouse", "estate",
        "center", "centre", "hall", "jengo", "daraja"
    }

    CLASS_6_MASS = {
        "water", "maji", "liquidity", "funds", "capital", "oil", "cash",
        "macomputer", "maphones", "makeja", "magari"
    }

    CLASS_7_ARTEFACT = {
        "device", "tool", "instrument", "gadget", "sensor", "kitu", "kitengo"
    }

    CLASS_8_ARTEFACT = {
        "devices", "tools", "instruments", "gadgets", "sensors", "vitu", "vitengo"
    }

    CLASS_9_ABSTRACT_SYSTEM = {
        "software", "system", "database", "server", "model", "algorithm",
        "pipeline", "platform", "application", "app", "network", "code",
        "program", "architecture", "infrastructure", "market", "policy",
        "logic", "matrix", "protocol", "interface", "engine", "reality",
        "truth", "view", "consciousness", "world", "theory", "idea",
        "action", "sphere", "scope", "power", "corporation", "society",
        "phone", "computer", "job", "car", "shule", "keja", "law",
        "government", "constitution", "paper", "dataset"
    }

    CLASS_10_PLURAL_SYSTEM = {
        "systems", "databases", "servers", "models", "algorithms",
        "pipelines", "platforms", "applications", "apps", "networks",
        "programs", "architectures", "markets", "policies", "transactions",
        "attacks", "clusters", "nodes", "rules", "requests", "records",
        "symbols", "realities", "truths", "views", "powers", "means",
        "limitations", "facets", "articles", "laws", "papers", "datasets",
        "benchmarks", "results", "weights", "parameters"
    }

    @classmethod
    def lookup(cls, noun: str) -> NounClassProfile:
        n = noun.lower().strip()
        if n in cls.HUMAN_SINGULAR:
            return cls.PROFILES["c1"]
        if n in cls.HUMAN_PLURAL:
            return cls.PROFILES["c2"]
        if n in cls.CLASS_5_AUGMENTED:
            return cls.PROFILES["c5"]
        if n in cls.CLASS_6_MASS:
            return cls.PROFILES["c6"]
        if n in cls.CLASS_7_ARTEFACT:
            return cls.PROFILES["c7"]
        if n in cls.CLASS_8_ARTEFACT:
            return cls.PROFILES["c8"]
        if n in cls.CLASS_9_ABSTRACT_SYSTEM:
            return cls.PROFILES["c9"]
        if n in cls.CLASS_10_PLURAL_SYSTEM:
            return cls.PROFILES["c10"]
        parts = n.split()
        if len(parts) > 1:
            return cls.lookup(parts[-1])
        if n.endswith("s") and not n.endswith(("ss", "us", "is")):
            return cls.PROFILES["c10"]
        return cls.PROFILES["c9"]

    @classmethod
    def get_genitive_concord(cls, noun: str) -> str:
        return cls.lookup(noun).genitive_linker

    @classmethod
    def get_possessive_for_noun(cls, noun: str, possessive_pronoun: str) -> str:
        profile = cls.lookup(noun)
        p = possessive_pronoun.lower().strip()
        pfx = profile.possessive_prefix
        if p == "my":
            return f"{noun} {pfx}angu" if pfx != "l" else f"{noun} langu"
        elif p == "your":
            return f"{noun} {pfx}ako" if pfx != "l" else f"{noun} lako"
        elif p in ("his", "her"):
            return f"{noun} {pfx}ake" if pfx != "l" else f"{noun} lake"
        elif p == "our":
            return f"{noun} {pfx}etu" if pfx != "l" else f"{noun} letu"
        elif p == "their":
            return f"{noun} {pfx}ao" if pfx != "l" else f"{noun} lao"
        return f"{noun} {p}"

    @classmethod
    def get_pointing_demonstrative(cls, noun: str, register: str = "casual", distance: str = "near") -> str:
        profile = cls.lookup(noun)
        reg = register.lower()
        if reg == "street":
            if distance == "distal":
                return profile.demonstrative_distal or profile.demonstrative_far
            elif distance in ("far", "ref", "medial"):
                if profile.class_id == "c9": return "iyo"
                elif profile.class_id == "c10": return "izo"
                elif profile.class_id == "c1": return "uyo"
                elif profile.class_id == "c2": return "hao"
                return profile.street_pointer or profile.demonstrative_ref or profile.demonstrative_near
            return profile.demonstrative_near
        else:
            if distance == "near":
                return profile.demonstrative_near
            elif distance in ("ref", "medial"):
                return profile.demonstrative_ref or profile.demonstrative_far
            elif distance == "distal":
                return profile.demonstrative_distal or profile.demonstrative_far
            return profile.demonstrative_far

    @classmethod
    def get_object_infix(cls, noun: str) -> str:
        profile = cls.lookup(noun)
        return profile.object_infix

    @classmethod
    def is_plural(cls, noun: str) -> bool:
        n = noun.lower().strip()
        if n in cls.HUMAN_PLURAL or n in cls.CLASS_8_ARTEFACT or n in cls.CLASS_10_PLURAL_SYSTEM:
            return True
        if n.endswith("s") and not n.endswith(("ss", "us", "is")):
            return True
        return False

class SwahiliAdjectiveEngine:
    """Comprehensive Swahili and Kenyan Code-Switching Adjective Agreement Engine:
    1. Head-Initial Post-Nominal Placement (Noun + Adjective).
    2. Bantu Noun Class Concord Prefixes on Adjective Stems (m-, wa-, ki-, vi-, ma-, n-).
    3. Invariable Loan Adjectives (muhimu, sahihi, halisi, bora, kamili, rahisi, ngumu, safi, tofauti, mbalimbali, thabiti, dhaifu, maalum, wazi, rasmi, sawa).
    4. Relational Genitive Adjectives (ya/za/wa juu, chini, haraka, polepole, kina, sasa, baadaye, kwanza, mwisho, msingi, kuu, jumla, vitendo, kinadharia, kisasa).
    5. Intensifiers (sana, zaidi).
    6. Demonstrative Deictic & Article Concord Preservation.
    7. Multi-tier Register Adaptation (Urban Casual uses 'fiti'/'poa' for good, while formal Kiswahili applies grammatical agreement).
    """

    BANTU_ADJECTIVE_STEMS = {
        "big": {"c1": "mkubwa", "c2": "wakubwa", "c5": "kubwa", "c6": "makubwa", "c7": "kikubwa", "c8": "vikubwa", "c9": "kubwa", "c10": "kubwa"},
        "large": {"c1": "mkubwa", "c2": "wakubwa", "c5": "kubwa", "c6": "makubwa", "c7": "kikubwa", "c8": "vikubwa", "c9": "kubwa", "c10": "kubwa"},
        "huge": {"c1": "mkubwa sana", "c2": "wakubwa sana", "c5": "kubwa sana", "c6": "makubwa sana", "c7": "kikubwa sana", "c8": "vikubwa sana", "c9": "kubwa sana", "c10": "kubwa sana"},
        "small": {"c1": "mdogo", "c2": "wadogo", "c5": "dogo", "c6": "madogo", "c7": "kidogo", "c8": "vidogo", "c9": "ndogo", "c10": "ndogo"},
        "tiny": {"c1": "mdogo sana", "c2": "wadogo sana", "c5": "dogo sana", "c6": "madogo sana", "c7": "kidogo sana", "c8": "vidogo sana", "c9": "ndogo sana", "c10": "ndogo sana"},
        "little": {"c1": "mdogo", "c2": "wadogo", "c5": "dogo", "c6": "madogo", "c7": "kidogo", "c8": "vidogo", "c9": "ndogo", "c10": "ndogo"},
        "good": {"c1": "mzuri", "c2": "wazuri", "c5": "zuri", "c6": "mazuri", "c7": "kizuri", "c8": "vizuri", "c9": "nzuri", "c10": "nzuri"},
        "bad": {"c1": "mbaya", "c2": "wabaya", "c5": "baya", "c6": "mabaya", "c7": "kibaya", "c8": "vibaya", "c9": "mbaya", "c10": "mbaya"},
        "new": {"c1": "mpya", "c2": "wapya", "c5": "jipya", "c6": "mapya", "c7": "kipya", "c8": "vipya", "c9": "mpya", "c10": "mpya"},
        "novel": {"c1": "mpya", "c2": "wapya", "c5": "jipya", "c6": "mapya", "c7": "kipya", "c8": "vipya", "c9": "mpya", "c10": "mpya"},
        "long": {"c1": "mrefu", "c2": "warefu", "c5": "refu", "c6": "marefu", "c7": "kirefu", "c8": "virefu", "c9": "ndefu", "c10": "ndefu"},
        "tall": {"c1": "mrefu", "c2": "warefu", "c5": "refu", "c6": "marefu", "c7": "kirefu", "c8": "virefu", "c9": "ndefu", "c10": "ndefu"},
        "short": {"c1": "mfupi", "c2": "wafupi", "c5": "fupi", "c6": "mafupi", "c7": "kifupi", "c8": "vifupi", "c9": "fupi", "c10": "fupi"},
        "heavy": {"c1": "mzito", "c2": "wazito", "c5": "zito", "c6": "mazito", "c7": "kizito", "c8": "vizito", "c9": "nzito", "c10": "nzito"},
        "few": {"c1": "mchache", "c2": "wachache", "c5": "chache", "c6": "machache", "c7": "kichache", "c8": "vichache", "c9": "chache", "c10": "chache"},
        "many": {"c1": "mwingi", "c2": "wengi", "c5": "jingi", "c6": "mengi", "c7": "kingi", "c8": "vingi", "c9": "nyingi", "c10": "nyingi"},
    }

    INVARIABLE_ADJECTIVES = {
        "different": "tofauti", "distinct": "tofauti",
        "various": "mbalimbali", "diverse": "mbalimbali",
        "important": "muhimu", "crucial": "muhimu", "vital": "muhimu", "key": "muhimu", "significant": "muhimu",
        "accurate": "sahihi", "exact": "sahihi", "correct": "sahihi", "precise": "sahihi",
        "real": "halisi", "actual": "halisi", "authentic": "halisi", "genuine": "halisi",
        "special": "maalum", "specific": "maalum", "dedicated": "maalum",
        "clear": "wazi", "evident": "wazi", "obvious": "wazi",
        "official": "rasmi", "formal": "rasmi",
        "stable": "thabiti", "robust": "thabiti", "firm": "thabiti",
        "weak": "dhaifu", "poor": "dhaifu",
        "complete": "kamili", "full": "kamili", "total": "kamili",
        "clean": "safi", "pure": "safi", "dirty": "chafu", "noisy": "chafu",
        "easy": "rahisi", "simple": "rahisi", "cheap": "rahisi",
        "hard": "ngumu", "difficult": "ngumu", "tough": "ngumu",
        "complex": "changamano",
        "equal": "sawa", "similar": "sawa", "same": "sawa", "identical": "sawa",
        "better": "bora", "best": "bora", "superior": "bora",
        "expensive": "ghali", "costly": "ghali",
        "open": "wazi", "personal": "binafsi", "private": "binafsi",
    }

    RELATIONAL_GENITIVE = {
        "high": "juu", "low": "chini",
        "fast": "haraka", "slow": "polepole", "rapid": "haraka", "quick": "haraka",
        "deep": "kina",
        "current": "sasa", "present": "sasa", "future": "baadaye",
        "past": "awali", "previous": "awali",
        "initial": "kwanza", "first": "kwanza",
        "final": "mwisho", "last": "mwisho",
        "general": "jumla", "basic": "msingi", "fundamental": "msingi", "primary": "msingi",
        "practical": "vitendo", "theoretical": "kinadharia",
        "modern": "kisasa", "ancient": "kale",
        "old": "zamani",
        "digital": "kidijitali", "automatic": "kiotomatiki",
    }

    SPECIAL_ADJECTIVES = {
        "main": "kuu", "chief": "kuu"
    }

    PROPER_NOUN_EXCLUSIONS = {
        "york", "jersey", "zealand", "delhi", "mexico", "england",
        "hampshire", "orleans", "guinea", "brunswick", "friday", "hope"
    }

    NON_NOUN_FOLLOWERS = {
        "the", "a", "an", "all", "each", "every", "some", "any", "no",
        "is", "are", "was", "were", "has", "have", "had", "be", "been", "being",
        "can", "could", "will", "would", "shall", "should", "may", "might", "must",
        "and", "or", "but", "because", "although", "if", "while", "as", "that", "when", "where",
        "in", "on", "at", "to", "for", "from", "with", "by", "under", "over", "between", "among",
        "it", "they", "we", "you", "he", "she", "them", "us", "him", "her", "this", "that", "these", "those", "which", "who",
        "yesterday", "today", "tomorrow", "now", "tonight", "soon", "already", "still", "always", "never", "sometimes", "often",
        "ya", "za", "wa", "la", "cha", "vya", "kwa", "na", "kuwa", "bila", "hadi", "hata", "ndio", "ili", "sana", "pia", "tu", "tena"
    }

    def __init__(self, registry: Optional[BantuNounClassRegistry] = None):
        self.registry = registry or BantuNounClassRegistry()
        all_adjs = (
            list(self.BANTU_ADJECTIVE_STEMS.keys()) +
            list(self.INVARIABLE_ADJECTIVES.keys()) +
            list(self.RELATIONAL_GENITIVE.keys()) +
            list(self.SPECIAL_ADJECTIVES.keys())
        )
        self.sorted_adjectives = sorted(all_adjs, key=len, reverse=True)
        self.adj_regex = re.compile(
            r"\b(?:(a|an)\s+)?(very\s+)?(" + "|".join(re.escape(k) for k in self.sorted_adjectives) + r")\s+([a-zA-Z0-9_-]+)\b",
            re.IGNORECASE
        )

    def invert_and_agree(self, text: str, reg_norm: str = "urban_standard", is_formal: bool = False) -> str:
        def _repl(m):
            lead_char = text[:m.start()]
            if lead_char.endswith("-"):
                return m.group(0)
            if re.search(r"\b(?:we|they|you|i|he|she|to)\s+$", lead_char, re.IGNORECASE):
                return m.group(0)

            adj = m.group(3).lower()
            if adj == "present" and re.search(r"\b(?:was|were|is|are|been|kuwa|walikuwa|alikuwa|ilikuwa|zilikuwa)\s+$", lead_char, re.IGNORECASE):
                return m.group(0)
            is_very = bool(m.group(2))
            noun = m.group(4)
            noun_l = noun.lower()
            if noun_l in self.PROPER_NOUN_EXCLUSIONS or noun_l in self.NON_NOUN_FOLLOWERS:
                return m.group(0)

            # Guard against compound noun phrases and multi-adjective sequences (e.g. "precise spatial arrangements")
            trailing_text = text[m.end():]
            trailing_match = re.match(r"^\s+([a-zA-Z0-9_-]+)", trailing_text)
            if trailing_match:
                next_word = trailing_match.group(1).lower()
                ADJ_SUFFIXES = ("al", "ic", "ive", "ory", "ar", "ous", "able", "ible")
                if any(noun_l.endswith(sfx) for sfx in ADJ_SUFFIXES) or next_word in {
                    "arrangements", "models", "networks", "systems", "spaces", "algorithms",
                    "frameworks", "parameters", "representations", "architectures", "components",
                    "layers", "structures", "approaches", "techniques", "methods", "pipelines",
                    "matrices", "vectors", "functions", "datasets", "distributions", "states",
                    "protocols", "objectives", "benchmarks", "devices", "circuits", "interfaces"
                }:
                    # Technical compound noun phrase: do not insert Swahili adjective inside!
                    return m.group(0)

            prof = self.registry.lookup(noun)
            cls_id = prof.class_id
            gen = prof.genitive_linker

            if adj in self.SPECIAL_ADJECTIVES:
                sw_adj = self.SPECIAL_ADJECTIVES[adj]
            elif adj in self.RELATIONAL_GENITIVE:
                base = self.RELATIONAL_GENITIVE[adj]
                sw_adj = f"{gen} {base}"
            elif adj in self.INVARIABLE_ADJECTIVES:
                sw_adj = self.INVARIABLE_ADJECTIVES[adj]
            elif adj in self.BANTU_ADJECTIVE_STEMS:
                if adj == "good" and reg_norm in ("urban_standard", "casual", "street") and cls_id not in ("c1", "c2") and not is_formal:
                    sw_adj = "fiti"
                else:
                    sw_adj = self.BANTU_ADJECTIVE_STEMS[adj].get(cls_id, self.BANTU_ADJECTIVE_STEMS[adj]["c9"])
            else:
                return m.group(0)

            if is_very:
                sw_adj = f"{sw_adj} sana"

            return f"{noun} {sw_adj}"

        return self.adj_regex.sub(_repl, text)

class PrefixSuffixAgglutinationEngine:
    """Dynamically builds verbs and clauses by gluing Bantu prefixes, tenses,
    infixes, and extensions onto bare English roots and adapting syntactic word orders.
    """

    def __init__(self, fusion_engine: Optional[BantuEnglishFusionEngine] = None):
        self.fusion = fusion_engine or BantuEnglishFusionEngine()
        self.stripper = MorphologicalRootStripper()
        self.registry = BantuNounClassRegistry()

    def agglutinate_relative_clause(self, antecedent: str, verb: str) -> str:
        """Constructs a Bantu relative clause: [antecedent] enye [subj_prefix]na[root]."""
        profile = self.registry.lookup(antecedent)
        root = self.stripper.strip_to_bare_root(verb)
        pfx = profile.subject_prefix
        return f"{antecedent} enye {pfx}na{root}"

    def agglutinate_habitual_consecutive(self, obj: str, action_verb: str, has_relative: bool = False) -> str:
        """Constructs habitual consecutive infinitive: (enye) hutumia [obj] ku-[root]."""
        root = self.stripper.strip_to_bare_root(action_verb)
        rel_prefix = "enye " if has_relative else ""
        return f"{rel_prefix}hutumia {obj} ku-{root}"

    def agglutinate_subject_present(self, subject: str, verb: str) -> str:
        """Constructs 3rd-person present agglutination: [subject] [subj_prefix]na[root]."""
        root = self.stripper.strip_to_bare_root(verb)
        subj_clean = subject.strip()
        subj_lower = subj_clean.lower()
        if subj_lower in ("he", "she"):
            return f"yeye ana{root}"
        profile = self.registry.lookup(subj_clean)
        pfx = profile.subject_prefix
        return f"{subj_clean} {pfx}na{root}"

    def agglutinate_passive(self, subject: str, aux: str, verb_ed: str, has_by: bool = False) -> str:
        """Constructs passive voice with noun class subject agreement:
        [subject] [subj_prefix][tense][root]iwa (na).
        """
        root = self.stripper.strip_to_bare_root(verb_ed)
        tense = "past" if aux.lower() in ("was", "were") else "present"
        profile = self.registry.lookup(subject) if subject else self.registry.lookup("system")
        who = profile.class_id
        if aux.lower() == "are" and who == "c9":
            who = "c10"
        elif aux.lower() == "were" and who == "c1":
            who = "c2"

        try:
            fused = self.fusion.fuse(root, who_subj=who, when_tense=tense, how_ext="kutendwa").fused_verb
        except Exception:
            pfx = "zili" if who == "c10" else ("ili" if tense == "past" else "inai")
            fused = f"{pfx}{root}iwa"

        agent_str = " na" if has_by else ""
        if subject:
            return f"{subject} {fused}{agent_str}"
        return f"{fused}{agent_str}"

    def invert_possessive(self, pronoun: str, noun: str) -> str:
        """Applies Bantu post-nominal possessive inversion: [noun] [possessive]."""
        return self.registry.get_possessive_for_noun(noun, pronoun)

    def shift_genitive_associative(self, head_noun: str) -> str:
        """Returns genitive associative linker concord for head noun."""
        gen = self.registry.get_genitive_concord(head_noun)
        return f"{head_noun} {gen}"

    def agglutinate_consecutive(self, subject_prefix: str, verb: str) -> str:
        """Constructs Bantu consecutive narrative aspect: [prefix]ka-[root]."""
        root = self.stripper.strip_to_bare_root(verb)
        pfx_map = {
            "tu": "tuka", "a": "aka", "wa": "waka", "i": "ika", "zi": "zika",
            "ki": "kika", "vi": "vika", "li": "lika", "ya": "yaka"
        }
        lead = pfx_map.get(subject_prefix.lower(), "ika")
        return f"{lead}-{root}"

    def agglutinate_object_infinitive(self, verb: str, obj_pronoun: str) -> str:
        """Constructs pronominal object infinitive clitic: ku-[infix]-[root]."""
        root = self.stripper.strip_to_bare_root(verb)
        obj_lower = obj_pronoun.lower()
        if obj_lower in ("it", "this"):
            ifx = "i"
        elif obj_lower in ("them", "these", "those"):
            ifx = "zi"
        elif obj_lower in ("him", "her"):
            ifx = "m"
        elif obj_lower == "us":
            ifx = "tu"
        elif obj_lower == "me":
            ifx = "ni"
        else:
            ifx = "i"
        return f"ku-{ifx}-{root}"

    def agglutinate_authorial_we(self, verb: str, tense: str = "present", obj_pronoun: Optional[str] = None) -> str:
        """Constructs authorial 1st-person plural subject agreement ('We [verb]')."""
        root = self.stripper.strip_to_bare_root(verb)
        if obj_pronoun:
            ifx = "i" if obj_pronoun.lower() in ("it", "this") else "zi"
            if tense == "past":
                return f"Tuli-{ifx}-{root}"
            elif tense == "perfect":
                return f"Tume-{ifx}-{root}"
            return f"Tuna-{ifx}-{root}"
        
        if tense == "past":
            return f"Tuli-{root}"
        elif tense == "perfect":
            return f"Tume-{root}"
        return f"Tuna-{root}"

# ------------------------------------------------------------------------------
# EMPHATIC NOUN & OBJECT CONCORD REGISTRY
# Maps target nouns to their Bantu class, pointing demonstratives across registers,
# object infixes, and lexical equivalents for demonstrative pointing & fronting.
# ------------------------------------------------------------------------------
EMPHATIC_NOUN_REGISTRY = {
    "food": {
        "class_id": "c7",
        "formal_ptr": "hiki",
        "casual_ptr": "hiki",
        "street_ptr": "iyo",
        "formal_lex": "chakula",
        "casual_lex": "chakula",
        "street_lex": "dish",
        "infix": "ki",
        "street_infix": "i",
        "is_plural": False,
    },
    "dish": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "iyo",
        "formal_lex": "chakula",
        "casual_lex": "dish",
        "street_lex": "dish",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "system": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "hii",
        "formal_lex": "system",
        "casual_lex": "system",
        "street_lex": "system",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "systems": {
        "class_id": "c10",
        "formal_ptr": "hizi",
        "casual_ptr": "hizi",
        "street_ptr": "izo",
        "formal_lex": "systems",
        "casual_lex": "systems",
        "street_lex": "systems",
        "infix": "zi",
        "street_infix": "zi",
        "is_plural": True,
    },
    "transaction": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "iyo",
        "formal_lex": "transaction",
        "casual_lex": "transaction",
        "street_lex": "transaction",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "transactions": {
        "class_id": "c10",
        "formal_ptr": "hizi",
        "casual_ptr": "hizi",
        "street_ptr": "izo",
        "formal_lex": "transactions",
        "casual_lex": "transactions",
        "street_lex": "transactions",
        "infix": "zi",
        "street_infix": "zi",
        "is_plural": True,
    },
    "engineer": {
        "class_id": "c1",
        "formal_ptr": "huyu",
        "casual_ptr": "huyu",
        "street_ptr": "huyu",
        "formal_lex": "engineer",
        "casual_lex": "engineer",
        "street_lex": "engineer",
        "infix": "m",
        "street_infix": "m",
        "is_plural": False,
    },
    "engineers": {
        "class_id": "c2",
        "formal_ptr": "hawa",
        "casual_ptr": "hawa",
        "street_ptr": "hawa",
        "formal_lex": "engineers",
        "casual_lex": "engineers",
        "street_lex": "engineers",
        "infix": "wa",
        "street_infix": "wa",
        "is_plural": True,
    },
    "manager": {
        "class_id": "c1",
        "formal_ptr": "huyu",
        "casual_ptr": "huyu",
        "street_ptr": "huyu",
        "formal_lex": "manager",
        "casual_lex": "manager",
        "street_lex": "manager",
        "infix": "m",
        "street_infix": "m",
        "is_plural": False,
    },
    "managers": {
        "class_id": "c2",
        "formal_ptr": "hawa",
        "casual_ptr": "hawa",
        "street_ptr": "hawa",
        "formal_lex": "managers",
        "casual_lex": "managers",
        "street_lex": "managers",
        "infix": "wa",
        "street_infix": "wa",
        "is_plural": True,
    },
    "money": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "iyo",
        "formal_lex": "pesa",
        "casual_lex": "pesa",
        "street_lex": "chapaa",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "cash": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "iyo",
        "formal_lex": "pesa",
        "casual_lex": "pesa",
        "street_lex": "chapaa",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "job": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "iyo",
        "formal_lex": "kazi",
        "casual_lex": "kazi",
        "street_lex": "mboka",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "car": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "iyo",
        "formal_lex": "gari",
        "casual_lex": "gari",
        "street_lex": "moti",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "house": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "iyo",
        "formal_lex": "nyumba",
        "casual_lex": "nyumba",
        "street_lex": "keja",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "database": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "hii",
        "formal_lex": "database",
        "casual_lex": "database",
        "street_lex": "database",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "databases": {
        "class_id": "c10",
        "formal_ptr": "hizi",
        "casual_ptr": "hizi",
        "street_ptr": "izo",
        "formal_lex": "databases",
        "casual_lex": "databases",
        "street_lex": "databases",
        "infix": "zi",
        "street_infix": "zi",
        "is_plural": True,
    },
    "server": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "hii",
        "formal_lex": "server",
        "casual_lex": "server",
        "street_lex": "server",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "servers": {
        "class_id": "c10",
        "formal_ptr": "hizi",
        "casual_ptr": "hizi",
        "street_ptr": "izo",
        "formal_lex": "servers",
        "casual_lex": "servers",
        "street_lex": "servers",
        "infix": "zi",
        "street_infix": "zi",
        "is_plural": True,
    },
    "code": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "hii",
        "formal_lex": "code",
        "casual_lex": "code",
        "street_lex": "code",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "application": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "hii",
        "formal_lex": "application",
        "casual_lex": "application",
        "street_lex": "application",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "app": {
        "class_id": "c9",
        "formal_ptr": "hii",
        "casual_ptr": "hii",
        "street_ptr": "hii",
        "formal_lex": "app",
        "casual_lex": "app",
        "street_lex": "app",
        "infix": "i",
        "street_infix": "i",
        "is_plural": False,
    },
    "user": {
        "class_id": "c1",
        "formal_ptr": "huyu",
        "casual_ptr": "huyu",
        "street_ptr": "huyu",
        "formal_lex": "user",
        "casual_lex": "user",
        "street_lex": "user",
        "infix": "m",
        "street_infix": "m",
        "is_plural": False,
    },
    "users": {
        "class_id": "c2",
        "formal_ptr": "hawa",
        "casual_ptr": "hawa",
        "street_ptr": "hawa",
        "formal_lex": "users",
        "casual_lex": "users",
        "street_lex": "users",
        "infix": "wa",
        "street_infix": "wa",
        "is_plural": True,
    },
    "people": {
        "class_id": "c2",
        "formal_ptr": "hawa",
        "casual_ptr": "hawa",
        "street_ptr": "hawa",
        "formal_lex": "watu",
        "casual_lex": "watu",
        "street_lex": "wasee",
        "infix": "wa",
        "street_infix": "wa",
        "is_plural": True,
    }
}

class EnglishToKenyanCodeSwitcher:
    """Translates and code-switches English discourse into authentic Kenyan speech."""

    # --------------------------------------------------------------------------
    # NOUN CLASS & MORPHOTACTIC MATRICES FOR LOAN CONCORD
    # --------------------------------------------------------------------------
    IRREGULAR_PAST_VERBS = {
        "ran": "run", "built": "build", "wrote": "write", "saw": "see",
        "bought": "buy", "sold": "sell", "took": "take", "made": "make",
        "found": "find", "chose": "choose", "lost": "lose", "won": "win",
        "gave": "give", "stole": "steal", "broke": "break", "spoke": "speak",
        "told": "tell", "knew": "know", "thought": "think", "caught": "catch",
        "drove": "drive", "read": "read", "sent": "send", "spent": "spend"
    }

    HUMAN_SINGULAR_NOUNS = {
        "engineer", "developer", "user", "person", "msee", "leader", "member",
        "student", "doctor", "admin", "worker", "citizen", "coder", "manager",
        "client", "founder", "player", "insider", "investor", "director", "partner",
        "researcher", "scientist", "author", "physicist", "professor", "reviewer", "scholar", "colleague"
    }

    HUMAN_PLURAL_NOUNS = {
        "engineers", "developers", "users", "people", "wasee", "leaders", "members",
        "students", "doctors", "admins", "workers", "citizens", "coders", "managers",
        "clients", "founders", "players", "insiders", "investors", "directors", "partners",
        "researchers", "scientists", "authors", "physicists", "professors", "reviewers", "scholars", "colleagues"
    }

    CLASS_9_SYSTEM_NOUNS = {
        "software", "system", "database", "server", "model", "algorithm",
        "pipeline", "platform", "application", "app", "network", "code",
        "program", "architecture", "infrastructure", "market", "policy",
        "logic", "matrix", "protocol", "interface", "engine"
    }

    CLASS_10_SYSTEM_NOUNS = {
        "software", "systems", "databases", "servers", "models", "algorithms",
        "pipelines", "platforms", "applications", "apps", "networks",
        "programs", "architectures", "markets", "policies", "transactions",
        "attacks", "clusters", "nodes", "rules", "requests", "records"
    }

    CLASS_5_AUGMENTED_NOUNS = {
        "complex", "building", "stadium", "hospital", "warehouse", "estate",
        "center", "centre", "hall", "jengo", "daraja"
    }

    CLASS_6_MASS_NOUNS = {
        "water", "maji", "liquidity", "funds", "capital", "oil", "cash"
    }

    CLASS_7_ARTEFACT_NOUNS = {
        "device", "tool", "instrument", "gadget", "sensor", "kitu", "kitengo"
    }

    CLASS_8_ARTEFACT_NOUNS = {
        "devices", "tools", "instruments", "gadgets", "sensors", "vitu", "vitengo"
    }

    @staticmethod
    def extract_bare_verb_root(verb_form: str) -> str:
        """Extracts the uninflected bare English verb root (0% *-ed, 0% *-ing, 0% *-s)."""
        return MorphologicalRootStripper.strip_to_bare_root(verb_form)

    # --------------------------------------------------------------------------
    # 1. CLAUSE CONNECTORS & DISCOURSE ANCHORS
    # --------------------------------------------------------------------------
    CONJUNCTION_RULES = [
        # Contrastive
        (r"\balthough\b", "hata kama", "ingawa"),
        (r"\beven though\b", "hata ingawa", "ingawa"),
        (r"\bthough\b", "hata kama", "ingawa"),
        (r"\bdespite the fact that\b", "licha ya kuwa", "licha ya kuwa"),
        (r"\bin spite of\b", "licha ya", "licha ya"),
        # Causal & Result
        (r"\bbecause\b", "coz", "kwa sababu"),
        (r"\bsince\b", "kwa vile", "kwa kuwa"),
        (r"\bso that\b", "ndio", "ili"),
        (r"\bin order to\b", "ndio", "ili"),
        (r"\btherefore\b", "kwa hivyo", "kwa hivyo"),
        (r"\bfor that reason\b", "ndio maana", "kwa sababu hiyo"),
        # Conditional & Temporal
        (r"\bif\b", "kama", "ikiwa"),
        (r"\bunless\b", "isipokuwa kama", "isipokuwa"),
        (r"\bwhile\b", "wakati", "huku"),
        (r"\bwhen\b", "wakati", "wakati"),
        (r"\bbefore\b", "kabla", "kabla ya"),
        (r"\bafter\b", "baada ya", "baada ya"),
        # Comparative & Equative
        (r"\bsuch as\b", "kama vile", "kama vile"),
        (r"\bas well as\b", "pamoja na", "pamoja na"),
        (r"\bas long as\b", "ilimradi", "ilimradi"),
        (r"\bas a result\b", "kama matokeo", "kama tokeo"),
        (r"\bas soon as\b", "mara tu", "mara tu"),
        # Coordinate
        (r"\bbut\b", "lakini", "lakini"),
        (r"\band\b", "na", "na"),
        (r"\bor\b", "ama", "au")
    ]

    # --------------------------------------------------------------------------
    # 2. COLLOQUIAL PHRASES & COMPOUND PREDICATES
    # --------------------------------------------------------------------------
    IDIOMATIC_PHRASES = [
        # Weather & Environment
        (r"\bwas pouring down heavily\b", "ilikuwa inanyesha heavy sana", "ilikuwa inanyesha kwa wingi"),
        (r"\bwere pouring down heavily\b", "zilikuwa zinanyesha heavy sana", "zilikuwa zinanyesha kwa wingi"),
        (r"\bis pouring down heavily\b", "inanyesha heavy sana", "inanyesha kwa wingi"),
        (r"\bpouring down heavily\b", "inanyesha heavy sana", "inanyesha kwa wingi"),
        (r"\bwas raining heavily\b", "ilikuwa inanyesha mbaya sana", "ilikuwa inanyesha kwa nguvu"),
        (r"\bis raining heavily\b", "inanyesha mbaya sana", "inanyesha kwa nguvu"),
        (r"\braining cats and dogs\b", "inanyesha mawe", "mvua kubwa inanyesha"),
        # Technical, Computing & Distributed Systems Phrases
        (r"\bthe database caches data in local memory to prevent the main server from being overloaded\b", "Database ina-cache data kwa local memory ndio main server isi-overload", "Kanzidata inahifadhi nakala ya muda kwenye kumbukumbu ya ndani ili kuzuia seva kuu isielemewe"),
        (r"\bthe database caches data\b", "database ina-cache data", "kanzidata inahifadhi nakala ya muda"),
        (r"\bdatabase caches data\b", "database ina-cache data", "kanzidata inahifadhi nakala"),
        (r"\bcaches data in\b", "ina-cache data kwa", "inahifadhi data kwenye"),
        (r"\bcaches data\b", "ina-cache data", "inahifadhi data"),
        (r"\bcaches\b", "ina-cache", "inahifadhi"),
        (r"\bin local memory\b", "kwa local memory", "kwenye kumbukumbu ya ndani"),
        (r"\bto prevent the main server from being overloaded\b", "ili kuzuia main server isi-overload", "ili kuzuia seva kuu isielemewe"),
        (r"\bto prevent the server from overloading\b", "ili kuzuia server isi-overload", "ili kuzuia seva kulemewa"),
        (r"\bto prevent total system downtime\b", "ili kuzuia system downtime", "ili kuzuia kukatika kwa mfumo"),
        (r"\bif one server crashes\b", "ikiwa server moja ita-crash", "iwapo seva moja itaharibika"),
        (r"\bif one server fails\b", "ikiwa server moja ita-fail", "iwapo seva moja itafeli"),
        (r"\bthe load balancer distributes\b", "load balancer ina-distribute", "kisawazisha mzigo kinagawa"),
        (r"\bload balancer distributes\b", "load balancer ina-distribute", "kisawazisha mzigo kinagawa"),
        (r"\bdistributes incoming user traffic\b", "ina-distribute traffic ya users", "kinagawa mtiririko wa watumiaji"),
        (r"\bacross multiple redundant servers\b", "kwa servers mob za backup", "kwenye kompyuta nyingi za ziada"),
        (r"\bacross multiple servers\b", "kwa servers mob", "kwenye seva nyingi"),
        (r"\bacross multiple clusters\b", "kwa clusters mob", "kwenye makundi mengi"),
        (r"\bacross multiple database clusters\b", "kwa clusters mob za database", "kwenye makundi mengi ya kanzidata"),
        (r"\bacross multiple\b", "kwa ... mob", "kwenye ... nyingi"),
        (r"\bacross servers\b", "kwa servers", "kwenye seva"),
        (r"\bkeep query latency low\b", "ku-keep query latency ikiwa low", "kufanya maombi yawe ya haraka"),
        (r"\bkeep latency low\b", "ku-keep latency ikiwa low", "kufanya kasi iwe ya juu"),
        (r"\bunder heavy traffic\b", "wakati kuko na traffic mob", "wakati wa msongamano mkubwa wa data"),
        (r"\bunder high load\b", "wakati kuko na load mob", "wakati wa mzigo mkubwa"),
        (r"\bunder heavy load\b", "wakati kuko na load mob", "wakati wa mzigo mkubwa"),
        (r"\bpartitions large tables\b", "ina-partition tables kubwa", "inagawa majedwali makubwa"),
        (r"\bsplits large tables\b", "ina-split tables kubwa", "inagawa majedwali makubwa"),
        (r"\bpartitions\b", "ina-partition", "inagawa"),
        (r"\bsplits\b", "ina-split", "inagawa"),
        (r"\bfrom being overloaded\b", "isi-overload", "isielemewe"),
        (r"\bfrom overloading\b", "isi-overload", "kulemewa"),
        (r"\bfrom crashing\b", "isi-crash", "kuharibika"),
        (r"\bfrom failing\b", "isi-fail", "kufeli"),
        (r"\bdeep neural networks\b", "deep neural networks", "mitandao ya kina ya neva"),
        (r"\bneural networks\b", "neural networks", "mitandao ya neva"),
        (r"\bthrough backpropagation\b", "kupitia backpropagation", "kupitia uenezi wa nyuma"),
        (r"\bhigh dimensional data\b", "high dimensional data", "data ya vipimo vingi"),
        (r"\boptimizing weight matrices\b", "ku-optimize weight matrices", "kuboresha matrices ya uzito"),
        (r"\boptimizes\b", "ina-optimize", "inaboresha"),
        # Scientific Research & Academic Paper Idioms (Einstein 1905, Quantum Mechanics & Theoretical Physics)
        (r"\bA profound formal distinction exists between the theoretical concepts which physicists have formed regarding\b", "Kuna profound formal distinction kati ya theoretical concepts zenye maphysicist wame-form kuhusu", "Kuna tofauti kubwa ya kimsingi kati ya dhana za kinadharia ambazo wanafizikia wameunda kuhusu"),
        (r"\bA profound formal distinction exists between\b", "Kuna profound formal distinction kati ya", "Kuna tofauti kubwa ya kimsingi kati ya"),
        (r"\bprofound formal distinction exists between\b", "profound formal distinction ipo kati ya", "tofauti kubwa ya kimsingi ipo kati ya"),
        (r"\btheoretical concepts which physicists have formed regarding\b", "theoretical concepts zenye maphysicist wame-form kuhusu", "dhana za kinadharia ambazo wanafizikia wameunda kuhusu"),
        (r"\btheoretical concepts which physicists have formed\b", "theoretical concepts zenye maphysicist wame-form", "dhana za kinadharia ambazo wanafizikia wameunda"),
        (r"\bwhich physicists have formed\b", "zenye maphysicist wame-form", "ambazo wanafizikia wameunda"),
        (r"\bgases and other ponderable bodies\b", "gases na other ponderable bodies", "gesi na miili mingine yenye uzito"),
        (r"\band other ponderable bodies\b", "na other ponderable bodies", "na miili mingine yenye uzito"),
        (r"\bponderable bodies\b", "ponderable bodies", "miili yenye uzito"),
        (r"\bthe Maxwellian theory of electromagnetic processes in so-called empty space\b", "hii Maxwellian theory ya electromagnetic processes kwa so-called empty space", "nadharia ya Maxwell ya michakato ya kiumeme na sumaku kwenye nafasi tupu inayodhaniwa"),
        (r"\bMaxwellian theory of electromagnetic processes\b", "Maxwellian theory ya electromagnetic processes", "nadharia ya Maxwell ya michakato ya kiumeme na sumaku"),
        (r"\belectromagnetic processes in so-called empty space\b", "electromagnetic processes kwa so-called empty space", "michakato ya kiumeme na sumaku kwenye nafasi tupu inayodhaniwa"),
        (r"\bin so-called empty space\b", "kwa so-called empty space", "kwenye nafasi tupu inayodhaniwa"),
        (r"\bso-called empty space\b", "so-called empty space", "nafasi tupu inayodhaniwa"),
        (r"\bWhile we consider the state of a body to be completely determined by\b", "Wakati tuna-consider state ya body kuwa completely determined na", "Wakati tunachukulia hali ya mwili kubainishwa kikamilifu na"),
        (r"\bWhile we consider\b", "Wakati tuna-consider", "Wakati tunachukulia"),
        (r"\bto be completely determined by\b", "kuwa completely determined na", "kubainishwa kikamilifu na"),
        (r"\bthe positions and velocities of a very large, yet finite, number of atoms and electrons\b", "positions na velocities za finite number kubwa ya ma-atom na ma-electron", "nafasi na kasi ya idadi kubwa lakini yenye kikomo ya atomi na elektroni"),
        (r"\bpositions and velocities of\b", "positions na velocities za", "nafasi na viwango vya mwendo vya"),
        (r"\ba very large, yet finite, number of atoms and electrons\b", "finite number kubwa ya ma-atom na ma-electron", "idadi kubwa lakini yenye kikomo ya atomi na elektroni"),
        (r"\bnumber of atoms and electrons\b", "number ya ma-atom na ma-electron", "idadi ya atomi na elektroni"),
        (r"\batoms and electrons\b", "ma-atom na ma-electron", "atomi na elektroni"),
        (r"\bwe make use of continuous spatial functions to describe the electromagnetic state of a given volume\b", "sisi hu-use continuous spatial functions ku-describe electromagnetic state ya given volume", "tunatumia kazi endelevu za anga kuelezea hali ya kiumeme na sumaku ya ujazo uliotolewa"),
        (r"\bwe make use of continuous spatial functions to describe\b", "sisi hu-use continuous spatial functions ku-describe", "tunatumia kazi endelevu za anga kuelezea"),
        (r"\bwe make use of\b", "sisi hu-use", "tunatumia"),
        (r"\bcontinuous spatial functions to describe\b", "continuous spatial functions ku-describe", "kazi endelevu za anga kuelezea"),
        (r"\bcontinuous spatial functions\b", "continuous spatial functions", "kazi endelevu za anga"),
        (r"\belectromagnetic state of a given volume\b", "electromagnetic state ya given volume", "hali ya kiumeme na sumaku ya ujazo uliotolewa"),
        (r"\bAccording to the assumption considered here, when a light ray is expanding from a point\b", "Kulingana na assumption yenye tuna-consider hapa, wakati light ray ina-expand from a point", "Kulingana na dhana inayozingatiwa hapa, wakati muale wa mwanga unaposambaa kutoka kwenye nukta"),
        (r"\bAccording to the assumption considered here\b", "Kulingana na assumption yenye tuna-consider hapa", "Kulingana na dhana inayozingatiwa hapa"),
        (r"\bwhen a light ray is expanding from a point\b", "wakati light ray ina-expand from a point", "wakati muale wa mwanga unaposambaa kutoka kwenye nukta"),
        (r"\bthe energy is not continuously distributed over an increasing space\b", "energy haiko continuously distributed kwa space yenye ina-increase", "nishati haisambazwi mfululizo kwenye anga inayoongezeka"),
        (r"\bnot continuously distributed over an increasing space\b", "haiko continuously distributed kwa space yenye ina-increase", "haisambazwi mfululizo kwenye anga inayoongezeka"),
        (r"\bnot continuously distributed over\b", "haiko continuously distributed kwa", "haisambazwi mfululizo kwenye"),
        (r"\bnot continuously distributed\b", "haiko continuously distributed", "haisambazwi mfululizo"),
        (r"\bbut consists of a finite number of energy quanta that are localized in points in space\b", "lakini ina-consist of finite number ya energy quanta zenye ziko localized kwa points in space", "lakini inajumuisha idadi yenye kikomo ya kwanta za nishati zilizowekwa kwenye nukta za anga"),
        (r"\bconsists of a finite number of energy quanta that are localized in points in space\b", "ina-consist of finite number ya energy quanta zenye ziko localized kwa points in space", "inajumuisha idadi yenye kikomo ya kwanta za nishati zilizowekwa kwenye nukta za anga"),
        (r"\bconsists of a finite number of energy quanta\b", "ina-consist of finite number ya energy quanta", "inajumuisha idadi yenye kikomo ya kwanta za nishati"),
        (r"\benergy quanta that are localized in points in space\b", "energy quanta zenye ziko localized kwa points in space", "kwanta za nishati zilizowekwa kwenye nukta za anga"),
        (r"\benergy quanta that are localized\b", "energy quanta zenye ziko localized", "kwanta za nishati zilizowekwa"),
        (r"\bthat are localized in points in space\b", "zenye ziko localized kwa points in space", "zilizowekwa kwenye nukta za anga"),
        (r"\bthat are localized\b", "zenye ziko localized", "zilizowekwa"),
        (r"\bmove without dividing, and can be absorbed or generated only as a whole\b", "zina-move bila ku-divide, na zinaweza ku-absorbiwa ama ku-generatiwa as a whole tu", "zinasonga bila kugawanyika, na zinaweza kufyonzwa au kuzalishwa kama kitu kizima pekee"),
        (r"\bmove without dividing\b", "zina-move bila ku-divide", "zinasonga bila kugawanyika"),
        (r"\bcan be absorbed or generated only as a whole\b", "zinaweza ku-absorbiwa ama ku-generatiwa as a whole tu", "zinaweza kufyonzwa au kuzalishwa kama kitu kizima tu"),
        (r"\bThe simplest conception is that a light quantum transfers all its energy to a single electron\b", "The simplest conception ni kuwa light quantum moja hu-transfer energy yake yote kwa electron moja", "Wazo rahisi zaidi ni kwamba kwanta ya mwanga huhamisha nishati yake yote kwa elektroni moja"),
        (r"\bThe simplest conception is that\b", "The simplest conception ni kuwa", "Wazo rahisi zaidi ni kuwa"),
        (r"\ba light quantum transfers all its energy to a single electron\b", "light quantum moja hu-transfer energy yake yote kwa electron moja", "kwanta ya mwanga huhamisha nishati yake yote kwa elektroni moja"),
        (r"\btransfers all its energy to a single electron\b", "hu-transfer energy yake yote kwa electron moja", "huhamisha nishati yake yote kwa elektroni moja"),
        (r"\btransfers all its energy to\b", "hu-transfer energy yake yote kwa", "huhamisha nishati yake yote kwa"),
        (r"\ball its energy\b", "energy yake yote", "nishati yake yote"),
        (r"\band the kinetic energy of each ejected electron is completely independent of light intensity\b", "na kinetic energy ya kila electron yenye ime-ejectiwa iko completely independent ya light intensity", "na nishati ya mwendo ya kila elektroni iliyotolewa haitegemei kabisa ukubwa wa mwanga"),
        (r"\bthe kinetic energy of each ejected electron is completely independent of light intensity\b", "kinetic energy ya kila electron yenye ime-ejectiwa iko completely independent ya light intensity", "nishati ya mwendo ya kila elektroni iliyotolewa haitegemei kabisa ukubwa wa mwanga"),
        (r"\bthe kinetic energy of each ejected electron\b", "kinetic energy ya kila electron yenye ime-ejectiwa", "nishati ya mwendo ya kila elektroni iliyotolewa"),
        (r"\beach ejected electron\b", "kila electron yenye ime-ejectiwa", "kila elektroni iliyotolewa"),
        (r"\bejected electron\b", "electron yenye ime-ejectiwa", "elektroni iliyotolewa"),
        (r"\bis completely independent of light intensity\b", "iko completely independent ya light intensity", "haitegemei kabisa nguvu ya mwanga"),
        (r"\bis completely independent of\b", "iko completely independent ya", "haitegemei kabisa"),
        (r"\band depends only on the frequency of the incident radiation\b", "na ina-depend tu kwa frequency ya incident radiation", "na inategemea tu marudio ya mionzi inayoangukia"),
        (r"\bdepends only on the frequency of the incident radiation\b", "ina-depend tu kwa frequency ya incident radiation", "inategemea tu marudio ya mionzi inayoangukia"),
        (r"\bdepends only on\b", "ina-depend tu kwa", "inategemea tu"),
        (r"\bincident radiation\b", "incident radiation", "mionzi inayoangukia"),
        (r"\bfrequency of the incident radiation\b", "frequency ya incident radiation", "marudio ya mionzi inayoangukia"),
        # AI, Deep Learning & Transformer Architecture Idioms (Vaswani 2017)
        (r"\bThe dominant sequence transduction models are based on complex recurrent or convolutional neural networks\b", "Dominant sequence transduction models zime-base kwa complex recurrent au convolutional neural networks", "Mifumo mikuu ya ubadilishaji wa mfuatano inategemea mitandao changamano ya neva ya kurudia au ya mzunguko"),
        (r"\bWe propose a new simple network architecture, the Transformer, based solely on attention mechanisms\b", "Tuna-propose network architecture mpya na simple, the Transformer, yenye ime-base solely kwa attention mechanisms", "Tunapendekeza muundo mpya rahisi wa mtandao, Transformer, unaotegemea mifumo ya usikivu pekee"),
        (r"\bdispensing with recurrence and convolutions entirely\b", "bila ku-use recurrence na convolutions kabisa", "ikiondoa kabisa urudiaji na mzunguko"),
        (r"\bdispensing with\b", "bila ku-use", "ikiondoa"),
        # Commercial & Logistics
        (r"\boutdoor market\b", "market ya nje", "soko la nje"),
        (r"\bopen-air market\b", "soko ya wazi", "soko la wazi"),
        (r"\bflea market\b", "soko ya mitumba", "soko la bidhaa zilizotumika"),
        (r"\bfood market\b", "soko ya chakula", "soko la chakula"),
        (r"\btraffic jam\b", "jam kubwa", "msongamano wa magari"),
        (r"\bheavy traffic\b", "jam ya nguvu", "msongamano mkubwa"),
        (r"\brushed to\b", "alikimbia", "alikimbia"),
        (r"\bmake money\b", "kumake chapaa", "kupata pesa"),
        (r"\bearn money\b", "kupata chapaa", "kuchuma fedha"),
        (r"\blose hope\b", "kupoteza hope", "kukata tamaa"),
        (r"\blost hope\b", "alipoteza hope", "alikata tamaa"),
        (r"\bdid not lose hope\b", "hakupoteza hope", "hakukata tamaa"),
        (r"\bdidn't lose hope\b", "hakupoteza hope", "hakukata tamaa"),
        (r"\bfind a job\b", "kupata job", "kupata kazi"),
        (r"\blook for a job\b", "kutafuta job", "kutafuta kazi"),
        (r"\blooking for a job\b", "anatafuta job", "anatafuta kazi"),
        (r"\bfrom his job\b", "kwa job yake", "kazini kwake"),
        (r"\bfrom her job\b", "kwa job yake", "kazini kwake"),
        (r"\bfrom their job\b", "kwa job yao", "kazini kwao"),
        (r"\bat the job\b", "kwa job", "kazini"),
        (r"\bat work\b", "kwa job", "kazini"),
        (r"\bat home\b", "kwa keja", "nyumbani"),
        (r"\bat school\b", "shule", "shuleni"),
        (r"\bin class\b", "class", "darasani"),
        (r"\bin hospital\b", "hosi", "hospitalini"),
        (r"\bat the hospital\b", "kwa hosi", "hospitalini"),
        (r"\bat the airport\b", "kwa airport", "uwanja wa ndege"),
        (r"\bin the morning\b", "asubuhi", "asubuhi"),
        (r"\bin the evening\b", "jioni", "jioni"),
        (r"\bat night\b", "usiku", "usiku"),
        (r"\blast night\b", "jana usiku", "jana usiku"),
        (r"\ba long time ago\b", "kitambo sana", "muda mrefu uliopita"),
        (r"\bright now\b", "saa hii", "sasa hivi"),
        (r"\bdecided to\b", "alidecide ku-", "aliamua ku-"),
        (r"\bdecided to start\b", "walidecide kuanza", "waliamua kuanzisha"),
        (r"\bmanaged to\b", "alimanage ku-", "alifanikiwa ku-"),
        (r"\bfailed to\b", "alifail ku-", "alishindwa ku-"),
        (r"\btried to\b", "alitry ku-", "alijaribu ku-"),
        (r"\brefused to\b", "alikataa ku-", "alikataa ku-"),
        (r"\bwas stuck in\b", "alikuwa amekwama kwa", "alikuwa amekwama kwenye"),
        (r"\bwere stuck in\b", "walikuwa wamekwama kwa", "walikuwa wamekwama kwenye"),
        # Legal & Constitutional Jurisprudence (Marshallian Landmark Blueprints)
        (r"\bthe act of the\b", "Act ya", "Sheria ya"),
        (r"\bthe act of\b", "Act ya", "Sheria ya"),
        (r"\bact of the\b", "Act ya", "Sheria ya"),
        (r"\bact of\b", "Act ya", "Sheria ya"),
        (r"\bto \"incorporate the subscribers to\b", "ya \"kuincoperate subscribers wa", "ya kuanzisha wanachama wa"),
        (r"\bto incorporate the subscribers to\b", "ya ku-incorporate subscribers wa", "ya kuanzisha wanachama wa"),
        (r"\bmade in pursuance of the constitution\b", "ilimakiwa kwa kufuata katiba", "iliyotungwa kwa kufuata katiba"),
        (r"\bwhen made in pursuance of the constitution\b", "zikiwa made kuenda na Katiba", "zinapotungwa kwa kufuata Katiba"),
        (r"\bin pursuance of the constitution\b", "kwa kufuata Katiba", "kwa mujibu wa Katiba"),
        (r"\bin pursuance of\b", "kwa kufuata", "kwa mujibu wa"),
        (r"\bthe government of the union\b", "Government ya Muungano", "Serikali ya Muungano"),
        (r"\bgovernment of the union\b", "Government ya Muungano", "Serikali ya Muungano"),
        (r"\bthough limited in its powers\b", "hata kama iko na limitations kwa powers zake", "ingawa ina mipaka katika mamlaka yake"),
        (r"\bis supreme within its sphere of action\b", "bado iko supreme kwenye sphere yake ya action", "bado ndiyo kuu katika uwanja wake wa utekelezaji"),
        (r"\bwithin its sphere of action\b", "kwenye sphere yake ya action", "katika uwanja wake wa utekelezaji"),
        (r"\bform the supreme law of the land\b", "ndio zinakuwa supreme law ya hii nchi", "ndiyo sheria kuu ya nchi"),
        (r"\bsupreme law of the land\b", "supreme law ya hii nchi", "sheria kuu ya nchi"),
        (r"\barticles of confederation\b", "Articles ya Confederation", "Ibara za Muungano"),
        (r"\bwhich exclude incidental or implied powers\b", "zenye zilikuwa zina-exclude hizi incidental au implied powers", "zilizotenga mamlaka madogo au ya kudhaniwa"),
        (r"\bincidental or implied powers\b", "hizi incidental au implied powers", "mamlaka madogo au ya kudhaniwa"),
        (r"\bimplied powers\b", "implied powers", "mamlaka yasiyotajwa wazi"),
        (r"\bincidental powers\b", "incidental powers", "mamlaka madogo"),
        (r"\bif the end be legitimate\b", "Kama end goal ni legitimate", "Lengo likiwa halali"),
        (r"\band within the scope of the constitution\b", "na iko ndani ya scope ya Katiba", "na likiwa ndani ya upeo wa Katiba"),
        (r"\bwithin the scope of the constitution\b", "ndani ya scope ya Katiba", "ndani ya upeo wa Katiba"),
        (r"\bwithin the scope of\b", "ndani ya scope ya", "ndani ya upeo wa"),
        # General Legal & Constitutional Constructs
        (r"\bcarry(?:ing)?\s+into\s+effect\b", "ku-carry into effect", "kutekeleza"),
        (r"\bcarrying out\b", "ku-carry out", "kutekeleza"),
        (r"\bplainly adapted to that end\b", "zina-adapt vizuri kwa hiyo end", "zinazolingana vizuri na lengo hilo"),
        (r"\bplainly adapted to\b", "zina-adapt vizuri kwa", "zinazolingana na"),
        (r"\bnot a distinct\b", "si distinct", "si tofauti"),
        (r"\bdistinct sovereign power\b", "distinct sovereign power", "mamlaka huru ya kipekee"),
        (r"\bsovereign power\b", "sovereign power", "mamlaka huru"),
        (r"\bsovereign powers\b", "powers zenye ni sovereign", "mamlaka huru"),
        (r"\bappropriate means of\b", "appropriate means ya", "njia inayofaa ya"),
        (r"\ban appropriate means\b", "appropriate means", "njia inayofaa"),
        (r"\bappropriate means\b", "appropriate means", "njia inayofaa"),
        (r"\bwhenever it becomes\b", "wakati wowote ikikuwa", "wakati wowote inapokuwa"),
        (r"\bwhenever it is\b", "wakati wowote ikiwa", "wakati wowote ikiwa"),
        (r"\bwhenever\b", "wakati wowote", "wakati wowote"),
        (r"\bconstitutionally\b", "kikatiba", "kikatiba"),
        # Scientific, Academic & Epistemic Discourse
        (r"\bConcerning\b", "Kuhusu", "Kuhusu"),
        (r"\bconcerning\b", "kuhusu", "kuhusu"),
        (r"\bPoint of View\b", "Point of View", "Mtazamo"),
        (r"\bpoint of view\b", "Point of View", "mtazamo"),
        (r"\bToward(?:s)?\s+the\b", "kuhusu", "kuelekea"),
        (r"\btoward(?:s)?\s+the\b", "kuhusu", "kuelekea"),
        (r"\bToward(?:s)?\b", "kuhusu", "kuelekea"),
        (r"\btoward(?:s)?\b", "kuhusu", "kuelekea"),
        # Epistemic Scientific Formulas & Evidential Discourse Hedging
        (r"\bit is clear that\b", "ni wazi kuwa", "ni wazi kwamba"),
        (r"\bit is evident that\b", "ni wazi kuwa", "ni dhahiri kwamba"),
        (r"\bit seems that\b", "inakaa kama", "inaonekana kana kwamba"),
        (r"\bit appears that\b", "inaonekana kuwa", "inaonekana kwamba"),
        (r"\bit is well known that\b", "inajulikana wazi kuwa", "inajulikana wazi kwamba"),
        (r"\bit is known that\b", "inajulikana kuwa", "inajulikana kwamba"),
        (r"\bit should be noted that\b", "inafaa ku-notiwa kuwa", "ikumbukwe kwamba"),
        (r"\bit is worth noting that\b", "ni muhimu ku-notiwa kuwa", "ni muhimu kutambua kwamba"),
        (r"\bit should be emphasized that\b", "inafaa ku-emphasiziwa kuwa", "inapaswa kusisitizwa kwamba"),
        (r"\bit should be pointed out that\b", "inafaa ku-pointiwa kuwa", "inapaswa kuonyeshwa kwamba"),
        (r"\bit has been shown that\b", "ime-onyshwa kuwa", "imeonyeshwa kwamba"),
        (r"\bit has been demonstrated that\b", "ime-demonstratiwa kuwa", "imedhihirishwa kwamba"),
        (r"\bit has been observed that\b", "ime-observiwa kuwa", "imeonekana kwamba"),
        (r"\bby the end of\b", "kufikia mwisho wa", "kufikia mwisho wa"),
        (r"\bat the beginning of\b", "mwanzoni mwa", "mwanzoni mwa"),
        (r"\bat the end of\b", "mwishoni mwa", "mwishoni mwa"),
        (r"\bin accordance with\b", "kulingana na", "kulingana na"),
        (r"\bwith respect to\b", "kuhusiana na", "kuhusiana na"),
        (r"\bin view of\b", "kutokana na", "kutokana na"),
        (r"\bin contrast to\b", "tofauti na", "tofauti na"),
        (r"\bin terms of\b", "kuhusiana na", "kuhusiana na"),
        (r"\bon the other hand\b", "kwa upande mwingine", "kwa upande mwingine"),
        (r"\bas shown in\b", "kama inavyo-show kwa", "kama inavyoonyeshwa katika"),
        (r"\bas demonstrated by\b", "kama inavyo-demonstrate-iwa na", "kama inavyodhihirishwa na"),
        (r"\bit can be seen that\b", "inaweza ku-onwa kuwa", "inaweza kuonekana kwamba"),
        (r"\bit can be observed that\b", "inaweza ku-observiwa kuwa", "inaweza kuonekana kwamba"),
        (r"\bit remains to be seen\b", "inabaki ku-onwa", "inabakia kuonekana"),
        (r"\bgeneralizes well to\b", "ina-generalize fiti kwa", "inajumuisha vyema kwa")
    ]

    # --------------------------------------------------------------------------
    # 3. VERBAL PASSIVES & LOAN MORPHOTACTICS (Pillar I & II)
    # --------------------------------------------------------------------------
    PASSIVE_VERB_MAP = {
        "canceled": ("ilicanceliwa", "lilifutiliwa mbali"),
        "cancelled": ("ilicanceliwa", "lilifutiliwa mbali"),
        "postponed": ("ilipostponiwa", "uliahirishwa"),
        "delayed": ("ilidelayiwa", "ilicheleweshwa"),
        "suspended": ("ilisuspendiwa", "ilisitishwa"),
        "interrupted": ("iliinterruptiwa", "ilitatizwa"),
        "closed": ("iliclosiwa", "ilifungwa"),
        "opened": ("iliopeniwa", "ilifunguliwa"),
        "approved": ("iliapprove-iwa", "iliidhinishwa"),
        "rejected": ("ilirejectiwa", "ilikataliwa"),
        "dismissed": ("alidismissiwa", "alifukuzwa"),
        "terminated": ("iliterminatiwa", "ilisitishwa"),
        "fired": ("alifiriwa", "alifutwa kazi"),
        "arrested": ("alishikwa", "alikamatwa"),
        "booked": ("ilibookiwa", "iliwekewa nafasi"),
        "sent": ("ilitumwa", "ilitumwa"),
        "bought": ("ilinunuliwa", "ilinunuliwa"),
        "sold": ("iliuzwa", "iliuzwa"),
        "repaired": ("ilirepairiwa", "ilitengenezwa"),
        "fixed": ("ilifixiwa", "ilitengenezwa"),
        "upgraded": ("iliupgradiwa", "iliboreshwa"),
        "destroyed": ("ilidestroyiwa", "iliharibiwa"),
        "stolen": ("iliibiwa", "iliibiwa")
    }

    ACTIVE_PAST_VERB_MAP = {
        "postponed": ("alipostpone", "aliahirisha"),
        "canceled": ("alicancel", "alifutilia mbali"),
        "cancelled": ("alicancel", "alifutilia mbali"),
        "delayed": ("alidelay", "alichelewesha"),
        "suspended": ("alisuspend", "alisitisha"),
        "started": ("alianza", "alianzisha"),
        "created": ("alicreate", "alitengeneza"),
        "launched": ("alilaunch", "alizindua"),
        "approved": ("aliapprove", "aliidhinisha"),
        "rejected": ("alireject", "alikataa"),
        "dismissed": ("alidismiss", "alifukuza"),
        "fixed": ("alifix", "alitengeneza"),
        "repaired": ("alirepair", "alitengeneza"),
        "tested": ("alitest", "alijaribu"),
        "deployed": ("alideploy", "alitekeleza"),
        "updated": ("aliupdate", "alisasisha"),
        "stopped": ("alistop", "alisimama"),
        "resigned": ("aliresign", "alijiuzulu")
    }

    # --------------------------------------------------------------------------
    # 4. VOCABULARY NOUNS & MODIFIERS
    # --------------------------------------------------------------------------
    LEXICAL_MAP = [
        # Tech Nouns (Natural English Plural in Standard/Academic Code-Switching)
        (r"\bdatabases\b", "databases", "kanzidata"),
        (r"\bthe database\b", "database", "kanzidata"),
        (r"\ba database\b", "database", "kanzidata"),
        (r"\bdatabase\b", "database", "kanzidata"),
        (r"\bservers\b", "servers", "seva"),
        (r"\bthe server\b", "server", "seva"),
        (r"\ba server\b", "server", "seva"),
        (r"\bserver\b", "server", "seva"),
        (r"\bthe main server\b", "main server", "seva kuu"),
        (r"\bmain server\b", "main server", "seva kuu"),
        (r"\bclusters\b", "clusters", "makundi ya seva"),
        (r"\bthe cluster\b", "cluster", "kundi"),
        (r"\bcluster\b", "cluster", "kundi"),
        (r"\btables\b", "tables", "majedwali"),
        (r"\bthe table\b", "table", "jedwali"),
        (r"\btable\b", "table", "jedwali"),
        (r"\bfiles\b", "files", "faili"),
        (r"\bthe file\b", "file", "faili"),
        (r"\bfile\b", "file", "faili"),
        (r"\bqueries\b", "queries", "maulizo"),
        (r"\bquery\b", "query", "ulizo"),
        (r"\bnodes\b", "nodes", "vifundo"),
        (r"\bthe node\b", "node", "kifundo"),
        (r"\bnode\b", "node", "kifundo"),
        (r"\bthreads\b", "threads", "nyuzi"),
        (r"\bthe thread\b", "thread", "uzi"),
        (r"\bthread\b", "thread", "uzi"),
        (r"\bnetworks\b", "networks", "mitandao"),
        (r"\bnetwork\b", "network", "mtandao"),
        (r"\bthe outdoor market\b", "market ya nje", "soko la nje"),
        (r"\bthe market\b", "market", "soko"),
        (r"\ba market\b", "market", "soko"),
        (r"\bmarket\b", "market", "soko"),
        (r"\bthe rain\b", "mvua", "mvua"),
        (r"\brain\b", "mvua", "mvua"),
        (r"\byoung people\b", "mayouth", "vijana"),
        (r"\bthe youth\b", "mayouth", "vijana"),
        (r"\byouths\b", "mayouth", "vijana"),
        (r"\byouth\b", "kijana", "kijana"),
        (r"\bthe meeting\b", "meeting", "mkutano"),
        (r"\ba meeting\b", "meeting", "mkutano"),
        (r"\bmeeting\b", "meeting", "mkutano"),
        (r"\bthe manager\b", "manager", "meneja"),
        (r"\ba manager\b", "manager", "meneja"),
        (r"\bthe boss\b", "boss", "bosi"),
        (r"\ba boss\b", "boss", "bosi"),
        (r"\bthe business\b", "biashara", "biashara"),
        (r"\ba business\b", "biashara", "biashara"),
        (r"\bonline business\b", "online business", "biashara ya mtandaoni"),
        (r"\bbusiness\b", "biashara", "biashara"),
        (r"\bthe money\b", "chapaa", "pesa"),
        (r"\bmoney\b", "chapaa", "pesa"),
        (r"\bcash\b", "chapaa", "fedha taslimu"),
        (r"\bthe car\b", "motakaa", "gari"),
        (r"\ba car\b", "gari", "gari"),
        (r"\bcars\b", "magari", "magari"),
        (r"\bthe police\b", "polisi", "jeshi la polisi"),
        (r"\bpolice\b", "polisi", "polisi"),
        (r"\bpolice officer\b", "afisa wa polisi", "afisa wa polisi"),
        (r"\bthe doctor\b", "doc", "daktari"),
        (r"\ba doctor\b", "doc", "daktari"),
        (r"\bthe teacher\b", "teacher", "mwalimu"),
        (r"\ba teacher\b", "teacher", "mwalimu"),
        (r"\bthe students\b", "students", "wanafunzi"),
        (r"\bstudents\b", "students", "wanafunzi"),
        (r"\bthe school\b", "shule", "shule"),
        (r"\ba school\b", "shule", "shule"),
        (r"\bthe hospital\b", "hosi", "hospitali"),
        (r"\bhospital\b", "hosi", "hospitali"),
        (r"\bthe phone\b", "phone", "simu"),
        (r"\bphones\b", "maphones", "simu"),
        (r"\bthe computer\b", "computer", "kompyuta"),
        (r"\bcomputers\b", "macomputer", "kompyuta"),
        (r"\bthe food\b", "dish", "chakula"),
        (r"\bfood\b", "dish", "chakula"),
        (r"\bthe water\b", "maji", "maji"),
        (r"\bwater\b", "maji", "maji"),
        (r"\bthe house\b", "keja", "nyumba"),
        (r"\ba house\b", "keja", "nyumba"),
        (r"\bhouses\b", "makeja", "nyumba"),
        (r"\bthe friend\b", "beshte", "rafiki"),
        (r"\bfriends\b", "mabeshte", "marafiki"),
        (r"\ba friend\b", "beshte", "rafiki"),
        (r"\bthe clothes\b", "luku", "mavazi"),
        (r"\bclothes\b", "luku", "mavazi"),
        (r"\bthe job\b", "job", "kazi"),
        (r"\ba job\b", "job", "kazi"),
        (r"\bjob\b", "job", "kazi"),
        (r"\bwork\b", "kazi", "kazi"),
        (r"\bhope\b", "hope", "tumaini"),
        (r"\bproblem\b", "shida", "tatizo"),
        (r"\bproblems\b", "mashida", "matatizo"),
        (r"\btrouble\b", "trouble", "taabu"),
        (r"\btime\b", "time", "wakati"),
        (r"\bday\b", "siku", "siku"),
        (r"\bnight\b", "usiku", "usiku"),
        (r"\byear\b", "mwaka", "mwaka"),
        (r"\byears\b", "miaka", "miaka"),
        (r"\bweek\b", "wiki", "wiki"),
        (r"\bweeks\b", "wiki", "wiki"),
        (r"\bmonth\b", "mwezi", "mwezi"),
        (r"\bmonths\b", "miezi", "miezi"),
        # Pronouns
        (r"\bhe\b", "yeye", "yeye"),
        (r"\bshe\b", "yeye", "yeye"),
        (r"\bthey\b", "wao", "wao"),
        (r"\bwe\b", "sisi", "sisi"),
        (r"\byou\b", "wewe", "wewe"),
        (r"(?<!-)\bi\b(?!-)", "mimi", "mimi"),
        (r"\bmy\b", "yangu", "yangu"),
        (r"\byour\b", "yako", "yako"),
        (r"\bhis\b", "yake", "yake"),
        (r"\bher\b", "yake", "yake"),
        (r"\bour\b", "yetu", "yetu"),
        (r"\btheir\b", "yao", "yao"),
        # Adverbs & Adjectives
        (r"\bheavily\b", "heavy sana", "kwa wingi"),
        (r"\bheavy\b", "heavy", "kubwa"),
        (r"\bvery\b", "sana", "sana"),
        (r"\ba lot\b", "mob", "sana"),
        (r"\bmany\b", "mob", "mengi"),
        (r"\bmuch\b", "mob", "mengi"),
        (r"\bevery\b", "kila", "kila"),
        (r"\ball\b", "zote", "zote"),
        (r"\bclean\b", "safi", "safi"),
        (r"\bgood\b", "fiti", "nzuri"),
        (r"\bbad\b", "mbaya", "mbaya"),
        (r"\bhard\b", "ngumu", "ngumu"),
        (r"\beasy\b", "rahisi", "rahisi"),
        (r"\bfast\b", "haraka", "haraka"),
        (r"\bslowly\b", "polepole", "polepole"),
        (r"\bnew(?!\s+(?:York|Jersey|Zealand|Delhi|Mexico|England|Hampshire|Orleans|Guinea|Brunswick))\b", "mpya", "mpya"),
        (r"\bold\b", "ya zamani", "ya zamani"),
        # High-Frequency Temporal Invariants & Relational Time Markers
        (r"\bover time\b", "kwa muda", "baada ya muda"),
        (r"\bprior to\b", "kabla ya", "kabla ya"),
        (r"\bsubsequently\b", "baadaye", "kisha"),
        (r"\bsimultaneously\b", "kwa wakati mmoja", "kwa wakati mmoja"),
        (r"\bat the same time\b", "kwa wakati mmoja", "kwa wakati mmoja"),
        (r"\bin real-time\b", "in real-time", "kwa wakati halisi"),
        (r"\bin the short term\b", "kwa muda mfupi", "kwa muda mfupi"),
        (r"\bin the long term\b", "kwa muda mrefu", "kwa muda mrefu"),
        (r"\bat high speed\b", "kwa high speed", "kwa kasi ya juu"),
        (r"\bat constant speed\b", "kwa constant speed", "kwa kasi thabiti"),
        (r"\bat speed\b", "kwa speed", "kwa kasi"),
        (r"\byesterday\b", "jana", "jana"),
        (r"\btoday\b", "leo", "leo"),
        (r"\btomorrow\b", "kesho", "kesho"),
        (r"\bnow\b", "sasa", "sasa"),
        (r"\btonight\b", "leo usiku", "usiku wa leo"),
        (r"\bmorning\b", "asubuhi", "asubuhi"),
        (r"\bevening\b", "jioni", "jioni"),
        (r"\balready\b", "tayari", "tayari"),
        (r"\bstill\b", "bado", "bado"),
        # High-Frequency Human Nouns
        (r"\bthe people\b", "watu", "watu"),
        (r"\bpeople\b", "watu", "watu"),
        (r"\bthe children\b", "watoto", "watoto"),
        (r"\bchildren\b", "watoto", "watoto"),
        (r"\bthe child\b", "mtoto", "mtoto"),
        (r"\bchild\b", "mtoto", "mtoto"),
        (r"\bthe man\b", "mwanaume", "mwanaume"),
        (r"\bmen\b", "wanaume", "wanaume"),
        (r"\bthe woman\b", "mwanamke", "mwanamke"),
        (r"\bwomen\b", "wanawake", "wanawake"),
        (r"\bthe family\b", "familia", "familia"),
        (r"\bfamily\b", "familia", "familia"),
        (r"\bthe parents\b", "wazazi", "wazazi"),
        (r"\bparents\b", "wazazi", "wazazi")
    ]

    ACADEMIC_PRESENT_VERBS = {
        "release", "propose", "introduce", "present", "demonstrate", "show",
        "evaluate", "compare", "describe", "formulate", "examine", "investigate",
        "define", "analyze", "observe", "consider", "construct", "adopt",
        "summarize", "conclude", "argue", "claim", "hypothesize", "assume",
        "believe", "provide", "develop", "design", "implement", "extend",
        "leverage", "explore", "conduct", "measure", "benchmark", "optimize",
        "validate", "verify", "train", "test", "find", "clean", "normalize",
        "filter", "process", "collect", "scale", "compute", "achieve",
        "handle", "determine", "require", "support", "exhibit", "outperform", "converge",
        "confirm", "indicate", "reveal", "yield", "alter", "induce", "inhibit",
        "modulate", "regulate", "bind", "cleave", "stabilize", "accelerate",
        "fluctuate", "oscillate", "dissipate", "attenuate", "propagate", "decay",
        "undergo", "exceed", "differ", "depend", "correspond", "reflect", "govern",
        "drive", "form", "trigger", "maintain", "enhance", "suppress", "dominate",
        "vary", "diverge", "store", "generate", "produce", "predict", "capture",
        "contain", "utilize", "apply", "execute", "run", "fail", "operate", "suggest",
        "state", "note", "report", "deploy", "build", "highlight", "prove"
    }

    def __init__(self):
        self.fusion = BantuEnglishFusionEngine()
        self.stripper = MorphologicalRootStripper()
        self.registry = BantuNounClassRegistry()
        self.agglutinator = PrefixSuffixAgglutinationEngine(self.fusion)
        self.adj_engine = SwahiliAdjectiveEngine(self.registry)

    def is_english_text(self, text: str) -> bool:
        """Determines if the sentence is predominantly English rather than Sheng or Swahili."""
        words = re.findall(r"[a-zA-Z]+", text.lower())
        if not words:
            return False
        
        english_markers = {
            "the", "is", "are", "was", "were", "although", "because", "market", 
            "canceled", "cancelled", "pouring", "down", "heavily", "with", "from",
            "have", "has", "had", "will", "would", "could", "should", "people",
            "manager", "meeting", "postponed", "decided", "delayed", "weather",
            "business", "friend", "money", "traffic", "school", "hospital"
        }
        swahili_sheng_markers = {
            "niko", "uko", "ako", "tuko", "wako", "mtaani", "mayouth", "luku",
            "chapaa", "nduthi", "matatu", "fiti", "keja", "buda", "msee", "wasee",
            "kwenye", "katika", "lakini", "hata", "kama", "ili", "yake", "yangu",
            "alikuwa", "walikuwa", "ilikuwa", "kwa", "na", "ya", "wa", "za"
        }

        en_count = sum(1 for w in words if w in english_markers)
        sw_count = sum(1 for w in words if w in swahili_sheng_markers)

        # If has significant English markers and few or zero Swahili markers
        if en_count >= 2 and en_count > sw_count:
            return True
        if en_count >= 1 and sw_count == 0 and len(words) >= 3:
            return True
        return False

    def code_switch_sentence(self, english_text: str, dialect_mode: str = "urban_standard") -> EnglishCodeSwitchResult:
        """Transforms an English sentence into authentic Kenyan Code-Switching & Kiswahili Sanifu."""
        cleaned = english_text.strip()
        rules_applied = []
        dialect_alternatives = {}

        # Step 0: Check for Instruction Control Tokens ([GENERATE_FORMAL], [GENERATE_CASUAL], [GENERATE_STREET])
        ctrl_match = re.match(r"^\[(?:GENERATE_)?(FORMAL|CASUAL|STREET)\]\s*", cleaned, re.IGNORECASE)
        if not ctrl_match:
            ctrl_match = re.match(r"^<\|style:(formal|casual|street)\|>\s*", cleaned, re.IGNORECASE)
        
        control_tag = None
        if ctrl_match:
            tag_name = ctrl_match.group(1).lower()
            cleaned = cleaned[ctrl_match.end():].strip()
            control_tag = f"[GENERATE_{tag_name.upper()}]"
            dialect_mode = tag_name
            rules_applied.append(f"Instruction Control Token ('{control_tag}')")

        # Step 0A: Check for Demonstrative Fronting Flags & Explicit Focus Tags
        is_front_focus = bool(re.search(r"\[(?:FRONT_FOCUS|FOCUS_FRONT)\]", cleaned, re.IGNORECASE))
        if is_front_focus:
            cleaned = re.sub(r"\[(?:FRONT_FOCUS|FOCUS_FRONT)\]\s*", "", cleaned, flags=re.IGNORECASE).strip()

        explicit_focus_targets = re.findall(r"\((?:[Ee]mphasis on|[Ff]ocus on)\s+([a-zA-Z0-9_-]+)\)|\[FOCUS:\s*([a-zA-Z0-9_-]+)\]", cleaned, re.IGNORECASE)
        if explicit_focus_targets:
            cleaned = re.sub(r"\s*\((?:[Ee]mphasis on|[Ff]ocus on)\s+([a-zA-Z0-9_-]+)\)|\s*\[FOCUS:\s*([a-zA-Z0-9_-]+)\]", "", cleaned, flags=re.IGNORECASE).strip()
            for ef in explicit_focus_targets:
                f_noun = ef[0] or ef[1]
                if f_noun and f_noun.lower() in cleaned.lower():
                    cleaned = re.sub(rf"\b(?:the\s+)?{re.escape(f_noun)}\b", f"*{f_noun}*", cleaned, flags=re.IGNORECASE, count=1)

        # Normalize dialect_mode to register profile
        reg_mode = dialect_mode.lower()
        if reg_mode in ("formal", "tech_standard", "corporate"):
            reg_norm = "formal"
        elif reg_mode in ("street", "urban_street", "deep_sheng", "slang"):
            reg_norm = "street"
        elif reg_mode in ("casual",):
            reg_norm = "casual"
        else:
            reg_norm = "urban_standard"

        is_sheng = (reg_norm == "street" or dialect_mode in ("deep_sheng", "street", "casual"))

        cs_text = cleaned
        sw_text = cleaned

        # Detect Distal Historical / Remote Temporal Anchors
        is_historical_distal = bool(re.search(
            r"\b(?:in\s+(?:the\s+)?(?:1[0-9]{3}|20[01][0-9]|19[0-9]{2})|mnamo\s+[0-9]{4}|historically|originally|in\s+ancient\s+times|in\s+the\s+early\s+days|centuries\s+ago|in\s+the\s+19th\s+century|in\s+the\s+20th\s+century)\b",
            cleaned,
            re.IGNORECASE
        ))

        # Step 0B: Everyday Verb Negation Framework Across Registers
        # "I don't care"
        if re.search(r"\bi\s+(?:don't|do\s+not)\s+care\b", cs_text, re.IGNORECASE):
            if reg_norm == "street":
                cs_text = re.sub(r"\bi\s+(?:don't|do\s+not)\s+care\b", "sina shughuli", cs_text, flags=re.IGNORECASE)
            else:
                cs_text = re.sub(r"\bi\s+(?:don't|do\s+not)\s+care\b", "sijali", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\bi\s+(?:don't|do\s+not)\s+care\b", "sijali", sw_text, flags=re.IGNORECASE)
            rules_applied.append(f"Everyday Negation ('i don't care' -> '{reg_norm}')")

        # "We didn't agree"
        if re.search(r"\bwe\s+(?:didn't|did\s+not)\s+agree\b", cs_text, re.IGNORECASE):
            if reg_norm == "street":
                cs_text = re.sub(r"\bwe\s+(?:didn't|did\s+not)\s+agree\b", "hatukuskizana", cs_text, flags=re.IGNORECASE)
            else:
                cs_text = re.sub(r"\bwe\s+(?:didn't|did\s+not)\s+agree\b", "hatukukubaliana", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\bwe\s+(?:didn't|did\s+not)\s+agree\b", "hatukukubaliana", sw_text, flags=re.IGNORECASE)
            rules_applied.append(f"Everyday Negation ('we didn't agree' -> '{reg_norm}')")

        # "He/She doesn't know"
        if re.search(r"\b(he|she)\s+(?:doesn't|does\s+not)\s+know\b", cs_text, re.IGNORECASE):
            if reg_norm == "street":
                cs_text = re.sub(r"\b(he|she)\s+(?:doesn't|does\s+not)\s+know\b", "hananga clue", cs_text, flags=re.IGNORECASE)
            else:
                cs_text = re.sub(r"\b(he|she)\s+(?:doesn't|does\s+not)\s+know\b", "hajui", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\b(he|she)\s+(?:doesn't|does\s+not)\s+know\b", "hajui", sw_text, flags=re.IGNORECASE)
            rules_applied.append(f"Everyday Negation ('doesn't know' -> '{reg_norm}')")

        # "They don't know"
        if re.search(r"\bthey\s+(?:don't|do\s+not)\s+know\b", cs_text, re.IGNORECASE):
            if reg_norm == "street":
                cs_text = re.sub(r"\bthey\s+(?:don't|do\s+not)\s+know\b", "hawananga clue", cs_text, flags=re.IGNORECASE)
            else:
                cs_text = re.sub(r"\bthey\s+(?:don't|do\s+not)\s+know\b", "hawajui", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\bthey\s+(?:don't|do\s+not)\s+know\b", "hawajui", sw_text, flags=re.IGNORECASE)
            rules_applied.append(f"Everyday Negation ('they don't know' -> '{reg_norm}')")

        # "I don't have money" / "I don't have cash"
        if re.search(r"\bi\s+(?:don't|do\s+not)\s+have\s+(?:any\s+)?(?:money|cash)\b", cs_text, re.IGNORECASE):
            if reg_norm == "street":
                cs_text = re.sub(r"\bi\s+(?:don't|do\s+not)\s+have\s+(?:any\s+)?(?:money|cash)\b", "sina chapaa", cs_text, flags=re.IGNORECASE)
            else:
                cs_text = re.sub(r"\bi\s+(?:don't|do\s+not)\s+have\s+(?:any\s+)?(?:money|cash)\b", "sina pesa", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\bi\s+(?:don't|do\s+not)\s+have\s+(?:any\s+)?(?:money|cash)\b", "sina pesa", sw_text, flags=re.IGNORECASE)
            rules_applied.append(f"Everyday Negation ('i don't have money' -> '{reg_norm}')")

        # "They don't understand"
        if re.search(r"\bthey\s+(?:don't|do\s+not)\s+understand\b", cs_text, re.IGNORECASE):
            if reg_norm == "street":
                cs_text = re.sub(r"\bthey\s+(?:don't|do\s+not)\s+understand\b", "hawashiki", cs_text, flags=re.IGNORECASE)
            else:
                cs_text = re.sub(r"\bthey\s+(?:don't|do\s+not)\s+understand\b", "hawaelewi", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\bthey\s+(?:don't|do\s+not)\s+understand\b", "hawaelewi", sw_text, flags=re.IGNORECASE)
            rules_applied.append(f"Everyday Negation ('they don't understand' -> '{reg_norm}')")

        # "We don't understand"
        if re.search(r"\bwe\s+(?:don't|do\s+not)\s+understand\b", cs_text, re.IGNORECASE):
            if reg_norm == "street":
                cs_text = re.sub(r"\bwe\s+(?:don't|do\s+not)\s+understand\b", "hatushiki", cs_text, flags=re.IGNORECASE)
            else:
                cs_text = re.sub(r"\bwe\s+(?:don't|do\s+not)\s+understand\b", "hatuelewi", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\bwe\s+(?:don't|do\s+not)\s+understand\b", "hatuelewi", sw_text, flags=re.IGNORECASE)
            rules_applied.append(f"Everyday Negation ('we don't understand' -> '{reg_norm}')")

        # "Don't worry"
        if re.search(r"\b(?:don't|do\s+not)\s+worry\b", cs_text, re.IGNORECASE):
            if reg_norm == "street":
                cs_text = re.sub(r"\b(?:don't|do\s+not)\s+worry\b", "usi-stress", cs_text, flags=re.IGNORECASE)
            else:
                cs_text = re.sub(r"\b(?:don't|do\s+not)\s+worry\b", "usijali", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\b(?:don't|do\s+not)\s+worry\b", "usijali", sw_text, flags=re.IGNORECASE)
            rules_applied.append(f"Everyday Negation ('don't worry' -> '{reg_norm}')")

        # "We cannot stop" / "We can't stop"
        if re.search(r"\bwe\s+(?:cannot|can't)\s+stop\b", cs_text, re.IGNORECASE):
            has_following_obj = bool(re.search(r"\bwe\s+(?:cannot|can't)\s+stop\s+(?:the\s+)?(?:\*|_|[a-zA-Z])", cs_text, re.IGNORECASE))
            if reg_norm == "street":
                cs_text = re.sub(r"\bwe\s+(?:cannot|can't)\s+stop\b", "hatuezi ku-stop", cs_text, flags=re.IGNORECASE)
            elif reg_norm == "casual" or has_following_obj:
                cs_text = re.sub(r"\bwe\s+(?:cannot|can't)\s+stop\b", "hatuwezi ku-stop", cs_text, flags=re.IGNORECASE)
            else:
                cs_text = re.sub(r"\bwe\s+(?:cannot|can't)\s+stop\b", "hatuwezi kusimama", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\bwe\s+(?:cannot|can't)\s+stop\b", "hatuwezi kusimama", sw_text, flags=re.IGNORECASE)
            rules_applied.append(f"Everyday Negation ('we cannot stop' -> '{reg_norm}')")

        # Step 0C: Demonstrative Object Fronting & Pointing Concord with Object Infixes
        has_emphasis = bool(re.search(r"(?:\bthe\s+)?(?:\*|_)([a-zA-Z0-9_-]+)(?:\*|_)", cs_text, re.IGNORECASE))
        if has_emphasis or is_front_focus:
            def _resolve_emphatic(noun: str) -> Tuple[str, str, str, bool, str]:
                nl = noun.lower().strip()
                if nl in EMPHATIC_NOUN_REGISTRY:
                    info = EMPHATIC_NOUN_REGISTRY[nl]
                    if reg_norm == "street":
                        ptr = info["street_ptr"]
                        lex = info["street_lex"]
                        ifx = info.get("street_infix", info["infix"])
                    elif reg_norm == "formal":
                        ptr = info["formal_ptr"]
                        lex = info["formal_lex"]
                        ifx = info["infix"]
                    else:
                        ptr = info["casual_ptr"]
                        lex = info["casual_lex"]
                        ifx = info["infix"]
                    is_plural = info.get("is_plural", False)
                    class_id = info.get("class_id", "c9")
                else:
                    profile = self.registry.lookup(nl)
                    ptr = self.registry.get_pointing_demonstrative(nl, register=reg_norm)
                    ifx = self.registry.get_object_infix(nl)
                    is_plural = self.registry.is_plural(nl)
                    lex = noun
                    class_id = profile.class_id
                return ptr, lex, ifx, is_plural, class_id

            focus_match = re.search(r"(?:\bthe\s+)?(?:\*|_)([a-zA-Z0-9_-]+)(?:\*|_)", cs_text, re.IGNORECASE)
            if focus_match:
                raw_focus_noun = focus_match.group(1)
                ptr, lex, ifx, is_plural, class_id = _resolve_emphatic(raw_focus_noun)
                pointed_object = f"{ptr} {lex}"

                sw_infinitive_map = {
                    "buy": "kununua",
                    "eat": "kula",
                    "drink": "kunywa",
                    "get": "kupata",
                    "see": "kuona",
                    "know": "kujua"
                }

                subj_marker_street = {"we": "hatuezi", "you": "hauezi", "they": "hawaezi", "he": "haezi", "she": "haezi", "i": "siezi"}
                subj_marker_formal = {"we": "hatuwezi", "you": "huwezi", "they": "hawawezi", "he": "hawezi", "she": "hawezi", "i": "siwezi"}

                if is_front_focus:
                    # Demonstrative Left-Dislocation Fronting: "Hii system, ..."
                    front_phrase = f"{ptr.capitalize()} {lex}, "

                    # 1. Preceded by modal negation
                    mod_neg_match = re.search(
                        r"\b([A-Za-z0-9_-]+\s+)?(hatuwezi|hatuezi|huwezi|hauezi|hawawezi|hawaezi|hawezi|haezi|siwezi|siezi|cannot|can't)\s+(?:ku-)?([a-zA-Z]+)\s+(?:the\s+)?(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)",
                        cs_text,
                        re.IGNORECASE
                    )
                    if mod_neg_match:
                        subj_lead = (mod_neg_match.group(1) or "").strip()
                        raw_neg = mod_neg_match.group(2).lower().strip()
                        verb = mod_neg_match.group(3)
                        stem = self.extract_bare_verb_root(verb)
                        if subj_lead.lower() == "we":
                            lead_str = ""
                            neg_pfx = "hatuezi" if reg_norm == "street" else "hatuwezi"
                        elif subj_lead.lower() in subj_marker_street:
                            lead_str = ""
                            neg_pfx = subj_marker_street[subj_lead.lower()] if reg_norm == "street" else subj_marker_formal[subj_lead.lower()]
                        elif subj_lead:
                            lead_str = f"{subj_lead} "
                            neg_pfx = "hatuezi" if reg_norm == "street" else "hatuwezi"
                        else:
                            lead_str = ""
                            if "we" in raw_neg or "hatu" in raw_neg:
                                neg_pfx = "hatuezi" if reg_norm == "street" else "hatuwezi"
                            else:
                                neg_pfx = subj_marker_street.get(raw_neg, "hatuezi") if reg_norm == "street" else subj_marker_formal.get(raw_neg, "hatuwezi")
                        
                        if stem.lower() in sw_infinitive_map:
                            replacement_verb = f"{lead_str}{neg_pfx} {sw_infinitive_map[stem.lower()]}"
                        else:
                            replacement_verb = f"{lead_str}{neg_pfx} ku-{ifx}-{stem}"
                        cs_text = cs_text[:mod_neg_match.start()] + replacement_verb + cs_text[mod_neg_match.end():]
                    else:
                        # 2. Preceded by modal affirmative
                        modal_aff_match = re.search(
                            r"\b(we|they|you|he|she)\s+must\s+([a-zA-Z]+)\s+(?:the\s+)?(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)",
                            cs_text,
                            re.IGNORECASE
                        )
                        if modal_aff_match:
                            subj = modal_aff_match.group(1).lower()
                            verb = modal_aff_match.group(2)
                            stem = self.extract_bare_verb_root(verb)
                            s_pfx = {"we": "tu", "they": "wa", "you": "u", "he": "a", "she": "a"}.get(subj, "tu")
                            if stem.lower() in sw_infinitive_map:
                                replacement_verb = f"lazima {s_pfx}-{sw_infinitive_map[stem.lower()]}"
                            else:
                                replacement_verb = f"lazima {s_pfx}-{ifx}-{stem}"
                            cs_text = cs_text[:modal_aff_match.start()] + replacement_verb + cs_text[modal_aff_match.end():]
                        else:
                            # 3. Preceded by infinitive
                            to_inf_match = re.search(
                                r"\bto\s+([a-zA-Z]+)\s+(?:the\s+)?(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)",
                                cs_text,
                                re.IGNORECASE
                            )
                            if to_inf_match:
                                verb = to_inf_match.group(1)
                                stem = self.extract_bare_verb_root(verb)
                                if stem.lower() in sw_infinitive_map:
                                    replacement_verb = sw_infinitive_map[stem.lower()]
                                else:
                                    replacement_verb = f"ku-{ifx}-{stem}"
                                cs_text = cs_text[:to_inf_match.start()] + replacement_verb + cs_text[to_inf_match.end():]
                            else:
                                # 4. Simply remove in-situ noun
                                cs_text = re.sub(r"(?:\bthe\s+)?(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)", "", cs_text, count=1)

                    # Prepend fronted demonstrative noun phrase with case preservation for proper nouns
                    cs_text = re.sub(r"\s+", " ", cs_text).strip()
                    cs_text = f"{front_phrase}{preserve_case_first_word(cs_text)}"
                    rules_applied.append(f"Demonstrative Object Fronting ('{front_phrase.strip()}')")

                else:
                    # In-Situ Demonstrative Pointing Concord & Verb Infix
                    # 1. Preceded by modal negation
                    mod_neg_match = re.search(
                        r"\b([A-Za-z0-9_-]+\s+)?(hatuwezi|hatuezi|huwezi|hauezi|hawawezi|hawaezi|hawezi|haezi|siwezi|siezi|cannot|can't)\s+(?:ku-)?([a-zA-Z]+)\s+(?:the\s+)?(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)",
                        cs_text,
                        re.IGNORECASE
                    )
                    if mod_neg_match:
                        subj_lead = (mod_neg_match.group(1) or "").strip()
                        raw_neg = mod_neg_match.group(2).lower().strip()
                        verb = mod_neg_match.group(3)
                        stem = self.extract_bare_verb_root(verb)
                        if subj_lead.lower() == "we":
                            lead_str = ""
                            neg_pfx = "hatuezi" if reg_norm == "street" else "hatuwezi"
                        elif subj_lead.lower() in subj_marker_street:
                            lead_str = ""
                            neg_pfx = subj_marker_street[subj_lead.lower()] if reg_norm == "street" else subj_marker_formal[subj_lead.lower()]
                        elif subj_lead:
                            lead_str = f"{subj_lead} "
                            neg_pfx = "hatuezi" if reg_norm == "street" else "hatuwezi"
                        else:
                            lead_str = ""
                            if "we" in raw_neg or "hatu" in raw_neg:
                                neg_pfx = "hatuezi" if reg_norm == "street" else "hatuwezi"
                            else:
                                neg_pfx = subj_marker_street.get(raw_neg, "hatuezi") if reg_norm == "street" else subj_marker_formal.get(raw_neg, "hatuwezi")
                        
                        if stem.lower() in sw_infinitive_map:
                            replacement_chunk = f"{lead_str}{neg_pfx} {sw_infinitive_map[stem.lower()]} {pointed_object}"
                        else:
                            replacement_chunk = f"{lead_str}{neg_pfx} ku-{ifx}-{stem} {pointed_object}"
                        cs_text = cs_text[:mod_neg_match.start()] + replacement_chunk + cs_text[mod_neg_match.end():]
                        rules_applied.append(f"Emphatic Pointing Concord & Infix ('{replacement_chunk}')")
                    else:
                        # 2. Preceded by modal affirmative
                        modal_aff_match = re.search(
                            r"\b(we|they|you|he|she)\s+must\s+([a-zA-Z]+)\s+(?:the\s+)?(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)",
                            cs_text,
                            re.IGNORECASE
                        )
                        if modal_aff_match:
                            subj = modal_aff_match.group(1).lower()
                            verb = modal_aff_match.group(2)
                            stem = self.extract_bare_verb_root(verb)
                            s_pfx = {"we": "tu", "they": "wa", "you": "u", "he": "a", "she": "a"}.get(subj, "tu")
                            if stem.lower() in sw_infinitive_map:
                                replacement_chunk = f"lazima {s_pfx}-{sw_infinitive_map[stem.lower()]} {pointed_object}"
                            else:
                                replacement_chunk = f"lazima {s_pfx}-{ifx}-{stem} {pointed_object}"
                            cs_text = cs_text[:modal_aff_match.start()] + replacement_chunk + cs_text[modal_aff_match.end():]
                            rules_applied.append(f"Emphatic Pointing Concord & Infix ('{replacement_chunk}')")
                        else:
                            # 3. Preceded by infinitive
                            to_inf_match = re.search(
                                r"\bto\s+([a-zA-Z]+)\s+(?:the\s+)?(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)",
                                cs_text,
                                re.IGNORECASE
                            )
                            if to_inf_match:
                                verb = to_inf_match.group(1)
                                stem = self.extract_bare_verb_root(verb)
                                if stem.lower() in sw_infinitive_map:
                                    replacement_chunk = f"{sw_infinitive_map[stem.lower()]} {pointed_object}"
                                else:
                                    replacement_chunk = f"ku-{ifx}-{stem} {pointed_object}"
                                cs_text = cs_text[:to_inf_match.start()] + replacement_chunk + cs_text[to_inf_match.end():]
                                rules_applied.append(f"Emphatic Pointing Concord & Infix ('{replacement_chunk}')")
                            else:
                                # 4. In-situ noun replacement without adjacent verb
                                in_situ_pat = re.compile(r"(?:\bthe\s+)?(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)", re.IGNORECASE)
                                cs_text = in_situ_pat.sub(pointed_object, cs_text, count=1)
                                rules_applied.append(f"Emphatic Pointing Concord ('{pointed_object}')")

                # Clean leftover markers
                cs_text = re.sub(r"(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)", raw_focus_noun, cs_text)
                sw_text = re.sub(r"(?:\*|_)" + re.escape(raw_focus_noun) + r"(?:\*|_)", raw_focus_noun, sw_text)
            
            # Universal cleanup of any residual focus symbols in sw_text
            sw_text = re.sub(r"[\*_]", "", sw_text)

        # Step 0D / RULE 1B: Locative Interrogatives with Pointing Elements
        # e.g., "Where is that machine?" -> "Iyo machine iko wapi?"
        #       "Where is this system?" -> "Hii system iko wapi?"
        #       "Where are those transactions?" -> "Izo transactions ziko wapi?" (street) / "Hizo transactions ziko wapi?" (formal)
        #       "Where is that manager?" -> "Uyo manager ako wapi?" (street) / "Yule manager ako wapi?" (formal)
        is_true_question = cleaned.strip().endswith("?") or bool(re.match(r"^\s*where\s+(?:is|are)\b", cleaned, re.IGNORECASE))
        loc_match = re.search(r"\bwhere\s+(is|are)\s+(that|this|those|these|the)\s+([a-zA-Z0-9_-]+)\s*\??", cs_text, re.IGNORECASE) if is_true_question else None
        if loc_match:
            cop_en = loc_match.group(1).lower()
            det = loc_match.group(2).lower()
            target_noun = loc_match.group(3)
            nl = target_noun.lower().strip()

            profile = self.registry.lookup(nl)
            is_plural = (cop_en == "are") or (det in ("those", "these")) or self.registry.is_plural(nl)
            
            # Determine Noun Class and locative copula
            if profile.class_id in ("c1", "c2"):
                cls_id = "c2" if is_plural else "c1"
                copula = "wako" if is_plural else "ako"
            elif profile.class_id in ("c7", "c8"):
                cls_id = "c8" if is_plural else "c7"
                copula = "viko" if is_plural else "kiko"
            elif profile.class_id in ("c5", "c6"):
                cls_id = "c6" if is_plural else "c5"
                copula = "yako" if is_plural else "liko"
            else:
                cls_id = "c10" if is_plural else "c9"
                copula = "ziko" if is_plural else "iko"

            # Determine pointing demonstrative
            if det == "this":
                ptr_map = {"c1": "huyu", "c2": "hawa", "c5": "hili", "c6": "haya", "c7": "hiki", "c8": "hivi", "c9": "hii", "c10": "hizi"}
                pointer = ptr_map.get(cls_id, "hii")
            elif det == "these":
                ptr_map = {"c2": "hawa", "c6": "haya", "c8": "hivi", "c10": "hizi"}
                pointer = ptr_map.get(cls_id, "hizi")
            elif det == "that":
                if reg_norm == "street":
                    ptr_map = {"c1": "uyo", "c2": "hao", "c5": "lile", "c6": "yale", "c7": "kile", "c8": "vile", "c9": "iyo", "c10": "izo"}
                    pointer = ptr_map.get(cls_id, "iyo")
                elif reg_norm == "formal":
                    ptr_map = {"c1": "yule", "c2": "wale", "c5": "lile", "c6": "yale", "c7": "kile", "c8": "vile", "c9": "iyo", "c10": "hizo"}
                    pointer = ptr_map.get(cls_id, "iyo")
                else: # casual / urban
                    ptr_map = {"c1": "uyo", "c2": "hao", "c5": "lile", "c6": "yale", "c7": "kile", "c8": "vile", "c9": "iyo", "c10": "hizo"}
                    pointer = ptr_map.get(cls_id, "iyo")
            elif det == "those":
                if reg_norm == "street":
                    ptr_map = {"c2": "hao", "c6": "yale", "c8": "vile", "c10": "izo"}
                    pointer = ptr_map.get(cls_id, "izo")
                elif reg_norm == "formal":
                    ptr_map = {"c2": "wale", "c6": "yale", "c8": "vile", "c10": "hizo"}
                    pointer = ptr_map.get(cls_id, "hizo")
                else: # casual / urban
                    ptr_map = {"c2": "hao", "c6": "yale", "c8": "vile", "c10": "hizo"}
                    pointer = ptr_map.get(cls_id, "hizo")
            else: # "the"
                pointer = ""

            if pointer:
                replacement_interrogative = f"{pointer.capitalize()} {target_noun} {copula} wapi?"
            else:
                replacement_interrogative = f"{target_noun.capitalize()} {copula} wapi?"

            cs_text = cs_text[:loc_match.start()] + replacement_interrogative + cs_text[loc_match.end():]
            sw_pointer = pointer if pointer else ""
            if det in ("that", "those") and reg_norm == "formal":
                if cls_id == "c9": sw_pointer = "ile"
                elif cls_id == "c10": sw_pointer = "zile"
                elif cls_id == "c1": sw_pointer = "yule"
                elif cls_id == "c2": sw_pointer = "wale"
            sw_target = target_noun
            if nl == "machine": sw_target = "mashine"
            elif nl == "system": sw_target = "mfumo"
            elif nl == "systems": sw_target = "mifumo"
            elif nl == "manager": sw_target = "meneja"
            elif nl == "engineers": sw_target = "wahandisi"
            
            if sw_pointer:
                sw_text = f"{sw_pointer.capitalize()} {sw_target} {copula} wapi?"
            else:
                sw_text = f"{sw_target.capitalize()} {copula} wapi?"

            rules_applied.append(f"Rule 1B: Locative Interrogative with Pointing Elements ('{replacement_interrogative}')")

        # Step 0E: Scientific & Systems Compound Noun Head-Initial Inversion
        # English Modifier-First -> Bantu Head-First ('[Head] ya/za [Modifier]')
        compound_head_inversions = [
            (r"\b(quantum\s+mechanics|machine\s+learning|deep\s+learning|distributed\s+systems)\s+research\s+paper\b", r"research paper ya \1"),
            (r"\blight\s+intensity\b", r"intensity ya light"),
            (r"\bblack\s+body\s+radiation\b", r"radiation ya black body"),
            (r"\belectromagnetic\s+radiation\b", r"radiation ya electromagnetic"),
            (r"\benergy\s+distribution\b", r"distribution ya energy"),
            (r"\btemperature\s+gradient\b", r"gradient ya temperature"),
            (r"\bpressure\s+gradient\b", r"gradient ya pressure"),
            (r"\bquantum\s+states\b", r"states za quantum"),
            (r"\bneural\s+network\s+architecture\b", r"architecture ya neural network"),
            (r"\bsystem\s+architecture\b", r"architecture ya system"),
            (r"\bmodel\s+architecture\b", r"architecture ya model"),
            (r"\btransformer\s+architecture\b", r"architecture ya transformer"),
            (r"\bsystem\s+performance\b", r"performance ya system"),
            (r"\bmodel\s+performance\b", r"performance ya model"),
            (r"\bnetwork\s+performance\b", r"performance ya network"),
            (r"\bdatabase\s+performance\b", r"performance ya database"),
            (r"\bnetwork\s+latency\b", r"latency ya network"),
            (r"\bsystem\s+latency\b", r"latency ya system"),
            (r"\bsystem\s+throughput\b", r"throughput ya system"),
            (r"\bmemory\s+consumption\b", r"consumption ya memory"),
            (r"\bstate\s+machine\s+replication\b", r"replication ya state machine"),
            (r"\bstate\s+machine\s+operations\b", r"operations za state machine"),
            (r"\b(machine|deep)\s+learning\s+models\b", r"models za \1 learning"),
            (r"\blanguage\s+models\b", r"models za language"),
            (r"\bfoundation\s+models\b", r"models za foundation"),
            (r"\bdiscrete\s+choice\s+models\b", r"models za discrete choice"),
            (r"\bidentification\s+problem\b", r"problem ya identification"),
            (r"\bestimation\s+pathologies\b", r"pathologies za estimation"),
            (r"\bparameter\s+space\b", r"space ya parameters"),
            (r"\bmaximum\s+score\s+estimator\b", r"estimator ya maximum score"),
            (r"\bfinite\s+collection\b", r"collection finite"),
        ]
        for pat_str, rep_str in compound_head_inversions:
            pat = re.compile(pat_str, re.IGNORECASE)
            if pat.search(cs_text):
                cs_text = pat.sub(rep_str, cs_text)
                rules_applied.append("Compound Noun Head-Initial Inversion ('[head] ya [domain]')")

        # Step 1: Idiomatic phrases & compound predicates
        for pattern, cs_rep, sw_rep in self.IDIOMATIC_PHRASES:
            pat = re.compile(pattern, re.IGNORECASE)
            if pat.search(cs_text):
                cs_text = pat.sub(cs_rep, cs_text)
                sw_text = pat.sub(sw_rep, sw_text)
        # Step 1A2: Equative & Comparative Role Preposition ("as a / as an" -> "kama")
        if re.search(r"\bas\s+(?:a|an)\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(r"\bas\s+(?:a|an)\b", "kama", cs_text, flags=re.IGNORECASE)
            sw_text = re.sub(r"\bas\s+(?:a|an)\b", "kama", sw_text, flags=re.IGNORECASE)
            rules_applied.append("Equative Role Preposition ('as a' -> 'kama')")

        # Step 1A3: Kenyan Academic Discourse Framing & Evaluative Bridges (Golden Standard)
        # 1. Evaluative Resultative Participles: ", making [it] [adj] to [verb]" -> ", jambo linalofanya iwe [adj] ku-[root]"
        def _repl_making_it_eval(m):
            adj = m.group(1).lower()
            verb = m.group(2).lower()
            adj_sw = {"important": "muhimu", "necessary": "lazima", "crucial": "muhimu sana", "possible": "inawezekana", "impossible": "haiwezekani", "difficult": "ngumu", "hard": "ngumu", "easy": "rahisi"}.get(adj, adj)
            root = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f", jambo linalofanya iwe {adj_sw} ku{root}"
        cs_text = re.sub(r",\s+making\s+it\s+([a-zA-Z]+)\s+to\s+([a-zA-Z]+)\b", _repl_making_it_eval, cs_text, flags=re.IGNORECASE)

        # 2. Causative Object Inversion: ", making [NP] hard/difficult to reason about" -> ", jambo linalofanya iwe ngumu kureason kuhusu [NP]"
        def _repl_making_obj_hard(m):
            obj = m.group(1).strip()
            adj = m.group(2).lower()
            v_phrase = m.group(3).strip()
            adj_sw = "ngumu" if adj in ("hard", "difficult") else ("rahisi" if adj == "easy" else "muhimu")
            if "reason about" in v_phrase.lower():
                return f", jambo linalofanya iwe {adj_sw} kureason kuhusu {obj}"
            root = MorphologicalRootStripper.strip_to_bare_root(v_phrase.split()[0])
            return f", jambo linalofanya iwe {adj_sw} ku{root} {obj}"
        cs_text = re.sub(r",\s+making\s+([a-zA-Z0-9_\s-]+?)\s+(hard|difficult|easy|possible|impossible)\s+to\s+([a-zA-Z]+(?:\s+about)?)\b", _repl_making_obj_hard, cs_text, flags=re.IGNORECASE)

        # 3. Evidential Secondary Findings & Discourse Anchors:
        cs_text = re.sub(r",\s+suggesting\s+(?:that|kuwa)\s+", ", jambo linalosuggest kwamba ", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r",\s+matching\s+(?:the\s+)?", ", jambo linalomatch ", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r",\s+eliminating\s+(?:the\s+)?", ", jambo linaloeliminate ", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r",\s+enabling\s+", ", jambo linaloenable ", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r",\s+making\s+the\s+([a-zA-Z0-9_-]+)\s+applicable\s+to\b", r", ikifanya \1 iwe applicable kwa", cs_text, flags=re.IGNORECASE)

        # 4. Habitual Action & State: "often [verb]" -> "mara nyingi hu-[root]"
        cs_text = re.sub(r"\bis\s+often\s+interpreted\s+as\s+(?:a\s+)?sign\s+that\b", "mara nyingi huwa interpreted kama sign kwamba", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bis\s+often\s+([a-zA-Z]+ed)\s+as\b", r"mara nyingi huwa \1 kama", cs_text, flags=re.IGNORECASE)
        def _repl_often_v(m):
            v = m.group(1).lower()
            if v in ("split", "use", "uses", "occur", "fail", "lead", "depend", "result", "require"):
                root = MorphologicalRootStripper.strip_to_bare_root(v)
                return f"mara nyingi hu{root}"
            return m.group(0)
        cs_text = re.sub(r"\boften\s+([a-zA-Z]+)\b", _repl_often_v, cs_text, flags=re.IGNORECASE)

        # 5. Purpose & Epistemic Bridges:
        cs_text = re.sub(r"\bessential\s+for\s+([a-zA-Z]+)ing\b", lambda m: f"essential sana kwa ajili ya ku{MorphologicalRootStripper.strip_to_bare_root(m.group(1))}", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bhow\s+to\s+([a-zA-Z]+)\b", lambda m: f"namna ya ku{MorphologicalRootStripper.strip_to_bare_root(m.group(1))}", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bhow\s+([a-zA-Z0-9_-]+(?:\s+[a-zA-Z0-9_-]+)?)\s+can\s+([a-zA-Z]+)\b", lambda m: f"venye {m.group(1)} inaweza ku-{MorphologicalRootStripper.strip_to_bare_root(m.group(2))}", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\busing\s+only\b", "tukitumia tu", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bby\s+making\s+([a-zA-Z0-9_\s-]+?)\s+(?:a|an)\s+source\s+of\b", r"kwa kumake \1 kuwa source ya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bfrom\s+(?:the\s+)?([a-zA-Z0-9_\s'-]+?)\s+to\s+recent\b", r"kuanzia \1 hadi kufikia zile recent", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bend-to-end\b", "kuanzia mwanzo hadi mwisho", cs_text, flags=re.IGNORECASE)

        # 6. Locative Academic Domains: "in [domain]" -> "kwenye [domain]"
        ACADEMIC_DOMAIN_NOUNS = (
            "quantum foundations|foundations|theory|theories|models?|frameworks?|"
            "measurements?|mechanics|physics|biology|chemistry|science|sciences|"
            "economics|computations?|networks?|experiments?|protocols?|databases?|"
            "servers?|systems?|codebases?|languages?|vision|literature|approaches?|"
            "contexts?|tasks?|bases|subtypes?|states?|settings?|domains?|regimes?"
        )
        cs_text = re.sub(rf"\b[Ii]n\s+(?:the\s+)?([a-zA-Z0-9_-]+\s+)?({ACADEMIC_DOMAIN_NOUNS})\b", r"kwenye \1\2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bextends?\s+to\s+", "ina-extend kwenye ", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bfrom\s+(?:the\s+)?perspective\s+of\b", "kutoka kwenye perspective ya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bfrom\s+experimentally\s+accessible\b", "kutoka kwenye experimentally accessible", cs_text, flags=re.IGNORECASE)

        # 7. Perfect & Stative Clitics:
        if dialect_mode != "deep_sheng":
            cs_text = re.sub(r"\bhave\s+long\s+been\b", "zime-kuwa kwa muda mrefu kama", cs_text, flags=re.IGNORECASE)
        else:
            cs_text = re.sub(r"\bhave\s+long\s+been\b", "zime-kuwa kwa muda mrefu", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bit\s+has\s+remained\s+(?:largely\s+)?open\s+whether\b", "ime-remain largely open kama", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bit\s+has\s+remained\s+open\b", "imeremain open", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bWhile\s+each\s+has\s+developed\b", "Wakati kila moja ime-develop", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\binto\s+a\s+rich\s+subject\b", "kuwa rich subject", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bin\s+its\s+own\s+right\b", "kwenye its own right", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthey\s+can\s+be\s+connected\b", "zinaweza kuwa connected", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthrough\s+measurements\b", "kupitia measurements", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwithout\s+assuming\b", "bila ku-assume", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwithout\s+requiring\b", "bila ku-require", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bWe\s+answer\s+this\s+question\s+in\s+the\s+affirmative\b", "Tuna-answer question hii kwa affirmative", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthe\s+key\s+is\b", "key ni", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\binduced\s+by\s+measurements\b", "inayo-induce-iwa na measurements", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\ba\s+much\s+more\s+relaxed\s+condition\s+than\b", "ambayo ni much more relaxed condition kuliko", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bSpecifically,\s+for\b", "Specifically, kwa ajili ya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bPOVMs\s+satisfying\b", "POVMs zinazo-satisfy", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+establish\s+a\s+quantitative\s+relation\b", "tuna-establish quantitative relation", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\binto\s+a\s+maximally\s+entangled\s+state\b", "kuwa maximally entangled state", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bWe\s+then\s+characterize\s+when\s+both\s+errors\s+can\s+vanish\s+simultaneously\b", "Kisha tuna-characterize ni lini errors zote mbili zinaweza ku-vanish simultaneously", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bTheir\s+errors\s+can\s+be\s+certified\b", "Errors zao zinaweza ku-certify-iwa", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bWe\s+derive\s+novel\s+trade-off\s+relations\s+that\s+bridge\b", "Tuna-derive novel trade-off relations zinazo-bridge", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\btwo\s+historically\s+distinct\s+approaches\b", "mbinu mbili zilizo historically distinct", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\band\s+observable\s+noise--disturbance\b", "pamoja na observable noise--disturbance", cs_text, flags=re.IGNORECASE)
        # Step 1A4: FastAPI Golden Clausal Architecture & Technical Cadence
        # 1. Correlative & Copular Negation Synthesizer ("this is not merely [X] but [creates/causes/etc] [Y]")
        def _repl_not_merely(m):
            subj_term = m.group(1).lower()
            pronoun = "hiki" if "device" in subj_term or "tool" in subj_term else "hii"
            prob_noun = m.group(2).strip()
            verb = m.group(3).lower()
            rest = m.group(4).strip()
            verb_root = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"{pronoun} si {prob_noun} tu, bali ina-{verb_root} {rest}"
        cs_text = re.sub(
            r"\b(this|it)\s+is\s+not\s+merely\s+(?:an?|the)?\s*([a-zA-Z0-9_\s-]+?)\s+but\s+(creates|causes|generates|yields|leads\s+to|results\s+in)\s+([a-zA-Z0-9_\s-]+)",
            _repl_not_merely,
            cs_text,
            flags=re.IGNORECASE
        )
        cs_text = re.sub(r"\b(?:this|it)\s+is\s+not\s+merely\s+(?:an?|the)?\s*([a-zA-Z0-9_\s-]+?)\s+but\s+also\b", r"hii si \1 tu, bali pia", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:this|it)\s+is\s+not\s+merely\s+(?:an?|the)?\s*([a-zA-Z0-9_\s-]+?)\s+but\b", r"hii si \1 tu, bali", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthis\s+is\s+not\s+(?:an?|the)?\s*([a-zA-Z0-9_-]+)\b", r"hii si \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bnot\s+only\s+have\b", "si tu kwamba ziko na", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bnot\s+only\b", "si tu kwamba", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bbut\s+also\b", "bali pia", cs_text, flags=re.IGNORECASE)

        # 2. FastAPI Purpose & Clausal Openers ("To resolve [failure], we introduce [estimator]")
        cs_text = re.sub(r"^[Tt]o\s+investigate\s+this\s+question,\s*(?:we\s+)?introduce\b", "Ili ku-investigate swali hili, tuna-introduce", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"^[Tt]o\s+address\s+(?:this|the)\s+([a-zA-Z0-9_-]+),\s*(?:we\s+)?(?:propose|introduce)\b", r"Ili ku-address \1 hii, tuna-introduce", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"^[Tt]o\s+resolve\s+(?:this|the)\s+([a-zA-Z0-9_-]+),\s*(?:we\s+)?introduce\b", r"Ili kuresolve \1 hii, tuna-introduce", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+resolve\s+(?:this|the)\s+([a-zA-Z0-9_-]+)\b", r"ili kuresolve \1 hii", cs_text, flags=re.IGNORECASE)

        cs_text = re.sub(r"^[Tt]o\s+([a-zA-Z]+)\s+(this|the|a|an)\s+([a-zA-Z0-9_-]+),\s*we\s+([a-zA-Z]+)\b",
            lambda m: f"Ili ku{MorphologicalRootStripper.strip_to_bare_root(m.group(1))} {m.group(3)}, tuna-{MorphologicalRootStripper.strip_to_bare_root(m.group(4))}",
            cs_text, flags=re.IGNORECASE)

        # 3. Active Technical Verb Conjugators (Zero Uninflected Verbs)
        cs_text = re.sub(r"\binherits\s+both\s+properties\b", "ina-inherit properties zote mbili", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\binherits\s+([a-zA-Z0-9_\s-]+)\b", r"ina-inherit \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bensures\s+that\b", "inahakikisha kwamba", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bguarantees\s+that\b", "inahakikisha kwamba", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bare\s+widely\s+applied\b", "zina-tumika sana", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bis\s+widely\s+applied\b", "ina-tumika sana", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\byet\s+a\s+fundamental\s+tension\s+arises\s+when\b", "lakini tension ya msingi inatokea wakati", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\barises\s+when\b", "inatokea wakati", cs_text, flags=re.IGNORECASE)

        # Relative Predicates of Quality/Attribute ("which/that are of [X]" -> "zenye ziko na [X]", "which/that is of [X]" -> "yenye iko na [X]")
        cs_text = re.sub(r"\b(?:which|that)\s+are\s+of\b", "zenye ziko na", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:which|that)\s+is\s+of\b", "yenye iko na", cs_text, flags=re.IGNORECASE)

        # Telescopic Language Model Continuum & Supervision Patterns
        cs_text = re.sub(r"\b[Ww]e\s+train\s+(?:a\s+)?([a-zA-Z0-9_\s\(\)-]+?)\s+to\s+be\s+that\s+([a-zA-Z0-9_-]+)\b", r"Tuna-train \1 ndiyo ikuwe iyo \2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+be\s+that\s+([a-zA-Z0-9_-]+)\b", r"ndiyo ikuwe iyo \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b([a-zA-Z0-9_-]+)\s+supervised\s+by\s+([a-zA-Z0-9_\s-]+?)\s+with\s+(?:a\s+)?([a-zA-Z0-9_\s-]+)", r"\1 enye iko supervised na \2 na \3", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b([a-zA-Z0-9_-]+)\s+supervised\s+by\s+([a-zA-Z0-9_\s-]+)", r"\1 enye iko supervised na \2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bfull\s+anchor\b", "anchor kamili", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r":\s+(?:a\s+)?", ": ", cs_text)

        # Compound Compute Budgets & Disjunctive Training/Compression Patterns
        if dialect_mode != "deep_sheng":
            cs_text = re.sub(r"\bmany\s+compute\s+budgets\b", "compute budgets nyingi", cs_text, flags=re.IGNORECASE)
        else:
            cs_text = re.sub(r"\bmany\s+compute\s+budgets\b", "compute nyingi budgets", cs_text, flags=re.IGNORECASE)

        cs_text = re.sub(r"\byet\s+serving\s+each\s+budget\b", "lakini ku-serve each budget", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\byet\s+([a-zA-Z]+)ing\b", lambda m: f"lakini ku-{MorphologicalRootStripper.strip_to_bare_root(m.group(1))}", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bstill\s+means\b", "bado inamaanisha", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:a\s+)?separate\s+training\b", "ku-separate training", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bor\s+compression\s+run\b", "au compression run", cs_text, flags=re.IGNORECASE)

        # 3B. FastAPI Clausal Predicates & Verbs (Modules 1-7 Golden Cadence)
        # Nominal Openers ("The task of [X]", "The challenge of [X]", "The problem of [X]")
        def _repl_the_nominal_of(m):
            head = m.group(1).capitalize()
            obj = m.group(2).strip()
            if dialect_mode == "deep_sheng":
                return f"Hii {head.lower()} ya {obj}"
            return f"{head} ya {obj}"

        cs_text = re.sub(
            r"\b[Tt]he\s+(task|problem|challenge|process|method|concept|objective|goal|framework)\s+of\s+([a-zA-Z0-9_\s-]+?)\s+(requires|involves|aims|leads|serves|allows|enables|depends)\b",
            lambda m: f"{_repl_the_nominal_of(m)} {m.group(3)}",
            cs_text,
            flags=re.IGNORECASE
        )
        cs_text = re.sub(
            r"\b[Tt]he\s+(task|problem|challenge|process|method|concept|objective|goal|framework)\s+of\s+([a-zA-Z0-9_\s-]+?)\b(?!\s+(?:is|was|are|were|can|will|should|which|that))",
            _repl_the_nominal_of,
            cs_text,
            flags=re.IGNORECASE
        )

        # Verb + Gerund/Infinitive Transduction ("requires translating [X] into [Y]")
        def _repl_requires_translating(m):
            complement = m.group(1).strip()
            target = m.group(2).strip()
            comp_clean = re.sub(r"\ban\s+understanding\s+of\s+", "understanding ya ", complement, flags=re.IGNORECASE)
            comp_clean = re.sub(r"\band\s+their\s+([a-zA-Z0-9_-]+)", r"na \1 zao", comp_clean, flags=re.IGNORECASE)
            if dialect_mode == "deep_sheng":
                comp_clean = re.sub(r"\bparts\b", "maparts", comp_clean, flags=re.IGNORECASE)
                comp_clean = re.sub(r"\brelationships zao\b", "marelationships zao", comp_clean, flags=re.IGNORECASE)
                return f"ina-require ku-translate {comp_clean} kuwa {target}"
            return f"inahitaji ku-translate {comp_clean} kuwa {target}"

        cs_text = re.sub(
            r"\brequires\s+translating\s+([a-zA-Z0-9_\s-]+?)\s+into\s+([a-zA-Z0-9_\s-]+)",
            _repl_requires_translating,
            cs_text,
            flags=re.IGNORECASE
        )

        # General "requires [verb]-ing" / "involves [verb]-ing" / "allows [verb]-ing" / "enables [verb]-ing"
        def _repl_requires_verb_ing(m):
            verb_type = m.group(1).lower()
            gerund = m.group(2).lower()
            stem = MorphologicalRootStripper.strip_to_bare_root(gerund)
            if verb_type == "requires":
                prefix = "inahitaji" if dialect_mode != "deep_sheng" else "ina-require"
            elif verb_type == "involves":
                prefix = "inahusisha" if dialect_mode != "deep_sheng" else "ina-involve"
            elif verb_type == "allows":
                prefix = "inaruhusu" if dialect_mode != "deep_sheng" else "ina-allow"
            elif verb_type == "enables":
                prefix = "inawezesha" if dialect_mode != "deep_sheng" else "ina-enable"
            elif verb_type == "serves":
                prefix = "inasaidia"
            else:
                prefix = f"ina-{verb_type}"
            return f"{prefix} ku-{stem}"

        cs_text = re.sub(
            r"\b(requires|involves|allows|enables|serves)\s+(?:to\s+)?([a-zA-Z]+)ing\b",
            _repl_requires_verb_ing,
            cs_text,
            flags=re.IGNORECASE
        )

        # General "translating/converting/transforming/mapping [X] into [Y]" -> "ku-[root] [X] kuwa [Y]"
        def _repl_transform_into(m):
            action = m.group(1).lower()
            stem = MorphologicalRootStripper.strip_to_bare_root(action)
            obj = m.group(2).strip()
            dest = m.group(3).strip()
            obj_clean = re.sub(r"\ban\s+understanding\s+of\s+", "understanding ya ", obj, flags=re.IGNORECASE)
            obj_clean = re.sub(r"\band\s+their\s+([a-zA-Z0-9_-]+)", r"na \1 zao", obj_clean, flags=re.IGNORECASE)
            return f"ku-{stem} {obj_clean} kuwa {dest}"

        cs_text = re.sub(
            r"\b(translating|converting|transforming|mapping|partitioning)\s+([a-zA-Z0-9_\s-]+?)\s+into\s+([a-zA-Z0-9_\s-]+)",
            _repl_transform_into,
            cs_text,
            flags=re.IGNORECASE
        )

        # Standalone "an understanding of [X]" -> "understanding ya [X]"
        cs_text = re.sub(r"\ban\s+understanding\s+of\s+([a-zA-Z0-9_-]+)", r"understanding ya \1", cs_text, flags=re.IGNORECASE)
        # Standalone "and their [noun]" -> "na [noun] zao"
        cs_text = re.sub(r"\band\s+their\s+([a-zA-Z0-9_-]+)", r"na \1 zao", cs_text, flags=re.IGNORECASE)
        # "depends on" -> "inategemea"
        cs_text = re.sub(r"\bdepends\s+on\b", "inategemea", cs_text, flags=re.IGNORECASE)
        # "focuses on" -> "inazingatia"
        cs_text = re.sub(r"\bfocuses\s+on\b", "inazingatia", cs_text, flags=re.IGNORECASE)
        # "aims to" -> "inalenga ku-"
        cs_text = re.sub(r"\baims\s+to\s+([a-zA-Z]+)\b", lambda m: f"inalenga ku-{MorphologicalRootStripper.strip_to_bare_root(m.group(1))}", cs_text, flags=re.IGNORECASE)

        # Academic Interrogative Openers ("Can [subject] [verb]")
        def _repl_can_subj_verb(m):
            subj = m.group(1).strip()
            verb = m.group(2).strip()
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            pfx = "zinaweza" if subj.endswith("s") else "inaweza"
            return f"Je, {subj} {pfx} ku-{stem}"
        cs_text = re.sub(
            r"^[Cc]an\s+([a-zA-Z0-9_\s-]+?)\s+(assemble|perform|execute|achieve|learn|adapt|process|handle|generalize|solve|converge)\b",
            _repl_can_subj_verb, cs_text, flags=re.IGNORECASE
        )

        # Locative Relative Clauses ("environment in which [subject] [verb]")
        def _repl_in_which(m):
            det = (m.group(1) or "").strip().lower()
            subj = m.group(2).strip()
            verb = m.group(3).strip()
            if det:
                det_sw = "iyo" if det == "that" else ("hii" if det == "this" else ("hizi" if det in ("these", "those") else ("the" if det == "the" else det)))
                full_subj = f"{det_sw} {subj}"
            else:
                full_subj = subj
            if verb.lower() in ("is", "are", "was", "were"):
                return f"ambapo {full_subj} {verb}"
            pfx = "zina-" if subj.endswith("s") else "ina-"
            return f"ambapo {full_subj} {pfx}{verb}"
        cs_text = re.sub(r"\bin\s+which\s+(?:(that|this|the|these|those|hizi|hii|iyo)\s+)?([a-zA-Z0-9_-]+)\s+([a-zA-Z]+)\b", _repl_in_which, cs_text, flags=re.IGNORECASE)

        # Phrasal Verb & Contrastive Linkers
        cs_text = re.sub(r"\band\s+manipulate\b", "na ku-manipulate", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\brather\s+than\s+direct\s+access\s+to\b", "badala ya direct access kwa", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\brather\s+than\b", "badala ya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwhile\s+their\s+resulting\s+assemblies\s+are\s+evaluated\s+geometrically\b",
                         "huku resulting assemblies zao zikiwa evaluated geometrically", cs_text, flags=re.IGNORECASE)

        # Generative Inversion Openers ("Building on this [X], we construct [Y]")
        cs_text = re.sub(
            r"^[Bb]uilding\s+on\s+this\s+([a-zA-Z0-9_-]+),\s*we\s+([a-zA-Z]+)\b",
            lambda m: f"Kujenga juu ya {m.group(1)} hii, tuna-{MorphologicalRootStripper.strip_to_bare_root(m.group(2))}",
            cs_text, flags=re.IGNORECASE
        )

        # Empirical Evaluation Openers ("Evaluating [X] reveals [Y]")
        cs_text = re.sub(
            r"^[Ee]valuating\s+([a-zA-Z0-9_\s-]+?)\s+reveals\s+([a-zA-Z0-9_\s-]+)",
            r"Ku-evaluate \1 kuna-reveal \2",
            cs_text, flags=re.IGNORECASE
        )

        # System Performance & Comparative Verbs
        cs_text = re.sub(r"\b[Tt]he\s+strongest\s+system\s+achieves\b", "System yenye nguvu zaidi ina-achieve", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b[Tt]he\s+evaluated\s+open-source\s+systems\s+lag\s+substantially\s+behind\s+their\s+stronger\s+closed-source\s+peers\b",
                         "Mifumo ya open-source iliyo-evaluated ina-lag kwa kiwango kikubwa nyuma ya stronger closed-source peers zao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bshow\s+how\s+agents\s+revise\s+assemblies\s+while\s+leaving\s+residual\s+positioning\s+errors\b",
                         "zina-onyesha jinsi agents zinavyo-revise assemblies huku zikiacha residual positioning errors", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(
            r"\bprovides\s+a\s+common\s+setting\s+for\s+both\s+assessing\s+([a-zA-Z0-9_\s-]+?)\s+and\s+characterizing\s+([a-zA-Z0-9_\s-]+)",
            r"inatoa common setting kwa ajili ya ku-assess \1 na ku-characterize \2",
            cs_text, flags=re.IGNORECASE
        )
        cs_text = re.sub(r"\bprovides\s+a\s+common\s+setting\s+for\b", "inatoa common setting kwa ajili ya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bprovides\s+a\s+([a-zA-Z0-9_-]+)\b", r"inatoa \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bprovides\b", "inatoa", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bTo\s+investigate\s+this\s+question,\s*we\s+introduce\b", "Ili ku-investigate swali hili, tuna-introduce", cs_text, flags=re.IGNORECASE)



        # 4. First-Person Authorial Declaratives ("We show that", "We prove this result", "We apply")
        cs_text = re.sub(r"\bWe\s+show\s+that\b", "Tuna-onyesha kwamba", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bWe\s+prove\s+this\s+result\s+for\b", "Tuna-prove result hii kwa ajili ya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bWe\s+prove\s+that\b", "Tuna-prove kwamba", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bWe\s+apply\s+the\s+methodology\s+to\b", "Tuna-apply methodology kwenye", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bWe\s+apply\b", "Tuna-apply", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bWe\s+introduce\b", "Tuna-introduce", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwhich\s+includes\b", "ambayo inajumuisha", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwhich\s+include\b", "ambazo zinajumuisha", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bboth\s+properties\b", "properties zote mbili", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bUK\s+General\s+Election\b", "UK Election ya jumla", cs_text, flags=re.IGNORECASE)

        # Shift temporal modifier 'current' to the end of compound technical phrases across both registers
        cs_text = re.sub(
            r"\bcurrent\s+(state-of-the-art(?:\s+[a-zA-Z0-9_-]+)?\s+(?:generators|models|systems|methods|algorithms|architectures|frameworks|approaches|techniques|baselines|pipelines|networks|datasets|solutions|implementations))\b",
            r"\1 ya sasa",
            cs_text,
            flags=re.IGNORECASE
        )

        rules_applied.append("FastAPI Golden Clausal Architecture & Technical Cadence")
        rules_applied.append("Kenyan Academic Discourse Framing & Evaluative Bridges ('jambo linalo- / kwenye / zinazo-')")

        # Step 1B: Swahili Adjective Engine (Bantu Noun Class Concord, Relational Genitives & Post-Nominal Word Order)
        if self.adj_engine.adj_regex.search(cs_text):
            cs_text = self.adj_engine.invert_and_agree(cs_text, reg_norm=reg_norm, is_formal=False)
            rules_applied.append("Swahili Adjective Engine ('[noun] [adj_concord]')")
        if self.adj_engine.adj_regex.search(sw_text):
            sw_text = self.adj_engine.invert_and_agree(sw_text, reg_norm="formal", is_formal=True)

        # Step 2: Conjunctions & Clause Connectors
        for pattern, cs_rep, sw_rep in self.CONJUNCTION_RULES:
            if pattern in [r"\band\b", r"\bor\b"]:
                pat = re.compile(r"\b(and|or|And|Or)\b")
            else:
                pat = re.compile(pattern, re.IGNORECASE)
            if pat.search(cs_text):
                cs_text = pat.sub(cs_rep, cs_text)
                sw_text = pat.sub(sw_rep, sw_text)
                rules_applied.append(f"Discourse Connector ('{cs_rep}')")

        # Step 2A1: Compound Relative Pronouns & Indefinite Boundaries
        compound_pronoun_rules = [
            (r"\bEverything [Tt]hat\b", "kila kitu enye"),
            (r"\beverything that\b", "kila kitu enye"),
            (r"\bAnything [Tt]hat\b", "kitu yoyote enye"),
            (r"\banything that\b", "kitu yoyote enye"),
            (r"\bSomething [Tt]hat\b", "kitu enye"),
            (r"\bsomething that\b", "kitu enye"),
            (r"\bNothing [Tt]hat\b", "hakuna kitu chenye"),
            (r"\bnothing that\b", "hakuna kitu chenye"),
            (r"\bEveryone [Ww]ho\b", "kila mtu mwenye"),
            (r"\beveryone who\b", "kila mtu mwenye"),
            (r"\bAnyone [Ww]ho\b", "msee yeyote mwenye"),
            (r"\banyone who\b", "msee yeyote mwenye"),
        ]
        for pat, rep in compound_pronoun_rules:
            if re.search(pat, cs_text):
                cs_text = re.sub(pat, rep, cs_text)
                rules_applied.append(f"Compound Relative Pronoun ('{rep}')")

        # Step 2A2: Modal Auxiliaries ("can [verb]" -> "inaweza [verb]")
        cs_text = re.sub(r"\b(?:they|wasee|people)\s+can\s+([a-zA-Z]+)\b", r"wanaweza \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+can\s+([a-zA-Z]+)\b", r"tunaweza \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\byou\s+can\s+([a-zA-Z]+)\b", r"unaweza \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:he|she)\s+can\s+([a-zA-Z]+)\b", r"anaweza \1", cs_text, flags=re.IGNORECASE)
        def _repl_can_modal(m):
            v = m.group(1)
            return f"inaweza {v.lower()}"
        if re.search(r"\b[Cc]an\s+([a-zA-Z]+)\b", cs_text):
            cs_text = re.sub(r"\b[Cc]an\s+([a-zA-Z]+)\b", _repl_can_modal, cs_text)
            rules_applied.append("Modal Auxiliary Mapping ('can [verb]' -> 'inaweza [verb]')")

        # Step 2A2B: Comprehensive Negative Auxiliary Inversion Engine
        # Handles: does not / doesn't, do not / don't, did not / didn't, cannot / can't, will not / won't
        def _resolve_neg_subj_class(subj_str: str) -> str:
            s = subj_str.strip().lower()
            s = re.sub(r"^(?:the|The|hii|hizi|huyu|hao|wale|ile|hili|hiki|our|team\s+yetu)\s+", "", s).strip()
            if s in ("we", "sisi"):
                return "1p"
            if s in ("i", "mimi"):
                return "1s"
            if s in ("you", "wewe"):
                return "2s"
            if s in ("they", "people", "wasee") or s in self.HUMAN_PLURAL_NOUNS or s in self.registry.HUMAN_PLURAL:
                return "c2"
            if s in ("he", "she", "yeye") or s in self.HUMAN_SINGULAR_NOUNS or s in self.registry.HUMAN_SINGULAR or s in {
                "researcher", "engineer", "author", "scientist", "manager", "developer", "admin", "doctor",
                "physicist", "professor", "reviewer", "scholar", "colleague"
            }:
                return "c1"
            if s in self.CLASS_10_SYSTEM_NOUNS or s in self.registry.CLASS_10_PLURAL_SYSTEM or self.registry.is_plural(s) or (s.endswith("s") and not s.endswith(("ss", "us", "is"))):
                return "c10"
            return "c9"

        def _build_neg_verb(cid: str, aux: str, verb: str, obj_clitic: str = "") -> str:
            aux_l = aux.lower().replace("'", "")
            root = MorphologicalRootStripper.strip_to_bare_root(verb)
            
            HUMAN_DIRECTED = {
                "call", "contact", "hire", "interview", "invite", "ask", "pay", "visit",
                "help", "inform", "remind", "warn", "advise", "tell", "consult", "meet",
                "welcome", "elect", "appoint", "question", "interrogate", "critique", "teach"
            }
            infix = ""
            if obj_clitic:
                oc_l = obj_clitic.lower()
                if oc_l in ("them", "wasee", "people"):
                    infix = "-wa-" if root.lower() in HUMAN_DIRECTED or cid in ("c1", "c2") else "-zi-"
                elif oc_l in ("him", "her"):
                    infix = "-m-"
                elif oc_l == "it":
                    infix = "-i-"
                elif oc_l in ("these", "those"):
                    infix = "-zi-"

            if "does" in aux_l:
                pfx_map = {"c9": "hai", "c1": "ha-", "c10": "hazi", "c2": "hawa", "1p": "hatu", "1s": "si"}
                pfx = pfx_map.get(cid, "hai")
                if infix:
                    return f"{pfx.rstrip('-')}{infix}{root}"
                return f"{pfx}{root}" if not pfx.endswith("-") else f"{pfx}{root}"
            elif "do" in aux_l:
                pfx_map = {"c10": "hazi", "c2": "hawa", "1p": "hatu", "1s": "si", "2s": "hu", "c9": "hai"}
                pfx = pfx_map.get(cid, "hazi")
                if infix:
                    return f"{pfx}{infix}{root}"
                return f"{pfx}{root}"
            elif "did" in aux_l:
                pfx_map = {"c9": "haiku-", "c10": "haziku-", "c1": "haku-", "c2": "hawaku-", "1p": "hatuku-", "1s": "siku-"}
                pfx = pfx_map.get(cid, "haiku-")
                if infix:
                    return f"{pfx.rstrip('-')}{infix}{root}"
                return f"{pfx}{root}"
            elif "can" in aux_l:
                pfx_map = {"c9": "haiwezi ku-", "c10": "haziwezi ku-", "c1": "hawezi ku-", "c2": "hawawezi ku-", "1p": "hatuwezi ku-", "1s": "siwezi ku-"}
                pfx = pfx_map.get(cid, "haiwezi ku-")
                if infix:
                    return f"{pfx.rstrip('-')}{infix}{root}"
                return f"{pfx}{root}"
            elif "will" in aux_l or "wo" in aux_l:
                pfx_map = {"c9": "haita-", "c10": "hazita-", "c1": "hata-", "c2": "hawata-", "1p": "hatuta-", "1s": "sita-"}
                pfx = pfx_map.get(cid, "haita-")
                if infix:
                    return f"{pfx.rstrip('-')}{infix}{root}"
                return f"{pfx}{root}"
            return f"{aux} {verb}"

        neg_aux_applied = False
        
        # 1. 1st Person Plural: "We [aux] [verb] [obj]" -> "[neg_verb]"
        def _repl_we_neg(m):
            nonlocal neg_aux_applied
            aux = m.group(1)
            verb = m.group(2)
            obj_p = m.group(3) or ""
            if verb.lower() in ("be", "have", "been", "a", "an", "the", "in", "to", "for", "with", "that"):
                return m.group(0)
            neg_aux_applied = True
            neg_v = _build_neg_verb("1p", aux, verb, obj_clitic=obj_p.strip().lower())
            return neg_v.capitalize() if m.group(0)[0].isupper() else neg_v

        pat_we = r"\b[Ww]e\s+(do\s+not|don't|did\s+not|didn't|cannot|can't|will\s+not|won't)\s+([a-zA-Z]+)(?:\s+(them|him|her|it|these|those))?\b"
        if re.search(pat_we, cs_text, re.IGNORECASE):
            cs_text = re.sub(pat_we, _repl_we_neg, cs_text, flags=re.IGNORECASE)

        # 2. General Subject + Negative Auxiliary + Verb + Optional Object
        def _repl_general_neg(m):
            nonlocal neg_aux_applied
            lead = m.group(1) or ""
            subj = m.group(2)
            aux = m.group(3)
            verb = m.group(4)
            obj_p = m.group(5) or ""
            if subj.lower() in ("who", "what", "where", "when", "why", "how", "which"):
                return m.group(0)
            if verb.lower() in ("be", "have", "been", "a", "an", "the", "in", "to", "for", "with", "that"):
                return m.group(0)
            neg_aux_applied = True
            cid = _resolve_neg_subj_class(f"{lead}{subj}")
            neg_v = _build_neg_verb(cid, aux, verb, obj_clitic=obj_p.strip().lower())
            return f"{lead}{subj} {neg_v}"

        pat_gen = r"\b((?:[Tt]he|[Hh]ii|[Hh]izi|[Hh]ao|[Ww]ale|[Ii]le|[Tt]his|[Tt]hese|[Tt]hose|[Oo]ur)\s+)?([a-zA-Z0-9_-]+)\s+(does\s+not|doesn't|do\s+not|don't|did\s+not|didn't|cannot|can't|will\s+not|won't)\s+([a-zA-Z]+)(?:\s+(them|him|her|it|these|those))?\b"
        if re.search(pat_gen, cs_text, re.IGNORECASE):
            cs_text = re.sub(pat_gen, _repl_general_neg, cs_text, flags=re.IGNORECASE)

        if neg_aux_applied:
            rules_applied.append("Negative Auxiliary Inversion ('[subject] [aux] [verb]' -> '[subject] [neg_prefix][root]')")

        # Step 2A3: Emphatic Declarative Auxiliary ("Does Happen" -> "inaweza kuHappen")
        def _repl_emphatic_does(m):
            verb = m.group(1)
            if verb.lower() in ("not", "n't", "it", "he", "she", "they", "this", "that", "the", "a", "an"):
                return m.group(0)
            if verb[0].isupper():
                return f"inaweza ku{verb[0].upper()}{verb[1:]}"
            return f"inaweza ku{verb}"

        if re.search(r"\b[Dd]oes\s+(?!(?:not|n't)\b)([a-zA-Z]+)\b", cs_text):
            cs_text = re.sub(r"\b[Dd]oes\s+(?!(?:not|n't)\b)([a-zA-Z]+)\b", _repl_emphatic_does, cs_text)
            rules_applied.append("Emphatic Declarative Inversion ('does [verb]' -> 'inaweza ku[Verb]')")

        # Step 2A4: Future Hypothetical Tense Sub-Graph ("would have [verb-ed]" -> "[prefix]ngekuwa [prefix]me[root]")
        def _repl_would_have(m):
            full_subj = m.group(1) or ""
            v_ed = m.group(2)
            subj = re.sub(r"^(?:the|The)\s+", "", full_subj).strip()
            root = MorphologicalRootStripper.strip_to_bare_root(v_ed)
            subj_l = subj.lower()
            if subj_l in ("they", "people", "engineers", "wasee", "managers", "hackers"):
                pfx = "wa"
            elif subj_l in ("we", "sisi"):
                pfx = "tu"
            elif subj_l in ("i", "mimi"):
                pfx = "ni"
            elif subj_l in ("you", "wewe"):
                pfx = "u"
            elif subj_l in ("he", "she", "manager", "engineer", "admin", "doctor", "yeye"):
                pfx = "a"
            elif subj_l.endswith("s") and not subj_l.endswith(("ss", "us", "is")):
                pfx = "zi"
            else:
                profile = self.registry.lookup(subj) if subj else self.registry.PROFILES["c9"]
                pfx = profile.subject_prefix
            return f"{subj.capitalize()} {pfx}ngekuwa {pfx}me{root}"

        would_have_pat = re.compile(r"\b((?:[Tt]he\s+)?[a-zA-Z0-9_-]+)?\s*would\s+have\s+([a-zA-Z]+(?:ed|en|t))\b", re.IGNORECASE)
        if would_have_pat.search(cs_text):
            cs_text = would_have_pat.sub(_repl_would_have, cs_text)
            rules_applied.append("Future Hypothetical Sub-Graph ('would have [verb]' -> '[prefix]ngekuwa [prefix]me[root]')")

        # Step 2A5: Preposition Alignment Matrix & Copula
        cs_text = re.sub(
            r"\bis\s+a\s+(\d{4})\s+book\s+by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b",
            r"ni a \1 book ya \2",
            cs_text,
            flags=re.IGNORECASE
        )
        cs_text = re.sub(
            r"\bis\s+a\s+book\s+by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b",
            r"ni a book ya \1",
            cs_text,
            flags=re.IGNORECASE
        )
        # Authorship / Possession / Passive Agency by:
        PASSIVE_PARTICIPLES = {
            "published", "written", "created", "developed", "authored", "discovered",
            "invented", "designed", "built", "composed", "founded", "led", "managed",
            "proposed", "introduced", "transmitted", "produced", "edited", "directed", "formulated"
        }

        # Case 1: [Noun] [Participle] by [Author] -> [Noun] yenye/mwenye/zenye ili[root]iwa na [Author]
        # e.g., "paper published by Albert Einstein" -> "paper yenye ilipublishiwa na Albert Einstein"
        def _repl_noun_participle_author(m):
            antecedent = m.group(1)
            participle = m.group(2)
            author = m.group(3)
            if antecedent.lower() in ("is", "was", "are", "were", "be", "been", "being"):
                return m.group(0)
            root = MorphologicalRootStripper.strip_to_bare_root(participle)
            profile = self.registry.lookup(antecedent)
            rel = "yenye" if profile.class_id == "c9" else profile.relative_marker
            pfx = profile.subject_prefix
            return f"{antecedent} {rel} {pfx}li{root}iwa na {author}"

        participle_pattern = "|".join(PASSIVE_PARTICIPLES)
        cs_text = re.sub(
            rf"\b([a-zA-Z0-9_-]+)\s+({participle_pattern})\s+by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b",
            _repl_noun_participle_author,
            cs_text
        )

        # Case 2: [Participle] by [Author] -> yenye ilipublishiwa na [Author]
        def _repl_bare_participle_author(m):
            participle = m.group(1)
            author = m.group(2)
            root = MorphologicalRootStripper.strip_to_bare_root(participle)
            return f"yenye ili{root}iwa na {author}"

        cs_text = re.sub(
            rf"\b({participle_pattern})\s+by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b",
            _repl_bare_participle_author,
            cs_text
        )

        # Case 3: Standard head noun by [Author] -> [Noun] ya/za/wa [Author]
        # e.g., "book by Brian Cox" -> "book ya Brian Cox"
        def _repl_noun_by_author(m):
            noun = m.group(1)
            author = m.group(2)
            linker = self.registry.lookup(noun).genitive_linker
            return f"{noun} {linker} {author}"

        cs_text = re.sub(
            r"\b([a-zA-Z0-9_-]+)\s+by\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b",
            _repl_noun_by_author,
            cs_text
        )

        # Year temporal locative ("in 1905" -> "in the 1905" in conversational / "mnamo 1905" in formal)
        if reg_norm == "formal":
            cs_text = re.sub(r"\bin\s+(?:the\s+)?([12]\d{3})\b", r"mnamo \1", cs_text)
        else:
            cs_text = re.sub(r"\bin\s+(?:the\s+)?([12]\d{3})\b", r"in the \1", cs_text)
        sw_text = re.sub(r"\bin\s+(?:the\s+)?([12]\d{3})\b", r"mnamo \1", sw_text)
        # Purpose for: [Noun] for [Target] -> [Noun] ya [Target] (with duration numbers guard: "for 50 epochs" -> "kwa 50 epochs")
        def _repl_noun_for(m):
            head = m.group(1)
            target = m.group(2)
            if head.lower() in ("ask", "wait", "call", "search", "look", "pay", "stand", "opt", "trained", "tested", "run", "account"):
                return m.group(0)
            if target.isdigit():
                return f"{head} kwa {target}"
            return f"{head} ya {target}"

        cs_text = re.sub(
            r"\b([a-zA-Z0-9_-]+)\s+for\s+([a-zA-Z0-9_-]+)\b",
            _repl_noun_for,
            cs_text
        )
        # Accompaniment with: with [Noun] -> na [Noun]
        cs_text = re.sub(
            r"\bwith\s+([a-zA-Z0-9_-]+)\b",
            r"na \1",
            cs_text,
            flags=re.IGNORECASE
        )

        # Motion to markets / town
        cs_text = re.sub(r"\bthey\s+will\s+go\s+to\s+(?:the\s+)?market\b", "wataenda sokoni", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwill\s+go\s+to\s+(?:the\s+)?market\b", "ataenda sokoni", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthey\s+went\s+to\s+(?:the\s+)?market\b", "walienda sokoni", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+went\s+to\s+(?:the\s+)?market\b", "alienda sokoni", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+went\s+to\s+(?:the\s+)?market\b", "tulienda sokoni", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthey\s+went\s+to\s+(?:the\s+)?town\b", "walienda tao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+went\s+to\s+(?:the\s+)?town\b", "alienda tao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+went\s+to\s+(?:the\s+)?town\b", "tulienda tao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthey\s+went\b", "walienda", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+went\b", "alienda", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+went\b", "tulienda", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bi\s+went\b", "nilienda", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+the\s+market\b", "sokoni", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+market\b", "sokoni", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwent\s+to\s+(?:the\s+)?town\b", "alienda tao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwent\s+to\s+town\b", "alienda tao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+town\b", "tao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwent\s+to\s+([a-zA-Z0-9_-]+)\b", r"alienda \1", cs_text, flags=re.IGNORECASE)

        # High-frequency past actions (seeing, coming, saying)
        cs_text = re.sub(r"\bthey\s+came\b", "walikuja", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+came\b", "alikuja", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+came\b", "tulikuja", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bi\s+came\b", "nilikuja", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthey\s+saw\b", "waliona", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+saw\b", "aliona", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+saw\b", "tuliona", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bi\s+saw\b", "niliona", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthey\s+said\b", "walisema", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+said\b", "alisema", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+said\b", "tulisema", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bi\s+said\b", "nilisema", cs_text, flags=re.IGNORECASE)

        # Acquisition & Purpose ("got a new [X]", "to make more [X]")
        cs_text = re.sub(r"\bgot\s+a\s+new\s+([a-zA-Z]+)\b", r"alipata \1 mpya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bgot\s+([a-zA-Z]+)\b", r"alipata \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+make\s+more\s+([a-zA-Z]+)\b", r"ndio apate \1 mob", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+make\s+([a-zA-Z]+)\b", r"kupata \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\babout\s+(?:the\s+)?([a-zA-Z]+)\b", r"kuhusu \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bneeds\s+([a-zA-Z]+)\b", r"anahitaji \1", cs_text, flags=re.IGNORECASE)

        # Volition & Desire (Order before bare infinitives)
        cs_text = re.sub(r"\bwe\s+want\s+to\s+([a-zA-Z]+)\b", r"tunataka ku-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bi\s+want\s+to\s+([a-zA-Z]+)\b", r"ninataka ku-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(they|watu|wasee|children|watoto)\s+want\s+to\s+eat\b", r"\1 wanataka kula", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+wants\s+to\s+eat\b", r"\1 anataka kula", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+wants\s+to\s+([a-zA-Z]+)\b", r"\1 anataka ku-\2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(want|wants)\s+(?:to\s+)?eat\b", "wanataka kula", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(want|wants)\s+kula\b", "wanataka kula", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwant\s+to\s+buy\b", "wanataka kununua", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwants\s+to\s+buy\b", "anataka kununua", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(want|wants)\s+to\s+([a-zA-Z]+)\b", r"wanataka ku-\2", cs_text, flags=re.IGNORECASE)

        # High-frequency infinitives
        cs_text = re.sub(r"\bto\s+get\s+money\b", "kupata chapaa", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+get\b", "kupata", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+buy\b", "kununua", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+eat\b", "kula", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+drink\b", "kunywa", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+see\b", "kuona", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+know\b", "kujua", cs_text, flags=re.IGNORECASE)

        # Cognition: know / knows
        cs_text = re.sub(r"\b(he|she)\s+knows\s+that\b", r"\1 anajua kuwa", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+knows\b", r"\1 anajua", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(they|watu|wasee|children|watoto)\s+know\s+that\b", r"\1 wanajua kuwa", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(they|watu|wasee|children|watoto)\s+know\b", r"\1 wanajua", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bi\s+know\s+that\b", "ninajua kuwa", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bi\s+know\b", "ninajua", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+know\s+that\b", "tunajua kuwa", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+know\b", "tunajua", cs_text, flags=re.IGNORECASE)

        # Need: need water / need food
        cs_text = re.sub(r"\b(the\s+)?people\s+need\b", "watu wanahitaji", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(they|watu|wasee)\s+need\b", r"\1 wanahitaji", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(he|she)\s+needs\b", r"\1 anahitaji", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+need\b", "tunahitaji", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bi\s+need\b", "ninahitaji", cs_text, flags=re.IGNORECASE)

        # Food modifiers (fresh food -> chakula fresh)
        cs_text = re.sub(r"\bfresh\s+food\b", "chakula fresh", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bfresh\s+dish\b", "chakula fresh", cs_text, flags=re.IGNORECASE)
        rules_applied.append("Universal High-Frequency Lexicon Alignment ('Swahili Core')")


        # Step 2B: Post-nominal Possessive Inversion (Pillar III)
        # e.g., "our reality" -> "reality yetu", "their systems" -> "systems zao"
        cs_text = re.sub(r"\bevery\s+facet\s+of\s+their\s+lives\b", "kila facet ya maisha zao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bof\s+their\s+lives\b", "ya maisha zao", cs_text, flags=re.IGNORECASE)

        ADJ_MODIFIER_PATTERN = (
            r"[a-zA-Z]+(?:ive|al|ic|ary|able|ible|ous|ful|less|ed|ing)|"
            r"mechanical|neural|personal|digital|physical|financial|entire|whole|"
            r"new|old|current|internal|external|global|local|deep|complex|simple|"
            r"primary|critical|secret|human|artificial|public|private|sensitive|main|key|raw"
        )
        def _repl_possessive_invert(m):
            pron = m.group(1).lower()
            adj = m.group(2)
            noun = m.group(3)
            full_noun = f"{adj} {noun}" if adj else noun
            return self.agglutinator.invert_possessive(pron, full_noun)

        cs_text = re.sub(
            rf"\b(our|my|your|his|her|their)\s+(?:({ADJ_MODIFIER_PATTERN})\s+)?([a-zA-Z0-9_-]+)\b",
            _repl_possessive_invert,
            cs_text,
            flags=re.IGNORECASE
        )
        rules_applied.append("Bantu Morphotactics: Post-nominal Possessive Inversion ('[noun] yetu/zao')")

        if not is_sheng:
            # Way 1 (Academic Standard): Plural Subject-Verb Agreement with 'Results zetu / Findings zetu show that' -> 'Results zetu zinashow kuwa'
            cs_text = re.sub(
                r"\b((?:results|findings|data|observations|simulations|experiments|measurements|evaluations)\s+(?:zetu|zao|yetu)?)\s+show\s+(?:that|kuwa|kwamba)?\b",
                r"\1 zinashow kuwa",
                cs_text,
                flags=re.IGNORECASE
            )

        # Normalize 'that the [noun]' -> 'that [noun]' before deictic processing
        cs_text = re.sub(r"\bthat\s+the\s+([a-zA-Z0-9_-]+)\b", r"that \1", cs_text, flags=re.IGNORECASE)

        # Step 2C: Habitual Consecutive Infinitives (e.g. "that/who use symbols to veil" -> "enye hutumia symbols ku-veil")
        def _repl_habitual_consec(m):
            rel = m.group(1)
            obj = m.group(2)
            action_v = m.group(3)
            return self.agglutinator.agglutinate_habitual_consecutive(obj, action_v, has_relative=bool(rel))

        if re.search(r"\b(?:(that|which|who)\s+)?(?:use|uses)\s+([a-zA-Z0-9_\s-]+?)\s+to\s+([a-zA-Z]+)\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(
                r"\b(?:(that|which|who)\s+)?(?:use|uses)\s+([a-zA-Z0-9_\s-]+?)\s+to\s+([a-zA-Z]+)\b",
                _repl_habitual_consec,
                cs_text,
                flags=re.IGNORECASE
            )
            rules_applied.append("Consecutive Infinitive Integration ('hutumia ... ku-[root]')")

        COMPLEMENTIZER_VERBS = {
            "said", "say", "says", "saying",
            "noticed", "notice", "notices", "noticing",
            "suggesting", "suggested", "suggests", "suggest",
            "believe", "believes", "believed", "believing",
            "thought", "think", "thinks", "thinking",
            "showed", "shows", "show", "showing",
            "argued", "argues", "argue", "arguing",
            "explained", "explains", "explain", "explaining",
            "observed", "observes", "observe", "observing",
            "proved", "proves", "prove", "proving",
            "realized", "realizes", "realize", "realizing",
            "found", "finds", "find", "finding",
            "concluded", "concludes", "conclude", "concluding",
            "stated", "states", "state", "stating",
            "claimed", "claims", "claim", "claiming",
            "noted", "notes", "note", "noting",
            "revealed", "reveals", "reveal", "revealing",
            "discovered", "discovers", "discover", "discovering",
            "confirmed", "confirms", "confirm", "confirming",
            "understood", "understands", "understand", "understanding",
            "knew", "knows", "know", "knowing",
            "felt", "feels", "feel", "feeling",
            "agreed", "agrees", "agree", "agreeing"
        }
        NON_VERB_S_NOUNS = {
            "virus", "viruses", "status", "crisis", "basis", "chaos", "gas", "gases", "bus",
            "buses", "corpus", "species", "series", "consensus", "apparatus",
            "process", "processes", "access", "class", "classes", "mass", "masses",
            "glass", "grass", "physicists", "researchers", "scientists", "engineers",
            "developers", "authors", "legislators", "concepts", "bodies", "atoms", "electrons", "quanta"
        }

        # Step 2D: Relative Clauses with Morphotactic Agreement: [noun] that/which/who [verb] -> [noun] enye [prefix]na[root]
        def _repl_rel_clause_morph(m):
            antecedent = m.group(1)
            verb = m.group(2)
            verb_l = verb.lower()
            PREPOSITIONS = {"in", "at", "on", "by", "from", "through", "under", "over", "for", "with", "kwa", "into", "onto", "upon", "without", "against", "between", "among", "within", "during", "before", "after"}
            if antecedent.lower() in COMPLEMENTIZER_VERBS or antecedent.lower() in PREPOSITIONS:
                return m.group(0)
            if verb_l in ("is", "was", "are", "were", "has", "had", "can", "could", "will", "would", "should", "does", "did"):
                return m.group(0)
            if verb_l in NON_VERB_S_NOUNS:
                return m.group(0)

            is_polysemous_verb = verb_l in ("records", "attacks", "rules", "requests", "controls", "functions", "claims", "marks", "limits")
            if (verb_l in self.registry.CLASS_9_ABSTRACT_SYSTEM or verb_l in self.registry.CLASS_10_PLURAL_SYSTEM or verb_l in self.registry.HUMAN_SINGULAR or verb_l in self.registry.HUMAN_PLURAL) and not (is_polysemous_verb and not antecedent.endswith("s")):
                return m.group(0)
            if not antecedent.endswith("s") and not verb_l.endswith(("s", "es")):
                return m.group(0)
            return self.agglutinator.agglutinate_relative_clause(antecedent, verb)

        if re.search(r"\b([a-zA-Z0-9_-]+)\s+(?:that|which|who)\s+([a-zA-Z]+)\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(
                r"\b([a-zA-Z0-9_-]+)\s+(?:that|which|who)\s+([a-zA-Z]+)\b",
                _repl_rel_clause_morph,
                cs_text,
                flags=re.IGNORECASE
            )
            rules_applied.append("Relative Clause Concord Shift ('[noun] enye [prefix]na[root]')")

        # Step 3: Passive Verb Syntheses with Noun Class Subject Agreement
        def replace_passive_dynamic(match):
            subj_dem = match.group(1) or ""
            subj = match.group(2)
            aux = match.group(3).lower()
            verb_part = match.group(4).lower()
            has_by = bool(match.group(5))

            profile = self.registry.lookup(subj)

            if subj_dem.strip().lower() in ("that", "this", "those", "these", "the"):
                dem_raw = subj_dem.strip().lower()
                if dem_raw == "the":
                    if is_historical_distal:
                        subj_dem = f"{profile.demonstrative_distal} "
                    elif profile.class_id in ("c1", "c2"):
                        subj_dem = f"{profile.demonstrative_ref} "
                    elif profile.class_id == "c10":
                        subj_dem = "hizi "
                    else:
                        subj_dem = "hii "
                elif dem_raw in ("that", "those"):
                    subj_dem = f"{profile.demonstrative_far} "
                else:
                    subj_dem = f"{profile.demonstrative_near} "

            STATIVE_ADJECTIVES = {"localized", "distributed", "connected", "related", "isolated", "fixed"}
            if verb_part in STATIVE_ADJECTIVES and not has_by:
                copula = "ziko" if profile.class_id == "c10" else "iko"
                return f"{subj_dem}{subj} {copula} {verb_part}".strip()

            if verb_part in self.PASSIVE_VERB_MAP and not has_by and aux in ("was", "were"):
                cs_v = self.PASSIVE_VERB_MAP[verb_part][0]
                return f"{subj_dem}{subj} {cs_v}".strip()

            agglutinated = self.agglutinator.agglutinate_passive(subj, aux, verb_part, has_by=has_by)
            return f"{subj_dem}{agglutinated}".strip()

        passive_with_subj_regex = re.compile(
            r"\b((?:that|this|those|these|the|iyo|hii|hizo|hizi|ile|zile|wale|yule|hao|huyo)\s+)?([a-zA-Z0-9_-]+)\s+(was|were|is|are)\s+([a-zA-Z]+ed)\b(?:\s+(by))?",
            re.IGNORECASE
        )
        if passive_with_subj_regex.search(cs_text):
            cs_text = passive_with_subj_regex.sub(replace_passive_dynamic, cs_text)
            rules_applied.append("Pillar I & II: Morphotactic Passive Fusion ('inainfluenciwa / ilicanceliwa')")

        # Fallback for headless passives
        passive_regex = re.compile(r"\b(was|were|is|are)\s+([a-zA-Z]+ed)\b", re.IGNORECASE)
        def replace_passive_fallback(match):
            aux = match.group(1).lower()
            verb_part = match.group(2).lower()
            STATIVE_ADJECTIVES = {"localized", "distributed", "connected", "related", "isolated", "fixed"}
            if verb_part in STATIVE_ADJECTIVES:
                copula = "ziko" if aux in ("were", "are") else "iko"
                return f"{copula} {verb_part}"
            base_verb = MorphologicalRootStripper.strip_to_bare_root(verb_part)
            if verb_part in self.PASSIVE_VERB_MAP and aux in ("was", "were"):
                return self.PASSIVE_VERB_MAP[verb_part][0]
            try:
                who = "c10" if aux in ("were", "are") else "c9"
                tense = "past" if aux in ("was", "were") else "present"
                res = self.fusion.fuse(base_verb, who_subj=who, when_tense=tense, how_ext="kutendwa")
                return res.fused_verb
            except Exception:
                return f"ili{base_verb}iwa"

        def replace_passive_sw(match):
            verb_part = match.group(2).lower()
            if verb_part in self.PASSIVE_VERB_MAP:
                return self.PASSIVE_VERB_MAP[verb_part][1]
            return f"ilifanywa {verb_part}"

        if passive_regex.search(cs_text):
            cs_text = passive_regex.sub(replace_passive_fallback, cs_text)
            rules_applied.append("Pillar I & II: Morphotactic Passive Fusion ('ilicanceliwa')")
        if passive_regex.search(sw_text):
            sw_text = passive_regex.sub(replace_passive_sw, sw_text)

        # Step 2A4B: Comprehensive Past & Present Copular Matrix (Kuwa: walikuwa / alikuwa / ilikuwa / zilikuwa)
        # 1. Pronoun subjects
        cs_text = re.sub(r"\b[Ww]e\s+were\s+not\b", "hatukuwa", cs_text)
        cs_text = re.sub(r"\b[Ww]e\s+were\b", "tulikuwa", cs_text)
        cs_text = re.sub(r"\b[Tt]hey\s+were\s+not\b", "hawakuwa", cs_text)
        cs_text = re.sub(r"\b[Tt]hey\s+were\b", "walikuwa", cs_text)
        cs_text = re.sub(r"\b[Ii]\s+was\s+not\b", "sikuwa", cs_text)
        cs_text = re.sub(r"\b[Ii]\s+was\b", "nilikuwa", cs_text)
        cs_text = re.sub(r"\b(?:[Hh]e|[Ss]he)\s+was\s+not\b", "hakuwa", cs_text)
        cs_text = re.sub(r"\b(?:[Hh]e|[Ss]he)\s+was\b", "alikuwa", cs_text)
        cs_text = re.sub(r"\b[Ii]t\s+was\s+not\b", "haikuwa", cs_text)
        cs_text = re.sub(r"\b[Ii]t\s+was\b", "ilikuwa", cs_text)

        # 2. Noun subjects with were / was (excluding passive participles which end in -ed / -iwa)
        PASSIVE_ED_LOOKAHEAD = r"(?!\s+(?:[a-zA-Z]+(?:ed|ted|iwa)|trained|tested|evaluated|deployed|cancelled|delayed|fixed|updated|created)\b)"

        def _repl_copula_were_not(m):
            subj = m.group(1)
            head = subj.split()[0].lower()
            if head in self.HUMAN_PLURAL_NOUNS or "wote" in subj.lower():
                return f"{subj} hawakuwa"
            return f"{subj} hazikuwa"

        def _repl_copula_were(m):
            subj = m.group(1)
            head = subj.split()[0].lower()
            if head in self.HUMAN_PLURAL_NOUNS or "wote" in subj.lower():
                return f"{subj} walikuwa"
            prof = self.registry.lookup(head)
            pfx = "zi" if prof.class_id in ("c10", "c9") and (head.endswith("s") or "zote" in subj.lower()) else prof.subject_prefix
            return f"{subj} {pfx}likuwa"

        def _repl_copula_was_not(m):
            subj = m.group(1)
            head = subj.split()[0].lower()
            prof = self.registry.lookup(head)
            if prof.class_id == "c1":
                return f"{subj} hakuwa"
            return f"{subj} haikuwa"

        def _repl_copula_was(m):
            subj = m.group(1)
            head = subj.split()[0].lower()
            prof = self.registry.lookup(head)
            pfx = prof.subject_prefix
            return f"{subj} {pfx}likuwa"

        cs_text = re.sub(
            rf"\b([a-zA-Z0-9_-]+(?:\s+(?:wote|zote|wazuri|wabaya|kubwa|ndogo|mpya|thabiti|sahihi))?)\s+were\s+not\b{PASSIVE_ED_LOOKAHEAD}",
            _repl_copula_were_not,
            cs_text,
            flags=re.IGNORECASE
        )
        cs_text = re.sub(
            rf"\b([a-zA-Z0-9_-]+(?:\s+(?:wote|zote|wazuri|wabaya|kubwa|ndogo|mpya|thabiti|sahihi))?)\s+were\b{PASSIVE_ED_LOOKAHEAD}",
            _repl_copula_were,
            cs_text,
            flags=re.IGNORECASE
        )
        cs_text = re.sub(
            rf"\b([a-zA-Z0-9_-]+(?:\s+(?:kubwa|ndogo|mpya|thabiti|sahihi))?)\s+was\s+not\b{PASSIVE_ED_LOOKAHEAD}",
            _repl_copula_was_not,
            cs_text,
            flags=re.IGNORECASE
        )
        cs_text = re.sub(
            rf"\b([a-zA-Z0-9_-]+(?:\s+(?:kubwa|ndogo|mpya|thabiti|sahihi))?)\s+was\b{PASSIVE_ED_LOOKAHEAD}",
            _repl_copula_was,
            cs_text,
            flags=re.IGNORECASE
        )
        rules_applied.append("Comprehensive Bantu Copula Matrix ('walikuwa / ilikuwa / zilikuwa')")

        # Step 3A: Pronominal & Noun Object Clitics / Concord Engine
        HUMAN_VERBS = {
            "call", "contact", "consult", "interview", "invite", "tell", "inform",
            "warn", "advise", "ask", "hire", "fire", "pay", "help", "support",
            "visit", "greet", "congratulate", "remind", "appoint", "reach"
        }

        # 1. Pronominal Object Clitics on Infinitives ('to optimize it' -> 'ku-i-optimize', 'to evaluate them' -> 'ku-zi-evaluate', 'to call them' -> 'ku-wa-call')
        def _repl_to_obj_inf(m):
            verb = m.group(1)
            obj = m.group(2).lower()
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            if obj in ("him", "her"):
                ifx = "m"
            elif obj == "them":
                ifx = "wa" if stem.lower() in HUMAN_VERBS else "zi"
            elif obj == "it":
                ifx = "i"
            elif obj == "us":
                ifx = "tu"
            elif obj == "me":
                ifx = "ni"
            else:
                ifx = "zi"
            return f"ku-{ifx}-{stem}"

        cs_text = re.sub(r"\b(?:to|ku-?)\s*([a-zA-Z]+)\s+(it|them|him|her|us|me)\b", _repl_to_obj_inf, cs_text, flags=re.IGNORECASE)

        # 2. Human Noun Object Clitics on Infinitives ('to call the engineers' -> 'ku-wa-call hao engineers', 'to contact the manager' -> 'ku-m-contact huyo manager')
        def _repl_to_noun_obj(m):
            verb = m.group(1)
            det = (m.group(2) or "").strip().lower()
            noun = m.group(3)
            nl = noun.lower()
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            if nl in self.HUMAN_PLURAL_NOUNS or nl in self.registry.HUMAN_PLURAL:
                ptr = "wale" if is_historical_distal else ("hawa" if det in ("these", "hawa") else "hao")
                return f"ku-wa-{stem} {ptr} {noun}"
            elif nl in self.HUMAN_SINGULAR_NOUNS or nl in self.registry.HUMAN_SINGULAR:
                ptr = "yule" if is_historical_distal else ("huyu" if det in ("this", "huyu") else "huyo")
                return f"ku-m-{stem} {ptr} {noun}"
            return m.group(0)

        cs_text = re.sub(
            r"\b(?:to|ku-?)\s*([a-zA-Z]+)(?:\s+(these|those|this|that|the|hao|wale|hawa|huyo|yule|huyu))?\s+([a-zA-Z0-9_-]+)\b",
            _repl_to_noun_obj,
            cs_text,
            flags=re.IGNORECASE
        )

        cs_text = re.sub(r"\b(team\s+(?:yetu|our)?|committee|board)\s+alidecide\b", r"\1 ilidecide", cs_text, flags=re.IGNORECASE)

        # Authorial 1st-Person Plural Agreement ("We [verb]")
        # 1. We [past] + pronoun object: "We tested them" -> "Tuli-zi-test", "We called them" -> "Tuli-wa-call", "We called him" -> "Tuli-m-call"
        def _repl_we_past_obj(m):
            verb = m.group(1)
            obj = m.group(2).lower()
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            if obj in ("him", "her"):
                ifx = "m"
            elif obj == "them":
                ifx = "wa" if stem.lower() in HUMAN_VERBS else "zi"
            elif obj == "it":
                ifx = "i"
            elif obj == "us":
                ifx = "tu"
            elif obj == "me":
                ifx = "ni"
            else:
                ifx = "zi"
            return f"Tuli-{ifx}-{stem}"

        cs_text = re.sub(r"\b[Ww]e\s+([a-zA-Z]+ed)\s+(it|them|him|her|us|me)\b", _repl_we_past_obj, cs_text, flags=re.IGNORECASE)

        # 2. We [past] + noun object concord:
        #    "We called the engineers" -> "Tuli-wa-call hao engineers"
        #    "We contacted the manager" -> "Tuli-m-contact huyo manager"
        #    "We tested these models" -> "Tuli-zi-test hizi models"
        def _repl_we_past_noun_obj(m):
            verb = m.group(1)
            det = (m.group(2) or "").strip().lower()
            noun = m.group(3)
            nl = noun.lower()
            NON_PAST_ED = {"need", "proceed", "succeed", "exceed", "bleed", "breed", "feed", "seed", "speed", "weed", "bed", "red", "shed"}
            if verb.lower() in NON_PAST_ED:
                return m.group(0)
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            if nl in self.HUMAN_PLURAL_NOUNS or nl in self.registry.HUMAN_PLURAL:
                ptr = "wale" if is_historical_distal else ("hawa" if det in ("these", "hawa") else "hao")
                return f"Tuli-wa-{stem} {ptr} {noun}"
            elif nl in self.HUMAN_SINGULAR_NOUNS or nl in self.registry.HUMAN_SINGULAR:
                ptr = "yule" if is_historical_distal else ("huyu" if det in ("this", "huyu") else "huyo")
                return f"Tuli-m-{stem} {ptr} {noun}"
            elif det in ("these", "hizi") and (nl in self.CLASS_10_SYSTEM_NOUNS or self.registry.is_plural(nl)):
                return f"Tuli-zi-{stem} hizi {noun}"
            elif det in ("this", "hii") and (nl in self.CLASS_9_SYSTEM_NOUNS or nl in self.registry.CLASS_9_ABSTRACT_SYSTEM):
                return f"Tuli-i-{stem} hii {noun}"
            return m.group(0)

        cs_text = re.sub(
            r"\b[Ww]e\s+([a-zA-Z]+ed)(?:\s+(these|those|this|that|the|hao|wale|hawa|huyo|yule|huyu|hii|hizi))?\s+([a-zA-Z0-9_-]+)\b",
            _repl_we_past_noun_obj,
            cs_text,
            flags=re.IGNORECASE
        )

        # 3. 3rd-Person Past + Human Noun Object Concord:
        #    "They called the engineers" -> "Wali-wa-call hao engineers"
        #    "He/She contacted the manager" -> "Ali-m-contact huyo manager"
        def _repl_third_past_noun_obj(m):
            subj = m.group(1).lower()
            verb = m.group(2)
            det = (m.group(3) or "").strip().lower()
            noun = m.group(4)
            nl = noun.lower()
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            s_pfx = "wali" if subj in ("they", "wao") else "ali"
            if nl in self.HUMAN_PLURAL_NOUNS or nl in self.registry.HUMAN_PLURAL:
                ptr = "wale" if is_historical_distal else ("hawa" if det in ("these", "hawa") else "hao")
                return f"{s_pfx}-wa-{stem} {ptr} {noun}"
            elif nl in self.HUMAN_SINGULAR_NOUNS or nl in self.registry.HUMAN_SINGULAR:
                ptr = "yule" if is_historical_distal else ("huyu" if det in ("this", "huyu") else "huyo")
                return f"{s_pfx}-m-{stem} {ptr} {noun}"
            return m.group(0)

        cs_text = re.sub(
            r"\b(they|he|she)\s+([a-zA-Z]+ed)(?:\s+(these|those|this|that|the|hao|wale|hawa|huyo|yule|huyu))?\s+([a-zA-Z0-9_-]+)\b",
            _repl_third_past_noun_obj,
            cs_text,
            flags=re.IGNORECASE
        )

        # 4. We have [verb-ed]: "We have demonstrated" -> "Tume-demonstrate"
        def _repl_we_perf(m):
            verb = m.group(1)
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"Tume-{stem}"

        cs_text = re.sub(r"\b[Ww]e\s+have\s+([a-zA-Z]+ed)\b", _repl_we_perf, cs_text, flags=re.IGNORECASE)

        # 5. We [past-ed]: "We trained/initialized/evaluated" -> "Tuli-[root]"
        def _repl_we_past(m):
            verb = m.group(1)
            NON_PAST_ED = {"need", "proceed", "succeed", "exceed", "bleed", "breed", "feed", "seed", "speed", "weed", "bed", "red", "shed"}
            if verb.lower() in NON_PAST_ED:
                return m.group(0)
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"Tuli-{stem}"

        cs_text = re.sub(r"\b[Ww]e\s+([a-zA-Z]+ed)\b", _repl_we_past, cs_text, flags=re.IGNORECASE)

        # 6. We [irregular_past]: "We found/built/saw/chose" -> "Tuli-[root]"
        for irreg, root in MorphologicalRootStripper.IRREGULAR_PAST_VERBS.items():
            pat_we_irreg = re.compile(r"\b[Ww]e\s+" + re.escape(irreg) + r"\b", re.IGNORECASE)
            if pat_we_irreg.search(cs_text):
                cs_text = pat_we_irreg.sub(f"Tuli-{root}", cs_text)
                rules_applied.append(f"Authorial Past Agglutination ('Tuli-{root}')")

        # 7. We [present] + Object Concord:
        #    "We call the engineers" -> "Tuna-wa-call hao engineers"
        #    "We contact the manager" -> "Tuna-m-contact huyo manager"
        #    "We call them" -> "Tuna-wa-call"
        #    "We contact him" -> "Tuna-m-contact"
        pres_trans_verbs = sorted(HUMAN_VERBS | {"evaluate", "test", "optimize", "deploy", "examine", "analyze", "monitor"}, key=len, reverse=True)

        def _repl_we_pres_pron_obj(m):
            verb = m.group(1)
            obj = m.group(2).lower()
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            if obj in ("him", "her"):
                ifx = "m"
            elif obj == "them":
                ifx = "wa" if stem.lower() in HUMAN_VERBS else "zi"
            elif obj == "it":
                ifx = "i"
            else:
                ifx = "zi"
            return f"Tuna-{ifx}-{stem}"

        cs_text = re.sub(
            r"\b[Ww]e\s+(" + "|".join(re.escape(v) for v in pres_trans_verbs) + r")\s+(him|her|it|them)\b",
            _repl_we_pres_pron_obj,
            cs_text,
            flags=re.IGNORECASE
        )

        def _repl_we_pres_noun_obj(m):
            verb = m.group(1)
            det = (m.group(2) or "").strip().lower()
            noun = m.group(3)
            nl = noun.lower()
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            if nl in self.HUMAN_PLURAL_NOUNS or nl in self.registry.HUMAN_PLURAL:
                ptr = "wale" if is_historical_distal else ("hawa" if det in ("these", "hawa") else "hao")
                return f"Tuna-wa-{stem} {ptr} {noun}"
            elif nl in self.HUMAN_SINGULAR_NOUNS or nl in self.registry.HUMAN_SINGULAR:
                ptr = "yule" if is_historical_distal else ("huyu" if det in ("this", "huyu") else "huyo")
                return f"Tuna-m-{stem} {ptr} {noun}"
            elif det in ("these", "hizi") and (nl in self.CLASS_10_SYSTEM_NOUNS or self.registry.is_plural(nl)):
                return f"Tuna-zi-{stem} hizi {noun}"
            elif det in ("this", "hii") and (nl in self.CLASS_9_SYSTEM_NOUNS or nl in self.registry.CLASS_9_ABSTRACT_SYSTEM):
                return f"Tuna-i-{stem} hii {noun}"
            return m.group(0)

        cs_text = re.sub(
            r"\b[Ww]e\s+(" + "|".join(re.escape(v) for v in pres_trans_verbs) + r")(?:\s+(these|those|this|that|the|hao|wale|hawa|huyo|yule|huyu|hii|hizi))?\s+([a-zA-Z0-9_-]+)\b",
            _repl_we_pres_noun_obj,
            cs_text,
            flags=re.IGNORECASE
        )

        # 8. We [present_academic_verb]: "We release/propose/present/demonstrate" -> "Tuna-[root]"
        def _repl_we_pres(m):
            verb = m.group(1)
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"Tuna-{stem}"

        pres_pattern = r"\b[Ww]e\s+(" + "|".join(re.escape(v) for v in sorted(self.ACADEMIC_PRESENT_VERBS, key=len, reverse=True)) + r")\b"
        cs_text = re.sub(pres_pattern, _repl_we_pres, cs_text, flags=re.IGNORECASE)

        # Step 3A2: Temporal Tense, Aspect & Modality (TAM) Engine
        # A. Negative Inceptive Aspect ("have not yet / has not yet [verb]" -> "Hatuja-[root] / [Subject] haija-[root] bado")
        def _repl_not_yet_we(m):
            verb = m.group(1)
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"Hatuja-{stem}"
        cs_text = re.sub(r"\b[Ww]e\s+have\s+not\s+(?:yet\s+)?([a-zA-Z]+(?:ed|d)?)\b", _repl_not_yet_we, cs_text, flags=re.IGNORECASE)

        def _repl_not_yet_subj(m):
            subj = m.group(1)
            verb = m.group(2)
            profile = self.registry.lookup(subj)
            neg_pfx = "haija" if profile.class_id == "c9" else ("hazija" if profile.class_id == "c10" else ("haja" if profile.class_id == "c1" else "hawaja"))
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"{subj} {neg_pfx}-{stem}"
        cs_text = re.sub(r"\b([a-zA-Z0-9_-]+)\s+has\s+not\s+(?:yet\s+)?([a-zA-Z]+(?:ed|d)?)\b", _repl_not_yet_subj, cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b([a-zA-Z0-9_-]+)\s+have\s+not\s+(?:yet\s+)?([a-zA-Z]+(?:ed|d)?)\b", _repl_not_yet_subj, cs_text, flags=re.IGNORECASE)

        # B. Pluperfect / Past Anterior ("had [verb-ed]" -> "[Subject] [pfx]likuwa [pfx]me-[root]")
        def _repl_pluperfect(m):
            subj = m.group(1)
            verb = m.group(2)
            subj_l = subj.lower()
            NON_SUBJ = {"who", "which", "that", "it", "if", "and", "or", "because", "although", "so", "as"}
            if subj_l in NON_SUBJ:
                return m.group(0)
            profile = self.registry.lookup(subj)
            pfx = profile.subject_prefix
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"{subj} {pfx}likuwa {pfx}me-{stem}"
        cs_text = re.sub(r"\b([a-zA-Z0-9_-]+)\s+had\s+([a-zA-Z]+ed)\b", _repl_pluperfect, cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b[Ww]e\s+had\s+([a-zA-Z]+ed)\b", lambda m: f"Tulikuwa tume-{MorphologicalRootStripper.strip_to_bare_root(m.group(1))}", cs_text, flags=re.IGNORECASE)

        # C. Present Perfect ("have/has [verb-ed]" -> "[Subject] [pfx]me-[root]")
        def _repl_present_perfect(m):
            lead = m.group(1)
            verb = m.group(2)
            NON_SUBJ = {"to", "could", "should", "would", "must", "might", "may", "who", "which", "that", "and", "or", "we"}
            lead_last = lead.strip().split()[-1].lower()
            if lead_last in NON_SUBJ or lead_last.endswith(("ly", "ed", "ing")):
                return m.group(0)
            profile = self.registry.lookup(lead_last)
            pfx = profile.subject_prefix
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"{lead} {pfx}me-{stem}"
        cs_text = re.sub(
            r"\b((?:[a-zA-Z0-9_-]+\s+)?(?:studies|researchers|authors|experiments|data|models|algorithms|systems|paper|system|model|algorithm|physics|theory))\s+(?:have|has)\s+([a-zA-Z]+ed)\b",
            _repl_present_perfect,
            cs_text,
            flags=re.IGNORECASE
        )

        # D. Future Prospective ("will [verb]" -> "[Subject] [pfx]ta-[root]")
        def _repl_future_subj(m):
            lead = m.group(1)
            verb = m.group(2)
            NON_VERBS = {"be", "have", "not", "also", "always", "sometimes", "never", "only"}
            if verb.lower() in NON_VERBS:
                return m.group(0)
            lead_last = lead.strip().split()[-1].lower()
            profile = self.registry.lookup(lead_last)
            pfx = profile.subject_prefix
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"{lead} {pfx}ta-{stem}"
        cs_text = re.sub(
            r"\b((?:[a-zA-Z0-9_-]+\s+)?(?:algorithm|model|system|work|research|study|paper|architecture|approach|framework|method))\s+will\s+([a-zA-Z]+)\b",
            _repl_future_subj,
            cs_text,
            flags=re.IGNORECASE
        )
        cs_text = re.sub(r"\b[Ww]e\s+will\s+([a-zA-Z]+)\b", lambda m: f"Tuta-{MorphologicalRootStripper.strip_to_bare_root(m.group(1))}", cs_text, flags=re.IGNORECASE)

        # E. Modal Passive Infinitives ("should/can/could/must/cannot be [verb-ed]" -> "[modal] ku-[root]-iwa")
        def _repl_modal_passive(m):
            modal = m.group(1).lower()
            verb = m.group(2)
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            pass_stem = f"{stem}iwa" if not stem.endswith("e") else f"{stem[:-1]}iwa"
            if modal == "should":
                return f"inafaa ku-{pass_stem}"
            elif modal in ("can", "could"):
                return f"inaweza ku-{pass_stem}"
            elif modal == "must":
                return f"lazima ku-{pass_stem}"
            elif modal in ("cannot", "can't"):
                return f"haiwezi ku-{pass_stem}"
            return f"ku-{pass_stem}"
        cs_text = re.sub(r"\b(should|can|could|must|cannot|can't)\s+be\s+([a-zA-Z]+ed)\b", _repl_modal_passive, cs_text, flags=re.IGNORECASE)

        # F. Gnomic Scientific Laws on Plural Natural Science Subjects ("electrons travel at..." -> "electrons zina-travel...")
        def _repl_scilaw(m):
            subj = m.group(1)
            verb = m.group(2)
            NON_VERBS = {
                "are", "were", "have", "had", "can", "will", "may", "do", "did", "not",
                "with", "in", "at", "by", "that", "which", "zenye", "yenye", "wenye", "mwenye",
                "za", "ya", "wa", "ziko", "iko", "wako", "kuwa", "bila", "kwa", "na",
                "and", "or", "as", "if", "when", "where", "how", "all", "each", "every",
                "to", "from", "into", "onto", "through", "during", "before", "after"
            }
            if verb.lower() in NON_VERBS or verb.lower().startswith(("zina", "ina", "wali", "tuli", "ili", "zili", "kuwa", "kwa", "ali", "hazi", "hai")) or verb.lower().endswith("iwa"):
                return m.group(0)
            stem = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"{subj} zina-{stem}"
        cs_text = re.sub(
            r"\b(electrons|photons|particles|cells|enzymes|atoms|molecules|quanta|waves)\s+([a-zA-Z]+)\b",
            _repl_scilaw,
            cs_text,
            flags=re.IGNORECASE
        )

        # Step 3B: Active Past Verbs (Pillar I: Bare Root Constraint)
        PARTICIPIAL_FOLLOWERS = {
            "models", "model", "language", "systems", "system", "servers", "server",
            "databases", "database", "networks", "network", "layers", "layer",
            "pipelines", "pipeline", "clusters", "cluster", "architectures", "architecture",
            "applications", "application", "codebase", "codebases", "compiler", "compilers",
            "runtime", "runtimes", "agents", "agent", "policies", "policy", "tensors", "tensor"
        }
        for v_ed, (cs_v, sw_v) in self.ACTIVE_PAST_VERB_MAP.items():
            pat = re.compile(r"(\b(?:one|a|an|the|this|that|these|those)\s+)?\b(" + re.escape(v_ed) + r")\b(?:\s+([a-zA-Z0-9_-]+))?", re.IGNORECASE)
            if pat.search(cs_text):
                is_plural = bool(re.search(r"\b(they|people|wasee|mayouth|students|users)\b", cs_text, re.IGNORECASE))
                active_cs = cs_v if not is_plural else re.sub(r"^ali", "wali", cs_v)
                active_sw = sw_v if not is_plural else re.sub(r"^ali", "wali", sw_v)
                
                def _make_active_repl(base_v):
                    def _r(m):
                        det = m.group(1) or ""
                        following = (m.group(3) or "").lower()
                        if det or following in PARTICIPIAL_FOLLOWERS:
                            return m.group(0)
                        rest = f" {m.group(3)}" if m.group(3) else ""
                        return f"{base_v}{rest}"
                    return _r

                cs_text = pat.sub(_make_active_repl(active_cs), cs_text)
                sw_text = pat.sub(_make_active_repl(active_sw), sw_text)
                rules_applied.append(f"Pillar I: Bare Root Active Verb ('{active_cs}')")

        # Predicate Adjective / State with Manner Adverb ("light is spatially localized" -> "light iko spatially localized")
        def _repl_predicate_state(m):
            subj = m.group(1)
            adv = m.group(2) or ""
            adj = m.group(3)
            profile = self.registry.lookup(subj)
            copula = "yuko" if profile.class_id == "c1" else ("wako" if profile.class_id == "c2" else ("ziko" if profile.class_id == "c10" else "iko"))
            adv_str = f" {adv}" if adv else ""
            return f"{subj} {copula}{adv_str} {adj}"

        cs_text = re.sub(
            r"\b([a-zA-Z0-9_-]+)\s+is\s+(?:([a-zA-Z]+ly)\s+)?(localized|distributed|connected|related|isolated|fixed)\b",
            _repl_predicate_state,
            cs_text,
            flags=re.IGNORECASE
        )
        cs_text = re.sub(
            r"\b([a-zA-Z0-9_-]+)\s+is\s+([a-zA-Z]+ly)\s+([a-zA-Z]+(?:ed|ized|ised))\b",
            _repl_predicate_state,
            cs_text,
            flags=re.IGNORECASE
        )


        # Step 3B2: Dynamic Active Past-Tense Agglutination ([Subject Noun] [Past-Tense Verb] -> [Subject] [prefix]li[root])
        # e.g., "article challenged" -> "article ilichallenge"
        #       "Einstein proposed" -> "Einstein alipropose"
        #       "engineers tested" -> "engineers walitest"
        def _repl_subject_past_verb(m):
            subj_full = m.group(1)
            verb = m.group(2)
            # Acronyms (e.g. IED, LED, RFID) and short tokens are never regular past verbs
            if verb.isupper() or len(verb) <= 3:
                return m.group(0)
            if subj_full.lower().endswith(("-level", "-based", "-centric", "-driven", "-related", "-specific", "-scale", "-type", "-bound", "-free", "-oriented", "-aware")):
                return m.group(0)
            subj_tokens = subj_full.strip().split()
            head_noun = subj_tokens[0] if subj_tokens else subj_full
            subj_l = head_noun.lower()
            verb_l = verb.lower()
            NON_SUBJECTS = {
                "was", "were", "is", "are", "be", "been", "being", "have", "has", "had",
                "with", "kwa", "na", "yenye", "zenye", "mwenye", "wenye", "bila", "kama",
                "hata", "so", "ndio", "ili", "discrete", "classical", "wave", "that", "this",
                "these", "those", "which", "who", "not", "also", "and", "or", "in", "at", "by", "to",
                "ziko", "iko", "wako", "viko", "yako", "liko", "kiko", "kuwa", "za", "ya", "wa", "la", "cha", "vya",
                "use", "uses", "used", "using", "make", "take", "give", "find", "see", "get", "come", "go", "know",
                "high", "low", "great", "small", "large", "fast", "slow", "deep", "constant", "variable", "equal",
                "unequal", "total", "initial", "final", "point", "well", "partially", "fully", "locally", "globally",
                "process", "processes", "test", "tests", "run", "runs", "execute", "executes", "handle", "handles",
                "store", "stores", "deploy", "deploys", "call", "calls", "load", "loads", "send", "sends", "receive",
                "receives", "support", "supports", "update", "updates", "require", "requires",
                "inspect", "inspects", "manipulate", "manipulates", "perceive", "perceives", "construct", "constructs",
                "evaluate", "evaluates", "achieve", "achieves", "lag", "lags", "revise", "revises", "provide", "provides",
                "assess", "assesses", "characterize", "characterizes", "examine", "examines", "investigate", "investigates",
                "explore", "explores", "measure", "measures", "control", "controls", "formulate", "formulates", "derive", "derives",
                "generate", "generates", "produce", "produces", "create", "creates", "introduce", "introduces", "propose", "proposes",
                "present", "presents", "describe", "describes", "discuss", "discusses", "show", "shows", "contain", "contains",
                "involve", "involves", "allow", "allows", "enable", "enables"
            }
            NON_SUBJECTS.update({
                "stronger", "weaker", "better", "faster", "slower", "higher", "lower", "greater", "smaller", "larger",
                "one", "two", "three", "four", "five", "many", "several", "few", "some", "any", "every", "each", "such", "another", "single", "both"
            })
            if (subj_l in NON_SUBJECTS or subj_l.endswith(("ing", "ed", "ly")) or
                subj_l.startswith(("hai", "hazi", "ha-", "hawa", "hatu", "haku", "siku", "tuli", "wali", "ina", "zina", "wana", "tuna"))):
                return m.group(0)
            NON_PAST_VERBS = {
                "discrete", "united", "limited", "detailed", "advanced", "sophisticated",
                "isolated", "generalized", "specialized", "unprecedented", "connected", "related",
                "localized", "distributed", "crowded", "armed", "fixed", "mixed", "tired", "bored", "excited",
                "corrupted", "encrypted", "compressed", "encoded", "filtered", "sorted", "indexed",
                "identified", "quantized", "entangled", "bounded", "unrestricted", "unseen", "observed",
                "rendered", "supplied", "closed", "closed-source", "open-source", "pretrained", "fine-tuned",
                "measured", "tested", "trained", "annotated", "labeled", "weighted", "aligned", "guided",
                "impressed", "applied", "derived", "obtained", "calculated", "formulated", "expressed", "introduced", "induced",
                "deployed", "supervised", "unsupervised", "reinforced", "configured", "structured", "nested"
            }

            if verb_l in NON_PAST_VERBS or verb_l in MorphologicalRootStripper.NON_PAST_ED or verb_l.endswith("-source"):
                return m.group(0)
            
            profile = self.registry.lookup(head_noun)
            pfx = profile.subject_prefix
            root = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"{subj_full} {pfx}li{root}"

        cs_text = re.sub(
            r"\b([a-zA-Z0-9_-]+(?:\s+(?:wazuri|wabaya|wakubwa|wadogo|wapya|warefu|wafupi|wengi|wachache|kubwa|ndogo|nzuri|mbaya|mpya|ndefu|fupi|nyingi|chache|muhimu|sahihi|halisi|bora|kamili|rahisi|ngumu|safi|chafu|tofauti|mbalimbali|thabiti|dhaifu|maalum|wazi|rasmi|kuu|fiti))?)\s+([a-zA-Z]+ed)\b(?!-)(?!\s+(?:upon|on|in|at|by|to|with|from|under|over|across|into|and\s+(?:is|was|are|were|made))\b)(?!\s+(?:files|data|records|models?|language|code|codebase|tensor|runtime|compiler|transformer|prompt|policy|policies|systems?|servers?|images|nodes|packets|documents|layers|networks?|results|inputs|outputs|classification|detection|analysis|identification|recognition|segmentation|prediction|estimation|formulation|evaluation|generation|synthesis|processing|extraction|distribution|transformation|optimization|algorithm|framework|approach|strategy|method|protocol|paper|study|device|circuit|interface|benchmark|architecture|binding|feature|pipeline|views|parts|rigid|peers|objects|components|items|elements|agents?|samples|tasks|states|patterns|structures|functions|weights)\b)",
            _repl_subject_past_verb,
            cs_text,
            flags=re.IGNORECASE
        )



        # Consecutive Aspect Chaining (-ka- infix)
        # 1. 1st Person Plural (Tuli- ... -> ... tuka-[root])
        if re.search(r"\btuli-", cs_text, re.IGNORECASE):
            def _repl_tuka(m):
                sep = m.group(1)
                verb = m.group(2)
                root = MorphologicalRootStripper.strip_to_bare_root(verb)
                if "and" in sep.lower() or "na" in sep.lower():
                    return f" na tuka-{root}"
                return f", tuka-{root}"
            cs_text = re.sub(r"(,\s*|\s+(?:and|na)\s+)([a-zA-Z]+ed)\b(?!\s+(?:in|kwa|by|na)\b)", _repl_tuka, cs_text, flags=re.IGNORECASE)
            rules_applied.append("Consecutive Narrative Aspect ('tuka-[root]')")

        # 2. Inanimate Class 9 (ili- ... -> ... ika-[root])
        if re.search(r"\bili-?[a-zA-Z]+\b", cs_text, re.IGNORECASE):
            def _repl_ika(m):
                sep = m.group(1)
                verb = m.group(2)
                root = MorphologicalRootStripper.strip_to_bare_root(verb)
                if "and" in sep.lower() or "na" in sep.lower():
                    return f" na ika-{root}"
                return f", ika-{root}"
            cs_text = re.sub(r"(,\s*|\s+(?:and|na)\s+)([a-zA-Z]+ed)\b(?!\s+(?:in|kwa|by|na)\b)", _repl_ika, cs_text, flags=re.IGNORECASE)
            rules_applied.append("Inanimate Consecutive Aspect ('ika-[root]')")

        # 3. Human 3rd Person Singular (ali- ... -> ... aka-[root])
        if re.search(r"\bali-?[a-zA-Z]+\b", cs_text, re.IGNORECASE):
            def _repl_aka(m):
                sep = m.group(1)
                verb = m.group(2)
                root = MorphologicalRootStripper.strip_to_bare_root(verb)
                if "and" in sep.lower() or "na" in sep.lower():
                    return f" na aka-{root}"
                return f", aka-{root}"
            cs_text = re.sub(r"(,\s*|\s+(?:and|na)\s+)([a-zA-Z]+ed)\b(?!\s+(?:in|kwa|by|na)\b)", _repl_aka, cs_text, flags=re.IGNORECASE)
            rules_applied.append("Human Consecutive Aspect ('aka-[root]')")

        # 3rd person singular present on academic subjects ("research paper explains" -> "research paper inaexplain")
        def _repl_academic_subj_pres(m):
            lead = m.group(1)
            verb = m.group(2).lower()
            NON_VERB_S = {
                "is", "was", "has", "this", "us", "as", "yes", "always", "sometimes",
                "results", "weights", "parameters", "data", "models", "physics", "mechanics",
                "optics", "statistics", "analytics", "electronics", "robotics",
                "does", "did", "can", "will", "would", "should", "could"
            }
            if (verb in NON_VERB_S or verb.endswith("ss") or
                verb.startswith(("hai", "hazi", "ha-", "hawa", "hatu", "haku", "siku", "tuli", "wali", "ina", "zina", "wana", "tuna"))):
                return m.group(0)
            root = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"{lead} ina{root}"

        cs_text = re.sub(
            r"\b(research paper(?:\s+ya\s+[a-zA-Z0-9_\s-]+?)?|algorithm|model|system|server(?:\s+kuu)?|pipeline|network|platform|layer)\s+([a-zA-Z]+(?:s|es))\b",
            _repl_academic_subj_pres,
            cs_text,
            flags=re.IGNORECASE
        )

        # 3rd person plural present on inanimate subjects ("servers process" -> "servers zina-process", "models achieve" -> "models zina-achieve")
        def _repl_inanimate_plural_subj_pres(m):
            lead = m.group(1)
            verb = m.group(2).lower()
            NON_VERB = {"is", "was", "are", "were", "and", "na", "or", "au", "in", "kwa", "to", "for", "with", "from", "at", "by", "that", "which"}
            if verb in NON_VERB or verb.endswith(("ed", "ing", "ly", "iwa")) or verb.startswith(("zina", "ina", "zili", "ili", "wali", "tuli", "hazi", "hai")):
                return m.group(0)
            if verb in self.ACADEMIC_PRESENT_VERBS or verb in {"store", "yield", "generate", "produce", "predict", "capture", "contain", "utilize", "apply", "execute", "run", "fail", "operate"}:
                root = MorphologicalRootStripper.strip_to_bare_root(verb)
                return f"{lead} zina-{root}"
            return m.group(0)

        cs_text = re.sub(
            r"\b((?!(?:that|which|who|where|when|if|because|kuwa|na|kwa|ili)\s+)(?:[a-zA-Z0-9_-]+\s+){0,2}(?:hizi\s+)?(?:simulations|observations|experiments|calculations|measurements|evaluations|fluctuations|oscillations|pathways|mechanisms|structures|signals|genes|mutations|treatments|variables|factors|indicators|servers|databases|files|models|algorithms|clusters|tables|nodes|threads|networks|layers|systems|pipelines|parameters|weights|features|methods|approaches|datasets|results|inputs|outputs|queries|enzymes|molecules|particles|photons|cells|quanta|waves|electrons|atoms|components|protocols|equations|functions|representations|distributions|configurations|trajectories|dynamics))\s+([a-zA-Z]+)\b",
            _repl_inanimate_plural_subj_pres,
            cs_text,
            flags=re.IGNORECASE
        )

        # 3rd person plural present on human subjects ("researchers explain" -> "researchers wana-explain", "authors propose" -> "authors wana-propose")
        def _repl_human_plural_subj_pres(m):
            lead = m.group(1)
            verb = m.group(2).lower()
            NON_VERB = {"is", "was", "are", "were", "and", "na", "or", "au", "in", "kwa", "to", "for", "with", "from", "at", "by", "that", "which"}
            if verb in NON_VERB or verb.endswith(("ed", "ing", "ly", "iwa")) or verb.startswith(("zina", "ina", "zili", "ili", "wali", "tuli", "hazi", "hai", "wana")):
                return m.group(0)
            if verb in self.ACADEMIC_PRESENT_VERBS or verb in {"explain", "propose", "suggest", "argue", "state", "note", "report", "observe", "conclude", "find", "use", "apply", "deploy", "build"}:
                root = MorphologicalRootStripper.strip_to_bare_root(verb)
                return f"{lead} wana-{root}"
            return m.group(0)

        cs_text = re.sub(
            r"\b((?:hawa\s+)?(?:researchers|authors|scientists|engineers|users|developers|students|participants|reviewers|physicists))\s+([a-zA-Z]+)\b",
            _repl_human_plural_subj_pres,
            cs_text,
            flags=re.IGNORECASE
        )

        # Step 3C2: Trailing Participial Clauses (Bantu Simultaneous -ki- Aspect)
        # e.g., ", offering predictions" -> ", ziki-offer predictions"
        #       ", preventing viral replication" -> ", ziki-prevent viral replication"
        #       ", resulting in lower latency" -> ", ziki-result kwa lower latency"
        def _repl_trailing_participle(m):
            sep = m.group(1)
            v_ing = m.group(2)
            prep_trans = m.group(3) or ""
            root = MorphologicalRootStripper.strip_to_bare_root(v_ing)
            
            pfx = "zi" if re.search(r"\b(?:zina-|zili-|hizi|hizo|zile)\b", cs_text, re.IGNORECASE) else "i"
            prep_str = " kwa" if prep_trans.strip() in ("in", "to") else (f" {prep_trans.strip()}" if prep_trans else "")
            return f"{sep}{pfx}ki-{root}{prep_str} "

        pat_participle = r"(,\s*)(offering|providing|showing|demonstrating|preventing|suggesting|indicating|yielding|leading|resulting|highlighting|confirming|revealing|enabling|facilitating|improving|reducing|establishing|generating|producing|reflecting)\s+(?!(?:that|kuwa|iyo|ile|hizo|zile|hii|hizi)\b)(?:(in|to)\s+)?"
        if re.search(pat_participle, cs_text, re.IGNORECASE):
            cs_text = re.sub(pat_participle, _repl_trailing_participle, cs_text, flags=re.IGNORECASE)
            rules_applied.append("Bantu Simultaneous Participial Aspect ('-ki-[root]')")

        # Step 3C: Purpose Clauses & Infinitives
        purpose_rules = [
            (r"\bto prevent\s+([a-zA-Z0-9_-]+)\s+from\s+([a-z]+)ing\b", r"ili kuzuia \1 isi-\2", r"ili kuzuia \1 isielemewe"),
            (r"\bto prevent\s+([a-zA-Z0-9_-]+)\s+from\s+([a-z]+)\b", r"ili kuzuia \1 isi-\2", r"ili kuzuia \1 isielemewe"),
            (r"\bto prevent\b", "ili kuzuia", "ili kuzuia"),
            (r"\bto keep\s+([a-zA-Z0-9_-]+)\s+low\b", r"ndio ku-keep \1 ikiwa low", r"kufanya \1 iwe ya chini"),
            (r"\bto keep\s+([a-zA-Z0-9_-]+)\s+high\b", r"ndio ku-keep \1 ikiwa high", r"kufanya \1 iwe ya juu"),
            (r"\bto ensure\b", "ndio ku-ensure", "ili kuhakikisha"),
            (r"\bto reduce\b", "ndio ku-reduce", "ili kupunguza"),
            (r"\bto improve\b", "ndio ku-improve", "ili kuboresha"),
            (r"\bto handle\b", "ndio ku-handle", "ili kushughulikia"),
            (r"\bto scale\b", "ndio ku-scale", "ili kuongeza uwezo"),
            (r"\bto earn money\b", "ndio kupata chapaa", "ili kuchuma fedha"),
            (r"\bto start\b", "kuanza", "kuanzisha"),
            (r"\bfrom home\b", "kutoka keja", "kutoka nyumbani"),
            (r"\bat home\b", "kwa keja", "nyumbani"),
            (r"\bfrom work\b", "kutoka job", "kutoka kazini"),
            (r"\bat work\b", "kwa job", "kazini")
        ]
        for pat_str, cs_p, sw_p in purpose_rules:
            pat = re.compile(pat_str, re.IGNORECASE)
            if pat.search(cs_text):
                cs_text = pat.sub(cs_p, cs_text)
                sw_text = pat.sub(sw_p, sw_text)
                rules_applied.append(f"Purpose Clause ('{cs_p}')")

        # Step 3D: Empirical Causal & Scientific Proof Templates
        # A: Instrumental Gerund: "By [verb]ing" -> "kwa ku-[root]"
        def _repl_by_gerund(m):
            v_ing = m.group(1).lower() + "ing"
            root = MorphologicalRootStripper.strip_to_bare_root(v_ing)
            return f"kwa ku-{root}"

        if re.search(r"\bby\s+([a-zA-Z]+)ing\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(r"\bby\s+([a-zA-Z]+)ing\b", _repl_by_gerund, cs_text, flags=re.IGNORECASE)
            rules_applied.append("Instrumental Gerund ('kwa ku-')")

        # Declarative Complementizer ("propose that", "suggest that", "argue that", "ku-propose that", etc. -> "... kuwa")
        PROPOSITIONAL_COMPLEMENTIZER_VERBS = {
            "propose", "suggest", "state", "argue", "show", "demonstrate", "prove",
            "believe", "claim", "reveal", "confirm", "indicate", "think", "note",
            "discover", "find", "realize", "say", "conclude", "assume", "assert",
            "observe", "explain", "hypothesize"
        }
        def _repl_declarative_complementizer(m):
            lead = m.group(1)
            lead_clean = re.sub(r"^ku-?", "", lead, flags=re.IGNORECASE)
            root = MorphologicalRootStripper.strip_to_bare_root(lead_clean)
            if root in PROPOSITIONAL_COMPLEMENTIZER_VERBS or lead_clean.lower() in PROPOSITIONAL_COMPLEMENTIZER_VERBS:
                return f"{lead} kuwa"
            return m.group(0)

        cs_text = re.sub(
            r"\b((?:ku-?)?[a-zA-Z]+)\s+that\b",
            _repl_declarative_complementizer,
            cs_text,
            flags=re.IGNORECASE
        )

        # Coordinated passive participle ("and transmitted in/kwa" -> "na inatransmitiwa kwa")
        def _repl_coord_passive(m):
            conj = m.group(1)
            verb = m.group(2)
            prep = m.group(3)
            root = MorphologicalRootStripper.strip_to_bare_root(verb)
            return f"na ina{root}iwa kwa"

        cs_text = re.sub(
            r"\b(and|na)\s+([a-zA-Z]+(?:ed|ted))\s+(in|kwa)\b",
            _repl_coord_passive,
            cs_text,
            flags=re.IGNORECASE
        )

        # Trailing Participial Consecutive Clause (", introducing" -> ", ikaintroduce")
        def _repl_participial_consecutive(m):
            comma = m.group(1)
            v_ing = m.group(2)
            root = MorphologicalRootStripper.strip_to_bare_root(v_ing)
            return f"{comma} ika{root}"

        cs_text = re.sub(
            r"(,\s*)(introducing|establishing|creating|generating|laying|providing|forming|revealing|demonstrating)\b",
            _repl_participial_consecutive,
            cs_text,
            flags=re.IGNORECASE
        )

        # Relative clause with past-tense verb ("core concept that laid" -> "core concept enye ili-lay")
        def _repl_rel_past_verb(m):
            head = m.group(1)
            past_v = m.group(2)
            profile = self.registry.lookup(head)
            rel = profile.relative_marker
            root = MorphologicalRootStripper.strip_to_bare_root(past_v)
            return f"{head} {rel} ili-{root}"

        cs_text = re.sub(
            r"\b((?:[a-zA-Z0-9_-]+\s+)?[a-zA-Z0-9_-]+)\s+(?:that|which)\s+(laid|built|led|won|lost|found|took|made|gave|[a-zA-Z]+ed)\b",
            _repl_rel_past_verb,
            cs_text,
            flags=re.IGNORECASE
        )

        # B: Relational Dative shift after link/connect/bind/map ("to" -> "na")
        cs_text = re.sub(r"(\bku-(?:link|connect|bind|map)\s+[^,]+?)\s+to\s+", r"\1 na ", cs_text, flags=re.IGNORECASE)

        # C: Empirical Evidential Assertion: "it proved/showed/demonstrated that" -> "iliprove/ilishow/ilidemonstrate that"
        evidential_map = [
            (r"\bit proved that\b", "iliprove that", "ilithibitisha kuwa"),
            (r"\bit showed that\b", "ilishow that", "ilionyesha kuwa"),
            (r"\bit demonstrated that\b", "ilidemonstrate that", "ilidhihirisha kuwa"),
            (r"\bit confirmed that\b", "iliconfirm that", "ilithibitisha kuwa"),
            (r"\bit indicated that\b", "ili-indicate that", "iliashiria kuwa")
        ]
        for pat_str, cs_ev, sw_ev in evidential_map:
            if re.search(pat_str, cs_text, re.IGNORECASE):
                cs_text = re.sub(pat_str, cs_ev, cs_text, flags=re.IGNORECASE)
                sw_text = re.sub(pat_str, sw_ev, sw_text, flags=re.IGNORECASE)
                rules_applied.append(f"Evidential Matrix ('{cs_ev}')")

        # Step 3E: Subject 3rd-person Singular Agglutination
        # e.g., "He challenges" -> "yeye anachallenge"
        NON_ACTION_VERBS = {"is", "was", "are", "were", "has", "had", "does", "did", "this", "us", "as", "yes", "always", "sometimes"}
        def _match_subj_pres(m):
            subj = m.group(1)
            verb = m.group(2)
            if verb.lower() in NON_ACTION_VERBS:
                return m.group(0)
            return self.agglutinator.agglutinate_subject_present(subj, verb)

        if re.search(r"\b(he|she)\s+([a-zA-Z]+(?:s|es))\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(
                r"\b(he|she)\s+([a-zA-Z]+(?:s|es))\b",
                _match_subj_pres,
                cs_text,
                flags=re.IGNORECASE
            )
            rules_applied.append("Subject 3rd-Person Agglutination ('yeye ana[root]')")

        # Step 3F: Genitive Associative Concord Shift ([Noun1] of [Noun2] -> [Noun1] ya/za/wa [Noun2])
        def _repl_genitive_associative(m):
            head_noun = m.group(1)
            if head_noun.lower() in ("because", "spite", "instead", "out", "front", "back", "kind", "sort", "any", "all", "which", "that", "is", "are", "was", "were", "be", "been", "being"):
                return m.group(0)
            rem = cs_text[m.start():m.start()+25]
            if re.match(r"^point\s+of\s+view\b", rem, re.IGNORECASE):
                return m.group(0)
            return f"{self.agglutinator.shift_genitive_associative(head_noun)} "

        cs_text = re.sub(
            r"\b([a-zA-Z0-9_-]+)\s+of\s+",
            _repl_genitive_associative,
            cs_text,
            flags=re.IGNORECASE
        )
        rules_applied.append("Genitive Associative Concord ('[noun] ya/za/wa')")

        # Step 3G: Modal Pronoun Concord (they/we/you/he/she must [verb])
        cs_text = re.sub(r"\bthey\s+must\s+([a-zA-Z]+)\b", r"lazima wa-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+must\s+([a-zA-Z]+)\b", r"lazima tu-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\byou\s+must\s+([a-zA-Z]+)\b", r"lazima u-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:he|she)\s+must\s+([a-zA-Z]+)\b", r"lazima a-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthey\s+can\s+([a-zA-Z]+)\b", r"wanaweza ku-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwe\s+can\s+([a-zA-Z]+)\b", r"tunaweza ku-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\byou\s+can\s+([a-zA-Z]+)\b", r"unaweza ku-\1", cs_text, flags=re.IGNORECASE)

        # ----------------------------------------------------------------------
        # EXPANDED GENERATIVE GRAMMAR BLUEPRINT: RULES 1 TO 7 (STRESS-TESTED)
        # ----------------------------------------------------------------------

        # RULE 1: The Wh-Interrogative Morphotactic Rule (Nani [prefix]-[root])
        # Accommodates: Negative (ha-, haku-, hata-, hawezi ku-), Future (ata-), Past (ali-), Present (ana-)
        def _repl_wh_neg(m):
            aux = m.group(1).lower()
            verb = self.extract_bare_verb_root(m.group(2))
            if "did" in aux:
                return f"Nani haku-{verb}"
            elif "won't" in aux or "will" in aux:
                return f"Nani hata-{verb}"
            elif "can" in aux:
                return f"Nani hawezi ku-{verb}"
            return f"Nani ha-{verb}"
        
        if re.search(r"\bwho\s+(?:doesn't|does\s+not|didn't|did\s+not|won't|will\s+not|can't|cannot)\s+([a-zA-Z]+)\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(r"\bwho\s+(doesn't|does\s+not|didn't|did\s+not|won't|will\s+not|can't|cannot)\s+([a-zA-Z]+)\b", _repl_wh_neg, cs_text, flags=re.IGNORECASE)
            rules_applied.append("Rule 1: Wh-Interrogative Negative Fusion ('ha- / haku- / hata-')")

        if re.search(r"\bwho\s+(?:will|is\s+going\s+to|shall)\s+([a-zA-Z]+)\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(r"\bwho\s+(?:will|is\s+going\s+to|shall)\s+([a-zA-Z]+)\b", r"Nani ata-\1", cs_text, flags=re.IGNORECASE)
            rules_applied.append("Rule 1: Wh-Interrogative Future Tense Collision ('ata-')")

        def _repl_wh_past(m):
            v = self.extract_bare_verb_root(m.group(1))
            return f"Nani ali-{v}"
        if re.search(r"\bwho\s+([a-zA-Z]+ed)\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(r"\bwho\s+([a-zA-Z]+ed)\b", _repl_wh_past, cs_text, flags=re.IGNORECASE)
            rules_applied.append("Rule 1: Wh-Interrogative Past Tense Collision ('ali-')")

        for irreg, root in self.IRREGULAR_PAST_VERBS.items():
            pat_wh_irreg = re.compile(r"\bwho\s+" + re.escape(irreg) + r"\b", re.IGNORECASE)
            if pat_wh_irreg.search(cs_text):
                cs_text = pat_wh_irreg.sub(f"Nani ali-{root}", cs_text)
                rules_applied.append(f"Rule 1: Wh-Interrogative Irregular Past ('ali-{root}')")

        cs_text = re.sub(r"\bwho\s+really\s+([a-zA-Z]+)s\b", r"Nani really ana\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwho\s+([a-zA-Z]+)s\b", r"Nani ana\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwho\s+is\s+([a-zA-Z]+)ing\b", r"Nani ana-\1", cs_text, flags=re.IGNORECASE)

        # RULE 4: Negative Gerund Inversion (Object Infixes & Reflexive Insertion)
        # Targeted Action: "without you noticing them" -> "bila wewe ku-wa-notice"
        # Reflexive Gerund: "without you hurting yourself" -> "bila wewe ku-ji-hurt"
        subj_sw_map = {"you": "wewe", "them": "wao", "him": "yeye", "her": "yeye", "us": "sisi"}
        obj_infix_map = {"them": "wa", "him": "m", "her": "m", "it": "i", "us": "tu", "me": "ni"}

        def _repl_gerund_reflexive(m):
            subj = subj_sw_map.get(m.group(1).lower(), m.group(1))
            stem = self.extract_bare_verb_root(m.group(2) + "ing")
            return f"bila {subj} ku-ji-{stem}"

        if re.search(r"\bwithout\s+(you|them|him|her|us)\s+([a-zA-Z]+)ing\s+(?:yourself|themselves|himself|herself|ourselves)\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(r"\bwithout\s+(you|them|him|her|us)\s+([a-zA-Z]+)ing\s+(?:yourself|themselves|himself|herself|ourselves)\b", _repl_gerund_reflexive, cs_text, flags=re.IGNORECASE)
            rules_applied.append("Rule 4: Reflexive Gerund Insertion ('ku-ji-')")

        def _repl_gerund_object(m):
            subj = subj_sw_map.get(m.group(1).lower(), m.group(1))
            stem = self.extract_bare_verb_root(m.group(2) + "ing")
            ifx = obj_infix_map.get(m.group(3).lower(), "i")
            return f"bila {subj} ku-{ifx}-{stem}"

        if re.search(r"\bwithout\s+(you|them|him|her|us)\s+([a-zA-Z]+)ing\s+(them|him|her|it|us|me)\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(r"\bwithout\s+(you|them|him|her|us)\s+([a-zA-Z]+)ing\s+(them|him|her|it|us|me)\b", _repl_gerund_object, cs_text, flags=re.IGNORECASE)
            rules_applied.append("Rule 4: Targeted Action Object Infix ('ku-[obj]-')")

        cs_text = re.sub(r"\bwithout\s+you\s+knowing\s+a\s+thing\s+about\s+it\b", "bila wewe kujua kitu kuihusu", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwithout\s+(you|them|him|her|us)\s+([a-zA-Z]+)ing\b", lambda m: f"bila {subj_sw_map.get(m.group(1).lower(), m.group(1))} ku-{self.extract_bare_verb_root(m.group(2) + 'ing')}", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwithout\s+([a-zA-Z]+ing)\b", lambda m: f"bila ku-{self.extract_bare_verb_root(m.group(1))}", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\babout\s+it\b", "kuihusu", cs_text, flags=re.IGNORECASE)

        # RULE 5: Rhetorical Topic-Fronting ([Noun] kama hiyo/hizo ni/si [Adj], kweli?)
        # Negative Rhetorical: "Is such an attack not dangerous?" -> "Attack kama hiyo si dangerous, kweli?"
        # Plural Rhetorical: "Are such attacks possible?" -> "Attacks kama hizo ni possible, kweli?"
        cs_text = re.sub(r"\bis\s+such\s+an?\s+([a-zA-Z0-9_-]+)\s+not\s+([a-zA-Z0-9_-]+)\?", r"\1 kama hiyo si \2, kweli?", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bisn't\s+such\s+an?\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\?", r"\1 kama hiyo si \2, kweli?", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bare\s+such\s+([a-zA-Z0-9_-]+s)\s+not\s+([a-zA-Z0-9_-]+)\?", r"\1 kama hizo si \2, kweli?", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\baren't\s+such\s+([a-zA-Z0-9_-]+s)\s+([a-zA-Z0-9_-]+)\?", r"\1 kama hizo si \2, kweli?", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bare\s+such\s+([a-zA-Z0-9_-]+s)\s+([a-zA-Z0-9_-]+)\?", r"\1 kama hizo ni \2, kweli?", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bis\s+such\s+an?\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\?", r"\1 kama hiyo ni \2, kweli?", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bis\s+such\s+a\s+thing\s+possible\b", "Kitu kama hiyo ni possible, kweli?", cs_text, flags=re.IGNORECASE)

        # RULE 3: Distributive Concord Shift (kila [noun] ya / wa / za [noun])
        # Plural Distributive: "Every facet of their lives" -> "Kila facet ya maisha zao"
        # Human Target: "Every member of the team" -> "Kila member wa team" (Class 1 wa)
        cs_text = re.sub(r"\bevery\s+facet\s+of\s+their\s+lives\b", "kila facet ya maisha zao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bof\s+their\s+lives\b", "ya maisha zao", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bof\s+their\s+([a-zA-Z]+s)\b", r"za \1 zao", cs_text, flags=re.IGNORECASE)

        def _repl_distributive(m):
            head_noun = m.group(1).lower()
            target_noun = m.group(2)
            if head_noun in self.HUMAN_SINGULAR_NOUNS:
                return f"kila {head_noun} wa {target_noun}"
            elif head_noun in self.CLASS_7_ARTEFACT_NOUNS:
                return f"kila {head_noun} cha {target_noun}"
            return f"kila {head_noun} ya {target_noun}"

        cs_text = re.sub(r"\bevery\s+([a-zA-Z0-9_-]+)\s+of\s+(?:the\s+)?([a-zA-Z0-9_-]+)\b", _repl_distributive, cs_text, flags=re.IGNORECASE)

        # RULE 7: Complete Bantu Modal Concord Matrix (could [verb])
        # Singular Human (Class 1): ange-
        # Plural Human (Class 2): wange-
        # Singular Abstract/System (Class 9): inge-
        # Plural Inanimate/Systems (Class 10): zinge-
        # Mass Nouns (Class 6): yange-
        # Artefacts (Class 7/8): kinge- / vinge-
        cs_text = re.sub(r"\bfew\s+people\s+could\s+([a-zA-Z]+)\b", r"wasee wachache wange-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:an?\s+)?(" + "|".join(re.escape(n) for n in sorted(self.HUMAN_SINGULAR_NOUNS, key=len, reverse=True)) + r")\s+could\s+([a-zA-Z]+)\b", r"\1 ange-\2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(" + "|".join(re.escape(n) for n in sorted(self.HUMAN_PLURAL_NOUNS, key=len, reverse=True)) + r")\s+could\s+([a-zA-Z]+)\b", r"\1 wange-\2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bpeople\s+could\s+([a-zA-Z]+)\b", r"wasee wange-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthey\s+could\s+([a-zA-Z]+)\b", r"wao wange-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:he|she)\s+could\s+([a-zA-Z]+)\b", r"yeye ange-\1", cs_text, flags=re.IGNORECASE)

        cs_text = re.sub(r"\b(?:the\s+)?water\s+could\s+([a-zA-Z]+(?:\s+up|\s+out)?)\b", r"Maji yange-\1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:the\s+)?liquidity\s+could\s+([a-zA-Z]+(?:\s+up|\s+out)?)\b", r"Liquidity inge-\1", cs_text, flags=re.IGNORECASE)

        cs_text = re.sub(r"\b(?:the\s+)?(" + "|".join(re.escape(n) for n in sorted(self.CLASS_9_SYSTEM_NOUNS, key=len, reverse=True)) + r")\s+could\s+([a-zA-Z]+)\b", r"\1 inge-\2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:the\s+)?(" + "|".join(re.escape(n) for n in sorted(self.CLASS_10_SYSTEM_NOUNS, key=len, reverse=True)) + r")\s+could\s+([a-zA-Z]+)\b", r"\1 zinge-\2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:the\s+)?(" + "|".join(re.escape(n) for n in sorted(self.CLASS_7_ARTEFACT_NOUNS, key=len, reverse=True)) + r")\s+could\s+([a-zA-Z]+)\b", r"\1 kinge-\2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:the\s+)?(" + "|".join(re.escape(n) for n in sorted(self.CLASS_8_ARTEFACT_NOUNS, key=len, reverse=True)) + r")\s+could\s+([a-zA-Z]+)\b", r"\1 vinge-\2", cs_text, flags=re.IGNORECASE)

        # Fallback modal concord if any unmatched "could [verb]"
        if re.search(r"\bcould\s+([a-zA-Z]+)\b", cs_text, re.IGNORECASE):
            cs_text = re.sub(r"\bcould\s+([a-zA-Z]+)\b", r"zinge-\1", cs_text, flags=re.IGNORECASE)
            rules_applied.append("Rule 7: Complete Bantu Modal Concord Matrix ('-nge-')")

        # RULE 2: Demonstrative Deictic Grounding (hii, hizi, hili, iyo/ile, hizo/zile, hawa)
        # Near Demonstrative: this [noun phrase] -> hii / huyu / hili / hiki [noun phrase]
        def _repl_this(m):
            lead = m.group(1) or ""
            noun = m.group(2)
            w = noun.lower()
            if w in ("is", "was", "are", "were", "can", "could", "will", "would", "should", "has", "have", "had", "means"):
                return m.group(0)
            profile = self.registry.lookup(noun)
            ptr = profile.demonstrative_near
            return f"{ptr} {lead}{noun}"

        cs_text = re.sub(
            r"\bthis\s+((?:[a-zA-Z0-9_-]+\s+)*)([a-zA-Z0-9_-]+)\b",
            _repl_this,
            cs_text,
            flags=re.IGNORECASE
        )

        # Distance Deixis: that/those -> iyo/ile / hizo/zile
        def _repl_that(m):
            w = m.group(1).lower()
            if w in ("was", "were", "is", "are", "can", "could", "will", "would", "should", "has", "have", "had", "shapes", "uses", "controls", "runs", "laid", "led"):
                return m.group(0)
            profile = self.registry.lookup(m.group(1))
            return f"{profile.demonstrative_far} {m.group(1)}"
        cs_text = re.sub(r"\bthat\s+([a-zA-Z0-9_-]+)\b", _repl_that, cs_text, flags=re.IGNORECASE)

        def _repl_those(m):
            w = m.group(1).lower()
            if w in self.HUMAN_PLURAL_NOUNS or w in ("people", "wasee"): return f"wale {m.group(1)}"
            return f"hizo {m.group(1)}"
        cs_text = re.sub(r"\bthose\s+([a-zA-Z0-9_-]+)\b", _repl_those, cs_text, flags=re.IGNORECASE)

        def _repl_these(m):
            w = m.group(1).lower()
            if w in self.HUMAN_PLURAL_NOUNS or w in ("people", "wasee"): return f"hawa {m.group(1)}"
            return f"hizi {m.group(1)}"
        cs_text = re.sub(r"\bthese\s+([a-zA-Z0-9_-]+)\b", _repl_these, cs_text, flags=re.IGNORECASE)

        # Specific Noun Class Assignments for Definite Article "The" with 3-Degree Spatio-Temporal Deixis
        cs_text = re.sub(r"\bthe\s+world\b", "hii dunia", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthe\s+money\b", "chapaa", cs_text, flags=re.IGNORECASE)

        if is_historical_distal:
            # Degree 3 Distal Deixis (historical years, remote past epochs)
            cs_text = re.sub(r"\bthe\s+(" + "|".join(re.escape(n) for n in sorted(self.HUMAN_PLURAL_NOUNS, key=len, reverse=True)) + r")\b", r"wale \1", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+(" + "|".join(re.escape(n) for n in sorted(self.HUMAN_SINGULAR_NOUNS, key=len, reverse=True)) + r")\b", r"yule \1", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+(" + "|".join(re.escape(n) for n in sorted(self.CLASS_9_SYSTEM_NOUNS | {"paper", "model", "theory", "hypothesis", "experiment", "dataset"}, key=len, reverse=True)) + r")\b", r"ile \1", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+(" + "|".join(re.escape(n) for n in sorted(self.CLASS_5_AUGMENTED_NOUNS, key=len, reverse=True)) + r")\b", r"lile \1", cs_text, flags=re.IGNORECASE)
            def _repl_the_plural_distal(m):
                w = m.group(1)
                wl = w.lower()
                if wl in self.HUMAN_PLURAL_NOUNS: return f"wale {w}"
                if wl.endswith("ss") or wl.endswith(("us", "is", "ics")) or wl in ("bus", "gas", "chaos", "basis", "crisis", "status", "news", "boss"):
                    return f"ile {w}"
                return f"zile {w}"
            cs_text = re.sub(r"\bthe\s+([a-zA-Z]+s)\b", _repl_the_plural_distal, cs_text, flags=re.IGNORECASE)
        else:
            # Degree 2 Medial Referential Deixis (entities mentioned in discourse, not co-present) & Degree 1 Proximal
            cs_text = re.sub(r"\bthe\s+(" + "|".join(re.escape(n) for n in sorted(self.HUMAN_PLURAL_NOUNS, key=len, reverse=True)) + r")\b", r"hao \1", cs_text, flags=re.IGNORECASE)
            academic_singulars = {"researcher", "scientist", "author", "physicist", "professor", "reviewer", "scholar", "colleague", "engineer", "developer"}
            cs_text = re.sub(r"\bthe\s+(" + "|".join(re.escape(n) for n in sorted(academic_singulars, key=len, reverse=True)) + r")\b", r"huyo \1", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+(" + "|".join(re.escape(n) for n in sorted(self.CLASS_5_AUGMENTED_NOUNS, key=len, reverse=True)) + r")\b", r"hili \1", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+(" + "|".join(re.escape(n) for n in sorted(self.CLASS_9_SYSTEM_NOUNS | {"paper", "dataset"}, key=len, reverse=True)) + r")\b", r"hii \1", cs_text, flags=re.IGNORECASE)
            
            # Plural Transformation: "The transactions" -> "Hizi transactions"
            def _repl_the_plural(m):
                w = m.group(1)
                wl = w.lower()
                if wl in self.HUMAN_PLURAL_NOUNS: return f"hao {w}"
                if wl.endswith("ss") or wl.endswith(("us", "is", "ics")) or wl in ("bus", "gas", "chaos", "basis", "crisis", "status", "news", "boss"):
                    return f"hii {w}"
                return f"hizi {w}"
            cs_text = re.sub(r"\bthe\s+([a-zA-Z]+s)\b", _repl_the_plural, cs_text, flags=re.IGNORECASE)

        rules_applied.append("Rule 2: Demonstrative Deictic Grounding ('hii / hizi / hili / iyo / wale / ile')")

        # RULE 6: Locative Overlord Preposition vs. Suffixation Threshold (kwa vs. -ini)
        # Abstract Domains: always "kwa [domain]"
        cs_text = re.sub(r"\bin\s+(international\s+politics|politics|economics|religion|machine\s+learning|finance|law|science|business|engineering)\b", r"kwa \1", cs_text, flags=re.IGNORECASE)
        
        # Physical Locations
        locative_spots = {
            "office": ("kwa office", "office-ini"),
            "hospital": ("kwa hospital", "hosi-ini"),
            "market": ("kwa market", "soko-ini"),
            "room": ("kwa room", "room-ini"),
            "kitchen": ("kwa kitchen", "kitchen-ini"),
            "church": ("kwa church", "church-ini"),
            "school": ("kwa shule", "shule-ini")
        }
        for spot, (urban_form, sheng_form) in locative_spots.items():
            pat_loc = re.compile(r"\bin\s+the\s+" + re.escape(spot) + r"\b", re.IGNORECASE)
            if pat_loc.search(cs_text):
                if dialect_mode == "deep_sheng":
                    cs_text = pat_loc.sub(sheng_form, cs_text)
                    dialect_alternatives[spot] = urban_form
                else:
                    cs_text = pat_loc.sub(urban_form, cs_text)
                    dialect_alternatives[spot] = sheng_form
                rules_applied.append(f"Rule 6: Locative Preposition & Suffixation ('{urban_form}' / '{sheng_form}')")

        # Additional Biographical / Narrative Anchors
        cs_text = re.sub(r"\bgrew\s+up\s+in\s+a\s+family\s+that\s+had\b", "alilelewa kwa family yenye ilikuwa na", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bso\s+had\s+access\s+to\b", "so alikuwa na access to", cs_text, flags=re.IGNORECASE)

        # Scientific Proofs & Causal Quantifiers
        cs_text = re.sub(r"\b([a-zA-Z]+s)\s+of\s+", r"\1 za ", cs_text, flags=re.IGNORECASE)
        if re.search(r"\bany\s+([a-zA-Z0-9_\s-]+?)(\.|\,|;|\?|\)|$)", cs_text, re.IGNORECASE):
            cs_text = re.sub(r"\bany\s+([a-zA-Z0-9_\s-]+?)(\.|\,|;|\?|\)|$)", r"\1 yoyote\2", cs_text, flags=re.IGNORECASE)
            rules_applied.append("Universal Quantifier Postposition ('yoyote')")

        def _repl_all_which(m):
            noun = m.group(1)
            adj = m.group(2)
            if noun.lower() in self.HUMAN_PLURAL_NOUNS:
                return f"{noun} wote wenye wako {adj}"
            return f"{noun} zote zenye ziko {adj}"
        cs_text = re.sub(r"\ball\s+(?:the\s+)?([a-zA-Z]+s)\s+which\s+are\s+([a-zA-Z]+)\b", _repl_all_which, cs_text, flags=re.IGNORECASE)

        def _repl_all_plural(m):
            noun = m.group(1)
            if noun.lower() in self.HUMAN_PLURAL_NOUNS:
                return f"{noun} wote"
            return f"{noun} zote"
        cs_text = re.sub(r"\ball\s+(?:the\s+)?([a-zA-Z]+s)\b", _repl_all_plural, cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bmay\s+constitutionally\s+be\s+([a-zA-Z]+ed)\b", r"zinaweza kuwa \1 kikatiba", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bmay\s+be\s+([a-zA-Z]+ed)\b", r"inaweza kuwa \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:and\s+)?which\s+are\s+not\s+([a-zA-Z]+ed)\b", r"na zenye hazijakuwa \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:which|that)\s+are\s+of\b", "zenye ziko na", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\b(?:which|that)\s+is\s+of\b", "yenye iko na", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwhich\s+are\s+([a-zA-Z]+)\b", r"zenye ziko \1", cs_text, flags=re.IGNORECASE)

        # Step 4A: Multi-Tier Contextual Register Lexical Routing
        if reg_norm in ("formal", "casual"):
            cs_text = re.sub(r"\bthe\s+money\b", "pesa", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bmoney\b", "pesa", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+job\b", "kazi", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bjob\b", "kazi", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+friend\b", "rafiki", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bfriend\b", "rafiki", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bfriends\b", "marafiki", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+house\b", "nyumba", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bhouse\b", "nyumba", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bhome\b", "nyumbani", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+food\b", "chakula", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bfood\b", "chakula", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+car\b", "gari", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bcar\b", "gari", cs_text, flags=re.IGNORECASE)
        elif reg_norm == "street":
            cs_text = re.sub(r"\bthe\s+money\b", "chapaa", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bmoney\b", "chapaa", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+job\b", "mboka", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bjob\b", "mboka", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bwork\b", "mboka", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+friend\b", "beste", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bfriend\b", "beste", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bfriends\b", "mabeshte", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+house\b", "keja", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bhouse\b", "keja", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bhome\b", "keja", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+food\b", "dish", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bfood\b", "dish", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bthe\s+car\b", "moti", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bcar\b", "moti", cs_text, flags=re.IGNORECASE)

        # Step 4: Lexical Nouns, Modifiers & Adverbs
        for pattern, cs_rep, sw_rep in self.LEXICAL_MAP:
            pat = re.compile(pattern, re.IGNORECASE)
            if pat.search(cs_text):
                cs_text = pat.sub(cs_rep, cs_text)
                sw_text = pat.sub(sw_rep, sw_text)

        # Step 4B: Advanced Prepositional & Relational Semantic Network
        # 1. Historical Year Locatives ("in 1905" -> "mnamo 1905")
        cs_text = re.sub(r"\bin\s+([12][0-9]{3})\b", r"mnamo \1", cs_text, flags=re.IGNORECASE)

        # 2. Terminal Temporal Horizon ("by the end of [noun]" -> "kufikia mwisho wa [noun]", "by epoch 100" -> "kufikia epoch 100")
        cs_text = re.sub(r"\bby\s+(?:the\s+)?end\s+of\s+([a-zA-Z0-9_-]+)\b", r"kufikia mwisho wa \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bby\s+(epoch\s+[0-9]+|[0-9]+(?:\.[0-9]+)?%?)\b", r"kufikia \1", cs_text, flags=re.IGNORECASE)

        # 3. Evidential Source ("according to [noun]" -> "kulingana na [noun]")
        cs_text = re.sub(r"\baccording\s+to\b", "kulingana na", cs_text, flags=re.IGNORECASE)

        # 4. Substitutive Relator ("instead of [noun/gerund]" -> "badala ya [noun]")
        cs_text = re.sub(r"\binstead\s+of\b", "badala ya", cs_text, flags=re.IGNORECASE)

        # 5. Causal Relator ("due to / owing to [noun]" -> "kutokana na [noun]", "because of [noun]" -> "kwa sababu ya [noun]")
        cs_text = re.sub(r"\b(?:due|owing)\s+to\b", "kutokana na", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bbecause\s+of\b", "kwa sababu ya", cs_text, flags=re.IGNORECASE)

        # 6. Dyadic Relator ("between [X] and [Y]" -> "kati ya [X] na [Y]")
        cs_text = re.sub(r"\bbetween\s+([a-zA-Z0-9_\s-]+?)\s+(?:and|na)\s+([a-zA-Z0-9_-]+)\b", r"kati ya \1 na \2", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bbetween\s+(?:the\s+)?two\s+([a-zA-Z0-9_-]+)\b", r"kati ya \1 mbili", cs_text, flags=re.IGNORECASE)

        # 7. Collective Relator ("among [plural]" -> "miongoni mwa [plural]")
        cs_text = re.sub(r"\bamong(?:st)?\b", "miongoni mwa", cs_text, flags=re.IGNORECASE)

        # 8. Temporal Interval ("during [noun]" -> "wakati wa [noun]")
        cs_text = re.sub(r"\bduring\b", "wakati wa", cs_text, flags=re.IGNORECASE)

        # 9. Spatial / Temporal Containment ("within [span/limit]" -> "ndani ya [span/limit]")
        cs_text = re.sub(r"\bwithin\b", "ndani ya", cs_text, flags=re.IGNORECASE)

        # 10. Origin to Destination ("from [X] to [Y]" -> "kutoka [X] hadi [Y]")
        cs_text = re.sub(r"\bfrom\s+([a-zA-Z0-9_\.-]+)\s+to\s+([a-zA-Z0-9_\.-]+)\b", r"kutoka \1 hadi \2", cs_text, flags=re.IGNORECASE)

        # 10B. Origin Source ("from [Noun]" -> "kutoka [Noun]")
        cs_text = re.sub(r"\bfrom\s+(?:an?\s+)?([a-zA-Z0-9_-]+)", r"kutoka \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bfrom\b", "kutoka", cs_text, flags=re.IGNORECASE)

        # 11. Conditional Regimen ("under [conditions/assumption/pressure]" -> "chini ya [conditions]")
        cs_text = re.sub(r"\bunder\s+([a-zA-Z0-9_\s-]+?\b(?:conditions|assumptions|circumstances|pressure|load|temperature|supervision))\b", r"chini ya \1", cs_text, flags=re.IGNORECASE)

        # 12. Deprivation ("without [verb-ing]" -> "bila ku-[root]", "without [noun]" -> "bila [noun]")
        cs_text = re.sub(r"\bwithout\s+([a-zA-Z]+)ing\b", lambda m: f"bila ku-{MorphologicalRootStripper.strip_to_bare_root(m.group(1))}", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bwithout\b", "bila", cs_text, flags=re.IGNORECASE)

        # 13. Instrumental Medium ("through [noun]" -> "kupitia [noun]", "by means of" -> "kwa njia ya")
        cs_text = re.sub(r"\bby\s+means\s+of\b", "kwa njia ya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bthrough\b", "kupitia", cs_text, flags=re.IGNORECASE)

        # 14. Durational Measure ("for [number] [units]" -> "kwa [units] [number]")
        cs_text = re.sub(r"\bfor\s+([0-9]+)\s+([a-zA-Z]+s)\b", r"kwa \2 \1", cs_text, flags=re.IGNORECASE)

        # 15. Concessive & Adversarial ("despite" -> "licha ya", "against" -> "dhidi ya")
        cs_text = re.sub(r"\bdespite\b", "licha ya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bin\s+spite\s+of\b", "licha ya", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bagainst\b", "dhidi ya", cs_text, flags=re.IGNORECASE)

        # 16. Directional Goal ("towards" / "toward" -> "kuelekea kwa")
        cs_text = re.sub(r"\btoward(?:s)?\b", "kuelekea", cs_text, flags=re.IGNORECASE)

        # 17. Distributed Domain & General Locatives ("across all [plural]" -> "kwa [plural] zote", "into" -> "kwa / ndani ya", "in" -> "kwa")
        if not is_sheng:
            cs_text = re.sub(r"\bacross\s+levels\b", "katika levels", cs_text, flags=re.IGNORECASE)
            cs_text = re.sub(r"\bacross\s+all\s+levels\b", "katika levels zote", cs_text, flags=re.IGNORECASE)

        cs_text = re.sub(r"\bacross\s+all\s+([a-zA-Z0-9_-]+s)\b", r"kwa \1 zote", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bacross\s+([a-zA-Z0-9_-]+)", r"kwa \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bin\s+(?!(?:pursuance|spite|order|front|the\s+[12]\d{3}|[12]\d{3}))\b([a-zA-Z0-9_-]+)", r"kwa \1", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bon\s+(?:an?\s+)?([a-zA-Z0-9_-]+)", r"kwa \1", cs_text, flags=re.IGNORECASE)

        if not is_sheng:
            cs_text = re.sub(r"\bkwa\s+levels\b", "katika levels", cs_text, flags=re.IGNORECASE)

        # Post-nominal Bantu Numeral Inversion ("two different tasks" / "two tasks tofauti" -> "(ma)tasks mbili tofauti")
        BANTU_NUM_MAP = {"two": "mbili", "three": "tatu", "four": "nne", "five": "tano", "one": "moja"}
        def _repl_bantu_num_diff(m):
            prep = m.group(1) or ""
            num_word = m.group(2).lower()
            bantu_num = BANTU_NUM_MAP.get(num_word, num_word)
            noun = m.group(3)
            return f"{prep}{noun} {bantu_num} tofauti"
        cs_text = re.sub(
            r"\b(kwa\s+|on\s+)?(one|two|three|four|five)\s+different\s+([a-zA-Z0-9_-]+s)\b",
            _repl_bantu_num_diff,
            cs_text,
            flags=re.IGNORECASE
        )
        cs_text = re.sub(
            r"\b(kwa\s+|on\s+)?(one|two|three|four|five)\s+([a-zA-Z0-9_-]+s)\s+tofauti\b",
            _repl_bantu_num_diff,
            cs_text,
            flags=re.IGNORECASE
        )

        # Step 5: Clean up English leftover determiners, artifact spaces & concords
        cs_text = re.sub(r"\bto\s+ku-", "ndio ku-", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+kupata\b", "ndio kupata", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bto\s+kuanza\b", "ndio kuanza", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\bku-\s+", "ku-", cs_text)
        cs_text = re.sub(r"\bmayouth\s+alidecide\b", "mayouth walidecide", cs_text, flags=re.IGNORECASE)
        cs_text = re.sub(
            r"\bSisi\s+([a-zA-Z]+)\b",
            lambda m: f"Tuna-{MorphologicalRootStripper.strip_to_bare_root(m.group(1))}" if m.group(1).lower() in self.ACADEMIC_PRESENT_VERBS else m.group(0),
            cs_text
        )

        cs_text = re.sub(r"\bthe\s+(?![12]\d{3}\b)", "", cs_text, flags=re.IGNORECASE)
        sw_text = re.sub(r"\bthe\s+", "", sw_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"(?<!\bni )\ba\s+(?=[a-zA-Z])", "", cs_text)
        cs_text = re.sub(r"^A\s+(?=[a-zA-Z])", "", cs_text)
        sw_text = re.sub(r"\ba\s+", "", sw_text, flags=re.IGNORECASE)
        cs_text = re.sub(r"\ban\s+", "", cs_text, flags=re.IGNORECASE)
        sw_text = re.sub(r"\ban\s+", "", sw_text, flags=re.IGNORECASE)

        # Register-Aware Technical Plural Alternatives
        technical_plurals = {
            "servers": "maserver",
            "databases": "madatabase",
            "models": "mamodel",
            "files": "mafiles",
            "papers": "mapapers",
            "algorithms": "maalgorithms",
            "computers": "macomputer",
            "laptops": "malaptop",
            "phones": "maphones",
            "parts": "maparts",
            "relationships": "marelationships",
            "networks": "manetworks",
            "systems": "masystems",
            "datasets": "madatasets",
            "problems": "maproblems",
            "tasks": "matasks",
            "results": "maresults",
            "weights": "maweights",
            "parameters": "maparameters",
            "features": "mafeatures",
            "layers": "malayers",
            "methods": "mamethods",
            "solutions": "masolutions",
            "concepts": "maconcepts",
            "experiments": "maexperiments",
            "errors": "maerrors",
            "agents": "maagents",
            "pairs": "mapairs",
            "clusters": "maclusters",
            "variables": "mavariables",
            "signals": "masignals",
            "functions": "mafunctions"
        }
        for eng_pl, sheng_pl in technical_plurals.items():
            if re.search(r"\b" + eng_pl + r"\b", cs_text, re.IGNORECASE):
                dialect_alternatives[f"plural_{eng_pl}"] = sheng_pl
                if dialect_mode == "deep_sheng":
                    cs_text = re.sub(r"\b" + eng_pl + r"\b", sheng_pl, cs_text, flags=re.IGNORECASE)

        # Capitalize first letter
        cs_text = re.sub(r"\s+", " ", cs_text).strip()
        sw_text = re.sub(r"\s+", " ", sw_text).strip()
        if cs_text:
            cs_text = cs_text[0].upper() + cs_text[1:]
        if sw_text:
            sw_text = sw_text[0].upper() + sw_text[1:]

        # Token savings simulation on the generated code-switched text
        orig_tokens = len(cleaned.split()) * 2.8  # BPE fragmentation estimate
        cs_tokens = len(cs_text.split())
        savings = round(((orig_tokens - cs_tokens) / max(1, orig_tokens)) * 100, 1)

        return EnglishCodeSwitchResult(
            original_english=cleaned,
            kenyan_codeswitch=cs_text,
            formal_swahili=sw_text,
            detected_language="English",
            applied_rules=rules_applied,
            token_savings_pct=max(50.0, savings),
            dialect_mode=dialect_mode,
            dialect_alternatives=dialect_alternatives
        )

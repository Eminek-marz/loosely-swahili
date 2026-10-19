"""
Synthetic NLP Training Dataset Generator for Kenyan Code-Switching (Sheng / Tech KCS)
Produces large-scale, morphotactically validated parallel corpora for fine-tuning
open-weights LLMs (Llama 3, Mistral, Gemma, Qwen) or sequence-to-sequence models.

Features:
  1. Six Morphotactic Matrix Scenarios:
     - Scenario 1: Passive Voice Agglutination ([Subject] + is/was [verb-ed] by -> [Subject] [prefix][tense]-[root]wa na)
     - Scenario 2: Future Hypothetical Sub-Graph ([Subject] would have [verb-ed] -> [Subject] [prefix]ngekuwa [prefix]me-[root])
     - Scenario 3: Quantum Modal & Relative Clauses (Everything that can [verb] does [verb] -> Kila kitu enye inaweza [verb] inaweza ku[Verb])
     - Scenario 4: Loanword Pluralization Tokenizer (ma- prefixing: ma-manager, ma-system)
     - Scenario 5: Preposition Alignment Matrix (by/of/for/with governed by Bantu Noun Classes)
     - Scenario 6: Habitual Consecutive Infinitives (who use [X] to [Y] -> enye hutumia [X] ku-[Y])
  2. Multi-Format Prompt Wrappers:
     - Tagged: <|src_en|> ... </|src_en|> <|tgt_kcs|> ... </|tgt_kcs|>
     - Llama-3 / ChatML: <|begin_of_text|><|start_header_id|>...
     - Alpaca JSON: instruction / input / output
     - HuggingFace ShareGPT
  3. Register & Slang Conditioning:
     - 'tech_standard': Professional corporate/engineering code-switching (preserving technical loanwords)
     - 'urban_street': Nairobi youth vernacular (applying slang overlays like chapaa, mboka, moti, wasee)
"""

import os
import sys
import re
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.english_to_codeswitch import (
    BantuNounClassRegistry,
    MorphologicalRootStripper,
    EnglishToKenyanCodeSwitcher,
    EMPHATIC_NOUN_REGISTRY,
    preserve_case_first_word,
    native_agglutination_filter,
    informal_purpose_bridge_filter,
    clean_and_tune_dataset_pair,
)

# ==============================================================================
# VOCABULARY & DOMAIN EXPANSION POOLS
# ==============================================================================

NOUN_POOL: Dict[str, List[Tuple[str, str, str]]] = {
    # (singular_form, plural_form, noun_class)
    "systems": [
        ("system", "systems", "c9"),
        ("network", "networks", "c9"),
        ("database", "databases", "c9"),
        ("server", "servers", "c9"),
        ("model", "models", "c9"),
        ("algorithm", "algorithms", "c9"),
        ("architecture", "architectures", "c9"),
        ("infrastructure", "infrastructures", "c9"),
        ("pipeline", "pipelines", "c9"),
        ("transaction", "transactions", "c9"),
        ("ledger", "ledgers", "c9"),
        ("protocol", "protocols", "c9")
    ],
    "humans": [
        ("engineer", "engineers", "c1"),
        ("developer", "developers", "c1"),
        ("architect", "architects", "c1"),
        ("specialist", "specialists", "c1"),
        ("manager", "managers", "c1"),
        ("hacker", "hackers", "c1"),
        ("validator", "validators", "c1"),
        ("doctor", "doctors", "c1"),
        ("user", "users", "c1"),
        ("admin", "admins", "c1")
    ],
    "artefacts": [
        ("device", "devices", "c7"),
        ("sensor", "sensors", "c7"),
        ("tool", "tools", "c7"),
        ("gadget", "gadgets", "c7"),
        ("satellite", "satellites", "c7")
    ],
    "publications": [
        ("book", "books", "c9"),
        ("paper", "papers", "c9"),
        ("article", "articles", "c9"),
        ("report", "reports", "c9"),
        ("manifesto", "manifestos", "c9")
    ]
}

AUTHORS = [
    "Brian Cox", "Alan Turing", "Claude Shannon", "Geoffrey Hinton",
    "John von Neumann", "Richard Feynman", "Tim Nitche", "Satoshi Nakamoto"
]

VERB_POOL = [
    {"root": "monitor", "past": "monitored", "pres_s": "monitors", "pres_prog": "monitoring"},
    {"root": "control", "past": "controlled", "pres_s": "controls", "pres_prog": "controlling"},
    {"root": "fail", "past": "failed", "pres_s": "fails", "pres_prog": "failing"},
    {"root": "notice", "past": "noticed", "pres_s": "notices", "pres_prog": "noticing"},
    {"root": "verify", "past": "verified", "pres_s": "verifies", "pres_prog": "verifying"},
    {"root": "protect", "past": "protected", "pres_s": "protects", "pres_prog": "protecting"},
    {"root": "optimize", "past": "optimized", "pres_s": "optimizes", "pres_prog": "optimizing"},
    {"root": "influence", "past": "influenced", "pres_s": "influences", "pres_prog": "influencing"},
    {"root": "shape", "past": "shaped", "pres_s": "shapes", "pres_prog": "shaping"},
    {"root": "upgrade", "past": "upgraded", "pres_s": "upgrades", "pres_prog": "upgrading"},
    {"root": "deploy", "past": "deployed", "pres_s": "deploys", "pres_prog": "deploying"},
    {"root": "cancel", "past": "canceled", "pres_s": "cancels", "pres_prog": "canceling"},
    {"root": "happen", "past": "happened", "pres_s": "happens", "pres_prog": "happening"}
]

# ==============================================================================
# MULTI-TIER PROBABILISTIC LEXICON & NEGATION MATRICES
# ==============================================================================

PROBABILISTIC_LEXICON: Dict[str, Dict[str, List[Tuple[str, float]]]] = {
    "money": {
        "formal": [("money", 0.6), ("pesa", 0.4), ("chapaa", 0.0)],
        "casual": [("money", 0.2), ("pesa", 0.6), ("chapaa", 0.2)],
        "street": [("ganji", 0.4), ("chapaa", 0.5), ("pesa", 0.1)]
    },
    "cash": {
        "formal": [("cash", 0.7), ("pesa taslimu", 0.3), ("chapaa", 0.0)],
        "casual": [("cash", 0.5), ("pesa", 0.4), ("chapaa", 0.1)],
        "street": [("chapaa", 0.6), ("ganji", 0.3), ("cash", 0.1)]
    },
    "job": {
        "formal": [("job", 0.5), ("kazi", 0.5), ("mboka", 0.0)],
        "casual": [("job", 0.4), ("kazi", 0.5), ("mboka", 0.1)],
        "street": [("mboka", 0.7), ("job", 0.2), ("kazi", 0.1)]
    },
    "work": {
        "formal": [("work", 0.5), ("kazi", 0.5), ("mboka", 0.0)],
        "casual": [("kazi", 0.6), ("work", 0.3), ("mboka", 0.1)],
        "street": [("mboka", 0.7), ("kazi", 0.2), ("job", 0.1)]
    },
    "friend": {
        "formal": [("colleague", 0.5), ("friend", 0.5), ("msee", 0.0)],
        "casual": [("friend", 0.3), ("rafiki", 0.4), ("msee", 0.3)],
        "street": [("beste", 0.4), ("buda", 0.3), ("msee", 0.3)]
    },
    "friends": {
        "formal": [("colleagues", 0.5), ("friends", 0.5), ("wasee", 0.0)],
        "casual": [("marafiki", 0.4), ("friends", 0.3), ("mabeshte", 0.3)],
        "street": [("mabeshte", 0.6), ("wasee", 0.3), ("mabuda", 0.1)]
    },
    "house": {
        "formal": [("house", 0.6), ("nyumba", 0.4), ("keja", 0.0)],
        "casual": [("house", 0.2), ("nyumba", 0.6), ("keja", 0.2)],
        "street": [("keja", 0.6), ("base", 0.3), ("nyumba", 0.1)]
    },
    "home": {
        "formal": [("home", 0.6), ("nyumbani", 0.4), ("keja", 0.0)],
        "casual": [("nyumbani", 0.6), ("home", 0.2), ("keja", 0.2)],
        "street": [("keja", 0.7), ("base", 0.2), ("nyumbani", 0.1)]
    },
    "understand": {
        "formal": [("understand", 0.7), ("elewa", 0.3), ("shika", 0.0)],
        "casual": [("elewa", 0.5), ("understand", 0.3), ("shika", 0.2)],
        "street": [("shika", 0.5), ("ng'amua", 0.3), ("elewa", 0.2)]
    },
    "car": {
        "formal": [("car", 0.6), ("gari", 0.4), ("moti", 0.0)],
        "casual": [("gari", 0.6), ("car", 0.3), ("moti", 0.1)],
        "street": [("moti", 0.7), ("ndae", 0.2), ("gari", 0.1)]
    },
    "food": {
        "formal": [("food", 0.6), ("chakula", 0.4), ("dish", 0.0)],
        "casual": [("chakula", 0.6), ("dish", 0.3), ("food", 0.1)],
        "street": [("dish", 0.6), ("msosi", 0.3), ("chakula", 0.1)]
    },
    "people": {
        "formal": [("people", 0.5), ("watu", 0.5), ("wasee", 0.0)],
        "casual": [("watu", 0.6), ("wasee", 0.3), ("people", 0.1)],
        "street": [("wasee", 0.7), ("mayouth", 0.2), ("watu", 0.1)]
    }
}

PROBABILISTIC_NEGATION: Dict[str, Dict[str, List[Tuple[str, float]]]] = {
    "i don't care": {
        "formal": [("sijali", 0.6), ("sina wasiwasi", 0.4)],
        "casual": [("sijali", 0.5), ("sina shughuli", 0.4), ("i don't care", 0.1)],
        "street": [("sina shughuli", 0.5), ("sina time", 0.3), ("sina stress", 0.2)]
    },
    "we didn't agree": {
        "formal": [("hatukukubaliana", 0.8), ("hatukufikia makubaliano", 0.2)],
        "casual": [("hatukukubaliana", 0.5), ("hatukusikizana", 0.3), ("hatuku-agree", 0.2)],
        "street": [("hatukuskizana", 0.5), ("hatukuagree hiyo form", 0.3), ("hiyo risto haikushika", 0.2)]
    },
    "he doesn't know": {
        "formal": [("hajui", 0.8), ("hana taarifa", 0.2)],
        "casual": [("hajui", 0.7), ("hajui hiyo kitu", 0.2), ("he doesn't know", 0.1)],
        "street": [("hananga clue", 0.5), ("hajui kitu", 0.3), ("hajui risto", 0.2)]
    },
    "they don't know": {
        "formal": [("hawajui", 0.8), ("hawana taarifa", 0.2)],
        "casual": [("hawajui", 0.7), ("hawajui kitu", 0.2), ("they don't know", 0.1)],
        "street": [("hawananga clue", 0.5), ("hawajui risto", 0.3), ("hawajui kitu", 0.2)]
    },
    "i don't have money": {
        "formal": [("sina pesa", 0.8), ("sina fedha", 0.2)],
        "casual": [("sina pesa", 0.6), ("sina cash", 0.3), ("i don't have money", 0.1)],
        "street": [("sina chapaa", 0.5), ("niko broken", 0.3), ("sina ganji", 0.2)]
    },
    "they don't understand": {
        "formal": [("hawaelewi", 0.8), ("hawaelewi dhana hii", 0.2)],
        "casual": [("hawaelewi", 0.5), ("hawashiki", 0.3), ("hawana understanding", 0.2)],
        "street": [("hawashiki", 0.5), ("hawang'amui", 0.3), ("hawashiki risto", 0.2)]
    },
    "we don't understand": {
        "formal": [("hatuelewi", 0.8), ("hatuelewi jambo hili", 0.2)],
        "casual": [("hatuelewi", 0.5), ("hatushiki", 0.4), ("we don't understand", 0.1)],
        "street": [("hatushiki", 0.6), ("hatung'amui", 0.3), ("hatushiki hiyo form", 0.1)]
    },
    "don't worry": {
        "formal": [("usijali", 0.7), ("usiwe na wasiwasi", 0.3)],
        "casual": [("usijali", 0.6), ("usiwe na wasiwasi", 0.3), ("don't worry", 0.1)],
        "street": [("usi-stress", 0.5), ("tuliza wenge", 0.3), ("no stress", 0.2)]
    },
    "we cannot stop": {
        "formal": [("hatuwezi kusimama", 0.8), ("hatuwezi kusitisha", 0.2)],
        "casual": [("hatuwezi ku-stop", 0.6), ("hatuwezi kusimama", 0.4)],
        "street": [("hatuezi ku-stop", 0.6), ("hatuezi ku-stop hii mboka", 0.4)]
    }
}

def choose_weighted_token(concept: str, context: str, rng: Optional[random.Random] = None) -> str:
    """Selects a word token based on the selected register and weighted probability profile."""
    r = rng or random
    c_lower = concept.lower()
    ctx = context.lower()
    if ctx in ("tech_standard", "corporate"):
        ctx = "formal"
    elif ctx in ("urban_street", "deep_sheng", "slang"):
        ctx = "street"
    elif ctx not in ("formal", "casual", "street"):
        ctx = "casual"

    if c_lower in PROBABILISTIC_LEXICON:
        options_profile = PROBABILISTIC_LEXICON[c_lower].get(ctx, PROBABILISTIC_LEXICON[c_lower]["casual"])
        tokens, weights = zip(*options_profile)
        return r.choices(tokens, weights=weights, k=1)[0]
    return concept

def choose_weighted_negation(neg_phrase: str, context: str, rng: Optional[random.Random] = None) -> str:
    """Selects an everyday verb negation based on the selected register and weighted probability profile."""
    r = rng or random
    p_lower = neg_phrase.lower().strip()
    ctx = context.lower()
    if ctx in ("tech_standard", "corporate"):
        ctx = "formal"
    elif ctx in ("urban_street", "deep_sheng", "slang"):
        ctx = "street"
    elif ctx not in ("formal", "casual", "street"):
        ctx = "casual"

    if p_lower in PROBABILISTIC_NEGATION:
        options_profile = PROBABILISTIC_NEGATION[p_lower].get(ctx, PROBABILISTIC_NEGATION[p_lower]["casual"])
        tokens, weights = zip(*options_profile)
        return r.choices(tokens, weights=weights, k=1)[0]
    return neg_phrase

def generate_context_weighted_pair(eng_sentence: str, context: str = "casual", rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """Generates a code-switched target that respects text context probabilities for NLP training."""
    words = eng_sentence.lower().split()
    target_words = []
    r = rng or random
    ctx = context.lower()
    if ctx in ("tech_standard", "corporate"):
        ctx = "formal"
    elif ctx in ("urban_street", "deep_sheng", "slang"):
        ctx = "street"
    elif ctx not in ("formal", "casual", "street"):
        ctx = "casual"

    for word in words:
        clean_word = word.strip(",.?!")
        suffix = word[len(clean_word):] if len(word) > len(clean_word) else ""
        if clean_word in PROBABILISTIC_LEXICON:
            selected_token = choose_weighted_token(clean_word, ctx, rng=r)
            target_words.append(selected_token + suffix)
        else:
            target_words.append(word)

    control_token = f"[GENERATE_{ctx.upper()}]"
    cs_out = " ".join(target_words)
    if cs_out:
        cs_out = cs_out[0].upper() + cs_out[1:]
    if not cs_out.endswith((".", "!", "?")):
        cs_out += "."

    return {
        "english": eng_sentence,
        "context_tag": ctx,
        "control_token": control_token,
        "kenyan_code_switch": cs_out
    }

def apply_emphatic_pointing(sentence: str, focus_noun: str, register: str = "casual", front: bool = False) -> str:
    """Wraps focus_noun in emphasis syntax and applies demonstrative pointing or fronting concord."""
    switcher = EnglishToKenyanCodeSwitcher()
    marked = sentence
    if f"*{focus_noun}*" not in marked and f"_{focus_noun}_" not in marked:
        marked = re.sub(rf"\b(?:the\s+)?{re.escape(focus_noun)}\b", f"*{focus_noun}*", marked, flags=re.IGNORECASE, count=1)
    
    front_tag = "[FRONT_FOCUS] " if front else ""
    ctrl_token = f"[GENERATE_{register.upper()}] "
    return switcher.code_switch_sentence(f"{ctrl_token}{front_tag}{marked}").kenyan_codeswitch

def generate_emphatic_training_pair(register: str = "casual", front: bool = False, rng: Optional[random.Random] = None, seamless: bool = False) -> Dict[str, Any]:
    """Generates a structured training pair exhibiting demonstrative object fronting or pointing concord with object infixes."""
    r = rng or random.Random()
    templates = [
        ("We cannot stop the *system* now.", "system"),
        ("I don't have money to buy *food* today.", "food"),
        ("We must monitor *transactions* now.", "transactions"),
        ("They want to monitor *transactions*.", "transactions"),
        ("We must call the *engineers* now.", "engineers"),
        ("We must call the *manager* now.", "manager"),
        ("We cannot stop the *systems* now.", "systems"),
        ("They cannot stop the *database* now.", "database")
    ]
    eng_template, focus_noun = r.choice(templates)
    switcher = EnglishToKenyanCodeSwitcher()
    front_tag = "[FRONT_FOCUS] " if front else ""
    ctrl_token = f"[GENERATE_{register.upper()}] "
    res = switcher.code_switch_sentence(f"{ctrl_token}{front_tag}{eng_template}")
    
    rules = ["Demonstrative Pointing Concord", "Object Pronoun Infix Integration"]
    if front:
        rules.append("Demonstrative Left-Dislocation Fronting")
    else:
        rules.append("In-Situ Pointing Concord")

    pair = {
        "scenario": "emphatic_pointing_and_fronting",
        "english": eng_template,
        "kenyan_code_switch": res.kenyan_codeswitch,
        "focus_noun": focus_noun,
        "is_front_focus": front,
        "register": register,
        "control_token": f"[GENERATE_{register.upper()}]",
        "rules": rules
    }
    if seamless:
        pair = clean_and_tune_dataset_pair(pair, seamless=True)
    return pair

SYSTEM_INSTRUCTION = (
    "You are an expert bilingual AI specialized in natural Kenyan Code-Switching (Sheng / Technical Swahili-English Blend). "
    "Translate the given English input into authentic Kenyan Code-Switching. You natively understand and obey register instruction control tokens: "
    "[GENERATE_FORMAL] (corporate/tech/standard without slang), [GENERATE_CASUAL] (standard conversational Swahili baseline), and [GENERATE_STREET] (high-velocity Nairobi youth Sheng slang). "
    "Strictly adhere to Bantu morphotactics: inflect bare English roots (0% *-ed endings), execute post-nominal possessive inversion (yetu/zao), resolve Bantu noun class "
    "concords (i-/zi-/wa-), map modal auxiliaries, apply loanword pluralization, and execute demonstrative object pointing concord and fronting accurately."
)

# ==============================================================================
# CORE SYNTHETIC GENERATOR ENGINE
# ==============================================================================

class SyntheticCodeSwitchGenerator:
    """Generates mathematically sound and linguistically authentic parallel training pairs."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.registry = BantuNounClassRegistry()
        self.switcher = EnglishToKenyanCodeSwitcher()

    def generate_sample(self, register: Optional[str] = None) -> Dict[str, Any]:
        """Generates a single synthetic training pair across morphotactic and register scenarios."""
        # Normalize register
        if not register or register == "random":
            reg = self.rng.choice(["formal", "casual", "street"])
        elif register in ("tech_standard", "corporate"):
            reg = "formal"
        elif register in ("urban_street", "deep_sheng", "slang"):
            reg = "street"
        elif register in ("urban_standard", "casual"):
            reg = "casual"
        else:
            reg = register.lower()

        scenario = self.rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
        
        if scenario == 1:
            sample = self._generate_passive_voice(reg)
        elif scenario == 2:
            sample = self._generate_future_hypothetical(reg)
        elif scenario == 3:
            sample = self._generate_quantum_modal(reg)
        elif scenario == 4:
            sample = self._generate_loanword_plural(reg)
        elif scenario == 5:
            sample = self._generate_preposition_authorship(reg)
        elif scenario == 6:
            sample = self._generate_habitual_consecutive(reg)
        elif scenario == 7:
            sample = self._generate_context_weighted_register(reg)
        elif scenario == 8:
            sample = self._generate_everyday_negation(reg)
        else:
            sample = self._generate_emphatic_pointing_scenario(reg)

        sample["register"] = reg
        sample["control_token"] = f"[GENERATE_{reg.upper()}]"
        return sample

    def _generate_passive_voice(self, register: str) -> Dict[str, Any]:
        """Scenario 1: Passive Voice Agglutination Rule."""
        category = self.rng.choice(["systems", "artefacts"])
        singular, plural, n_class = self.rng.choice(NOUN_POOL[category])
        is_plural = self.rng.choice([True, False])
        noun = plural if is_plural else singular
        verb = self.rng.choice([v for v in VERB_POOL if v["root"] != "happen"])
        tense = self.rng.choice(["present", "past"])
        agent_s, agent_p, _ = self.rng.choice(NOUN_POOL["humans"])

        if is_plural:
            subj_pfx = "zi"
            aux = "are" if tense == "present" else "were"
            t_infix = "na" if tense == "present" else "li"
        else:
            subj_pfx = "i"
            aux = "is" if tense == "present" else "was"
            t_infix = "na" if tense == "present" else "li"

        eng = f"The {noun} {aux} {verb['past']} by {agent_p}."
        
        # Morphotactically fused code-switch
        hybrid_verb = f"{subj_pfx}{t_infix}{verb['root']}iwa" if not verb['root'].endswith('e') else f"{subj_pfx}{t_infix}{verb['root'][:-1]}iwa"
        # Check standard spelling
        if verb['root'] == "monitor": hybrid_verb = f"{subj_pfx}{t_infix}monitoriwa"
        elif verb['root'] == "verify": hybrid_verb = f"{subj_pfx}{t_infix}verifyiwa"
        elif verb['root'] == "protect": hybrid_verb = f"{subj_pfx}{t_infix}protectiwa"
        elif verb['root'] == "upgrade": hybrid_verb = f"{subj_pfx}{t_infix}upgradiwa"
        elif verb['root'] == "influence": hybrid_verb = f"{subj_pfx}{t_infix}influenciwa"
        elif verb['root'] == "control": hybrid_verb = f"{subj_pfx}{t_infix}controliwa"
        elif verb['root'] == "cancel": hybrid_verb = f"{subj_pfx}{t_infix}canceliwa"

        kcs = f"{noun.capitalize()} {hybrid_verb} na {agent_p}."

        return {
            "scenario": "passive_voice_morphotactics",
            "english": eng,
            "kenyan_code_switch": kcs,
            "rules": ["Pillar I & II: Morphotactic Passive Fusion", "Bantu Noun Class Agreement"]
        }

    def _generate_future_hypothetical(self, register: str) -> Dict[str, Any]:
        """Scenario 2: Future Hypothetical Tense Sub-Graph (would have [verb-ed])."""
        category = self.rng.choice(["systems", "humans"])
        singular, plural, n_class = self.rng.choice(NOUN_POOL[category])
        is_plural = self.rng.choice([True, False])
        noun = plural if is_plural else singular
        verb = self.rng.choice([v for v in VERB_POOL if v["root"] in ("fail", "notice", "crash", "stop", "succeed", "happen")])

        if category == "humans":
            pfx = "wa" if is_plural else "a"
        else:
            pfx = "zi" if is_plural else "i"

        eng = f"The {noun} would have {verb['past']} yesterday."
        kcs = f"{noun.capitalize()} {pfx}ngekuwa {pfx}me{verb['root']} jana."

        return {
            "scenario": "future_hypothetical_subgraph",
            "english": eng,
            "kenyan_code_switch": kcs,
            "rules": ["Future Hypothetical Sub-Graph ('[prefix]ngekuwa [prefix]me-[root]')"]
        }

    def _generate_quantum_modal(self, register: str) -> Dict[str, Any]:
        """Scenario 3: Quantum Modal Clause & Compound Pronoun."""
        verb = self.rng.choice([v for v in VERB_POOL if v["root"] in ("happen", "fail", "change", "occur")])
        sys_s, sys_p, _ = self.rng.choice(NOUN_POOL["systems"])

        eng = f"Everything that can {verb['root']} does {verb['root']} inside the {sys_s}."
        kcs = f"Kila kitu enye inaweza {verb['root']} inaweza ku{verb['root'].capitalize()} ndani ya {sys_s}."

        return {
            "scenario": "quantum_modal_clause",
            "english": eng,
            "kenyan_code_switch": kcs,
            "rules": ["Compound Relative Pronoun ('kila kitu enye')", "Modal Auxiliary Mapping ('inaweza')", "Emphatic Declarative Inversion"]
        }

    def _generate_loanword_plural(self, register: str) -> Dict[str, Any]:
        """Scenario 4: Loanword Pluralization Tokenizer (ma- prefixing)."""
        category = self.rng.choice(["systems", "humans"])
        singular, plural, _ = self.rng.choice(NOUN_POOL[category])
        verb = self.rng.choice([v for v in VERB_POOL if v["root"] in ("delay", "fail", "crash", "deploy", "monitor")])

        eng = f"The {plural} {verb['past']} the operations."
        
        # When in urban mode or loanword prefixing:
        ma_noun = f"ma-{singular}"
        subj_pfx = "wali" if category == "humans" else "zili"
        kcs = f"{ma_noun.capitalize()} {subj_pfx}-{verb['root']} operations."

        return {
            "scenario": "loanword_plural_ma_prefix",
            "english": eng,
            "kenyan_code_switch": kcs,
            "rules": ["Class 6 Loanword Collective ('ma-')", "Pillar I: Bare Root Constraint"]
        }

    def _generate_preposition_authorship(self, register: str) -> Dict[str, Any]:
        """Scenario 5: Preposition Alignment Matrix (Authorship / Possession)."""
        pub_s, pub_p, _ = self.rng.choice(NOUN_POOL["publications"])
        author = self.rng.choice(AUTHORS)
        is_plural = self.rng.choice([True, False])
        year = self.rng.randint(2010, 2024)

        if is_plural:
            eng = f"These are {year} {pub_p} by {author}."
            kcs = f"Hizi ni {pub_p} za {year} za {author}."
        else:
            eng = f"Everything That Can Happen Does Happen is a {year} {pub_s} by {author}."
            kcs = f"Kila kitu enye inaweza happen inaweza kuHappen ni a {year} {pub_s} ya {author}."

        return {
            "scenario": "preposition_alignment_authorship",
            "english": eng,
            "kenyan_code_switch": kcs,
            "rules": ["Preposition Alignment Matrix ('ya/za')", "Demonstrative Deictic Grounding"]
        }

    def _generate_habitual_consecutive(self, register: str) -> Dict[str, Any]:
        """Scenario 6: Habitual Consecutive Infinitives."""
        h_s, h_p, _ = self.rng.choice(NOUN_POOL["humans"])
        tool_s, tool_p, _ = self.rng.choice(NOUN_POOL["systems"])
        v_action = self.rng.choice(["protect", "verify", "monitor", "optimize", "secure"])
        target_s, target_p, _ = self.rng.choice(NOUN_POOL["systems"])

        eng = f"The {h_p} who use {tool_p} to {v_action} our {target_p}."
        kcs = f"{h_p.capitalize()} enye hutumia {tool_p} ku-{v_action} {target_p} zetu."

        return {
            "scenario": "habitual_consecutive_infinitive",
            "english": eng,
            "kenyan_code_switch": kcs,
            "rules": ["Consecutive Infinitive Integration ('hutumia ... ku-[root]')", "Post-nominal Possessive Inversion"]
        }

    def _generate_context_weighted_register(self, register: str) -> Dict[str, Any]:
        """Scenario 7: Multi-Tier Context-Weighted Conversational Register."""
        templates = [
            "My friend got a new job to make more money.",
            "The people need money to buy food for their home.",
            "His friend bought a car with his money.",
            "They understand that the job requires more money.",
            "The workers want a job to buy food for their home.",
            "My friend is at home looking for a new job.",
            "The police saw the car near his house."
        ]
        eng = self.rng.choice(templates)
        res = self.switcher.code_switch_sentence(f"[GENERATE_{register.upper()}] {eng}")
        
        return {
            "scenario": "context_weighted_conversational_register",
            "english": eng,
            "kenyan_code_switch": res.kenyan_codeswitch,
            "rules": [f"Multi-Tier Context Register ('{register}')", "Probabilistic Frequency Weighting"]
        }

    def _generate_everyday_negation(self, register: str) -> Dict[str, Any]:
        """Scenario 8: Multi-Register Everyday Verb Negation Framework."""
        negation_templates = [
            "I don't care about the problem.",
            "We didn't agree with the manager.",
            "He doesn't know that my friend needs money.",
            "They don't understand our new system.",
            "I don't have money to buy food today.",
            "Don't worry about the job.",
            "We cannot stop the work now.",
            "They don't know that we don't have money at home."
        ]
        eng = self.rng.choice(negation_templates)
        res = self.switcher.code_switch_sentence(f"[GENERATE_{register.upper()}] {eng}")
        
        return {
            "scenario": "multi_register_everyday_negation",
            "english": eng,
            "kenyan_code_switch": res.kenyan_codeswitch,
            "rules": [f"Everyday Verb Negation ('{register}')", "Pillar I: Bare Root Constraint"]
        }

    def _generate_emphatic_pointing_scenario(self, register: str) -> Dict[str, Any]:
        """Scenario 9: Demonstrative Object Fronting & Pointing Concord with Object Infixes."""
        is_front = self.rng.choice([True, False])
        return generate_emphatic_training_pair(register=register, front=is_front, rng=self.rng)

    # ==========================================================================
    # FORMATTING & EXPORT WRAPPERS
    # ==========================================================================

    def format_sample(self, sample: Dict[str, Any], fmt: str = "llama3") -> Dict[str, Any]:
        """Formats the raw pair into specific LLM training templates with instruction control tokens."""
        src = sample["english"]
        tgt = sample["kenyan_code_switch"]
        reg = sample.get("register", "casual")
        ctrl_token = sample.get("control_token", f"[GENERATE_{reg.upper()}]")

        if fmt == "tagged":
            # Specialized bilingual token boundary with register tag
            formatted_text = f"<|style:{reg}|> <|src_en|> {ctrl_token} {src} </|src_en|> <|tgt_kcs|> {tgt} </|tgt_kcs|>"
            return {"text": formatted_text, "metadata": sample}

        elif fmt == "llama3":
            # Llama 3 / ChatML prompt template with instruction control token
            formatted_text = (
                f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
                f"{SYSTEM_INSTRUCTION}<|eot_id|>\n"
                f"<|start_header_id|>user<|end_header_id|>\n\n"
                f"Translate to authentic Kenyan Code-Switching:\n{ctrl_token} {src}<|eot_id|>\n"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
                f"{tgt}<|eot_id|>"
            )
            return {"text": formatted_text, "src": f"{ctrl_token} {src}", "tgt": tgt}

        elif fmt == "alpaca":
            return {
                "instruction": f"{SYSTEM_INSTRUCTION} Mode: {reg.upper()}.",
                "input": f"{ctrl_token} {src}",
                "output": tgt
            }

        else: # default json
            return {
                "english": src,
                "kenyan_code_switch": tgt,
                "register": reg,
                "control_token": ctrl_token,
                "scenario": sample["scenario"],
                "rules": sample["rules"]
            }

    def generate_batch(self, count: int = 1000, fmt: str = "llama3", register: str = "tech_standard") -> List[Dict[str, Any]]:
        """Generates a batch of synthetic pairs."""
        return [self.format_sample(self.generate_sample(register=register), fmt=fmt) for _ in range(count)]

    def export_dataset(self, output_path: Path, count: int = 5000, fmt: str = "llama3") -> Path:
        """Exports a batch to JSONL."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        batch = self.generate_batch(count=count, fmt=fmt)
        with open(output_path, "w", encoding="utf-8") as f:
            for item in batch:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        return output_path


if __name__ == "__main__":
    generator = SyntheticCodeSwitchGenerator(seed=42)
    print("--- 5 HIGH-VOLUME SYNTHETIC SAMPLES ---")
    for i in range(5):
        s = generator.generate_sample()
        print(f"[{i+1}] SCENARIO: {s['scenario']}")
        print(f"    SRC (EN): {s['english']}")
        print(f"    TGT (CS): {s['kenyan_code_switch']}")
        print()

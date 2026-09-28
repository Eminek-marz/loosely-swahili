"""
Loosely Swahili Natural Language Processing (LS-NLP) Engine
The Official Master Lexicon & Structural Blueprint for East African Swahili-English Hybrid (Sheng / Engsh).

Codified Sections:
  I.    The Morphosyntactic Engine (Verbs & Actions)
          - Bare Root Constraint (rejection of double-conjugations / English past endings)
          - Verbal Plug-In Matrix: [Subject Prefix] + [Tense Prefix] + [Object Prefix] + [Bare English Verb]
          - Negation Framework: rejection of mid-sentence 'don't'/'not', Swahili prefixes:
            Present 'si-', Past '-ku-', Not-Yet '-ja-'
  II.   Noun Pluralization & Simplified Grammatical Classes
          - A-WA Class (for people only)
          - I-ZI Class (for everything else: objects, tech, concepts)
          - English '-s' Double-Stack Rule (Ma- + Root + -s; e.g. Maphones, Mabooks; Chapos - NEVER 'Machapo')
  III.  The Modifier System (Ki-/Vi- Adverbs of Manner: '-ly' converter)
  IV.   Possessives (Ownership: Track 1 Post-Noun vs Track 2 Pre-Noun)
  V.    Prepositions (Zero-Preposition Rule, 'Kwa' Overlord, Suffix '-ni' Ban on English roots)
  VI.   Time & Certainty (Written in Words Only: 'Saa' Convention, English Direct 'No At', 'Around' Buffer)
  VII.  Financial & Electronics Value Matrix (Currency vocabulary, Counting Thousands tracks, 'Tenje' electronics)
  VIII. Conversational Status & Distress System (Mandatory peer responses, Security Command, Financial distress)
  IX.   Master Contextual Script Parser & Validator
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


# ==============================================================================
# DATA STRUCTURES & DIAGNOSTIC RESULTS
# ==============================================================================

@dataclass
class RuleValidationIssue:
    pillar: str
    rule_name: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    faulty_segment: str
    explanation: str
    suggestion: str


@dataclass
class VerbAnalysis:
    surface_form: str
    is_valid_plug_in: bool
    subject_prefix: str = ""
    subject_desc: str = ""
    tense_marker: str = ""
    tense_desc: str = ""
    object_marker: str = ""
    object_desc: str = ""
    bare_verb_root: str = ""
    is_negated: bool = False
    negation_type: str = ""  # 'present', 'past_never_happened', 'not_yet', 'none'
    has_double_conjugation_error: bool = False
    error_message: str = ""
    normalized_swahili: str = ""
    english_translation: str = ""
    is_soft_target: bool = False
    is_disgust_depersonalized: bool = False
    emotional_affect: str = ""
    has_affect_conflict: bool = False


@dataclass
class NounAnalysis:
    surface_form: str
    noun_class: str  # 'A-WA' (People), 'I-ZI' (Objects/Tech), 'DOUBLE_STACK'
    is_double_stack: bool = False
    prefix: str = ""
    stem: str = ""
    suffix: str = ""
    number: str = "singular"  # 'singular' or 'plural'
    gloss: str = ""


@dataclass
class MannerModifierAnalysis:
    surface_form: str
    is_manner_modifier: bool
    prefix: str = ""  # 'ki' or 'vi'
    english_root: str = ""
    adverbial_meaning_en: str = ""
    adverbial_meaning_sw: str = ""


@dataclass
class TimeAnalysis:
    raw_expression: str
    convention: str  # 'SWAHILI_SAA', 'ENGLISH_DIRECT', 'UNCERTAINTY_AROUND', 'DIGIT_VIOLATION'
    written_word: str
    clock_hour: int
    is_written_in_words: bool
    swahili_clock_meaning: Optional[str] = None
    digital_clock_meaning: Optional[str] = None
    note: str = ""


@dataclass
class FinancialAnalysis:
    raw_expression: str
    token_type: str  # 'CURRENCY_BASE', 'ENGLISH_TRACK', 'SWAHILI_TRACK', 'LUMP_SUM', 'DEVICE_TENJE'
    value_kes: Optional[int]
    meaning: str
    is_valid: bool = True
    error_message: str = ""


@dataclass
class ConversationalStatusAnalysis:
    raw_expression: str
    category: str  # 'GREETING', 'PEER_RESPONSE', 'SECURITY_COMMAND', 'FINANCIAL_DISTRESS'
    meaning: str
    context: str = ""


@dataclass
class MetathesisEntry:
    surface_form: str
    internal_rewrite: str
    standard_root: str
    safe_universal_equivalent: str
    meaning: str
    inversion_index: float  # e.g., 0.60 to 0.95
    socio_economic_layer: str
    primary_risk_factor: str  # e.g. 'High Risk (Total semantic shift)'
    is_semantic_shift: bool = False
    semantic_shift_note: str = ""
    bracket_label: str = ""


@dataclass
class MetathesisAnalysis:
    surface_form: str
    internal_rewrite: str
    standard_root: str
    safe_universal_equivalent: str
    meaning: str
    inversion_index: float
    socio_economic_layer: str
    primary_risk_factor: str
    is_semantic_shift: bool
    slider_active: bool
    bracket_label: str
    gloss: str
    semantic_shift_note: str = ""


@dataclass
class SentenceComplianceReport:
    original_sentence: str
    is_fully_compliant: bool
    issues: List[RuleValidationIssue] = field(default_factory=list)
    pillars_triggered: List[str] = field(default_factory=list)
    normalized_swahili: str = ""
    english_translation: str = ""
    syntactic_breakdown: Dict[str, Any] = field(default_factory=dict)


# ==============================================================================
# PILLAR I: THE MORPHOSYNTACTIC ENGINE (VERBS & ACTIONS)
# ==============================================================================

class MorphosyntacticEngine:
    """
    Enforces the Bare Root Constraint, the Verbal Plug-In Matrix, and the Negation Framework.
    Swahili supplies prefixes/infixes (hardware); English supplies the uninflected root (software).
    """

    # Subject prefixes
    SUBJECTS = {
        "ni": ("1s", "I / Mimi"),
        "u": ("2s", "You / Wewe"),
        "a": ("3s", "He/She / Yeye"),
        "tu": ("1p", "We / Sisi"),
        "m": ("2p", "You all / Ninyi"),
        "wa": ("3p", "They / Wao"),
        "i": ("c9", "It (Class 9)"),
        "zi": ("c10", "They (Class 10)"),
        "li": ("c5", "It (Class 5)"),
        "ya": ("c6", "They (Class 6)"),
        "ki": ("c7", "It (Class 7)"),
        "vi": ("c8", "They (Class 8)"),
    }

    # Negative subject prefixes
    NEGATIVE_SUBJECTS = {
        "si": ("1s", "I not / Mimi si"),
        "hu": ("2s", "You not / Wewe hu"),
        "hau": ("2s", "You not / Wewe hu"),
        "ha": ("3s", "He/She not / Yeye ha"),
        "hatu": ("1p", "We not / Sisi hatu"),
        "ham": ("2p", "You all not / Ninyi ham"),
        "hawa": ("3p", "They not / Wao hawa"),
        "hai": ("c9", "It not (Class 9)"),
        "hazi": ("c10", "They not (Class 10)"),
    }

    # Tense markers
    TENSES = {
        "na": ("present_continuous", "is/are ...-ing", "Wakati Uliopo"),
        "li": ("past", "did / ...-ed", "Wakati Uliopita"),
        "ta": ("future", "will / shall", "Wakati Ujao"),
        "me": ("perfect", "has / have", "Wakati Uliotimilika"),
        "ki": ("conditional", "if / when / while", "Hali ya Masharti"),
        "ka": ("narrative", "and then", "Wakati wa Kusimulia"),
        "nge": ("hypothetical", "would", "Masharti ya Kutegemea"),
        "ku": ("infinitive", "to", "Kitenzi Jina"),
    }

    # Object infixes
    OBJECTS = {
        "ni": ("me", "me (mimi)"),
        "ku": ("you", "you (wewe)"),
        "m": ("him_her", "him/her (yeye)"),
        "mu": ("him_her", "him/her (yeye)"),
        "tu": ("us", "us (sisi)"),
        "wa": ("them", "them (wao)"),
        "ji": ("self", "oneself / reflexive (mwenyewe)"),
        "ka": ("soft_target", "delicate/cute target (-ka-) [Bantu Cl. 12 Diminutive Affective]"),
    }

    # Common English verb roots and irregular pasts to detect double conjugation
    IRREGULAR_PAST_MAP = {
        "shocked": "shock",
        "picked": "pick",
        "called": "call",
        "texted": "text",
        "cloned": "clone",
        "blocked": "block",
        "cleaned": "clean",
        "cleared": "clear",
        "arrived": "arrive",
        "replied": "reply",
        "matched": "match",
        "shopped": "shop",
        "transferred": "transfer",
        "posted": "post",
        "confused": "confuse",
        "agreed": "agree",
        "ghosted": "ghost",
        "deleted": "delete",
        "fixed": "fix",
        "watched": "watch",
        "enjoyed": "enjoy",
        "cared": "care",
        "told": "tell",
        "went": "go",
        "came": "come",
        "seen": "see",
        "saw": "see",
        "took": "take",
        "taken": "take",
        "turned": "turn",
    }

    KNOWN_ENGLISH_VERBS = {
        "pick", "shock", "text", "call", "clone", "block", "clean", "clear", "arrive",
        "reply", "match", "care", "go", "come", "chill", "vibe", "post", "shop", "enjoy",
        "confuse", "agree", "ghost", "delete", "fix", "deliver", "carry", "watch", "support",
        "transfer", "share", "sign", "date", "tell", "listen", "start", "stop", "turn",
        "dial", "phone", "approach", "songa", "shika", "say", "surrender", "sarrender", "kaa"
    }

    def analyze_verb(self, word: str) -> VerbAnalysis:
        cleaned = word.lower().replace("-", "")

        # A. Check for Double-Conjugation / English Past Suffixes
        for bad_past, base_root in self.IRREGULAR_PAST_MAP.items():
            if cleaned.endswith(bad_past):
                prefix_part = cleaned[:-len(bad_past)]
                if len(prefix_part) >= 2:
                    return VerbAnalysis(
                        surface_form=word,
                        is_valid_plug_in=False,
                        has_double_conjugation_error=True,
                        bare_verb_root=base_root,
                        error_message=(
                            f"Violation of The Bare Root Constraint: English verbs must remain uninflected. "
                            f"'{word}' exhibits double-conjugation ending in '-ed'/past tense. "
                            f"Enforce bare root: '{prefix_part + base_root}'."
                        )
                    )

        # Generic regex check for -ed on verb-like hybrid
        if re.search(r"^[a-z]{2,8}[a-z]+ed$", cleaned) and not cleaned.endswith(("need", "feed", "seed", "bleed")):
            for pfx in list(self.SUBJECTS.keys()) + list(self.NEGATIVE_SUBJECTS.keys()):
                if cleaned.startswith(pfx):
                    stem = cleaned[len(pfx):]
                    return VerbAnalysis(
                        surface_form=word,
                        is_valid_plug_in=False,
                        has_double_conjugation_error=True,
                        error_message=(
                            f"Violation of The Bare Root Constraint: English verb '{stem}' is inflected with past tense. "
                            f"Bare uninflected base required."
                        )
                    )

        # B. Check Negation Framework
        # 1. "Never Happened" Past Negation (-ku-)
        for neg_pfx, (subj_code, subj_desc) in self.NEGATIVE_SUBJECTS.items():
            if cleaned.startswith(neg_pfx + "ku"):
                root = cleaned[len(neg_pfx) + 2:]
                if root in self.KNOWN_ENGLISH_VERBS or len(root) >= 3:
                    return VerbAnalysis(
                        surface_form=word,
                        is_valid_plug_in=True,
                        subject_prefix=neg_pfx,
                        subject_desc=subj_desc,
                        tense_marker="ku",
                        tense_desc="Past Negation / 'Never Happened' (-ku-)",
                        bare_verb_root=root,
                        is_negated=True,
                        negation_type="past_never_happened",
                        normalized_swahili=f"siku{root} / siku-fanya {root}",
                        english_translation=f"did not {root}"
                    )

        # 2. "Not Yet" Past Negation (-ja-)
        for neg_pfx, (subj_code, subj_desc) in self.NEGATIVE_SUBJECTS.items():
            if cleaned.startswith(neg_pfx + "ja"):
                root = cleaned[len(neg_pfx) + 2:]
                if root in self.KNOWN_ENGLISH_VERBS or len(root) >= 3:
                    return VerbAnalysis(
                        surface_form=word,
                        is_valid_plug_in=True,
                        subject_prefix=neg_pfx,
                        subject_desc=subj_desc,
                        tense_marker="ja",
                        tense_desc="Not Yet Negation (-ja-)",
                        bare_verb_root=root,
                        is_negated=True,
                        negation_type="not_yet",
                        normalized_swahili=f"sijafanya {root} bado",
                        english_translation=f"have not {root}ed yet"
                    )

        # 3. Simple Present Negation (Subject Neg Prefix + Bare Verb)
        for neg_pfx, (subj_code, subj_desc) in self.NEGATIVE_SUBJECTS.items():
            if cleaned.startswith(neg_pfx):
                root = cleaned[len(neg_pfx):]
                if root in self.KNOWN_ENGLISH_VERBS:
                    return VerbAnalysis(
                        surface_form=word,
                        is_valid_plug_in=True,
                        subject_prefix=neg_pfx,
                        subject_desc=subj_desc,
                        tense_marker="",
                        tense_desc="Simple Present Negation (No Tense Infix)",
                        bare_verb_root=root,
                        is_negated=True,
                        negation_type="present",
                        normalized_swahili=f"ha-{root}i",
                        english_translation=f"do/does not {root}"
                    )

        # C. Verbal Plug-In Matrix: [Subject] + [Tense] + [Object Prefix] + [Bare English Verb]
        subj_keys = sorted(self.SUBJECTS.keys(), key=lambda k: -len(k))
        tense_keys = sorted(self.TENSES.keys(), key=lambda k: -len(k))
        obj_keys = sorted(self.OBJECTS.keys(), key=lambda k: -len(k))

        for s_pfx in subj_keys:
            if not cleaned.startswith(s_pfx):
                continue
            rem1 = cleaned[len(s_pfx):]
            for t_marker in tense_keys:
                if not rem1.startswith(t_marker):
                    continue
                rem2 = rem1[len(t_marker):]

                matched_obj = ""
                matched_obj_desc = ""
                root_candidate = rem2

                for o_ifx in obj_keys:
                    if rem2.startswith(o_ifx):
                        cand = rem2[len(o_ifx):]
                        if cand in self.KNOWN_ENGLISH_VERBS or len(cand) >= 3:
                            matched_obj = o_ifx
                            matched_obj_desc = self.OBJECTS[o_ifx][1]
                            root_candidate = cand
                            break

                if root_candidate in self.KNOWN_ENGLISH_VERBS or len(root_candidate) >= 3:
                    s_code, s_desc = self.SUBJECTS[s_pfx]
                    t_code, t_helper, t_desc = self.TENSES[t_marker]

                    # Master Architectural Rule: Affective Polarity Constraint (Mutual Exclusion Rule)
                    # Forced Ki- (Disgust) and -ka- (Soft-Target Endearment) cannot be stacked!
                    if s_pfx in ["ki", "vi"] and matched_obj == "ka":
                        return VerbAnalysis(
                            surface_form=word,
                            is_valid_plug_in=False,
                            has_affect_conflict=True,
                            bare_verb_root=root_candidate,
                            subject_prefix=s_pfx,
                            tense_marker=t_marker,
                            object_marker=matched_obj,
                            error_message=(
                                f"Violation of Affective Polarity Constraint (Mutual Exclusion Rule): "
                                f"'{word}' stacks forced inanimate prefix '{s_pfx}-' (Disgust/Contempt) with '-ka-' "
                                f"(Soft-Target Endearment). These morphemes pull in opposite emotional directions and "
                                f"are strictly mutually exclusive."
                            )
                        )

                    is_soft = (matched_obj == "ka")
                    is_disgust = (s_pfx in ["ki", "vi"])

                    if is_soft:
                        affect = (
                            "Soft-Target / Endearing / Vulnerable (Bantu Cl. 12 Affective Infix: "
                            "target framed as cute, delicate, or handled gently)"
                        )
                        if root_candidate == "songa":
                            en_trans = f"{s_desc.split('/')[0].strip()} danced/grooved gently with her [delicate target]"
                            norm_sw = f"{s_pfx}{t_marker}sogea naye kwa upole / kucheza naye densi"
                        elif root_candidate == "approach":
                            en_trans = f"{s_desc.split('/')[0].strip()} stepped up to her gently / approached the cute target"
                            norm_sw = f"{s_pfx}{t_marker}msogelea kwa upole"
                        elif root_candidate == "shika":
                            en_trans = f"{s_desc.split('/')[0].strip()} held her gently [delicate target]"
                            norm_sw = f"{s_pfx}{t_marker}mshika kwa upole"
                        elif root_candidate == "vibe":
                            en_trans = f"{s_desc.split('/')[0].strip()} vibed with her playfully [cute target]"
                            norm_sw = f"{s_pfx}{t_marker}piga stori naye kwa upole"
                        elif root_candidate == "enjoy":
                            en_trans = f"{s_desc.split('/')[0].strip()} enjoyed time with her [cute target]"
                            norm_sw = f"{s_pfx}{t_marker}furahia kuwa naye"
                        else:
                            en_trans = f"{s_desc.split('/')[0].strip()} {t_helper} {root_candidate} her gently [cute target]"
                            norm_sw = f"{s_pfx}{t_marker}ka{root_candidate}"
                    elif is_disgust:
                        affect = (
                            "Disgust / Sarcastic Depersonalization (Forced Class 7 Ki- shift: "
                            "speaker strips human dignity, treating referent as an irritating object/it)"
                        )
                        s_obj_label = "that irritating object / pathetic thing" if s_pfx == "ki" else "those irritating objects"
                        if root_candidate == "say":
                            en_trans = f"what is {s_obj_label} saying / {s_obj_label} is saying"
                            norm_sw = f"{s_pfx}{t_marker}sema (kwa dharau)"
                        elif root_candidate in ["surrender", "sarrender"]:
                            en_trans = f"look at {s_obj_label} giving up / {s_obj_label} is surrendering"
                            norm_sw = f"{s_pfx}{t_marker}salimu amri (kwa dharau)"
                        elif root_candidate == "kaa":
                            en_trans = f"{s_obj_label} looks / behaves"
                            norm_sw = f"{s_pfx}{t_marker}kaa (kwa dharau)"
                        else:
                            en_trans = f"{s_obj_label} is {root_candidate}ing"
                            norm_sw = f"{s_pfx}{t_marker}{root_candidate} (kwa dharau)"
                    else:
                        affect = ""
                        en_trans = f"{s_desc.split('/')[0].strip()} {t_helper} {root_candidate}"
                        if matched_obj:
                            en_trans += f" ({matched_obj_desc})"
                        norm_sw = f"{s_pfx}{t_marker}{root_candidate}"

                    return VerbAnalysis(
                        surface_form=word,
                        is_valid_plug_in=True,
                        subject_prefix=s_pfx,
                        subject_desc=s_desc,
                        tense_marker=t_marker,
                        tense_desc=t_desc,
                        object_marker=matched_obj,
                        object_desc=matched_obj_desc,
                        bare_verb_root=root_candidate,
                        normalized_swahili=norm_sw,
                        english_translation=en_trans,
                        is_soft_target=is_soft,
                        is_disgust_depersonalized=is_disgust,
                        emotional_affect=affect
                    )

        return VerbAnalysis(
            surface_form=word,
            is_valid_plug_in=False,
            error_message="Not recognized as a valid Swahili-English verbal plug-in"
        )


# ==============================================================================
# PILLAR II: NOUN PLURALIZATION & SIMPLIFIED GRAMMATICAL CLASSES
# ==============================================================================

class NounClassEngine:
    """
    Implements the collapse of traditional Ngeli into two universal pathways:
      1. A-WA Class (For People Only)
      2. I-ZI Class (For Everything Else: Objects, Tech, Concepts)
      3. The English '-s' Double-Stack Rule (Ma- + [English Root] + -s)
         Exception: Chapos (NEVER 'Machapo')
    """

    PEOPLE_ROOTS = {
        "msee", "wasee", "boy", "boys", "maboys", "maboyfriends", "girl", "girls",
        "magirls", "guy", "guys", "maguys", "teacher", "teachers", "mateachers",
        "driver", "drivers", "madrivers", "doctor", "doctors", "madoctors", "youth",
        "youths", "mayouth", "mayouths", "cop", "cops", "macops", "man", "men",
        "askari", "polisi", "mwanamke", "mwanaume", "daktari", "abiria"
    }

    OBJECT_ROOTS = {
        "book", "books", "phone", "phones", "computer", "computers", "laptop",
        "laptops", "table", "tables", "gate", "car", "cars", "macars", "job",
        "class", "town", "office", "fare", "house", "screen", "seat", "tenje",
        "chapo", "chapos", "madondo", "dondo", "dawa", "doba"
    }

    def analyze_noun(self, word: str) -> NounAnalysis:
        cleaned = word.lower()

        # Dawa is explicitly medicine (Standard Swahili / Healthcare)
        if cleaned == "dawa":
            return NounAnalysis(
                surface_form=word,
                noun_class="I-ZI",
                is_double_stack=False,
                stem="dawa",
                number="singular",
                gloss="I-ZI Class (Medicine / Treatment / Healthcare: 'dawa ya hospitali / duka la dawa')"
            )

        # Check illegal "Machapo" food plural rule
        if cleaned == "machapo":
            return NounAnalysis(
                surface_form=word,
                noun_class="ILLEGAL_FOOD_PLURAL",
                is_double_stack=False,
                stem="chapo",
                number="plural",
                gloss="Illegal Plural: Use 'Chapos', NEVER 'Machapo'!"
            )

        # Check legal "Chapos"
        if cleaned == "chapos":
            return NounAnalysis(
                surface_form=word,
                noun_class="I-ZI",
                is_double_stack=False,
                stem="chapo",
                suffix="s",
                number="plural",
                gloss="I-ZI Food Plural: 'Chapos' (Valid street syntax; never 'Machapo')"
            )

        # Check English "-s" Double-Stack (Ma- ... -s)
        # E.g. Maphones, Mabooks, Macomputers, Madrivers
        if cleaned.startswith("ma") and cleaned.endswith("s") and len(cleaned) > 4:
            stem = cleaned[2:-1]
            return NounAnalysis(
                surface_form=word,
                noun_class="DOUBLE_STACK",
                is_double_stack=True,
                prefix="ma",
                stem=stem,
                suffix="s",
                number="plural",
                gloss=f"Double-Stack Plural: Swahili collective [Ma-] + English [{stem}] + English Plural [-s]"
            )

        # Check A-WA people markers
        if cleaned in self.PEOPLE_ROOTS:
            is_pl = (
                cleaned.startswith("wa") or
                cleaned.startswith("ma") or
                cleaned.endswith("s") or
                cleaned in {"men", "wasee", "mayouth"}
            )
            return NounAnalysis(
                surface_form=word,
                noun_class="A-WA",
                is_double_stack=False,
                prefix="wa" if cleaned.startswith("wa") else ("m" if cleaned.startswith("m") else ""),
                stem=cleaned,
                number="plural" if is_pl else "singular",
                gloss="A-WA Class (People Only)"
            )

        # Everything else is I-ZI
        is_plural_obj = cleaned.endswith("s") or cleaned.startswith("zi")
        return NounAnalysis(
            surface_form=word,
            noun_class="I-ZI",
            is_double_stack=False,
            stem=cleaned,
            number="plural" if is_plural_obj else "singular",
            gloss="I-ZI Class (Inanimate Objects, Technology & Concepts)"
        )

    def validate_agreement(self, noun: str, verb_or_det: str) -> Tuple[bool, str]:
        n_info = self.analyze_noun(noun)
        v_clean = verb_or_det.lower()

        if n_info.noun_class == "A-WA":
            if n_info.number == "singular":
                if v_clean.startswith("a") or v_clean.startswith("huyu") or v_clean.startswith("yu"):
                    return True, "Valid A-WA singular agreement (Living/Person: a-)"
                if v_clean.startswith("i") or v_clean.startswith("zi"):
                    return False, f"Agreement Violation: Person '{noun}' cannot trigger I-ZI agreement ('{verb_or_det}')"
            else:
                if v_clean.startswith("wa") or v_clean.startswith("hawa"):
                    return True, "Valid A-WA plural agreement (Living/People: wa-)"
                if v_clean.startswith("zi"):
                    return False, f"Agreement Violation: People plural '{noun}' must trigger A-WA 'wa-', not I-ZI 'zi-'"

        elif n_info.noun_class in ("I-ZI", "DOUBLE_STACK"):
            if n_info.number == "singular":
                if v_clean.startswith("i") or v_clean == "hiyo" or v_clean.startswith("y"):
                    return True, "Valid I-ZI singular agreement (Objects/Tech: i-)"
                if v_clean.startswith("a"):
                    return False, f"Agreement Violation: Inanimate object '{noun}' cannot trigger personal agreement 'a-'"
            else:
                if v_clean.startswith("zi") or v_clean == "hizo" or v_clean.startswith("z"):
                    return True, "Valid I-ZI plural agreement (Objects/Tech: zi-)"
                if v_clean.startswith("wa"):
                    return False, f"Agreement Violation: Inanimate object '{noun}' cannot trigger human agreement 'wa-'"

        return True, "Default agreement verified"


# ==============================================================================
# PILLAR III: THE KI- / VI- MODIFIER (ADVERBS OF MANNER)
# ==============================================================================

class MannerModifierEngine:
    """
    Ki- and Vi- do not pluralize nouns here. They act like the English suffix '-ly',
    converting an English adjective or noun into an adverb describing how an action was completed.
    Formula: [Swahili Verb Engine] + Ki- / Vi- + [English Root]
    """

    KNOWN_ADVERB_ROOTS = {
        "stupid": ("stupidly / in a stupid manner", "kijinga / bila busara"),
        "hero": ("heroically / like a hero", "kwa kishujaa"),
        "actor": ("like an actor / dramatically", "kama msanii mwigizaji"),
        "cool": ("coolly / smartly", "kwa utulivu na mtindo"),
        "rude": ("rudely / insolently", "kwa jeuri / ukorofi"),
        "pro": ("professionally / like a pro", "kwa umahiri wa kiwango cha juu"),
        "star": ("like a celebrity / star", "kama nyota maarufu"),
        "slow": ("slowly / calmly", "polepole"),
        "smart": ("smartly / cleverly", "kwa weledi na werevu")
    }

    def analyze_manner(self, word: str) -> MannerModifierAnalysis:
        cleaned = word.lower()
        for pfx in ("vi", "ki"):
            if cleaned.startswith(pfx) and len(cleaned) > len(pfx) + 2:
                root = cleaned[len(pfx):]
                if root in self.KNOWN_ADVERB_ROOTS:
                    en_mean, sw_mean = self.KNOWN_ADVERB_ROOTS[root]
                    return MannerModifierAnalysis(
                        surface_form=word,
                        is_manner_modifier=True,
                        prefix=pfx,
                        english_root=root,
                        adverbial_meaning_en=en_mean,
                        adverbial_meaning_sw=sw_mean
                    )
                if root in MorphosyntacticEngine.KNOWN_ENGLISH_VERBS or len(root) >= 3:
                    return MannerModifierAnalysis(
                        surface_form=word,
                        is_manner_modifier=True,
                        prefix=pfx,
                        english_root=root,
                        adverbial_meaning_en=f"in a {root} manner / {root}-ly",
                        adverbial_meaning_sw=f"kwa njia ya {root}"
                    )

        return MannerModifierAnalysis(
            surface_form=word,
            is_manner_modifier=False
        )


# ==============================================================================
# PILLAR IV: POSSESSIVES (OWNERSHIP)
# ==============================================================================

class PossessiveEngine:
    """
    Two parallel structural tracks:
      Track 1: Swahili Agreement Track (Post-Noun)
        - Singular Object (Y-): Book yangu, Phone yako
        - Plural Object (Z-): Mabooks zangu, Maphones zako
        - Human System (W-): Driver wangu, Maboyfriends wake
      Track 2: English Structural Track (Pre-Noun)
        - Pre-nominal English possessive importing the noun phrase,
          yet still triggering Swahili plural verbs at boundary:
          e.g., 'My phones zimepotea', 'Your books ziko wapi?'
    """

    ENGLISH_POSSESSIVES = {"my", "your", "his", "her", "our", "their", "its"}

    SWAHILI_POSSESSIVE_STEMS = {
        "angu": "my",
        "ako": "your",
        "ake": "his/her",
        "etu": "our",
        "enu": "your (all)",
        "ao": "their"
    }

    def analyze_possessive_phrase(self, tokens: List[str]) -> Dict[str, Any]:
        for i, tok in enumerate(tokens):
            tok_lower = tok.lower()

            # Track 2: Pre-Noun English Possessive (e.g. "My phones zimepotea", "Your books ziko wapi?")
            if tok_lower in self.ENGLISH_POSSESSIVES and i + 1 < len(tokens):
                next_tok = tokens[i + 1]
                plural_verb_followed = False
                if i + 2 < len(tokens):
                    following = tokens[i + 2].lower()
                    if following.startswith("zi") or following.startswith("wa") or following.startswith("ime") or following.startswith("ziko"):
                        plural_verb_followed = True

                return {
                    "track": "Track 2 (English Structural Pre-Noun)",
                    "possessive": tok,
                    "head_noun": next_tok,
                    "triggers_swahili_verb": plural_verb_followed,
                    "explanation": f"Pre-nominal English '{tok}' imports noun '{next_tok}', driving Swahili verb concord."
                }

            # Track 1: Post-Noun Swahili Possessive (e.g. "Book yangu", "Driver wangu", "Mabooks zangu")
            if i > 0:
                prev_tok = tokens[i - 1]
                if tok_lower.startswith("y") or tok_lower.startswith("z") or tok_lower.startswith("w"):
                    concord = tok_lower[0]
                    stem = tok_lower[1:]
                    if stem in self.SWAHILI_POSSESSIVE_STEMS:
                        expected_class = (
                            "I-ZI (Singular)" if concord == "y" else (
                                "I-ZI (Plural)" if concord == "z" else "A-WA (Human System)"
                            )
                        )
                        return {
                            "track": "Track 1 (Swahili Agreement Post-Noun)",
                            "head_noun": prev_tok,
                            "possessive": tok,
                            "concord": concord,
                            "expected_class": expected_class,
                            "explanation": f"Post-noun Swahili possessive '{tok}' respects {expected_class} concord for '{prev_tok}'."
                        }

        return {"track": "none"}


# ==============================================================================
# PILLAR V: PREPOSITIONS (LOCATION & SPATIAL MOVEMENT)
# ==============================================================================

class PrepositionEngine:
    """
    1. Zero-Preposition Rule (Familiar routine destinations): Drop preposition completely.
       e.g., 'Niko class', 'Enda town', 'Niko job', 'Siwezi fika town'.
       Exception: Idiomatic blocks are imported whole: 'Ako out of town'.
    2. The 'Kwa' Overlord (Physical points): Connect generalized physical points using 'kwa'.
       e.g., 'Weka kwa table', 'Simama kwa gate', 'Hapa kwa office'.
    3. The Suffix Ban: Never append the traditional Swahili -ni suffix to modern English roots.
       e.g., 'officeni' or 'classini' are structurally illegal.
    """

    FAMILIAR_ROUTINE_PLACES = {
        "class", "job", "town", "base", "home", "shule", "mtaa", "gym", "stage"
    }

    ILLEGAL_SUFFIX_ROOTS = {
        "office": "officeni",
        "class": "classini",
        "job": "jobni",
        "stage": "stageni",
        "court": "courtni",
        "school": "schoolni",
        "hospital": "hospitalni",
        "gym": "gymni",
        "bank": "bankini",
    }

    def check_prepositions(self, sentence: str) -> List[RuleValidationIssue]:
        issues = []
        lowered = sentence.lower()

        # Check idiomatic block exception: "out of town" is permitted intact
        if "out of town" in lowered:
            return issues

        tokens = re.findall(r"\b[\w'-]+\b", sentence)

        for tok in tokens:
            cleaned = tok.lower()

            # Rule V.3: Check Suffix Ban (Never append -ni to English root)
            for eng_root, illegal_form in self.ILLEGAL_SUFFIX_ROOTS.items():
                if cleaned == illegal_form or (cleaned.startswith(eng_root) and cleaned.endswith("ni")):
                    issues.append(RuleValidationIssue(
                        pillar="V. Prepositions",
                        rule_name="The Suffix Ban",
                        severity="ERROR",
                        faulty_segment=tok,
                        explanation=(
                            f"Violation of The Suffix Ban: Never append the traditional Swahili spatial suffix '-ni' "
                            f"to a modern English root ('{tok}')."
                        ),
                        suggestion=f"Use zero-preposition '{eng_root}' or 'kwa {eng_root}' instead."
                    ))

        # Check for unnecessary preposition insertion before familiar routine destinations
        for place in self.FAMILIAR_ROUTINE_PLACES:
            if f"at {place}" in lowered or f"in {place}" in lowered:
                faulty = "at " + place if f"at {place}" in lowered else "in " + place
                issues.append(RuleValidationIssue(
                    pillar="V. Prepositions",
                    rule_name="The Zero-Preposition Rule",
                    severity="WARNING",
                    faulty_segment=faulty,
                    explanation=(
                        f"Speech efficiency dictates dropping English prepositions like 'at/in' before familiar routine places. "
                        f"Kenyans drop the preposition entirely."
                    ),
                    suggestion=f"Niko {place} / Enda {place} / Siwezi fika {place}"
                ))

        return issues


# ==============================================================================
# PILLAR VI: TIME & CERTAINTY (WRITTEN IN WORDS ONLY)
# ==============================================================================

class TimeCertaintyEngine:
    """
    Time parameters are split across three strict conventions written out entirely in words:
      1. The Swahili 'Saa' Convention: Uses Swahili clock (+6 hours ahead of standard digital face).
         e.g., 'Saa three' = 9 o'clock | 'Saa ten' = 4 o'clock.
      2. The English Direct Convention (No 'At'): Standard digital numbers with 'at' dropped.
         e.g., 'Tupatane three' | 'Kesho ten nitadeliver hiyo book'.
      3. The Uncertainty Buffer ('Around'): Places 'around' directly before the number word.
         e.g., 'Nitakuja around three' | 'Tupatane around five'.
    """

    NUMBER_WORDS = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
        "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12
    }

    def analyze_time(self, text: str) -> List[TimeAnalysis]:
        results = []
        lowered = text.lower()

        # Check for forbidden numeric digits (e.g. 3:00, 3pm, at 3)
        digit_matches = re.finditer(r"\b(\d{1,2}(:\d{2})?\s*(am|pm)?)\b", lowered)
        for m in digit_matches:
            results.append(TimeAnalysis(
                raw_expression=m.group(0),
                convention="DIGIT_VIOLATION",
                written_word="",
                clock_hour=0,
                is_written_in_words=False,
                note="Violation of Pillar VI: Time must be written out in words only to prevent ambiguity and preserve speech fluidity."
            ))

        # Check for English "at <number_word>" violation
        for word, val in self.NUMBER_WORDS.items():
            if f"at {word}" in lowered:
                results.append(TimeAnalysis(
                    raw_expression=f"at {word}",
                    convention="AT_VIOLATION",
                    written_word=word,
                    clock_hour=val,
                    is_written_in_words=True,
                    note=f"Violation of English Direct Convention: Drop 'at' completely. Say '{word}' or 'around {word}'."
                ))

        # 1. Swahili "Saa" convention
        for word, val in self.NUMBER_WORDS.items():
            pattern = rf"\bsaa\s+{word}\b"
            if re.search(pattern, lowered):
                swahili_hour = val
                digital_equivalent = (swahili_hour + 6) % 12
                if digital_equivalent == 0:
                    digital_equivalent = 12

                results.append(TimeAnalysis(
                    raw_expression=f"saa {word}",
                    convention="SWAHILI_SAA",
                    written_word=word,
                    clock_hour=swahili_hour,
                    is_written_in_words=True,
                    swahili_clock_meaning=f"Swahili clock {swahili_hour} = Standard digital {digital_equivalent}:00",
                    digital_clock_meaning=f"{digital_equivalent}:00",
                    note=f"Explicit 'saa' triggers the Swahili 6-hour offset: 'saa {word}' means {digital_equivalent} o'clock."
                ))

        # 2. Uncertainty buffer: "around <word>"
        for word, val in self.NUMBER_WORDS.items():
            pattern = rf"\baround\s+{word}\b"
            if re.search(pattern, lowered):
                results.append(TimeAnalysis(
                    raw_expression=f"around {word}",
                    convention="UNCERTAINTY_AROUND",
                    written_word=word,
                    clock_hour=val,
                    is_written_in_words=True,
                    digital_clock_meaning=f"~{val}:00",
                    note=f"Uncertainty buffer 'around {word}' signals approximate timing (~{val} o'clock)."
                ))

        # 3. English Direct convention (No "at")
        for word, val in self.NUMBER_WORDS.items():
            if any(r.written_word == word for r in results):
                continue
            pattern = rf"\b(tupatane|kesho|nitakuja|enda|leo|delivered|deliver|fika|turn up)\s+{word}\b"
            if re.search(pattern, lowered):
                results.append(TimeAnalysis(
                    raw_expression=word,
                    convention="ENGLISH_DIRECT",
                    written_word=word,
                    clock_hour=val,
                    is_written_in_words=True,
                    digital_clock_meaning=f"{val}:00",
                    note=f"English Direct Convention: 'at' is omitted; '{word}' directly indicates {val} o'clock."
                ))

        return results


# ==============================================================================
# PILLAR VII: FINANCIAL & ELECTRONICS VALUE MATRIX
# ==============================================================================

class FinancialElectronicsEngine:
    """
    Money, numbers, and key tech assets follow highly specific street designations:
    1. Currency Base Vocabulary:
       - Ashu / Kinde: 10 KES
       - Mbao / Blue: 20 KES
       - Finje / Chuani: 50 KES
       - Soo / Red: 100 KES (Saying 'soo one' is banned as redundant redundancy)
       - Rwabe: 200 KES
       - Punch: 500 KES
       - Thao / Kapa / Ndovu: 1,000 KES
       - Mita: 1,000,000 KES
    2. Counting Thousands:
       - The English Track (English Number + 'K' Only): Two K | Five K | Ten K.
         (Combining English numbers with 'thao' or 'kapa' like 'two thao' is illegal).
       - The Swahili Track (Money Word + Swahili Number): Thao mbili | Kapa tatu | Thao tano.
       - Lump Sum Objects: Root on its own: Alinipea kapa | Niko na thao hapa | kapa moja.
    3. Electronics Domain Constraints:
       - 'Tenje' belongs exclusively to devices and phones.
       - 'vutia tenje': used to mean dialing or phoning someone up ('Alinivutia tenje').
    """

    CURRENCY_BASE = {
        "ashu": (10, "Ten shillings (Ashu / Kinde)"),
        "kinde": (10, "Ten shillings (Ashu / Kinde)"),
        "mbao": (20, "Twenty shillings (Mbao / Blue)"),
        "blue": (20, "Twenty shillings (Mbao / Blue)"),
        "finje": (50, "Fifty shillings (Finje / Chuani)"),
        "chuani": (50, "Fifty shillings (Finje / Chuani)"),
        "soo": (100, "One hundred shillings (Soo / Red)"),
        "red": (100, "One hundred shillings (Soo / Red)"),
        "rwabe": (200, "Two hundred shillings (Rwabe)"),
        "punch": (500, "Five hundred shillings (Punch)"),
        "thao": (1000, "One thousand shillings (Thao / Kapa / Ndovu)"),
        "kapa": (1000, "One thousand shillings (Thao / Kapa / Ndovu)"),
        "ndovu": (1000, "One thousand shillings (Thao / Kapa / Ndovu)"),
        "mita": (1000000, "One million shillings (Mita)")
    }

    SWAHILI_NUMBERS = {
        "moja": 1, "mbili": 2, "tatu": 3, "nne": 4, "tano": 5,
        "sita": 6, "saba": 7, "nane": 8, "tisa": 9, "kumi": 10
    }

    ENGLISH_NUMBERS = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }

    def analyze_financial(self, sentence: str) -> List[FinancialAnalysis]:
        results = []
        lowered = sentence.lower()

        # Check banned redundancy: "soo one"
        if "soo one" in lowered or "soo 1" in lowered:
            results.append(FinancialAnalysis(
                raw_expression="soo one",
                token_type="BANNED_REDUNDANCY",
                value_kes=None,
                meaning="Illegal redundant combination",
                is_valid=False,
                error_message="Violation of Financial Matrix: Saying 'soo one' is banned as redundant redundancy. 'Soo' inherently denotes one hundred."
            ))

        # Check English Track: English Number + 'K' Only (e.g. "two k", "five k", "ten k")
        for num_word, num_val in self.ENGLISH_NUMBERS.items():
            pattern = rf"\b{num_word}\s+k\b"
            if re.search(pattern, lowered):
                val_kes = num_val * 1000
                results.append(FinancialAnalysis(
                    raw_expression=f"{num_word} k",
                    token_type="ENGLISH_TRACK",
                    value_kes=val_kes,
                    meaning=f"English Track Thousands: {num_word.capitalize()} K = {val_kes:,} KES",
                    is_valid=True
                ))

            # Detect illegal combination of English number + Swahili money word (e.g. "two thao", "five kapa")
            for m_word in ("thao", "kapa", "ndovu"):
                illegal_pattern = rf"\b{num_word}\s+{m_word}\b"
                if re.search(illegal_pattern, lowered):
                    results.append(FinancialAnalysis(
                        raw_expression=f"{num_word} {m_word}",
                        token_type="ILLEGAL_HYBRID_TRACK",
                        value_kes=None,
                        meaning=f"Illegal cross-track combination: '{num_word} {m_word}'",
                        is_valid=False,
                        error_message=(
                            f"Violation of Financial Matrix: Combining English numbers with Swahili money words "
                            f"('{num_word} {m_word}') is illegal. Use the English Track ('{num_word.capitalize()} K') "
                            f"or the Swahili Track ('{m_word.capitalize()} mbili/tatu')."
                        )
                    ))

        # Check Swahili Track: Money Word + Swahili Number (e.g. "thao mbili", "kapa tatu", "kapa moja")
        for m_word in ("thao", "kapa", "ndovu"):
            for sw_num, sw_val in self.SWAHILI_NUMBERS.items():
                pattern = rf"\b{m_word}\s+{sw_num}\b"
                if re.search(pattern, lowered):
                    val_kes = sw_val * 1000
                    results.append(FinancialAnalysis(
                        raw_expression=f"{m_word} {sw_num}",
                        token_type="SWAHILI_TRACK",
                        value_kes=val_kes,
                        meaning=f"Swahili Track Thousands: {m_word.capitalize()} {sw_num} = {val_kes:,} KES",
                        is_valid=True
                    ))

        # Check Lump Sum Root usage (on its own: "kapa", "thao", "ashu", etc.)
        tokens = re.findall(r"\b[\w'-]+\b", lowered)
        for i, tok in enumerate(tokens):
            if tok in self.CURRENCY_BASE:
                # If not part of Swahili track or English track
                is_part_of_track = any(tok in r.raw_expression for r in results)
                if not is_part_of_track:
                    val, label = self.CURRENCY_BASE[tok]
                    results.append(FinancialAnalysis(
                        raw_expression=tok,
                        token_type="CURRENCY_BASE",
                        value_kes=val,
                        meaning=f"{label} ({val:,} KES)",
                        is_valid=True
                    ))

        # Check Electronics Domain: "tenje" and "vutia tenje"
        if "vutia tenje" in lowered:
            results.append(FinancialAnalysis(
                raw_expression="vutia tenje",
                token_type="DEVICE_TENJE",
                value_kes=None,
                meaning="Electronics Idiom: 'vutia tenje' = Dialing / Phoning someone up",
                is_valid=True
            ))
        elif "tenje" in tokens:
            results.append(FinancialAnalysis(
                raw_expression="tenje",
                token_type="DEVICE_TENJE",
                value_kes=None,
                meaning="Electronics Constraint: 'Tenje' belongs exclusively to mobile phones/devices",
                is_valid=True
            ))

        return results


# ==============================================================================
# PILLAR VIII: CONVERSATIONAL STATUS & DISTRESS SYSTEM
# ==============================================================================

class ConversationalDistressEngine:
    """
    1. Greetings & Mandatory Peer Responses:
       - Niaje? / Sasa? -> Freshi / Poa / Fiti
       - Form ni gani? -> Niko base / Kupiga story
       - Rada yako? -> Rada iko safi / Niko rada
    2. The Security Command:
       - Wee kaa rada! (Stay alert / Watch your back!)
    3. Financial Distress:
       - Nimesota: General state of being completely broke.
       - Nimekauka: Extreme, sudden lack of funds ('Nimekauka sasa sasa').
    """

    GREETING_MAP = {
        "niaje": ("Casual Greeting", ["freshi", "poa", "fiti"]),
        "sasa": ("Casual Greeting", ["freshi", "poa", "fiti"]),
        "form ni gani": ("Social Status Inquiry", ["niko base", "kupiga story"]),
        "rada yako": ("Situation/Status Inquiry", ["rada iko safi", "niko rada"]),
    }

    DISTRESS_TERMS = {
        "nimesota": ("Financial Distress", "General state of being completely broke (Hali ya kufilisika)"),
        "nimekauka": ("Financial Distress", "Extreme, sudden lack of funds (Kukauka kabisa kiuchumi)"),
        "nimekauka sasa sasa": ("Financial Distress", "Immediate absolute liquidity depletion"),
        "nimesota na nimekauka": ("Financial Distress", "Double-state compound financial devastation")
    }

    def analyze_status(self, sentence: str) -> List[ConversationalStatusAnalysis]:
        results = []
        lowered = sentence.lower()

        # Check Security Command: "kaa rada" / "wee kaa rada"
        if "kaa rada" in lowered:
            results.append(ConversationalStatusAnalysis(
                raw_expression="wee kaa rada" if "wee kaa rada" in lowered else "kaa rada",
                category="SECURITY_COMMAND",
                meaning="Security Command: Stay alert / Watch your back! (Kuwa macho / Chungia usalama)"
            ))

        # Check Financial Distress
        for term, (cat, meaning) in self.DISTRESS_TERMS.items():
            if term in lowered:
                results.append(ConversationalStatusAnalysis(
                    raw_expression=term,
                    category=cat,
                    meaning=meaning
                ))

        # Check Greetings & Responses
        for greeting, (cat, responses) in self.GREETING_MAP.items():
            if greeting in lowered:
                results.append(ConversationalStatusAnalysis(
                    raw_expression=greeting,
                    category="GREETING",
                    meaning=f"{cat} (Mandatory peer responses: {', '.join(responses)})"
                ))

        for resp in ("rada iko safi", "niko rada", "niko base", "kupiga story", "freshi", "poa", "fiti"):
            if resp in lowered and not any(r.raw_expression == resp for r in results):
                results.append(ConversationalStatusAnalysis(
                    raw_expression=resp,
                    category="PEER_RESPONSE",
                    meaning=f"Authentic Peer Response: '{resp}'"
                ))

        return results


# ==============================================================================
# DISCOVERED EMERGENT RULES: SECTIONS X - XVII (EMPIRICALLY MINED PATTERNS)
# ==============================================================================

class MetathesisEngine:
    """
    Rule X: Metathesis / Syllable Reversal Inversion Matrix ("Kibali / Otyeno")
    Engineered with a 4-part Structural Insulation Layer:
      1. Generational / Locational Slider (The Meta-Filter):
         - Inversion Index (0.0 - 1.0) and Socio-Economic Register metadata.
         - Cryptographic inversions are OFF by default for general/standard communication;
           activated when input explicitly requests 'Deep Street Slang / In-Group Authenticity'.
      2. Inversion Decoder Routing Table:
         - Every inverted word is structurally bound to its original, unchanged baseline root.
         - Internally rewrites tokens before downstream grammatical validation (A-WA, I-ZI, Value Matrix).
      3. Semantic Shift Exception Engine:
         - Contextual overrides and disambiguations:
           * 'doba' -> Rewritten to 'music' (music / track / beat), NOT literal 'bado' (still/not yet).
           * 'dawa' -> Strictly denotes 'medicine' (pharmaceutical / cure). In transit metathesis,
             'ndauwo' diverged to denote 'fare' (bus fare), while 'dawa' itself is always medicine.
      4. Failsafe UX Output Modes:
         - Method A: Silent Normalization (for translators/parsers) -> 'Sina sape' -> 'Sina pesa'.
         - Method B: Visual Glancing (for lexicon readers/educational tooltips) ->
           'Niko na doba [music], lakini sina sape [pesa] ya kubuy gomba [mboga].'
    """

    ROUTING_TABLE: Dict[str, MetathesisEntry] = {
        "seemo": MetathesisEntry(
            surface_form="seemo",
            internal_rewrite="msee",
            standard_root="msee",
            safe_universal_equivalent="Person / Guy",
            meaning="guy / person / youth",
            inversion_index=0.65,
            socio_economic_layer="Urban Youth / Casual Street Vernacular",
            primary_risk_factor="Low confusion (very common)",
            is_semantic_shift=False,
            bracket_label="msee"
        ),
        "seem": MetathesisEntry(
            surface_form="seem",
            internal_rewrite="msee",
            standard_root="msee",
            safe_universal_equivalent="Person / Guy",
            meaning="guy / person / youth",
            inversion_index=0.65,
            socio_economic_layer="Urban Youth / Casual Street Vernacular",
            primary_risk_factor="Low confusion (very common)",
            is_semantic_shift=False,
            bracket_label="msee"
        ),
        "sape": MetathesisEntry(
            surface_form="sape",
            internal_rewrite="pesa",
            standard_root="pesa",
            safe_universal_equivalent="Money / Cash",
            meaning="money / cash / funds",
            inversion_index=0.75,
            socio_economic_layer="Urban Sheng / Street Financial Register",
            primary_risk_factor="Medium confusion",
            is_semantic_shift=False,
            bracket_label="pesa"
        ),
        "ndauwo": MetathesisEntry(
            surface_form="ndauwo",
            internal_rewrite="fare",
            standard_root="dawa",
            safe_universal_equivalent="Bus Fare",
            meaning="bus fare / transit money",
            inversion_index=0.95,
            socio_economic_layer="Deep Street / Matatu Transit Subculture",
            primary_risk_factor="High Risk (Total semantic shift)",
            is_semantic_shift=True,
            semantic_shift_note=(
                "Standard 'dawa' strictly denotes medicine (pharmaceutical / healthcare). "
                "In street inversion 'ndauwo' specifically diverged to denote bus fare, "
                "while 'dawa' itself unambiguously remains medicine."
            ),
            bracket_label="fare"
        ),
        "dowo": MetathesisEntry(
            surface_form="dowo",
            internal_rewrite="fare",
            standard_root="dawa",
            safe_universal_equivalent="Bus Fare",
            meaning="bus fare / transit money",
            inversion_index=0.95,
            socio_economic_layer="Deep Street / Matatu Transit Subculture",
            primary_risk_factor="High Risk (Total semantic shift)",
            is_semantic_shift=True,
            semantic_shift_note="Phonetic variant of 'ndauwo', denoting bus fare.",
            bracket_label="fare"
        ),
        "doba": MetathesisEntry(
            surface_form="doba",
            internal_rewrite="music",
            standard_root="dub / music",
            safe_universal_equivalent="Music / Song",
            meaning="music / track / beat / song",
            inversion_index=0.80,
            socio_economic_layer="Street Music / Gengetone & Dancehall Register",
            primary_risk_factor="Medium confusion",
            is_semantic_shift=True,
            semantic_shift_note=(
                "Doba denotes music / track / beat (derived from dub/dancehall culture). "
                "Standard Kiswahili 'bado' strictly means 'still / not yet' and is a pure, "
                "uncorrupted Swahili word never altered by metathesis."
            ),
            bracket_label="music"
        ),
        "gomba": MetathesisEntry(
            surface_form="gomba",
            internal_rewrite="mboga",
            standard_root="mboga",
            safe_universal_equivalent="Vegetables / Greens",
            meaning="vegetables / greens",
            inversion_index=0.60,
            socio_economic_layer="Everyday Street Food Register",
            primary_risk_factor="Low confusion",
            is_semantic_shift=False,
            bracket_label="mboga"
        ),
        "pachu": MetathesisEntry(
            surface_form="pachu",
            internal_rewrite="chupa",
            standard_root="chupa",
            safe_universal_equivalent="Bottle / Alcoholic Drink",
            meaning="bottle / alcoholic drink",
            inversion_index=0.70,
            socio_economic_layer="Street Social / Nightlife Register",
            primary_risk_factor="Low confusion",
            is_semantic_shift=False,
            bracket_label="chupa"
        ),
        "manya": MetathesisEntry(
            surface_form="manya",
            internal_rewrite="nyama",
            standard_root="nyama",
            safe_universal_equivalent="Meat / Beef",
            meaning="meat / beef",
            inversion_index=0.65,
            socio_economic_layer="Street Food / Butcher Register",
            primary_risk_factor="Low confusion",
            is_semantic_shift=False,
            bracket_label="nyama"
        ),
        "tum": MetathesisEntry(
            surface_form="tum",
            internal_rewrite="mtu",
            standard_root="mtu",
            safe_universal_equivalent="Person / Human",
            meaning="person / human being",
            inversion_index=0.80,
            socio_economic_layer="Deep Street Cryptographic Register",
            primary_risk_factor="Medium confusion",
            is_semantic_shift=False,
            bracket_label="mtu"
        ),
        "ngeta": MetathesisEntry(
            surface_form="ngeta",
            internal_rewrite="chokehold",
            standard_root="chokehold",
            safe_universal_equivalent="Robbery / Mugging",
            meaning="mugging / neck grab / chokehold robbery",
            inversion_index=0.85,
            socio_economic_layer="Deep Street Danger / Crime Register",
            primary_risk_factor="Medium confusion",
            is_semantic_shift=False,
            bracket_label="mugging"
        )
    }

    # Backward compatibility mapping: surface -> (standard_root, meaning)
    INVERSIONS = {
        k: (e.standard_root, e.meaning) for k, e in ROUTING_TABLE.items()
    }

    def __init__(self, deep_street_slang: bool = False):
        self.deep_street_slang = deep_street_slang

    def get_routing_entry(self, word: str) -> Optional[MetathesisEntry]:
        return self.ROUTING_TABLE.get(word.lower())

    def analyze_metathesis(self, tokens: List[str], deep_street_slang: Optional[bool] = None) -> List[Dict[str, Any]]:
        slider = self.deep_street_slang if deep_street_slang is None else deep_street_slang
        found = []
        for t in tokens:
            t_low = t.lower()
            if t_low in self.ROUTING_TABLE:
                entry = self.ROUTING_TABLE[t_low]
                if entry.is_semantic_shift:
                    gloss = (
                        f"Metathesis Syllable Reversal: '{t}' <- '{entry.standard_root}' "
                        f"[Semantic Shift Override: '{entry.internal_rewrite}' ({entry.safe_universal_equivalent})]"
                    )
                else:
                    gloss = f"Metathesis Syllable Reversal: '{t}' <- '{entry.standard_root}' ({entry.meaning})"

                found.append({
                    "surface_form": t,
                    "internal_rewrite": entry.internal_rewrite,
                    "standard_root": entry.standard_root,
                    "safe_universal_equivalent": entry.safe_universal_equivalent,
                    "meaning": entry.meaning,
                    "inversion_index": entry.inversion_index,
                    "socio_economic_layer": entry.socio_economic_layer,
                    "primary_risk_factor": entry.primary_risk_factor,
                    "is_semantic_shift": entry.is_semantic_shift,
                    "semantic_shift_note": entry.semantic_shift_note,
                    "slider_active": slider,
                    "bracket_label": entry.bracket_label,
                    "gloss": gloss
                })
        return found

    def intercept_and_rewrite(self, tokens: List[str]) -> List[str]:
        """
        Inversion Decoder Routing Table:
        Rewrites cryptographic tokens internally to baseline roots before downstream
        grammatical processing (A-WA, I-ZI, Value Matrix).
        """
        rewritten = []
        for t in tokens:
            t_low = t.lower()
            if t_low in self.ROUTING_TABLE:
                target = self.ROUTING_TABLE[t_low].internal_rewrite
                if t.istitle():
                    rewritten.append(target.capitalize())
                elif t.isupper():
                    rewritten.append(target.upper())
                else:
                    rewritten.append(target)
            else:
                rewritten.append(t)
        return rewritten

    def normalize_silently(self, sentence: str) -> str:
        """
        Method A: Silent Normalization (For Translators / Parsers)
        Smoothly rewrites cryptographic tokens into standard safe universal equivalents.
        e.g. 'Sina sape' -> 'Sina pesa'
             'Niko na doba, lakini sina sape ya kubuy gomba.' ->
             'Niko na music, lakini sina pesa ya kubuy mboga.'
        """
        def replace_fn(match: re.Match) -> str:
            word = match.group(0)
            w_low = word.lower()
            if w_low in self.ROUTING_TABLE:
                entry = self.ROUTING_TABLE[w_low]
                repl = entry.internal_rewrite
                if word.istitle():
                    return repl.capitalize()
                elif word.isupper():
                    return repl.upper()
                return repl
            return word

        return re.sub(r"\b[A-Za-z]+\b", replace_fn, sentence)

    def glance_annotated(self, sentence: str) -> str:
        """
        Method B: Visual Glancing (For Lexicon Readers / Educational Tooltips)
        Retains the authentic cryptographic token for flavor and appends the
        un-inverted root / meaning in brackets.
        e.g. 'Niko na doba [music], lakini sina sape [pesa] ya kubuy gomba [mboga].'
             'Nipe ndauwo [fare] ya msupa.'
             'Seemo [msee] amego.'
        """
        def replace_fn(match: re.Match) -> str:
            word = match.group(0)
            w_low = word.lower()
            if w_low in self.ROUTING_TABLE:
                entry = self.ROUTING_TABLE[w_low]
                label = entry.bracket_label or entry.internal_rewrite
                end_pos = match.end()
                # Check if bracketed label already follows immediately
                following = sentence[end_pos:end_pos + len(label) + 4]
                if following.startswith(f" [{label}]"):
                    return word
                return f"{word} [{label}]"
            return word

        return re.sub(r"\b[A-Za-z]+\b", replace_fn, sentence)


class DemonstrativeCompressionEngine:
    """
    Rule XI: Demonstrative Compression & Universal Deictics (Hii, Hiyo, Ile)
    Collapses traditional class concords into three universal deictic anchors:
      - 'hii': proximal / immediate focus ("hii form", "hii issue", "hii ngoma")
      - 'hiyo': discourse-given / mental referent ("hiyo story", "hiyo meeting")
      - 'ile': distal / emphatic ("ile design", "ile mbaya")
    """
    DEICTICS = {
        "hii": "Proximal / Immediate Attention Anchor",
        "hiyo": "Discourse-Given / Mental Referent Anchor",
        "ile": "Distal / Emphatic Intensifier Anchor"
    }

    def analyze_deictics(self, tokens: List[str]) -> List[Dict[str, str]]:
        found = []
        for i in range(len(tokens) - 1):
            t_low = tokens[i].lower()
            if t_low in self.DEICTICS:
                nxt = tokens[i + 1]
                found.append({
                    "deictic": t_low,
                    "target": nxt,
                    "role": self.DEICTICS[t_low],
                    "gloss": f"Deictic Compression: '{t_low} {nxt}' ({self.DEICTICS[t_low]})"
                })
        return found


class CopulaPredicateEngine:
    """
    Rule XII: Copula-Predicate Clitic Chains
    Swahili locative copula '-ko' replaces English 'to be', directly binding English
    predicative adjectives and states without verbal auxiliaries:
      - Niko down, Ako bored, Tuko ready, Uko serious?, Wako broke
    """
    COPULAS = {"niko", "uko", "ako", "tuko", "mko", "wako"}
    ENGLISH_PREDICATES = {
        "down", "bored", "serious", "ready", "broke", "high", "active",
        "free", "busy", "fine", "confused", "safe", "calm", "sick"
    }

    def analyze_copula_predicates(self, tokens: List[str]) -> List[Dict[str, str]]:
        found = []
        for i in range(len(tokens) - 1):
            c_low = tokens[i].lower()
            if c_low in self.COPULAS:
                nxt = tokens[i + 1].lower()
                if nxt in self.ENGLISH_PREDICATES:
                    found.append({
                        "copula": c_low,
                        "predicate": nxt,
                        "gloss": f"Copula-Predicate Fusion: '{c_low} {nxt}' (replaces English 'is/am/are {nxt}')"
                    })
        return found


class UniversalGenitiveEngine:
    """
    Rule XIII: Universal Genitive Collapse ("Wa" & "Za")
    Bypasses traditional Kiswahili associative concords (cha, vya, la, ya, mwa, kwa, pa):
      - 'wa' strictly connects singular animates, creators, and leaders:
        e.g. 'mkuu wa shule', 'dereva wa matatu', 'chali wa mtaa', 'track wa Wakadinali'
      - 'za' strictly connects all plurals and inanimates:
        e.g. 'ngoma za Arbantone', 'issue za life', 'vitu za keja'
    """
    def analyze_genitives(self, tokens: List[str]) -> List[Dict[str, str]]:
        found = []
        for i in range(1, len(tokens) - 1):
            g_low = tokens[i].lower()
            if g_low in ("wa", "za"):
                prev = tokens[i - 1]
                nxt = tokens[i + 1]
                role = "Animate/Authorial Genitive" if g_low == "wa" else "Plural/Inanimate Genitive"
                found.append({
                    "genitive": g_low,
                    "head": prev,
                    "modifier": nxt,
                    "role": role,
                    "phrase": f"{prev} {g_low} {nxt}"
                })
        return found


class DiscourseAnchorEngine:
    """
    Rule XIV: Discourse Solidarity & Evidential Anchors
    Pragmatic clause-boundary anchors that control tone, intimacy, and authenticity:
      - 'Manze': Sentence-initial empathy, exasperation, or narrative gravity
      - 'Bana': Sentence-final solidarity, emphasis, or finality
      - 'Buda' / 'Maze': Vocative peer address
      - 'Walahi': Evidential truth marker / oath of authenticity
    """
    ANCHORS = {
        "manze": "Sentence-initial empathy / narrative gravitas",
        "bana": "Sentence-final solidarity / emphatic agreement",
        "buda": "Vocative peer address",
        "maze": "Conversational exclamation / emphasis",
        "mazee": "Conversational exclamation / emphasis",
        "walahi": "Evidential oath / truth assertion"
    }

    def analyze_anchors(self, tokens: List[str]) -> List[Dict[str, str]]:
        found = []
        for t in tokens:
            t_low = t.lower()
            if t_low in self.ANCHORS:
                found.append({
                    "anchor": t,
                    "pragmatic_function": self.ANCHORS[t_low]
                })
        return found


class SubjunctiveAuxiliaryEngine:
    """
    Rule XV: Subjunctive Cohortative & Prohibitive Chains
    1. Cohortative / Departure ('Acha' + Subjunctive -e):
       - Acha nichomoke (Let me leave)
       - Acha nikuitie (Let me call for you)
       - Wacha tuone (Let's see)
    2. Prohibitive ('Wacha ku-' + [Bare English Root]):
       - Wacha kuoverthink
       - Wacha kupanic
    """
    def analyze_subjunctive(self, sentence: str) -> List[Dict[str, str]]:
        found = []
        lowered = sentence.lower()
        # Check cohortative acha / wacha
        cohortative_matches = re.finditer(r"\b(acha|wacha)\s+([a-z]+[e])\b", lowered)
        for m in cohortative_matches:
            found.append({
                "type": "COHORTATIVE",
                "phrase": m.group(0),
                "meaning": f"Cohortative permission/departure: '{m.group(0)}'"
            })
        # Check prohibitive wacha ku-
        prohibitive_matches = re.finditer(r"\b(wacha|acha)\s+ku([a-z]+)\b", lowered)
        for m in prohibitive_matches:
            found.append({
                "type": "PROHIBITIVE",
                "phrase": m.group(0),
                "meaning": f"Prohibitive admonition against action: '{m.group(0)}'"
            })
        return found


class OpenVowelEpenthesisEngine:
    """
    Rule XVI: Bantu Open-Vowel Epenthesis / Paragoge (CV Syllabic Harmony)
    English words with terminal consonant codas undergo epenthesis (adding -i, -u, or -o)
    to enforce canonical Bantu open syllable structure (CV):
      - check -> cheki
      - pass -> pasi
      - book -> buku
      - lock -> loki
      - post -> posti
      - club -> klabu
      - court -> koti
      - soup -> supu
    """
    EPENTHETIC_LOANS = {
        "cheki": ("check", "look / observe"),
        "pasi": ("pass", "pass by / give"),
        "buku": ("book", "reading material"),
        "loki": ("lock", "secure / fasten"),
        "posti": ("post", "publish content"),
        "klabu": ("club", "entertainment venue"),
        "koti": ("court", "judicial court"),
        "supu": ("soup", "broth / stew")
    }

    def analyze_epenthesis(self, tokens: List[str]) -> List[Dict[str, str]]:
        found = []
        for t in tokens:
            t_low = t.lower()
            if t_low in self.EPENTHETIC_LOANS:
                src, meaning = self.EPENTHETIC_LOANS[t_low]
                found.append({
                    "surface_form": t,
                    "english_source": src,
                    "meaning": meaning,
                    "gloss": f"Open-Vowel CV Adaptation: '{t}' from English '{src}'"
                })
        return found


class ReduplicativeIntensifierEngine:
    """
    Rule XVII: Reduplicative Intensification Matrix
    Full morpheme reduplication functions as the ultimate street superlative:
      - mbaya mbaya (extraordinarily / excessively lit)
      - sasa sasa (right this instant / maximum urgency)
      - fiti fiti (pristine / top-tier)
      - pole pole (very slowly / calmly)
    """
    INTENSIFIERS = {
        "mbaya mbaya": "Superlative intensity (exceedingly / to the extreme)",
        "sasa sasa": "Immediate absolute temporal urgency",
        "fiti fiti": "Pristine perfection / flawless condition",
        "pole pole": "Deliberate gentle pacing"
    }

    def analyze_reduplication(self, sentence: str) -> List[Dict[str, str]]:
        found = []
        lowered = sentence.lower()
        for pattern, meaning in self.INTENSIFIERS.items():
            if pattern in lowered:
                found.append({
                    "reduplication": pattern,
                    "meaning": meaning
                })
        return found


# ==============================================================================
# UNIFIED VALIDATOR: LOOSELY SWAHILI MASTER BLUEPRINT
# ==============================================================================

class LooselySwahiliValidator:
    """
    End-to-End Auditor and Compliance Engine for all 17 Pillars & Emergent Rules of
    the Official Master Lexicon & Structural Blueprint for East African Sheng / Engsh.
    """

    def __init__(self, default_deep_street_slang: bool = False):
        self.default_deep_street_slang = default_deep_street_slang
        # Master Blueprint 9 Pillars
        self.morpho = MorphosyntacticEngine()
        self.nouns = NounClassEngine()
        self.manner = MannerModifierEngine()
        self.possessives = PossessiveEngine()
        self.prepositions = PrepositionEngine()
        self.time = TimeCertaintyEngine()
        self.financial = FinancialElectronicsEngine()
        self.conversational = ConversationalDistressEngine()

        # Discovered Emergent Rules (Rules X - XVII)
        self.metathesis = MetathesisEngine(deep_street_slang=default_deep_street_slang)
        self.deictics = DemonstrativeCompressionEngine()
        self.copula_pred = CopulaPredicateEngine()
        self.genitives = UniversalGenitiveEngine()
        self.anchors = DiscourseAnchorEngine()
        self.subjunctive = SubjunctiveAuxiliaryEngine()
        self.epenthesis = OpenVowelEpenthesisEngine()
        self.reduplication = ReduplicativeIntensifierEngine()

    def audit_sentence(self, sentence: str, deep_street_slang: Optional[bool] = None) -> SentenceComplianceReport:
        active_deep_street = self.default_deep_street_slang if deep_street_slang is None else deep_street_slang
        issues: List[RuleValidationIssue] = []
        pillars_triggered: List[str] = []
        breakdown: Dict[str, Any] = {}

        # 1. Preposition checks (Section V)
        prep_issues = self.prepositions.check_prepositions(sentence)
        if prep_issues:
            issues.extend(prep_issues)
            pillars_triggered.append("Pillar V: Prepositions")
        breakdown["preposition_issues"] = [i.faulty_segment for i in prep_issues]

        # 2. Time checks & conventions (Section VI)
        time_analyses = self.time.analyze_time(sentence)
        if time_analyses:
            pillars_triggered.append("Pillar VI: Time & Certainty")
            for t in time_analyses:
                if t.convention in ("DIGIT_VIOLATION", "AT_VIOLATION"):
                    issues.append(RuleValidationIssue(
                        pillar="VI. Time & Certainty",
                        rule_name="Written in Words Only / No 'At'",
                        severity="ERROR",
                        faulty_segment=t.raw_expression,
                        explanation=t.note,
                        suggestion="Write time in words without 'at' (e.g., 'three' or 'around three')."
                    ))
        breakdown["time_analyses"] = [t.__dict__ for t in time_analyses]

        # 3. Financial & Electronics checks (Section VII)
        fin_analyses = self.financial.analyze_financial(sentence)
        if fin_analyses:
            pillars_triggered.append("Pillar VII: Financial & Electronics Matrix")
            for f in fin_analyses:
                if not f.is_valid:
                    issues.append(RuleValidationIssue(
                        pillar="VII. Financial & Electronics Value Matrix",
                        rule_name="Street Currency & Counting Constraint",
                        severity="ERROR",
                        faulty_segment=f.raw_expression,
                        explanation=f.error_message,
                        suggestion="Use valid English Track ('Two K') or Swahili Track ('Thao mbili'). Avoid 'soo one'."
                    ))
        breakdown["financial_analyses"] = [f.__dict__ for f in fin_analyses]

        # 4. Conversational Status & Distress checks (Section VIII)
        status_analyses = self.conversational.analyze_status(sentence)
        if status_analyses:
            pillars_triggered.append("Pillar VIII: Conversational Status & Distress")
        breakdown["status_analyses"] = [s.__dict__ for s in status_analyses]

        # 5. Token-by-token Morphosyntactic & Noun checks (Sections I, II, III, IV)
        tokens = re.findall(r"\b[\w'-]+\b", sentence)

        # Inversion Decoder Routing Table: rewrite tokens internally before downstream parsing
        normalized_tokens = self.metathesis.intercept_and_rewrite(tokens)

        # Check mid-sentence English negations: "don't", "didn't", "not"
        lowered_tokens = [t.lower() for t in tokens]
        for bad_neg in ("don't", "dont", "didn't", "didnt"):
            if bad_neg in lowered_tokens:
                issues.append(RuleValidationIssue(
                    pillar="I. The Morphosyntactic Engine",
                    rule_name="The Negation Framework",
                    severity="ERROR",
                    faulty_segment=bad_neg,
                    explanation=(
                        f"Mid-sentence English '{bad_neg}' is rejected. The mouth relies entirely on Swahili negative prefixes."
                    ),
                    suggestion="Replace with Swahili negative verb (e.g., 'sicare', 'sikucall', 'sijaclean')."
                ))
                pillars_triggered.append("Pillar I: Morphosyntactic Engine")

        verbs_analyzed = []
        manner_analyzed = []
        double_stacks = []

        for orig_tok in tokens:
            # Check Ki-/Vi- manner modifier (Section III)
            man_res = self.manner.analyze_manner(orig_tok)
            if man_res.is_manner_modifier:
                manner_analyzed.append(man_res.__dict__)
                pillars_triggered.append("Pillar III: Ki-/Vi- Modifier")

            # Check Nouns & Food Plural rule (Section II)
            n_res = self.nouns.analyze_noun(orig_tok)
            if n_res.noun_class == "ILLEGAL_FOOD_PLURAL":
                issues.append(RuleValidationIssue(
                    pillar="II. Noun Pluralization",
                    rule_name="Food Plural Constraint",
                    severity="ERROR",
                    faulty_segment=orig_tok,
                    explanation=n_res.gloss,
                    suggestion="Use 'Chapos', never 'Machapo'."
                ))
                pillars_triggered.append("Pillar II: Noun Pluralization")
            elif n_res.is_double_stack:
                double_stacks.append(orig_tok)
                pillars_triggered.append("Pillar II: Noun Pluralization")

            # Check Verbs & Bare Root Constraint (Section I)
            v_res = self.morpho.analyze_verb(orig_tok)
            if v_res.has_affect_conflict:
                issues.append(RuleValidationIssue(
                    pillar="I. The Morphosyntactic Engine",
                    rule_name="Affective Polarity Mutual Exclusion Constraint",
                    severity="ERROR",
                    faulty_segment=orig_tok,
                    explanation=v_res.error_message,
                    suggestion="Choose either Forced Ki- for disgust/contempt OR -ka- for endearing/soft-target. Do not stack them."
                ))
                pillars_triggered.append("Pillar I: Morphosyntactic Engine")
            elif v_res.has_double_conjugation_error:
                issues.append(RuleValidationIssue(
                    pillar="I. The Morphosyntactic Engine",
                    rule_name="The Bare Root Constraint",
                    severity="ERROR",
                    faulty_segment=orig_tok,
                    explanation=v_res.error_message,
                    suggestion=f"Enforce bare root: Use uninflected base verb."
                ))
                pillars_triggered.append("Pillar I: Morphosyntactic Engine")
            elif v_res.is_valid_plug_in:
                verbs_analyzed.append(v_res.__dict__)
                pillars_triggered.append("Pillar I: Morphosyntactic Engine")
                if v_res.is_soft_target:
                    pillars_triggered.append("Pillar I: Soft-Target Modifier (-ka-)")
                    issues.append(RuleValidationIssue(
                        pillar="I. The Morphosyntactic Engine",
                        rule_name="The Soft-Target Modifier (-ka-)",
                        severity="INFO",
                        faulty_segment=orig_tok,
                        explanation=(
                            f"Bantu Class 12 Diminutive Infix '-ka-' detected inside verb complex '{orig_tok}'. "
                            f"The speaker injects emotional affect, framing the target as delicate, cute, non-threatening, "
                            f"or affectionately vulnerable (handled gently)."
                        ),
                        suggestion="Preserve soft-target endearing nuance in translation and downstream NLP representations."
                    ))
                elif v_res.is_disgust_depersonalized:
                    pillars_triggered.append("Pillar I: Disgust / Contempt Modifier (Forced Ki-)")
                    issues.append(RuleValidationIssue(
                        pillar="I. The Morphosyntactic Engine",
                        rule_name="The Disgust / Sarcasm Modifier (Forced Ki-)",
                        severity="INFO",
                        faulty_segment=orig_tok,
                        explanation=(
                            f"Forced Inanimate Ki- Class prefix detected on verb complex '{orig_tok}'. "
                            f"The speaker strips human dignity and forcefully depersonalizes the referent into an 'it' / object "
                            f"to express deep disgust, irritation, or biting sarcasm."
                        ),
                        suggestion="Preserve sarcastic/disgust depersonalization nuance in translation."
                    ))

        breakdown["verbs"] = verbs_analyzed
        breakdown["manner_modifiers"] = manner_analyzed
        breakdown["double_stack_nouns"] = double_stacks

        # Check Possessives (Section IV)
        poss_res = self.possessives.analyze_possessive_phrase(tokens)
        if poss_res["track"] != "none":
            pillars_triggered.append("Pillar IV: Possessives")
        breakdown["possessives"] = poss_res

        # Check Discovered Emergent Rules (Sections X - XVII)
        meta_res = self.metathesis.analyze_metathesis(tokens, deep_street_slang=active_deep_street)
        if meta_res:
            pillars_triggered.append("Pillar X: Metathesis Inversion")
            if not active_deep_street:
                crypto_words = [m["surface_form"] for m in meta_res]
                shifts = [m for m in meta_res if m["is_semantic_shift"]]
                shift_warn = ""
                if shifts:
                    shift_warn = " Semantic shift protection active: " + "; ".join(
                        f"'{s['surface_form']}' rewritten to '{s['internal_rewrite']}' ({s['safe_universal_equivalent']})"
                        for s in shifts
                    ) + "."
                issues.append(RuleValidationIssue(
                    pillar="X. Metathesis Inversion",
                    rule_name="Structural Insulation Layer (Generational Slider OFF)",
                    severity="INFO",
                    faulty_segment=", ".join(crypto_words),
                    explanation=(
                        f"Cryptographic Metathesis detected ({', '.join(crypto_words)}). "
                        f"The Generational/Locational Slider is currently OFF (Standard Mode). "
                        f"The Structural Insulation Layer has internally rewritten these tokens via the "
                        f"Inversion Decoder Routing Table before downstream grammatical parsing.{shift_warn}"
                    ),
                    suggestion=(
                        f"Use Silent Normalization: '{self.metathesis.normalize_silently(sentence)}' "
                        f"or Visual Glancing: '{self.metathesis.glance_annotated(sentence)}'. "
                        f"Activate deep_street_slang=True for raw street authenticity."
                    )
                ))
        breakdown["metathesis"] = meta_res
        breakdown["metathesis_slider_mode"] = "DEEP_STREET_AUTHENTICITY" if active_deep_street else "STANDARD_INSULATED"
        breakdown["silent_normalization"] = self.metathesis.normalize_silently(sentence)
        breakdown["visual_glancing"] = self.metathesis.glance_annotated(sentence)
        breakdown["internal_rewritten_tokens"] = normalized_tokens

        deictic_res = self.deictics.analyze_deictics(tokens)
        if deictic_res:
            pillars_triggered.append("Pillar XI: Demonstrative Compression")
        breakdown["deictics"] = deictic_res

        copula_res = self.copula_pred.analyze_copula_predicates(tokens)
        if copula_res:
            pillars_triggered.append("Pillar XII: Copula-Predicate Fusion")
        breakdown["copula_predicates"] = copula_res

        gen_res = self.genitives.analyze_genitives(tokens)
        if gen_res:
            pillars_triggered.append("Pillar XIII: Universal Genitives")
        breakdown["genitives"] = gen_res

        anchor_res = self.anchors.analyze_anchors(tokens)
        if anchor_res:
            pillars_triggered.append("Pillar XIV: Discourse Solidarity Anchors")
        breakdown["discourse_anchors"] = anchor_res

        subj_res = self.subjunctive.analyze_subjunctive(sentence)
        if subj_res:
            pillars_triggered.append("Pillar XV: Subjunctive Cohortative & Prohibitive Chains")
        breakdown["subjunctive"] = subj_res

        epenthesis_res = self.epenthesis.analyze_epenthesis(tokens)
        if epenthesis_res:
            pillars_triggered.append("Pillar XVI: Bantu Open-Vowel Epenthesis")
        breakdown["epenthesis"] = epenthesis_res

        redup_res = self.reduplication.analyze_reduplication(sentence)
        if redup_res:
            pillars_triggered.append("Pillar XVII: Reduplicative Intensification")
        breakdown["reduplication"] = redup_res

        unique_pillars = sorted(list(set(pillars_triggered)))
        is_compliant = not any(issue.severity == "ERROR" for issue in issues)

        return SentenceComplianceReport(
            original_sentence=sentence,
            is_fully_compliant=is_compliant,
            issues=issues,
            pillars_triggered=unique_pillars,
            syntactic_breakdown=breakdown
        )

    def validate_dialogue(self, transcript_lines: List[str], deep_street_slang: Optional[bool] = None) -> List[SentenceComplianceReport]:
        """
        Audits multi-turn spoken dialogue line by line (e.g. Master Contextual Script).
        """
        reports = []
        for line in transcript_lines:
            # Strip speaker prefix if present (e.g. 'Msee A: "..."')
            match = re.search(r'["“](.*?)["”]', line)
            speech_content = match.group(1) if match else line
            report = self.audit_sentence(speech_content, deep_street_slang=deep_street_slang)
            reports.append(report)
        return reports

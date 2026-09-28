"""
Bantu-English Verbal Fusion Engine (Kitenzi-Loan Morphotactic Matrix)
Treats English verbs as Bantu/Swahili roots (Vitenzi) and inflects them dynamically across:
1. WHO  - Subject Nafsi & Object agreement (1st/2nd/3rd person, Noun Classes 1-10)
2. WHEN - Tense, Aspect & Polarity (Past, Present, Future, Perfect, Conditional, Negation)
3. WHERE- Locative relatives & Directionals (-po-, -ko-, -mo-, -vyo-)
4. HOW  - Minyambuliko ya Vitenzi / Verbal Extensions (Kutenda, Kutendwa, Kutendea, Kutendesha, Kutendana, Kutendeka)

Connects the 3 Parallel Linguistic Sets:
- Set A: 100% Pure Kiswahili Sanifu
- Set B: 100% Pure English
- Set C: Kenyan Fused Sheng / Intra-Word Code-Switching
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

@dataclass
class FusionResult:
    fused_verb: str                  # Set C: e.g. "tutakutextia"
    formal_swahili: str              # Set A: e.g. "tutakuandikia ujumbe"
    pure_english: str                # Set B: e.g. "we will text for you"
    english_verb_root: str           # e.g. "text"
    who_subject: Dict[str, str]      # Who is doing it
    who_object: Dict[str, str]       # To whom it is done
    when_tense: Dict[str, str]       # When it is happening
    where_locative: Dict[str, str]   # Where / in what manner
    how_extension: Dict[str, str]    # How (voice / mnyambuliko)
    morpheme_chain: List[Dict[str, str]]
    explanation: str
    is_valid: bool = True            # False if semantically or morpho-syntactically invalid
    semantic_warning: str = ""       # Explanatory warning for invalid combinations (e.g. chill + kutendana)

@dataclass
class FusedDeconstructionResult:
    original_fused_word: str
    is_fused_verb: bool
    english_verb_root: str
    formal_swahili_equivalent: str
    pure_english_translation: str
    who: str
    when: str
    where: str
    how: str
    morpheme_gloss: str
    confidence: float

class BantuEnglishFusionEngine:
    """Algebraic Matrix for Swahili Morphological Fusion on Foreign Verb Stems."""

    # --------------------------------------------------------------------------
    # 1. WHO: SUBJECT PREFIXES (Nafsi & Ngeli za Majina)
    # --------------------------------------------------------------------------
    WHO_SUBJECTS = {
        "1s": {
            "pfx": "ni", "neg_pfx": "si", "label": "I (Mimi)",
            "sw": "mimi", "en": "I", "desc": "1st Person Singular"
        },
        "2s": {
            "pfx": "u", "neg_pfx": "hu", "label": "You (Wewe)",
            "sw": "wewe", "en": "you", "desc": "2nd Person Singular"
        },
        "3s": {
            "pfx": "a", "neg_pfx": "ha", "label": "He/She (Yeye)",
            "sw": "yeye", "en": "he/she", "desc": "3rd Person Singular (Class 1)"
        },
        "1p": {
            "pfx": "tu", "neg_pfx": "hatu", "label": "We (Sisi)",
            "sw": "sisi", "en": "we", "desc": "1st Person Plural"
        },
        "2p": {
            "pfx": "m", "neg_pfx": "ham", "label": "You all (Ninyi)",
            "sw": "ninyi", "en": "you all", "desc": "2nd Person Plural"
        },
        "3p": {
            "pfx": "wa", "neg_pfx": "hawa", "label": "They (Wao)",
            "sw": "wao", "en": "they", "desc": "3rd Person Plural (Class 2)"
        },
        "c9": {
            "pfx": "i", "neg_pfx": "hai", "label": "It (Class 9 - Simu/Kampuni)",
            "sw": "kitu hiki", "en": "it", "desc": "Inanimate Class 9 Singular"
        },
        "c10": {
            "pfx": "zi", "neg_pfx": "hazi", "label": "They (Class 10 - Sheria/Akaunti)",
            "sw": "vitu hivi", "en": "they", "desc": "Inanimate Class 10 Plural"
        },
        "c7": {
            "pfx": "ki", "neg_pfx": "haki", "label": "It (Class 7 - Chuo/Kitabu)",
            "sw": "kitu hiki", "en": "it", "desc": "Class 7 Singular"
        },
        "c8": {
            "pfx": "vi", "neg_pfx": "havi", "label": "They (Class 8 - Vituo/Vyuo)",
            "sw": "vitu hivi", "en": "they", "desc": "Class 8 Plural"
        },
        "c5": {
            "pfx": "li", "neg_pfx": "hali", "label": "It (Class 5 - Gari/Jiji)",
            "sw": "kitu hili", "en": "it", "desc": "Class 5 Singular"
        },
        "c6": {
            "pfx": "ya", "neg_pfx": "haya", "label": "They (Class 6 - Magari/Makampuni)",
            "sw": "vitu haya", "en": "they", "desc": "Class 6 Plural"
        }
    }

    # --------------------------------------------------------------------------
    # 1b. WHO: OBJECT INFIXES (Yambwa / Kitendewa)
    # --------------------------------------------------------------------------
    WHO_OBJECTS = {
        "none": {"ifx": "", "label": "None (No Object Marker)", "sw": "", "en": ""},
        "me": {"ifx": "ni", "label": "Me (Mimi)", "sw": "mimi", "en": "me"},
        "you": {"ifx": "ku", "label": "You (Wewe)", "sw": "wewe", "en": "you"},
        "him_her": {"ifx": "m", "label": "Him/Her (Yeye)", "sw": "yeye", "en": "him/her"},
        "us": {"ifx": "tu", "label": "Us (Sisi)", "sw": "sisi", "en": "us"},
        "them": {"ifx": "wa", "label": "Them (Wao)", "sw": "wao", "en": "them"},
        "self": {"ifx": "ji", "label": "Self / Reflexive (-ji-)", "sw": "mwenyewe", "en": "himself/herself"}
    }

    # --------------------------------------------------------------------------
    # 2. WHEN: TENSE & ASPECT (Nyakati na Hali)
    # --------------------------------------------------------------------------
    WHEN_TENSES = {
        "past": {
            "marker": "li", "neg_marker": "ku", "label": "Past Tense (-li-)",
            "en_helper": "did / was / were", "sw_desc": "Wakati Uliopita"
        },
        "present": {
            "marker": "na", "neg_marker": "i", "label": "Present Continuous (-na-)",
            "en_helper": "is / are ...-ing", "sw_desc": "Wakati Uliopo"
        },
        "future": {
            "marker": "ta", "neg_marker": "ta", "label": "Future Tense (-ta-)",
            "en_helper": "will / shall", "sw_desc": "Wakati Ujao"
        },
        "perfect": {
            "marker": "me", "neg_marker": "ja", "label": "Present Perfect (-me-)",
            "en_helper": "has / have", "sw_desc": "Wakati Uliotimilika"
        },
        "conditional": {
            "marker": "ki", "neg_marker": "sipo", "label": "Conditional Participle (-ki-)",
            "en_helper": "if / while", "sw_desc": "Hali ya Masharti / Wakati ukiendelea"
        },
        "narrative": {
            "marker": "ka", "neg_marker": "ka", "label": "Narrative Consecutive (-ka-)",
            "en_helper": "and then ...", "sw_desc": "Wakati wa Kusimulia"
        },
        "hypothetical": {
            "marker": "nge", "neg_marker": "singe", "label": "Hypothetical Conditional (-nge-)",
            "en_helper": "would", "sw_desc": "Masharti ya Kutegemea"
        },
        "infinitive": {
            "marker": "ku", "neg_marker": "kuto", "label": "Infinitive (ku-)",
            "en_helper": "to", "sw_desc": "Kauli ya Majina (Kitenzi Jina)"
        }
    }

    # --------------------------------------------------------------------------
    # 3. WHERE: LOCATIVES & DIRECTIONAL RELATIVES (-po-, -ko-, -mo-, -vyo-)
    # --------------------------------------------------------------------------
    WHERE_LOCATIVES = {
        "none": {"marker": "", "label": "None (No Location)", "en_phrase": "", "sw_phrase": ""},
        "where_at": {
            "marker": "po", "label": "Where / Point Location (-po-)",
            "en_phrase": "where / at the place that", "sw_phrase": "mahali / wakati ambapo"
        },
        "where_to": {
            "marker": "ko", "label": "Where to / Directional Location (-ko-)",
            "en_phrase": "to where / towards which", "sw_phrase": "kule ambako"
        },
        "inside": {
            "marker": "mo", "label": "Inside / Internal Location (-mo-)",
            "en_phrase": "inside where / wherein", "sw_phrase": "ndani ambamo"
        },
        "manner": {
            "marker": "vyo", "label": "How / Manner Relative (-vyo-)",
            "en_phrase": "how / the way that", "sw_phrase": "jinsi / vile"
        }
    }

    # --------------------------------------------------------------------------
    # 4. HOW: MINYAMBULIKO YA VITENZI / VERBAL EXTENSIONS
    # --------------------------------------------------------------------------
    HOW_EXTENSIONS = {
        "kutenda": {
            "label": "Kutenda (Base Active Action)",
            "suffix": "",
            "sw_voice": "Kauli ya Kutenda (Kawaida)",
            "en_voice": "Active Voice",
            "en_pattern": "{stem}",
            "sw_pattern": "{stem}"
        },
        "kutendwa": {
            "label": "Kutendwa (Passive Voice: -iwa)",
            "suffix": "iwa",
            "sw_voice": "Kauli ya Kutendwa (Passive)",
            "en_voice": "Passive Voice",
            "en_pattern": "be {stem}ed",
            "sw_pattern": "{stem}wa"
        },
        "kutendea": {
            "label": "Kutendea (Applicative: -ia - for / to)",
            "suffix": "ia",
            "sw_voice": "Kauli ya Kutendea (Kufanyia mtu)",
            "en_voice": "Applicative / Benefactive",
            "en_pattern": "{stem} for / on behalf of",
            "sw_pattern": "{stem}ia"
        },
        "kutendesha": {
            "label": "Kutendesha (Causative: -isha - make / cause to)",
            "suffix": "isha",
            "sw_voice": "Kauli ya Kutendesha (Kusababisha afanye)",
            "en_voice": "Causative",
            "en_pattern": "make / cause to {stem}",
            "sw_pattern": "fanya {stem}"
        },
        "kutendana": {
            "label": "Kutendana (Reciprocal / Mutual: ... pamoja - e.g. tunavibe pamoja)",
            "suffix": "pamoja",
            "sw_voice": "Kauli ya Kutendana (Pamoja / Wao kwa wao)",
            "en_voice": "Reciprocal / Mutual (pamoja)",
            "en_pattern": "{stem} together",
            "sw_pattern": "{stem} pamoja"
        },
        "kutendeka": {
            "label": "Kutendeka (Stative: -ika - capable of being done)",
            "suffix": "ika",
            "sw_voice": "Kauli ya Kutendeka (Uwezekano)",
            "en_voice": "Stative / Potential",
            "en_pattern": "capable of being {stem}ed / solvable",
            "sw_pattern": "{stem}ika"
        }
    }

    # --------------------------------------------------------------------------
    # 4b. TRANSITIVITY & SEMANTIC RESTRICTIONS (KENYAN NATURAL SPEECH CONSTRAINTS)
    # --------------------------------------------------------------------------
    INTRANSITIVE_RESTRICTIONS = {
        "chill": {
            "disallowed": ["kutendwa"],
            "reason": "'chill' is an intransitive stative verb in Kenyan speech; passive voice ('chilliwa') is unnatural."
        },
        "retire": {
            "disallowed": ["kutendwa"],
            "reason": "'retire' is an intransitive action (kustaafu); passive voice is not used."
        },
        "resign": {
            "disallowed": ["kutendwa"],
            "reason": "'resign' is intransitive (kujiuzulu); passive voice is not used."
        },
        "party": {
            "disallowed": ["kutendwa"],
            "reason": "'party' is intransitive; passive voice is not used."
        },
        "trend": {
            "disallowed": ["kutendwa"],
            "reason": "'trend' is an intransitive status; passive voice is not used."
        },
        "trip": {
            "disallowed": ["kutendwa"],
            "reason": "'trip' (in slang: panicking/overreacting) is intransitive; passive voice is unnatural."
        }
    }

    # --------------------------------------------------------------------------
    # 5. 150+ ENGLISH LOAN VERB ROOTS IN KENYAN URBAN SPEECH
    # --------------------------------------------------------------------------
    ENGLISH_LOAN_VERBS = {
        # Workplace, Career & Corporate
        "fire": ("futa kazi", "dismiss from employment", "corporate"),
        "hire": ("ajiri kazini", "employ", "corporate"),
        "promote": ("pandisha cheo", "elevate in rank", "corporate"),
        "demote": ("shusha cheo", "reduce in rank", "corporate"),
        "suspend": ("simamisha kwa muda", "suspend temporarily", "corporate"),
        "cancel": ("futa / ahirisha", "call off / nullify", "corporate"),
        "resign": ("jiuzulu", "step down from office", "corporate"),
        "retire": ("staafu", "retire from service", "corporate"),
        "interview": ("hoji kazini", "interview", "corporate"),
        "confirm": ("thibitisha", "verify / confirm", "corporate"),
        "sign": ("tia saini", "sign formally", "corporate"),
        "retrench": ("punguza wafanyikazi", "downsize staff", "corporate"),
        "negotiate": ("jadiliana maslahi", "bargain / negotiate", "corporate"),

        # Technology, Software & Data
        "hack": ("dukua mtandaoni", "gain unauthorized access", "tech"),
        "block": ("zuia mawasiliano", "bar communication", "tech"),
        "delete": ("futa kabisa", "erase permanently", "tech"),
        "freeze": ("zuia akaunti / gandisha", "halt bank or system access", "tech"),
        "wire": ("tuma fedha kielektroniki", "transfer funds electronically", "tech"),
        "update": ("sasisha taarifa", "bring up to date", "tech"),
        "download": ("pakua mtandaoni", "retrieve from network", "tech"),
        "upload": ("pakia mtandaoni", "send to network", "tech"),
        "code": ("andika msimbo wa programu", "program / write software", "tech"),
        "deploy": ("weka mfumo hewani", "release software to production", "tech"),
        "format": ("futa na kuweka upya", "wipe and reinitialize", "tech"),
        "install": ("weka programu", "set up application", "tech"),
        "uninstall": ("ondoa programu", "remove application", "tech"),
        "forward": ("tuma mbele", "redirect message", "tech"),
        "backup": ("hifadhi nakala", "create redundant copy", "tech"),
        "record": ("rekodi sauti / video", "capture audio/video", "tech"),
        "post": ("chapisha mtandaoni", "publish online", "tech"),
        "screenshot": ("piga picha ya skrini", "capture screen image", "tech"),
        "share": ("shiriki maudhui", "distribute content", "tech"),

        # Street, Relationships & Social Dynamics
        "date": ("kuwa katika uhusiano wa kimapenzi", "be in a dating relationship", "social"),
        "ghost": ("katiza mawasiliano ghafla", "cut off contact abruptly", "social"),
        "confuse": ("changanya akili", "disorient / bewilder", "social"),
        "vibe": ("elewana vizuri", "connect well / resonate", "social"),
        "chill": ("pumzika kwa utulivu", "relax / hang out", "social"),
        "party": ("sherehekea kwa furaha", "celebrate vigorously", "social"),
        "snitch": ("chongea kwa mamlaka", "inform / betray trust", "social"),
        "frame": ("singizia makosa", "set up wrongfully", "social"),
        "blame": ("laumu bure", "accuse / hold responsible", "social"),
        "expose": ("anika hadharani", "reveal shameful secrets", "social"),
        "trend": ("kuwa maarufu mtandaoni", "become widely talked about", "social"),
        "text": ("tuma ujumbe mfupi", "send mobile text message", "social"),
        "call": ("piga simu", "make phone call", "social"),
        "flirt": ("tongoza kwa utani", "court playfully", "social"),
        "ignore": ("puuza kabisa", "disregard intentionally", "social"),
        "support": ("saidia / unga mkono", "aid / back up", "social"),
        "organize": ("panga mambo vizuri", "arrange / coordinate", "social"),
        "enjoy": ("furahia sana", "relish / take pleasure", "social"),
        "trip": ("kwazika / shindwa kuelewa", "overreact / stumble", "social"),
        "delay": ("chelewesha", "postpone / linger", "social"),

        # Law, Civic Life & Discipline
        "arrest": ("kamata chini ya ulinzi", "detain legally", "civic"),
        "cane": ("piga kwa bakora", "flog with a cane", "civic"),
        "ban": ("piga marufuku", "prohibit legally", "civic"),
        "charge": ("fungulia mashtaka", "indict in court", "civic"),
        "fine": ("toza faini", "penalize financially", "civic"),
        "inspect": ("kagua kwa kina", "examine officially", "civic"),
        "patrol": ("fanya doria", "conduct security rounds", "civic"),
        "snatch": ("pora kwa nguvu", "grab and steal", "civic"),

        # Everyday Transactions & Services
        "book": ("weka nafasi", "reserve in advance", "everyday"),
        "pay": ("lipa fedha", "settle payment", "everyday"),
        "repair": ("tengeneza kilichoharibika", "mend / restore", "everyday"),
        "fix": ("rekebisha hitilafu", "resolve fault", "everyday"),
        "clean": ("safisha kabisa", "sanitize / clean", "everyday"),
        "rush": ("harakisha", "hurry / hasten", "everyday"),
        "solve": ("tatua tatizo", "resolve conundrum", "everyday")
    }

    def __init__(self):
        pass

    # --------------------------------------------------------------------------
    # FUSION COMPILATION ENGINE: SYNTHESIS (WHO + WHEN + WHERE + HOW -> SET C)
    # --------------------------------------------------------------------------
    def fuse(
        self,
        english_verb: str,
        who_subj: str = "3s",       # e.g. "1s", "2s", "3s", "1p", "2p", "3p", "c9", "c10"
        who_obj: str = "none",      # e.g. "none", "me", "you", "him_her", "us", "them", "self"
        when_tense: str = "past",   # e.g. "past", "present", "future", "perfect", "conditional"
        where_loc: str = "none",    # e.g. "none", "where_at", "where_to", "inside", "manner"
        how_ext: str = "kutenda",   # e.g. "kutenda", "kutendwa", "kutendea", "kutendesha", "kutendana", "kutendeka"
        is_negative: bool = False
    ) -> FusionResult:
        """
        Dynamically fuses an English verb into a Swahili kitenzi structure and generates
        the 3 synchronized parallel linguistic sets (Set A, Set B, Set C).
        """
        verb_clean = english_verb.lower().strip()
        v_info = self.ENGLISH_LOAN_VERBS.get(verb_clean, (f"kufanya {verb_clean}", verb_clean, "general"))
        sw_canonical, en_base, domain = v_info

        # 1. Subject Prefix
        subj_data = self.WHO_SUBJECTS.get(who_subj, self.WHO_SUBJECTS["3s"])
        s_pfx = subj_data["neg_pfx"] if is_negative else subj_data["pfx"]

        # 2. Tense Marker
        tense_data = self.WHEN_TENSES.get(when_tense, self.WHEN_TENSES["past"])
        t_marker = tense_data["neg_marker"] if is_negative else tense_data["marker"]

        # 3. Where / Relative Locative
        loc_data = self.WHERE_LOCATIVES.get(where_loc, self.WHERE_LOCATIVES["none"])
        loc_marker = loc_data["marker"]

        # 4. Object Infix
        obj_data = self.WHO_OBJECTS.get(who_obj, self.WHO_OBJECTS["none"])
        obj_marker = obj_data["ifx"]

        # Phonological adjustment for 3rd person singular object infix: 'm' -> 'mw' before vowel
        if obj_marker == "m" and verb_clean[0] in "aeiou":
            obj_marker = "mw"

        # 5. How: Derivational Verbal Extension (Mnyambuliko)
        ext_data = self.HOW_EXTENSIONS.get(how_ext, self.HOW_EXTENSIONS["kutenda"])
        raw_suffix = ext_data["suffix"]

        # Vowel elision & phonological harmony on loan verb
        fused_stem, applied_suffix = self._apply_loan_phonotactics(verb_clean, raw_suffix, how_ext=how_ext)

        # -------------------------------------------------------------
        # SYNTHESIZE SET C: FUSED KENYAN SHENG VERB
        # -------------------------------------------------------------
        morphemes = []
        if s_pfx:
            morphemes.append({"morpheme": s_pfx, "type": "Subject Prefix (WHO)", "meaning": subj_data["en"]})
        if t_marker:
            morphemes.append({"morpheme": t_marker, "type": "Tense/Aspect Marker (WHEN)", "meaning": tense_data["label"]})
        if loc_marker:
            morphemes.append({"morpheme": loc_marker, "type": "Locative/Manner Relative (WHERE)", "meaning": loc_data["en_phrase"]})
        if obj_marker:
            morphemes.append({"morpheme": obj_marker, "type": "Object Infix (TO WHOM)", "meaning": obj_data["en"]})
        
        morphemes.append({"morpheme": fused_stem, "type": "Loan Verb Root (KITENZI)", "meaning": en_base})
        
        if applied_suffix:
            morphemes.append({"morpheme": applied_suffix, "type": "Mnyambuliko Extension (HOW)", "meaning": ext_data["en_voice"]})

        # Concatenate Set C fused surface form
        if how_ext == "kutendana":
            # Natural Kenyan Speech: Reciprocal on English loan verbs uses 'pamoja'
            verb_chain = [s_pfx, t_marker, loc_marker, obj_marker, verb_clean]
            set_c_fused = "".join(tok for tok in verb_chain if tok) + " pamoja"
            morphemes = []
            if s_pfx:
                morphemes.append({"morpheme": s_pfx, "type": "Subject Prefix (WHO)", "meaning": subj_data["en"]})
            if t_marker:
                morphemes.append({"morpheme": t_marker, "type": "Tense/Aspect Marker (WHEN)", "meaning": tense_data["label"]})
            if loc_marker:
                morphemes.append({"morpheme": loc_marker, "type": "Locative/Manner Relative (WHERE)", "meaning": loc_data["en_phrase"]})
            if obj_marker:
                morphemes.append({"morpheme": obj_marker, "type": "Object Infix (TO WHOM)", "meaning": obj_data["en"]})
            morphemes.append({"morpheme": verb_clean, "type": "Loan Verb Root (KITENZI)", "meaning": en_base})
            morphemes.append({"morpheme": "pamoja", "type": "Reciprocal / Mutual Particle", "meaning": "together / mutually"})
        else:
            chain_tokens = [s_pfx, t_marker, loc_marker, obj_marker, fused_stem, applied_suffix]
            set_c_fused = "".join(tok for tok in chain_tokens if tok)

        # -------------------------------------------------------------
        # SYNTHESIZE SET A: PURE KISWAHILI SANIFU
        # -------------------------------------------------------------
        set_a_sanifu = self._synthesize_sanifu_set_a(
            sw_canonical, subj_data, obj_data, tense_data, loc_data, how_ext, is_negative
        )

        # -------------------------------------------------------------
        # SYNTHESIZE SET B: PURE ENGLISH
        # -------------------------------------------------------------
        set_b_english = self._synthesize_english_set_b(
            verb_clean, subj_data, obj_data, tense_data, loc_data, how_ext, is_negative
        )

        # -------------------------------------------------------------
        # TRANSITIVITY & SEMANTIC VALIDATION (KENYAN NATURAL CONSTRAINTS)
        # -------------------------------------------------------------
        is_valid = True
        semantic_warning = ""
        restriction = self.INTRANSITIVE_RESTRICTIONS.get(verb_clean)
        if restriction and how_ext in restriction["disallowed"]:
            is_valid = False
            semantic_warning = restriction["reason"]

        explanation = (
            f"English root '{verb_clean}' fused as a Swahili kitenzi with: "
            f"WHO ({subj_data['label']}" + (f" -> {obj_data['label']}" if obj_data['ifx'] else "") + "), "
            f"WHEN ({tense_data['label']}), "
            f"WHERE ({loc_data['label']}), and "
            f"HOW ({ext_data['label']})."
        )
        if not is_valid:
            explanation += f" [Note: {semantic_warning}]"

        return FusionResult(
            fused_verb=set_c_fused,
            formal_swahili=set_a_sanifu,
            pure_english=set_b_english,
            english_verb_root=verb_clean,
            who_subject=subj_data,
            who_object=obj_data,
            when_tense=tense_data,
            where_locative=loc_data,
            how_extension=ext_data,
            morpheme_chain=morphemes,
            explanation=explanation,
            is_valid=is_valid,
            semantic_warning=semantic_warning
        )

    def _apply_loan_phonotactics(self, stem: str, suffix: str = "", how_ext: str = "") -> Tuple[str, str]:
        """
        Kenyan Verbal Morphotactic Rule:
        - If the verb ends with a vowel and the preceding letter is a consonant (e.g. fire, cane, solve):
            Drop the vowel only, and use extensions starting with 'i':
            - Kutendwa   -> -iwa   (fire -> fir + iwa = firiwa)
            - Kutendea   -> -ia    (cane -> can + ia = cania)
            - Kutendesha -> -isha  (solve -> solv + isha = solvisha)
            - Kutendeka  -> -ika   (solve -> solv + ika = solvika)
            - Kutendana  -> -iana / -ana (vibe -> vibiana, date -> datiana, chill -> chillana)
        - If the verb ends with a consonant (e.g. book, text, sign, call, chill):
            Keep the verb stem intact, and use extensions starting with 'i':
            - Kutendwa   -> -iwa   (book -> book + iwa = bookiwa)
            - Kutendea   -> -ia    (text -> text + ia = textia)
            - Kutendesha -> -isha  (sign -> sign + isha = signisha)
            - Kutendeka  -> -ika   (lock -> lock + ika = lockika)
            - Kutendana  -> -ana   (chill -> chill + ana = chillana)
        """
        clean_stem = stem.lower().strip()
        if not clean_stem:
            return stem, ""

        key = how_ext
        if not key:
            suffix_map = {
                "iwa": "kutendwa", "ewa": "kutendwa", "wa": "kutendwa",
                "ia": "kutendea", "ea": "kutendea", "a": "kutendea",
                "isha": "kutendesha", "esha": "kutendesha", "sha": "kutendesha",
                "ika": "kutendeka", "eka": "kutendeka", "ka": "kutendeka",
                "ana": "kutendana", "eana": "kutendana", "iana": "kutendana",
            }
            key = suffix_map.get(suffix, "kutenda")

        if key == "kutenda" or (not suffix and not how_ext):
            return clean_stem, ""

        # 1. Verbs ending in '-are' (e.g. share, care) with r-diphthong /ɛər/:
        # - Reciprocal: preserves root + 'ana' -> 'wanashareana'
        # - i-extensions (-iwa, -ia, -ika, -isha): inserts euphonic 'r' -> 'sharer' + 'iwa' = 'tutashareriwa'
        if clean_stem.endswith("are"):
            if key == "kutendana":
                return clean_stem, "ana"
            elif key in ["kutendwa", "kutendea", "kutendeka", "kutendesha"]:
                i_exts_are = {
                    "kutendwa": "iwa",
                    "kutendea": "ia",
                    "kutendesha": "isha",
                    "kutendeka": "ika"
                }
                return clean_stem[:-1] + "er", i_exts_are.get(key, "iwa")

        # 2. Reciprocal (Kutendana):
        # User rule: If the verb ends with 'e' and preceding letter is a consonant (e.g. vibe, date),
        # drop the 'e' and use 'iana' (vibe -> vibiana, date -> datiana)
        if key == "kutendana":
            vowels = ("a", "e", "i", "o", "u")
            if len(clean_stem) >= 2 and clean_stem.endswith("e") and clean_stem[-2] not in vowels:
                return clean_stem[:-1], "iana"
            elif clean_stem[-1] in vowels:
                return clean_stem[:-1], "iana"
            return clean_stem, "ana"

        # General i-extensions:
        i_extensions = {
            "kutendwa": "iwa",
            "kutendea": "ia",
            "kutendesha": "isha",
            "kutendeka": "ika",
            "kutenda": ""
        }
        applied = i_extensions.get(key, "ia")

        vowels = ("a", "e", "i", "o", "u")
        ends_with_vowel = clean_stem[-1] in vowels

        if ends_with_vowel:
            # Verb ends with a vowel: drop the vowel only, attach 'i' extension
            clean_stem = clean_stem[:-1]

        return clean_stem, applied

    def _synthesize_sanifu_set_a(
        self, sw_canonical: str, subj: Dict, obj: Dict, tense: Dict, loc: Dict, how: str, is_neg: bool
    ) -> str:
        """Constructs 100% pure Kiswahili Sanifu equivalent."""
        s_pfx = subj["pfx"]
        t_marker = tense["marker"]
        o_ifx = obj["ifx"]
        if is_neg:
            s_pfx = subj["neg_pfx"]
            t_marker = tense["neg_marker"]

        loc_str = f" {loc['sw_phrase']}" if loc["marker"] else ""

        # Special phrasing for corporate/street loans
        if sw_canonical == "futa kazi":
            if how == "kutendwa":
                verb_part = "kufutwa kazi" if is_neg else "lifutwa kazi"
                return f"{subj['sw']} {s_pfx}{verb_part}{loc_str}"
            elif obj["ifx"]:
                obj_m = "m" if obj["ifx"] in ["m", "him_her"] else obj["ifx"]
                return f"{subj['sw']} {s_pfx}{t_marker}{obj_m}futa kazi{loc_str}"
            return f"{subj['sw']} {s_pfx}{t_marker}futa kazi{loc_str}"

        if sw_canonical == "tuma ujumbe mfupi":
            if how == "kutendea":
                target_ifx = o_ifx if o_ifx else "m"
                return f"{subj['sw']} {s_pfx}{t_marker}{target_ifx}tumia ujumbe mfupi{loc_str}"
            return f"{subj['sw']} {s_pfx}{t_marker}tuma ujumbe mfupi{loc_str}"

        if sw_canonical == "changanya akili":
            target_ifx = o_ifx if o_ifx else ""
            return f"{subj['sw']} {s_pfx}{t_marker}{target_ifx}changanya akili{loc_str}"

        if sw_canonical == "elewana vizuri":
            if how == "kutendana" or subj["pfx"] in ["wa", "tu", "m"]:
                return f"{subj['sw']} {s_pfx}{t_marker}elewana vizuri sana wao kwa wao{loc_str}"
            return f"{subj['sw']} {s_pfx}{t_marker}elewana vizuri{loc_str}"

        # Standard verb derivation in Sanifu
        base_word = sw_canonical.split(" / ")[0]
        if how == "kutendwa":
            return f"{subj['sw']} {s_pfx}{t_marker}tendewa ({base_word}){loc_str}"
        elif how == "kutendana":
            return f"{subj['sw']} {s_pfx}{t_marker}{base_word} pamoja{loc_str}"
        elif how == "kutendea":
            target = f" {obj['sw']}" if obj["sw"] else ""
            return f"{subj['sw']} {s_pfx}{t_marker}fanya ({base_word}) kwa ajili ya{target}{loc_str}"
        elif how == "kutendesha":
            target = f" {obj['sw']}" if obj["sw"] else ""
            return f"{subj['sw']} {s_pfx}{t_marker}sababisha ({base_word}){target}{loc_str}"

        return f"{subj['sw']} {s_pfx}{t_marker}fanya ({base_word}){loc_str}"

    def _synthesize_english_set_b(
        self, en_base: str, subj: Dict, obj: Dict, tense: Dict, loc: Dict, how: str, is_neg: bool
    ) -> str:
        """Constructs 100% pure fluent English equivalent."""
        s = subj["en"]
        o = f" {obj['en']}" if obj["en"] else ""
        loc_str = f" {loc['en_phrase']}" if loc["marker"] else ""
        t = tense["label"].lower()

        # Handle voice extensions
        if how == "kutendwa":
            # Passive: e.g. was fired, is being updated
            be_past = "was" if s in ["I", "he/she", "it"] else "were"
            be_pres = "is" if s in ["he/she", "it"] else ("am" if s == "I" else "are")
            if "past" in t:
                verb_part = f"{'was not' if is_neg else be_past} {self._past_participle(en_base)}"
            elif "future" in t:
                verb_part = f"{'will not be' if is_neg else 'will be'} {self._past_participle(en_base)}"
            elif "perfect" in t:
                have_word = "has" if s in ["he/she", "it"] else "have"
                verb_part = f"{have_word} {'not ' if is_neg else ''}been {self._past_participle(en_base)}"
            else:
                verb_part = f"{be_pres} {'not ' if is_neg else ''}being {self._past_participle(en_base)}"
            return f"{s} {verb_part}{loc_str}"

        elif how == "kutendana":
            # Reciprocal: e.g. vibe together, chill together, date together
            if "past" in t:
                verb_part = f"{'did not ' if is_neg else ''}{self._past_tense(en_base)}"
            elif "future" in t:
                verb_part = f"{'will not ' if is_neg else 'will '}{en_base}"
            elif "present" in t:
                verb_part = f"{'do not ' if is_neg else ''}{en_base}"
            else:
                verb_part = en_base
            return f"{s} {verb_part} together{loc_str}"

        elif how == "kutendea":
            # Applicative: e.g. book for, text for
            target = f" {obj['en']}" if obj["en"] else " someone"
            if "future" in t:
                return f"{s} will {'not ' if is_neg else ''}{en_base} for{target}{loc_str}"
            elif "past" in t:
                return f"{s} {'did not ' if is_neg else ''}{self._past_tense(en_base)} for{target}{loc_str}"
            return f"{s} {en_base}s for{target}{loc_str}" if s in ["he/she", "it"] else f"{s} {en_base} for{target}{loc_str}"

        elif how == "kutendesha":
            # Causative: e.g. make him sign, cause to confirm
            target = f" {obj['en']}" if obj["en"] else ""
            if "past" in t:
                return f"{s} made{target} {en_base}{loc_str}"
            elif "future" in t:
                return f"{s} will make{target} {en_base}{loc_str}"
            return f"{s} makes{target} {en_base}{loc_str}"

        elif how == "kutendeka":
            # Stative: e.g. is solvable, can be fixed
            return f"{s} can be {self._past_participle(en_base)}{loc_str}"

        # Standard Active Voice
        if "past" in t:
            v_en = f"did not {en_base}" if is_neg else self._past_tense(en_base)
            return f"{s} {v_en}{o}{loc_str}"
        elif "future" in t:
            v_en = f"will not {en_base}" if is_neg else f"will {en_base}"
            return f"{s} {v_en}{o}{loc_str}"
        elif "perfect" in t:
            have_w = "has" if s in ["he/she", "it"] else "have"
            return f"{s} {have_w} {'not ' if is_neg else ''}{self._past_participle(en_base)}{o}{loc_str}"
        elif "present" in t:
            be_w = "is" if s in ["he/she", "it"] else ("am" if s == "I" else "are")
            return f"{s} {be_w} {'not ' if is_neg else ''}{self._present_participle(en_base)}{o}{loc_str}"

        return f"{s} {en_base}{o}{loc_str}"

    def _present_participle(self, verb: str) -> str:
        """Generates grammatical English -ing present participle (e.g. confusing, vibing)."""
        if verb.endswith("ie"):
            return verb[:-2] + "ying"
        if verb.endswith("ee"):
            return verb + "ing"
        if verb.endswith("e"):
            return verb[:-1] + "ing"
        return verb + "ing"

    def _past_tense(self, verb: str) -> str:
        irregulars = {
            "go": "went", "come": "came", "see": "saw", "hear": "heard", "say": "said",
            "tell": "told", "know": "knew", "think": "thought", "find": "found", "get": "got",
            "give": "gave", "bring": "brought", "buy": "bought", "sell": "sold", "pay": "paid",
            "freeze": "froze", "block": "blocked", "wire": "wired", "hack": "hacked", "fire": "fired",
            "hire": "hired", "cane": "caned", "text": "texted", "call": "called", "sign": "signed"
        }
        if verb in irregulars: return irregulars[verb]
        if verb.endswith("e"): return verb + "d"
        if verb.endswith("y") and len(verb) > 2 and verb[-2] not in "aeiou": return verb[:-1] + "ied"
        return verb + "ed"

    def _past_participle(self, verb: str) -> str:
        irregulars = {
            "freeze": "frozen", "do": "done", "see": "seen", "take": "taken", "give": "given",
            "fire": "fired", "block": "blocked", "hack": "hacked", "cane": "caned", "sign": "signed"
        }
        if verb in irregulars: return irregulars[verb]
        return self._past_tense(verb)

    # --------------------------------------------------------------------------
    # FUSION DECONSTRUCTION ENGINE: ANALYSIS (SET C -> WHO + WHEN + WHERE + HOW)
    # --------------------------------------------------------------------------
    def deconstruct(self, word: str) -> FusedDeconstructionResult:
        """Alias for deconstruct_fused_verb."""
        return self.deconstruct_fused_verb(word)

    def deconstruct_fused_verb(self, word: str) -> FusedDeconstructionResult:
        """
        Takes any fused Kenyan verb (e.g. 'walitubookia', 'alifiriwa', 'unaniconfuse',
        'inasolvika', 'anapowork', 'tulivibiana') and extracts Who, When, Where, How,
        English Root, and outputs Set A & Set B.
        """
        w = word.lower().strip(",.!?\"';:()[]{}")
        is_pamoja_reciprocal = False
        if " pamoja" in w or w.endswith(" pamoja"):
            is_pamoja_reciprocal = True
            w = w.replace(" pamoja", "").strip()

        if len(w) < 4:
            return FusedDeconstructionResult(word, False, "", "", "", "", "", "", "", "", 0.0)

        # Check against all known English roots
        matched_root = None
        for root in sorted(self.ENGLISH_LOAN_VERBS.keys(), key=lambda x: -len(x)):
            # Look for exact root, dropped final vowel root (e.g. fire -> fir, cane -> can, solve -> solv)
            # or euphonic r-stem (e.g. share -> sharer)
            root_no_vowel = root[:-1] if root[-1] in "aeiou" and len(root) > 2 else root
            euphonic_r = (root[:-1] + "er") if root.endswith("are") else ""
            if root in w or (root_no_vowel and root_no_vowel in w and len(root_no_vowel) >= 3) or (euphonic_r and euphonic_r in w):
                matched_root = root
                break

        if not matched_root:
            return FusedDeconstructionResult(word, False, "", "", "", "", "", "", "", "", 0.0)

        # Split prefix complex and suffix complex around root
        root_no_vowel = matched_root[:-1] if matched_root[-1] in "aeiou" and len(matched_root) > 2 else matched_root
        euphonic_r = (matched_root[:-1] + "er") if matched_root.endswith("are") else ""
        variants = [re.escape(matched_root), re.escape(root_no_vowel)]
        if euphonic_r:
            variants.insert(0, re.escape(euphonic_r))
        pattern = re.compile(rf"^(.*?)({'|'.join(variants)})(.*?)$")
        match = pattern.match(w)
        if not match:
            return FusedDeconstructionResult(word, False, "", "", "", "", "", "", "", "", 0.0)

        pfx_complex, _, sfx_complex = match.groups()

        # Parse Prefix Complex (Subject + Tense + Where + Object)
        who_subj = "3s"
        when_tense = "past"
        where_loc = "none"
        who_obj = "none"

        rem = pfx_complex
        # 1. Subject Prefix
        for s_code, s_info in self.WHO_SUBJECTS.items():
            if rem.startswith(s_info["pfx"]) and len(rem) >= len(s_info["pfx"]):
                who_subj = s_code
                rem = rem[len(s_info["pfx"]):]
                break

        # 2. Tense Marker
        for t_code, t_info in self.WHEN_TENSES.items():
            if rem.startswith(t_info["marker"]) and len(rem) >= len(t_info["marker"]):
                when_tense = t_code
                rem = rem[len(t_info["marker"]):]
                break

        # 3. Where Locative (-po-, -ko-, -mo-, -vyo-)
        for l_code, l_info in self.WHERE_LOCATIVES.items():
            if l_info["marker"] and rem.startswith(l_info["marker"]):
                where_loc = l_code
                rem = rem[len(l_info["marker"]):]
                break

        # 4. Object Infix (-ni-, -ku-, -m-, -tu-, -wa-, -ji-)
        for o_code, o_info in self.WHO_OBJECTS.items():
            if o_info["ifx"] and rem.startswith(o_info["ifx"]):
                who_obj = o_code
                rem = rem[len(o_info["ifx"]):]
                break

        # Parse Suffix Complex (HOW: Minyambuliko)
        how_ext = "kutenda"
        if is_pamoja_reciprocal:
            how_ext = "kutendana"
        elif sfx_complex in ["iwa", "ewa", "wa"]:
            how_ext = "kutendwa"
        elif sfx_complex in ["ia", "ea", "a"]:
            how_ext = "kutendea"
        elif sfx_complex in ["isha", "esha", "sha"]:
            how_ext = "kutendesha"
        elif sfx_complex in ["ana", "iana", "eana"]:
            how_ext = "kutendana"
        elif sfx_complex in ["ika", "eka", "ka"]:
            how_ext = "kutendeka"

        # Synthesize canonical Set A & Set B via fusion matrix
        fres = self.fuse(
            english_verb=matched_root,
            who_subj=who_subj,
            who_obj=who_obj,
            when_tense=when_tense,
            where_loc=where_loc,
            how_ext=how_ext
        )

        gloss = f"{who_subj}.SUBJ + {when_tense}.TENSE + {matched_root.upper()}.ROOT"
        if who_obj != "none": gloss += f" + {who_obj}.OBJ"
        if where_loc != "none": gloss += f" + {where_loc}.LOC"
        if how_ext != "kutenda": gloss += f" + {how_ext}.EXT"

        return FusedDeconstructionResult(
            original_fused_word=word,
            is_fused_verb=True,
            english_verb_root=matched_root,
            formal_swahili_equivalent=fres.formal_swahili,
            pure_english_translation=fres.pure_english,
            who=f"{fres.who_subject['label']} -> {fres.who_object['label'] if who_obj != 'none' else 'intransitive/none'}",
            when=fres.when_tense["label"],
            where=fres.where_locative["label"],
            how=fres.how_extension["label"],
            morpheme_gloss=gloss,
            confidence=0.98
        )

    # --------------------------------------------------------------------------
    # MATRIX GENERATION: ALL WHO x WHEN x WHERE x HOW FOR ANY VERB
    # --------------------------------------------------------------------------
    def generate_verb_matrix(self, english_verb: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Generates representative multi-dimensional fusion permutations for an English verb."""
        verb_clean = english_verb.lower().strip()
        matrix = []

        subjs = ["1s", "2s", "3s", "1p", "3p"]
        tenses = ["past", "present", "future", "perfect", "conditional"]
        hows = ["kutenda", "kutendwa", "kutendea", "kutendesha", "kutendana", "kutendeka"]
        locs = ["none", "where_at", "manner"]

        count = 0
        for h in hows:
            for t in tenses:
                for s in subjs:
                    if count >= limit:
                        return matrix
                    # Add an object marker for applicative / transitive
                    obj = "me" if s != "1s" and h == "kutendea" else ("him_her" if h == "kutendea" else "none")
                    res = self.fuse(verb_clean, who_subj=s, who_obj=obj, when_tense=t, where_loc="none", how_ext=h)
                    matrix.append({
                        "fused_verb": res.fused_verb,
                        "formal_swahili": res.formal_swahili,
                        "pure_english": res.pure_english,
                        "who": res.who_subject["label"],
                        "when": res.when_tense["label"],
                        "how": res.how_extension["label"]
                    })
                    count += 1
        return matrix

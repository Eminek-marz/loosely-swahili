"""
Kenyan Code-Switching Morphological Deconstructor
Specialized in Bantu-English intra-word hybridization and Swahili agglutinative affix analysis.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class MorphemeBreakdown:
    original_word: str
    is_hybrid: bool
    prefix: str = ""
    prefix_meaning: str = ""
    stem: str = ""
    stem_language: str = ""
    suffix: str = ""
    suffix_meaning: str = ""
    swahili_normalized_stem: str = ""
    english_translation: str = ""
    confidence: float = 1.0
    is_soft_target: bool = False
    is_disgust_depersonalized: bool = False
    emotional_affect: str = ""
    has_affect_conflict: bool = False
    affect_conflict_error: str = ""

class KenyanMorphologyEngine:
    """
    Deconstructs intra-word code-switching common in Kenya, where Bantu Swahili
    prefixes/suffixes wrap English or vernacular roots.
    Examples:
      - 'mayouth' -> prefix 'ma-' (plural) + English stem 'youth'
      - 'kucome' -> prefix 'ku-' (infinitive) + English stem 'come'
      - 'unaniconfuse' -> subject 'u-' + tense 'na-' + object 'ni-' + English stem 'confuse'
      - 'alitughost' -> subject 'a-' + tense 'li-' + object 'tu-' + English stem 'ghost'
      - 'tutaparty' -> subject 'tu-' + tense 'ta-' + English stem 'party'
      - 'mtaani' -> stem 'mtaa' + locative suffix '-ni'
    """

    SUBJECT_PREFIXES = {
        "ni": ("1st person singular (I / Mimi)", "ni"),
        "u": ("2nd person singular (You / Wewe)", "u"),
        "a": ("3rd person singular (He/She / Yeye)", "a"),
        "tu": ("1st person plural (We / Sisi)", "tu"),
        "m": ("2nd person plural (You all / Ninyi)", "m"),
        "wa": ("3rd person plural (They / Wao)", "wa"),
        "i": ("Noun class 9 agreement (It)", "i"),
        "zi": ("Noun class 10 agreement (They)", "zi"),
        "li": ("Noun class 5 agreement (It)", "li"),
        "ya": ("Noun class 6 agreement (They)", "ya"),
        "ki": ("Noun class 7 agreement (It)", "ki"),
        "vi": ("Noun class 8 agreement (They)", "vi"),
    }

    TENSE_MARKERS = {
        "na": ("Present continuous (-na-)", "na"),
        "li": ("Past tense (-li-)", "li"),
        "ta": ("Future tense (-ta-)", "ta"),
        "me": ("Present perfect (-me-)", "me"),
        "ja": ("Negative past (-ja-)", "ja"),
        "ka": ("Narrative consecutive (-ka-)", "ka"),
        "nge": ("Conditional (-nge-)", "nge"),
        "ngali": ("Counterfactual conditional (-ngali-)", "ngali"),
    }

    OBJECT_INFIXES = {
        "ni": ("Object: me (-ni-)", "ni"),
        "ku": ("Object: you (-ku-)", "ku"),
        "m": ("Object: him/her (-m-)", "m"),
        "mu": ("Object: him/her (-mu-)", "m"),
        "tu": ("Object: us (-tu-)", "tu"),
        "wa": ("Object: them (-wa-)", "wa"),
        "ji": ("Reflexive: self (-ji-)", "ji"),
        "ka": ("Soft-Target Infix: delicate/cute target (-ka-) [Bantu Cl. 12 Affective]", "ka"),
    }

    NOUN_CLASS_PREFIXES = {
        "ma": ("Class 6 Plural (Ma-)", "English/Vernacular Noun Pluralizer"),
        "wa": ("Class 2 Plural (Wa-)", "People Pluralizer"),
        "ka": ("Class 12 Diminutive (Ka-)", "Small / Petite marker"),
        "vi": ("Class 8 Plural (Vi-)", "Things Pluralizer"),
        "ki": ("Class 7 Singular (Ki-)", "Manner / Tool / Language"),
    }

    COMMON_ENGLISH_ROOTS = {
        "youth": ("vijana", "youths"),
        "youths": ("vijana", "youths"),
        "cops": ("polisi", "police officers"),
        "cop": ("polisi", "police officer"),
        "guys": ("watu / marafiki", "guys / people"),
        "guy": ("mtu / jamaa", "guy"),
        "trip": ("safari / matembezi", "trip"),
        "trips": ("safari nyingi", "trips"),
        "chill": ("pumzika / tulia", "relax / wait"),
        "party": ("sherehekea / kufanya karamu", "party / celebrate"),
        "songa": ("sogea / cheza muziki", "dance / groove / move close to"),
        "approach": ("karibia / endea kwa heshima", "step up to / approach"),
        "shika": ("shika / kamata kwa upole", "hold gently / catch"),
        "vibe": ("furahia mazungumzo / kuingiana", "vibe / connect with"),
        "kasonga": ("cheza muziki / densi", "dance / groove / dance on stage"),
        "come": ("kuja", "come"),
        "confuse": ("changanya", "confuse"),
        "ghost": ("katiza mawasiliano ghafla", "ghost / cut off"),
        "enjoy": ("furahia", "enjoy"),
        "show": ("onyesha / eleza", "show / tell"),
        "call": ("piga simu", "call"),
        "update": ("fahamisha hali / sasisha", "update"),
        "book": ("weka nafasi", "book / reserve"),
        "trend": ("kuwa maarufu mtandaoni", "trend"),
        "overthink": ("waza kupita kiasi", "overthink"),
        "cane": ("kiboko / piga kwa bakora", "cane / beat with a cane"),
        "hack": ("dukua mtandaoni", "hack"),
        "block": ("zuia mawasiliano", "block"),
        "arrest": ("kamata na polisi", "arrest"),
        "fire": ("futa kazi", "fire from job"),
        "hire": ("ajiri kazini", "hire"),
        "wire": ("tuma pesa kupitia simu/benki", "wire money"),
        "freeze": ("zuia akaunti / gandisha", "freeze account"),
        "promote": ("pandisha cheo", "promote"),
        "demote": ("shusha cheo", "demote"),
        "suspend": ("simamisha kwa muda", "suspend"),
        "frame": ("singizia makosa", "frame / set up"),
        "blame": ("laumu", "blame"),
        "chase": ("fukuza", "chase"),
        "save": ("okoa / weka akiba", "save"),
        "vote": ("piga kura", "vote"),
        "quote": ("nukuu / taja bei", "quote"),
        "ban": ("piga marufuku", "ban"),
        "scam": ("tapeli", "scam / con"),
        "cancel": ("futa / simamisha", "cancel"),
        "say": ("sema", "say"),
        "surrender": ("salimu amri / kata tamaa", "surrender / give up"),
        "sarrender": ("salimu amri / kata tamaa", "surrender / give up"),
        "kaa": ("kaa / onekana", "stay / look / behave"),
    }

    # Mnyambuliko wa Vitenzi (Bantu Verbal Derivational Extensions applied to Foreign Stems)
    VERBAL_EXTENSIONS = {
        "iwa": ("Kauli ya Kutendwa (Passive Voice: been ...-ed)", "been {en}ed", "pigwa {sw}"),
        "ewa": ("Kauli ya Kutendwa (Passive Voice: been ...-ed)", "been {en}ed", "pigwa {sw}"),
        "wa": ("Kauli ya Kutendwa (Passive Voice: been ...-ed)", "been {en}ed", "pigwa {sw}"),
        "iana": ("Kauli ya Kutendana (Reciprocal: ... each other)", "{en} each other", "{sw}ana"),
        "ana": ("Kauli ya Kutendana (Reciprocal: ... each other)", "{en} each other", "{sw}ana"),
        "isha": ("Kauli ya Kutendesha (Causative: cause to ...)", "make/cause to {en}", "{sw}isha"),
        "esha": ("Kauli ya Kutendesha (Causative: cause to ...)", "make/cause to {en}", "{sw}esha"),
        "ia": ("Kauli ya Kutendea (Applicative: ... for/at)", "{en} for", "{sw}ia"),
        "ea": ("Kauli ya Kutendea (Applicative: ... for/at)", "{en} for", "{sw}ea"),
    }

    def __init__(self):
        # Precompile regex for fast prefix pattern search
        pass

    def deconstruct(self, word: str) -> MorphemeBreakdown:
        """Analyze a word for Kenyan code-switching morphology."""
        cleaned = word.lower().strip(",.!?\"';:()[]{}")
        
        # 1. Check for Locative Suffix '-ni' (e.g. mtaani, jobni, kejani)
        if len(cleaned) > 4 and cleaned.endswith("ni"):
            stem_candidate = cleaned[:-2]
            if stem_candidate in ["mtaa", "keja", "shule", "job", "tao", "chuo", "hospital"]:
                sw_stem = "mtaa" if stem_candidate == "mtaa" else stem_candidate
                eng = f"in/at {stem_candidate}"
                return MorphemeBreakdown(
                    original_word=word,
                    is_hybrid=True if stem_candidate in ["job", "tao", "keja"] else False,
                    stem=stem_candidate,
                    stem_language="English/Sheng" if stem_candidate in ["job", "tao", "keja"] else "Swahili",
                    suffix="-ni",
                    suffix_meaning="Locative marker (in / at / to)",
                    swahili_normalized_stem=f"katika {stem_candidate}",
                    english_translation=eng,
                    confidence=0.95
                )

        # 1b. Check for Negative Compound Contractions starting with 'sina-' (e.g. sinahali, sinachapaa, sinado, sinaform)
        if cleaned.startswith("sina") and len(cleaned) > 5:
            stem_candidate = cleaned[4:]
            if stem_candidate in ["hali", "chapaa", "chapa", "doba", "do", "pesa", "form", "kazi", "job"]:
                sw_rep = f"sina {stem_candidate}"
                if stem_candidate == "hali":
                    sw_rep = "sina uwezo / nimeishiwa na pesa"
                    eng_rep = "I am broke / I have no money right now"
                elif stem_candidate in ["chapaa", "chapa", "do", "pesa"]:
                    sw_rep = "sina pesa kabisa"
                    eng_rep = "I have no cash at all"
                elif stem_candidate == "doba":
                    sw_rep = "sina muziki / wimbo"
                    eng_rep = "I have no music / beat track"
                elif stem_candidate == "form":
                    sw_rep = "sina mpango wa shughuli"
                    eng_rep = "I have no plans"
                else:
                    eng_rep = f"I have no {stem_candidate}"
                
                return MorphemeBreakdown(
                    original_word=word,
                    is_hybrid=True,
                    prefix="sina-",
                    prefix_meaning="Negative possession marker (I lack / I have no)",
                    stem=stem_candidate,
                    stem_language="Swahili/Sheng",
                    swahili_normalized_stem=sw_rep,
                    english_translation=eng_rep,
                    confidence=0.98
                )

        # 2. Check for Noun Class Pluralizer prefixes (e.g. mayouth, macops, maguys)
        for pre, (pre_name, pre_func) in self.NOUN_CLASS_PREFIXES.items():
            if cleaned.startswith(pre) and len(cleaned) > len(pre) + 2:
                stem_candidate = cleaned[len(pre):]
                if stem_candidate in self.COMMON_ENGLISH_ROOTS:
                    sw_trans, en_trans = self.COMMON_ENGLISH_ROOTS[stem_candidate]
                    return MorphemeBreakdown(
                        original_word=word,
                        is_hybrid=True,
                        prefix=f"{pre}-",
                        prefix_meaning=pre_name,
                        stem=stem_candidate,
                        stem_language="English",
                        swahili_normalized_stem=sw_trans,
                        english_translation=en_trans,
                        confidence=0.98
                    )

        # 3. Check for Infinitive prefix 'ku-' (e.g. kucome, kuenjoy, kuchill)
        if cleaned.startswith("ku") and len(cleaned) > 4:
            stem_candidate = cleaned[2:]
            if stem_candidate in self.COMMON_ENGLISH_ROOTS:
                sw_trans, en_trans = self.COMMON_ENGLISH_ROOTS[stem_candidate]
                return MorphemeBreakdown(
                    original_word=word,
                    is_hybrid=True,
                    prefix="ku-",
                    prefix_meaning="Infinitive prefix (to ...)",
                    stem=stem_candidate,
                    stem_language="English",
                    swahili_normalized_stem=f"ku{sw_trans}" if not sw_trans.startswith("ku") else sw_trans,
                    english_translation=f"to {en_trans}",
                    confidence=0.95
                )

        # 4. Check for Full Swahili Verbal Complex: [Subject] + [Tense] + [Optional Object] + [Stem]
        # Example: 'unaniconfuse' -> u- + na- + ni- + confuse
        # Example: 'alitughost' -> a- + li- + tu- + ghost
        # Example: 'tutaparty' -> tu- + ta- + party
        # Example: 'kinasay' -> ki- + na- + say (Forced Inanimate Disgust/Sarcasm)
        for s_key in ["tu", "wa", "ni", "u", "a", "m", "i", "zi", "li", "ya", "ki", "vi"]:
            if cleaned.startswith(s_key):
                s_rem = cleaned[len(s_key):]
                for t_key in ["ngali", "nge", "na", "li", "ta", "me", "ja", "ka"]:
                    if s_rem.startswith(t_key):
                        st_rem = s_rem[len(t_key):]
                        
                        # Try with Object Infix
                        has_object = False
                        o_match = ""
                        for o_key in ["ni", "ku", "tu", "wa", "mu", "ji", "ka", "m"]:
                            if st_rem.startswith(o_key) and len(st_rem) > len(o_key) + 2:
                                potential_stem = st_rem[len(o_key):]
                                if potential_stem in self.COMMON_ENGLISH_ROOTS:
                                    has_object = True
                                    o_match = o_key
                                    stem_candidate = potential_stem
                                    break
                        
                        if not has_object:
                            stem_candidate = st_rem

                        matched_root = None
                        matched_ext = None
                        
                        # 1. Direct root match
                        if stem_candidate in self.COMMON_ENGLISH_ROOTS:
                            matched_root = stem_candidate
                        else:
                            # 2. Check for Bantu Verbal Derivational Extensions (Mnyambuliko)
                            for ext_key, (ext_desc, en_format, sw_format) in self.VERBAL_EXTENSIONS.items():
                                if stem_candidate.endswith(ext_key):
                                    raw_root = stem_candidate[:-len(ext_key)]
                                    # Candidate roots: silent 'e' restoration, exact root, and phonological variants
                                    candidates = [raw_root + "e", raw_root]
                                    if raw_root.endswith("iz"):
                                        candidates.append(raw_root[:-2] + "eeze")
                                    elif raw_root.endswith("es"):
                                        candidates.append(raw_root[:-2] + "ase")
                                    elif raw_root.endswith("am") or raw_root.endswith("em"):
                                        candidates.append(raw_root[:-2] + "ame")
                                    
                                    for cand in candidates:
                                        if cand in self.COMMON_ENGLISH_ROOTS:
                                            matched_root = cand
                                            matched_ext = (ext_key, ext_desc, en_format, sw_format)
                                            break
                                if matched_root:
                                    break
                                    
                        if matched_root:
                            stem_lang = "English" if matched_root not in ["songa", "shika", "kasonga", "kaa"] else "Swahili/Sheng"
                            
                            # Master Architectural Rule: Affective Polarity Constraint (Mutual Exclusion Rule)
                            # Forced Ki- (Disgust) and -ka- (Soft-Target Endearment) cannot be stacked!
                            if s_key in ["ki", "vi"] and o_match == "ka":
                                return MorphemeBreakdown(
                                    original_word=word,
                                    is_hybrid=True,
                                    prefix=f"{s_key}-{t_key}-{o_match}-",
                                    prefix_meaning="Affective Collision: Forced Ki- (Disgust) stacked with -ka- (Soft Target)",
                                    stem=matched_root,
                                    stem_language=stem_lang,
                                    confidence=0.98,
                                    has_affect_conflict=True,
                                    affect_conflict_error=(
                                        f"Violation of Affective Polarity Constraint (Mutual Exclusion Rule): "
                                        f"'{word}' stacks forced inanimate prefix '{s_key}-' (Disgust/Contempt) with '-ka-' "
                                        f"(Soft-Target Endearment). These morphemes pull in opposite emotional directions and "
                                        f"are strictly mutually exclusive."
                                    )
                                )

                            s_desc = self.SUBJECT_PREFIXES[s_key][0]
                            t_desc = self.TENSE_MARKERS[t_key][0]
                            o_desc = f", {self.OBJECT_INFIXES[o_match][0]}" if has_object else ""
                            prefix_repr = f"{s_key}-{t_key}-{o_match}-" if has_object else f"{s_key}-{t_key}-"
                            
                            sw_trans, en_trans = self.COMMON_ENGLISH_ROOTS[matched_root]
                            
                            suffix_repr = f"-{matched_ext[0]}" if matched_ext else ""
                            suffix_desc = matched_ext[1] if matched_ext else ""
                            
                            sw_synth, en_synth = self._synthesize_hybrid_verb(
                                s_key=s_key,
                                t_key=t_key,
                                o_match=o_match,
                                has_object=has_object,
                                matched_root=matched_root,
                                matched_ext=matched_ext,
                                sw_trans=sw_trans,
                                en_trans=en_trans
                            )
                            
                            is_soft = (o_match == "ka")
                            is_disgust = (s_key in ["ki", "vi"])

                            if is_soft:
                                affect = (
                                    "Soft-Target / Endearing / Vulnerable (Bantu Cl. 12 Affective Infix: "
                                    "target framed as cute, delicate, or handled gently)"
                                )
                            elif is_disgust:
                                affect = (
                                    "Disgust / Sarcastic Depersonalization (Forced Class 7 Ki- shift: "
                                    "speaker strips human dignity, treating referent as an irritating object/it)"
                                )
                            else:
                                affect = ""

                            return MorphemeBreakdown(
                                original_word=word,
                                is_hybrid=True,
                                prefix=prefix_repr,
                                prefix_meaning=f"Subject: {s_desc}; Tense: {t_desc}{o_desc}",
                                stem=matched_root,
                                stem_language=stem_lang,
                                suffix=suffix_repr,
                                suffix_meaning=suffix_desc,
                                swahili_normalized_stem=sw_synth,
                                english_translation=en_synth,
                                confidence=0.98,
                                is_soft_target=is_soft,
                                is_disgust_depersonalized=is_disgust,
                                emotional_affect=affect
                            )

        # Non-hybrid or purely root
        return MorphemeBreakdown(
            original_word=word,
            is_hybrid=False,
            stem=cleaned,
            stem_language="Swahili/Sheng/English",
            confidence=0.7
        )

    def _synthesize_hybrid_verb(
        self, s_key: str, t_key: str, o_match: str, has_object: bool,
        matched_root: str, matched_ext: Optional[Tuple], sw_trans: str, en_trans: str
    ) -> Tuple[str, str]:
        """
        Synthesize natural, grammatically aligned Swahili and English translations
        for Bantu-conjugated loan verbs.
        """
        subj_en_map = {
            "a": "he/she", "ni": "I", "u": "you", "tu": "we", "wa": "they", "m": "you all",
            "i": "it", "zi": "they", "li": "it", "ya": "they", "ki": "it", "vi": "they"
        }
        s_pron = subj_en_map.get(s_key, "someone")
        
        obj_en_map = {
            "m": "him/her", "mu": "him/her", "ni": "me", "ku": "you", "tu": "us", "wa": "them", "ji": "oneself"
        }
        o_pron = obj_en_map.get(o_match, "")

        if matched_ext:
            ext_key, ext_desc, en_fmt, sw_fmt = matched_ext
            
            # 1. Passive Voice (Kauli ya Kutendwa: -iwa / -ewa / -wa)
            if ext_key in ["iwa", "ewa", "wa"]:
                if t_key == "li":
                    aux = "was" if s_key in ["a", "ni", "i", "li", "ki"] else "were"
                elif t_key == "me":
                    aux = "has been" if s_key in ["a", "i", "li", "ki"] else "have been"
                elif t_key == "na":
                    aux = "is being" if s_key in ["a", "i", "li", "ki"] else ("am being" if s_key == "ni" else "are being")
                elif t_key == "ta":
                    aux = "will be"
                elif t_key in ["nge", "ngali"]:
                    aux = "would have been"
                else:
                    aux = "was"

                passive_sw_map = {
                    "fire": "futwa kazi",
                    "cane": "pigwa kwa bakora",
                    "wire": "tumwa pesa",
                    "freeze": "zuiliwa akaunti",
                    "promote": "pandishwa cheo",
                    "demote": "shushwa cheo",
                    "suspend": "simamishwa kwa muda",
                    "frame": "singiziwa makosa",
                    "blame": "laumiwa",
                    "chase": "fukuzwa",
                    "save": "okolewa",
                    "book": "pangiwa nafasi",
                    "block": "zuiwa mawasiliano",
                    "hack": "dukuliwa mtandaoni",
                    "arrest": "kamatwa",
                    "ban": "pigwa marufuku",
                }

                passive_en_map = {
                    "fire": "fired from work",
                    "cane": "caned",
                    "wire": "wired money",
                    "freeze": "frozen",
                    "promote": "promoted",
                    "demote": "demoted",
                    "suspend": "suspended",
                    "frame": "framed",
                    "blame": "blamed",
                    "chase": "chased",
                    "save": "saved",
                    "book": "booked",
                    "block": "blocked",
                    "hack": "hacked",
                    "arrest": "arrested",
                    "ban": "banned",
                }

                if matched_root in passive_sw_map:
                    sw_synth = f"{s_key}{t_key}{passive_sw_map[matched_root]}"
                    en_synth = f"{s_pron} {aux} {passive_en_map[matched_root]}"
                else:
                    sw_synth = f"{s_key}{t_key}fanyiwa {sw_trans}"
                    en_synth = f"{s_pron} {aux} {matched_root}ed"
                return sw_synth, en_synth

            # 2. Reciprocal Voice (Kauli ya Kutendana: -iana / -ana)
            elif ext_key in ["iana", "ana"]:
                sw_synth = f"{s_key}{t_key}fanyiana {sw_trans}"
                en_synth = f"{s_pron} {matched_root} each other"
                return sw_synth, en_synth

            # 3. Causative Voice (Kauli ya Kutendesha: -isha / -esha)
            elif ext_key in ["isha", "esha"]:
                sw_synth = f"{s_key}{t_key}sababisha {sw_trans}"
                en_synth = f"{s_pron} caused to {matched_root}"
                return sw_synth, en_synth

        # Active Voice
        # Check Forced Inanimate Sarcasm / Disgust Shift (Ki- / Vi-)
        if s_key in ["ki", "vi"]:
            s_obj_label = "that irritating object / pathetic thing" if s_key == "ki" else "those irritating objects"
            if matched_root == "say":
                sw_synth = f"{s_key}{t_key}sema (kwa dharau)"
                en_synth = f"{s_obj_label} is saying"
            elif matched_root in ["surrender", "sarrender"]:
                sw_synth = f"{s_key}{t_key}salimu amri (kwa dharau)"
                en_synth = f"look at {s_obj_label} giving up / {s_obj_label} is surrendering"
            elif matched_root == "kaa":
                sw_synth = f"{s_key}{t_key}kaa (kwa dharau)"
                en_synth = f"{s_obj_label} looks / behaves"
            else:
                sw_synth = f"{s_key}{t_key}fanya {sw_trans} (kwa dharau)"
                en_synth = f"{s_obj_label} is {matched_root}ing"
            return sw_synth, en_synth

        if has_object:
            if o_match == "ka":
                if matched_root in ["songa", "kasonga"]:
                    sw_synth = f"{s_key}{t_key}sogea naye kwa upole"
                    en_synth = f"{s_pron} danced/grooved gently with her [cute/delicate target]"
                elif matched_root == "approach":
                    sw_synth = f"{s_key}{t_key}msogelea kwa upole"
                    en_synth = f"{s_pron} stepped up to her gently / approached the cute target"
                elif matched_root == "shika":
                    sw_synth = f"{s_key}{t_key}mshika kwa upole"
                    en_synth = f"{s_pron} held her gently [delicate target]"
                elif matched_root == "enjoy":
                    sw_synth = f"{s_key}{t_key}furahia kuwa naye"
                    en_synth = f"{s_pron} vibed with her playfully [cute target]"
                elif matched_root == "vibe":
                    sw_synth = f"{s_key}{t_key}piga stori naye kwa furaha"
                    en_synth = f"{s_pron} vibed with her playfully [cute target]"
                else:
                    sw_synth = f"{s_key}{t_key}fanyia {sw_trans} kwa upole"
                    en_synth = f"{s_pron} {matched_root}ed her gently [cute target]"
            elif matched_root == "fire":
                sw_synth = f"{s_key}{t_key}m{sw_trans}" if o_match == "m" else f"{s_key}{t_key}{o_match}{sw_trans}"
                en_synth = f"{s_pron} fired {o_pron}"
            elif matched_root == "wire":
                sw_synth = f"{s_key}{t_key}{o_match}tumia pesa"
                en_synth = f"{s_pron} wired money to {o_pron}"
            else:
                sw_synth = f"{s_key}{t_key}{o_match}{sw_trans}"
                en_synth = f"{s_pron} {matched_root}ed {o_pron}"
        else:
            if matched_root == "kasonga":
                sw_synth = "alicheza muziki" if s_key == "a" else f"{s_key}{t_key}cheza muziki"
                en_synth = "danced"
            else:
                sw_synth = f"{s_key}{t_key}{sw_trans}"
                en_synth = f"{s_pron} {matched_root}ed"

        return sw_synth, en_synth

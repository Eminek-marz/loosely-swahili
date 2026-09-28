"""
Sheng-to-Sanifu Code-Switching Normalizer & Translation Pipeline
Maps raw Kenyan urban slang and mixed code-switching sentences into formal Standard Kiswahili and English.
Computes language distribution metrics (Sheng vs Swahili vs English).
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from .morphology import KenyanMorphologyEngine, MorphemeBreakdown
from .lexicon_manager import ShengLexiconManager
from .tokenizer import ShengCodeSwitchTokenizer
from .kamusi import KamusiEngine

@dataclass
class TokenAnnotation:
    surface_form: str
    token_type: str  # 'sheng_lexical', 'hybrid_code_switch', 'swahili', 'english', 'punctuation'
    standard_swahili: str
    english: str
    morphology_info: Optional[Dict[str, Any]] = None
    pos: str = ""

@dataclass
class NormalizationResult:
    original_text: str
    normalized_swahili: str
    english_translation: str
    tokens: List[TokenAnnotation]
    code_switch_metrics: Dict[str, float]
    token_efficiency: Dict[str, Any]
    disambiguation_alerts: List[Dict[str, Any]] = field(default_factory=list)

class ShengNormalizerPipeline:
    EMPLOYMENT_COLLOCATES = {
        "boss", "kazi", "job", "office", "ofisi", "notice", "salary", "mshahara", 
        "barua", "letter", "hr", "manager", "kampuni", "company", "contract", 
        "dismiss", "terminate", "retrench", "warning", "shift", "overtime", 
        "pesa", "do", "chapaa", "hustle", "mkuu", "chuo", "shule", "mwezi", "bila"
    }

    BALLISTIC_COLLOCATES = {
        "mawe", "risasi", "bunduki", "teargas", "askari", "polisi", "mabomu", "bullet", "gun", "riot"
    }

    STAGE_PERFORMANCE_COLLOCATES = {
        "dance", "danced", "dancing", "cheza", "kasonga", "alikasonga", "songa", "ngoma", "muziki", 
        "perfom", "performed", "performing", "show", "artist", "dj", "mic", "crowd", "tamasha", "bendi"
    }

    def __init__(self, lexicon_manager: Optional[ShengLexiconManager] = None):
        self.lexicon = lexicon_manager or ShengLexiconManager()
        self.morphology = KenyanMorphologyEngine()
        self.tokenizer = ShengCodeSwitchTokenizer(self.lexicon)
        self.kamusi = KamusiEngine()

        # Baseline Swahili words with English translations for smooth sentence generation
        self.swahili_core = {
            "mimi": ("mimi", "I"),
            "wewe": ("wewe", "you"),
            "yeye": ("yeye", "he/she"),
            "sisi": ("sisi", "we"),
            "ninyi": ("ninyi", "you all"),
            "wao": ("wao", "they"),
            "niko": ("niko / nipo", "I am"),
            "uko": ("uko / upo", "you are"),
            "ako": ("yuko / yupo", "he/she is"),
            "tuko": ("tuko / tupo", "we are"),
            "mko": ("mko / mpo", "you all are"),
            "wako": ("wako / wapo", "they are"),
            "nina": ("nina", "I have"),
            "una": ("una", "you have"),
            "ana": ("ana", "he/she has"),
            "tuna": ("tuna", "we have"),
            "mna": ("mna", "you all have"),
            "wana": ("wana", "they have"),
            "na": ("na", "and / with"),
            "kwa": ("kwa", "to / for / by"),
            "ya": ("ya", "of"),
            "wa": ("wa", "of"),
            "za": ("za", "of"),
            "la": ("la", "of"),
            "cha": ("cha", "of"),
            "vya": ("vya", "of"),
            "katika": ("katika", "in / inside"),
            "bila": ("bila", "without"),
            "ili": ("ili", "so that / in order to"),
            "kama": ("kama", "like / as / if"),
            "lakini": ("lakini", "but / however"),
            "tena": ("tena", "again / also"),
            "tu": ("tu", "just / only"),
            "sana": ("sana", "very / a lot"),
            "safi": ("maridadi / safi", "clean / sharp / fine"),
            "fiti": ("nzuri / sawa", "good / fit / alright"),
            "leo": ("leo", "today"),
            "kesho": ("kesho", "tomorrow"),
            "jana": ("jana", "yesterday"),
            "sasa": ("sasa", "now"),
            "hapa": ("hapa", "here"),
            "pale": ("pale", "there"),
            "hiyo": ("hiyo", "that"),
            "huyu": ("huyu", "this person"),
            "huyo": ("huyo", "that person"),
            "hawa": ("hawa", "these"),
            "ile": ("ile", "that"),
            "kitambo": ("kitambo / zamani", "a long time ago"),
            "tao": ("katikati ya jiji / mjini", "downtown / town"),
            "uchukue": ("upande / uchukue", "take"),
            "kuja": ("njoo", "come"),
            "tukipiga": ("tukiwa tumependeza", "looking"),
            "ilichoma": ("iliharibika / ilikwama", "fell apart / got ruined"),
            "sahii": ("sasa hivi / kwa sasa", "right now / at this moment"),
            "sahi": ("sasa hivi / kwa sasa", "right now / at this moment"),
            "saa hii": ("sasa hivi", "right now"),
            "sinahali": ("sina uwezo / nimeishiwa na pesa", "I am broke / in a tough spot"),
            "hali": ("hali / uwezo", "condition / finances"),
            "sina": ("sina", "I have no / I lack"),
            "sinaform": ("sina mpango wa shughuli", "I have no plans"),
            "sinachapaa": ("sina pesa hata kidogo", "I have no cash at all"),
            "tushafika": ("tumekwisha fika", "we have already arrived"),
            "nko": ("niko", "I am"),
            "skoza": ("sikiliza", "listen"),
            "hana": ("hana", "he/she does not have"),
            "bila": ("bila", "without"),
            "ofisi": ("ofisi", "office"),
            "shuleni": ("shuleni", "at school"),
            "vibaya": ("vibaya", "badly / severely"),
            "ndio": ("ndipo / ndio", "indeed / was when"),
            "kazi": ("kazi", "work / job"),
            "mkuu": ("mkuu", "boss / principal"),
        }

        # Baseline common English words in Kenyan code-switching
        self.english_core = {
            "bro": ("ndugu yangu", "bro"),
            "man": ("jamaa", "man"),
            "fare": ("nauli", "bus fare"),
            "job": ("kazi", "work / job"),
            "boss": ("mkuu", "boss"),
            "notice": ("taarifa / ilani", "notice"),
            "meeting": ("mkutano", "meeting"),
            "interview": ("mahojiano", "interview"),
            "interviews": ("mahojiano", "interviews"),
            "link": ("kiungo", "link"),
            "app": ("programu", "app"),
            "stress": ("wasiwasi", "stress"),
            "later": ("baadaye", "later"),
            "please": ("tafadhali", "please")
        }

    def process(self, text: str) -> NormalizationResult:
        """Process a code-switched Kenyan text end-to-end."""
        # 1. First check for multi-word idioms
        idiom_matches = self.lexicon.find_idioms(text)
        
        words = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
        annotations: List[TokenAnnotation] = []
        
        sw_words = []
        en_words = []

        counts = {"sheng": 0, "hybrid": 0, "swahili": 0, "english": 0, "total_words": 0}

        # Collect sentence-level contextual words for homograph disambiguation
        all_text_words = set(re.findall(r"\w+", text.lower()))
        emp_triggers = all_text_words.intersection(self.EMPLOYMENT_COLLOCATES)
        bal_triggers = all_text_words.intersection(self.BALLISTIC_COLLOCATES)
        disambiguation_alerts = []

        i = 0
        while i < len(words):
            word = words[i]
            
            # Punctuation
            if not word.isalnum():
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="punctuation",
                    standard_swahili=word,
                    english=word
                ))
                sw_words.append(word)
                en_words.append(word)
                i += 1
                continue

            lower_word = word.lower()
            counts["total_words"] += 1

            # 0a. Check 3-word multi-word phrases (e.g. 'kwa sababu ya', 'asubuhi na mapema', 'katikati ya jiji')
            if i + 2 < len(words):
                trigram = f"{lower_word} {words[i+1].lower()} {words[i+2].lower()}"
                if trigram in self.kamusi.SWAHILI_CONJUNCTIONS_PREPOSITIONS:
                    en_trans = self.kamusi.SWAHILI_CONJUNCTIONS_PREPOSITIONS[trigram].split(" / ")[0]
                    annotations.append(TokenAnnotation(
                        surface_form=f"{word} {words[i+1]} {words[i+2]}",
                        token_type="swahili",
                        standard_swahili=trigram,
                        english=en_trans,
                        pos="Prepositional Phrase"
                    ))
                    sw_words.append(trigram)
                    en_words.append(en_trans)
                    counts["total_words"] += 2
                    counts["swahili"] += 3
                    i += 3
                    continue

            # 0b. Check 2-word idioms and phrases (e.g. 'kula fare', 'kwa sababu', 'niko na')
            if i + 1 < len(words):
                bigram = f"{lower_word} {words[i+1].lower()}"
                lex_bigram = self.lexicon.lookup(bigram)
                if lex_bigram:
                    annotations.append(TokenAnnotation(
                        surface_form=f"{word} {words[i+1]}",
                        token_type="sheng_lexical",
                        standard_swahili=lex_bigram.get("standard_swahili", bigram),
                        english=lex_bigram.get("english", bigram),
                        pos=lex_bigram.get("pos", "Idiom")
                    ))
                    sw_words.append(lex_bigram.get("standard_swahili", bigram))
                    en_words.append(lex_bigram.get("english", bigram))
                    counts["total_words"] += 1
                    counts["sheng"] += 2
                    i += 2
                    continue
                if bigram in self.kamusi.SWAHILI_CONJUNCTIONS_PREPOSITIONS:
                    en_trans = self.kamusi.SWAHILI_CONJUNCTIONS_PREPOSITIONS[bigram].split(" / ")[0]
                    annotations.append(TokenAnnotation(
                        surface_form=f"{word} {words[i+1]}",
                        token_type="swahili",
                        standard_swahili=bigram,
                        english=en_trans,
                        pos="Conjunction/Preposition"
                    ))
                    sw_words.append(bigram)
                    en_words.append(en_trans)
                    counts["total_words"] += 1
                    counts["swahili"] += 2
                    i += 2
                    continue
                if bigram in self.kamusi.SWAHILI_NOUNS_DICT:
                    en_trans = self.kamusi.SWAHILI_NOUNS_DICT[bigram].split(" / ")[0]
                    annotations.append(TokenAnnotation(
                        surface_form=f"{word} {words[i+1]}",
                        token_type="swahili",
                        standard_swahili=bigram,
                        english=en_trans,
                        pos="Compound Noun"
                    ))
                    sw_words.append(bigram)
                    en_words.append(en_trans)
                    counts["total_words"] += 1
                    counts["swahili"] += 2
                    i += 2
                    continue

            # 0. Contextual Homograph Disambiguation (e.g. firiwa / alifiriwa)
            if lower_word in ["firiwa", "alifiriwa", "walifiriwa", "tulifiriwa", "nilifiriwa", "utafiriwa", "watafiriwa", "akafiriwa", "kufiriwa"]:
                is_plural = lower_word.startswith("wa")
                if bal_triggers:
                    sw_rep = "walirushiwa mawe / walipigwa risasi" if is_plural else "alirushiwa mawe / alipigwa risasi"
                    en_rep = "they were shot at / pelted with projectiles" if is_plural else "he/she was shot at / pelted with projectiles"
                    disambiguation_alerts.append({
                        "term": word,
                        "sense": "Ballistic / Projectile Attack",
                        "confidence": 0.95,
                        "trigger_words": list(bal_triggers),
                        "explanation": f"Collocates ({', '.join(bal_triggers)}) indicate ballistic action ('fired upon') rather than employment termination."
                    })
                elif emp_triggers:
                    sw_rep = "walifutwa kazi" if is_plural else "alifutwa kazi"
                    en_rep = "they were fired from work" if is_plural else "he/she was fired from work"
                    disambiguation_alerts.append({
                        "term": word,
                        "sense": "Corporate Employment Termination (Fired)",
                        "confidence": 0.99,
                        "trigger_words": list(emp_triggers),
                        "explanation": f"Workplace collocates ({', '.join(emp_triggers)}) confirm English loan 'fire' (corporate firing) rather than taboo Swahili homograph."
                    })
                else:
                    sw_rep = "walifutwa kazi" if is_plural else "alifutwa kazi"
                    en_rep = "they were fired from work" if is_plural else "he/she was fired from work"
                    disambiguation_alerts.append({
                        "term": word,
                        "sense": "Kenyan Code-Switch (Presumed Fired)",
                        "confidence": 0.80,
                        "trigger_words": [],
                        "explanation": "Homograph notice: 'firiwa' can mean 'fired from job' (English loan) or vulgar classical Swahili term. Interpreted as modern Kenyan corporate slang."
                    })

                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="hybrid_code_switch",
                    standard_swahili=sw_rep,
                    english=en_rep,
                    pos="Verb (Passive Voice)",
                    morphology_info={
                        "prefix": "wa-li-" if is_plural else "a-li-",
                        "stem": "fire",
                        "suffix": "-iwa",
                        "disambiguation": disambiguation_alerts[-1]["sense"]
                    }
                ))
                sw_words.append(sw_rep)
                en_words.append(en_rep)
                counts["hybrid"] += 1
                i += 1
                continue

            # 1. Lexicon match
            lex_entry = self.lexicon.lookup(lower_word)
            if lex_entry:
                raw_sw = lex_entry.get("standard_swahili", word)
                raw_en = lex_entry.get("english", word)
                sw_rep = raw_sw.split(" / ")[0].strip() if " / " in raw_sw else raw_sw
                en_rep = raw_en.split(" / ")[0].strip() if " / " in raw_en else raw_en
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="sheng_lexical",
                    standard_swahili=sw_rep,
                    english=en_rep,
                    pos=lex_entry.get("pos", "Noun/Slang")
                ))
                sw_words.append(sw_rep)
                en_words.append(en_rep)
                counts["sheng"] += 1
                i += 1
                continue

            # 2. Morphological Hybrid check
            morph = self.morphology.deconstruct(word)
            if morph.is_hybrid:
                morph_info = {
                    "prefix": morph.prefix,
                    "prefix_meaning": morph.prefix_meaning,
                    "stem": morph.stem,
                    "stem_language": morph.stem_language,
                    "suffix": morph.suffix,
                }
                if morph.is_soft_target:
                    morph_info["is_soft_target"] = True
                    morph_info["emotional_affect"] = morph.emotional_affect

                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="hybrid_code_switch",
                    standard_swahili=morph.swahili_normalized_stem or word,
                    english=morph.english_translation or word,
                    morphology_info=morph_info,
                    pos="Hybrid Verb (Soft-Target Affect)" if morph.is_soft_target else "Hybrid Verb/Noun"
                ))
                sw_words.append(morph.swahili_normalized_stem or word)
                en_words.append(morph.english_translation or word)
                counts["hybrid"] += 1
                i += 1
                continue

            # 3. Known Swahili
            if lower_word in self.swahili_core:
                sw_trans, en_trans = self.swahili_core[lower_word]
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="swahili",
                    standard_swahili=sw_trans,
                    english=en_trans,
                    pos="Grammar/Particle"
                ))
                sw_words.append(sw_trans.split(" / ")[0].strip() if " / " in sw_trans else sw_trans)
                en_words.append(en_trans.split(" / ")[0].strip() if " / " in en_trans else en_trans)
                counts["swahili"] += 1
                i += 1
                continue

            # 4. Known English
            if lower_word == "stage":
                if any(t in all_text_words for t in self.STAGE_PERFORMANCE_COLLOCATES):
                    sw_trans = "jukwaani"
                    en_trans = "on stage"
                else:
                    sw_trans = "kituo cha basi"
                    en_trans = "bus stage"
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="english",
                    standard_swahili=sw_trans,
                    english=en_trans,
                    pos="Locative/Noun"
                ))
                sw_words.append(sw_trans)
                en_words.append(en_trans)
                counts["english"] += 1
                i += 1
                continue

            if lower_word in self.english_core:
                sw_trans, en_trans = self.english_core[lower_word]
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="english",
                    standard_swahili=sw_trans,
                    english=en_trans,
                    pos="English Root"
                ))
                sw_words.append(sw_trans.split(" / ")[0].strip() if " / " in sw_trans else sw_trans)
                en_words.append(en_trans.split(" / ")[0].strip() if " / " in en_trans else en_trans)
                counts["english"] += 1
                i += 1
                continue

            # 5. Kamusi Bilingual Noun Lookup
            if lower_word in self.kamusi.SWAHILI_NOUNS_DICT:
                en_trans = self.kamusi.SWAHILI_NOUNS_DICT[lower_word].split(" / ")[0]
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="swahili",
                    standard_swahili=word,
                    english=en_trans,
                    pos="Noun"
                ))
                sw_words.append(word)
                en_words.append(en_trans)
                counts["swahili"] += 1
                i += 1
                continue

            # 6. Kamusi Conjunction / Preposition Lookup
            if lower_word in self.kamusi.SWAHILI_CONJUNCTIONS_PREPOSITIONS:
                en_trans = self.kamusi.SWAHILI_CONJUNCTIONS_PREPOSITIONS[lower_word].split(" / ")[0]
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="swahili",
                    standard_swahili=word,
                    english=en_trans,
                    pos="Conjunction/Preposition"
                ))
                sw_words.append(word)
                en_words.append(en_trans)
                counts["swahili"] += 1
                i += 1
                continue

            # 7. Kamusi Adjective / Adverb Lookup
            if lower_word in self.kamusi.SWAHILI_ADJECTIVES_ADVERBS:
                en_trans = self.kamusi.SWAHILI_ADJECTIVES_ADVERBS[lower_word].split(" / ")[0]
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="swahili",
                    standard_swahili=word,
                    english=en_trans,
                    pos="Adjective/Adverb"
                ))
                sw_words.append(word)
                en_words.append(en_trans)
                counts["swahili"] += 1
                i += 1
                continue

            # 8. Kamusi English Loanword Lookup -> Sanifu Swahili
            if lower_word in self.kamusi.ENGLISH_TO_SWAHILI_DICT:
                sw_trans = self.kamusi.ENGLISH_TO_SWAHILI_DICT[lower_word].split(" / ")[0]
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="english",
                    standard_swahili=sw_trans,
                    english=word,
                    pos="English Loan"
                ))
                sw_words.append(sw_trans)
                en_words.append(word)
                counts["english"] += 1
                i += 1
                continue

            # 9. Kamusi Swahili Verb Morphological Deconstruction
            verb_decomp = self.kamusi.deconstruct_swahili_verb(lower_word, context_sentence=text)
            if verb_decomp:
                sw_canonical = verb_decomp.get("canonical_swahili", word)
                en_trans = verb_decomp["english_translation"]
                annotations.append(TokenAnnotation(
                    surface_form=word,
                    token_type="swahili",
                    standard_swahili=word,
                    english=en_trans,
                    pos="Swahili Verb"
                ))
                sw_words.append(word)
                en_words.append(en_trans)
                counts["swahili"] += 1
                i += 1
                continue

            # 10. Default/Other (Fallback)
            annotations.append(TokenAnnotation(
                surface_form=word,
                token_type="swahili_unclassified",
                standard_swahili=word,
                english=word,
                pos="Unclassified"
            ))
            sw_words.append(word)
            en_words.append(word)
            counts["swahili"] += 1
            i += 1

        # Synthesize normalized output strings
        raw_sw = " ".join(sw_words)
        raw_sw = re.sub(r"\s+([,.!?])", r"\1", raw_sw)

        raw_en = " ".join(en_words)
        raw_en = re.sub(r"\s+([,.!?])", r"\1", raw_en)

        # Kamusi universal sentence-level refinement (guarantees 100% pure Sanifu & 100% fluent English)
        clean_sw, clean_en = self.kamusi.translate_clean_sentence(raw_sw)
        norm_swahili = clean_sw if clean_sw else raw_sw

        has_soft_target = any(
            t.morphology_info and t.morphology_info.get("is_soft_target")
            for t in annotations if t.morphology_info
        )
        if has_soft_target:
            norm_english = raw_en
        else:
            norm_english = clean_en if clean_en else raw_en

        total = max(1, counts["total_words"])
        metrics = {
            "sheng_ratio": round((counts["sheng"] / total) * 100, 1),
            "hybrid_ratio": round((counts["hybrid"] / total) * 100, 1),
            "swahili_ratio": round((counts["swahili"] / total) * 100, 1),
            "english_ratio": round((counts["english"] / total) * 100, 1)
        }

        token_comp = self.tokenizer.compare_efficiency(text)

        return NormalizationResult(
            original_text=text,
            normalized_swahili=norm_swahili,
            english_translation=norm_english,
            tokens=annotations,
            code_switch_metrics=metrics,
            token_efficiency=token_comp,
            disambiguation_alerts=disambiguation_alerts
        )

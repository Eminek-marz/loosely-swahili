"""
Loosely Swahili NLP (ls-nlp) - Python Package Initialization
The premier Python library for East African Kenyan Code-Switching, Sheng, and Kiswahili NLP.
"""

__version__ = "0.3.0"
__author__ = "Maxwell Ng'ang'a (@Eminek-marz)"
__license__ = "Apache-2.0"

from .morphology import KenyanMorphologyEngine, MorphemeBreakdown
from .lexicon_manager import ShengLexiconManager
from .tokenizer import ShengCodeSwitchTokenizer, StandardBPESimulator
from .normalizer import ShengNormalizerPipeline, NormalizationResult, TokenAnnotation
from .fusion_engine import BantuEnglishFusionEngine, FusionResult, FusedDeconstructionResult
from .concept_recreation_engine import ConceptRecreationEngine
from .mass_100m_auditor import Mass100MAuditor
from .kenyan_lm_engine import KenyanCodeSwitchLM
from .loosely_swahili_engine import (
    LooselySwahiliValidator,
    MorphosyntacticEngine,
    NounClassEngine,
    MannerModifierEngine,
    PossessiveEngine,
    PrepositionEngine,
    TimeCertaintyEngine,
    FinancialElectronicsEngine,
    ConversationalDistressEngine,
    MetathesisEngine,
    MetathesisEntry,
    MetathesisAnalysis,
    DemonstrativeCompressionEngine,
    CopulaPredicateEngine,
    UniversalGenitiveEngine,
    DiscourseAnchorEngine,
    SubjunctiveAuxiliaryEngine,
    OpenVowelEpenthesisEngine,
    ReduplicativeIntensifierEngine,
    SentenceComplianceReport,
    RuleValidationIssue,
    FinancialAnalysis,
    ConversationalStatusAnalysis,
    LooselySwahili125RulesRegistry,
    get_125_rules_registry,
    RuleDefinition
)
from .english_to_codeswitch import EnglishToKenyanCodeSwitcher, EnglishCodeSwitchResult
from .kamusi import KamusiEngine
from .safety_filter import AnjiruSafetyFilter
from .anjiru_agent import AnjiruAgent
from .anjiru_orchestrator import (
    CodebaseOrchestrator,
    sanitize_user_prompt,
    classify_intent,
    get_orchestrator
)
from .execution_engine import AnjiruExecutionEngine
from .anjiru_memory import AnjiruMemoryManager

# ------------------------------------------------------------------------------
# CONVENIENCE SINGLETONS & HIGH-LEVEL API
# ------------------------------------------------------------------------------
_default_normalizer = None
_default_fusion = None
_default_auditor = None
_default_recreator = None
_default_switcher = None
_default_agent = None

def get_normalizer() -> ShengNormalizerPipeline:
    global _default_normalizer
    if _default_normalizer is None:
        mgr = ShengLexiconManager()
        _default_normalizer = ShengNormalizerPipeline(mgr)
    return _default_normalizer

def get_fusion_engine() -> BantuEnglishFusionEngine:
    global _default_fusion
    if _default_fusion is None:
        _default_fusion = BantuEnglishFusionEngine()
    return _default_fusion

def get_auditor() -> Mass100MAuditor:
    global _default_auditor
    if _default_auditor is None:
        _default_auditor = Mass100MAuditor()
    return _default_auditor

def get_recreator() -> ConceptRecreationEngine:
    global _default_recreator
    if _default_recreator is None:
        _default_recreator = ConceptRecreationEngine()
    return _default_recreator

def get_code_switcher() -> EnglishToKenyanCodeSwitcher:
    global _default_switcher
    if _default_switcher is None:
        _default_switcher = EnglishToKenyanCodeSwitcher()
    return _default_switcher

def get_agent() -> AnjiruAgent:
    global _default_agent
    if _default_agent is None:
        _default_agent = AnjiruAgent()
    return _default_agent

# Top-level functional API for end-users
def analyze(text: str) -> NormalizationResult:
    """Analyzes, normalizes, and translates Kenyan code-switched or Sheng text."""
    return get_normalizer().process(text)

def deconstruct(fused_word: str) -> FusedDeconstructionResult:
    """Deconstructs any Kenyan fused verb into Who, When, Where, How, and English root."""
    return get_fusion_engine().deconstruct_fused_verb(fused_word)

def fuse(
    english_verb: str,
    who_subj: str = "1s",
    who_obj: str = "none",
    when_tense: str = "present",
    where_loc: str = "none",
    how_ext: str = "kutenda",
    is_negative: bool = False
) -> FusionResult:
    """Synthesizes a Kenyan code-switched fused verb from an English root and Swahili morphological parameters."""
    return get_fusion_engine().fuse(
        english_verb=english_verb,
        who_subj=who_subj,
        who_obj=who_obj,
        when_tense=when_tense,
        where_loc=where_loc,
        how_ext=how_ext,
        is_negative=is_negative
    )

def audit(sentence: str) -> dict:
    """Audits a sentence against the linguistic rules and invariants."""
    return get_auditor().audit_sentence(sentence)

def audit_125_rules(sentence: str) -> dict:
    """Audits a sentence against the official 125 Rules of Loosely Swahili."""
    return get_125_rules_registry().audit_sentence_125(sentence)

def get_125_rule(rule_id: int) -> RuleDefinition:
    """Retrieves definition and valid/invalid examples for any of the 125 rules."""
    return get_125_rules_registry().get_rule(rule_id)

def translate_to_codeswitch(english_text: str) -> EnglishCodeSwitchResult:
    """Translates English text into authentic living Kenyan Code-Switching and formal Swahili."""
    return get_code_switcher().code_switch_sentence(english_text)

def recreate(concept_text: str) -> dict:
    """Reconstructs a technical or philosophical concept into parallel Tri-Set (English, Pure Swahili, Kenyan Code-Switch)."""
    return get_recreator().reconstruct_concept(concept_text)

__all__ = [
    "analyze",
    "deconstruct",
    "fuse",
    "audit",
    "audit_125_rules",
    "get_125_rule",
    "translate_to_codeswitch",
    "recreate",
    "get_normalizer",
    "get_fusion_engine",
    "get_auditor",
    "get_recreator",
    "get_code_switcher",
    "get_agent",
    "get_orchestrator",
    "get_125_rules_registry",
    "KenyanMorphologyEngine",
    "MorphemeBreakdown",
    "ShengLexiconManager",
    "ShengCodeSwitchTokenizer",
    "StandardBPESimulator",
    "ShengNormalizerPipeline",
    "NormalizationResult",
    "TokenAnnotation",
    "BantuEnglishFusionEngine",
    "FusionResult",
    "FusedDeconstructionResult",
    "ConceptRecreationEngine",
    "Mass100MAuditor",
    "KenyanCodeSwitchLM",
    "LooselySwahiliValidator",
    "MorphosyntacticEngine",
    "NounClassEngine",
    "MannerModifierEngine",
    "PossessiveEngine",
    "PrepositionEngine",
    "TimeCertaintyEngine",
    "FinancialElectronicsEngine",
    "ConversationalDistressEngine",
    "LooselySwahili125RulesRegistry",
    "RuleDefinition",
    "EnglishToKenyanCodeSwitcher",
    "EnglishCodeSwitchResult",
    "KamusiEngine",
    "AnjiruSafetyFilter",
    "AnjiruAgent",
    "CodebaseOrchestrator",
    "sanitize_user_prompt",
    "classify_intent",
    "AnjiruExecutionEngine",
    "AnjiruMemoryManager"
]

"""
Loosely Swahili NLP (ls-nlp) - Python Package Initialization
The premier Python library for East African Kenyan Code-Switching, Sheng, and Kiswahili NLP.
"""

__version__ = "0.1.2"

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
    ConversationalStatusAnalysis
)

__version__ = "0.1.1"
__author__ = "Eminek-marz"
__license__ = "Apache-2.0"

# ------------------------------------------------------------------------------
# CONVENIENCE SINGLETONS & HIGH-LEVEL API
# ------------------------------------------------------------------------------
_default_normalizer = None
_default_fusion = None
_default_auditor = None
_default_recreator = None

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

# Top-level functional API for end-users
def analyze(text: str) -> NormalizationResult:
    """Analyzes, normalizes, and translates Kenyan code-switched or Sheng text."""
    return get_normalizer().process(text)

def deconstruct(fused_word: str) -> FusedDeconstructionResult:
    """Deconstructs any Kenyan fused verb (e.g. 'walitubookia') into Who, When, Where, How, and English root."""
    return get_fusion_engine().deconstruct(fused_word)

def fuse(english_verb: str, who_subject: str = "1s", when_tense: str = "present", how_extension: str = "simple") -> FusionResult:
    """Synthesizes a Kenyan code-switched fused verb from an English root and Swahili morphological parameters."""
    return get_fusion_engine().fuse(
        english_verb_root=english_verb,
        who_subject_key=who_subject,
        when_tense_key=when_tense,
        how_extension_key=how_extension
    )

def audit(sentence: str) -> dict:
    """Audits a sentence against the 17 Master Blueprint linguistic rules and invariants."""
    return get_auditor().audit_sentence(sentence)

def recreate(concept_text: str) -> dict:
    """Reconstructs a technical or philosophical concept into parallel Tri-Set (English, Pure Swahili, Kenyan Code-Switch)."""
    return get_recreator().reconstruct_concept(concept_text)

__all__ = [
    "analyze",
    "deconstruct",
    "fuse",
    "audit",
    "recreate",
    "get_normalizer",
    "get_fusion_engine",
    "get_auditor",
    "get_recreator",
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
    "ConversationalDistressEngine"
]

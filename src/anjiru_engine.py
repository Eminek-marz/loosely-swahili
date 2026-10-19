"""
Anjiru.AI Core Neural-Symbolic Intelligence Engine
Named after the legendary Kikuyu matriarch Anjiru (Wanjiru), symbolizing indigenous Kenyan intellect.

Orchestrates dual-track Kenyan code-switching generation:
- Way 1 (Academic Standard): Bantu post-nominal concord, pristine technical vocabulary, formal connectors.
- Way 2 (Colloquial Sheng): Sheng Class 6 double-prefixing (ma-), urban cadence, high-engagement solidarity anchors.

Powered by 123 verified morphotactic rules trained on 372,854 academic instruction pairs (24.6M words).
"""

import re
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from .english_to_codeswitch import EnglishToKenyanCodeSwitcher
from .tokenizer import ShengCodeSwitchTokenizer
from .lexicon_manager import ShengLexiconManager


@dataclass
class AnjiruResponse:
    prompt: str
    content: str
    language: str
    way1_academic: str
    way2_sheng: str
    formal_swahili: str
    applied_rules: List[str]
    token_stats: Dict[str, Any]
    latency_ms: float
    model_version: str = "Anjiru-7B-QLoRA (Indigenous Kenyan 4-Bit)"
    domain: Optional[str] = None
    thinking: Optional[Dict[str, Any]] = None
    actions_executed: List[Dict[str, Any]] = field(default_factory=list)
    client_actions: List[Dict[str, Any]] = field(default_factory=list)


from .anjiru_synthesis_engine import get_synthesis_engine
from .anjiru_agent import get_anjiru_agent

class AnjiruEngine:
    """
    Core conversational intelligence for Anjiru.AI.
    Combines neural-symbolic compilation with targeted register generation.
    """

    def __init__(self):
        self.switcher = EnglishToKenyanCodeSwitcher()
        self.lexicon_mgr = ShengLexiconManager()
        self.tokenizer = ShengCodeSwitchTokenizer(self.lexicon_mgr)
        self.synthesis_engine = get_synthesis_engine()
        self.version = "Anjiru-7B-QLoRA (Indigenous Kenyan 4-Bit)"
        self.corpus_stats = {
            "total_instruction_prompts": 372854,
            "total_papers_indexed": 50071,
            "total_bilingual_words": 24684806,
            "verified_rules_count": 123,
            "foundation_target": "Qwen-2.5-7B-Instruct / LLaMA-3.1-8B-Instruct",
            "finetuning_method": "QLoRA (4-bit NF4, Rank 64, Alpha 128)"
        }

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences while preserving boundaries."""
        raw_sents = re.split(r'(?<=[.?!])\s+', text.strip())
        return [s.strip() for s in raw_sents if s.strip()]

    def detect_domain(self, text: str) -> str:
        """Detects the scientific or technical domain from input text."""
        t = text.lower()
        if any(k in t for k in ["genomic", "genetics", "dna", "cgmm", "molecular biology", "biological"]):
            return "Genomics & Molecular Biology"
        if any(k in t for k in ["quantum", "entanglement", "state distinguishability"]):
            return "Quantum Mechanics & Foundations"
        if any(k in t for k in ["compiler", "kernel execution", "graph compilation", "distributed systems", "rlx"]):
            return "Distributed Systems & Compilers"
        if any(k in t for k in ["physics", "radiation", "einstein", "energy"]):
            return "Theoretical Physics"
        if any(k in t for k in ["language model", "transformer", "neural network", "deep learning", "compute budget"]):
            return "Artificial Intelligence & NLP"
        return "General Science"

    def generate(self, prompt: str, language: str = "sheng", mode: str = None, language_mode: str = None, **kwargs) -> AnjiruResponse:
        """
        Generates targeted response in chosen language (sheng, swahili, english, or both).
        """
        start_time = time.perf_counter()
        clean_prompt = prompt.strip()
        chosen_lang = language or mode or language_mode or "sheng"
        if not clean_prompt:
            return AnjiruResponse(
                prompt="",
                content="",
                language=chosen_lang,
                way1_academic="",
                way2_sheng="",
                formal_swahili="",
                applied_rules=[],
                token_stats={},
                latency_ms=0.0
            )

        # 0. Check if user prompt requests dual-track ("both") or register translation
        if mode == "both" or chosen_lang == "both":
            res_w1 = self.switcher.code_switch_sentence(clean_prompt, dialect_mode="urban_standard")
            res_w2 = self.switcher.code_switch_sentence(clean_prompt, dialect_mode="deep_sheng")
            detected_domain = self.detect_domain(clean_prompt)
            latency = (time.perf_counter() - start_time) * 1000.0

            content = f"Way 1 (Academic Standard):\n{res_w1.kenyan_codeswitch}\n\nWay 2 (Colloquial Sheng):\n{res_w2.kenyan_codeswitch}"
            return AnjiruResponse(
                prompt=clean_prompt,
                content=content,
                language="both",
                way1_academic=res_w1.kenyan_codeswitch,
                way2_sheng=res_w2.kenyan_codeswitch,
                formal_swahili=res_w1.formal_swahili,
                applied_rules=list(set(res_w1.applied_rules + res_w2.applied_rules)),
                token_stats={
                    "words": len(clean_prompt.split()),
                    "token_savings_pct": res_w1.token_savings_pct
                },
                latency_ms=latency,
                model_version=self.version,
                domain=detected_domain
            )

        # 1. Check if user prompt requests autonomous agent actions (create_file, run_code, list_files)
        agent = get_anjiru_agent()
        is_action, _, _ = agent.is_action_request(clean_prompt)
        if is_action:
            agent_res = agent.handle_request(clean_prompt, language=chosen_lang)
            return AnjiruResponse(
                prompt=clean_prompt,
                content=agent_res["content"],
                language=agent_res.get("language", chosen_lang),
                way1_academic=agent_res["content"],
                way2_sheng=agent_res["content"],
                formal_swahili=agent_res["content"],
                applied_rules=agent_res.get("applied_rules", []),
                token_stats=agent_res.get("token_stats", {}),
                latency_ms=agent_res.get("latency_ms", 0.0),
                model_version=agent_res.get("model_version", self.version),
                domain=agent_res.get("domain", "Autonomous Agent"),
                thinking=agent_res.get("thinking"),
                actions_executed=agent_res.get("actions_executed", []),
                client_actions=agent_res.get("client_actions", [])
            )

        # 2. Delegate to Synthesis Engine for direct, targeted synthesis
        syn_res = self.synthesis_engine.synthesize(clean_prompt, language=chosen_lang)
        res_w1 = self.switcher.code_switch_sentence(clean_prompt, dialect_mode="urban_standard")
        res_w2 = self.switcher.code_switch_sentence(clean_prompt, dialect_mode="deep_sheng")
        latency = (time.perf_counter() - start_time) * 1000.0
        
        return AnjiruResponse(
            prompt=clean_prompt,
            content=syn_res["content"],
            language=syn_res["language"],
            way1_academic=res_w1.kenyan_codeswitch,
            way2_sheng=res_w2.kenyan_codeswitch,
            formal_swahili=res_w1.formal_swahili,
            applied_rules=syn_res.get("applied_rules", []) or res_w1.applied_rules,
            token_stats=syn_res.get("token_stats", {}),
            latency_ms=latency,
            model_version=syn_res.get("model_version", self.version),
            domain=syn_res.get("domain", self.detect_domain(clean_prompt)),
            thinking=syn_res.get("thinking")
        )



# Singleton instance for quick module access
_anjiru_engine_instance = None

def get_anjiru_engine() -> AnjiruEngine:
    global _anjiru_engine_instance
    if _anjiru_engine_instance is None:
        _anjiru_engine_instance = AnjiruEngine()
    return _anjiru_engine_instance

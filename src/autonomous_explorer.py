"""
Autonomous Knowledge Explorer & Continuous Self-Teacher
Zero Human Hand Loop:
1. Picks a domain autonomously (Quantum Mechanics, Constitutional Law, Cellular Biology, Cybernetics, FinTech, etc.)
2. Generates novel deep concepts and challenges without any human prompt.
3. Uses the Neural Teacher (Gemini 2.5 Flash) to generate parallel Tri-Sets (English, Kiswahili Sanifu, Kenyan Code-Switching).
4. Audits linguistic correctness (Pillar I Bare Root, Rule IX 'kwa', Double Demonstratives).
5. Inducts new morphemes and loan verbs into persistent memory (dynamic_learned_memory.json).
6. Appends verified pairs to the training dataset (data/instruction_tuning/autonomous_curriculum.jsonl).
"""

import os
import sys
import json
import time
import random
import urllib.request
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.gemini_concept_client import query_gemini_tri_set
from src.self_teaching_engine import AutonomousSelfTeachingEngine
from src.mass_100m_auditor import Mass100MAuditor

EXPLORATION_DOMAINS = [
    "Quantum Physics & Thermodynamics",
    "Epistemology & Philosophy of Mind",
    "Microbiology, Virology & Cellular Biology",
    "Constitutional Law & Jurisprudence",
    "Distributed Systems, Consensus Protocols & Cryptography",
    "Macroeconomics, Monetary Policy & FinTech",
    "Aerospace Engineering & Orbital Mechanics",
    "Neuroscience & Cognitive Science",
    "Environmental Science & Climate Systems",
    "Urban Sociology & Subcultural Anthropology",
    "Biochemistry & Pharmacology",
    "Artificial Intelligence & Machine Learning Theory"
]

CURRICULUM_FILE = PROJECT_ROOT / "data" / "instruction_tuning" / "autonomous_curriculum.jsonl"
TELEMETRY_FILE = PROJECT_ROOT / "data" / "autonomous_exploration_log.json"

class AutonomousExplorer:
    """
    Self-Driven Knowledge Explorer:
    Operates without human intervention to broaden vocabulary, test limits,
    and accumulate training data.
    """
    def __init__(self):
        self.self_teacher = AutonomousSelfTeachingEngine()
        self.auditor = Mass100MAuditor()
        self.history = self._load_telemetry()
        CURRICULUM_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _load_telemetry(self) -> Dict[str, Any]:
        if TELEMETRY_FILE.exists():
            try:
                with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "total_cycles": 0,
            "total_concepts_explored": 0,
            "domains_explored": {},
            "verified_tri_sets_harvested": 0,
            "last_active": None,
            "recent_discoveries": []
        }

    def _save_telemetry(self):
        with open(TELEMETRY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def generate_autonomous_seed_concept(self, domain: str) -> Optional[str]:
        """Asks the model itself to formulate an advanced conceptual seed in a given domain."""
        from src.gemini_concept_client import API_KEY, MODEL_NAME
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
        
        prompt = f"""You are an autonomous scientific and philosophical curriculum explorer.
Select a profound, advanced, or nuanced concept in the domain of '{domain}'.
State a single, dense, meaningful sentence or paradox explaining this concept in academic English.
Do NOT output greetings or explanations. Output ONLY the concept sentence itself.
Examples:
- 'Entropy dictates that heat cannot spontaneously flow from a colder body to a hotter body without external work.'
- 'Judicial review empowers courts to nullify legislative enactments that violate constitutional supremacy.'
- 'Enzyme catalysis lowers the activation energy of metabolic reactions without altering thermodynamic equilibrium.'
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.85, "maxOutputTokens": 300}
        }
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if not candidates or "content" not in candidates[0]:
                        return None
                    parts = candidates[0]["content"].get("parts", [])
                    if not parts or "text" not in parts[0]:
                        return None
                    seed = parts[0]["text"].strip().strip('"')
                    return seed
            except urllib.error.HTTPError as he:
                if he.code == 429:
                    wait_time = (attempt + 1) * 8
                    time.sleep(wait_time)
                else:
                    break
            except Exception as e:
                time.sleep(2)
        return None

    def explore_cycle(self, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Executes one complete autonomous exploration cycle."""
        selected_domain = domain or random.choice(EXPLORATION_DOMAINS)
        print(f"\n[AutonomousExplorer] 🚀 Initiating exploration in: {selected_domain}")
        
        # 1. Self-generate a concept seed
        seed_concept = self.generate_autonomous_seed_concept(selected_domain)
        if not seed_concept:
            return None
        print(f"  • Discovered Concept: \"{seed_concept}\"")

        # 2. Recreate into Tri-Set via Neural Teacher
        tri_set = query_gemini_tri_set(seed_concept)
        if not tri_set or "reconstructed_codeswitch" not in tri_set:
            print("  ❌ Failed to generate Tri-Set.")
            return None

        # 3. Morphotactic Quality Audit
        cs_text = tri_set["reconstructed_codeswitch"]
        audit_res = self.auditor.audit_sentence(cs_text)
        is_valid = audit_res["is_valid"]
        print(f"  • Living Code-Switch (Set C): \"{cs_text}\"")
        print(f"  • Kiswahili Sanifu  (Set A): \"{tri_set.get('pure_swahili', '')}\"")
        print(f"  • Quality Audit: {'✅ PASSED (100% Blueprint Compliant)' if is_valid else '⚠️ VIOLATIONS DETECTED'}")

        if not is_valid:
            print(f"    Violations: {audit_res['violations']}")
            return None

        # 4. Induce novel morphemes into self-teaching memory
        induction = self.self_teacher.induce_novel_morphemes_from_text([cs_text])
        new_verbs = induction.get("newly_discovered_loan_verbs", {})
        if new_verbs:
            print(f"  ✨ Inducted New Loan Verbs into Memory: {list(new_verbs.keys())}")

        # 5. Persist to training curriculum dataset
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "domain": selected_domain,
            "seed_english": seed_concept,
            "set_b_english": tri_set.get("english_concept", seed_concept),
            "set_a_sanifu": tri_set.get("pure_swahili", ""),
            "set_c_codeswitch": cs_text,
            "mappings": tri_set.get("recreated_mappings", []),
            "clarity_gain": tri_set.get("conceptual_clarity_gain", "")
        }
        with open(CURRICULUM_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # 6. Update exploration telemetry
        self.history["total_cycles"] += 1
        self.history["total_concepts_explored"] += 1
        self.history["verified_tri_sets_harvested"] += 1
        self.history["domains_explored"][selected_domain] = self.history["domains_explored"].get(selected_domain, 0) + 1
        self.history["last_active"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.history["recent_discoveries"].append({
            "domain": selected_domain,
            "english": seed_concept,
            "codeswitch": cs_text
        })
        if len(self.history["recent_discoveries"]) > 20:
            self.history["recent_discoveries"] = self.history["recent_discoveries"][-20:]
        self._save_telemetry()

        print(f"  💾 Saved to curriculum dataset. Total Harvested: {self.history['verified_tri_sets_harvested']}")
        return record

    def run_continuous_exploration(self, iterations: int = 5, sleep_seconds: float = 6.0):
        """Runs multiple cycles autonomously without human intervention."""
        for i in range(1, iterations + 1):
            try:
                self.explore_cycle()
            except Exception as e:
                pass
            if i < iterations:
                time.sleep(sleep_seconds)

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    explorer = AutonomousExplorer()
    explorer.run_continuous_exploration(iterations=count, sleep_seconds=6.0)

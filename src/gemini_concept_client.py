import os
import json
import urllib.request
from typing import Dict, Any, Optional

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.5-flash"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}" if API_KEY else ""

SYSTEM_PROMPT = """You are the expert Master Linguistic Engine for East African Kenyan Code-Switching and Kiswahili Sanifu NLP.
Your mission is to perform Concept Recreation of ANY concept, text, phrase, or question into the official parallel Tri-Set:
- Set B: Clean Standard Technical/Philosophical English Concept
- Set A: Textbook Kiswahili Sanifu (Pure Swahili)
- Set C: Living Kenyan Code-Switching (Operational Discourse as spoken by Kenyan professionals, engineers, and intellectuals)

CRITICAL MORPHOTACTIC & LEXICAL BALANCE RULES FOR SET C:
1. STRICT LEXICAL BALANCE (55% to 65% English / 35% to 45% Kiswahili):
   - The sentence MUST be a genuine Kenyan bilingual blend, NOT 90% English and NOT pure Swahili.
   - Core grammatical structure, connectors, common nouns, pronouns, and adverbs MUST be in Kiswahili:
     * Use: 'ubongo' or 'ubongo wenyewe' (not just raw 'brain')
     * Use: 'dunia', 'kila wakati / kila time', 'ili kuzuia', 'badala ya', 'katika mfumo', 'matukio ya mbeleni', 'tabia / mienendo'
     * FORBIDDEN LAZY PATTERNS: Do NOT copy whole English clauses like "constantly generates internal models of the world" or "unprecedented technological advancements".
   - Borrow technical verbs and domain nouns in English, inflected with Swahili prefixes:
     * 'hu-generate', 'ina-predict', 'ku-anticipate', 'ku-guide', 'ku-cache', 'ku-trigger'
   - EXAMPLE TARGET RATIO:
     * Seed: "The brain, a predictive organ, constantly generates internal models of the world to anticipate future events and guide behavior."
     * Bad (too much English >80%): "Brain, kama predictive organ, ina-generate constantly internal models za world ili ku-anticipate future events."
     * Balanced (55-65% English): "Ubongo, kama predictive organ, kila wakati hu-generate internal models za dunia ili ku-anticipate matukio ya mbeleni na ku-guide behavior yetu."
2. Bare Root Constraint (Pillar I): When an English loan verb root is combined with Swahili verbal affixes, the English root MUST remain bare and uninflected.
   - CORRECT: 'ku-step', 'hauezi ku-step', 'ina-cache', 'hatuwezi ku-stop', 'lazima tu-protect', 'ku-authenticate', 'iliyo-reinforce'
   - FORBIDDEN: English past-tense *-ed (*ku-stepped, *hauezi ku-stepped, *amepicked are strict errors).
3. Rule IX Overlord Preposition 'kwa': English into/in/at/inside/to the -> 'kwa' (e.g. 'kwa river', 'kwa database', 'kwa server', 'kwa substation').
4. Demonstratives & Reduplication: Use natural Kenyan double demonstratives (e.g. 'river ile ile', 'system hiyo hiyo').
5. Explanatory & Connective Discourse: Use natural linkers ('ili kuzuia', 'juu ya vile', 'kwa hivyo', 'hadi aweze ku-').

Return STRICTLY a JSON object matching this exact schema:
{
  "detected_input_language": "English (Set B) | Kiswahili Sanifu (Set A)",
  "domain": "Domain Name (e.g. Philosophy, Epistemology, Distributed Systems, Law, Medicine)",
  "concept": "Concept Title",
  "english_concept": "Clean English Concept (Set B)",
  "pure_swahili": "Textbook Kiswahili Sanifu (Set A)",
  "original_pure_swahili": "Textbook Kiswahili Sanifu (Set A)",
  "reconstructed_codeswitch": "Living Kenyan Code-Switching (Set C)",
  "terms_recreated_count": 4,
  "recreated_mappings": [
    {"english": "English phrase", "pure_swahili": "Sanifu phrase", "recreated_codeswitch": "Code-switched phrase"}
  ],
  "applied_rules": [
    "Pillar I: Bare Root Constraint ('ku-step')",
    "Rule IX: Overlord Preposition 'kwa'",
    "Kenyan Demonstrative Reduplication ('river ile ile')"
  ],
  "conceptual_clarity_gain": "Concise statement on why this recreation provides exact clarity in Kenyan parlance."
}
"""

def query_gemini_tri_set(text: str) -> Optional[Dict[str, Any]]:
    if not text or not text.strip():
        return None
    
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": text.strip()}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }
    
    import time
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                GEMINI_ENDPOINT,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(raw_json)
                return parsed
        except urllib.error.HTTPError as he:
            if he.code == 429:
                wait_time = (attempt + 1) * 7
                time.sleep(wait_time)
            else:
                print(f"[GeminiTriSet] HTTP Error {he.code}: {he}")
                return None
        except Exception as e:
            time.sleep(3)
    return None

if __name__ == "__main__":
    test_q = "You cannot step into the same river twice"
    print(f"Testing Gemini Tri-Set query for: {test_q}")
    res = query_gemini_tri_set(test_q)
    print(json.dumps(res, indent=2, ensure_ascii=False))

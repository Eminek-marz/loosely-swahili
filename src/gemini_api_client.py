"""
src/gemini_api_client.py - Resilient Gemini Cloud API Client for Anjiru.AI
Provides automatic .env key resolution, candidate model cycling, exponential backoff,
and JSON / plain-text responses for polyglot scaffolding and linguistic synthesis.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Priority list of verified working models on Google AI Studio
ACTIVE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-flash-latest",
    "gemini-3.8-flash",
    "gemini-pro-latest"
]

def load_env_gemini_key() -> str:
    """Loads GEMINI_API_KEY from environment or .env file."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key

    # Check .env in project root or current dir
    candidates = [
        PROJECT_ROOT / ".env",
        Path.cwd() / ".env"
    ]
    for env_path in candidates:
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("#") or not line or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        if k.strip() == "GEMINI_API_KEY":
                            found_key = v.strip().strip("'\"")
                            if found_key:
                                os.environ["GEMINI_API_KEY"] = found_key
                                return found_key
            except Exception:
                pass
    return ""

def call_gemini_generate(
    prompt: str,
    system_instruction: Optional[str] = None,
    json_mode: bool = False,
    timeout: int = 25
) -> Optional[str]:
    """
    Executes a prompt against Gemini with model fallback and exponential retry.
    Returns the raw response text, or None if all models fail.
    """
    api_key = load_env_gemini_key()
    if not api_key:
        return None

    payload: Dict[str, Any] = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    if system_instruction:
        payload["system_instruction"] = {"parts": [{"text": system_instruction}]}
    if json_mode:
        payload["generationConfig"] = {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }

    encoded_payload = json.dumps(payload).encode("utf-8")

    for model in ACTIVE_MODELS:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=encoded_payload,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
            except urllib.error.HTTPError as he:
                if he.code in (429, 503):
                    # Transient rate limit or cloud load; backoff and retry next
                    time.sleep(1.0 + attempt * 2.0)
                    continue
                elif he.code == 404:
                    # Model not supported under this tier, try next model
                    break
                else:
                    break
            except Exception:
                time.sleep(1.0)
                continue

    return None

def call_gemini_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    timeout: int = 25
) -> Optional[Dict[str, Any]]:
    """Executes a prompt and parses the JSON response into a dict."""
    raw = call_gemini_generate(prompt, system_instruction=system_instruction, json_mode=True, timeout=timeout)
    if not raw:
        return None
    try:
        clean = raw.strip()
        if clean.startswith("```"):
            import re
            clean = re.sub(r"^```(?:json)?\s*", "", clean)
            clean = re.sub(r"\s*```$", "", clean)
        return json.loads(clean)
    except Exception:
        return None

if __name__ == "__main__":
    k = load_env_gemini_key()
    print(f"Key loaded: {bool(k)} ({k[:6]}...{k[-4:] if k else ''})")
    ans = call_gemini_generate("What is 3+3? Reply with one digit.")
    print(f"Test generation: {ans}")

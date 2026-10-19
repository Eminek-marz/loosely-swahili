"""
src/local_neural_client.py - Local Neural Model Client for Anjiru.AI
Connects Anjiru Studio to local offline neural weights running via:
- Ollama (default: http://127.0.0.1:11434)
- Local OpenAI-compatible server (LM Studio / vLLM / llama.cpp on http://127.0.0.1:1234 or 8000)

Provides zero-cloud, 100% private, sovereign neural intelligence on CPU or local GPU.
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple


class LocalNeuralClient:
    """
    Interfaces with locally running neural engines (Ollama, LM Studio, llama.cpp).
    """

    def __init__(self, ollama_url: str = "http://127.0.0.1:11434", openai_url: str = "http://127.0.0.1:1234/v1"):
        self.ollama_url = os.environ.get("OLLAMA_HOST", ollama_url).rstrip("/")
        self.openai_url = os.environ.get("LOCAL_OPENAI_URL", openai_url).rstrip("/")
        self.preferred_models = [
            "llama3.2:3b",
            "llama3.2:1b",
            "llama3.2",
            "llama3.1:8b",
            "llama3:8b",
            "codellama:7b",
            "codellama",
            "qwen2.5-coder:7b",
            "qwen2.5-coder:3b",
            "qwen2.5-coder:1.5b",
            "qwen2.5-coder",
            "qwen2.5:7b",
            "deepseek-coder:6.7b",
            "mistral:7b"
        ]

    def _find_ollama_executable(self) -> Optional[str]:
        import shutil
        from pathlib import Path
        which_path = shutil.which("ollama")
        if which_path:
            return which_path
        candidates = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe",
            Path("C:/Program Files/Ollama/ollama.exe"),
            Path("C:/Users/USER/AppData/Local/Programs/Ollama/ollama.exe")
        ]
        for p in candidates:
            if p.exists():
                return str(p)
        return None

    def _auto_start_ollama(self) -> bool:
        exe = self._find_ollama_executable()
        if not exe:
            return False
        import subprocess
        try:
            startupinfo = None
            flags = 0
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
                if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
                    flags |= subprocess.CREATE_NEW_PROCESS_GROUP

            subprocess.Popen(
                [exe, "serve"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=flags
            )
            # Poll until port is actively responding
            for _ in range(12):
                time.sleep(0.5)
                try:
                    with urllib.request.urlopen(f"{self.ollama_url}/api/tags", timeout=1.0):
                        return True
                except Exception:
                    pass
            return False
        except Exception:
            return False

    def check_status(self, auto_start: bool = True) -> Dict[str, Any]:
        """
        Inspects whether Ollama or an OpenAI-compatible local server is running.
        Autonomously spawns Ollama daemon if installed on disk but not yet started.
        """
        # 1. Probe Ollama
        for attempt in range(2 if auto_start else 1):
            t0 = time.perf_counter()
            try:
                req = urllib.request.Request(f"{self.ollama_url}/api/tags", headers={"User-Agent": "Anjiru/1.0"})
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name") for m in data.get("models", [])]
                    latency = round((time.perf_counter() - t0) * 1000.0, 1)
                    active_model = self._pick_best_model(models)
                    return {
                        "available": True,
                        "provider": "ollama",
                        "endpoint": self.ollama_url,
                        "models": models,
                        "selected_model": active_model,
                        "latency_ms": latency
                    }
            except Exception:
                if attempt == 0 and auto_start:
                    self._auto_start_ollama()
                else:
                    pass

        # 2. Probe LM Studio / Local OpenAI Compatible Endpoint
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(f"{self.openai_url}/models", headers={"User-Agent": "Anjiru/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("id") for m in data.get("data", [])]
                latency = round((time.perf_counter() - t0) * 1000.0, 1)
                active_model = models[0] if models else "local-model"
                return {
                    "available": True,
                    "provider": "lm_studio",
                    "endpoint": self.openai_url,
                    "models": models,
                    "selected_model": active_model,
                    "latency_ms": latency
                }
        except Exception:
            pass

        return {
            "available": False,
            "provider": "none",
            "endpoint": None,
            "models": [],
            "selected_model": None,
            "latency_ms": 0.0
        }

    def _pick_best_model(self, available_models: List[str]) -> Optional[str]:
        if not available_models:
            return None
        # Check priority list
        for pref in self.preferred_models:
            for av in available_models:
                if pref in av:
                    return av
        return available_models[0]

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        timeout: int = 180
    ) -> Optional[Dict[str, Any]]:
        """
        Generates completion from active local neural model.
        """
        status = self.check_status()
        if not status["available"]:
            return None

        provider = status["provider"]
        target_model = model or status["selected_model"] or "qwen2.5-coder:7b"
        sys_p = system_prompt or "You are Anjiru.AI, a high-precision software engineering and linguistic AI."

        t0 = time.perf_counter()

        if provider == "ollama":
            payload = {
                "model": target_model,
                "prompt": prompt,
                "system": sys_p,
                "stream": False,
                "keep_alive": "60m",
                "options": {
                    "temperature": temperature,
                    "num_predict": 768,
                    "num_ctx": 1536,
                    "num_thread": 2,
                    "num_batch": 128
                }
            }
            try:
                req = urllib.request.Request(
                    f"{self.ollama_url}/api/generate",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    text = res.get("response", "")
                    elapsed = round((time.perf_counter() - t0) * 1000.0, 1)
                    return {
                        "text": text,
                        "model": target_model,
                        "provider": "ollama",
                        "latency_ms": elapsed,
                        "eval_count": res.get("eval_count", len(text.split())),
                        "eval_duration_ms": round(res.get("eval_duration", 0) / 1e6, 1)
                    }
            except Exception as e:
                print(f"[LocalNeuralClient] Ollama query failed: {e}")
                return None

        elif provider == "lm_studio":
            payload = {
                "model": target_model,
                "messages": [
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature
            }
            try:
                req = urllib.request.Request(
                    f"{self.openai_url}/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    text = res["choices"][0]["message"]["content"]
                    elapsed = round((time.perf_counter() - t0) * 1000.0, 1)
                    return {
                        "text": text,
                        "model": target_model,
                        "provider": "lm_studio",
                        "latency_ms": elapsed,
                        "eval_count": len(text.split())
                    }
            except Exception as e:
                print(f"[LocalNeuralClient] LM Studio query failed: {e}")
                return None

        return None


_local_neural_singleton = None

def get_local_neural_client() -> LocalNeuralClient:
    global _local_neural_singleton
    if _local_neural_singleton is None:
        _local_neural_singleton = LocalNeuralClient()
    return _local_neural_singleton


if __name__ == "__main__":
    client = get_local_neural_client()
    st = client.check_status()
    print("Local Neural Client Status:")
    print(json.dumps(st, indent=2))

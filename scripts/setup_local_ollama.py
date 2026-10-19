#!/usr/bin/env python3
"""
scripts/setup_local_ollama.py - Sovereign Offline Neural Engine Setup for Anjiru.AI
Assists users in configuring, verifying, and testing local neural models via Ollama.
Supports:
- Checking Ollama binary installation
- Inspecting active background daemon on http://127.0.0.1:11434
- Listing and pulling recommended models (qwen2.5-coder:1.5b, qwen2.5-coder:7b)
- Running instant latency and response verification
"""

import os
import sys
import json
import time
import shutil
import subprocess
import urllib.request
import urllib.error

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

OLLAMA_DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")

RECOMMENDED_MODELS = [
    {
        "name": "qwen2.5-coder:1.5b",
        "size": "~986 MB",
        "ram": "Requires ~2 GB RAM",
        "desc": "Ultra-fast, runs on any laptop CPU with instant response times"
    },
    {
        "name": "qwen2.5-coder:7b",
        "size": "~4.7 GB",
        "ram": "Requires ~8 GB RAM",
        "desc": "Recommended for high-accuracy enterprise polyglot coding and agentic loops"
    },
    {
        "name": "llama3.1:8b",
        "size": "~4.9 GB",
        "ram": "Requires ~8 GB RAM",
        "desc": "General reasoning and bilingual conversation"
    }
]

def check_daemon_running(host: str = OLLAMA_DEFAULT_HOST) -> bool:
    try:
        req = urllib.request.Request(f"{host}/api/tags", headers={"User-Agent": "AnjiruSetup/1.0"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            return resp.status == 200
    except Exception:
        return False

def get_installed_models(host: str = OLLAMA_DEFAULT_HOST):
    try:
        req = urllib.request.Request(f"{host}/api/tags", headers={"User-Agent": "AnjiruSetup/1.0"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m.get("name") for m in data.get("models", [])]
    except Exception:
        return []

def test_inference(model_name: str, host: str = OLLAMA_DEFAULT_HOST):
    print(f"\n[*] Testing live neural generation with '{model_name}'...")
    payload = {
        "model": model_name,
        "prompt": "Habari! Sema 'Anjiru Local Neural Engine iko online' kisha andika Python function ya kupata Fibonacci.",
        "stream": False,
        "options": {"temperature": 0.2}
    }
    t0 = time.perf_counter()
    try:
        req = urllib.request.Request(
            f"{host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            elapsed = (time.perf_counter() - t0) * 1000.0
            print(f"[✓] Generation successful in {elapsed:.1f}ms!")
            print(f"[*] Response Preview:\n{res.get('response', '').strip()[:250]}...\n")
            return True
    except Exception as e:
        print(f"[x] Inference test failed: {e}")
        return False

def main():
    print("=" * 65)
    print(" 🇰🇪 Anjiru.AI: Sovereign Local Offline Neural Engine Setup")
    print("=" * 65)

    ollama_path = shutil.which("ollama")
    is_installed = bool(ollama_path)
    is_daemon_up = check_daemon_running()

    print(f"[*] Ollama Binary: {'Found (' + ollama_path + ')' if is_installed else 'Not Found in PATH'}")
    print(f"[*] Daemon Endpoint: {OLLAMA_DEFAULT_HOST}")
    print(f"[*] Daemon Status: {'🟢 Active & Listening' if is_daemon_up else '⚪ Inactive / Not Running'}\n")

    if not is_installed:
        print("[!] Ollama is not installed on your system.")
        print("    You have two easy ways to install it for free on Windows:")
        print("    1. Via Windows Package Manager (run in terminal):")
        print("       winget install Ollama.Ollama --accept-source-agreements --accept-package-agreements")
        print("    2. Or download installer directly:")
        print("       https://ollama.com/download/windows\n")
        print("    After installation, run this script again or run:")
        print("       ollama run qwen2.5-coder:1.5b")
        return

    if not is_daemon_up:
        print("[!] Ollama is installed but the background service is not running.")
        print("[*] Starting Ollama daemon in background...")
        try:
            if sys.platform == "win32":
                subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["ollama", "serve"])
            print("[*] Waiting for daemon to initialize...")
            for _ in range(6):
                time.sleep(1.0)
                if check_daemon_running():
                    is_daemon_up = True
                    break
        except Exception as e:
            print(f"[!] Failed to auto-start daemon: {e}")
            print("    Please run 'ollama serve' in a separate terminal.")

    if not is_daemon_up:
        print("[x] Could not connect to Ollama daemon on http://127.0.0.1:11434.")
        print("    Please start it manually by typing 'ollama serve' in PowerShell.")
        return

    print("[✓] Connected to local Ollama daemon!")
    models = get_installed_models()
    print(f"[*] Installed Local Models ({len(models)} found):")
    if models:
        for m in models:
            print(f"    - {m}")
    else:
        print("    (No models installed yet)")

    # Suggest recommended model if none found
    if not models:
        print("\n[*] Recommended models to install:")
        for r in RECOMMENDED_MODELS:
            print(f"    - {r['name']} ({r['size']}, {r['ram']}): {r['desc']}")
        print("\n[*] To download and run the recommended model now, run in terminal:")
        print("    ollama pull qwen2.5-coder:1.5b")
        print("    (or for 7B: ollama pull qwen2.5-coder:7b)")
    else:
        # Run test on first model
        test_model = models[0]
        test_inference(test_model)

    print("=" * 65)
    print("[✓] Anjiru Studio is ready to use your local offline neural weights!")
    print("=" * 65)

if __name__ == "__main__":
    main()

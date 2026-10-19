#!/usr/bin/env python3
"""
scripts/download_and_install_ollama.py - Automated Direct Installer for Ollama on Windows
Downloads official OllamaSetup.exe from https://ollama.com/download/OllamaSetup.exe,
executes silent installation, starts the background service, and pulls the recommended model.
"""

import os
import sys
import time
import shutil
import subprocess
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DOWNLOAD_URL = "https://ollama.com/download/OllamaSetup.exe"
TEMP_DIR = Path(os.environ.get("TEMP", "C:/Windows/Temp"))
INSTALLER_PATH = TEMP_DIR / "OllamaSetup.exe"

def download_file(url: str, dest_path: Path):
    print(f"[*] Downloading Ollama installer from {url}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        total_size = int(resp.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 1024 * 512 # 512 KB
        
        with open(dest_path, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    pct = (downloaded / total_size) * 100
                    mb_down = downloaded / (1024 * 1024)
                    mb_tot = total_size / (1024 * 1024)
                    print(f"\r[*] Progress: {mb_down:.1f} MB / {mb_tot:.1f} MB ({pct:.1f}%)", end="", flush=True)
                else:
                    mb_down = downloaded / (1024 * 1024)
                    print(f"\r[*] Downloaded: {mb_down:.1f} MB", end="", flush=True)
    print(f"\n[✓] Download complete: {dest_path} ({dest_path.stat().st_size / (1024*1024):.1f} MB)")

def find_ollama_binary():
    # 1. In PATH
    bin_path = shutil.which("ollama")
    if bin_path:
        return bin_path
    
    # 2. In Local AppData
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        cand1 = Path(local_appdata) / "Programs" / "Ollama" / "ollama.exe"
        if cand1.exists():
            return str(cand1)
            
    # 3. In Program Files
    prog_files = os.environ.get("ProgramFiles", "")
    if prog_files:
        cand2 = Path(prog_files) / "Ollama" / "ollama.exe"
        if cand2.exists():
            return str(cand2)
            
    return None

def install_ollama():
    if not INSTALLER_PATH.exists() or INSTALLER_PATH.stat().st_size < 1024 * 1024:
        download_file(DOWNLOAD_URL, INSTALLER_PATH)
    else:
        print(f"[*] Found existing installer: {INSTALLER_PATH} ({INSTALLER_PATH.stat().st_size / (1024*1024):.1f} MB)")

    print("[*] Running Ollama installer (silent mode)...")
    # InnoSetup / NSIS flags for silent installation: /silent /install
    proc = subprocess.run([str(INSTALLER_PATH), "/silent"], capture_output=True, text=True, timeout=120)
    print(f"[*] Installer finished with code {proc.returncode}")
    
    # Poll for binary appearance
    print("[*] Verifying binary installation...")
    for _ in range(15):
        bin_path = find_ollama_binary()
        if bin_path:
            print(f"[✓] Found Ollama binary at: {bin_path}")
            return bin_path
        time.sleep(2)
        
    return None

def main():
    print("=" * 65)
    print("[*] Anjiru.AI: Automated Direct Ollama Installer")
    print("=" * 65)
    
    existing = find_ollama_binary()
    if existing:
        print(f"[✓] Ollama is already installed at: {existing}")
        ollama_bin = existing
    else:
        ollama_bin = install_ollama()
        
    if not ollama_bin:
        print("[x] Installation did not finish or binary was not found.")
        print(f"    You can run {INSTALLER_PATH} manually by double-clicking it.")
        return 1

    # Update PATH for this process
    bin_dir = str(Path(ollama_bin).parent)
    if bin_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
        print(f"[*] Added {bin_dir} to PATH.")

    # Check daemon
    from scripts.setup_local_ollama import check_daemon_running
    if not check_daemon_running():
        print("[*] Starting Ollama daemon in background...")
        if sys.platform == "win32":
            subprocess.Popen([ollama_bin, "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen([ollama_bin, "serve"])
            
        for _ in range(10):
            time.sleep(1)
            if check_daemon_running():
                break

    if check_daemon_running():
        print("[✓] Ollama daemon is active and listening on http://127.0.0.1:11434!")
    else:
        print("[!] Daemon could not be auto-started. Run 'ollama serve' manually.")
        
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(main())

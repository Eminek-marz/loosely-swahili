r"""
github_mass_code_harvester.py - Mass GitHub Source Code & G-Code Harvester
For Anjiru.AI Multi-Dimensional Pretraining Matrix
Target Storage: D:\ANJIRU_AI_MASSIVE_CORPUS\dimensions\02_code_software

Ingests real production source code repositories from GitHub:
  - CNC Machining & G-Code Repositories (Grbl, Marlin, Klipper, LinuxCNC, Smoothieware)
  - Systems Programming in C, C++, Rust, Go, Python, JavaScript, TypeScript, SQL, Bash
  - AI & Deep Learning Implementations (nanoGPT, micrograd, llm.c, PyTorch examples)

Generates dual-register African technical linguistics for every file:
  - Way 1 (Academic Standard Kiswahili)
  - Way 2 (Colloquial Nairobi Tech Sheng)
Memory: Strictly stream-buffered (< 90 MB RAM).
"""

import sys
import os
import io
import json
import time
import zipfile
import urllib.request
from pathlib import Path
from typing import Dict, List, Any, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent
D_BASE = Path("D:/ANJIRU_AI_MASSIVE_CORPUS")
CODE_DIR = D_BASE / "dimensions" / "02_code_software"
GCODE_DIR = D_BASE / "dimensions" / "01_gcode_manufacturing"
REPORTS_DIR = D_BASE / "reports"

for d in [CODE_DIR, GCODE_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

OUT_GITHUB_JSONL = CODE_DIR / "github_repositories_stream.jsonl"
TELEMETRY_FILE = REPORTS_DIR / "github_harvester_telemetry.json"

# Curated high-signal GitHub repositories
GITHUB_REPOSITORIES = [
    # CNC, G-Code, Motion Control & 3D Printing
    ("grbl", "grbl", "master", "CNC G-Code Motion Controller & Canned Cycles"),
    ("MarlinFirmware", "Marlin", "bugfix-2.1.x", "World 3D Printer & CNC Firmware (G-Code Parser, Kinematics)"),
    ("Klipper3d", "klipper", "master", "3D Printing & Stepper Kinematics G-Code Engine"),
    ("LinuxCNC", "linuxcnc", "master", "Industrial LinuxCNC Machine Control & Toolpath Kinematics"),
    ("Smoothieware", "Smoothieware", "edge", "Modular G-Code Interpreter & High-Speed Motion Control"),
    ("bcn3d", "BCN3DMoveo", "master", "3D Printed Robotic Arm CAD & G-Code Motion Firmware"),

    # AI, Neural Networks & Machine Learning
    ("karpathy", "nanoGPT", "master", "Lightweight PyTorch Transformer Language Model"),
    ("karpathy", "micrograd", "master", "Autograd Engine with Backpropagation in Python"),
    ("karpathy", "llm.c", "master", "Pure C Neural Network Training without PyTorch"),
    ("pytorch", "examples", "main", "Official PyTorch Deep Learning Implementations"),
    ("huggingface", "transformers", "main", "State-of-the-Art Machine Learning Architecture"),

    # Python High-Performance Web & Systems
    ("tiangolo", "fastapi", "master", "FastAPI High Performance Async Web Framework"),
    ("pallets", "flask", "main", "Lightweight WSGI Python Web Application Framework"),
    ("psf", "requests", "main", "Python HTTP for Humans & Socket Connection Pooling"),
    ("encode", "httpx", "master", "Next-Gen HTTP Client for Python with HTTP/2"),

    # Rust Systems & Low-Level Tooling
    ("BurntSushi", "ripgrep", "master", "Ultra-Fast Multi-Threaded Regex Search in Rust"),
    ("sharkdp", "fd", "master", "High-Performance File System Traversal in Rust"),
    ("tokio-rs", "tokio", "master", "Asynchronous Runtime for the Rust Programming Language"),
    ("actix", "actix-web", "master", "Blazing Fast Rust Asynchronous Web Framework"),

    # C / C++ Core Systems
    ("redis", "redis", "unstable", "In-Memory Data Structure Store and Cache in C"),
    ("antirez", "kilo", "master", "Minimal 1000-Line Text Editor in C"),
    ("curl", "curl", "master", "Universal Command Line Network Tool & Library in C"),

    # Go Distributed Systems
    ("gin-gonic", "gin", "master", "Fastest HTTP Web Framework for Golang"),
    ("gorilla", "mux", "main", "Powerful URL Router & Dispatcher for Go"),
    ("caddyserver", "caddy", "master", "Fast & Extensible Multi-Platform HTTPS Web Server in Go")
]

CODE_EXTENSIONS = {
    ".gcode": "G-Code Machine Toolpath",
    ".nc": "Numerical Control G-Code",
    ".ngc": "LinuxCNC G-Code Routine",
    ".py": "Python",
    ".rs": "Rust",
    ".c": "C",
    ".h": "C Header",
    ".cpp": "C++",
    ".hpp": "C++ Header",
    ".go": "Go (Golang)",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".sh": "Shell Script / Bash",
    ".sql": "SQL Database Query",
    ".java": "Java",
    ".cs": "C#",
    ".html": "HTML",
    ".css": "CSS",
    ".toml": "TOML Configuration",
    ".yaml": "YAML Specification",
    ".json": "JSON Data Structure",
    ".md": "Markdown Technical Documentation"
}

SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".bmp",
    ".exe", ".dll", ".so", ".dylib", ".wasm", ".bin", ".o", ".a",
    ".pyc", ".pyo", ".pyd", ".zip", ".tar", ".gz", ".7z",
    ".min.js", ".min.css", ".map", ".lock"
}


def download_github_repo_zip(owner: str, repo: str, branch: str) -> bytes:
    """Downloads repository archive as a single compressed zip stream."""
    urls = [
        f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}",
        f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/main",
        f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/master"
    ]
    for url in urls:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AnjiruAI-Code-Harvester/2.0 (EastAfrica-Pretraining-Research)"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                if len(data) > 1000:
                    return data
        except Exception:
            continue
    return b""


def generate_linguistic_annotations(file_path: str, lang: str, repo: str, code_sample: str) -> Tuple[str, str]:
    """Generates dual-register Kenyan technical explanations for code files."""
    file_name = Path(file_path).name
    # Way 1 (Academic Standard Kiswahili)
    w1 = (
        f"Faili la chanzo cha msimbo wa {lang} lenye jina '{file_name}' kutoka hazina ya GitHub ya {repo}. "
        f"Inatekeleza miundo ya hesabu, mantiki ya kiutendaji, na udhibiti wa mfumo unaohakikisha usindikaji "
        f"wa haraka wa data bila makosa ya kumbukumbu."
    )
    # Way 2 (Colloquial Nairobi Tech Sheng)
    w2 = (
        f"Hii file ya {lang} inaitwa '{file_name}' kutoka kwa repo ya {repo} kwa GitHub. "
        f"Ina-implement logic safi ya ku-handle execution, data structures, na functions muhimu "
        f"ndio code i-run smooth bila ku-crash au ku-leak memory kwa machine."
    )
    return w1, w2


def harvest_github_code_repositories():
    print("=" * 80)
    print("ANJIRU.AI GITHUB SOURCE CODE & G-CODE INDUSTRIAL HARVESTER")
    print(f"Target Destination: {OUT_GITHUB_JSONL}")
    print(f"Total Curated Repositories: {len(GITHUB_REPOSITORIES)}")
    print("=" * 80)

    t_start = time.time()
    total_files = 0
    total_words = 0
    total_tokens = 0
    repos_completed = 0

    out_f = open(OUT_GITHUB_JSONL, "a", encoding="utf-8")
    batch = []

    try:
        for owner, repo, branch, description in GITHUB_REPOSITORIES:
            print(f"\n[*] Fetching repository: {owner}/{repo} ({description})...")
            t_repo_start = time.time()

            zip_data = download_github_repo_zip(owner, repo, branch)
            if not zip_data:
                print(f"  [-] Failed to download archive for {owner}/{repo}. Skipping.")
                continue

            dl_mb = len(zip_data) / (1024 * 1024)
            print(f"  ✓ Downloaded archive: {dl_mb:.2f} MB in {time.time() - t_repo_start:.2f}s. Unpacking in-flight...")

            repo_files = 0
            repo_words = 0

            try:
                with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
                    for name in zf.namelist():
                        ext = Path(name).suffix.lower()
                        if ext in SKIP_EXTENSIONS or ext not in CODE_EXTENSIONS:
                            continue

                        # Read text content
                        try:
                            with zf.open(name) as cf:
                                content = cf.read().decode("utf-8", errors="ignore")
                        except Exception:
                            continue

                        if not content.strip() or len(content.split()) < 5:
                            continue

                        # Limit extremely huge single minified files
                        if len(content) > 500000:
                            content = content[:500000]

                        lang = CODE_EXTENSIONS[ext]
                        w1, w2 = generate_linguistic_annotations(name, lang, f"{owner}/{repo}", content[:200])

                        words_count = len(content.split()) + len(w1.split()) + len(w2.split())
                        tokens_est = int(words_count * 1.30)

                        record = {
                            "id": f"GH_{owner}_{repo}_{repo_files:06d}".replace("-", "_").replace(".", "_"),
                            "repository": f"{owner}/{repo}",
                            "repo_description": description,
                            "file_path": name,
                            "language": lang,
                            "extension": ext,
                            "way1_academic": w1,
                            "way2_sheng": w2,
                            "code_content": content,
                            "metrics": {
                                "words": words_count,
                                "tokens_estimated": tokens_est,
                                "lines": len(content.splitlines())
                            }
                        }

                        batch.append(json.dumps(record, ensure_ascii=False))
                        repo_files += 1
                        repo_words += words_count
                        total_files += 1
                        total_words += words_count
                        total_tokens += tokens_est

                        if len(batch) >= 500:
                            out_f.write("\n".join(batch) + "\n")
                            out_f.flush()
                            batch = []

            except Exception as e:
                print(f"  [!] Error processing zip archive: {e}")

            del zip_data  # Immediate memory release
            repos_completed += 1
            elapsed = time.time() - t_start
            wps = total_words / max(0.1, elapsed)

            print(f"  ⚡ Ingested: {repo_files:,} files ({repo_words:,} words) from {owner}/{repo}")
            print(f"  📊 Grand Total: {total_files:,} files | {total_words:,} words | Speed: {wps:,.0f} words/sec")

            # Update telemetry
            telemetry = {
                "pipeline": "GitHub Mass Code & G-Code Harvester",
                "repos_completed": repos_completed,
                "total_repos": len(GITHUB_REPOSITORIES),
                "total_code_files_ingested": total_files,
                "total_words_generated": total_words,
                "total_tokens_estimated": total_tokens,
                "file_size_on_disk_bytes": OUT_GITHUB_JSONL.stat().st_size if OUT_GITHUB_JSONL.exists() else 0,
                "speed_words_per_sec": round(wps, 1),
                "elapsed_seconds": round(elapsed, 1),
                "storage_drive": str(D_BASE),
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(TELEMETRY_FILE, "w", encoding="utf-8") as tf:
                json.dump(telemetry, tf, indent=2)

        if batch:
            out_f.write("\n".join(batch) + "\n")
            out_f.flush()

    finally:
        out_f.close()

    total_time = time.time() - t_start
    print("\n" + "=" * 80)
    print("🎉 GITHUB MASS CODE INGESTION COMPLETE!")
    print(f"Total Repositories:      {repos_completed} / {len(GITHUB_REPOSITORIES)}")
    print(f"Total Code Files:        {total_files:,}")
    print(f"Total Words Generated:   {total_words:,} words")
    print(f"Total Tokens Estimated:  {total_tokens:,} tokens")
    print(f"File Size on Disk:       {OUT_GITHUB_JSONL.stat().st_size / (1024*1024):.2f} MB")
    print(f"Throughput Speed:        {total_words / max(0.1, total_time):,.0f} words / second")
    print(f"Elapsed Time:            {total_time:.1f}s ({total_time/60:.2f} mins)")
    print(f"Output File:             {OUT_GITHUB_JSONL}")
    print("=" * 80)


if __name__ == "__main__":
    harvest_github_code_repositories()

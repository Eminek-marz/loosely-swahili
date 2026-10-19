#!/usr/bin/env python3
"""
scripts/package_colab_bundle.py - Prepares Standalone Colab Training Archive
Packages:
1. notebooks/Train_Anjiru_AI_QLoRA_Colab.ipynb
2. data/instruction_tuning/anjiru_colab_fast_train.jsonl
3. README instructions for 1-click training on Google Colab

Output: dist/anjiru_colab_training_bundle.zip
"""

import os
import sys
import zipfile
from pathlib import Path

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
DIST_DIR.mkdir(parents=True, exist_ok=True)

BUNDLE_PATH = DIST_DIR / "anjiru_colab_training_bundle.zip"

README_TEXT = """# 🇰🇪 Anjiru.AI: Google Colab 4-Bit QLoRA Fine-Tuning Bundle

This archive contains everything needed to train the sovereign **Anjiru.AI** polyglot coding and bilingual foundation model on a free Google Colab T4 GPU.

## Files in this Bundle:
1. `Train_Anjiru_AI_QLoRA_Colab.ipynb`: Complete self-contained notebook configured with 4-bit NF4 quantization, Qwen2.5-Coder-7B-Instruct, SFTTrainer, and export to Ollama Modelfile.
2. `anjiru_colab_fast_train.jsonl`: Curated balanced training dataset (~4,500 samples) with 10x oversampled polyglot coding plans and Kenyan bilingual registers (~8 MB).

## 3 Steps to Run on Google Colab:
1. Go to https://colab.research.google.com/ and click **Upload Notebook**. Choose `Train_Anjiru_AI_QLoRA_Colab.ipynb`.
2. Set Runtime to T4 GPU: Click **Runtime > Change runtime type > T4 GPU > Save**.
3. In the Colab file browser (left folder icon), upload `anjiru_colab_fast_train.jsonl`.
4. Click **Runtime > Run all** (or press `Ctrl+F9`).
5. After training finishes (~45 minutes), download `anjiru_adapter.tar.gz`.
6. Extract it on your computer and run:
   ```bash
   ollama create anjiru -f Modelfile
   ollama run anjiru
   ```
   Anjiru Studio will automatically detect the fine-tuned model and use it for all coding and reasoning!
"""

def make_bundle():
    print("[*] Creating Anjiru Colab Training Bundle...")
    notebook_file = PROJECT_ROOT / "notebooks" / "Train_Anjiru_AI_QLoRA_Colab.ipynb"
    dataset_file = PROJECT_ROOT / "data" / "instruction_tuning" / "anjiru_colab_fast_train.jsonl"

    if not notebook_file.exists():
        print(f"[x] Missing notebook at {notebook_file}")
        return False
    if not dataset_file.exists():
        print(f"[x] Missing dataset at {dataset_file}")
        return False

    with zipfile.ZipFile(BUNDLE_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(notebook_file, arcname="Train_Anjiru_AI_QLoRA_Colab.ipynb")
        zf.write(dataset_file, arcname="anjiru_colab_fast_train.jsonl")
        zf.writestr("README_COLAB.md", README_TEXT)

    size_mb = BUNDLE_PATH.stat().st_size / (1024 * 1024)
    print(f"[✓] Successfully generated Colab bundle: {BUNDLE_PATH} ({size_mb:.2f} MB)")
    return True

if __name__ == "__main__":
    make_bundle()

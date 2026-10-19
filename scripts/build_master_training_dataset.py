#!/usr/bin/env python3
"""
scripts/build_master_training_dataset.py - Compiles Unified Anjiru Master & Fast Colab Training Datasets
Merges:
1. data/instruction_tuning/train.jsonl (45k linguistic, translation, code-switching records)
2. data/instruction_tuning/polyglot_coder_instructions.jsonl (75 enterprise polyglot coding execution plans)
3. data/instruction_tuning/academic_scholar_train.jsonl (76 scholarly Kiswahili records)
4. data/instruction_tuning/autonomous_curriculum.jsonl (4 autonomous curriculum records)

Outputs:
- data/instruction_tuning/anjiru_master_train.jsonl: Complete combined dataset (~45k rows)
- data/instruction_tuning/anjiru_colab_fast_train.jsonl: Balanced ~4,500-sample shard optimized
  for rapid 45-60 minute QLoRA fine-tuning on Google Colab Free T4 GPU.
"""

import os
import sys
import json
import random
from pathlib import Path
from typing import List, Dict, Any

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTRUCTION_DIR = PROJECT_ROOT / "data" / "instruction_tuning"

MASTER_OUTPUT_PATH = INSTRUCTION_DIR / "anjiru_master_train.jsonl"
FAST_COLAB_OUTPUT_PATH = INSTRUCTION_DIR / "anjiru_colab_fast_train.jsonl"

def normalize_to_chatml(item: Dict[str, Any], default_source: str = "general") -> Dict[str, Any]:
    """
    Ensures item strictly conforms to ChatML schema:
    {"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}], "metadata": {...}}
    """
    if "messages" in item and isinstance(item["messages"], list) and len(item["messages"]) >= 2:
        # Already has messages structure
        messages = []
        for m in item["messages"]:
            role = m.get("role", "user")
            content = m.get("content", "")
            if content:
                messages.append({"role": role, "content": str(content).strip()})
        
        # Ensure system message is present
        if messages and messages[0]["role"] != "system":
            sys_msg = (
                "You are Anjiru.AI, the sovereign Kenyan foundation AI and universal polyglot execution kernel. "
                "You write, edit, and debug code across arbitrary stacks and communicate natively in "
                "Kiswahili Sanifu, Nairobi Tech Sheng, and English."
            )
            messages.insert(0, {"role": "system", "content": sys_msg})
        
        meta = item.get("metadata", {})
        if not isinstance(meta, dict):
            meta = {}
        if "source" not in meta:
            meta["source"] = default_source
        if "domain" not in meta:
            meta["domain"] = item.get("domain", "general")
        return {"messages": messages, "metadata": meta}

    # Support autonomous curriculum format
    if "set_b_english" in item and ("set_a_sanifu" in item or "set_c_codeswitch" in item):
        eng = item.get("set_b_english", "").strip()
        sanifu = item.get("set_a_sanifu", "").strip()
        cs = item.get("set_c_codeswitch", "").strip()
        sys_msg = (
            "You are Anjiru.AI, the sovereign Kenyan foundation AI. Translate and provide bilingual "
            "conceptual breakdowns across Kiswahili Sanifu and Kenyan Code-Switching."
        )
        return {
            "messages": [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": f"Explain and translate the following into Kiswahili Sanifu and Kenyan technical code-switch:\n\n{eng}"},
                {"role": "assistant", "content": f"### Kiswahili Sanifu\n{sanifu}\n\n### Kenyan Code-Switching\n{cs}"}
            ],
            "metadata": {
                "source": default_source,
                "domain": item.get("domain", "science")
            }
        }

    # Otherwise format from instruction/input/output or english/way1/way2
    instruction = item.get("instruction", item.get("prompt", "")).strip()
    user_input = item.get("input", item.get("english", item.get("sentence", ""))).strip()
    output = item.get("output", "").strip()

    if not output and ("way1_academic" in item or "way2_sheng" in item):
        w1 = item.get("way1_academic", "")
        w2 = item.get("way2_sheng", "")
        output = f"### Way 1 (Academic Standard)\n{w1}\n\n### Way 2 (Colloquial Sheng)\n{w2}"

    prompt_content = f"{instruction}\n\n{user_input}".strip() if user_input else instruction
    if not prompt_content:
        prompt_content = user_input

    if not prompt_content or not output:
        return {}

    sys_msg = (
        "You are Anjiru.AI, the sovereign Kenyan foundation AI and universal polyglot execution kernel. "
        "You write, edit, and debug code across arbitrary stacks and communicate natively in "
        "Kiswahili Sanifu, Nairobi Tech Sheng, and English."
    )

    return {
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt_content},
            {"role": "assistant", "content": output}
        ],
        "metadata": {
            "source": item.get("task", default_source),
            "domain": item.get("domain", "general"),
            "id": item.get("id", "")
        }
    }


def compile_datasets():
    print("=" * 65)
    print("[*] Anjiru.AI: Compiling Master & Colab Fast Training Datasets")
    print("=" * 65)

    all_polyglot = []
    poly_path = INSTRUCTION_DIR / "polyglot_coder_instructions.jsonl"
    if poly_path.exists():
        with open(poly_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    norm = normalize_to_chatml(item, default_source="polyglot_coder")
                    if norm:
                        all_polyglot.append(norm)
        print(f"[✓] Loaded {len(all_polyglot):,} polyglot coding execution plan instructions.")

    all_academic = []
    acad_path = INSTRUCTION_DIR / "academic_scholar_train.jsonl"
    if acad_path.exists():
        with open(acad_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    norm = normalize_to_chatml(item, default_source="academic_scholar")
                    if norm:
                        all_academic.append(norm)
        print(f"[✓] Loaded {len(all_academic):,} academic scholar instructions.")

    all_curriculum = []
    curr_path = INSTRUCTION_DIR / "autonomous_curriculum.jsonl"
    if curr_path.exists():
        with open(curr_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    norm = normalize_to_chatml(item, default_source="autonomous_curriculum")
                    if norm:
                        all_curriculum.append(norm)
        print(f"[✓] Loaded {len(all_curriculum):,} autonomous curriculum instructions.")

    all_linguistic = []
    train_path = INSTRUCTION_DIR / "train.jsonl"
    if train_path.exists():
        with open(train_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    norm = normalize_to_chatml(item, default_source="linguistic_train")
                    if norm:
                        all_linguistic.append(norm)
        print(f"[✓] Loaded {len(all_linguistic):,} general linguistic/code-switching instructions.")

    # 1. BUILD MASTER DATASET
    print("\n[*] Writing Master Dataset (all combined)...")
    master_records = all_polyglot + all_academic + all_curriculum + all_linguistic
    with open(MASTER_OUTPUT_PATH, "w", encoding="utf-8") as f:
        for rec in master_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    master_mb = MASTER_OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"[✓] Saved Master Dataset: {MASTER_OUTPUT_PATH}")
    print(f"    Total Records: {len(master_records):,} | Size: {master_mb:.2f} MB")

    # 2. BUILD BALANCED FAST COLAB DATASET (~4,500 samples)
    # Balanced formulation:
    # - 75 polyglot instructions repeated 10x = 750 samples (ensures high gradient signal for coding!)
    # - 100% of academic (76)
    # - 100% of curriculum (4)
    # - Stratified sample of 3,670 linguistic/code-switching records
    print("\n[*] Building Balanced Fast Colab Dataset (~4,500 samples)...")
    random.seed(42)

    oversampled_polyglot = []
    for _ in range(10):
        oversampled_polyglot.extend(all_polyglot)

    sampled_linguistic = random.sample(all_linguistic, min(3670, len(all_linguistic)))

    fast_records = oversampled_polyglot + all_academic + all_curriculum + sampled_linguistic
    random.shuffle(fast_records)

    with open(FAST_COLAB_OUTPUT_PATH, "w", encoding="utf-8") as f:
        for rec in fast_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    fast_mb = FAST_COLAB_OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print(f"[✓] Saved Fast Colab Dataset: {FAST_COLAB_OUTPUT_PATH}")
    print(f"    Total Records: {len(fast_records):,} | Size: {fast_mb:.2f} MB")
    print(f"    Breakdown:")
    print(f"    - Polyglot Coder (10x oversample): {len(oversampled_polyglot):,} records ({len(all_polyglot)} unique)")
    print(f"    - Academic Scholar: {len(all_academic):,} records")
    print(f"    - Autonomous Curriculum: {len(all_curriculum):,} records")
    print(f"    - Bilingual Kenyan NLP: {len(sampled_linguistic):,} records")
    print("=" * 65)

if __name__ == "__main__":
    compile_datasets()

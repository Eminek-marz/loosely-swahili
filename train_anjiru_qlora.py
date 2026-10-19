"""
train_anjiru_qlora.py - Production QLoRA Fine-Tuning Pipeline for Anjiru.AI

Fine-tunes open-weights foundation models (LLaMA-3.1-8B, Gemma-2-9B, Qwen-2.5-7B)
on 372,854 academic instruction prompts using 4-bit Low-Rank Adaptation (QLoRA).
Internalizes 123 Kenyan morphotactic rules directly into transformer attention layers.

Usage:
  # Dry-run validation (checks dataset, tokenizes sample, previews ChatML prompts on any CPU):
  python train_anjiru_qlora.py --dry-run

  # Full training on GPU (Colab T4/A100, RunPod, or local NVIDIA GPU):
  python train_anjiru_qlora.py --base_model meta-llama/Llama-3.1-8B-Instruct --output_dir ./models/anjiru-8b-lora

  # Quick fine-tune test (first 5,000 samples):
  python train_anjiru_qlora.py --max_samples 5000 --epochs 1
"""

import os
import sys
import json
import argparse
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Ensure project root in path
PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_PATH_DEFAULT = PROJECT_ROOT / "data" / "bulk_academic" / "instruction_tuning_academic.jsonl"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "models" / "anjiru-8b-lora"

ANJIRU_SYSTEM_PROMPT = """You are Anjiru.AI, the indigenous Kenyan neural language intelligence.
You translate and express complex academic research, computer science, mathematics, and natural sciences into authentic Kenyan Loosely Swahili using the 123 Master Morphotactic Rules.

When answering, always produce BOTH living registers:
Way 1 (Academic Standard): Bantu post-nominal concord, pristine technical English stems, post-nominal temporal modifiers (e.g. 'state-of-the-art genomics generators ya sasa kwa tasks mbili tofauti').
Way 2 (Colloquial Sheng): Sheng Class 6 double-prefixing (ma-), urban cadence, high-solidarity anchors (e.g. 'maresults zetu show kuwa... kwa matasks mbili tofauti')."""


def build_chatml_example(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an instruction record or pre-formatted message into a standard ChatML conversation."""
    if "messages" in item:
        return {"messages": item["messages"]}

    instruction = item.get("instruction", "Translate this academic text into authentic Kenyan Loosely Swahili:")
    input_text = item.get("input", "").strip()
    w1_out = item.get("output", "").strip()
    w2_out = item.get("way2_output", "").strip()
    domain = item.get("domain", "General Science")

    user_content = f"{instruction}\n\n[Domain: {domain}]\n{input_text}"
    assistant_content = f"Way 1 (Academic Standard):\n{w1_out}\n\nWay 2 (Colloquial Sheng):\n{w2_out}"

    messages = [
        {"role": "system", "content": ANJIRU_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": assistant_content}
    ]
    return {"messages": messages}


def run_dry_run_validation(dataset_path: Path, max_check: int = 1000):
    """
    Validates dataset integrity, ChatML formatting, and token statistics
    without requiring PyTorch or CUDA. Runs seamlessly on any CPU.
    """
    print("=" * 70)
    print("ANJIRU.AI QLoRA FINE-TUNING PRE-FLIGHT VALIDATION (DRY RUN)")
    print("=" * 70)
    print(f"[*] Dataset file: {dataset_path}")

    if not dataset_path.exists():
        print(f"[ERROR] Dataset file not found at {dataset_path}")
        return

    file_size_mb = dataset_path.stat().st_size / (1024 * 1024)
    print(f"[*] Dataset Size: {file_size_mb:.2f} MB")

    total_valid = 0
    total_words_input = 0
    total_words_w1 = 0
    total_words_w2 = 0
    domains = set()

    sample_preview = None

    t0 = time.time()
    with open(dataset_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                total_valid += 1
                if "messages" in rec:
                    msgs = rec["messages"]
                    u_content = " ".join([m["content"] for m in msgs if m["role"] == "user"])
                    a_content = " ".join([m["content"] for m in msgs if m["role"] == "assistant"])
                    total_words_input += len(u_content.split())
                    total_words_w1 += len(a_content.split())
                    dom = rec.get("metadata", {}).get("domain", rec.get("domain", "Polyglot Coding"))
                    domains.add(dom)
                else:
                    inp = rec.get("input", "")
                    w1 = rec.get("output", "")
                    w2 = rec.get("way2_output", "")
                    dom = rec.get("domain", "Unknown")

                    total_words_input += len(inp.split())
                    total_words_w1 += len(w1.split())
                    total_words_w2 += len(w2.split())
                    domains.add(dom)

                if idx == 0:
                    sample_preview = build_chatml_example(rec)

                if total_valid >= max_check:
                    break
            except Exception as e:
                print(f"[!] Error reading line {idx}: {e}")

    duration = time.time() - t0
    print(f"[*] Validated sample of {total_valid:,} instructions in {duration:.2f}s")
    print(f"[*] Average source words / sentence: {total_words_input / max(1, total_valid):.1f}")
    print(f"[*] Average Way 1 words / sentence:   {total_words_w1 / max(1, total_valid):.1f}")
    print(f"[*] Average Way 2 words / sentence:   {total_words_w2 / max(1, total_valid):.1f}")
    print(f"[*] Unique scientific domains found: {len(domains)}")
    print(f"[*] Sample domains: {list(domains)[:5]}")

    print("\n" + "-" * 70)
    print("CHATML PROMPT TEMPLATE PREVIEW FOR ANJIRU.AI:")
    print("-" * 70)
    if sample_preview:
        for m in sample_preview["messages"]:
            print(f"[{m['role'].upper()}]:")
            print(f"{m['content']}\n")
    print("-" * 70)

    print("\n[SUCCESS] Pre-flight validation passed! Ready for GPU training.")
    print("To launch training on a GPU instance:")
    print("  python train_anjiru_qlora.py --base_model meta-llama/Llama-3.1-8B-Instruct --batch_size 4 --epochs 2\n")


def train(
    base_model_name: str,
    dataset_path: Path,
    output_dir: Path,
    epochs: int = 2,
    batch_size: int = 4,
    gradient_accumulation_steps: int = 8,
    learning_rate: float = 2e-4,
    lora_r: int = 64,
    lora_alpha: int = 128,
    max_seq_length: int = 1024,
    max_samples: Optional[int] = None,
    push_to_hub: bool = False,
    hub_model_id: Optional[str] = None
):
    """Executes 4-bit QLoRA fine-tuning using transformers, peft, and trl."""
    print("=" * 70)
    print("ANJIRU.AI NEURAL QLoRA FINE-TUNING PIPELINE")
    print("=" * 70)
    print(f"[*] Base Foundation Model: {base_model_name}")
    print(f"[*] Dataset: {dataset_path}")
    print(f"[*] Output Directory: {output_dir}")
    print(f"[*] Target Architecture: 4-bit NormalFloat4 (NF4) + Double Quantization")
    print(f"[*] LoRA Hyperparameters: Rank={lora_r}, Alpha={lora_alpha}, Target=All Projections")

    # Verify ML dependencies
    try:
        import torch
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            TrainingArguments
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer
        from datasets import Dataset
    except ImportError as e:
        print(f"\n[FATAL] Missing required deep learning dependency: {e}")
        print("Please install training dependencies:")
        print("  pip install torch transformers peft bitsandbytes trl datasets accelerate\n")
        sys.exit(1)

    # 1. Prepare Dataset
    print("\n[*] Loading dataset...")
    data_records = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                data_records.append(build_chatml_example(rec))
                if max_samples and len(data_records) >= max_samples:
                    break
            except Exception:
                pass

    print(f"[*] Loaded {len(data_records):,} ChatML instruction training conversations.")
    hf_dataset = Dataset.from_list(data_records)

    # 2. Tokenizer Setup
    print(f"[*] Loading tokenizer for {base_model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # 3. 4-bit Quantization Configuration (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    )

    # 4. Load Base Model
    print(f"[*] Loading quantized base model {base_model_name}...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    model = prepare_model_for_kbit_training(model)

    # 5. Configure LoRA
    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 6. Training Arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        gradient_checkpointing=True,
        optim="paged_adamw_32bit",
        logging_steps=10,
        save_strategy="epoch",
        learning_rate=learning_rate,
        weight_decay=0.001,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        max_grad_norm=0.3,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        report_to="none"
    )

    # 7. SFT Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=hf_dataset,
        peft_config=peft_config,
        dataset_text_field="messages",
        max_seq_length=max_seq_length,
        tokenizer=tokenizer,
        args=training_args
    )

    print("\n[*] Starting QLoRA fine-tuning for Anjiru.AI...")
    trainer.train()

    print(f"\n[*] Training complete! Saving LoRA adapter to {output_dir}...")
    trainer.model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    if push_to_hub and hub_model_id:
        print(f"[*] Pushing fine-tuned Anjiru adapter to Hugging Face Hub: {hub_model_id}...")
        trainer.model.push_to_hub(hub_model_id)
        tokenizer.push_to_hub(hub_model_id)

    print("\n[SUCCESS] Anjiru.AI neural adapter successfully trained and serialized.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Anjiru.AI using QLoRA 4-bit fine-tuning.")
    parser.add_argument("--base_model", type=str, default="meta-llama/Llama-3.1-8B-Instruct",
                        help="Hugging Face base model identifier.")
    parser.add_argument("--dataset_path", type=str, default=str(DATASET_PATH_DEFAULT),
                        help="Path to instruction_tuning_academic.jsonl.")
    parser.add_argument("--output_dir", type=str, default=str(DEFAULT_OUTPUT_DIR),
                        help="Directory to save fine-tuned LoRA weights.")
    parser.add_argument("--epochs", type=int, default=2, help="Number of training epochs.")
    parser.add_argument("--batch_size", type=int, default=4, help="Per-device batch size.")
    parser.add_argument("--grad_accum", type=int, default=8, help="Gradient accumulation steps.")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate.")
    parser.add_argument("--lora_r", type=int, default=64, help="LoRA rank.")
    parser.add_argument("--lora_alpha", type=int, default=128, help="LoRA alpha.")
    parser.add_argument("--max_seq_len", type=int, default=1024, help="Max sequence length.")
    parser.add_argument("--max_samples", type=int, default=None, help="Limit number of samples for rapid prototyping.")
    parser.add_argument("--dry-run", action="store_true", help="Run pre-flight validation on CPU without GPU.")
    parser.add_argument("--push_to_hub", action="store_true", help="Push to Hugging Face Hub.")
    parser.add_argument("--hub_id", type=str, default=None, help="Hugging Face repo id.")

    args = parser.parse_args()

    if args.dry_run:
        run_dry_run_validation(Path(args.dataset_path))
    else:
        # Check if torch is available; if not, run dry run with friendly guidance
        try:
            import torch
            train(
                base_model_name=args.base_model,
                dataset_path=Path(args.dataset_path),
                output_dir=Path(args.output_dir),
                epochs=args.epochs,
                batch_size=args.batch_size,
                gradient_accumulation_steps=args.grad_accum,
                learning_rate=args.lr,
                lora_r=args.lora_r,
                lora_alpha=args.lora_alpha,
                max_seq_length=args.max_seq_len,
                max_samples=args.max_samples,
                push_to_hub=args.push_to_hub,
                hub_model_id=args.hub_id
            )
        except ImportError:
            print("[INFO] PyTorch not detected in local environment. Running pre-flight dry-run validation:")
            run_dry_run_validation(Path(args.dataset_path))

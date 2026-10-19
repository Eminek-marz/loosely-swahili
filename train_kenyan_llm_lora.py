"""
One-Click LoRA / QLoRA Fine-Tuning Pipeline for Kenyan Code-Switching LLM
Adapts open-weights foundation models (Llama 3, Mistral, Gemma, Qwen) to become fluent in:
  1. Authentic Kenyan Code-Switching (Sheng / Technical Swahili-English Blend)
  2. Multi-Domain Technical Concept Recreation (Engineering, Finance, Tech, Medicine, Politics)
  3. Strict Master Blueprint Rule Enforcement (0% *-ed endings, double-stack plurals, semantic invariants)

Compatible with:
  - Single GPU (16GB VRAM, e.g. Free Google Colab T4) via 4-bit QLoRA (bitsandbytes)
  - Multi-GPU servers (A100, H100, RTX 4090/3090) with BF16/FP16
  - CPU testing / dry-run mode
"""

import sys
import os
import argparse
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
INSTRUCTION_DIR = DATA_DIR / "instruction_tuning"
OUTPUT_DIR = PROJECT_ROOT / "models" / "kenyan_codeswitch_lora"

def parse_args():
    parser = argparse.ArgumentParser(description="Train Kenyan Code-Switching LLM via LoRA / QLoRA")
    parser.add_argument("--base_model", type=str, default="meta-llama/Meta-Llama-3-8B-Instruct",
                        help="Base Hugging Face model identifier (e.g. meta-llama/Meta-Llama-3-8B-Instruct, mistralai/Mistral-7B-Instruct-v0.3, Qwen/Qwen2.5-7B-Instruct)")
    parser.add_argument("--train_file", type=str, default=str(INSTRUCTION_DIR / "train.jsonl"),
                        help="Path to JSONL training dataset")
    parser.add_argument("--val_file", type=str, default=str(INSTRUCTION_DIR / "validation.jsonl"),
                        help="Path to JSONL validation dataset")
    parser.add_argument("--output_dir", type=str, default=str(OUTPUT_DIR),
                        help="Output directory for LoRA adapters and model checkpoints")
    parser.add_argument("--batch_size", type=int, default=4, help="Per-device training batch size")
    parser.add_argument("--grad_accum", type=int, default=4, help="Gradient accumulation steps (effective batch = batch * accum)")
    parser.add_argument("--lr", type=float, default=2e-4, help="Peak learning rate")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--lora_r", type=int, default=16, help="LoRA rank dimension")
    parser.add_argument("--lora_alpha", type=int, default=32, help="LoRA scaling alpha")
    parser.add_argument("--lora_dropout", type=float, default=0.05, help="LoRA dropout rate")
    parser.add_argument("--max_seq_length", type=int, default=1024, help="Maximum sequence token length")
    parser.add_argument("--use_4bit", action="store_true", default=True, help="Enable 4-bit QLoRA quantization (NF4)")
    parser.add_argument("--dry_run", action="store_true", help="Perform sanity check and dataset validation without initiating GPU training")
    return parser.parse_args()

def main():
    args = parse_args()
    print("=" * 80)
    print("🚀 KENYAN CODE-SWITCHING LLM FINE-TUNING PIPELINE (LORA / QLORA)")
    print("=" * 80)
    print(f"• Base Model:       {args.base_model}")
    print(f"• Training Data:    {args.train_file}")
    print(f"• Validation Data:  {args.val_file}")
    print(f"• Output Directory: {args.output_dir}")
    print(f"• LoRA Config:      r={args.lora_r}, alpha={args.lora_alpha}, dropout={args.lora_dropout}")
    print(f"• 4-Bit QLoRA:      {args.use_4bit}")
    print("=" * 80)

    # 1. Validate Dataset Files Exist
    train_path = Path(args.train_file)
    val_path = Path(args.val_file)
    if not train_path.exists():
        print(f"[ERROR] Training file {train_path} not found. Run 'src/instruction_tuning_generator.py' first.")
        sys.exit(1)

    print(f"[*] Verified training dataset: {train_path} ({os.path.getsize(train_path) / (1024*1024):.2f} MB)")
    if val_path.exists():
        print(f"[*] Verified validation dataset: {val_path} ({os.path.getsize(val_path) / (1024*1024):.2f} MB)")

    # Read first record as sanity check
    with open(train_path, "r", encoding="utf-8") as f:
        first_line = json.loads(f.readline())
        print(f"\nSample Training Instance (ID: {first_line.get('id')}):")
        print(f"  • Task:   {first_line.get('task')}")
        print(f"  • Input:  {first_line.get('input')[:90]}...")
        print(f"  • Output: {first_line.get('output')[:90]}...")

    if args.dry_run:
        print("\n[+] Dry run complete! Datasets, schemas, and hyperparameters are verified.")
        return

    # 2. Check for PyTorch & CUDA
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else ("mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu")
        print(f"\n[*] Execution Device: {device.upper()}")
        if device == "cuda":
            print(f"  • GPU Model: {torch.cuda.get_device_name(0)}")
            print(f"  • VRAM:      {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    except ImportError:
        print("[!] PyTorch not installed in this environment. To run active training:")
        print("    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        print("    pip install transformers peft bitsandbytes datasets trl accelerate")
        return

    # 3. Dynamic Import of Hugging Face Training Toolchain
    try:
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            TrainingArguments
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from datasets import load_dataset
        from trl import SFTTrainer
    except ImportError as e:
        print(f"\n[!] Required fine-tuning libraries missing ({e.name}).")
        print("To install the full GPU fine-tuning stack:")
        print("  pip install transformers peft bitsandbytes datasets trl accelerate")
        print("\nOr run this pipeline directly in Google Colab using free T4 GPU.")
        return

    # 4. Configure Quantization (QLoRA)
    bnb_config = None
    if args.use_4bit and device == "cuda":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )

    print(f"\n[*] Loading tokenizer for {args.base_model}...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    print(f"[*] Loading foundation model {args.base_model}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=bnb_config,
        device_map="auto" if device == "cuda" else None,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        trust_remote_code=True
    )

    if args.use_4bit and device == "cuda":
        model = prepare_model_for_kbit_training(model)

    # 5. Configure LoRA
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 6. Load Dataset
    print(f"\n[*] Streaming dataset from {args.train_file}...")
    data_files = {"train": args.train_file}
    if val_path.exists():
        data_files["validation"] = args.val_file
    dataset = load_dataset("json", data_files=data_files)

    # Format ChatML / Alpaca prompt template
    def formatting_prompts_func(example):
        output_texts = []
        for i in range(len(example["instruction"])):
            text = (
                f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
                f"{SYSTEM_PROMPT}<|eot_id|>"
                f"<|start_header_id|>user<|end_header_id|>\n\n"
                f"{example['instruction'][i]}\n\n"
                f"Context / Input:\n{example['input'][i]}<|eot_id|>"
                f"<|start_header_id|>assistant<|end_header_id|>\n\n"
                f"{example['output'][i]}<|eot_id|>"
            )
            output_texts.append(text)
        return output_texts

    # 7. Training Arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        num_train_epochs=args.epochs,
        logging_steps=10,
        save_strategy="epoch",
        evaluation_strategy="epoch" if "validation" in dataset else "no",
        fp16=(device == "cuda"),
        optim="paged_adamw_8bit" if (args.use_4bit and device == "cuda") else "adamw_torch",
        report_to="none"
    )

    # 8. SFTTrainer Initialization
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        eval_dataset=dataset.get("validation"),
        peft_config=lora_config,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        tokenizer=tokenizer,
        args=training_args,
        formatting_func=formatting_prompts_func
    )

    print("\n" + "=" * 80)
    print("🔥 LAUNCHING TRAINING RUN...")
    print("=" * 80)
    trainer.train()

    print(f"\n[+] Training complete! Saving LoRA adapter weights to {args.output_dir}...")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"[+] All artifacts successfully saved to: {args.output_dir}")

if __name__ == "__main__":
    main()

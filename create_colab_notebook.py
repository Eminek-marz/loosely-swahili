#!/usr/bin/env python3
"""
create_colab_notebook.py - Generates the Production QLoRA Training Notebook for Google Colab
Prepares Anjiru.AI's fine-tuning on free Colab T4 GPU with:
- 4-Bit NF4 Quantization (Qwen-2.5-Coder-7B-Instruct or LLaMA-3.1-8B)
- Universal ChatML formatting using tokenizer.apply_chat_template
- Support for anjiru_colab_fast_train.jsonl (4,500 samples, ~45 min run)
- Export to Ollama Modelfile & GGUF for local offline execution in Anjiru Studio
"""

import json
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 🇰🇪 Anjiru.AI: 4-Bit QLoRA Fine-Tuning Pipeline (Google Colab T4 GPU)\n",
    "### Sovereign Kenyan Polyglot Coder & Bilingual Foundation Intelligence\n",
    "\n",
    "This notebook trains **Anjiru.AI** using 4-bit NormalFloat4 (NF4) QLoRA on a free Google Colab T4 GPU (16 GB VRAM).\n",
    "\n",
    "### Capabilities Trained:\n",
    "1. **Universal Polyglot Execution Kernel:** Language & framework agnostic 2-pass planning (`[EXECUTION_KERNEL_PLAN]`) across Rust, Go, Next.js, FastAPI, C++, Kotlin, and Python.\n",
    "2. **Dual-Register Kenyan Linguistics:** Flawless switching between **Kiswahili Sanifu** (formal/academic Bantu concord) and **Nairobi Tech Sheng** (colloquial urban youth vernacular with intact technical stems).\n",
    "3. **Zero-Cloud Local Deployment:** Export directly to an **Ollama Modelfile** or **GGUF** to drop into Anjiru Studio on your local PC with zero cloud API keys!\n",
    "\n",
    "**Hardware Requirement:** Google Colab Free Tier with T4 GPU runtime (`Runtime > Change runtime type > T4 GPU`)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 1: Verify GPU Acceleration (Must show NVIDIA T4, L4, or A100)\n",
    "!nvidia-smi"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 2: Install High-Performance Training & Quantization Libraries\n",
    "!pip install -q -U torch transformers peft bitsandbytes datasets trl accelerate huggingface_hub"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 3: Base Foundation Model Configuration & 4-Bit NF4 Quantization\n",
    "import os\n",
    "import torch\n",
    "from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments\n",
    "from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training\n",
    "from trl import SFTTrainer\n",
    "from datasets import Dataset\n",
    "\n",
    "# Recommended Base Models:\n",
    "# 1. 'Qwen/Qwen2.5-Coder-7B-Instruct' (SOTA Coding + Multilingual)\n",
    "# 2. 'Qwen/Qwen2.5-7B-Instruct' (General Reasoning + Polyglot)\n",
    "# 3. 'meta-llama/Meta-Llama-3.1-8B-Instruct' (Requires HF token)\n",
    "MODEL_ID = \"Qwen/Qwen2.5-Coder-7B-Instruct\"\n",
    "OUTPUT_DIR = \"anjiru-polyglot-7b-qlora\"\n",
    "\n",
    "print(f\"[*] Configuring 4-Bit NF4 Quantization for: {MODEL_ID}...\")\n",
    "bnb_config = BitsAndBytesConfig(\n",
    "    load_in_4bit=True,\n",
    "    bnb_4bit_quant_type=\"nf4\",\n",
    "    bnb_4bit_use_double_quant=True,\n",
    "    bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16\n",
    ")\n",
    "\n",
    "print(\"[*] Loading tokenizer...\")\n",
    "tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True, trust_remote_code=True)\n",
    "if tokenizer.pad_token is None:\n",
    "    tokenizer.pad_token = tokenizer.eos_token\n",
    "tokenizer.padding_side = \"right\"\n",
    "\n",
    "print(\"[*] Loading 4-bit quantized base model into VRAM...\")\n",
    "model = AutoModelForCausalLM.from_pretrained(\n",
    "    MODEL_ID,\n",
    "    quantization_config=bnb_config,\n",
    "    device_map=\"auto\",\n",
    "    trust_remote_code=True\n",
    ")\n",
    "model = prepare_model_for_kbit_training(model)\n",
    "print(\"[✓] Base model loaded successfully in 4-bit NF4! Fits within ~5.5 GB VRAM.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 4: Attach PEFT LoRA Adapters to All Attention & MLP Projections\n",
    "peft_config = LoraConfig(\n",
    "    r=64,\n",
    "    lora_alpha=128,\n",
    "    target_modules=[\"q_proj\", \"k_proj\", \"v_proj\", \"o_proj\", \"gate_proj\", \"up_proj\", \"down_proj\"],\n",
    "    lora_dropout=0.05,\n",
    "    bias=\"none\",\n",
    "    task_type=\"CAUSAL_LM\"\n",
    ")\n",
    "model = get_peft_model(model, peft_config)\n",
    "print(\"[*] LoRA Trainable Parameters Summary:\")\n",
    "model.print_trainable_parameters()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 5: Upload / Load Dataset & Format using Universal ChatML Template\n",
    "import json\n",
    "from google.colab import files\n",
    "\n",
    "# Instructions for dataset upload:\n",
    "# Upload 'anjiru_colab_fast_train.jsonl' (8 MB, ~4,500 curated balanced records)\n",
    "# or 'anjiru_master_train.jsonl' (63 MB, 45,155 full records)\n",
    "DATASET_FILENAME = \"anjiru_colab_fast_train.jsonl\"\n",
    "\n",
    "if not os.path.exists(DATASET_FILENAME):\n",
    "    print(f\"[*] '{DATASET_FILENAME}' not found in runtime. Please upload it now:\")\n",
    "    uploaded = files.upload()\n",
    "\n",
    "formatted_samples = []\n",
    "with open(DATASET_FILENAME, \"r\", encoding=\"utf-8\") as f:\n",
    "    for line in f:\n",
    "        if not line.strip():\n",
    "            continue\n",
    "        item = json.loads(line)\n",
    "        messages = item.get(\"messages\", [])\n",
    "        if len(messages) >= 2:\n",
    "            # Format using official tokenizer chat template\n",
    "            try:\n",
    "                chat_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)\n",
    "                formatted_samples.append({\"text\": chat_text})\n",
    "            except Exception as e:\n",
    "                pass\n",
    "\n",
    "dataset = Dataset.from_list(formatted_samples)\n",
    "print(f\"[✓] Successfully tokenized and loaded {len(dataset):,} training samples into memory.\")\n",
    "print(\"[*] Sample ChatML Text Preview:\")\n",
    "print(dataset[0][\"text\"][:300] + \"...\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 6: Configure & Execute SFTTrainer (Supervised Fine-Tuning)\n",
    "training_args = TrainingArguments(\n",
    "    output_dir=OUTPUT_DIR,\n",
    "    per_device_train_batch_size=2,\n",
    "    gradient_accumulation_steps=4,\n",
    "    learning_rate=2e-4,\n",
    "    lr_scheduler_type=\"cosine\",\n",
    "    warmup_ratio=0.03,\n",
    "    logging_steps=10,\n",
    "    save_strategy=\"steps\",\n",
    "    save_steps=100,\n",
    "    num_train_epochs=1,\n",
    "    fp16=not torch.cuda.is_bf16_supported(),\n",
    "    bf16=torch.cuda.is_bf16_supported(),\n",
    "    optim=\"paged_adamw_8bit\",\n",
    "    gradient_checkpointing=True,\n",
    "    report_to=\"none\"\n",
    ")\n",
    "\n",
    "trainer = SFTTrainer(\n",
    "    model=model,\n",
    "    train_dataset=dataset,\n",
    "    dataset_text_field=\"text\",\n",
    "    max_seq_length=1024,\n",
    "    tokenizer=tokenizer,\n",
    "    args=training_args\n",
    ")\n",
    "\n",
    "print(\"[*] Starting Anjiru.AI QLoRA Fine-Tuning Loop on Colab T4 GPU...\")\n",
    "trainer.train()\n",
    "print(\"[✓] Training completed successfully!\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 7: Live Inference Verification (Dual-Register & Polyglot Coder)\n",
    "def test_anjiru_inference(user_prompt: str, system_msg: str = \"You are Anjiru.AI, the sovereign Kenyan foundation AI and universal polyglot execution kernel.\"):\n",
    "    messages = [\n",
    "        {\"role\": \"system\", \"content\": system_msg},\n",
    "        {\"role\": \"user\", \"content\": user_prompt}\n",
    "    ]\n",
    "    formatted_input = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)\n",
    "    inputs = tokenizer(formatted_input, return_tensors=\"pt\").to(\"cuda\")\n",
    "    \n",
    "    with torch.no_grad():\n",
    "        outputs = model.generate(\n",
    "            **inputs,\n",
    "            max_new_tokens=400,\n",
    "            temperature=0.3,\n",
    "            top_p=0.9,\n",
    "            do_sample=True,\n",
    "            pad_token_id=tokenizer.pad_token_id\n",
    "        )\n",
    "    \n",
    "    response_tokens = outputs[0][inputs.input_ids.shape[1]:]\n",
    "    response_text = tokenizer.decode(response_tokens, skip_special_tokens=True)\n",
    "    print(f\"\\n{'='*60}\")\n",
    "    print(f\"USER: {user_prompt}\")\n",
    "    print(f\"ANJIRU.AI RESPONSE:\\n{response_text}\")\n",
    "    print(f\"{'='*60}\")\n",
    "\n",
    "# Test 1: Polyglot Coding Execution Plan\n",
    "test_anjiru_inference(\"Tengeneza Rust Actix microservice yenye connection pool ya Postgres na health check endpoint.\")\n",
    "\n",
    "# Test 2: Dual-Track Kenyan Concept Synthesis\n",
    "test_anjiru_inference(\"Explain how microservices handle distributed transactions using the Saga pattern in Kenyan tech sheng.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 8: Save Trained LoRA Adapter & Export Package\n",
    "ADAPTER_PATH = f\"{OUTPUT_DIR}/final_adapter\"\n",
    "model.save_pretrained(ADAPTER_PATH)\n",
    "tokenizer.save_pretrained(ADAPTER_PATH)\n",
    "print(f\"[✓] LoRA adapter weights saved to: {ADAPTER_PATH}\")\n",
    "\n",
    "# Compress adapter folder for easy download to PC\n",
    "!tar -czvf anjiru_adapter.tar.gz -C {OUTPUT_DIR} final_adapter\n",
    "print(\"[✓] Created downloadable archive: anjiru_adapter.tar.gz\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 9: Export Directly to Ollama Modelfile (Option 1 -> Option 3 Bridge!)\n",
    "# This lets you run your fine-tuned model locally in Ollama with zero cloud dependencies!\n",
    "modelfile_content = f\"\"\"# Ollama Modelfile for Anjiru.AI Sovereign Kenyan Foundation Model\n",
    "FROM {MODEL_ID}\n",
    "ADAPTER ./final_adapter\n",
    "\n",
    "PARAMETER temperature 0.3\n",
    "PARAMETER top_p 0.9\n",
    "PARAMETER stop \"<|im_end|>\"\n",
    "PARAMETER stop \"<|endoftext|>\"\n",
    "\n",
    "SYSTEM \\\"\\\"\\\"You are Anjiru.AI, the sovereign Kenyan foundation AI and universal polyglot execution kernel. You write, edit, and debug code across arbitrary stacks and communicate natively in Kiswahili Sanifu, Nairobi Tech Sheng, and English.\\\"\\\"\\\"\n",
    "\"\"\"\n",
    "\n",
    "with open(f\"{OUTPUT_DIR}/Modelfile\", \"w\", encoding=\"utf-8\") as f:\n",
    "    f.write(modelfile_content)\n",
    "\n",
    "print(\"[✓] Generated Ollama Modelfile:\")\n",
    "print(modelfile_content)\n",
    "print(\"\\n[*] How to deploy to your local PC in 2 steps:\")\n",
    "print(\"1. Download 'anjiru_adapter.tar.gz' and extract it on your PC.\")\n",
    "print(\"2. In your terminal, run: ollama create anjiru -f Modelfile\")\n",
    "print(\"3. Anjiru Studio on your PC will automatically detect 'anjiru' in Local Neural Engine!\")"
   ]
  }
 ],
 "metadata": {
  "accelerator": "GPU",
  "colab": {
   "gpuType": "T4",
   "provenance": []
  },
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 0
}

nb_local_path = NOTEBOOKS_DIR / "Train_Anjiru_AI_QLoRA_Colab.ipynb"
with open(nb_local_path, "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=1)

print(f"[✓] Created Colab Notebook at: {nb_local_path}")

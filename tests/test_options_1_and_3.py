"""
tests/test_options_1_and_3.py - Verification Suite for Option 1 (Colab QLoRA) and Option 3 (Local Offline Neural Engine)
Tests:
1. Dataset compilation integrity (ChatML schema, row counts, oversampling of polyglot coder instructions).
2. Modernized Google Colab QLoRA notebook (ChatML tokenization, NF4 bitsandbytes, Ollama Modelfile export).
3. LocalNeuralClient offline resilience and graceful fallback.
4. AnjiruSynthesisEngine integration with LocalNeuralClient.
5. Server API endpoints for neural status and models.
"""

import os
import sys
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.local_neural_client import LocalNeuralClient, get_local_neural_client
from src.anjiru_synthesis_engine import AnjiruSynthesisEngine
from scripts.setup_local_ollama import check_daemon_running, get_installed_models


class TestOption1ColabFineTuning(unittest.TestCase):
    """Verifies all assets and configurations for Option 1 (Colab 4-Bit QLoRA Fine-Tuning)."""

    def setUp(self):
        self.master_dataset_path = PROJECT_ROOT / "data" / "instruction_tuning" / "anjiru_master_train.jsonl"
        self.fast_colab_path = PROJECT_ROOT / "data" / "instruction_tuning" / "anjiru_colab_fast_train.jsonl"
        self.notebook_path = PROJECT_ROOT / "notebooks" / "Train_Anjiru_AI_QLoRA_Colab.ipynb"

    def test_01_master_dataset_exists_and_valid(self):
        self.assertTrue(self.master_dataset_path.exists(), f"Missing master dataset at {self.master_dataset_path}")
        
        # Check first 50 lines for ChatML structure
        with open(self.master_dataset_path, "r", encoding="utf-8") as f:
            for idx in range(50):
                line = f.readline()
                if not line:
                    break
                data = json.loads(line)
                self.assertIn("messages", data, f"Record {idx} missing 'messages' key")
                self.assertIsInstance(data["messages"], list)
                self.assertGreaterEqual(len(data["messages"]), 2)
                roles = [m.get("role") for m in data["messages"]]
                self.assertIn("user", roles)
                self.assertIn("assistant", roles)

    def test_02_fast_colab_dataset_balance_and_oversampling(self):
        self.assertTrue(self.fast_colab_path.exists(), f"Missing fast Colab dataset at {self.fast_colab_path}")
        
        count = 0
        polyglot_count = 0
        academic_count = 0
        linguistic_count = 0

        with open(self.fast_colab_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                count += 1
                item = json.loads(line)
                source = item.get("metadata", {}).get("source", "")
                if source == "polyglot_coder":
                    polyglot_count += 1
                elif source == "academic_scholar":
                    academic_count += 1
                elif source == "linguistic_train":
                    linguistic_count += 1

        self.assertGreaterEqual(count, 4000, f"Fast dataset has {count} rows, expected >= 4000")
        self.assertLessEqual(count, 5500, f"Fast dataset has {count} rows, expected <= 5500")
        self.assertGreaterEqual(polyglot_count, 700, f"Expected polyglot coder oversampled to >= 700, got {polyglot_count}")
        self.assertGreaterEqual(academic_count, 70, f"Expected academic scholar >= 70, got {academic_count}")
        self.assertGreaterEqual(linguistic_count, 3000, f"Expected linguistic samples >= 3000, got {linguistic_count}")

    def test_03_colab_notebook_structure_and_export_cells(self):
        self.assertTrue(self.notebook_path.exists(), f"Missing Colab notebook at {self.notebook_path}")
        
        with open(self.notebook_path, "r", encoding="utf-8") as f:
            nb = json.load(f)

        self.assertIn("cells", nb)
        cells = nb["cells"]
        self.assertGreaterEqual(len(cells), 9, f"Expected at least 9 notebook cells, found {len(cells)}")

        # Check for key technical concepts in cell source
        all_sources = "".join("".join(c.get("source", [])) for c in cells)
        self.assertIn("BitsAndBytesConfig", all_sources)
        self.assertIn("load_in_4bit=True", all_sources)
        self.assertIn("apply_chat_template", all_sources)
        self.assertIn("SFTTrainer", all_sources)
        self.assertIn("Modelfile", all_sources)
        self.assertIn("ollama create anjiru", all_sources)


class TestOption3LocalNeuralEngine(unittest.TestCase):
    """Verifies all assets and behaviors for Option 3 (Local Offline Neural Engine via Ollama/GGUF)."""

    def setUp(self):
        self.client = get_local_neural_client()
        self.synth = AnjiruSynthesisEngine()

    def test_01_client_status_structure(self):
        status = self.client.check_status()
        self.assertIsInstance(status, dict)
        self.assertIn("available", status)
        self.assertIn("provider", status)
        self.assertIn("endpoint", status)
        self.assertIn("models", status)
        self.assertIn("selected_model", status)
        self.assertIn("latency_ms", status)
        self.assertIsInstance(status["models"], list)

    def test_02_client_generate_offline_graceful_handling(self):
        # Client should not crash when offline; it should return None cleanly
        res = self.client.generate("Test prompt", timeout=1)
        # Res is either None (if no server running) or a valid dict (if Ollama happens to be up)
        if res is not None:
            self.assertIn("text", res)
            self.assertIn("provider", res)

    def test_03_synthesis_engine_uses_offline_fallback_safely(self):
        # When local neural is offline, synthesis engine must seamlessly fallback to symbolic knowledge
        prompt = "Write a Python function to compute Fibonacci sequence"
        res = self.synth.synthesize(prompt, language="sheng")
        self.assertEqual(res["status"], "success")
        self.assertIn("content", res)
        self.assertIn("def fibonacci", res["content"].lower())
        self.assertGreater(res["token_stats"]["output_tokens"], 0)

    def test_04_setup_ollama_helper_functions(self):
        # check_daemon_running on dummy invalid port must return False without throwing
        self.assertFalse(check_daemon_running("http://127.0.0.1:54321"))
        self.assertEqual(get_installed_models("http://127.0.0.1:54321"), [])


if __name__ == "__main__":
    unittest.main()

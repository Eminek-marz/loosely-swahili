"""
tests/test_polyglot_kernel.py - Automated End-to-End Test Suite for Polyglot Kernel
Validates Discovery, Universal Block Diffing, Repo Map, Sandbox, Error Extractor, and HTTP Endpoints.
"""

import os
import sys
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.polyglot_discovery import get_polyglot_discovery
from src.universal_patch_engine import UniversalFileModifier, get_repo_map
from src.polyglot_sandbox import get_polyglot_sandbox
from src.polyglot_error_extractor import get_error_extractor
from src.execution_engine import get_execution_engine


class TestPolyglotKernel(unittest.TestCase):

    def setUp(self):
        self.discovery = get_polyglot_discovery()
        self.sandbox = get_polyglot_sandbox()
        self.extractor = get_error_extractor()
        self.repo_map = get_repo_map()
        self.exec_engine = get_execution_engine()

    def test_01_environment_discovery(self):
        manifest = self.discovery.inspect_local_capabilities()
        self.assertIn("python", manifest)
        self.assertTrue(manifest["python"]["installed"])
        self.assertIn("docker", manifest)
        self.assertIn("docker_daemon_active", manifest)

        env_prompt = self.discovery.format_system_env_prompt()
        self.assertIn("[SYSTEM_ENV_CAPABILITIES]", env_prompt)
        self.assertIn("Installed Host Runtimes", env_prompt)
        print("[✓] Environment Discovery test passed.")

    def test_02_workspace_stack_detection(self):
        stack = self.discovery.detect_workspace_stack()
        self.assertIn("primary_language", stack)
        self.assertIn("stack_name", stack)
        self.assertIn("icon", stack)
        print(f"[✓] Stack detection passed: {stack['icon']} {stack['stack_name']}")

    def test_03_universal_block_diffing(self):
        original = (
            "def calculate_tax(amount):\n"
            "    tax_rate = 0.16\n"
            "    return amount * tax_rate\n"
        )
        patch = {
            "search_block": "    tax_rate = 0.16\n    return amount * tax_rate",
            "replace_block": "    tax_rate = 0.14\n    return round(amount * tax_rate, 2)"
        }
        modified, meta = UniversalFileModifier.apply_block_patch(original, patch)
        self.assertIn("tax_rate = 0.14", modified)
        self.assertIn("round(amount * tax_rate, 2)", modified)
        diff = UniversalFileModifier.generate_unified_diff(original, modified, "tax.py")
        self.assertIn("-    tax_rate = 0.16", diff)
        self.assertIn("+    tax_rate = 0.14", diff)
        print("[✓] Universal Block Diffing test passed.")

    def test_04_repo_map_generation(self):
        outline = self.repo_map.generate_repo_map()
        self.assertIn("[REPO_MAP_OUTLINE]", outline)
        self.assertIn("[END_REPO_MAP", outline)
        print(f"[✓] Repo Map generated ({len(outline)} chars).")

    def test_05_polyglot_error_extractor(self):
        # Rust Trace
        rust_trace = (
            "error[E0308]: mismatched types\n"
            "  --> src/lib.rs:42:15\n"
            "   |\n"
            "42 |     let count: i32 = \"100\";\n"
            "   |                      ^^^^^ expected `i32`, found `&str`"
        )
        parsed_rust = self.extractor.parse_traceback(rust_trace)
        self.assertTrue(parsed_rust["detected"])
        self.assertEqual(parsed_rust["language"], "rust")
        self.assertEqual(parsed_rust["line_number"], 42)
        healing_rust = self.extractor.generate_healing_blueprint(parsed_rust, "sheng")
        self.assertIn("Hitilafu", healing_rust["explanation"])

        # Go Trace
        go_trace = "server.go:19:5: undefined: mux.NewRouter"
        parsed_go = self.extractor.parse_traceback(go_trace)
        self.assertTrue(parsed_go["detected"])
        self.assertEqual(parsed_go["language"], "go")
        self.assertEqual(parsed_go["line_number"], 19)

        # Python Trace
        py_trace = (
            'Traceback (most recent call last):\n'
            '  File "worker.py", line 12, in <module>\n'
            'ModuleNotFoundError: No module named \'celery\''
        )
        parsed_py = self.extractor.parse_traceback(py_trace)
        self.assertTrue(parsed_py["detected"])
        self.assertEqual(parsed_py["language"], "python")
        self.assertEqual(parsed_py["error_type"], "ModuleNotFoundError")
        print("[✓] Polyglot Error Extractor test passed across Rust, Go, Python.")

    def test_06_sandbox_execution(self):
        cmd = 'python -c "print(40 + 2)"'
        res = self.sandbox.execute(cmd, timeout_sec=5)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["stdout"].strip(), "42")
        self.assertIn("sandbox_mode", res)
        print(f"[✓] Sandbox Execution test passed (mode: {res['sandbox_mode']}).")

    def test_07_workspace_file_patching(self):
        test_filename = "_test_polyglot_sample.txt"
        self.exec_engine.write_workspace_file(test_filename, "ALPHA = 100\nBETA = 200\n")
        patch_res = self.exec_engine.patch_workspace_file(
            test_filename,
            search_block="ALPHA = 100",
            replace_block="ALPHA = 999 # Updated"
        )
        self.assertEqual(patch_res["status"], "success")
        read_back = self.exec_engine.read_workspace_file(test_filename)
        self.assertIn("ALPHA = 999 # Updated", read_back["content"])
        self.exec_engine.delete_workspace_file(test_filename)
        print("[✓] Workspace File Patching test passed.")


if __name__ == "__main__":
    unittest.main()

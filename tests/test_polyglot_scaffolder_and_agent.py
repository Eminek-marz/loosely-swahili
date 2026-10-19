"""
tests/test_polyglot_scaffolder_and_agent.py - Comprehensive Polyglot Architecture & Agent Tests
Tests all 14 architectures in PolyglotCodebaseScaffolder, intent classification,
ContinuousMultiStepPlanner execution, and dataset integrity.
"""

import unittest
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from src.polyglot_scaffolder import PolyglotCodebaseScaffolder
from src.anjiru_orchestrator import classify_intent, get_orchestrator, ContinuousMultiStepPlanner
from src.anjiru_agent import get_anjiru_agent


class TestPolyglotScaffolderAndAgent(unittest.TestCase):

    def test_all_14_scaffold_architectures(self):
        stacks = [
            ("build a microservice in rust with actix", "rust", ["Cargo.toml", "src/main.rs"]),
            ("create an async cli tool in rust with clap", "rust", ["Cargo.toml", "src/cli.rs"]),
            ("build a concurrent rest api in go", "go", ["go.mod", "main.go"]),
            ("create a concurrent worker pool in go", "go", ["go.mod", "worker/pool.go"]),
            ("build a fullstack next.js 14 dashboard app", "typescript", ["package.json", "app/page.tsx"]),
            ("scaffold an asynchronous fastapi backend", "python", ["requirements.txt", "app/main.py"]),
            ("create a modular typescript backend", "typescript", ["package.json", "src/types.ts"]),
            ("build a real-time websocket server in node", "typescript", ["package.json", "src/room_manager.js"]),
            ("create an async database repository with sqlalchemy 2.0", "python", ["requirements.txt", "app/models.py"]),
            ("develop a modern c++ computational engine with cmake", "c/c++", ["CMakeLists.txt", "include/engine.hpp"]),
            ("synthesize a pytorch deep learning pipeline", "python", ["requirements.txt", "model.py"]),
            ("build a django web application with sqlite", "python", ["manage.py", "config/settings.py"]),
            ("create an enterprise kotlin jvm microservice with gradle", "kotlin", ["build.gradle.kts", "src/main/kotlin/com/anjiru/Application.kt"]),
            ("write a modular algorithmic data processor", "python", ["test_main.py"])
        ]

        for prompt, expected_lang, expected_files in stacks:
            with self.subTest(prompt=prompt):
                res = PolyglotCodebaseScaffolder.scaffold_project(prompt)
                self.assertIn("files", res)
                self.assertGreater(len(res["files"]), 1)
                self.assertEqual(res["language"], expected_lang)
                
                file_names = [f["file"] for f in res["files"]]
                for ef in expected_files:
                    self.assertIn(ef, file_names, f"Expected file '{ef}' not found in {file_names}")
                    
                # Invariant: Every file must have non-empty content and zero placeholders
                for f in res["files"]:
                    content = f.get("content", "")
                    self.assertTrue(len(content.strip()) > 10, f"File {f['file']} has empty or trivial content")
                    self.assertNotIn("# TODO: implement", content)

    def test_intent_classification_polyglot(self):
        test_cases = [
            ("Build a Rust microservice with Actix", "FRAMEWORK", "rust"),
            ("Create a Go concurrent worker pool", "FRAMEWORK", "go_concurrency"),
            ("Build a Next.js 14 dashboard", "FRAMEWORK", "nextjs"),
            ("Scaffold a FastAPI backend", "FRAMEWORK", "fastapi"),
            ("Build a WebSocket real-time server", "FRAMEWORK", "websocket"),
            ("Develop a C++ CMake engine", "FRAMEWORK", "cpp"),
            ("Synthesize a PyTorch neural pipeline", "FRAMEWORK", "ml"),
            ("Create a Kotlin Gradle service", "FRAMEWORK", "kotlin"),
            ("Build an async SQLAlchemy database layer", "FRAMEWORK", "sqlalchemy"),
        ]

        for prompt, expected_type, expected_fw in test_cases:
            with self.subTest(prompt=prompt):
                intent = classify_intent(prompt)
                self.assertEqual(intent["type"], expected_type)
                self.assertEqual(intent["framework"], expected_fw)

    def test_continuous_multi_step_planner(self):
        orch = get_orchestrator()
        planner = ContinuousMultiStepPlanner(orch)
        plan = planner.generate_plan("Build a high-performance memory-safe web microservice in Rust with Actix-web")
        self.assertGreaterEqual(len(plan), 3)
        files = [p["file"] for p in plan]
        self.assertIn("Cargo.toml", files)
        self.assertIn("src/main.rs", files)

    def test_dataset_jsonl_integrity(self):
        dataset_path = PROJECT_ROOT / "data" / "instruction_tuning" / "polyglot_coder_instructions.jsonl"
        self.assertTrue(dataset_path.exists())
        
        valid_records = 0
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    self.assertIn("messages", rec)
                    self.assertEqual(len(rec["messages"]), 3)
                    self.assertEqual(rec["messages"][0]["role"], "system")
                    self.assertEqual(rec["messages"][1]["role"], "user")
                    self.assertEqual(rec["messages"][2]["role"], "assistant")
                    self.assertIn("[EXECUTION_KERNEL_PLAN]", rec["messages"][2]["content"])
                    valid_records += 1

    def test_extended_polyglot_architectures(self):
        extended_stacks = [
            ("build a memory allocator in zig", "zig", ["build.zig", "src/main.zig"]),
            ("build a game physics engine in odin", "odin", ["src/main.odin"]),
            ("create an erc20 staking smart contract in solidity", "solidity", ["package.json", "contracts/TokenContract.sol"]),
            ("create a mobile banking app in flutter with dart", "dart", ["pubspec.yaml", "lib/main.dart"]),
            ("build an ios patient management app in swiftui", "swift", ["Package.swift", "Sources/App/main.swift"]),
            ("build an api microservice in c# asp.net core", "csharp", ["AnjiruApi.csproj", "Program.cs"]),
            ("build an ecommerce backend in php laravel", "php", ["composer.json", "routes/api.php"]),
            ("create a restful api in ruby on rails", "ruby", ["Gemfile", "config/routes.rb"]),
            ("build a dashboard in vue 3 with vite", "typescript", ["package.json", "src/App.vue"]),
            ("build a reactive web app in sveltekit", "typescript", ["package.json", "src/routes/+page.svelte"]),
            ("build an enterprise patient portal in angular", "typescript", ["package.json", "src/app/app.component.ts"]),
            ("build a high performance http server in bun", "typescript", ["package.json", "src/index.ts"]),
            ("create terraform infrastructure and kubernetes deployment", "terraform/hcl", ["Dockerfile", "terraform/main.tf", "k8s/deployment.yaml"]),
            ("build a rag pipeline with qdrant and langchain", "python", ["requirements.txt", "app/rag_pipeline.py"]),
            ("build a banking microservice in java with spring boot", "java", ["pom.xml", "src/main/java/com/anjiru/Application.java"]),
            ("create a scientific simulation module in julia", "julia", ["Project.toml", "src/AnjiruScientific.jl"]),
            ("design a postgresql database schema with migrations", "sql", ["migrations/001_initial_schema.sql"])
        ]

        for prompt, expected_lang, expected_files in extended_stacks:
            with self.subTest(prompt=prompt):
                res = PolyglotCodebaseScaffolder.scaffold_project(prompt)
                self.assertIn("files", res)
                self.assertGreater(len(res["files"]), 0)
                self.assertEqual(res["language"], expected_lang)
                file_names = [f["file"] for f in res["files"]]
                for ef in expected_files:
                    self.assertIn(ef, file_names, f"Expected file '{ef}' not found in {file_names}")
                for f in res["files"]:
                    content = f.get("content", "")
                    self.assertTrue(len(content.strip()) > 10, f"File {f['file']} has empty content")
                    self.assertNotIn("# TODO: implement", content)

    def test_polyglot_agent_action_detection(self):
        agent = get_anjiru_agent()
        test_prompts = [
            ("Create a file called main.zig that implements an arena memory allocator", "create_file", "main.zig"),
            ("Create a file named Token.sol for an ERC20 token", "create_file", "Token.sol"),
            ("Tengeneza faili inayoitwa models.dart", "create_file", "models.dart"),
            ("Write a script called service.cs that handles banking transactions", "create_file", "service.cs"),
            ("Create a file named app.vue with a counter component", "create_file", "app.vue"),
        ]

        for p, expected_action, expected_fn in test_prompts:
            with self.subTest(prompt=p):
                is_act, action, params = agent.is_action_request(p)
                self.assertTrue(is_act)
                self.assertEqual(action, expected_action)
                self.assertEqual(params.get("raw_filename"), expected_fn)

    def test_domain_entity_fidelity(self):
        from src.universal_polyglot_builder import extract_prompt_domain_and_entities
        
        test_pairs = [
            ("Build a hospital clinic patient management system", "Patient"),
            ("Create an ecommerce shop product catalog and checkout", "Product"),
            ("Build an mpesa banking wallet transaction engine", "Account"),
            ("Develop a high-performance 3D raytracer with spheres and rays", "Sphere"),
            ("Build an arena memory allocator with heap buffer", "MemoryBlock"),
            ("Create an ERC-20 staking token smart contract", "Token"),
            ("Build a university education course portal for students", "Student"),
            ("Create a library catalog system for books and authors", "Book"),
            ("Develop a logistics fleet delivery transport tracking system", "Delivery"),
            ("Build an IoT sensor telemetry monitoring hub", "SensorReading"),
        ]

        for prompt, expected_entity in test_pairs:
            with self.subTest(prompt=prompt):
                meta = extract_prompt_domain_and_entities(prompt)
                self.assertEqual(meta["entity"], expected_entity)


if __name__ == "__main__":
    unittest.main()


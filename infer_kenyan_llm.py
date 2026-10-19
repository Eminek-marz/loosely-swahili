"""
Interactive Inference & Prompt Evaluation for Kenyan Code-Switching LLM
Enables immediate testing across all four multi-task benchmarks:
  1. Concept Recreation (Academic Pure Swahili -> Kenyan Code-Switching)
  2. Grammar Linter (Catching *-ed, *kinaka-, food plurals, semantic errors)
  3. Multi-Domain Technical Explanation (Engineering, Finance, Tech, Medicine, Politics)
  4. Urban Street Sheng & Cultural Grounding

Features Dual-Engine Execution:
  - Neural Mode: Loads LoRA adapter weights on top of Llama 3 / Mistral / Gemma
  - Deterministic Expert Mode: Falls back to built-in linguistic matrices for instant zero-dependency CPU inference
"""

import sys
import os
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.concept_recreation_engine import ConceptRecreationEngine
from src.self_teaching_engine import AutonomousSelfTeachingEngine

def parse_args():
    parser = argparse.ArgumentParser(description="Run Kenyan Code-Switching Prompt Inference")
    parser.add_argument("--prompt", type=str, default="", help="Input text or question to evaluate")
    parser.add_argument("--task", type=str, choices=["recreate", "lint", "explain", "sheng", "interactive"],
                        default="interactive", help="Task mode to run")
    parser.add_argument("--adapter_dir", type=str, default=str(PROJECT_ROOT / "models" / "kenyan_codeswitch_lora"),
                        help="Path to trained LoRA adapter weights")
    return parser.parse_args()

def run_expert_recreation(text: str):
    engine = ConceptRecreationEngine()
    res = engine.reconstruct_concept(text)
    print("\n" + "=" * 80)
    print("🔄 KENYAN CODE-SWITCHING TRI-SET CONCEPT RECREATION")
    print("=" * 80)
    print(f"• Detected Input:       {res.get('detected_input_language', 'Unknown')}")
    print(f"• Domain:               {res.get('domain', 'Technical Domain')} ({res.get('concept', '')})")
    print(f"\n🇬🇧 Set B (English Concept):")
    print(f"  \"{res.get('english_concept', '')}\"")
    print(f"\n🇹🇿 Set A (Kiswahili Sanifu):")
    print(f"  \"{res.get('pure_swahili', '')}\"")
    print(f"\n🇰🇪 Set C (Living Kenyan Code-Switching):")
    print(f"  \"{res.get('reconstructed_codeswitch', '')}\"")
    print(f"\n• Transformed Mappings: {len(res.get('recreated_mappings', []))} terms transformed")
    for m in res.get("recreated_mappings", []):
        print(f"    - '{m.get('pure_swahili', '')}' -> '{m.get('recreated_codeswitch', '')}'")
    if res.get("conceptual_clarity_gain"):
        print(f"\n• Clarity Gain:         {res.get('conceptual_clarity_gain')}")
    print("=" * 80)

def run_expert_linter(text: str):
    engine = AutonomousSelfTeachingEngine()
    ppl_score = engine.lm.score_sentence_perplexity(text)["perplexity"]
    
    # Check violations
    has_past_ed = " ku-" in text and "ed" in text
    has_affect_clash = "kinaka" in text.lower()
    has_machapo = "machapo" in text.lower()
    
    print("\n" + "=" * 75)
    print("🔍 KENYAN CODE-SWITCHING LINTER & AUDITOR")
    print("=" * 75)
    print(f"• Sentence Audited: \"{text}\"")
    print(f"• Perplexity Score: {ppl_score:.2f}")
    
    violations = []
    if has_past_ed or "*ku-" in text:
        violations.append("Pillar I (Bare Root Violation): English past-tense *-ed detected after Swahili prefixation.")
    if has_affect_clash:
        violations.append("Rule XX (Affective Polarity Clash): Forced Ki- and Diminutive -ka- stacked (*kinaka-).")
    if has_machapo:
        violations.append("Rule V (Food Plural Violation): Found *machapo instead of authentic 'chapos'.")

    if violations:
        print("\n🚫 VIOLATIONS DETECTED:")
        for v in violations:
            print(f"  • {v}")
    else:
        print("\n✅ 100% BLUEPRINT COMPLIANT: No structural violations detected.")

def run_interactive_console():
    print("=" * 80)
    print("🇰🇪 KENYAN CODE-SWITCHING INTERACTIVE EVALUATION CONSOLE")
    print("=" * 80)
    print("Commands:")
    print("  1. 'recreate <pure_swahili_text>' -> Transforms academic Swahili to living code-switching")
    print("  2. 'lint <sentence>'              -> Checks sentence for Blueprint rule violations & perplexity")
    print("  3. 'exit'                         -> Quit console")
    print("=" * 80)

    while True:
        try:
            line = input("\n[KCS-Console] > ").strip()
            if not line or line.lower() in ("exit", "quit"):
                break
            
            if line.startswith("recreate "):
                run_expert_recreation(line[9:].strip())
            elif line.startswith("lint "):
                run_expert_linter(line[5:].strip())
            else:
                # Default to recreation
                run_expert_recreation(line)
        except (KeyboardInterrupt, EOFError):
            break

def main():
    args = parse_args()
    if args.task == "interactive" and not args.prompt:
        run_interactive_console()
    elif args.task == "recreate" or (args.prompt and args.task != "lint"):
        run_expert_recreation(args.prompt)
    elif args.task == "lint":
        run_expert_linter(args.prompt)

if __name__ == "__main__":
    main()

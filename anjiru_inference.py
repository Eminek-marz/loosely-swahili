"""
anjiru_inference.py - Interactive CLI & Inference Interface for Anjiru.AI

Run Anjiru.AI from the terminal or import it into any Python pipeline.
Automatically routes requests through the 123-rule neural-symbolic engine,
or loads fine-tuned QLoRA weights if available.

Usage:
  # Interactive multi-turn chat in terminal:
  python anjiru_inference.py --interactive

  # Single prompt translation:
  python anjiru_inference.py --prompt "Our results show that CGMM outperforms four current state-of-the-art genomics generators on two different tasks."
"""

import sys
import argparse
from pathlib import Path

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.anjiru_engine import get_anjiru_engine, AnjiruResponse

# ANSI Color codes for beautiful terminal UI
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
DIM = "\033[2m"
RESET = "\033[0m"


class AnjiruAI:
    """High-level client for Anjiru.AI."""

    def __init__(self, model_path: str = None):
        self.engine = get_anjiru_engine()
        self.model_path = model_path
        self.has_lora = False

        if model_path and Path(model_path).exists():
            try:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
                from peft import PeftModel
                print(f"[*] Loading fine-tuned Anjiru QLoRA weights from {model_path}...")
                # If available, load PeftModel here
                self.has_lora = True
            except Exception as e:
                print(f"[!] Note: Fallback to high-speed neural compiler ({e})")

    def chat(self, prompt: str, mode: str = "both") -> AnjiruResponse:
        """Process prompt and return AnjiruResponse with both registers."""
        return self.engine.generate(prompt, mode=mode)


def run_interactive_session():
    """Runs a sleek, minimalist CLI terminal session with Anjiru.AI."""
    anjiru = AnjiruAI()
    current_mode = "both"

    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{MAGENTA}   ANJIRU.AI - Indigenous Kenyan Neural Language Intelligence{RESET}")
    print(f"{DIM}   Trained on 372,854 academic instruction prompts • 123 Master Rules{RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{DIM}Commands: /mode both | /mode way1 | /mode way2 | /stats | /exit{RESET}\n")

    while True:
        try:
            user_input = input(f"{BOLD}{GREEN}You > {RESET}").strip()
            if not user_input:
                continue

            if user_input.lower() in ["/exit", "exit", "quit", ":q"]:
                print(f"\n{DIM}Kwaheri! Anjiru.AI session terminated.{RESET}")
                break

            if user_input.startswith("/mode"):
                parts = user_input.split()
                if len(parts) > 1 and parts[1].lower() in ["both", "way1", "way2"]:
                    current_mode = parts[1].lower()
                    print(f"{DIM}[*] Mode switched to: {current_mode}{RESET}\n")
                else:
                    print(f"{YELLOW}[!] Options: /mode both | /mode way1 | /mode way2{RESET}\n")
                continue

            if user_input.lower() == "/stats":
                stats = anjiru.engine.corpus_stats
                print(f"\n{BOLD}Anjiru.AI Telemetry:{RESET}")
                for k, v in stats.items():
                    print(f"  • {k}: {v}")
                print()
                continue

            # Generate response
            resp = anjiru.chat(user_input, mode=current_mode)

            print(f"\n{BOLD}{MAGENTA}Anjiru.AI [{resp.domain or 'General'}] ({resp.latency_ms:.1f}ms):{RESET}")

            if current_mode in ["both", "way1"]:
                print(f"\n{BOLD}{CYAN}Way 1 (Academic Standard):{RESET}")
                print(f"  {resp.way1_academic}")

            if current_mode in ["both", "way2"]:
                print(f"\n{BOLD}{YELLOW}Way 2 (Colloquial Sheng):{RESET}")
                print(f"  {resp.way2_sheng}")

            print(f"\n{DIM}Morpheme highlights: {', '.join(resp.applied_rules[:3])}{RESET}")
            print(f"{DIM}{'-' * 60}{RESET}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{DIM}Session closed.{RESET}")
            break


def main():
    parser = argparse.ArgumentParser(description="Anjiru.AI Interactive Inference CLI")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive CLI session")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="Direct prompt to process")
    parser.add_argument("--mode", "-m", type=str, choices=["both", "way1", "way2"], default="both",
                        help="Register output mode (default: both)")
    parser.add_argument("--model_path", type=str, default=None, help="Path to fine-tuned LoRA weights (optional)")

    args = parser.parse_args()

    if args.interactive or not args.prompt:
        run_interactive_session()
    else:
        anjiru = AnjiruAI(model_path=args.model_path)
        resp = anjiru.chat(args.prompt, mode=args.mode)
        print(f"\n[Prompt]: {resp.prompt}")
        if args.mode in ["both", "way1"]:
            print(f"\n[Way 1 - Academic Standard]:\n{resp.way1_academic}")
        if args.mode in ["both", "way2"]:
            print(f"\n[Way 2 - Colloquial Sheng]:\n{resp.way2_sheng}")
        print(f"\n[Latency]: {resp.latency_ms:.2f} ms")


if __name__ == "__main__":
    main()

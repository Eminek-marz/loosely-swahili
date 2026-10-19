"""
Kenyan Podcast Voice & Code-Switching ASR (Speech-to-Text) Blueprint
Solves the out-of-sync, hallucinated YouTube subtitle issue by biasing Whisper / Meta MMS
with Kenyan code-switching vocabulary and applying post-ASR morphological restoration.
"""

import sys
import os
import json
import argparse
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent

KENYAN_ASR_BIAS_PROMPT = (
    "Sheng, Kiswahili Sanifu, na English code-switching ya Nairobi. "
    "Maneno kama: alifiriwa, amecaniwa, unaniconfuse, ilifriziwa, mayouth, "
    "luku safi, chapaa, nduthi, nganya, keja, buda, msee, mresh, sonko, rada, "
    "kula fare, bana, enyewe, yaani, Westlands, Eastlands, Kanairo, arbantone."
)

def build_asr_instruction_guide():
    return {
        "problem": "Standard YouTube/Whisper ASR is locked into 100% English or 100% Swahili, causing timestamp drift and acoustic hallucinations on Kenyan podcasts.",
        "solution_architecture": [
            {
                "step": 1,
                "name": "Audio Preprocessing & VAD (Voice Activity Detection)",
                "tool": "Silero VAD / ffmpeg",
                "action": "Split 1-2 hour podcast episodes (e.g. Iko Nini, Mic Cheque) into 15-30 second clean vocal segments, removing background studio music."
            },
            {
                "step": 2,
                "name": "Prompt-Biased Whisper Decoding",
                "tool": "Faster-Whisper / OpenAI Whisper",
                "action": "Inject KENYAN_ASR_BIAS_PROMPT into Whisper's decoder so it recognizes hybrid verbs (alifiriwa, amecaniwa) instead of hallucinating English words."
            },
            {
                "step": 3,
                "name": "Post-ASR Morphological Normalization",
                "tool": "ShengNormalizerPipeline",
                "action": "Run raw transcript segments through our Bantu engine to correct loan roots and generate parallel Sanifu Swahili & English training triples."
            }
        ]
    }

def transcribe_audio_snippet(audio_path: str, model_size: str = "base"):
    """
    Demonstrates running vocabulary-biased Whisper on a Kenyan audio file.
    """
    print("=" * 75)
    print("🎙️ KENYAN CODE-SWITCHING VOICE TRANSCRIBER (BIAS-AUGMENTED ASR)")
    print("=" * 75)
    print(f"Target Audio: {audio_path}")
    print(f"ASR Model: Whisper ({model_size}) with Sheng Lexical Biasing")
    print(f"Vocabulary Bias Prompt: {KENYAN_ASR_BIAS_PROMPT[:80]}...")

    try:
        import whisper
        print("\n[*] Loading Whisper model...")
        model = whisper.load_model(model_size)
        print("[*] Transcribing audio with Kenyan linguistic biasing...")
        result = model.transcribe(
            audio_path,
            initial_prompt=KENYAN_ASR_BIAS_PROMPT,
            language="sw", # Swahili acoustic base with code-switching prompt
            temperature=0.0
        )
        print("\n[+] Transcribed Clean Dialogue:")
        print(result["text"])
        return result["text"]
    except ImportError:
        print("\n[INFO] To run live audio transcription on local mp3/wav files:")
        print("       pip install openai-whisper")
        print("\n[*] The Prompt-Biased ASR Blueprint is configured and ready.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kenyan Code-Switching Podcast ASR Transcriber")
    parser.add_argument("--audio", "-a", type=str, help="Path to audio file (mp3/wav)")
    parser.add_argument("--model", "-m", type=str, default="base", help="Whisper model size (tiny, base, small, medium)")
    args = parser.parse_args()

    if args.audio:
        transcribe_audio_snippet(args.audio, args.model)
    else:
        guide = build_asr_instruction_guide()
        print(json.dumps(guide, indent=2, ensure_ascii=False))

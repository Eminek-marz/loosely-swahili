"""
Exports custom Sheng-aware vocabulary to Hugging Face Tokenizer format.
"""

from pathlib import Path
import json
from src.tokenizer import ShengCodeSwitchTokenizer

def main():
    tokenizer = ShengCodeSwitchTokenizer()
    export_path = Path(__file__).resolve().parent / "data" / "sheng_tokenizer_vocab.json"
    result = tokenizer.export_huggingface_vocab(export_path)
    print(f"[SUCCESS] Exported {len(tokenizer.vocab)} tokens to {result}")

    # Also write a standard vocab.txt
    vocab_txt_path = Path(__file__).resolve().parent / "data" / "vocab.txt"
    with open(vocab_txt_path, "w", encoding="utf-8") as f:
        for idx in range(len(tokenizer.inv_vocab)):
            tok = tokenizer.inv_vocab[idx]
            f.write(f"{tok}\n")
    print(f"[SUCCESS] Exported plain vocab file to {vocab_txt_path}")

if __name__ == "__main__":
    main()

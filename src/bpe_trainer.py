"""
Morpheme-Constrained BPE (Byte-Pair Encoding) Trainer for Kenyan Code-Switching.
Demonstrates why standard naive BPE fails and how Morpheme-Aware BPE produces superior tokens.
"""

import re
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict, Tuple, Set, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class ShengBPETrainer:
    def __init__(self, vocab_size: int = 500):
        self.target_vocab_size = vocab_size
        self.bantu_prefixes = ["ma", "ku", "wa", "ka", "vi", "ki", "tuta", "wata", "nili", "tuli", "wali", "unani", "alitughost"]
        self.locative_suffixes = ["ni"]

    def pre_tokenize_naive(self, text: str) -> List[List[str]]:
        """Standard BPE: splits text into space-separated words, then raw characters."""
        words = re.findall(r"[a-zA-Z]+", text.lower())
        # Each word is represented as a list of characters ending with a special end-of-word marker </w>
        tokenized_corpus = []
        for w in words:
            chars = list(w) + ["</w>"]
            tokenized_corpus.append(chars)
        return tokenized_corpus

    def pre_tokenize_morpheme_aware(self, text: str) -> List[List[str]]:
        """
        BETTER BPE (Sheng-BPE):
        Respects Bantu agglutinative prefix and suffix boundaries BEFORE merging.
        Prevents slicing across grammatical roots.
        """
        words = re.findall(r"[a-zA-Z]+", text.lower())
        tokenized_corpus = []
        
        for w in words:
            # 1. Check for Locative suffix '-ni' (e.g. mtaani -> mtaa + -ni)
            if len(w) > 4 and w.endswith("ni"):
                stem = w[:-2]
                tokenized_corpus.append(list(stem) + ["@@"])
                tokenized_corpus.append(["-ni</w>"])
                continue

            # 2. Check for Bantu Pluralizer / Verbal prefixes (e.g. mayouth -> ma@@ + youth)
            matched_prefix = None
            for p in sorted(self.bantu_prefixes, key=len, reverse=True):
                if w.startswith(p) and len(w) > len(p) + 2:
                    matched_prefix = p
                    break

            if matched_prefix:
                stem = w[len(matched_prefix):]
                # Keep prefix as a protected morpheme block, then characters of stem
                tokenized_corpus.append([f"{matched_prefix}@@"])
                tokenized_corpus.append(list(stem) + ["</w>"])
            else:
                tokenized_corpus.append(list(w) + ["</w>"])

        return tokenized_corpus

    def get_stats(self, corpus: List[List[str]]) -> Counter:
        """Count all adjacent symbol pairs in the corpus."""
        pairs = Counter()
        for word_tokens in corpus:
            for i in range(len(word_tokens) - 1):
                pairs[(word_tokens[i], word_tokens[i + 1])] += 1
        return pairs

    def merge_pair(self, pair: Tuple[str, str], corpus: List[List[str]]) -> List[List[str]]:
        """Merge all occurrences of the most frequent pair in the corpus."""
        bigram = re.escape(" ".join(pair))
        pattern = re.compile(r"(?<!\S)" + bigram + r"(?!\S)")
        new_corpus = []
        for word_tokens in corpus:
            word_str = " ".join(word_tokens)
            new_word_str = pattern.sub("".join(pair), word_str)
            new_corpus.append(new_word_str.split())
        return new_corpus

    def train(self, raw_text: str, mode: str = "morpheme_aware", num_merges: int = 50) -> Dict[str, Any]:
        """Runs the BPE merge training loop."""
        if mode == "morpheme_aware":
            corpus = self.pre_tokenize_morpheme_aware(raw_text)
        else:
            corpus = self.pre_tokenize_naive(raw_text)

        merges = []
        for step in range(num_merges):
            pairs = self.get_stats(corpus)
            if not pairs:
                break
            best_pair, count = pairs.most_common(1)[0]
            if count < 2:  # Stop if pairs don't repeat
                break
            corpus = self.merge_pair(best_pair, corpus)
            merges.append({"step": step + 1, "pair": best_pair, "merged": "".join(best_pair), "frequency": count})

        # Collect final vocabulary
        vocab = set()
        for word_tokens in corpus:
            for tok in word_tokens:
                vocab.add(tok)

        return {
            "mode": mode,
            "merges_performed": len(merges),
            "top_merges": merges[:15],
            "final_sample_tokens": list(vocab)[:30]
        }

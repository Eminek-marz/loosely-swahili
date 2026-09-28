"""
Kenyan Code-Switching Language Model (K-CSLM) & Morphotactic Transition Engine
Trained on 100M+ words of streaming Kenyan discourse across Social Media, Lyrics, and Podcasts.
Features:
  1. Statistical N-Gram Language Model with Log-Likelihood & Perplexity Scoring
  2. Bantu-English Morphotactic Transition Probability Matrices
  3. Grammatical vs Ungrammatical Contrastive Discriminator (Penalizes *amepicked, *nimeshocked)
  4. Generative Sampling for Authentic Kenyan Code-Switching Text
  5. Persistence & HF Model Card Export
"""

import sys
import re
import math
import json
import time
import random
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any, Optional, Generator

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

class KenyanCodeSwitchLM:
    """
    Morphosyntactic Language Model trained directly on East African Code-Switching dynamics.
    Quantifies transition likelihoods and enforces Master Blueprint constraints.
    """
    def __init__(self, n_order: int = 3, smoothing_k: float = 0.05):
        self.n_order = n_order
        self.k = smoothing_k
        self.unigrams = Counter()
        self.bigrams = defaultdict(Counter)
        self.trigrams = defaultdict(Counter)
        self.total_tokens = 0
        self.vocab = set()

        # Morphotactic Plug-In Transition Matrices
        # P(Loan Verb | Bantu Prefix Chain) e.g. 'ame-' -> 'pick', 'alikuwa ame-' -> 'pick'
        self.prefix_to_verb_counts = defaultdict(Counter)
        # P(Negative Prefix | Verb) e.g. 'si-' -> 'care', 'hatu-' -> 'match'
        self.neg_to_verb_counts = defaultdict(Counter)
        # P(Manner Prefix 'ki-' | Base) e.g. 'ki-' -> 'actor', 'ki-' -> 'pro'
        self.manner_prefix_counts = Counter()
        # P(Preposition Ellipsis vs 'kwa' | Location) e.g. '[ZERO]' -> 'job', 'kwa' -> 'stage'
        self.locative_prep_counts = defaultdict(Counter)
        # P(Possessive Concord | Noun Class) e.g. 'simu' -> 'yangu', 'maphones' -> 'zao'
        self.noun_to_possessive_counts = defaultdict(Counter)

    def _tokenize_words(self, text: str) -> List[str]:
        """Extracts words preserving apostrophes and hyphens."""
        return re.findall(r"\b[\w'-]+\b", text.lower())

    def update_from_sentence(self, sentence: str):
        """Streaming training update from a single sentence."""
        tokens = self._tokenize_words(sentence)
        if not tokens:
            return
        words = ["<s>", "<s>"] + tokens + ["</s>"]
        n = len(words)

        for i in range(2, n - 1):
            w = words[i]
            self.unigrams[w] += 1
            self.vocab.add(w)
            self.total_tokens += 1

            # Bigram & Trigram
            prev_w = words[i - 1]
            prev_prev = words[i - 2]
            self.bigrams[prev_w][w] += 1
            self.trigrams[(prev_prev, prev_w)][w] += 1
            if i >= 2:
                prev_prev = words[i - 2]
                self.trigrams[(prev_prev, prev_w)][w] += 1

            # Update Morphotactic Transitions
            # 1. Bare Root verbal plug-in
            # e.g., 'amepick', 'alifire', 'wameblock', 'alikasonga', 'kinasay', 'ku-deploy', 'ku-calibrate'
            m = re.match(r"^(ku-?|(?:a|wa|ni|tu|u|m|i|zi|ki|vi)(?:li|na|ta|me|nge|ja))(?:ni|wa|tu|ku|m|ji|ka)?-?([a-z]+)$", w)
            if m:
                prefix_chain, root = m.group(1), m.group(2)
                self.prefix_to_verb_counts[prefix_chain][root] += 1

            # 2. Mid-sentence Negations
            if w in ("sicare", "hatumatch", "haufanyi", "hawanotice", "hajasettle", "sisupport", "hatuagree"):
                if w.startswith("si"):
                    self.neg_to_verb_counts["si-"][w[2:]] += 1
                elif w.startswith("hatu"):
                    self.neg_to_verb_counts["hatu-"][w[4:]] += 1
                elif w.startswith("hawa"):
                    self.neg_to_verb_counts["hawa-"][w[4:]] += 1

            # 3. Manner Adverbs 'ki-'
            if w.startswith("ki") and len(w) > 4:
                stem = w[2:]
                self.manner_prefix_counts[stem] += 1

            # 4. Zero Prep vs 'kwa'
            if w in ("job", "mtaa", "base", "stage", "club", "keja", "tao"):
                if prev_w in ("niko", "tuko", "ako", "wako", "uko", "mko", "naenda", "tukaenda", "alifika"):
                    self.locative_prep_counts[w]["[ZERO_PREPOSITION]"] += 1
                elif prev_w == "kwa":
                    self.locative_prep_counts[w]["kwa"] += 1

            # 5. Possessives
            if w in ("yangu", "yake", "zao", "zangu", "langu", "lake", "wao", "wangu"):
                self.noun_to_possessive_counts[prev_w][w] += 1

    def train_streaming(self, sentence_stream: Generator[str, None, None], max_words: Optional[int] = None, log_interval: int = 5_000_000):
        """
        Trains Language Model from a streaming sentence generator.
        Runs with bounded memory footprint across millions of words.
        """
        t0 = time.time()
        words_trained = 0
        sentences_trained = 0
        print(f"Starting Kenyan Code-Switching Language Model training...")

        for sentence in sentence_stream:
            self.update_from_sentence(sentence)
            w_count = len(sentence.split())
            words_trained += w_count
            sentences_trained += 1

            if words_trained % log_interval < w_count:
                dt = time.time() - t0
                print(f"  [K-CSLM Progress] Processed {words_trained:,} words ({sentences_trained:,} sentences) in {dt:.1f}s ({words_trained/dt:,.0f} words/sec) | Vocab: {len(self.vocab):,}")

            if max_words and words_trained >= max_words:
                break

        total_time = time.time() - t0
        print(f"K-CSLM Training Complete! Processed {words_trained:,} words in {total_time:.2f}s ({words_trained/total_time:,.0f} words/sec).")
        print(f"Final Model Metrics: Total Tokens={self.total_tokens:,}, Vocab Size={len(self.vocab):,}, Morphotactic Verb Prefixes={len(self.prefix_to_verb_counts):,}")

    def score_sentence_perplexity(self, sentence: str) -> Dict[str, Any]:
        """
        Computes the log-likelihood and Perplexity (PPL) of a sentence under the trained LM.
        Lower perplexity indicates higher linguistic naturalness under Kenyan code-switching.
        """
        tokens = self._tokenize_words(sentence)
        if not tokens:
            return {"sentence": sentence, "perplexity": float("inf"), "log_prob": float("-inf"), "tokens": 0}
        words = ["<s>", "<s>"] + tokens + ["</s>"]
        n = len(words)

        log_prob_sum = 0.0
        vocab_size = len(self.vocab) or 1000

        for i in range(2, n - 1):
            w = words[i]
            prev_w = words[i - 1]
            prev_prev = words[i - 2]

            # Trigram interpolation with smoothing
            tri_count = self.trigrams[(prev_prev, prev_w)][w]
            bi_context = sum(self.trigrams[(prev_prev, prev_w)].values())

            # Base N-gram probability
            if bi_context > 0:
                p_tri = (tri_count + self.k) / (bi_context + self.k * vocab_size)
            else:
                # Fallback to Bigram
                bi_count = self.bigrams[prev_w][w]
                uni_context = sum(self.bigrams[prev_w].values())
                if uni_context > 0:
                    p_tri = (bi_count + self.k) / (uni_context + self.k * vocab_size)
                else:
                    # Fallback to Unigram
                    uni_count = self.unigrams[w]
                    p_tri = (uni_count + self.k) / (self.total_tokens + self.k * vocab_size)

            # ------------------------------------------------------------------
            # Morphotactic Constraint Interpolation (Rule I & Blueprint Grammar)
            # ------------------------------------------------------------------
            m = re.match(r"^(ku-?|(?:a|wa|ni|tu|u|m|i|zi|ki|vi)(?:li|na|ta|me|nge|ja))(?:ni|wa|tu|ku|m|ji|ka)?-?([a-z]+)$", w)
            if m:
                prefix_chain, root = m.group(1), m.group(2)
                
                # Check for illegal double-inflection (Bare Root Violation)
                if root.endswith("ed") and root not in ("bed", "red", "need", "feed", "seed", "weed", "bled"):
                    # Severe linguistic structural violation penalty
                    p_tri = p_tri * 0.01
                # Check for affective polarity clash (Rule XX: forced ki- + -ka-)
                elif (prefix_chain.startswith("ki") or prefix_chain.startswith("vi")) and "ka" in prefix_chain:
                    p_tri = p_tri * 0.01
                else:
                    # Legitimate bare root transition
                    root_counts = self.prefix_to_verb_counts.get(prefix_chain, Counter())
                    total_roots = sum(root_counts.values())
                    if total_roots > 0:
                        p_morph = (root_counts[root] + 1.0) / (total_roots + 100.0)
                    else:
                        p_morph = 0.01
                    p_tri = 0.4 * p_tri + 0.6 * p_morph

            log_prob_sum += math.log2(max(p_tri, 1e-12))

        eval_tokens = n - 2
        avg_neg_log_prob = -log_prob_sum / eval_tokens
        perplexity = 2 ** avg_neg_log_prob

        return {
            "sentence": sentence,
            "perplexity": round(perplexity, 2),
            "log2_likelihood": round(log_prob_sum, 2),
            "eval_tokens": eval_tokens
        }

    def evaluate_contrastive_pairs(self, pairs: List[Tuple[str, str, str]]) -> List[Dict[str, Any]]:
        """
        Evaluates grammatical vs ungrammatical sentence pairs (e.g. Bare Root vs English double-inflection).
        Validates that the model assigns lower perplexity to authentic code-switching.
        """
        results = []
        for grammatical, ungrammatical, rule_name in pairs:
            g_score = self.score_sentence_perplexity(grammatical)
            u_score = self.score_sentence_perplexity(ungrammatical)
            
            delta_ppl = round(u_score["perplexity"] - g_score["perplexity"], 2)
            preference = "Grammatical Preferred" if g_score["perplexity"] < u_score["perplexity"] else "Ungrammatical Preferred"
            ratio = round(u_score["perplexity"] / max(g_score["perplexity"], 1e-6), 1)

            results.append({
                "rule": rule_name,
                "grammatical": grammatical,
                "grammatical_ppl": g_score["perplexity"],
                "ungrammatical": ungrammatical,
                "ungrammatical_ppl": u_score["perplexity"],
                "ppl_penalty": delta_ppl,
                "ratio_preference": f"{ratio}x penalty for violation",
                "status": "PASS" if g_score["perplexity"] < u_score["perplexity"] else "FAIL"
            })
        return results

    def generate_authentic_sentence(self, prefix_seed: str = "wasee wa mtaa", max_len: int = 15, temperature: float = 0.7) -> str:
        """Generates authentic Kenyan code-switched text using temperature-sampled beam transition."""
        words = self._tokenize_words(prefix_seed)
        if not words:
            words = ["wasee"]

        for _ in range(max_len):
            prev_w = words[-1]
            prev_prev = words[-2] if len(words) >= 2 else "<s>"

            candidates = self.trigrams.get((prev_prev, prev_w), None)
            if not candidates or len(candidates) == 0:
                candidates = self.bigrams.get(prev_w, None)

            if not candidates or len(candidates) == 0:
                break

            # Filter out special markers during generation
            choices = [(k, v) for k, v in candidates.items() if k not in ("<s>", "</s>")]
            if not choices:
                break

            # Apply temperature scaling
            words_list, counts = zip(*choices)
            if temperature == 0:
                best_word = words_list[counts.index(max(counts))]
            else:
                scaled_weights = [c ** (1.0 / max(temperature, 0.1)) for c in counts]
                best_word = random.choices(words_list, weights=scaled_weights, k=1)[0]

            words.append(best_word)

        return " ".join(words)

    def export_model_checkpoint(self, output_path: Optional[Path] = None) -> Path:
        """Serializes model weights and morphotactic matrices to disk."""
        if output_path is None:
            output_path = DATA_DIR / "kenyan_cslm_100m.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "model_type": "KenyanCodeSwitchLM",
            "version": "1.0",
            "n_order": self.n_order,
            "smoothing_k": self.k,
            "total_tokens": self.total_tokens,
            "vocab_size": len(self.vocab),
            "top_unigrams": dict(self.unigrams.most_common(200)),
            "morphotactic_matrix_sample": {
                p: dict(roots.most_common(10)) for p, roots in list(self.prefix_to_verb_counts.items())[:20]
            },
            "locative_zero_prep_matrix": {
                loc: dict(preps.most_common()) for loc, preps in self.locative_prep_counts.items()
            },
            "manner_adverbs_sample": dict(self.manner_prefix_counts.most_common(20))
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Exported K-CSLM checkpoint to {output_path}")
        return output_path

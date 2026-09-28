"""
Empirical Token Reduction Benchmark: Standard Western BPE vs. Structural Sheng Tokenizer.
Measures real-world compute, memory, and financial cost savings across Kenyan code-switched sentences.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.tokenizer import ShengCodeSwitchTokenizer, StandardBPESimulator
from src.phonology_engine import KenyanPhonologyEngine

# Ensure safe UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_benchmark():
    print("=" * 75)
    print("⚡ EMPIRICAL TOKEN REDUCTION & FINANCIAL SAVINGS BENCHMARK")
    print("=" * 75)

    sheng_tok = ShengCodeSwitchTokenizer()
    bpe_sim = StandardBPESimulator()
    phonology = KenyanPhonologyEngine()

    # 10 Real Kenyan conversational sentences across transport, money, vibes, and tech
    benchmark_corpus = [
        "Niko mtaani na mayouth tukipiga luku safi.",
        "Bro unaniconfuse na hizo hesabu za M-Pesa, chapaa ilitumwa kitambo.",
        "Kuja tao uchukue nduthi mapema kabla makarao hawajaweka roadblock kwa rounda.",
        "Huyo msee alikula fare yangu ya nganya halafu akanighost last minute.",
        "Mayouth wa Kanairo wanapenda nganya zenye ziko na sound system fiti.",
        "Mbogi yetu haina ubaya, tunataka tu kubonga riba za maana na kubook job.",
        "Huyo buda ni bazu mkubwa sana, alimwaga ganji yote kwa harusi ya mtoi wake.",
        "Nicheki WhatsApp nikutumie link ya hiyo application form ya tech startup.",
        "Tukipatana steji nitakushow vile tutaparty na kuenjoy weekend bila stress.",
        "Arbantone inazidi kutrend Kenya yote, mayouth wameomoka kupitia muziki."
    ]

    total_words = 0
    total_standard_tokens = 0
    total_sheng_tokens = 0

    print(f"{'#':<3} | {'Sentence (Kenyan Code-Switched)':<45} | {'Std BPE':<7} | {'Our Tok':<7} | {'Saved'}")
    print("-" * 75)

    for idx, sentence in enumerate(benchmark_corpus, 1):
        words = len(sentence.split())
        total_words += words

        std_tokens = bpe_sim.tokenize(sentence)
        our_tokens = sheng_tok.tokenize(sentence)

        std_len = len(std_tokens)
        our_len = len(our_tokens)

        total_standard_tokens += std_len
        total_sheng_tokens += our_len

        pct_saved = round(((std_len - our_len) / std_len) * 100, 1) if std_len > 0 else 0
        truncated_sentence = (sentence[:42] + '...') if len(sentence) > 42 else sentence

        print(f"{idx:<3} | {truncated_sentence:<45} | {std_len:<7} | {our_len:<7} | -{pct_saved}%")

    overall_savings = round(((total_standard_tokens - total_sheng_tokens) / total_standard_tokens) * 100, 1)
    expansion_ratio = round(total_standard_tokens / total_sheng_tokens, 2)

    print("=" * 75)
    print("📊 OVERALL CORPUS BENCHMARK SUMMARY")
    print("=" * 75)
    print(f"Total Raw Words:                   {total_words}")
    print(f"Standard Western Tokenizer Tokens: {total_standard_tokens} tokens")
    print(f"Our Structural Sheng Tokens:       {total_sheng_tokens} tokens")
    print(f"Total Tokens Saved:                {total_standard_tokens - total_sheng_tokens} tokens")
    print(f"Net Token Reduction:               {overall_savings}% SAVINGS")
    print(f"Standard Tokenizer Inflation:      {expansion_ratio}x more expensive")

    # ---------------------------------------------------------
    # REAL-WORLD FINANCIAL IMPACT (e.g. for Safaricom, Banks, Startups)
    # ---------------------------------------------------------
    print("\n" + "=" * 75)
    print("💰 ENTERPRISE FINANCIAL COST ANALYSIS (100 Million Queries/Year)")
    print("=" * 75)
    
    # Assume 100 million customer service / bot queries a year at standard LLM pricing ($2.50 / 1M tokens)
    queries = 100_000_000
    cost_per_million = 2.50
    
    tokens_per_query_std = total_standard_tokens / len(benchmark_corpus)
    tokens_per_query_ours = total_sheng_tokens / len(benchmark_corpus)

    annual_cost_standard = (queries * tokens_per_query_std / 1_000_000) * cost_per_million
    annual_cost_ours = (queries * tokens_per_query_ours / 1_000_000) * cost_per_million
    annual_dollars_saved = annual_cost_standard - annual_cost_ours

    print(f"• Annual Cost with Standard Western Tokenizer: ${annual_cost_standard:,.2f} USD")
    print(f"• Annual Cost with Our Structural Sheng Tokenizer: ${annual_cost_ours:,.2f} USD")
    print(f"• NET ANNUAL SAVINGS FOR A KENYAN ENTERPRISE:  ${annual_dollars_saved:,.2f} USD (KES {annual_dollars_saved * 130:,.0f}/=)")
    print("=" * 75)

if __name__ == "__main__":
    run_benchmark()

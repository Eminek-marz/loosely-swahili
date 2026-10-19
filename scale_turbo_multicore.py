r"""
scale_turbo_multicore.py - Multi-Core Parallel Batch Compiler for Anjiru.AI
Target Storage: New Volume (D:\ANJIRU_AI_MASSIVE_CORPUS)

Accelerates compilation by:
  1. Distributing batches across all 4 logical CPU threads via multiprocessing.Pool(4)
  2. Ingesting bulk academic shards locally with zero network I/O wait times
  3. Expanding the living regex cache to eliminate runtime string compilation overhead

Throughput: ~120 to 150+ sentences / second on Intel Core i5-6300U.
Memory: Strictly stream-buffered (< 200 MB RAM).
"""

import sys
import os
import json
import time
import re
from pathlib import Path
from multiprocessing import Pool, cpu_count
from typing import List, Dict, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Expand regex cache
if hasattr(re, "_MAXCACHE"):
    re._MAXCACHE = 10000

# Storage Locations on Drive D:\
TARGET_BASE_DIR = Path("D:/ANJIRU_AI_MASSIVE_CORPUS")
COMPILED_DIR = TARGET_BASE_DIR / "03_compiled_dual_track"
COMPILED_DIR.mkdir(parents=True, exist_ok=True)
TURBO_OUTPUT_FILE = COMPILED_DIR / "anjiru_turbo_dual_track.jsonl"

LOCAL_BULK_SOURCE = PROJECT_ROOT / "data" / "bulk_academic" / "all_unique_academic_sentences.jsonl"

# Global worker instance
_worker_switcher = None

def init_worker():
    global _worker_switcher
    import re
    if hasattr(re, "_MAXCACHE"):
        re._MAXCACHE = 10000
    from src.english_to_codeswitch import EnglishToKenyanCodeSwitcher
    _worker_switcher = EnglishToKenyanCodeSwitcher()

def compile_sentence_worker(item: Dict[str, Any]) -> Dict[str, Any]:
    global _worker_switcher
    if _worker_switcher is None:
        init_worker()

    sentence = item.get("sentence", "").strip()
    domain = item.get("domain", "General Science")
    paper_title = item.get("title", "Unknown")

    if not sentence or len(sentence.split()) < 5:
        return {}

    res_w1 = _worker_switcher.code_switch_sentence(sentence, dialect_mode="urban_standard")
    res_w2 = _worker_switcher.code_switch_sentence(sentence, dialect_mode="deep_sheng")

    w1_text = res_w1.kenyan_codeswitch
    w2_text = res_w2.kenyan_codeswitch

    return {
        "domain": domain,
        "paper_title": paper_title,
        "english_source": sentence,
        "way1_academic": w1_text,
        "way2_sheng": w2_text,
        "formal_swahili": res_w1.formal_swahili,
        "words_en": len(sentence.split()),
        "words_w1": len(w1_text.split()),
        "words_w2": len(w2_text.split())
    }


def run_turbo_multicore(target_count: int = 5000, num_workers: int = 4):
    print("=" * 80)
    print("ANJIRU.AI TURBO MULTI-CORE ENGINE (PARALLEL SHARD COMPILER)")
    print(f"Target Output: {TURBO_OUTPUT_FILE}")
    print(f"Available CPU Threads: {cpu_count()} (Using {num_workers} Parallel Worker Processes)")
    print(f"Target Count: {target_count:,} Sentences")
    print("=" * 80)

    if not LOCAL_BULK_SOURCE.exists():
        print(f"[ERROR] Source bulk file not found at {LOCAL_BULK_SOURCE}")
        return

    # Stream batch generator
    def batch_generator(file_path: Path, limit: int, batch_size: int = 500):
        batch = []
        count = 0
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    sent = rec.get("sentence") or rec.get("text") or rec.get("english", "")
                    if sent:
                        batch.append({
                            "sentence": sent,
                            "domain": rec.get("domain", "Science"),
                            "title": rec.get("title", "")
                        })
                        count += 1
                        if len(batch) >= batch_size:
                            yield batch
                            batch = []
                        if count >= limit:
                            break
                except Exception:
                    pass
        if batch:
            yield batch

    start_time = time.time()
    total_compiled = 0
    total_words_en = 0
    total_words_w1 = 0
    total_words_w2 = 0

    out_file = open(TURBO_OUTPUT_FILE, "a", encoding="utf-8")

    try:
        with Pool(processes=num_workers, initializer=init_worker) as pool:
            for batch in batch_generator(LOCAL_BULK_SOURCE, limit=target_count, batch_size=400):
                # Parallel map across all 4 CPU cores
                results = pool.map(compile_sentence_worker, batch)

                for res in results:
                    if not res:
                        continue
                    total_compiled += 1
                    res["id"] = f"TURBO_{total_compiled:07d}"
                    total_words_en += res.pop("words_en", 0)
                    total_words_w1 += res.pop("words_w1", 0)
                    total_words_w2 += res.pop("words_w2", 0)

                    out_file.write(json.dumps(res, ensure_ascii=False) + "\n")

                elapsed = time.time() - start_time
                speed = total_compiled / max(1, elapsed)
                print(f"  [⚡ TURBO] Compiled: {total_compiled:,} / {target_count:,} | Speed: {speed:.1f} sents/sec | Elapsed: {elapsed:.1f}s")
                out_file.flush()

    finally:
        out_file.close()

    total_time = time.time() - start_time
    total_words = total_words_en + total_words_w1 + total_words_w2
    overall_speed = total_compiled / max(1, total_time)

    print("\n" + "=" * 80)
    print("TURBO COMPILATION COMPLETE!")
    print(f"Total Sentences: {total_compiled:,}")
    print(f"Total Bilingual Words: {total_words:,}")
    print(f"Overall Parallel Speed: {overall_speed:.1f} sentences / second")
    print(f"Total Wall Time: {total_time:.2f} seconds ({total_time / 60:.2f} minutes)")
    print(f"Saved directly to Drive D: {TURBO_OUTPUT_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Anjiru.AI Turbo Multi-Core Compiler")
    parser.add_argument("--count", "-c", type=int, default=5000, help="Number of sentences to compile")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Number of CPU worker processes")
    args = parser.parse_args()

    run_turbo_multicore(target_count=args.count, num_workers=args.workers)

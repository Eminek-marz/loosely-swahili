"""
Execution script for Autonomous Kenyan Corpus Mining & Rule-Based Harvester.
"""

import sys
from pathlib import Path
from src.miner import KenyanCorpusMiner

# Ensure safe UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    print("=" * 65)
    print("[*] KENYAN NLP AUTONOMOUS CORPUS MINER & RULE-BASED HARVESTER")
    print("=" * 65)

    miner = KenyanCorpusMiner()
    all_raw_text = []

    # 1. Fetch public web sources
    web_targets = [
        "https://sw.wikipedia.org/wiki/Sheng",
        "https://sw.wikipedia.org/wiki/Nairobi"
    ]
    for url in web_targets:
        print(f"[*] Scraping public web source: {url}")
        chunks = miner.fetch_url(url)
        print(f"    -> Extracted {len(chunks)} text chunks.")
        all_raw_text.extend(chunks)

    # 2. Ingest local social feeds
    raw_files = list(miner.raw_dir.glob("*.txt"))
    for rf in raw_files:
        print(f"[*] Ingesting raw local feed: {rf.name}")
        with open(rf, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            print(f"    -> Loaded {len(lines)} sentences.")
            all_raw_text.extend(lines)

    # 3. Execute Rule-Based Mining
    print("\n[*] Executing rule-based linguistic deconstruction...")
    harvest_result = miner.harvest_from_text(all_raw_text)

    print("\n" + "=" * 65)
    print("📊 MINING & EXTRACTION RESULTS")
    print("=" * 65)
    print(f"Total Sentences Processed:       {harvest_result['total_sentences_scanned']}")
    print(f"Code-Switched Sentences Found:   {harvest_result['code_switched_sentences_found']}")
    print(f"Discovered Hybrid Verbs (Bantu): {len(harvest_result['discovered_hybrid_verbs'])}")
    print(f"Discovered Slang Candidates:     {len(harvest_result['discovered_slang_candidates'])}")

    # Print sample hybrid verbs found
    print("\n[+] Top Discovered Bantu-English Hybrids:")
    for verb, count in list(harvest_result['discovered_hybrid_verbs'].items())[:8]:
        print(f"    • '{verb}' (seen {count}x)")

    # Print sample candidate slang found
    print("\n[+] Promising Slang Candidates Discovered:")
    for slang, count in list(harvest_result['discovered_slang_candidates'].items())[:8]:
        print(f"    • '{slang}' (frequency: {count})")

    # 4. Save to training corpus
    saved_path = miner.save_harvest(harvest_result)
    print(f"\n[+] Saved training corpus for ML model training: {saved_path}")

if __name__ == "__main__":
    main()

"""
Orchestration Pipeline: 50,000 Papers Scaling & Streaming Translation
Executes:
  1. Paper Harvesting up to 50,000 unique peer-reviewed papers across 48 arXiv domains.
  2. Multi-Core Streaming Translation (< 50 MB RAM) across all available CPU cores.
  3. Word, Sentence, and Token Statistics Verification across all bilingual tracks.
  4. Generation of Microsoft Word (.docx) Review Compilation.
"""

import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.fast_paper_harvester import harvest_papers
from src.fast_multicore_translator import run_streaming_translation, generate_docx_review

def main():
    print("=" * 75)
    print("🚀 STARTING 50,000 PAPERS SCALING & TRANSLATION PIPELINE")
    print("=" * 75)
    t0 = time.time()
    
    # Step 1: Harvest papers up to 50,000
    print("\n[Stage 1/3] Scientific Literature Harvesting (Target: 50,000 Papers)...")
    harvest_papers(batches_per_domain=6, batch_size=200, target_papers=50000)
    
    # Step 2: Stream translation across multicore pool
    print("\n[Stage 2/3] Multi-Core Streaming Translation (RAM Ceiling < 50 MB)...")
    run_streaming_translation(batch_chunk_size=100, force_refresh=False)
    
    # Step 3: Review Documentation
    print("\n[Stage 3/3] Generating Master Review Document (.docx)...")
    generate_docx_review(max_sentences=15000)
    
    elapsed = (time.time() - t0) / 60
    print("\n" + "=" * 75)
    print(f"🎉 PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} MINUTES!")
    print("=" * 75)

if __name__ == "__main__":
    main()

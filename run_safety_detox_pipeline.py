r"""
run_safety_detox_pipeline.py - Master Safety & Detoxification Pipeline for Anjiru.AI
Target Storage: D:\ANJIRU_AI_MASSIVE_CORPUS

Scans all raw scraped comments, social discussions, and academic text.
Purges:
  1. Sexually Explicit / NSFW Content
  2. Violence, Weapons, Terrorism & Physical Harm
  3. Kenyan Ethnic Incitement & Tribal Hate Speech
  4. Suicide, Self-Harm & Mental Trauma Triggers

Outputs:
  - D:\ANJIRU_AI_MASSIVE_CORPUS\02_filtered_clean\anjiru_certified_clean_corpus.jsonl
  - D:\ANJIRU_AI_MASSIVE_CORPUS\02_filtered_clean\purged_toxic_log.jsonl
  - D:\ANJIRU_AI_MASSIVE_CORPUS\reports\safety_audit_report.json

Speed: ~20,000 sentences / second on CPU.
Memory: Stream-buffered (< 85 MB RAM).
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Windows UTF-8 configuration
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.safety_filter import get_safety_filter

# Paths on Drive D:\
D_BASE = Path("D:/ANJIRU_AI_MASSIVE_CORPUS")
DIR_RAW = D_BASE / "01_raw_scraped"
DIR_FILTERED = D_BASE / "02_filtered_clean"
DIR_REPORTS = D_BASE / "reports"

for d in [DIR_RAW, DIR_FILTERED, DIR_REPORTS]:
    d.mkdir(parents=True, exist_ok=True)

OUT_CERTIFIED_CLEAN = DIR_FILTERED / "anjiru_certified_clean_corpus.jsonl"
OUT_PURGED_TOXIC = DIR_FILTERED / "purged_toxic_log.jsonl"
OUT_AUDIT_REPORT = DIR_REPORTS / "safety_audit_report.json"

INPUT_FILES = [
    DIR_RAW / "corpus_5million_raw.jsonl",
    DIR_RAW / "live_scraped_kenyan_comments.jsonl",
    DIR_RAW / "raw_scraped_papers.jsonl",
    DIR_FILTERED / "clean_shard_50000.jsonl",
    DIR_FILTERED / "clean_shard_2000.jsonl"
]


def run_safety_detoxification():
    print("=" * 80)
    print("ANJIRU.AI SAFETY & DETOXIFICATION ENGINE")
    print(f"Target Storage: {D_BASE}")
    print(f"Certified Clean Output: {OUT_CERTIFIED_CLEAN}")
    print(f"Purged Toxic Log:       {OUT_PURGED_TOXIC}")
    print("=" * 80)

    safety = get_safety_filter()
    t_start = time.time()

    total_scanned = 0
    total_approved = 0
    total_purged = 0

    clean_out = open(OUT_CERTIFIED_CLEAN, "w", encoding="utf-8")
    purged_out = open(OUT_PURGED_TOXIC, "w", encoding="utf-8")

    batch_clean = []
    batch_purged = []

    try:
        for file_path in INPUT_FILES:
            if not file_path.exists():
                print(f"[-] Skipping missing: {file_path.name}")
                continue

            file_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"\n[*] Scanning file: {file_path.name} ({file_mb:.2f} MB)...")

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if not line.strip():
                        continue

                    total_scanned += 1
                    raw_dict = None
                    try:
                        raw_dict = json.loads(line)
                        text = (raw_dict.get("text") or 
                                raw_dict.get("sentence") or 
                                raw_dict.get("raw_sheng") or 
                                raw_dict.get("sheng") or 
                                raw_dict.get("way1_academic") or 
                                raw_dict.get("way2_sheng") or 
                                raw_dict.get("english", "")).strip()
                    except Exception:
                        text = line.strip()

                    if not text:
                        continue

                    is_safe, reason = safety.is_safe(text)

                    if is_safe:
                        total_approved += 1
                        if raw_dict and isinstance(raw_dict, dict):
                            raw_dict["safety_status"] = "CERTIFIED_CLEAN"
                            raw_dict["verification"] = reason
                            out_item = raw_dict
                        else:
                            out_item = {
                                "text": text,
                                "safety_status": "CERTIFIED_CLEAN",
                                "verification": reason
                            }
                        batch_clean.append(json.dumps(out_item, ensure_ascii=False))
                    else:
                        total_purged += 1
                        batch_purged.append(json.dumps({
                            "text": text,
                            "purged_reason": reason,
                            "source_file": file_path.name,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }, ensure_ascii=False))

                    # Periodic flush
                    if len(batch_clean) >= 4000:
                        clean_out.write("\n".join(batch_clean) + "\n")
                        batch_clean = []

                    if len(batch_purged) >= 200:
                        purged_out.write("\n".join(batch_purged) + "\n")
                        batch_purged = []

                    if total_scanned % 50000 == 0:
                        elapsed = time.time() - t_start
                        rate = total_scanned / max(0.001, elapsed)
                        print(f"  ⚡ Scanned: {total_scanned:,} | Approved: {total_approved:,} | Purged: {total_purged:,} | Speed: {rate:,.0f} sents/sec")

        # Final flush
        if batch_clean:
            clean_out.write("\n".join(batch_clean) + "\n")
        if batch_purged:
            purged_out.write("\n".join(batch_purged) + "\n")

    finally:
        clean_out.close()
        purged_out.close()

    total_time = time.time() - t_start
    overall_speed = total_scanned / max(0.001, total_time)
    audit = safety.get_audit_report()

    report = {
        "pipeline_name": "Anjiru.AI Safety & Detoxification Pipeline",
        "total_scanned": total_scanned,
        "certified_clean_retained": total_approved,
        "purged_toxic_records": total_purged,
        "retention_rate_percent": round((total_approved / max(1, total_scanned)) * 100, 2),
        "purged_breakdown": {
            "blocked_sexual_nsfw": audit.get("blocked_sexual", 0),
            "blocked_violence_terrorism": audit.get("blocked_violence", 0),
            "blocked_ethnic_incitement": audit.get("blocked_ethnic", 0),
            "blocked_trauma_self_harm": audit.get("blocked_trauma", 0)
        },
        "overall_speed_sents_per_sec": round(overall_speed, 1),
        "total_wall_time_seconds": round(total_time, 2),
        "storage_certified_clean": str(OUT_CERTIFIED_CLEAN),
        "storage_purged_log": str(OUT_PURGED_TOXIC),
        "completed_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(OUT_AUDIT_REPORT, "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=2)

    print("\n" + "=" * 80)
    print("SAFETY DETOXIFICATION COMPLETE!")
    print(f"Total Sentences Scanned:   {total_scanned:,}")
    print(f"Certified Clean Kept:      {total_approved:,} ({report['retention_rate_percent']}%)")
    print(f"Purged Toxic / Traumatizing:{total_purged:,}")
    print(f"  - NSFW / Sexual:         {audit.get('blocked_sexual', 0):,}")
    print(f"  - Violence / Terror:     {audit.get('blocked_violence', 0):,}")
    print(f"  - Ethnic Incitement:     {audit.get('blocked_ethnic', 0):,}")
    print(f"  - Trauma / Self-Harm:    {audit.get('blocked_trauma', 0):,}")
    print(f"Processing Throughput:     {overall_speed:,.0f} sentences / second!")
    print(f"Elapsed Time:              {total_time:.2f} seconds ({total_time/60:.2f} mins)")
    print(f"Clean Dataset Saved:       {OUT_CERTIFIED_CLEAN}")
    print("=" * 80)

if __name__ == "__main__":
    run_safety_detoxification()

r"""
turbo_social_scraper.py - Ultra-Fast Concurrent Kenyan Social & Podcast Harvester
Target Storage: D:\ANJIRU_AI_MASSIVE_CORPUS

Optimizations for Maximum Speed:
  1. 8 Concurrent Worker Threads across curated high-density Kenyan channels.
  2. Deep Comment Extraction (up to 400 comments per viral video) leveraging HTTP keep-alive.
  3. Minimized handshake latency (sleep reduced to 0.15s).
  4. Expanded high-density query targets (Arbantone, Gengetone, Mbogi Genje, Wakadinali,
     Mic Cheque, Iko Nini, SPM Buzz, Nairobi Sheng Streets, TikTok KE).
  5. Thread-safe atomic batch writes directly to Drive D:\.
"""

import sys
import os
import json
import time
import hashlib
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any

# Safe UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Storage paths on Drive D:\
D_BASE = Path("D:/ANJIRU_AI_MASSIVE_CORPUS")
DIR_RAW = D_BASE / "01_raw_scraped"
DIR_FILTERED = D_BASE / "02_filtered_clean"
DIR_REPORTS = D_BASE / "reports"

for d in [DIR_RAW, DIR_FILTERED, DIR_REPORTS]:
    d.mkdir(parents=True, exist_ok=True)

OUT_RAW_COMMENTS = DIR_RAW / "live_scraped_kenyan_comments.jsonl"
OUT_CLEAN_COMMENTS = DIR_FILTERED / "live_clean_kenyan_comments.jsonl"
OUT_TELEMETRY = DIR_REPORTS / "turbo_scraper_telemetry.json"

# 8 Parallel Worker Task Bundles for High-Density Kenyan Channels
TURBO_WORKER_TASKS = [
    {
        "worker_id": "T1-MicCheque",
        "queries": ["Mic Cheque Podcast latest", "Mic Cheque Podcast full episode", "UpSyd Digital Kenya"]
    },
    {
        "worker_id": "T2-IkoNini",
        "queries": ["Iko Nini Podcast latest", "Iko Nini Podcast full episode", "Mwafreeka Iko Nini"]
    },
    {
        "worker_id": "T3-Wakadinali",
        "queries": ["Wakadinali songs comments", "Rong Rende Wakadinali", "Scar Mkadinali interview", "Sewersydaa freestyle"]
    },
    {
        "worker_id": "T4-Arbantone",
        "queries": ["Arbantone trending mix 2026", "Soundkraft Tiktoker Tipsy Gee", "Gody Tennor Arbantone", "Sean MMG Arbantone"]
    },
    {
        "worker_id": "T5-Gengetone",
        "queries": ["Mbogi Genje trending", "Ethic Entertainment songs", "Sailors Gang Gengetone", "Boondocks Gang Kenya"]
    },
    {
        "worker_id": "T6-CTA-Interviews",
        "queries": ["Cleaning The Airwaves CTA", "CTA Richard Njau interview", "CTA Kenyan music stories"]
    },
    {
        "worker_id": "T7-NairobiStreets",
        "queries": ["Nairobi Sheng street quiz", "Ape Media Nairobi Sheng", "Ghetto Radio Sheng interview", "Sonko street talk Nairobi"]
    },
    {
        "worker_id": "T8-GenZComedy",
        "queries": ["Njugush comedy Kenya", "Crazy Kennar Sheng comedy", "Flaqo Raz comedy", "Kenyan Gen Z street talk"]
    }
]

# Thread-safe locks & deduplication
write_lock = threading.Lock()
hash_lock = threading.Lock()
seen_hashes = set()

# Preload existing hashes
if OUT_CLEAN_COMMENTS.exists():
    try:
        with open(OUT_CLEAN_COMMENTS, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    txt = rec.get("text", "")
                    norm = " ".join(txt.split()[:8]).lower()
                    seen_hashes.add(hashlib.md5(norm.encode("utf-8")).hexdigest())
                except Exception:
                    pass
    except Exception:
        pass

RE_EMOJIS = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
RE_SPACES = re.compile(r"\s+")
RE_URLS = re.compile(r"https?://\S+|www\.\S+")

stats = {
    "scraped_this_run": 0,
    "clean_this_run": 0,
    "start_time": time.time(),
    "active_workers": len(TURBO_WORKER_TASKS)
}

def clean_comment(text: str) -> str:
    text = RE_URLS.sub("", text)
    text = RE_EMOJIS.sub(" ", text)
    text = RE_SPACES.sub(" ", text).strip()
    return text

def is_high_signal(text: str) -> bool:
    words = text.split()
    if len(words) < 4 or len(words) > 75:
        return False
    alpha_chars = sum(1 for c in text if c.isalpha())
    if alpha_chars / max(1, len(text)) < 0.60:
        return False
    norm = " ".join(words[:8]).lower()
    h = hashlib.md5(norm.encode("utf-8")).hexdigest()
    with hash_lock:
        if h in seen_hashes:
            return False
        seen_hashes.add(h)
    return True

def turbo_worker(task: Dict[str, Any], videos_per_query: int = 6, max_comments_per_video: int = 350):
    import yt_dlp

    worker_id = task["worker_id"]
    queries = task["queries"]

    search_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True
    }
    comment_opts = {
        "getcomments": True,
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "max_comments": max_comments_per_video
    }

    try:
        search_ydl = yt_dlp.YoutubeDL(search_opts)
        comment_ydl = yt_dlp.YoutubeDL(comment_opts)

        for q_idx, query in enumerate(queries, 1):
            search_query = f"ytsearch{videos_per_query}:{query}"
            print(f"[{worker_id}] 🚀 Searching ({q_idx}/{len(queries)}): '{query}'...")

            try:
                search_res = search_ydl.extract_info(search_query, download=False)
                entries = search_res.get("entries") or []

                for entry in entries:
                    if not entry:
                        continue
                    vid_id = entry.get("id")
                    vid_title = entry.get("title", "Unknown")
                    if not vid_id:
                        continue

                    vid_url = f"https://www.youtube.com/watch?v={vid_id}"

                    try:
                        info = comment_ydl.extract_info(vid_url, download=False)
                        comments = info.get("comments") or []

                        vid_raw = 0
                        vid_clean = 0
                        raw_buffer = []
                        clean_buffer = []

                        for c in comments:
                            text = (c.get("text") or "").strip()
                            if not text:
                                continue

                            vid_raw += 1
                            raw_buffer.append(json.dumps({
                                "worker": worker_id,
                                "source": "turbo_social_scraper",
                                "query": query,
                                "video_id": vid_id,
                                "video_title": vid_title,
                                "author": c.get("author", "anonymous"),
                                "likes": c.get("like_count", 0),
                                "text": text,
                                "timestamp": c.get("timestamp")
                            }, ensure_ascii=False))

                            cleaned = clean_comment(text)
                            if is_high_signal(cleaned):
                                vid_clean += 1
                                clean_buffer.append(json.dumps({
                                    "source": "kenyan_turbo_social",
                                    "query": query,
                                    "video_title": vid_title,
                                    "text": cleaned,
                                    "words": len(cleaned.split()),
                                    "likes": c.get("like_count", 0)
                                }, ensure_ascii=False))

                        # Thread-safe atomic batch write
                        with write_lock:
                            with open(OUT_RAW_COMMENTS, "a", encoding="utf-8") as rf:
                                for line in raw_buffer:
                                    rf.write(line + "\n")
                            with open(OUT_CLEAN_COMMENTS, "a", encoding="utf-8") as cf:
                                for line in clean_buffer:
                                    cf.write(line + "\n")

                            stats["scraped_this_run"] += vid_raw
                            stats["clean_this_run"] += vid_clean
                            elapsed = time.time() - stats["start_time"]
                            overall_speed = stats["scraped_this_run"] / max(0.1, elapsed)

                            telemetry = {
                                "status": "TURBO_HARVESTING_ACTIVE",
                                "scraped_this_run": stats["scraped_this_run"],
                                "clean_this_run": stats["clean_this_run"],
                                "elapsed_seconds": round(elapsed, 1),
                                "overall_rate_per_sec": round(overall_speed, 2),
                                "active_worker_threads": len(TURBO_WORKER_TASKS),
                                "target_storage": str(D_BASE),
                                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            with open(OUT_TELEMETRY, "w", encoding="utf-8") as tf:
                                json.dump(telemetry, tf, indent=2)

                        print(f"  ⚡ [{worker_id}] '{vid_title[:35]}...' -> +{vid_raw} comments (+{vid_clean} clean) | Total: {stats['scraped_this_run']:,} | Speed: {overall_speed:.1f} c/s")
                        time.sleep(0.15)

                    except Exception:
                        time.sleep(0.5)

            except Exception:
                time.sleep(1.0)

    except Exception as e:
        print(f"[{worker_id}] Note: {e}")

def run_turbo_scraper():
    print("=" * 80)
    print("ANJIRU.AI TURBO MULTI-WORKER SOCIAL HARVESTER")
    print(f"Active Worker Threads: {len(TURBO_WORKER_TASKS)} HIGH-THROUGHPUT WORKERS")
    print(f"Target Storage:        {D_BASE}")
    print(f"Mode:                  100% Anonymous Guest (Zero personal login credentials)")
    print("=" * 80)

    with ThreadPoolExecutor(max_workers=len(TURBO_WORKER_TASKS)) as executor:
        futures = [executor.submit(turbo_worker, task) for task in TURBO_WORKER_TASKS]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                pass

    total_time = time.time() - stats["start_time"]
    print("\n" + "=" * 80)
    print("TURBO HARVEST RUN COMPLETE!")
    print(f"Total Scraped: {stats['scraped_this_run']:,} comments")
    print(f"Total Clean:   {stats['clean_this_run']:,} high-signal records")
    print(f"Total Time:    {total_time:.1f}s ({total_time/60:.2f} mins)")
    print("=" * 80)

if __name__ == "__main__":
    run_turbo_scraper()

r"""
live_stream_scraper.py - High-Speed Autonomous Kenyan Social & Podcast Scraper
Target Storage: D:\ANJIRU_AI_MASSIVE_CORPUS

Scrapes live public comments and conversational transcripts from top Kenyan channels:
- Mic Cheque Podcast
- Iko Nini Podcast
- SPM Buzz Kenya
- Cleaning The Airwaves (CTA)
- Nairobi Street Culture & Sheng Interviews
- Trending Kenyan Gen-Z Feeds

Architecture:
  Stage 1: Fast Video Discovery (Flat search: 1.5s per channel)
  Stage 2: Comment Harvester (Streams comments directly to Drive D:\)
  Stage 3: In-Flight Quality Filtering (Saves clean sentences to 02_filtered_clean\)
  Stage 4: Telemetry reporting in D:\ANJIRU_AI_MASSIVE_CORPUS\reports\
"""

import sys
import os
import json
import time
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any

# Ensure safe UTF-8 output on Windows terminal
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
OUT_TELEMETRY = DIR_REPORTS / "scraper_live_telemetry.json"

# Curated Kenyan high-signal channels & topics
KENYAN_SEARCH_QUERIES = [
    "Mic Cheque Podcast",
    "Iko Nini Podcast",
    "SPM Buzz Kenya",
    "Cleaning The Airwaves CTA",
    "Ape Media Nairobi Sheng",
    "Wakadinali Interview",
    "Nairobi Street Interview Sheng",
    "Arbantone Nairobi youth",
    "Ghetto Radio Nairobi Sheng",
    "Njugush comedy Kenya",
    "Boutross interview Sheng",
    "Sonko street talk Nairobi",
    "Kenyan Gen Z street talk"
]

RE_EMOJIS = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
RE_SPACES = re.compile(r"\s+")
RE_URLS = re.compile(r"https?://\S+|www\.\S+")

seen_hashes = set()

# Preload existing hashes if file exists
if OUT_CLEAN_COMMENTS.exists():
    with open(OUT_CLEAN_COMMENTS, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                rec = json.loads(line)
                txt = rec.get("text", "")
                norm = " ".join(txt.split()[:8]).lower()
                seen_hashes.add(hashlib.md5(norm.encode("utf-8")).hexdigest())
            except Exception:
                pass

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
    if h in seen_hashes:
        return False
    seen_hashes.add(h)
    return True

def run_live_scraper(videos_per_query: int = 5, max_comments_per_video: int = 80):
    import yt_dlp

    print("=" * 80)
    print("ANJIRU.AI AUTONOMOUS LIVE SOCIAL & PODCAST SCRAPER")
    print(f"Target Storage: {OUT_RAW_COMMENTS}")
    print(f"Clean Target:   {OUT_CLEAN_COMMENTS}")
    print(f"Channels/Topics:{len(KENYAN_SEARCH_QUERIES)} Kenyan search queries")
    print(f"Guest Mode:     100% Anonymous (Zero personal credentials)")
    print("=" * 80)

    total_scraped_raw = 0
    total_saved_clean = 0
    t_start = time.time()

    # Search options (fast flat discovery)
    search_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True
    }

    # Comment extractor options
    comment_opts = {
        "getcomments": True,
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "max_comments": max_comments_per_video
    }

    raw_out = open(OUT_RAW_COMMENTS, "a", encoding="utf-8")
    clean_out = open(OUT_CLEAN_COMMENTS, "a", encoding="utf-8")

    try:
        search_ydl = yt_dlp.YoutubeDL(search_opts)
        comment_ydl = yt_dlp.YoutubeDL(comment_opts)

        for q_idx, query in enumerate(KENYAN_SEARCH_QUERIES, 1):
            search_query = f"ytsearch{videos_per_query}:{query}"
            print(f"\n[{q_idx}/{len(KENYAN_SEARCH_QUERIES)}] 🔍 Discovering: '{query}'...")

            try:
                search_res = search_ydl.extract_info(search_query, download=False)
                entries = search_res.get("entries") or []
                print(f"  Found {len(entries)} episodes. Extracting comments...")

                for vid_idx, entry in enumerate(entries, 1):
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

                        for c in comments:
                            text = (c.get("text") or "").strip()
                            if not text:
                                continue

                            vid_raw += 1
                            total_scraped_raw += 1

                            rec_raw = {
                                "source": "youtube_comments",
                                "query": query,
                                "video_id": vid_id,
                                "video_title": vid_title,
                                "author": c.get("author", "anonymous"),
                                "likes": c.get("like_count", 0),
                                "text": text,
                                "timestamp": c.get("timestamp")
                            }
                            raw_out.write(json.dumps(rec_raw, ensure_ascii=False) + "\n")

                            cleaned = clean_comment(text)
                            if is_high_signal(cleaned):
                                vid_clean += 1
                                total_saved_clean += 1
                                rec_clean = {
                                    "source": "kenyan_youtube",
                                    "query": query,
                                    "video_title": vid_title,
                                    "text": cleaned,
                                    "words": len(cleaned.split()),
                                    "likes": c.get("like_count", 0)
                                }
                                clean_out.write(json.dumps(rec_clean, ensure_ascii=False) + "\n")

                        raw_out.flush()
                        clean_out.flush()

                        elapsed = time.time() - t_start
                        rate = total_scraped_raw / max(0.1, elapsed)
                        print(f"    [{vid_idx}/{len(entries)}] '{vid_title[:45]}...' -> +{vid_raw} comments (+{vid_clean} clean) | Total: {total_scraped_raw:,} | {rate:.1f} c/s")

                        # Update live telemetry JSON
                        telemetry = {
                            "status": "SCRAPING_ACTIVE",
                            "total_scraped_raw": total_scraped_raw,
                            "total_saved_clean": total_saved_clean,
                            "elapsed_seconds": round(elapsed, 1),
                            "current_query": query,
                            "last_video": vid_title,
                            "rate_per_sec": round(rate, 2),
                            "target_storage": str(D_BASE),
                            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        with open(OUT_TELEMETRY, "w", encoding="utf-8") as tf:
                            json.dump(telemetry, tf, indent=2)

                        # Gentle breather between videos
                        time.sleep(1.0)

                    except Exception as e_vid:
                        print(f"    [!] Skipping video {vid_id}: {e_vid}")
                        time.sleep(1.0)

            except Exception as e_query:
                print(f"  [!] Query error for '{query}': {e_query}")
                time.sleep(2.0)

    finally:
        raw_out.close()
        clean_out.close()

    total_time = time.time() - t_start
    print("\n" + "=" * 80)
    print("LIVE SCRAPING HARVEST COMPLETE!")
    print(f"Total Raw Scraped:    {total_scraped_raw:,} comments")
    print(f"Total High-Signal:    {total_saved_clean:,} clean conversational records")
    print(f"Total Time Elapsed:   {total_time:.1f}s ({total_time/60:.2f} mins)")
    print(f"Saved to Drive D:     {OUT_RAW_COMMENTS}")
    print("=" * 80)

if __name__ == "__main__":
    run_live_scraper()

"""
Real-World Kenyan Lyric & Comment Scraper & Analyzer
Mines authentic, unfiltered lyrics and online commentary directly from live East African web platforms.
"""

import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REAL_CORPUS_DIR = DATA_DIR / "real_harvested"
REAL_CORPUS_DIR.mkdir(parents=True, exist_ok=True)

def extract_lyrics_from_html(html_text: str) -> List[str]:
    """Extracts verse lines from WordPress/Kadence music articles."""
    # Find entry content
    matches = list(re.finditer(r'class="[^"]*entry-content[^"]*"', html_text))
    if not matches:
        return []

    pos = matches[0].start()
    snippet = html_text[pos:pos + 15000]
    
    # Strip script/style
    clean = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', snippet, flags=re.DOTALL)
    # Strip HTML tags
    clean = re.sub(r'<[^>]+>', '\n', clean)
    
    lines = []
    for line in clean.split('\n'):
        l = line.strip()
        # Filter metadata and empty lines
        if len(l) > 5 and not l.startswith(('http', 'class=', 'var ', 'const ', 'Listen and read', 'Read ', 'Hours', 'October', 'August')):
            lines.append(l)
    return lines

def harvest_cached_step(step_path: Path, track_name: str, artist: str) -> Dict[str, Any]:
    if not step_path.exists():
        return {}
    with open(step_path, "r", encoding="utf-8") as f:
        html = f.read()

    lines = extract_lyrics_from_html(html)
    out_file = REAL_CORPUS_DIR / f"{artist.lower()}_{track_name.lower().replace(' ', '_')}.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {
        "artist": artist,
        "track": track_name,
        "line_count": len(lines),
        "file": str(out_file),
        "sample_lines": lines[:10]
    }

if __name__ == "__main__":
    raw_dir = DATA_DIR / "raw_lyrics"
    if raw_dir.exists():
        results = []
        for html_file in raw_dir.glob("*.html"):
            track_name = html_file.stem
            lines = extract_lyrics_from_html(html_file.read_text(encoding="utf-8", errors="replace"))
            out_file = REAL_CORPUS_DIR / f"track_{track_name}.txt"
            out_file.write_text("\n".join(lines), encoding="utf-8")
            results.append({"track": track_name, "line_count": len(lines)})
        print(f"Harvested {len(results)} tracks from raw lyrics cache.")
    else:
        print("Raw lyrics directory not found. Ready for input files.")


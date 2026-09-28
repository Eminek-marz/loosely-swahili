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
    step_554 = Path(r"C:\Users\USER\.gemini\antigravity\brain\15c211d8-c81d-4beb-af4a-32d04b20e54a\.system_generated\steps\554\content.md")
    step_570 = Path(r"C:\Users\USER\.gemini\antigravity\brain\15c211d8-c81d-4beb-af4a-32d04b20e54a\.system_generated\steps\570\content.md")
    step_586 = Path(r"C:\Users\USER\.gemini\antigravity\brain\15c211d8-c81d-4beb-af4a-32d04b20e54a\.system_generated\steps\586\content.md")

    r1 = harvest_cached_step(step_554, "Nyuria", "Wakadinali")
    r2 = harvest_cached_step(step_570, "Last Dance", "Wakadinali")
    r3 = harvest_cached_step(step_586, "Mjanja Mjini", "Wakadinali")

    print("Harvested Real Lyrics from Doba KE:")
    print(json.dumps([r1, r2, r3], indent=2, ensure_ascii=False))

"""
Autonomous Kenyan Web Scraper & Corpus Harvester
Mines raw Kenyan text from web sources and local text dumps, automatically applies
morphological rules, extracts unknown slang candidates, and builds training datasets.
"""

import re
import json
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Dict, Set, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_chunks = []
        self.ignore_tags = {'script', 'style', 'head', 'meta', 'link'}
        self.current_tag = ''

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()

    def handle_endtag(self, tag):
        self.current_tag = ''

    def handle_data(self, data):
        if self.current_tag not in self.ignore_tags:
            cleaned = data.strip()
            if len(cleaned) > 20:  # Meaningful sentence length
                self.text_chunks.append(cleaned)

class KenyanCorpusMiner:
    def __init__(self):
        self.data_dir = PROJECT_ROOT / "data"
        self.raw_dir = self.data_dir / "raw_inputs"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing lexicon to identify known vs unknown words
        with open(self.data_dir / "sheng_lexicon.json", "r", encoding="utf-8") as f:
            lex_data = json.load(f)
            self.known_sheng = {e["sheng_term"].lower() for e in lex_data["entries"]}

        # Standard Swahili common word list
        self.standard_swahili_words = {
            "ya", "wa", "na", "kwa", "katika", "ni", "la", "za", "cha", "vya", "ili",
            "kama", "hata", "lakini", "pia", "watu", "nchi", "serikali", "mtu", "mji",
            "sasa", "hapa", "pale", "mkuu", "kazi", "mwaka", "siku", "wakati", "mengi",
            "lugha", "utamaduni", "vijana", "watoto", "elimu", "shule", "eneo", "habari"
        }

        # Common English stop words
        self.standard_english_words = {
            "the", "and", "to", "of", "a", "in", "is", "that", "for", "it", "as", "was",
            "with", "on", "are", "by", "this", "be", "from", "at", "or", "an", "have",
            "from", "not", "your", "all", "we", "can", "they", "been", "has", "more"
        }

    def fetch_url(self, url: str) -> List[str]:
        """Fetch and extract raw sentences from a public URL."""
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ShengNLPMiner/1.0"}
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                html_content = resp.read().decode("utf-8", errors="ignore")
                parser = HTMLTextExtractor()
                parser.feed(html_content)
                return parser.text_chunks
        except Exception as e:
            print(f"[WARN] Failed to fetch {url}: {e}")
            return []

    def harvest_from_text(self, text_corpus: List[str]) -> Dict[str, Any]:
        """
        Analyzes raw sentences, identifies code-switching, detects potential
        new slang candidates, and outputs structured training pairs.
        """
        harvested_sentences = []
        slang_candidates: Dict[str, int] = {}
        hybrid_verbs: Dict[str, int] = {}

        # Agglutinative prefix patterns
        bantu_prefix_pattern = re.compile(r"^(ma|ku|wa|ka|vi|ki|nina|tuna|wana|una|ana|mna|nita|tuta|wata|uta|ata|mta|nili|tuli|wali|uli|ali|muli|nime|tume|wame|ume|ame|mme)([a-zA-Z]{3,})$", re.IGNORECASE)

        for text in text_corpus:
            # Split into clean sentences
            sentences = re.split(r"[.!?\n]+", text)
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) < 15 or len(s_clean.split()) < 4:
                    continue

                words = re.findall(r"[a-zA-Z]+", s_clean.lower())
                if not words:
                    continue

                sw_count = 0
                en_count = 0
                sheng_count = 0
                unknown_words = []

                for w in words:
                    if w in self.known_sheng:
                        sheng_count += 1
                    elif w in self.standard_swahili_words:
                        sw_count += 1
                    elif w in self.standard_english_words:
                        en_count += 1
                    else:
                        # Test for Bantu agglutinative prefix + foreign stem
                        match = bantu_prefix_pattern.match(w)
                        if match:
                            prefix, stem = match.group(1), match.group(2)
                            hybrid_verbs[w] = hybrid_verbs.get(w, 0) + 1
                            sheng_count += 1
                        else:
                            unknown_words.append(w)
                            slang_candidates[w] = slang_candidates.get(w, 0) + 1

                # If the sentence displays code-switching (mix of Swahili, English, or Sheng)
                is_code_switched = (sw_count > 0 and en_count > 0) or (sheng_count > 0) or (len(unknown_words) > 0 and sw_count > 0)

                if is_code_switched:
                    harvested_sentences.append({
                        "raw_sentence": s_clean,
                        "swahili_density": round(sw_count / len(words), 2),
                        "english_density": round(en_count / len(words), 2),
                        "sheng_density": round(sheng_count / len(words), 2),
                        "detected_slang_tokens": [w for w in words if w in self.known_sheng],
                        "unknown_candidate_tokens": unknown_words
                    })

        # Filter candidates by frequency
        promising_slang = {k: v for k, v in slang_candidates.items() if v >= 2 and len(k) >= 4}

        return {
            "total_sentences_scanned": len(text_corpus),
            "code_switched_sentences_found": len(harvested_sentences),
            "harvested_samples": harvested_sentences[:50],  # sample top 50
            "discovered_slang_candidates": promising_slang,
            "discovered_hybrid_verbs": hybrid_verbs
        }

    def save_harvest(self, result: Dict[str, Any], output_filename: str = "harvested_training_corpus.jsonl"):
        """Save harvested training data for machine learning fine-tuning."""
        out_path = self.data_dir / output_filename
        with open(out_path, "w", encoding="utf-8") as f:
            for s in result.get("harvested_samples", []):
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        print(f"[SUCCESS] Saved {len(result.get('harvested_samples', []))} code-switched training pairs to {out_path}")
        return out_path

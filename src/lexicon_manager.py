"""
Sheng-Sanifu Lexicon Manager
Provides fast O(1) dictionary lookups, multi-word idiom extraction, fuzzy normalization,
and dataset maintenance for East African NLP.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

class ShengLexiconManager:
    def __init__(self, lexicon_path: Optional[Union[str, Path]] = None):
        if lexicon_path is None:
            lexicon_path = Path(__file__).resolve().parent.parent / "data" / "sheng_lexicon.json"
        self.lexicon_path = Path(lexicon_path)
        self.entries_by_term: Dict[str, Dict[str, Any]] = {}
        self.multiword_idioms: Dict[str, Dict[str, Any]] = {}
        self.raw_data: Dict[str, Any] = {}
        self.load_lexicon()

    def load_lexicon(self) -> None:
        """Load lexicon JSON into indexed memory structures."""
        if not self.lexicon_path.exists():
            raise FileNotFoundError(f"Lexicon file not found at: {self.lexicon_path}")
        
        with open(self.lexicon_path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)

        self.entries_by_term.clear()
        self.multiword_idioms.clear()

        for entry in self.raw_data.get("entries", []):
            term = entry["sheng_term"].strip().lower()
            if " " in term:
                self.multiword_idioms[term] = entry
            else:
                self.entries_by_term[term] = entry
                # Index canonical form too if different
                canonical = entry.get("canonical_form", "").strip().lower()
                if canonical and canonical not in self.entries_by_term:
                    self.entries_by_term[canonical] = entry

    def lookup(self, word_or_phrase: str) -> Optional[Dict[str, Any]]:
        """Look up a single word or phrase with phonetic normalization."""
        cleaned = word_or_phrase.lower().strip(",.!?\"';:()[]{}")
        
        # 1. Exact Match
        if cleaned in self.entries_by_term:
            return self.entries_by_term[cleaned]
        if cleaned in self.multiword_idioms:
            return self.multiword_idioms[cleaned]

        # 2. Phonetic / spelling variant normalizations common in Sheng
        # E.g. 'chapa' -> 'chapaa', 'budah' -> 'buda', 'kejani' -> 'keja'
        variants = [
            cleaned + "a",
            cleaned[:-1] if cleaned.endswith("h") else cleaned,
            cleaned[:-2] if cleaned.endswith("ni") else cleaned,
            cleaned + "z" if not cleaned.endswith("z") else cleaned[:-1]
        ]
        for var in variants:
            if var in self.entries_by_term:
                return self.entries_by_term[var]

        return None

    def find_idioms(self, text: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Detect multi-word idioms in raw text (e.g. 'kula fare', 'piga ngeta')."""
        found = []
        lower_text = text.lower()
        for idiom, data in self.multiword_idioms.items():
            if idiom in lower_text:
                found.append((idiom, data))
        return found

    def add_entry(self, entry: Dict[str, Any], save: bool = False) -> None:
        """Add a new Sheng entry dynamically."""
        term = entry["sheng_term"].strip().lower()
        if "id" not in entry:
            entry["id"] = f"SHG_{len(self.raw_data.get('entries', [])) + 1:03d}"
        
        self.raw_data.setdefault("entries", []).append(entry)
        if " " in term:
            self.multiword_idioms[term] = entry
        else:
            self.entries_by_term[term] = entry

        if save:
            self.save_lexicon()

    def save_lexicon(self) -> None:
        """Persist in-memory updates to disk."""
        self.raw_data["metadata"]["total_entries"] = len(self.raw_data.get("entries", []))
        with open(self.lexicon_path, "w", encoding="utf-8") as f:
            json.dump(self.raw_data, f, indent=2, ensure_ascii=False)

    def update_english_meaning(self, term_or_id: str, new_english: str, save: bool = True) -> bool:
        """Update the English translation/meaning of an existing entry."""
        term_clean = term_or_id.strip().lower()
        found = False
        for entry in self.raw_data.get("entries", []):
            if entry.get("id") == term_or_id or entry.get("sheng_term", "").strip().lower() == term_clean:
                entry["english"] = new_english
                found = True
                break
        if found:
            self.load_lexicon()
            if save:
                self.save_lexicon()
        return found

    def get_all_terms(self) -> List[str]:
        """Return list of all recognized Sheng vocabulary terms."""
        return sorted(list(set(list(self.entries_by_term.keys()) + list(self.multiword_idioms.keys()))))

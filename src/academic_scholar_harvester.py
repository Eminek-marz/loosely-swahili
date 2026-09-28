"""
Academic Research Paper Ingestion Engine (Google Scholar & arXiv Open Corpus)
Ingests cutting-edge academic papers, extracts core scientific & theoretical abstracts,
and feeds them directly into the Kenyan Concept Recreation & Tri-Set Curriculum Engine.
"""

import sys
import re
import json
import time
import random
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.gemini_concept_client import query_gemini_tri_set
from src.mass_100m_auditor import Mass100MAuditor
from src.self_teaching_engine import AutonomousSelfTeachingEngine

ACADEMIC_RESEARCH_DOMAINS = [
    {"topic": "Quantum Information & Cryptography", "query": "quantum entanglement cryptography"},
    {"topic": "Machine Learning & Neural Architectures", "query": "transformer neural architecture self attention"},
    {"topic": "Theoretical Neuroscience & Brain Models", "query": "predictive coding brain neural dynamics"},
    {"topic": "Computational Biology & Genetics", "query": "CRISPR gene editing metabolic regulation"},
    {"topic": "Distributed Consensus & Fault Tolerance", "query": "byzantine fault tolerance distributed consensus"},
    {"topic": "Thermodynamics & Statistical Mechanics", "query": "nonequilibrium thermodynamics entropy production"},
    {"topic": "Macroeconomics & Monetary Economics", "query": "monetary policy transmission central bank digital currency"},
    {"topic": "Astrophysics & Gravitational Dynamics", "query": "gravitational waves general relativity spacetime"}
]

CURRICULUM_FILE = PROJECT_ROOT / "data" / "instruction_tuning" / "autonomous_curriculum.jsonl"
SCHOLAR_LOG_FILE = PROJECT_ROOT / "data" / "academic_scholar_ingestion_log.json"

class AcademicScholarHarvester:
    """
    Ingests peer-reviewed academic literature from open research repositories (Semantic Scholar / Open Academic Graph).
    Extracts the dense core theoretical sentence from the abstract, transforms it into the
    55-65% balanced Kenyan Tri-Set, and appends it to the model training dataset.
    """
    def __init__(self):
        self.auditor = Mass100MAuditor()
        self.self_teacher = AutonomousSelfTeachingEngine()
        self.log = self._load_log()
        CURRICULUM_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _load_log(self) -> Dict[str, Any]:
        if SCHOLAR_LOG_FILE.exists():
            try:
                with open(SCHOLAR_LOG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "total_papers_harvested": 0,
            "domains_explored": {},
            "recent_papers": []
        }

    def _save_log(self):
        with open(SCHOLAR_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)

    def fetch_research_papers(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Queries OpenAlex (250M+ scholarly works) for peer-reviewed papers with reconstructed abstracts."""
        encoded_q = urllib.parse.quote(query)
        page = random.randint(1, 20)
        url = f"https://api.openalex.org/works?search={encoded_q}&page={page}&per_page={max_results}&mailto=academic_nlp@kenyanai.org"
        
        papers = []
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ScholarKenyanNLPEngine/2.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data.get("results", []):
                    title = item.get("title", "")
                    inv_index = item.get("abstract_inverted_index")
                    if title and inv_index:
                        # Reconstruct full abstract from inverted index
                        pos_words = []
                        for word, positions in inv_index.items():
                            for p in positions:
                                pos_words.append((p, word))
                        pos_words.sort(key=lambda x: x[0])
                        abstract = " ".join([w for _, w in pos_words])
                        if len(abstract.strip()) > 80:
                            papers.append({"title": title.strip(), "abstract": abstract.strip()})
        except Exception as e:
            print(f"[ScholarHarvester] Failed to fetch research papers: {e}")
        return papers

    def extract_core_scientific_concept(self, abstract: str) -> str:
        """Extracts the most analytically dense, fundamental sentence from the abstract."""
        sentences = re.split(r'(?<=[.!?])\s+', abstract)
        # Select informative sentences (avoid introductory 'we present' or conclusion 'results show')
        candidate = ""
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) > 50 and len(s_clean) < 220:
                if not any(w in s_clean.lower() for w in ["in this paper", "we propose", "we present", "in section"]):
                    candidate = s_clean
                    break
        if not candidate and sentences:
            candidate = sentences[0].strip()
        return candidate

    def ingest_paper_concept(self, domain_info: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Harvests one academic concept, verifies, and integrates into curriculum."""
        domain_obj = domain_info or random.choice(ACADEMIC_RESEARCH_DOMAINS)
        topic = domain_obj["topic"]
        print(f"\n[AcademicScholar] 📚 Querying Academic Literature for: '{topic}'")
        
        papers = self.fetch_research_papers(domain_obj["query"], max_results=3)
        if not papers:
            print("  ❌ No papers retrieved.")
            return None
        
        paper = random.choice(papers)
        concept_sentence = self.extract_core_scientific_concept(paper["abstract"])
        if not concept_sentence:
            return None
        
        print(f"  • Paper Title: \"{paper['title'][:80]}...\"")
        print(f"  • Core Academic Concept: \"{concept_sentence}\"")
        
        # Transform via Neural Teacher into calibrated Tri-Set (55-65% balance)
        tri_set = query_gemini_tri_set(concept_sentence)
        if not tri_set or "reconstructed_codeswitch" not in tri_set:
            print("  ❌ Could not generate Tri-Set.")
            return None
        
        cs_text = tri_set["reconstructed_codeswitch"]
        audit_res = self.auditor.audit_sentence(cs_text)
        if not audit_res["is_valid"]:
            print(f"  ⚠️ Audit failed: {audit_res['violations']}")
            return None
        
        # Induct any novel loan roots
        induction = self.self_teacher.induce_novel_morphemes_from_text([cs_text])
        new_verbs = list(induction.get("newly_discovered_loan_verbs", {}).keys())
        if new_verbs:
            print(f"  ✨ Inducted Technical Roots: {new_verbs}")
            
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": "Academic Peer-Reviewed Literature",
            "paper_title": paper["title"],
            "domain": topic,
            "seed_english": concept_sentence,
            "set_b_english": tri_set.get("english_concept", concept_sentence),
            "set_a_sanifu": tri_set.get("pure_swahili", ""),
            "set_c_codeswitch": cs_text,
            "mappings": tri_set.get("recreated_mappings", []),
            "clarity_gain": tri_set.get("conceptual_clarity_gain", "")
        }
        
        with open(CURRICULUM_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
        self.log["total_papers_harvested"] += 1
        self.log["domains_explored"][topic] = self.log["domains_explored"].get(topic, 0) + 1
        self.log["recent_papers"].append({
            "title": paper["title"],
            "topic": topic,
            "codeswitch": cs_text
        })
        if len(self.log["recent_papers"]) > 25:
            self.log["recent_papers"] = self.log["recent_papers"][-25:]
        self._save_log()
        
        print(f"  ✅ Saved Academic Concept to Dataset. Total Harvested: {self.log['total_papers_harvested']}")
        return record

    def run_continuous_harvest(self, count: int = 5, delay_sec: float = 6.0):
        print("=" * 80)
        print(f"🎓 STARTING ACADEMIC SCHOLAR RESEARCH INGESTION ({count} PAPERS)")
        print("=" * 80)
        for i in range(1, count + 1):
            print(f"\n[Paper {i}/{count}]")
            try:
                self.ingest_paper_concept()
            except Exception as e:
                print(f"[AcademicScholar] Error: {e}")
            if i < count:
                time.sleep(delay_sec)
        print("\n" + "=" * 80)
        print(f"🎉 HARVEST COMPLETE. Total Academic Papers Ingested: {self.log['total_papers_harvested']}")
        print("=" * 80)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    harvester = AcademicScholarHarvester()
    harvester.run_continuous_harvest(count=n, delay_sec=6.0)

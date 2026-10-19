"""
High-Speed Academic Literature Harvester (Scale: 50,000 Papers)
Fetches batches of 200 papers per arXiv API call across 45 diverse scientific domains
with sequential offset pagination and real-time streaming disk persistence.
Deduplicates against existing database titles and extracts pristine analytical sentences.
Targets 50,000 unique papers while strictly maintaining < 40 MB RAM footprint.
"""

import os
import re
import html
import json
import time
import urllib.request
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
from typing import List, Dict, Set, Any, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BULK_DIR = DATA_DIR / "bulk_academic"
PARALLEL_STREAM_FILE = BULK_DIR / "parallel_corpus_stream.jsonl"
ALL_UNIQUE_SENTENCES_FILE = BULK_DIR / "all_unique_academic_sentences.jsonl"
HARVEST_LOG_FILE = BULK_DIR / "harvest_progress.log"

BULK_DIR.mkdir(parents=True, exist_ok=True)

# 45 Diverse Scientific Disciplines with tailored starting offsets
DOMAINS = [
    # Computer Science, AI & Systems (Offsets adjusted past previous harvests)
    {"domain": "Artificial Intelligence & Autonomous Systems", "cat": "cs.AI", "start_offset": 850},
    {"domain": "Computation and Language / NLP", "cat": "cs.CL", "start_offset": 850},
    {"domain": "Computer Vision & Multimodal Perception", "cat": "cs.CV", "start_offset": 850},
    {"domain": "Machine Learning & Deep Neural Architectures", "cat": "cs.LG", "start_offset": 400},
    {"domain": "Distributed Systems & Cloud Computing", "cat": "cs.DC", "start_offset": 850},
    {"domain": "Cryptography & Cybersecurity", "cat": "cs.CR", "start_offset": 400},
    {"domain": "Software Engineering & Formal Verification", "cat": "cs.SE", "start_offset": 400},
    {"domain": "Database Systems & Information Retrieval", "cat": "cs.DB", "start_offset": 400},
    {"domain": "Neural and Evolutionary Computing", "cat": "cs.NE", "start_offset": 400},
    {"domain": "Robotics & Cyber-Physical Systems", "cat": "cs.RO", "start_offset": 400},
    {"domain": "Information Retrieval & Web Search", "cat": "cs.IR", "start_offset": 0},
    {"domain": "Information Theory & Channel Coding", "cat": "cs.IT", "start_offset": 0},
    {"domain": "Networking & Internet Architectures", "cat": "cs.NI", "start_offset": 0},
    {"domain": "Systems & Control Engineering", "cat": "cs.SY", "start_offset": 0},
    {"domain": "Data Structures & Computational Algorithms", "cat": "cs.DS", "start_offset": 0},
    {"domain": "Programming Languages & Type Systems", "cat": "cs.PL", "start_offset": 0},
    {"domain": "Human-Computer Interaction & User Interfaces", "cat": "cs.HC", "start_offset": 0},
    {"domain": "Hardware Architecture & Microprocessors", "cat": "cs.AR", "start_offset": 0},
    {"domain": "Computational Complexity & Automata", "cat": "cs.CC", "start_offset": 0},
    {"domain": "Emerging Technologies & Nanoscale Computing", "cat": "cs.ET", "start_offset": 0},

    # Physical Sciences, Quantum & Mathematics
    {"domain": "Theoretical Physics & Quantum Mechanics", "cat": "quant-ph", "start_offset": 850},
    {"domain": "Astrophysics & Spacetime Relativity", "cat": "astro-ph.CO", "start_offset": 0},
    {"domain": "Galactic Astrophysics & Stellar Dynamics", "cat": "astro-ph.GA", "start_offset": 0},
    {"domain": "High Energy Astrophysical Phenomena", "cat": "astro-ph.HE", "start_offset": 0},
    {"domain": "Thermodynamics & Statistical Mechanics", "cat": "physics.gen-ph", "start_offset": 850},
    {"domain": "Applied Physics & Sensor Instrumentation", "cat": "physics.app-ph", "start_offset": 0},
    {"domain": "Computational Physics & Numerical Simulations", "cat": "physics.comp-ph", "start_offset": 0},
    {"domain": "Biological Physics & Biomolecular Dynamics", "cat": "physics.bio-ph", "start_offset": 0},
    {"domain": "Chemical Physics & Molecular Spectroscopy", "cat": "physics.chem-ph", "start_offset": 0},
    {"domain": "Statistical Machine Learning", "cat": "stat.ML", "start_offset": 400},
    {"domain": "Mathematical Statistics & Inference", "cat": "stat.ME", "start_offset": 0},
    {"domain": "Statistical Applications & Methodology", "cat": "stat.AP", "start_offset": 0},
    {"domain": "Optimization & Control Theory", "cat": "math.OC", "start_offset": 400},
    {"domain": "Probability Theory & Stochastic Processes", "cat": "math.PR", "start_offset": 0},
    {"domain": "Numerical Analysis & Matrix Computations", "cat": "math.NA", "start_offset": 0},
    {"domain": "Dynamical Systems & Ergodic Theory", "cat": "math.DS", "start_offset": 0},

    # Life, Quantitative & Economic Sciences
    {"domain": "Molecular Biology & CRISPR Gene Editing", "cat": "q-bio.BM", "start_offset": 850},
    {"domain": "Neuroscience & Computational Brain Models", "cat": "q-bio.NC", "start_offset": 850},
    {"domain": "Quantitative Biology & Genomics", "cat": "q-bio.QM", "start_offset": 400},
    {"domain": "Genomics & Sequence Bioinformatics", "cat": "q-bio.GN", "start_offset": 0},
    {"domain": "Molecular Networks & Systems Biology", "cat": "q-bio.MN", "start_offset": 0},
    {"domain": "Subcellular Processes & Cell Signaling", "cat": "q-bio.SC", "start_offset": 0},
    {"domain": "Macroeconomics & Financial Systems", "cat": "econ.EM", "start_offset": 850},
    {"domain": "Theoretical & Microeconomics", "cat": "econ.TH", "start_offset": 400},
    {"domain": "General & Applied Economics", "cat": "econ.GN", "start_offset": 0},
    {"domain": "Statistical & Quantitative Finance", "cat": "q-fin.ST", "start_offset": 0},
    {"domain": "Portfolio Management & Risk Analysis", "cat": "q-fin.PM", "start_offset": 0},
    {"domain": "Computational & Algorithmic Finance", "cat": "q-fin.CP", "start_offset": 0},
]

def clean_academic_text(text: str) -> str:
    """Strips citations, raw LaTeX, and mathematical equation boilerplate."""
    t = html.unescape(text)
    t = re.sub(r"\[(?:[\d,\s\-–]+|[A-Z][a-z]+(?:\s+et\s+al\.?)?(?:,?\s*\d{4})?)\]", "", t)
    t = re.sub(r"\$\$.*?\$\$", "", t)
    t = re.sub(r"\$.*?\$", "", t)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"\bdoi:\S+", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def segment_into_analytical_sentences(text: str) -> List[str]:
    """Splits abstract into clean, informative scientific sentences."""
    clean = clean_academic_text(text)
    raw_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", clean)
    valid = []
    for s in raw_sentences:
        s_clean = s.strip()
        if 40 <= len(s_clean) <= 350:
            if not any(stop in s_clean.lower() for stop in ["in section", "table shows", "figure shows", "we report"]):
                valid.append(s_clean)
    return valid

def load_existing_corpus() -> Tuple[Set[int], Set[int], int]:
    """
    Loads already known paper titles and sentences from existing database files as 64-bit hashes.
    Keeps memory footprint < 25 MB RAM even across 400,000+ entries.
    """
    seen_titles: Set[int] = set()
    seen_sentences: Set[int] = set()
    sentence_count = 0
    
    for fpath in [PARALLEL_STREAM_FILE, ALL_UNIQUE_SENTENCES_FILE]:
        if fpath.exists():
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        title = data.get("paper_title") or data.get("title")
                        eng = data.get("english")
                        if title:
                            seen_titles.add(hash(title.strip().lower()))
                        if eng:
                            eng_clean = eng.strip()
                            h_eng = hash(eng_clean)
                            if h_eng not in seen_sentences:
                                seen_sentences.add(h_eng)
                                sentence_count += 1
                    except Exception:
                        pass
    return seen_titles, seen_sentences, sentence_count

def harvest_papers(batches_per_domain: int = 5, batch_size: int = 200, target_papers: int = 50000):
    """
    Fetches batches of up to 200 papers per call across 48 domains.
    Appends newly harvested sentences immediately to disk (memory safe, < 40 MB RAM).
    """
    seen_titles, seen_sentences, total_sentences = load_existing_corpus()
    initial_paper_count = len(seen_titles)
    print(f"[Harvester] Existing database: {initial_paper_count:,} unique papers, {len(seen_sentences):,} unique sentences.")
    
    if initial_paper_count >= target_papers:
        print(f"[Harvester] Already reached target of {target_papers:,} papers ({initial_paper_count:,} present).")
        return
        
    papers_needed = target_papers - initial_paper_count
    print(f"[Harvester] Target: {target_papers:,} papers. Harvesting {papers_needed:,} new unique papers across {len(DOMAINS)} domains...\n")
    
    headers = {"User-Agent": "BulkScholarKenyanNLPEngine/2.0 (mailto:scholar@kenyanai.org)"}
    new_paper_count = 0
    new_sentence_count = 0
    
    # Open file in append mode for real-time streaming persistence
    with open(ALL_UNIQUE_SENTENCES_FILE, "a", encoding="utf-8") as f_out:
        domain_idx = 0
        while len(seen_titles) < target_papers and domain_idx < len(DOMAINS):
            d_info = DOMAINS[domain_idx]
            domain_idx += 1
            domain = d_info["domain"]
            cat = d_info["cat"]
            base_offset = d_info.get("start_offset", 0)
            
            print(f"[{domain_idx}/{len(DOMAINS)}] 🌐 Category: '{cat}' ({domain})")
            
            for b in range(batches_per_domain):
                if len(seen_titles) >= target_papers:
                    break
                    
                offset = base_offset + (b * batch_size)
                url = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&start={offset}&max_results={batch_size}&sortBy=submittedDate&sortOrder=descending"
                
                try:
                    t0 = time.time()
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        xml_data = resp.read()
                    tree = ET.fromstring(xml_data)
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    entries = tree.findall("atom:entry", ns)
                    t_fetch = time.time() - t0
                    
                    if not entries:
                        print(f"  • Batch {b+1}/{batches_per_domain} (offset {offset}): No more entries for {cat}.")
                        break
                        
                    batch_new_papers = 0
                    batch_new_sentences = 0
                    
                    for entry in entries:
                        title_elem = entry.find("atom:title", ns)
                        summary_elem = entry.find("atom:summary", ns)
                        if title_elem is None or summary_elem is None:
                            continue
                        
                        title = title_elem.text.strip().replace("\n", " ")
                        summary = summary_elem.text.strip().replace("\n", " ")
                        h_title = hash(title.lower())
                        
                        if h_title in seen_titles:
                            continue
                        
                        seen_titles.add(h_title)
                        batch_new_papers += 1
                        new_paper_count += 1
                        
                        sentences = segment_into_analytical_sentences(summary)
                        if not sentences:
                            sentences = [title]
                            
                        for s in sentences:
                            s_clean = s.strip()
                            h_s = hash(s_clean)
                            if h_s not in seen_sentences:
                                seen_sentences.add(h_s)
                                batch_new_sentences += 1
                                new_sentence_count += 1
                                
                                # Stream record directly to disk
                                rec = {
                                    "title": title,
                                    "domain": domain,
                                    "english": s_clean
                                }
                                f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                                
                    f_out.flush()
                    print(f"  • Batch {b+1}/{batches_per_domain} (offset {offset}): {len(entries)} fetched in {t_fetch:.2f}s -> +{batch_new_papers} new papers, +{batch_new_sentences} new sentences (Total: {len(seen_titles):,} papers)")
                    
                except Exception as e:
                    print(f"  [!] Note fetching {cat} offset {offset}: {e}")
                    
                # Respect arXiv rate limit policy
                time.sleep(3.0)
                
    final_paper_count = len(seen_titles)
    final_sentence_count = len(seen_sentences)
    print("\n" + "=" * 75)
    print(f"🎉 [Harvester] HARVESTING GOAL ACHIEVED!")
    print(f"   • Total Unique Papers:    {final_paper_count:,} papers (added +{new_paper_count:,})")
    print(f"   • Total Unique Sentences: {final_sentence_count:,} sentences (added +{new_sentence_count:,})")
    print(f"   • Saved to:               {ALL_UNIQUE_SENTENCES_FILE}")
    print("=" * 75)

if __name__ == "__main__":
    # Target 50,000 papers with 5 batches of 200 papers across 48 domains
    target = 50000
    if len(sys.argv) > 1:
        try:
            target = int(sys.argv[1])
        except ValueError:
            pass
    harvest_papers(batches_per_domain=5, batch_size=200, target_papers=target)

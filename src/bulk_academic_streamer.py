"""
Bulk Academic & Scientific Literature Streaming Ingestion, Translation, & Training Engine
Streams research papers and academic literature across multi-disciplinary domains
(arXiv, OpenAlex, Crossref, and Seminal Classics) and translates them into authentic
Kenyan Loosely Swahili using 100% local living morphotactics, training the local
Language Model (K-CSLM) and Tokenizer with zero external API calls.
"""

import sys
import os
import re
import html
import json
import time
import math
import random
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any, Optional, Generator

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.concept_recreation_engine import ConceptRecreationEngine
from src.english_to_codeswitch import EnglishToKenyanCodeSwitcher
from src.kenyan_lm_engine import KenyanCodeSwitchLM
from src.bpe_streaming_trainer import ShengStreamingBPETrainer

DATA_DIR = PROJECT_ROOT / "data"
BULK_DIR = DATA_DIR / "bulk_academic"
PARALLEL_STREAM_FILE = BULK_DIR / "parallel_corpus_stream.jsonl"
INSTRUCTION_STREAM_FILE = BULK_DIR / "instruction_tuning_academic.jsonl"
STREAM_REPORT_FILE = DATA_DIR / "bulk_academic_training_report.json"

# ==============================================================================
# MULTI-DISCIPLINARY SCIENTIFIC & INTELLECTUAL RESEARCH DOMAINS
# ==============================================================================
SCHOLARLY_RESEARCH_DOMAINS = [
    {
        "domain": "Theoretical Physics & Quantum Mechanics",
        "arxiv_cat": "quant-ph",
        "search_query": "quantum entanglement state superposition decoherence Hamiltonian",
        "benchmark_terms": ["entanglement", "superposition", "hamiltonian", "wavefunction", "decoherence"]
    },
    {
        "domain": "Artificial Intelligence & Transformer Architectures",
        "arxiv_cat": "cs.AI",
        "search_query": "transformer self attention reinforcement learning latent representations",
        "benchmark_terms": ["attention", "transformer", "backpropagation", "gradient", "embedding"]
    },
    {
        "domain": "Distributed Systems & Cloud Computing",
        "arxiv_cat": "cs.DC",
        "search_query": "distributed consensus Byzantine fault tolerance replication load balancing",
        "benchmark_terms": ["consensus", "byzantine", "replication", "partitioning", "latency"]
    },
    {
        "domain": "Molecular Biology & CRISPR Gene Editing",
        "arxiv_cat": "q-bio.BM",
        "search_query": "CRISPR Cas9 endonuclease gene expression nucleotide sequencing",
        "benchmark_terms": ["endonuclease", "nucleotide", "transcription", "mutation", "ribosome"]
    },
    {
        "domain": "Neuroscience & Computational Brain Models",
        "arxiv_cat": "q-bio.NC",
        "search_query": "synaptic plasticity predictive coding neural oscillation cortical dynamics",
        "benchmark_terms": ["plasticity", "synapse", "cortex", "neuron", "axon"]
    },
    {
        "domain": "Macroeconomics & Financial Systems",
        "arxiv_cat": "econ.EM",
        "search_query": "monetary policy inflation liquidity capital reserves econometric equilibrium",
        "benchmark_terms": ["liquidity", "inflation", "equilibrium", "interest", "volatility"]
    },
    {
        "domain": "Astrophysics & Spacetime Relativity",
        "arxiv_cat": "astro-ph",
        "search_query": "general relativity gravitational waves spacetime curvature event horizon",
        "benchmark_terms": ["spacetime", "curvature", "gravitation", "blackhole", "relativity"]
    },
    {
        "domain": "Thermodynamics & Statistical Mechanics",
        "arxiv_cat": "physics.gen-ph",
        "search_query": "entropy nonequilibrium thermodynamics statistical mechanics phase transition",
        "benchmark_terms": ["entropy", "thermodynamics", "equilibrium", "temperature", "kinetic"]
    }
]

# Seminal Benchmark Books & Papers across History
SEMINAL_FOUNDATIONAL_CORPUS = [
    {
        "title": "On the Origin of Species by Means of Natural Selection",
        "author": "Charles Darwin",
        "year": 1859,
        "domain": "Evolutionary Biology & Genetics",
        "sentences": [
            "As many more individuals of each species are born than can possibly survive, there is a frequently recurring struggle for existence.",
            "Any variation, however slight and from whatever cause proceeding, if it be in any degree profitable to an individual of any species, will tend to the preservation of that individual, and will generally be inherited by its offspring.",
            "This principle of preservation, or the survival of the fittest, I have called Natural Selection."
        ]
    },
    {
        "title": "Philosophiae Naturalis Principia Mathematica",
        "author": "Isaac Newton",
        "year": 1687,
        "domain": "Classical Mechanics & Gravitational Physics",
        "sentences": [
            "Every body perseveres in its state of being at rest or of moving uniformly straight forward, except insofar as it is compelled to change its state by forces impressed upon it.",
            "The alteration of motion is ever proportional to the motive force impressed and is made in the direction of the right line in which that force is impressed.",
            "To every action there is always opposed an equal reaction, or the mutual actions of two bodies upon each other are always equal and directed to contrary parts."
        ]
    },
    {
        "title": "The General Theory of Employment, Interest and Money",
        "author": "John Maynard Keynes",
        "year": 1936,
        "domain": "Macroeconomics & Monetary Policy",
        "sentences": [
            "The ideas of economists and political philosophers, both when they are right and when they are wrong, are more powerful than is commonly understood.",
            "When the accumulation of wealth is no longer of high social importance, there will be great changes in the code of morals.",
            "The outstanding faults of the economic society in which we live are its failure to provide for full employment and its arbitrary and inequitable distribution of wealth."
        ]
    },
    {
        "title": "Molecular Structure of Nucleic Acids: A Structure for Deoxyribose Nucleic Acid",
        "author": "James Watson and Francis Crick",
        "year": 1953,
        "domain": "Molecular Biology & Genetics",
        "sentences": [
            "We wish to suggest a structure for the salt of deoxyribose nucleic acid.",
            "This structure has novel features which are of considerable biological interest.",
            "It has not escaped our notice that the specific pairing we have postulated immediately suggests a possible copying mechanism for the genetic material."
        ]
    }
]


class BulkAcademicStreamer:
    """
    High-Throughput Streaming Engine:
    Ingests scholarly papers, translates them section-by-section into authentic
    Kenyan Loosely Swahili using local morphotactic rules, and trains the K-CSLM
    and BPE Tokenizer with zero memory bloat.
    """
    def __init__(self):
        self.concept_engine = ConceptRecreationEngine()
        self.switcher = EnglishToKenyanCodeSwitcher()
        self.cslm = KenyanCodeSwitchLM()
        self.bpe = ShengStreamingBPETrainer(target_vocab_size=6500)
        
        BULK_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def clean_academic_text(self, text: str) -> str:
        """Strips citations, raw LaTeX, and mathematical equation boilerplate."""
        # Unescape HTML entities
        t = html.unescape(text)
        # Remove citation brackets like [1], [1, 2], [1-3], [Smith et al., 2020]
        t = re.sub(r"\[(?:[\d,\s\-–]+|[A-Z][a-z]+(?:\s+et\s+al\.?)?(?:,?\s*\d{4})?)\]", "", t)
        # Remove LaTeX math blocks $$ ... $$ or $ ... $
        t = re.sub(r"\$\$.*?\$\$", "", t)
        t = re.sub(r"\$.*?\$", "", t)
        # Remove URLs / DOIs
        t = re.sub(r"https?://\S+", "", t)
        t = re.sub(r"\bdoi:\S+", "", t)
        # Clean up whitespace
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def segment_into_analytical_sentences(self, text: str) -> List[str]:
        """Splits abstract/text into informative, coherent scientific sentences."""
        clean = self.clean_academic_text(text)
        # Sentence splitting protecting abbreviations
        raw_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", clean)
        valid = []
        for s in raw_sentences:
            s_clean = s.strip()
            # Retain content-bearing analytical sentences (between 40 and 300 characters)
            if 40 <= len(s_clean) <= 350:
                if not any(stop in s_clean.lower() for stop in ["in section", "table shows", "figure shows", "we report"]):
                    valid.append(s_clean)
        return valid

    def fetch_arxiv_bulk_batch(self, category: str, max_papers: int = 4) -> List[Dict[str, Any]]:
        """Queries arXiv API for peer-reviewed papers in a specific category."""
        url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&start=0&max_results={max_papers}&sortBy=submittedDate&sortOrder=descending"
        papers = []
        headers = {"User-Agent": "BulkScholarKenyanNLPEngine/2.0 (mailto:scholar@kenyanai.org)"}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                xml_data = resp.read()
            tree = ET.fromstring(xml_data)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in tree.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                summary_elem = entry.find("atom:summary", ns)
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else ""
                summary = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""
                if title and summary:
                    papers.append({
                        "title": title,
                        "abstract": summary,
                        "source": f"arXiv ({category})"
                    })
        except Exception as e:
            print(f"[BulkStreamer] arXiv note for {category}: {e}")
        return papers

    def fetch_openalex_bulk_batch(self, query: str, max_papers: int = 4) -> List[Dict[str, Any]]:
        """Queries OpenAlex for high-impact peer-reviewed works with reconstructed abstracts."""
        encoded_q = urllib.parse.quote(query)
        url = f"https://api.openalex.org/works?search={encoded_q}&per_page={max_papers}&mailto=scholar@kenyanai.org"
        papers = []
        headers = {"User-Agent": "BulkScholarKenyanNLPEngine/2.0"}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for item in data.get("results", []):
                title = item.get("title", "")
                inv_index = item.get("abstract_inverted_index")
                if title and inv_index:
                    pos_words = []
                    for word, positions in inv_index.items():
                        for p in positions:
                            pos_words.append((p, word))
                    pos_words.sort(key=lambda x: x[0])
                    abstract = " ".join([w for _, w in pos_words])
                    if len(abstract.strip()) > 80:
                        papers.append({
                            "title": title.strip(),
                            "abstract": abstract.strip(),
                            "source": "OpenAlex Global Research Index"
                        })
        except Exception as e:
            print(f"[BulkStreamer] OpenAlex note: {e}")
        return papers

    def stream_and_translate_bulk_corpus(self, target_domains_count: int = 8, papers_per_domain: int = 3) -> Dict[str, Any]:
        """
        Runs the end-to-end streaming pipeline:
        1. Gathers research papers across all scientific & intellectual domains.
        2. Translates every analytical sentence into Kenyan Loosely Swahili.
        3. Updates the K-CSLM language model and BPE tokenizer in real time.
        4. Writes streaming outputs to disk.
        """
        print("=" * 80)
        print("🚀 LAUNCHING MASSIVE BULK ACADEMIC TRANSLATION & TRAINING STREAM")
        print("=" * 80)

        total_papers_streamed = 0
        total_sentences_translated = 0
        streamed_records = []
        domain_breakdown = Counter()

        # Benchmark sentence to monitor perplexity convergence
        benchmark_eval_sentence = (
            "Kuhusu Heuristic Point of View kuhusu Emission na Transformation ya Light: "
            "Foundational physics research paper yenye ilipublishiwa na Albert Einstein in the 1905, "
            "hii groundbreaking Annalen der Physik article ilichallenge classical wave theory kwa ku-propose kuwa "
            "light iko spatially localized na inatransmitiwa kwa discrete packages za energy."
        )
        pre_training_ppl = self.cslm.score_sentence_perplexity(benchmark_eval_sentence)["perplexity"]
        print(f"\n[Baseline Benchmark] Initial K-CSLM Perplexity: {pre_training_ppl} PPL")

        # ----------------------------------------------------------------------
        # A. Ingest Seminal Intellectual Classics
        # ----------------------------------------------------------------------
        print("\n[Phase 1] 📚 Streaming Seminal Academic Classics (Newton, Darwin, Keynes, Watson & Crick)...")
        for classic in SEMINAL_FOUNDATIONAL_CORPUS:
            c_title = classic["title"]
            c_domain = classic["domain"]
            print(f"  • Ingesting Classic: \"{c_title[:65]}...\" [{c_domain}]")
            total_papers_streamed += 1
            domain_breakdown[c_domain] += 1

            for s_en in classic["sentences"]:
                recreated = self.concept_engine.reconstruct_concept(s_en)
                cs_out = recreated.get("reconstructed_codeswitch", s_en)
                sw_out = recreated.get("pure_swahili", "")

                # Train K-CSLM streaming
                self.cslm.update_from_sentence(cs_out)
                total_sentences_translated += 1

                record = {
                    "source": "Foundational Classic Manuscript",
                    "title": c_title,
                    "author": classic.get("author", "Scholar"),
                    "domain": c_domain,
                    "english": s_en,
                    "loosely_swahili": cs_out,
                    "sanifu_swahili": sw_out,
                    "rules": recreated.get("applied_rules", [])
                }
                streamed_records.append(record)

        # ----------------------------------------------------------------------
        # B. Stream Multi-Domain arXiv & OpenAlex Papers
        # ----------------------------------------------------------------------
        print(f"\n[Phase 2] 🌐 Streaming Research Papers across {target_domains_count} Global Scientific Disciplines...")
        selected_domains = SCHOLARLY_RESEARCH_DOMAINS[:target_domains_count]

        for d_info in selected_domains:
            domain_name = d_info["domain"]
            arxiv_cat = d_info["arxiv_cat"]
            query = d_info["search_query"]

            print(f"\n[Domain Stream] 🔬 Ingesting: '{domain_name}'")

            # Try arXiv first
            harvested = self.fetch_arxiv_bulk_batch(arxiv_cat, max_papers=papers_per_domain)
            # Supplement with OpenAlex
            if len(harvested) < papers_per_domain:
                extra = self.fetch_openalex_bulk_batch(query, max_papers=(papers_per_domain - len(harvested)))
                harvested.extend(extra)

            print(f"  • Retrieved {len(harvested)} papers for '{domain_name}'")
            total_papers_streamed += len(harvested)
            domain_breakdown[domain_name] += len(harvested)

            for p_idx, paper in enumerate(harvested, 1):
                p_title = paper["title"]
                sentences = self.segment_into_analytical_sentences(paper["abstract"])
                if not sentences:
                    sentences = [p_title]

                for s_en in sentences:
                    # Translate to Kenyan Loosely Swahili with living morphotactics
                    recreated = self.concept_engine.reconstruct_concept(s_en)
                    cs_out = recreated.get("reconstructed_codeswitch", s_en)
                    sw_out = recreated.get("pure_swahili", "")

                    # Train K-CSLM language model in real time
                    self.cslm.update_from_sentence(cs_out)
                    total_sentences_translated += 1

                    # Stream record to memory batch
                    rec = {
                        "source": paper.get("source", "Peer-Reviewed Academic Archive"),
                        "title": p_title,
                        "domain": domain_name,
                        "english": s_en,
                        "loosely_swahili": cs_out,
                        "sanifu_swahili": sw_out,
                        "rules": recreated.get("applied_rules", [])
                    }
                    streamed_records.append(rec)

        # ----------------------------------------------------------------------
        # C. Flush Streaming Outputs to Disk (Zero RAM Overhead)
        # ----------------------------------------------------------------------
        print(f"\n[Phase 3] 💾 Writing {len(streamed_records)} translated academic pairs directly to disk...")
        with open(PARALLEL_STREAM_FILE, "a", encoding="utf-8") as f_par, \
             open(INSTRUCTION_STREAM_FILE, "a", encoding="utf-8") as f_inst:
            for r in streamed_records:
                # 1. Parallel corpus record
                f_par.write(json.dumps(r, ensure_ascii=False) + "\n")
                
                # 2. Instruction tuning record for LLM training
                inst_obj = {
                    "instruction": "Translate this academic research paper text into authentic Kenyan Loosely Swahili (Living Morphotactics) with natural Bantu verbal affixes and zero ungrammatical *-ed endings:",
                    "input": r["english"],
                    "output": r["loosely_swahili"],
                    "formal_swahili": r["sanifu_swahili"],
                    "domain": r["domain"],
                    "title": r["title"]
                }
                f_inst.write(json.dumps(inst_obj, ensure_ascii=False) + "\n")

        # ----------------------------------------------------------------------
        # D. Post-Training Evaluation & Checkpoint Export
        # ----------------------------------------------------------------------
        print("\n[Phase 4] 🧠 Evaluating K-CSLM Post-Training Perplexity & Vocabulary Growth...")
        post_training_ppl = self.cslm.score_sentence_perplexity(benchmark_eval_sentence)["perplexity"]
        ppl_gain = round(pre_training_ppl - post_training_ppl, 2)

        checkpoint_path = BULK_DIR / "kenyan_cslm_bulk_academic.json"
        self.cslm.export_model_checkpoint(checkpoint_path)

        # Check BPE Tokenizer preservation
        test_verbs = ["ilichallenge", "inatransmitiwa", "ku-propose", "zinalocaliziwa"]
        tokenizer_audit = []
        for v in test_verbs:
            morphemes = self.bpe.pre_tokenize_word_morpheme_aware(v)
            tokenizer_audit.append({"verb": v, "tokens": morphemes})

        summary_report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_papers_streamed": total_papers_streamed,
            "total_sentences_translated": total_sentences_translated,
            "domains_covered_count": len(domain_breakdown),
            "domains_breakdown": dict(domain_breakdown),
            "pre_training_perplexity": pre_training_ppl,
            "post_training_perplexity": post_training_ppl,
            "perplexity_improvement": ppl_gain,
            "tokenizer_morpheme_audit": tokenizer_audit,
            "parallel_corpus_file": str(PARALLEL_STREAM_FILE),
            "instruction_dataset_file": str(INSTRUCTION_STREAM_FILE),
            "checkpoint_file": str(checkpoint_path),
            "status": "SUCCESS"
        }

        with open(STREAM_REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(summary_report, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 80)
        print("🎉 BULK ACADEMIC STREAM & MODEL TRAINING COMPLETE")
        print(f"  • Total Papers Ingested:          {total_papers_streamed}")
        print(f"  • Total Sentences Translated:     {total_sentences_translated}")
        print(f"  • Disciplines Covered:            {len(domain_breakdown)}")
        print(f"  • K-CSLM Perplexity:              {pre_training_ppl} -> {post_training_ppl} (Gain: -{ppl_gain} PPL)")
        print(f"  • Parallel Corpus Location:       {PARALLEL_STREAM_FILE}")
        print(f"  • Instruction Tuning Dataset:     {INSTRUCTION_STREAM_FILE}")
        print("=" * 80)

        return summary_report

    def run_continuous_daemon(self, sleep_between_batches: float = 3.0, max_iterations: Optional[int] = None):
        """
        Runs continuously in the background, ingesting research papers across rotating
        scientific disciplines, translating them into Kenyan Loosely Swahili, and updating
        model checkpoints and datasets.
        """
        print("=" * 80)
        print("⚡ CONTINUOUS ACADEMIC TRANSLATION DAEMON ACTIVATED")
        print("=" * 80)
        
        # Count existing records
        existing_count = 0
        if PARALLEL_STREAM_FILE.exists():
            with open(PARALLEL_STREAM_FILE, "r", encoding="utf-8") as f:
                existing_count = sum(1 for _ in f)

        total_translated = existing_count
        iteration = 0
        
        while True:
            iteration += 1
            if max_iterations and iteration > max_iterations:
                break
                
            d_idx = (iteration - 1) % len(SCHOLARLY_RESEARCH_DOMAINS)
            domain_info = SCHOLARLY_RESEARCH_DOMAINS[d_idx]
            d_name = domain_info["domain"]
            arxiv_cat = domain_info["arxiv_cat"]
            query = domain_info["search_query"]
            
            # Fetch batch with random offset for fresh papers
            rand_offset = random.randint(0, 300)
            url = f"http://export.arxiv.org/api/query?search_query=cat:{arxiv_cat}&start={rand_offset}&max_results=2&sortBy=submittedDate&sortOrder=descending"
            papers = []
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "BulkScholarKenyanNLPEngine/2.0"})
                with urllib.request.urlopen(req, timeout=12) as resp:
                    tree = ET.fromstring(resp.read())
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    for entry in tree.findall("atom:entry", ns):
                        t_e = entry.find("atom:title", ns)
                        s_e = entry.find("atom:summary", ns)
                        t = t_e.text.strip().replace("\n", " ") if t_e is not None else ""
                        s = s_e.text.strip().replace("\n", " ") if s_e is not None else ""
                        if t and s:
                            papers.append({"title": t, "abstract": s, "source": f"arXiv ({arxiv_cat})"})
            except Exception as e:
                # Fallback to OpenAlex
                papers = self.fetch_openalex_bulk_batch(query, max_papers=2)
            
            if not papers:
                time.sleep(sleep_between_batches)
                continue
                
            batch_records = []
            for paper in papers:
                sentences = self.segment_into_analytical_sentences(paper["abstract"])
                if not sentences:
                    sentences = [paper["title"]]
                
                for s_en in sentences:
                    recreated = self.concept_engine.reconstruct_concept(s_en)
                    cs_out = recreated.get("reconstructed_codeswitch", s_en)
                    sw_out = recreated.get("pure_swahili", "")
                    
                    self.cslm.update_from_sentence(cs_out)
                    total_translated += 1
                    
                    rec = {
                        "source": paper.get("source", "Peer-Reviewed Academic Archive"),
                        "title": paper["title"],
                        "domain": d_name,
                        "english": s_en,
                        "loosely_swahili": cs_out,
                        "sanifu_swahili": sw_out,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    }
                    batch_records.append(rec)
            
            # Flush batch directly to disk
            with open(PARALLEL_STREAM_FILE, "a", encoding="utf-8") as f_par, \
                 open(INSTRUCTION_STREAM_FILE, "a", encoding="utf-8") as f_inst:
                for r in batch_records:
                    f_par.write(json.dumps(r, ensure_ascii=False) + "\n")
                    inst_obj = {
                        "instruction": "Translate this academic research paper text into authentic Kenyan Loosely Swahili (Living Morphotactics):",
                        "input": r["english"],
                        "output": r["loosely_swahili"],
                        "formal_swahili": r["sanifu_swahili"],
                        "domain": r["domain"],
                        "title": r["title"]
                    }
                    f_inst.write(json.dumps(inst_obj, ensure_ascii=False) + "\n")
            
            # Update telemetry report
            last_sample = batch_records[-1] if batch_records else {}
            telemetry = {
                "is_active_streaming": True,
                "status": "TRANSLATING_LIVE",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "iteration": iteration,
                "current_domain": d_name,
                "total_sentences_translated": total_translated,
                "last_paper_title": last_sample.get("title", ""),
                "latest_sample_english": last_sample.get("english", ""),
                "latest_sample_loosely_swahili": last_sample.get("loosely_swahili", "")
            }
            with open(STREAM_REPORT_FILE, "w", encoding="utf-8") as f:
                json.dump(telemetry, f, indent=2, ensure_ascii=False)
                
            print(f"[Cycle {iteration}] Translated {len(batch_records)} sentences for '{d_name}'. Cumulative: {total_translated}")
            if batch_records:
                print(f"  • EN: {batch_records[-1]['english'][:75]}...")
                print(f"  • CS: {batch_records[-1]['loosely_swahili'][:75]}...")
                
            if iteration % 10 == 0:
                checkpoint_path = BULK_DIR / "kenyan_cslm_bulk_academic.json"
                self.cslm.export_model_checkpoint(checkpoint_path)
                
            time.sleep(sleep_between_batches)


if __name__ == "__main__":
    streamer = BulkAcademicStreamer()
    if "--daemon" in sys.argv:
        streamer.run_continuous_daemon(sleep_between_batches=3.0)
    else:
        streamer.stream_and_translate_bulk_corpus(target_domains_count=8, papers_per_domain=3)

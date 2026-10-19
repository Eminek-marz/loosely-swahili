"""
Anjiru.AI Local Document Search & Retrieval-Augmented Generation (RAG) Engine
Indexes workspace files using an Inverted Index & BM25 / TF-IDF scoring to ground answers in local documents.
"""

import os
import re
import math
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_PROJECTS = PROJECT_ROOT / "workspace" / "projects"


class AnjiruRAGSearchEngine:
    """Fast, local lexical & semantic inverted-index retrieval engine."""

    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir or WORKSPACE_PROJECTS
        self.documents: List[Dict[str, Any]] = []
        self.inverted_index: Dict[str, List[Tuple[int, float]]] = defaultdict(list)
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.vocab: set = set()
        self.rebuild_index()

    def _tokenize(self, text: str) -> List[str]:
        """Normalize and tokenize text into clean search stems."""
        clean = re.sub(r'[^a-zA-Z0-9_\-\s]', ' ', text.lower())
        tokens = [t.strip() for t in clean.split() if len(t.strip()) > 1]
        # Basic stopword filter
        stopwords = {"the", "a", "an", "is", "in", "it", "of", "on", "and", "or", "to", "for", "with", "as", "by", "that", "this"}
        return [t for t in tokens if t not in stopwords]

    def rebuild_index(self):
        """Scans workspace projects and indexes text chunks."""
        self.documents = []
        self.inverted_index.clear()
        self.doc_lengths = []

        allowed_exts = {".py", ".md", ".txt", ".csv", ".json"}
        doc_id = 0

        for root, _, files in os.walk(str(self.workspace_dir)):
            for f in files:
                ext = Path(f).suffix.lower()
                if ext in allowed_exts:
                    full_p = Path(root) / f
                    rel_p = str(full_p.relative_to(self.workspace_dir)).replace("\\", "/")
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="replace") as fp:
                            content = fp.read()
                        
                        # Chunk file by double-newline or paragraphs (approx 150-300 words)
                        paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 20]
                        if not paragraphs:
                            paragraphs = [content[:1200]]

                        for p_idx, para in enumerate(paragraphs):
                            tokens = self._tokenize(para)
                            if not tokens:
                                continue
                            
                            doc_meta = {
                                "doc_id": doc_id,
                                "file_path": rel_p,
                                "file_name": f,
                                "chunk_idx": p_idx + 1,
                                "text": para[:800],
                                "token_count": len(tokens)
                            }
                            self.documents.append(doc_meta)
                            self.doc_lengths.append(len(tokens))

                            # Count term frequencies
                            term_counts = Counter(tokens)
                            for term, count in term_counts.items():
                                self.vocab.add(term)
                                self.inverted_index[term].append((doc_id, float(count)))

                            doc_id += 1
                    except Exception:
                        pass

        if self.doc_lengths:
            self.avg_doc_len = sum(self.doc_lengths) / len(self.doc_lengths)
        else:
            self.avg_doc_len = 1.0

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Executes BM25 scoring algorithm against local inverted index:
        Score(D, Q) = sum( IDF(q) * (f(q, D) * (k1 + 1)) / (f(q, D) + k1 * (1 - b + b * (|D| / avgdl))) )
        """
        query_tokens = self._tokenize(query)
        if not query_tokens or not self.documents:
            return []

        k1 = 1.5
        b = 0.75
        n_docs = len(self.documents)

        scores: Dict[int, float] = defaultdict(float)

        for term in query_tokens:
            postings = self.inverted_index.get(term, [])
            if not postings:
                continue

            df = len(postings)
            # IDF with smoothing
            idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)

            for d_id, tf in postings:
                doc_len = self.doc_lengths[d_id]
                numerator = tf * (k1 + 1.0)
                denominator = tf + k1 * (1.0 - b + b * (doc_len / self.avg_doc_len))
                scores[d_id] += idf * (numerator / max(1e-5, denominator))

        # Rank documents
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for d_id, score in ranked:
            doc = self.documents[d_id]
            results.append({
                "score": round(score, 3),
                "file_path": doc["file_path"],
                "file_name": doc["file_name"],
                "chunk_idx": doc["chunk_idx"],
                "snippet": doc["text"]
            })

        return results

    def answer_with_rag(self, query: str) -> Dict[str, Any]:
        """Retrieves matching chunks and synthesizes grounded answer."""
        retrieved = self.search(query, top_k=3)
        if not retrieved:
            return {
                "query": query,
                "found": False,
                "answer": f"No direct matching text found in local workspace for query '{query}'.",
                "citations": []
            }

        citations = [f"{r['file_path']} (Chunk #{r['chunk_idx']}, Score: {r['score']})" for r in retrieved]
        top_snippet = retrieved[0]["snippet"]

        answer = (
            f"Based on your local workspace records in **{retrieved[0]['file_path']}**:\n\n"
            f"> \"{top_snippet[:400].strip()}...\"\n\n"
            f"Found **{len(retrieved)} relevant context references** matching your query."
        )

        return {
            "query": query,
            "found": True,
            "answer": answer,
            "top_match": retrieved[0],
            "citations": citations,
            "results": retrieved
        }


# Global singleton
_rag_engine = None

def get_rag_engine() -> AnjiruRAGSearchEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = AnjiruRAGSearchEngine()
    return _rag_engine

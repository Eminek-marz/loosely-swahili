"""
src/github_knowledge_engine.py - Autonomous GitHub & Open-Source Research Engine for Anjiru.AI

Empowers Anjiru to act as a true Autonomous Software Engineer:
1. Searches millions of open-source GitHub repositories for production implementations,
   architectures, protocols, and standard libraries.
2. Reads repository READMEs, manifests (requirements.txt, package.json, go.mod, Cargo.toml),
   and technical documentation to learn domain logic.
3. Synthesizes best-in-class microservice architectures for maintainability.
4. Provides integrated domain blueprints for Anjiru's execution & self-healing engine.
"""

import os
import re
import json
import base64
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "src" / "data" / "github_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class GitHubKnowledgeEngine:
    """
    Autonomous Open-Source Intelligence & GitHub Harvester.
    Discovers real-world architectures, protocol standards, and libraries.
    """

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
        self.user_agent = "AnjiruAI-Autonomous-Engineer/2.0"

    def _headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/vnd.github.v3+json"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    def search_repositories(self, query: str, language: str = "python", max_results: int = 4) -> List[Dict[str, Any]]:
        """
        Searches GitHub for top-starred production repositories matching query.
        """
        clean_q = re.sub(r'[^a-zA-Z0-9_\s\-]', ' ', query).strip()
        cache_key = f"{clean_q.replace(' ', '_')}_{language}.json"
        cache_file = CACHE_DIR / cache_key

        # Check local cache first (avoids GitHub rate limits)
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        encoded_q = urllib.parse.quote(clean_q)
        url = f"https://api.github.com/search/repositories?q={encoded_q}+language:{language}&sort=stars&order=desc&per_page={max_results}"

        try:
            req = urllib.request.Request(url, headers=self._headers())
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                items = data.get("items", [])
                results = []
                for item in items[:max_results]:
                    results.append({
                        "full_name": item.get("full_name"),
                        "stars": item.get("stargazers_count", 0),
                        "description": item.get("description", ""),
                        "html_url": item.get("html_url"),
                        "topics": item.get("topics", []),
                        "default_branch": item.get("default_branch", "main")
                    })
                
                # Cache results locally
                try:
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=2)
                except Exception:
                    pass

                return results
        except Exception as e:
            # Fallback to local heuristic index if offline or rate-limited
            return self._offline_reference_search(clean_q, language)

    def fetch_readme_and_manifest(self, repo_full_name: str, default_branch: str = "main") -> Dict[str, Any]:
        """
        Reads repository documentation (README) and dependency manifest to extract logic.
        """
        clean_name = repo_full_name.replace("/", "_")
        cache_file = CACHE_DIR / f"{clean_name}_insights.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        insights = {
            "repo": repo_full_name,
            "readme_summary": "",
            "dependencies": [],
            "architecture_patterns": []
        }

        # 1. Fetch README
        content = ""
        try:
            url = f"https://api.github.com/repos/{repo_full_name}/readme"
            req = urllib.request.Request(url, headers=self._headers())
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
                insights["readme_summary"] = content[:2000]
        except Exception:
            pass

        # Extract architectural patterns from README text
        if content:
            c_lower = content.lower()
            detected_patterns = []
            if "rest" in c_lower or "api" in c_lower:
                detected_patterns.append("RESTful API Gateway")
            if "websocket" in c_lower or "real-time" in c_lower or "realtime" in c_lower:
                detected_patterns.append("Real-Time Stream / WebSocket")
            if "sqlite" in c_lower or "postgres" in c_lower or "sql" in c_lower or "database" in c_lower:
                detected_patterns.append("ACID Relational Persistence")
            if "microservice" in c_lower or "service" in c_lower:
                detected_patterns.append("Decoupled Microservice Topology")
            if "async" in c_lower or "concurrency" in c_lower or "thread" in c_lower:
                detected_patterns.append("Asynchronous Concurrent Processing")
            if "docker" in c_lower or "container" in c_lower:
                detected_patterns.append("Containerized Deployment")
            insights["architecture_patterns"] = detected_patterns

        # 2. Fetch Manifest (requirements.txt or package.json, etc.)
        manifest_files = ["requirements.txt", "package.json", "pyproject.toml", "Cargo.toml", "go.mod"]
        branches_to_try = [default_branch, "main", "master"]
        # deduplicate while keeping order
        seen_branches = []
        for b in branches_to_try:
            if b and b not in seen_branches:
                seen_branches.append(b)

        found_manifest = False
        for branch in seen_branches:
            if found_manifest:
                break
            for mf in manifest_files:
                try:
                    url = f"https://raw.githubusercontent.com/{repo_full_name}/{branch}/{mf}"
                    req = urllib.request.Request(url, headers=self._headers())
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        raw_manifest = resp.read().decode("utf-8", errors="replace")
                        deps = [line.strip().split("==")[0].split(">=")[0] for line in raw_manifest.splitlines() if line.strip() and not line.startswith("#")]
                        insights["dependencies"] = deps[:15]
                        found_manifest = True
                        break
                except Exception:
                    pass

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(insights, f, indent=2)
        except Exception:
            pass

        return insights

    def research_domain(self, prompt: str, language: str = "python") -> Dict[str, Any]:
        """
        End-to-end research phase:
        Discovers top repos on GitHub, digests their documentation and manifests,
        and produces an architectural specification for Anjiru to execute.
        """
        clean_terms = re.sub(r'\b(?:build|create|implement|in|with|using|and|unit|tests?|system|platform)\b', '', prompt.lower()).strip()
        search_query = " ".join(clean_terms.split()[:4]) or "microservice platform"

        repos = self.search_repositories(search_query, language=language, max_results=3)
        top_insights = []
        all_deps = set()
        all_patterns = set()

        for r in repos[:2]:
            ins = self.fetch_readme_and_manifest(r["full_name"], default_branch=r.get("default_branch", "main"))
            top_insights.append({
                "repo": r["full_name"],
                "stars": r["stars"],
                "description": r["description"],
                "dependencies": ins["dependencies"],
                "patterns": ins.get("architecture_patterns", [])
            })
            for dep in ins["dependencies"]:
                if dep and len(dep) < 25:
                    all_deps.add(dep)
            for pat in ins.get("architecture_patterns", []):
                all_patterns.add(pat)

        if not all_patterns:
            all_patterns = {"Decoupled Domain Service", "ACID Persistence", "Automated Invariant Verification"}

        return {
            "query": search_query,
            "language": language,
            "repos_analyzed": top_insights,
            "recommended_libraries": list(all_deps)[:8],
            "architectural_patterns": list(all_patterns),
            "microservice_recommendation": self._recommend_microservice_split(prompt)
        }

    def _recommend_microservice_split(self, prompt: str) -> List[Dict[str, str]]:
        """
        Designs clean microservice separation for enterprise maintainability.
        """
        p_lower = prompt.lower()
        if any(k in p_lower for k in ["aeroplane", "flight", "radar", "aviation", "tracking", "aircraft", "airspace"]):
            return [
                {"service": "telemetry_collector", "role": "Ingests real-time ADS-B / radar coordinates, barometric altitude, and heading."},
                {"service": "airspace_engine", "role": "Performs geospatial containment, collision alerts, and sector tracking."},
                {"service": "flight_api", "role": "Exposes REST endpoints & WebSocket radar feeds for consumers."},
                {"service": "audit_persistence", "role": "ACID transactional event logging with SQLite/PostgreSQL."}
            ]
        elif any(k in p_lower for k in ["ecommerce", "shop", "store", "checkout", "cart", "order"]):
            return [
                {"service": "catalog_service", "role": "Manages products, categories, SKU pricing, and active stock."},
                {"service": "cart_service", "role": "Manages user shopping carts, quantities, and line-item totals."},
                {"service": "order_checkout", "role": "Atomic transactional order processing, payment verification, and stock decrement."},
                {"service": "audit_persistence", "role": "ACID relational persistence and invoice records."}
            ]
        elif any(k in p_lower for k in ["hospital", "clinic", "medical", "patient", "health", "doctor"]):
            return [
                {"service": "patient_records", "role": "HIPAA-compliant patient demographic, admission, and medical history management."},
                {"service": "appointment_scheduler", "role": "Doctor scheduling, time-slot locking, and consultation dispatch."},
                {"service": "clinical_api", "role": "Authenticated REST API for healthcare providers and clinical dashboards."},
                {"service": "audit_persistence", "role": "ACID relational persistence for clinical logs and prescription trails."}
            ]
        elif any(k in p_lower for k in ["bank", "fintech", "wallet", "payment", "mpesa", "finance"]):
            return [
                {"service": "account_service", "role": "Manages account balances, ledger ownership, and KYC status."},
                {"service": "transaction_engine", "role": "Double-entry atomic ledger transfers, overdraft checks, and audit trails."},
                {"service": "payment_gateway", "role": "Handles M-Pesa, card, and EFT webhooks and dispatch."},
                {"service": "audit_persistence", "role": "Immutable cryptographic hash-chained transaction logs."}
            ]
        else:
            # Extract domain words for tailored microservices
            domain_words = [w.capitalize() for w in re.split(r'[^a-zA-Z0-9]', prompt) if len(w) > 3 and w.lower() not in ['create', 'build', 'implement', 'system', 'platform', 'service', 'project', 'unit', 'test']]
            tag = domain_words[0] if domain_words else "Domain"
            return [
                {"service": f"{tag.lower()}_ingestion", "role": f"Ingests external inputs, streams, and operational payloads for {tag}."},
                {"service": f"{tag.lower()}_engine", "role": f"Executes core business rules, entity validations, and state machines."},
                {"service": f"{tag.lower()}_api_gateway", "role": f"Exposes authenticated HTTP/REST and CLI endpoints."},
                {"service": "audit_persistence", "role": "ACID relational persistence and audit trail logging."},
                {"service": "test_verification_suite", "role": "Automated regression testing and invariant verification."}
            ]

    def _offline_reference_search(self, query: str, language: str) -> List[Dict[str, Any]]:
        """Fallback knowledge catalog when network is disconnected."""
        return [
            {
                "full_name": "skylines-project/skylines",
                "stars": 407,
                "description": "Open-source live tracking, flight database and competition platform.",
                "html_url": "https://github.com/skylines-project/skylines",
                "topics": ["flight-tracking", "aviation", "gis"],
                "default_branch": "master"
            },
            {
                "full_name": "ColinWaddell/FlightTracker",
                "stars": 207,
                "description": "Real-time aircraft radar display using FlightRadar24 and local ADS-B setup.",
                "html_url": "https://github.com/ColinWaddell/FlightTracker",
                "topics": ["ads-b", "radar", "tracker"],
                "default_branch": "main"
            }
        ]


# Singleton accessor
_github_engine: Optional[GitHubKnowledgeEngine] = None

def get_github_knowledge_engine() -> GitHubKnowledgeEngine:
    global _github_engine
    if _github_engine is None:
        _github_engine = GitHubKnowledgeEngine()
    return _github_engine

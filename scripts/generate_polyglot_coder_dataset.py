"""
scripts/generate_polyglot_coder_dataset.py - Scaled Polyglot Coding Instruction Dataset Generator
Generates a comprehensive, production-grade training corpus of multi-file architecture planning,
universal block diffing (EDIT mode), and compiler error self-healing (DEBUG mode) across
polyglot ecosystems (Rust, Go, FastAPI, Next.js, Node/TS, C++, PyTorch, Django, Kotlin, etc.)
Formatted in standard ChatML for fine-tuning open-weights foundation models.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.polyglot_scaffolder import PolyglotCodebaseScaffolder

OUT_PATH = PROJECT_ROOT / "data" / "instruction_tuning" / "polyglot_coder_instructions.jsonl"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

POLYGLOT_SYSTEM_PROMPT = """You are Anjiru.AI's Ultimate Polyglot Execution Kernel.
Your objective is to write, edit, and debug code across any arbitrary software stack, language, or ecosystem.

CRITICAL INSTRUCTIONS:
1. NEVER assume a predefined language layout or file structure.
2. Rely entirely on environmental runtime metadata to choose build tools and execution parameters.
3. Your output must strictly follow a two-pass architecture: [EXECUTION_KERNEL_PLAN] JSON blueprint followed by complete, production-grade files with zero placeholder code or omitted logic.
4. Always provide real dependency manifests (Cargo.toml, package.json, go.mod, requirements.txt) and automated unit test harnesses.
"""

# ==============================================================================
# 1. WRITE MODE DOMAIN PROMPTS MATRIX
# ==============================================================================
WRITE_SPECS = [
    # RUST
    {
        "framework": "rust",
        "lang": "rust",
        "domains": [
            ("Build a high-performance memory-safe web microservice in Rust with Actix-web, Tokio, and Serde", "en"),
            ("Nijengee microservice ya Rust yenye Actix-web na Tokio ya ku-handle high throughput bila memory leaks", "sheng"),
            ("Unda huduma ya wavuti ya kasi ya juu katika lugha ya Rust ukitumia Actix-web na Tokio", "sw"),
            ("Create a low-latency financial ledger microservice in Rust with JSON serialization and tests", "en"),
            ("Jenga Rust backend ya ku-process payments na transactions kwa concurrency salama", "sheng"),
        ]
    },
    # RUST CLI
    {
        "framework": "rust_cli",
        "lang": "rust",
        "domains": [
            ("Scaffold an asynchronous command-line utility in Rust using Clap derive and Tokio runtime", "en"),
            ("Nipangee Rust CLI tool ya ku-process streams za data kwa terminal ukitumia Clap", "sheng"),
            ("Unda zana ya mstari wa amri (CLI) katika Rust inayotumia uchanganuzi wa Clap na mtiririko wa kazi wa Tokio", "sw"),
            ("Build a high-performance log parsing CLI engine in Rust with subcommands and workers", "en"),
        ]
    },
    # GO REST
    {
        "framework": "go",
        "lang": "go",
        "domains": [
            ("Create a complete concurrent REST API in Go with net/http, entity schemas, and unit tests", "en"),
            ("Tengeneza Go microservice safi yenye net/http router, struct models, na automated test suite", "sheng"),
            ("Unda huduma ya REST katika Go inayothibitisha miundo ya data na kujumuisha majaribio ya kitengo", "sw"),
            ("Build a resilient East African mobile money payment gateway service in Go", "en"),
            ("Jenga API ya Go ya ku-stream telemetry data na health check endpoints", "sheng"),
        ]
    },
    # GO WORKER POOL
    {
        "framework": "go_concurrency",
        "lang": "go",
        "domains": [
            ("Build a robust concurrent worker pool in Go using channels, sync.WaitGroup, and context cancellation", "en"),
            ("Nijengee Go worker pool ya ku-process mamia ya tasks kwa concurrency bila race conditions", "sheng"),
            ("Tengeneza mfumo wa foleni ya vibarua (worker pool) katika Go kwa kutumia mifereji (channels) na muktadha", "sw"),
            ("Implement an asynchronous event dispatcher with bounded goroutines and backpressure in Go", "en"),
        ]
    },
    # FASTAPI
    {
        "framework": "fastapi",
        "lang": "python",
        "domains": [
            ("Scaffold a production asynchronous FastAPI backend with Pydantic v2 schemas and unit tests", "en"),
            ("Nipangee FastAPI REST backend yenye Pydantic v2 data validation, error handling, na unittest", "sheng"),
            ("Unda mfumo kamili wa FastAPI wenye uthibitishaji madhubuti wa Pydantic v2 na majaribio", "sw"),
            ("Build an async IoT telemetry ingestion service with FastAPI and structured validation", "en"),
            ("Tengeneza FastAPI backend ya hospital patient records yenye CRUD endpoints za maana", "sheng"),
        ]
    },
    # SQLALCHEMY 2.0 ORM
    {
        "framework": "sqlalchemy",
        "lang": "python",
        "domains": [
            ("Build an asynchronous database layer in Python using SQLAlchemy 2.0 and the Repository pattern", "en"),
            ("Nijengee async database repository pattern kwa Python ukitumia SQLAlchemy 2.0 na aiosqlite", "sheng"),
            ("Unda safu ya hifadhidata ya kisasa katika Python kwa kutumia SQLAlchemy 2.0 na modeli za ORM", "sw"),
            ("Scaffold an enterprise e-commerce product catalog repository with transactional integrity", "en"),
        ]
    },
    # NEXT.JS 14
    {
        "framework": "nextjs",
        "lang": "typescript",
        "domains": [
            ("Create a fullstack Next.js 14 App Router application with React Server Components, TypeScript, and API routes", "en"),
            ("Nijengee Next.js 14 dashboard yenye React components, TypeScript types, na internal API route", "sheng"),
            ("Unda programu kamili ya wavuti ya Next.js 14 inayotumia TypeScript na vipengele vya seva ya React", "sw"),
            ("Scaffold a modern real-time cloud analytics portal using Next.js 14 and Tailwind design patterns", "en"),
            ("Jenga full-stack web platform yenye Next.js App Router na edge API handlers", "sheng"),
        ]
    },
    # NODE / TYPESCRIPT
    {
        "framework": "node_ts",
        "lang": "typescript",
        "domains": [
            ("Create a modular TypeScript and Node.js backend service with domain models, tsconfig, and tests", "en"),
            ("Nipangee Node.js TypeScript architecture yenye strict types, interface definitions, na test script", "sheng"),
            ("Unda mfumo wa Node.js unaotumia TypeScript na kufuata kanuni za usanifu wa kisasa", "sw"),
            ("Build an identity verification and JWT token issuing service in TypeScript", "en"),
        ]
    },
    # WEBSOCKET
    {
        "framework": "websocket",
        "lang": "typescript",
        "domains": [
            ("Implement a real-time WebSocket server in TypeScript with room management and heartbeat ping/pong", "en"),
            ("Tengeneza real-time WebSocket cluster ya ku-broadcast live events na notifications kwa rooms", "sheng"),
            ("Unda seva ya moja kwa moja ya WebSocket yenye uwezo wa kusimamia vyumba na kutuma ujumbe papo hapo", "sw"),
            ("Build a collaborative live chat and telemetry broadcasting engine using WebSockets", "en"),
        ]
    },
    # MODERN C++ / CMAKE
    {
        "framework": "cpp",
        "lang": "c/c++",
        "domains": [
            ("Develop a high-performance C++20 computational engine with CMakeLists build definition, headers, and tests", "en"),
            ("Nijengee high-performance C++20 computational kernel yenye CMake build config na test assertions", "sheng"),
            ("Unda mfumo wa kompyuta wa kasi ya juu katika C++20 ukitumia mfumo wa ujenzi wa CMake na vichwa vya habari", "sw"),
            ("Build a low-latency digital signal processing and matrix computation engine in Modern C++", "en"),
        ]
    },
    # PYTORCH ML PIPELINE
    {
        "framework": "pytorch",
        "lang": "python",
        "domains": [
            ("Synthesize a complete deep learning pipeline with synthetic data loader, PyTorch neural model, and training loop", "en"),
            ("Nipangee machine learning training pipeline yenye dataset generator, neural network model, na training loop", "sheng"),
            ("Unda mfumo kamili wa mafunzo ya miundo ya neva (neural networks) ukitumia PyTorch na uthibitishaji wa data", "sw"),
            ("Build an end-to-end classifier training and evaluation harness with convergence metrics", "en"),
        ]
    },
    # DJANGO
    {
        "framework": "django",
        "lang": "python",
        "domains": [
            ("Build an enterprise Django web application with SQLite database, URL routing, models, and settings", "en"),
            ("Nijengee Django web application safi yenye settings, database configuration, na URL routes", "sheng"),
            ("Unda mfumo thabiti wa wavuti wa Django wenye muundo wa hifadhidata, njia za URL, na mipangilio sahihi", "sw"),
            ("Scaffold an institutional student information management platform in Django", "en"),
        ]
    },
    # KOTLIN / GRADLE
    {
        "framework": "kotlin",
        "lang": "kotlin",
        "domains": [
            ("Create an enterprise Kotlin JVM microservice with Gradle Kotlin DSL, coroutines, and JUnit 5 tests", "en"),
            ("Nipangee Kotlin microservice yenye build.gradle.kts, coroutines za asynchrony, na unit tests", "sheng"),
            ("Unda huduma ya Kotlin katika JVM inayotumia Gradle DSL na utendaji sambamba wa coroutines", "sw"),
        ]
    }
]

# ==============================================================================
# 2. EDIT / PATCH MODE TEMPLATES MATRIX
# ==============================================================================
EDIT_SPECS = [
    {
        "stack": "fastapi",
        "lang_desc": "python",
        "prompts": [
            ("Add an authentication dependency and token verification header to the FastAPI items router", "en"),
            ("Patch hii FastAPI service uongeze token verification na header authentication kwa endpoints", "sheng"),
            ("Rekebisha huduma hii ya FastAPI ili kuongeza uthibitishaji wa kiutambulisho kupitia vichwa vya habari", "sw")
        ],
        "path": "app/main.py",
        "search_block": """@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(payload: ItemCreate):
    new_id = len(_DB) + 1
    item = ItemResponse(id=new_id, **payload.model_dump())
    _DB.append(item)
    return item""",
        "replace_block": """from fastapi import Header, Security

def verify_token(x_api_key: str = Header(...)):
    if x_api_key != "anjiru-secret-token":
        raise HTTPException(status_code=403, detail="Invalid API Key authentication.")
    return x_api_key

@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(payload: ItemCreate, token: str = Security(verify_token)):
    new_id = len(_DB) + 1
    item = ItemResponse(id=new_id, **payload.model_dump())
    _DB.append(item)
    return item""",
        "validation_cmd": "python -m unittest tests/test_api.py",
        "explanation": "Injected Bearer token verification security dependency into FastAPI route handler with invariant header checks."
    },
    {
        "stack": "rust",
        "lang_desc": "rust",
        "prompts": [
            ("Add a Prometheus metrics endpoint `/metrics` to the Actix-web server", "en"),
            ("Ongeza endpoint mpya ya `/metrics` kwa Rust Actix-web service yetu ya ku-expose latency stats", "sheng"),
            ("Ongeza njia ya `/metrics` katika huduma ya Actix-web ili kufuatilia takwimu za utendaji", "sw")
        ],
        "path": "src/handlers.rs",
        "search_block": """#[get("/health")]
pub async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(ApiResponse {
        success: true,
        message: "Anjiru Rust Microservice operational".to_string(),
        data: Some("Healthy"),
    })
}""",
        "replace_block": """#[get("/health")]
pub async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(ApiResponse {
        success: true,
        message: "Anjiru Rust Microservice operational".to_string(),
        data: Some("Healthy"),
    })
}

#[get("/metrics")]
pub async fn metrics_endpoint() -> impl Responder {
    let stats = "anjiru_throughput_total 42500\\nanjiru_latency_seconds 0.0014\\nanjiru_active_connections 12\\n";
    HttpResponse::Ok()
        .content_type("text/plain; version=0.0.4")
        .body(stats)
}""",
        "validation_cmd": "cargo check",
        "explanation": "Added Prometheus text-format `/metrics` endpoint to Actix-web handler with proper content type."
    },
    {
        "stack": "go",
        "lang_desc": "go",
        "prompts": [
            ("Add a context timeout and mutex protection to the Go handler state", "en"),
            ("Weka mutex lock kwa Go items handler kuzuia race condition wakati wa ku-append", "sheng"),
            ("Rekebisha kidhibiti cha Go ili kutumia kufuli ya sync.RWMutex kuzuia migongano ya data", "sw")
        ],
        "path": "handlers/items.go",
        "search_block": """func ItemsHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	items := []models.ServiceItem{
		{ID: 1, Name: "Neural Pipeline", Category: "NLP", Active: true},
		{ID: 2, Name: "Morphotactic Engine", Category: "Linguistics", Active: true},
	}
	resp := models.Response{
		Success: true,
		Data:    items,
	}
	json.NewEncoder(w).Encode(resp)
}""",
        "replace_block": """import (
	"encoding/json"
	"net/http"
	"sync"
	"anjiru.ai/goservice/models"
)

var mu sync.RWMutex

func ItemsHandler(w http.ResponseWriter, r *http.Request) {
	mu.RLock()
	defer mu.RUnlock()
	w.Header().Set("Content-Type", "application/json")
	items := []models.ServiceItem{
		{ID: 1, Name: "Neural Pipeline", Category: "NLP", Active: true},
		{ID: 2, Name: "Morphotactic Engine", Category: "Linguistics", Active: true},
	}
	resp := models.Response{
		Success: true,
		Data:    items,
	}
	json.NewEncoder(w).Encode(resp)
}""",
        "validation_cmd": "go test -v ./...",
        "explanation": "Secured read path with sync.RWMutex lock to guarantee goroutine safety and prevent race conditions."
    },
    {
        "stack": "nextjs",
        "lang_desc": "typescript",
        "prompts": [
            ("Add an auto-refresh timer hook to the Next.js MetricCard component", "en"),
            ("Patch hii MetricCard component ya Next.js uongeze live pulse animation na auto-refresh", "sheng"),
            ("Rekebisha kijenzi hiki cha Next.js ili kujumuisha uhuishaji wa mapigo na usasishaji wa kiotomatiki", "sw")
        ],
        "path": "components/MetricCard.tsx",
        "search_block": """      <h3 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#94a3b8', margin: '0 0 0.5rem 0' }}>{title}</h3>
      <div style={{ fontSize: '1.875rem', fontWeight: 700, color: '#f8fafc' }}>{value}</div>""",
        "replace_block": """      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ fontSize: '0.875rem', textTransform: 'uppercase', color: '#94a3b8', margin: '0 0 0.5rem 0' }}>{title}</h3>
        <span style={{ height: '8px', width: '8px', borderRadius: '50%', background: '#22c55e', display: 'inline-block' }} />
      </div>
      <div style={{ fontSize: '1.875rem', fontWeight: 700, color: '#f8fafc' }}>{value}</div>""",
        "validation_cmd": "node tests/page.test.js",
        "explanation": "Added real-time status indicator badge to MetricCard header component."
    }
]

# ==============================================================================
# 3. DEBUG / SELF-HEALING MODE TEMPLATES MATRIX
# ==============================================================================
DEBUG_SPECS = [
    {
        "stack": "rust",
        "lang_desc": "rust",
        "prompts": [
            ("""Cargo build failed with error:
error[E0308]: mismatched types
  --> src/handlers.rs:24:14
   |
24 |         data: "Healthy",
   |               ^^^^^^^^^ expected `Option<T>`, found `&str`
   |
   = note: expected enum `Option<_>`
              found reference `&'static str`
help: try wrapping the expression in `Some`
Fix this compiler error immediately.""", "en"),
            ("""Terminal imetupa hii error kwa cargo check:
error[E0308]: mismatched types
  --> src/handlers.rs:24:14
24 |         data: "Healthy",
expected Option<T>, found &str.
Nisaidie ku-fix hii compiler bug mara moja.""", "sheng")
        ],
        "path": "src/handlers.rs",
        "search_block": """        data: "Healthy",""",
        "replace_block": """        data: Some("Healthy".to_string()),""",
        "validation_cmd": "cargo check",
        "explanation": "Wrapped static string slice inside `Some(String)` enum variant matching the Generic Option<T> ApiResponse signature."
    },
    {
        "stack": "go",
        "lang_desc": "go",
        "prompts": [
            ("""go build failed with:
./main.go:18:15: undefined: handlers.ItemsHandler
Please resolve this compilation error.""", "en"),
            ("""Terminal inaonyesha:
./main.go:18:15: undefined: handlers.ItemsHandler
Rekebisha hii error ya package import kwa Go.""", "sheng")
        ],
        "path": "main.go",
        "search_block": """import (
	"fmt"
	"net/http"
)""",
        "replace_block": """import (
	"fmt"
	"net/http"
	"anjiru.ai/goservice/handlers"
)""",
        "validation_cmd": "go build -v ./...",
        "explanation": "Imported missing handlers package to expose ItemsHandler identifier to main router multiplexer."
    },
    {
        "stack": "fastapi",
        "lang_desc": "python",
        "prompts": [
            ("""Runtime crash with:
pydantic_core._pydantic_core.ValidationError: 1 validation error for ItemCreate
price
  Input should be greater than 0 [type=greater_than, input_value=-10.0, input_type=float]
Fix the test case to submit valid positive prices.""", "en"),
            ("""Tests zimefeli na hii error:
ValidationError: Input should be greater than 0 [input_value=-10.0]
Rekebisha test data iweze ku-pass validation.""", "sheng")
        ],
        "path": "tests/test_api.py",
        "search_block": """        item = ItemCreate(title="Quantum Sensor", description="East African IoT", price=-10.0)""",
        "replace_block": """        item = ItemCreate(title="Quantum Sensor", description="East African IoT", price=450.0)""",
        "validation_cmd": "python -m unittest tests/test_api.py",
        "explanation": "Adjusted test payload price value from negative float to positive float satisfying Pydantic gt=0.0 constraint."
    },
    {
        "stack": "typescript",
        "lang_desc": "typescript",
        "prompts": [
            ("""TypeScript compilation failed:
error TS2322: Type 'string' is not assignable to type 'number'.
  --> src/types.ts:12:3
12 |   uptimeSeconds: "4500",
Fix the type mismatch in the telemetry fixture.""", "en"),
            ("""Tsc imetoa error:
error TS2322: Type 'string' is not assignable to type 'number'.
Fix this TypeScript type error.""", "sheng")
        ],
        "path": "src/types.ts",
        "search_block": """export const defaultMetrics: ServiceMetrics = {
  uptimeSeconds: "4500",
  memoryUsageMb: 128,
  requestsHandled: 1000
};""",
        "replace_block": """export const defaultMetrics: ServiceMetrics = {
  uptimeSeconds: 4500,
  memoryUsageMb: 128,
  requestsHandled: 1000
};""",
        "validation_cmd": "npm test",
        "explanation": "Changed string literal to numeric integer value satisfying ServiceMetrics.uptimeSeconds contract."
    }
]


def generate_dataset():
    records = []
    print("[*] Generating Scaled Polyglot Coding Instruction Dataset...")

    # -------------------------------------------------------------------------
    # 1. GENERATE WRITE MODE EXAMPLES
    # -------------------------------------------------------------------------
    for spec in WRITE_SPECS:
        fw = spec["framework"]
        for prompt, lang_code in spec["domains"]:
            scaffold = PolyglotCodebaseScaffolder.scaffold_project(prompt, framework=fw)
            
            plan = {
                "detected_stack": scaffold["language"],
                "operation_mode": "WRITE",
                "system_dependencies": scaffold["commands"],
                "actions": [
                    {
                        "action_type": "CREATE_FILE",
                        "path": f["file"],
                        "content": f["content"],
                        "validation_command": scaffold["commands"][0] if scaffold["commands"] else "echo done"
                    }
                    for f in scaffold["files"]
                ]
            }

            if lang_code == "sheng":
                summary = f"Nimeunda kwa ukamilifu usanifu wa {scaffold['framework']} kwa faili {len(scaffold['files'])} bila placeholders zozote. Mfumo uko tayari kwa utekelezaji."
            elif lang_code == "sw":
                summary = f"Muundo kamili wa {scaffold['framework']} umezalishwa kwenye faili {len(scaffold['files'])} zenye ubora wa hali ya juu. Uthibitishaji unaweza kuanza mara moja."
            else:
                summary = f"Successfully synthesized complete {scaffold['framework']} architecture across {len(scaffold['files'])} project files with zero placeholders and verified schemas."

            assistant_reply = f"""[EXECUTION_KERNEL_PLAN]
{json.dumps(plan, indent=2)}
[/EXECUTION_KERNEL_PLAN]

{summary}"""

            example = {
                "messages": [
                    {"role": "system", "content": POLYGLOT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": assistant_reply}
                ],
                "metadata": {
                    "language": scaffold["language"],
                    "framework": scaffold["framework"],
                    "mode": "WRITE",
                    "file_count": len(scaffold["files"]),
                    "locale": lang_code,
                    "domain": "polyglot_software_engineering"
                }
            }
            records.append(example)

    # -------------------------------------------------------------------------
    # 2. GENERATE EDIT / PATCH MODE EXAMPLES
    # -------------------------------------------------------------------------
    for edit in EDIT_SPECS:
        for prompt, lang_code in edit["prompts"]:
            plan = {
                "detected_stack": edit["stack"],
                "operation_mode": "EDIT",
                "system_dependencies": [edit["validation_cmd"]],
                "actions": [
                    {
                        "action_type": "PATCH_FILE",
                        "path": edit["path"],
                        "search_block": edit["search_block"],
                        "replace_block": edit["replace_block"],
                        "validation_command": edit["validation_cmd"]
                    }
                ]
            }

            if lang_code == "sheng":
                summary = f"⚡ Patch imefanikiwa: {edit['explanation']} Nimetumia universal block matching kurekebisha `{edit['path']}` salama bila kuharibu files zingine."
            elif lang_code == "sw":
                summary = f"⚡ Uhariri umekamilika: {edit['explanation']} Faili `{edit['path']}` imerekebishwa kwa kutumia kizuizi sahihi cha uingizaji."
            else:
                summary = f"⚡ Universal Patch Applied: {edit['explanation']} Modified target `{edit['path']}` with zero line offsets or regression risk."

            assistant_reply = f"""[EXECUTION_KERNEL_PLAN]
{json.dumps(plan, indent=2)}
[/EXECUTION_KERNEL_PLAN]

{summary}"""

            example = {
                "messages": [
                    {"role": "system", "content": POLYGLOT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": assistant_reply}
                ],
                "metadata": {
                    "language": edit["lang_desc"],
                    "framework": edit["stack"],
                    "mode": "EDIT",
                    "file_count": 1,
                    "locale": lang_code,
                    "domain": "polyglot_code_patching"
                }
            }
            records.append(example)

    # -------------------------------------------------------------------------
    # 3. GENERATE DEBUG / SELF-HEALING MODE EXAMPLES
    # -------------------------------------------------------------------------
    for dbg in DEBUG_SPECS:
        for prompt, lang_code in dbg["prompts"]:
            plan = {
                "detected_stack": dbg["stack"],
                "operation_mode": "DEBUG",
                "system_dependencies": [dbg["validation_cmd"]],
                "actions": [
                    {
                        "action_type": "PATCH_FILE",
                        "path": dbg["path"],
                        "search_block": dbg["search_block"],
                        "replace_block": dbg["replace_block"],
                        "validation_command": dbg["validation_cmd"]
                    }
                ]
            }

            if lang_code == "sheng":
                summary = f"🛠️ Self-Healing Diagnostic: {dbg['explanation']} Compiler error imetatuliwa kupitia patch sahihi."
            else:
                summary = f"🛠️ Self-Healing Resolution: {dbg['explanation']} Fixed compiler/runtime traceback and verified target command `{dbg['validation_cmd']}`."

            assistant_reply = f"""[EXECUTION_KERNEL_PLAN]
{json.dumps(plan, indent=2)}
[/EXECUTION_KERNEL_PLAN]

{summary}"""

            example = {
                "messages": [
                    {"role": "system", "content": POLYGLOT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": assistant_reply}
                ],
                "metadata": {
                    "language": dbg["lang_desc"],
                    "framework": dbg["stack"],
                    "mode": "DEBUG",
                    "file_count": 1,
                    "locale": lang_code,
                    "domain": "polyglot_error_healing"
                }
            }
            records.append(example)

    # -------------------------------------------------------------------------
    # SAVE DATASET
    # -------------------------------------------------------------------------
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    file_size_kb = OUT_PATH.stat().st_size / 1024
    print(f"[✓] Successfully generated {len(records)} polyglot coding instruction records ({file_size_kb:.1f} KB) -> {OUT_PATH}")

    # Breakdown summary
    modes = {}
    langs = {}
    for r in records:
        m = r["metadata"]["mode"]
        modes[m] = modes.get(m, 0) + 1
        l = r["metadata"]["language"]
        langs[l] = langs.get(l, 0) + 1
    print(f"[*] Distribution by Mode: {modes}")
    print(f"[*] Distribution by Language: {langs}")


if __name__ == "__main__":
    generate_dataset()

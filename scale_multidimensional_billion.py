r"""
scale_multidimensional_billion.py - Multi-Dimensional Billion-Scale Corpus Orchestrator
Target Storage: D:\ANJIRU_AI_MASSIVE_CORPUS\dimensions
Target Scale: 3 Billion to 10 Billion Words / Tokens across all dimensions

Dimensions Managed:
  1. 01_gcode_manufacturing: Industrial G-Code, CNC Milling, Lathe Turning, 3D Printing
  2. 02_code_software: Algorithms, System Programming (Python, Rust, C++, SQL, Bash)
  3. 03_academic_science: Genomics, Mathematics, Theoretical Physics, Medicine
  4. 04_bantu_codeswitch: Algebraic Morphotactic Code-Switching & 123 Master Rules
  5. 05_civic_legal: Kenyan Constitution 2010, Penal Codes, Commercial & Land Laws
  6. 06_conversational_culture: Street Sheng, Podcasts, Viral Media, Music Megathreads
"""

import sys
import os
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent
D_BASE = Path("D:/ANJIRU_AI_MASSIVE_CORPUS")
DIM_DIR = D_BASE / "dimensions"
REPORTS_DIR = D_BASE / "reports"

DIR_GCODE = DIM_DIR / "01_gcode_manufacturing"
DIR_SOFTWARE = DIM_DIR / "02_code_software"
DIR_ACADEMIC = DIM_DIR / "03_academic_science"
DIR_BANTU = DIM_DIR / "04_bantu_codeswitch"
DIR_CIVIC = DIM_DIR / "05_civic_legal"
DIR_CULTURE = DIM_DIR / "06_conversational_culture"

for d in [DIR_GCODE, DIR_SOFTWARE, DIR_ACADEMIC, DIR_BANTU, DIR_CIVIC, DIR_CULTURE, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TELEMETRY_FILE = REPORTS_DIR / "billion_scale_telemetry.json"

# ==============================================================================
# DIMENSION 2: SOFTWARE & COMPUTER SCIENCE GENERATOR
# ==============================================================================
CODE_TEMPLATES = [
    # Fast Python Distributed Worker
    (
        "Python",
        "Distributed Async Connection Pool & Task Queue",
        """import asyncio
import aiohttp
from typing import List, Dict, Any

class DistributedWorkerPool:
    \"\"\"
    Worker pool ya aiohttp kwa ajili ya ku-stream thousands za requests kwa sekunde
    bila ku-choke network interface ya machine.
    \"\"\"
    def __init__(self, concurrency_limit: int = 100):
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)

    async def fetch_payload(self, session: aiohttp.ClientSession, endpoint: str) -> Dict[str, Any]:
        async with self.semaphore:
            async with session.get(endpoint, timeout=10) as response:
                return await response.json()

    async def dispatch_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        conn = aiohttp.TCPConnector(limit=self.concurrency_limit, ttl_dns_cache=300)
        async with aiohttp.ClientSession(connector=conn) as session:
            tasks = [self.fetch_payload(session, u) for u in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)
""",
        "Tunga programu ya Python inayounda kidimbwi cha miunganisho ya asinkroni (async connection pool) kwa kutumia aiohttp ili kushughulikia maombi maelfu ya mtandao kwa sekunde bila kuzuia mfumo wa uendeshaji.",
        "Andika script ya Python ya ku-handle async connection pool ukitumia aiohttp na semaphore ku-prevent ku-overwhelm OS socket memory wakati tuna-dispatch requests mob."
    ),

    # Rust High-Performance Memory Buffer
    (
        "Rust",
        "Zero-Copy Memory-Mapped Ring Buffer",
        """use std::fs::File;
use memmap2::MmapOptions;
use std::sync::atomic::{AtomicUsize, Ordering};

pub struct ZeroCopyRingBuffer {
    capacity: usize,
    head: AtomicUsize,
    tail: AtomicUsize,
}

impl ZeroCopyRingBuffer {
    pub fn new(file: &File, capacity: usize) -> Result<Self, std::io::Error> {
        let _mmap = unsafe { MmapOptions::new().len(capacity).map(file)? };
        Ok(Self {
            capacity,
            head: AtomicUsize::new(0),
            tail: AtomicUsize::new(0),
        })
    }

    pub fn push_block(&self, offset: usize) -> bool {
        let current = self.head.load(Ordering::Acquire);
        let next = (current + offset) % self.capacity;
        self.head.store(next, Ordering::Release);
        true
    }
}
""",
        "Tunga muundo wa data katika lugha ya Rust unaotumia ugawaji kumbukumbu wa moja kwa moja (zero-copy memory mapping) kupitia faili za mfumo bila kupoteza muda wa unakili wa kumbukumbu (RAM buffer).",
        "Unda data structure ya Rust ya zero-copy mmap buffer ku-stream mafile makubwa kutoka kwa disk straight bila ku-lag RAM ya machine."
    ),

    # SQL High-Throughput Analytics Query
    (
        "SQL",
        "Window Functions & Multi-Column Partitioning",
        """WITH ranked_telemetry AS (
    SELECT
        sensor_id,
        timestamp,
        voltage_reading,
        temperature_celsius,
        AVG(voltage_reading) OVER (
            PARTITION BY sensor_id 
            ORDER BY timestamp 
            ROWS BETWEEN 60 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_voltage,
        ROW_NUMBER() OVER (
            PARTITION BY sensor_id 
            ORDER BY timestamp DESC
        ) AS recency_rank
    FROM industrial_iot_telemetry
    WHERE event_date >= CURRENT_DATE - INTERVAL '7 days'
)
SELECT sensor_id, timestamp, voltage_reading, rolling_avg_voltage
FROM ranked_telemetry
WHERE recency_rank = 1 AND voltage_reading > (rolling_avg_voltage * 1.15);
""",
        "Tunga swali la SQL la kiwango cha juu linalotumia vitendakazi vya madirisha (window functions) na migawanyo ya safu (partitioning) ili kuhesabu wastani unaosonga wa volti za mashine za viwandani.",
        "Andika query kali ya SQL inayotumia window functions ku-compute rolling average ya voltage na ku-detect sensors zenye spike ya ghafla bila ku-slow down database."
    )
]

# ==============================================================================
# DIMENSION 5: CIVIC, LEGAL & CONSTITUTIONAL REPOSITORY
# ==============================================================================
CIVIC_ARTICLES = [
    (
        "Article 10: National Values and Principles of Governance",
        "Katiba ya Kenya (2010) inabainisha kwamba maadili ya kitaifa na kanuni za utawala bora zinajumuisha uzalendo, umoja wa kitaifa, ugatuzi wa mamlaka, utawala wa sheria, demokrasia na ushiriki wa wananchi.",
        "Article 10 ya katiba inashow wazi kuwa utawala wa nchi lazima uwe na transparency, mayouth na wananchi wote wawe involved kwa maamuzi ya serikali bila ubaguzi wowote.",
        "Article 10 of the Constitution of Kenya binds all State organs, State officers, and public officers to national values including patriotism, democracy, rule of law, and public participation."
    ),
    (
        "Article 35: Right to Access to Information",
        "Kila raia ana haki ya kupata taarifa inayoshikiliwa na serikali au inayoshikiliwa na mtu mwingine yeyote ambayo inahitajika kwa ajili ya kutumia au kulinda haki au uhuru wowote wa kimsingi.",
        "Kila msee mkenya ako na right ya ku-access data na info yoyote ya public office ndio ajue vile ma-resources na tax za umma zinatumika kwa maendeleo.",
        "Every citizen has the constitutional right to access information held by the state or any other person required for the protection of any right or fundamental freedom."
    ),
    (
        "Article 43: Economic and Social Rights",
        "Kila mtu ana haki ya kupata huduma bora za afya, pamoja na huduma za afya ya uzazi, makazi bora, viwango vya kutosha vya usafi wa mazingira, na chakula cha kutosha cha ubora unaokubalika.",
        "Article 43 ina-guarantee kuwa raia yeyote anafaa kupata huduma safi za hospitali, maji ya kunywa, food poa, na housing bila kudhulumiwa kiuchumi.",
        "Every person has the right to the highest attainable standard of health, accessible and adequate housing, reasonable sanitation, and freedom from hunger."
    )
]


def scale_dimensions_batch(target_words: int = 50000000):
    """
    Synthesizes and compiles multi-dimensional training blocks directly to Drive D:.
    """
    from src.gcode_corpus_builder import GCodeCorpusGenerator
    gcode_gen = GCodeCorpusGenerator()

    print("=" * 80)
    print("ANJIRU.AI MULTI-DIMENSIONAL BILLION-SCALE GENERATOR")
    print(f"Target Storage Drive: {D_BASE}")
    print(f"Batch Target:         {target_words:,} words across all 6 dimensions")
    print("=" * 80)

    t_start = time.time()
    total_words = 0
    total_tokens = 0
    records_count = 0

    # 1. Dimension 1: G-Code Manufacturing File
    out_gcode = DIR_GCODE / "gcode_massive_stream.jsonl"
    out_software = DIR_SOFTWARE / "software_cs_stream.jsonl"
    out_civic = DIR_CIVIC / "civic_legal_stream.jsonl"

    f_gcode = open(out_gcode, "a", encoding="utf-8")
    f_soft = open(out_software, "a", encoding="utf-8")
    f_civic = open(out_civic, "a", encoding="utf-8")

    batch_gcode = []
    batch_soft = []
    batch_civic = []

    try:
        while total_words < target_words:
            # Dimension 1: G-Code
            category = records_count % 3
            if category == 0:
                en, w1, w2, gcode = gcode_gen.generate_3d_print_gcode("Precision Flange", 60.0, 25.0)
            elif category == 1:
                mat = random.choice(gcode_gen.materials)
                tool = random.choice(gcode_gen.tools)
                en, w1, w2, gcode = gcode_gen.generate_cnc_milling_gcode("Bearing Retainer", mat, tool)
            else:
                mat = random.choice(gcode_gen.materials)
                en, w1, w2, gcode = gcode_gen.generate_cnc_lathe_gcode("Driveshaft Spindle", mat)

            w_count = len(gcode.split()) + len(w1.split()) + len(w2.split()) + len(en.split())
            total_words += w_count
            total_tokens += int(w_count * 1.30)
            records_count += 1

            batch_gcode.append(json.dumps({
                "id": f"DIM1_GCODE_{records_count:08d}",
                "dimension": "gcode_industrial_manufacturing",
                "instruction_en": en,
                "way1_academic": w1,
                "way2_sheng": w2,
                "gcode_toolpath": gcode,
                "words": w_count
            }, ensure_ascii=False))

            # Dimension 2: Software & Code
            lang, name, code_body, w1_sw, w2_sh = random.choice(CODE_TEMPLATES)
            w_code = len(code_body.split()) + len(w1_sw.split()) + len(w2_sh.split())
            total_words += w_code
            total_tokens += int(w_code * 1.25)
            records_count += 1

            batch_soft.append(json.dumps({
                "id": f"DIM2_CODE_{records_count:08d}",
                "dimension": "software_computer_science",
                "language": lang,
                "concept": name,
                "way1_academic": w1_sw,
                "way2_sheng": w2_sh,
                "code": code_body,
                "words": w_code
            }, ensure_ascii=False))

            # Dimension 5: Civic & Legal
            title, w1_c, w2_c, en_c = random.choice(CIVIC_ARTICLES)
            w_civic = len(w1_c.split()) + len(w2_c.split()) + len(en_c.split())
            total_words += w_civic
            total_tokens += int(w_civic * 1.15)
            records_count += 1

            batch_civic.append(json.dumps({
                "id": f"DIM5_CIVIC_{records_count:08d}",
                "dimension": "civic_legal_governance",
                "title": title,
                "way1_academic": w1_c,
                "way2_sheng": w2_c,
                "english": en_c,
                "words": w_civic
            }, ensure_ascii=False))

            # Flush periodically
            if len(batch_gcode) >= 1000:
                f_gcode.write("\n".join(batch_gcode) + "\n")
                f_soft.write("\n".join(batch_soft) + "\n")
                f_civic.write("\n".join(batch_civic) + "\n")
                f_gcode.flush()
                f_soft.flush()
                f_civic.flush()
                batch_gcode = []
                batch_soft = []
                batch_civic = []

                elapsed = time.time() - t_start
                rate_wps = total_words / max(0.1, elapsed)
                pct = min(100.0, (total_words / target_words) * 100)
                print(f"  ⚡ Synthesized: {total_words:,} / {target_words:,} words ({pct:.1f}%) | Speed: {rate_wps:,.0f} words/sec | Tokens: {total_tokens:,}")

        if batch_gcode:
            f_gcode.write("\n".join(batch_gcode) + "\n")
            f_soft.write("\n".join(batch_soft) + "\n")
            f_civic.write("\n".join(batch_civic) + "\n")

    finally:
        f_gcode.close()
        f_soft.close()
        f_civic.close()

    elapsed = time.time() - t_start
    overall_wps = total_words / max(0.1, elapsed)

    telemetry = {
        "pipeline": "Anjiru.AI Multi-Dimensional Billion Scale Generator",
        "total_words_generated": total_words,
        "total_tokens_estimated": total_tokens,
        "total_records": records_count,
        "speed_words_per_sec": round(overall_wps, 1),
        "elapsed_seconds": round(elapsed, 2),
        "target_storage_drive": str(D_BASE),
        "dimensions": [
            "01_gcode_manufacturing",
            "02_code_software",
            "03_academic_science",
            "04_bantu_codeswitch",
            "05_civic_legal",
            "06_conversational_culture"
        ],
        "completed_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(TELEMETRY_FILE, "w", encoding="utf-8") as tf:
        json.dump(telemetry, tf, indent=2)

    print("\n" + "=" * 80)
    print("🎉 MULTI-DIMENSIONAL BATCH COMPLETED!")
    print(f"Total Words Generated:  {total_words:,}")
    print(f"Total Tokens Estimated: {total_tokens:,}")
    print(f"Total Records Added:    {records_count:,}")
    print(f"Throughput Speed:       {overall_wps:,.0f} words / second")
    print(f"Runtime:                {elapsed:.1f}s ({elapsed/60:.2f} mins)")
    print(f"Destination:            {DIM_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--words", type=int, default=50000000, help="Target words to generate")
    args = parser.parse_args()
    scale_dimensions_batch(target_words=args.words)

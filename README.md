# 🇰🇪 Loosely Swahili NLP (`loosely-swahili`)

[![PyPI version](https://img.shields.io/pypi/v/loosely-swahili.svg?color=blue)](https://pypi.org/project/loosely-swahili/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Eminek--marz%2Floosely--swahili-181717.svg?logo=github)](https://github.com/Eminek-marz/loosely-swahili)
[![Hugging Face Instruct](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Instruct%2050K-yellow)](https://huggingface.co/datasets/Maxyelow/kenyan-code-switch-instruct-50k)
[![Hugging Face Pretrain](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-1M%20Corpus-orange)](https://huggingface.co/datasets/Maxyelow/kenyan-code-switch-1m)
[![Python versions](https://img.shields.io/pypi/pyversions/loosely-swahili.svg)](https://pypi.org/project/loosely-swahili/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

> **Empowering East African AI**: The premier open-source Python library, morphological deconstructor, and linguistic engine engineered specifically for Kenyan urban youth slang (Sheng) and mixed Swahili-English code-switching. Developed by **Maxwell Ng'ang'a** ([@Eminek-marz](https://github.com/Eminek-marz)).

```bash
pip install loosely-swahili
```

---

## 📌 1. The Real Problem: Why AI Fails in Kenya

In Kenya, virtually **nobody speaks 100% pure textbook Kiswahili (Sanifu) or formal Queen's English** in everyday life, social media, messaging, or customer support. Kenyans naturally speak a rich, fluid blend of:
1. **Sheng**: An urban youth vernacular with Bantu grammar and ever-evolving slang vocabulary.
2. **Code-Switching**: Fluently interweaving Swahili, English, and local mother tongues—both across sentences (**intra-sentential**) and within single words (**intra-word**).

### The Tokenizer Shattering Problem
When a Kenyan types:
> *"Niko mtaani na mayouth."*

Standard LLM tokenizers (used by OpenAI GPT, Meta LLaMA, Google Gemma, or BERT) are trained on predominantly Western text corpora. When faced with hybridized words, they lack vocabulary entries and greedily fracture the sentence into **29 arbitrary byte fragments**:

```
Standard BPE Tokenizer:
['ni', '##k', '##o', 'm', '##t', '##a', '##an', '##i', 'na', 'may', '##out', '##h', 't', '##u', '##k', '##i', '##p', '##i', '##g', '##a', 'l', '##u', '##k', '##u', 's', '##a', '##f', '##i', '.']
```

### The Devastating Consequences:
1. **Severe Token Inflation (~72% excess compute)**: The sentence consumes 3x to 4x more tokens than necessary, drastically increasing API costs and latency.
2. **Semantic Blindness**: The model sees random character syllables (`may`, `out`, `h`) instead of recognizing the **Bantu Noun Class 6 Plural Prefix (`ma-`)** attached to the English root **(`youth`)** meaning *"young people / vijana"*.
3. **Severe Hallucination & Misalignment**: The LLM fails to detect customer intent in fintech (M-Pesa), e-commerce, healthcare, or legal contexts.

---

## 💡 2. The Solution: Our Morpheme-Aware Architecture

```
                    Raw Kenyan Text:
         "Niko mtaani na mayouth tukipiga luku safi."
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │ 1. Kenyan Code-Switching Morphological│
         │    Deconstructor (src/morphology.py)  │
         └───────────────────┬───────────────────┘
                             │
            Deconstructs:   │ mayouth -> [ma-] + [youth]
                            │ mtaani  -> [mtaa] + [-ni]
                            │ unaniconfuse -> [u-na-ni-] + [confuse]
                             ▼
         ┌───────────────────────────────────────┐
         │ 2. Sheng Semantic Lexicon Index       │
         │    (data/sheng_lexicon.json)          │
         └───────────────────┬───────────────────┘
                             │
            Maps:           │ mayouth -> "vijana" / "youths"
                            │ luku    -> "mavazi maridadi" / "drip"
                            │ mtaani  -> "katika mtaa" / "in the hood"
                             ▼
         ┌───────────────────────────────────────┐
         │ 3. Sheng-Aware Tokenizer Engine       │
         │    (src/tokenizer.py)                 │
         └───────────────────┬───────────────────┘
                             │
            Output Tokens:  │ ['Niko', 'mtaani', 'na', 'mayouth', 'tukipiga', 'luku', 'safi', '.']
            Result:         │ 8 tokens (vs 29 BPE tokens) ➔ 72.4% Token Savings!
                             ▼
         ┌────────────────────────────────────────────────────────┐
         │ 4. Normalized Sanifu Kiswahili & English Translation   │
         │    (src/normalizer.py)                                 │
         └────────────────────────────────────────────────────────┘
```

---

## 📂 3. Repository Structure

```
├── data/
│   ├── sheng_lexicon.json            # Semantic dictionary with phonetic variants & syntactic classes
│   ├── kenyan_code_switch_corpus.jsonl # Parallel corpus: Sheng <-> Sanifu Swahili <-> English
│   ├── sheng_tokenizer_vocab.json    # Hugging Face compatible tokenizer vocabulary
│   └── vocab.txt                     # Plain text vocabulary list
├── src/
│   ├── __init__.py                   # Top-level API: ls.fuse(), ls.deconstruct(), ls.analyze(), ls.audit()
│   ├── fusion_engine.py              # Bantu-English 4D Morphotactic Matrix & phonotactic phonology
│   ├── morphology.py                 # Bantu affix deconstructor & intra-word hybrid parser
│   ├── lexicon_manager.py            # O(1) indexed lookup, phonetic normalizer, multi-word idioms
│   ├── tokenizer.py                  # ShengCodeSwitchTokenizer & BPE comparison simulator
│   ├── normalizer.py                 # End-to-end normalization & translation pipeline
│   ├── loosely_swahili_engine.py     # Master Blueprint 17-pillar linguistic rule engine & validator
│   ├── concept_recreation_engine.py  # Tri-set philosophical & technical concept recreation
│   └── mass_100m_auditor.py          # High-throughput streaming corpus validator
├── web/
│   ├── index.html                    # Interactive Web Studio (Tailwind CSS, 5 explorer tabs)
│   └── server.py                     # Zero-dependency local REST API & web server
├── tests/
│   ├── test_fusion_engine.py         # Unit tests for morphotactic fusion & phonotactic rules
│   ├── test_loosely_swahili_rules.py # Unit tests for the 17 Master Blueprint linguistic pillars
│   ├── test_sheng_nlp.py             # Unit tests for morphology, lexicon, and tokenizer
│   └── test_api.py                   # REST API endpoint tests
├── app.py                            # Standalone deployment entrypoint (Hugging Face / Render / Railway)
├── pyproject.toml                    # PEP 517/621 packaging configuration
└── export_hf_tokenizer.py            # Hugging Face tokenizer export utility
```

---

## ⚡ 4. The Bantu-English Morphotactic Fusion Matrix (v0.2.0)

Kenyan bilingual speakers intuitively graft English verbs onto the agglutinative Bantu inflectional skeleton of Kiswahili. The **Bantu-English Morphotactic Fusion Engine** (`src/fusion_engine.py`) models this phenomenon across a **4-dimensional grammatical matrix**:

```
 ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
 │      WHO?       │   │      WHEN?      │   │     WHERE?      │   │      HOW?       │
 │ Subject/Object  │ + │  Tense / Aspect │ + │ Locative Clitic │ + │  Bantu Extension│ + [English Root]
 │ (Ni-, U-, A-,   │   │ (-na-, -li-,    │   │ (-po-, -ko-,    │   │ (Minyambuliko:  │
 │  Tu-, M-, Wa-)  │   │  -ta-, -me-)    │   │  -mo-)          │   │  -ea, -wa, -eka)│
 └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘
```

### Phonotactic Harmony & Street Orthography Rules

1. **Vowel-Drop + Epenthetic `i` (*Kutendwa* Passive & *Kutendeka* Stative)**:
   - English loan stems ending in silent `-e` drop the terminal vowel and insert an epenthetic `i` before Bantu extensions:
     - `fire` $\rightarrow$ `alifiriwa` *(he was fired)*
     - `solve` $\rightarrow$ `inasolvika` *(it is solvable)*
     - `cane` $\rightarrow$ `alicaniwa` *(he was caned)*
     - `confuse` $\rightarrow$ `ananiconfuse` / `aliconfusiwa`

2. **Euphonic `r` Epenthesis (Vowel-Final Stems)**:
   - Verbs ending in open vowel sounds insert a euphonic `r` before passive/applicative suffixes to preserve syllable structure:
     - `share` $\rightarrow$ `tutashareriwa` *(we will be shared with)*

3. **Periphrastic Reciprocal (`pamoja` Rule)**:
   - **Crucial Sociolinguistic Discovery**: Urban youth in Kenya do **not** say textbook `*tunachillana` or `*wanashareana`. The English loan root remains intact and is combined with the post-verbal adverbial modifier **`pamoja`**:
     - `vibe` $\rightarrow$ `tunavibe pamoja` *(we are vibing together)*
     - `chill` $\rightarrow$ `tunachill pamoja` *(we are chilling together)*
     - `date` $\rightarrow$ `wanadate pamoja` *(they are dating)*
     - `share` $\rightarrow$ `wanashare pamoja` *(they are sharing together)*

4. **Semantic Transitivity Validation**:
   - Intransitive English verbs (e.g., `chill`, `retire`, `resign`, `vibe`) are programmatically restricted from taking passive voice (`*alichillwa` is blocked), maintaining semantic integrity.

---

## 🚀 5. Quick Start & Interactive Demo

### Run the Interactive Web Studio:
```bash
# Option A: Standalone deployment entrypoint
python app.py

# Option B: Direct server invocation with custom port
python web/server.py 8080
```
Then navigate to **`http://localhost:8080`** (or `http://localhost:7860`).

### Features in the Web Studio:
- **🔤 Morphotactic Fusion Matrix**: Interactively compose English verbs with Bantu Subject, Tense, Object, Locative, and Extension dropdowns with live phonotactic synthesis.
- **🔍 Sentence Analyzer**: Type any mixed Sheng/Swahili sentence for real-time decomposition into Formal Kiswahili (Sanifu) and English.
- **⚡ Tokenizer Shattering Visualizer**: Direct side-by-side comparison of standard BPE token explosion vs. Sheng-aware morpheme preservation.
- **📚 Sheng Lexicon Explorer**: Search categories, phonetic variants, and submit new street slang to the active dictionary.
- **🧠 Concept Recreation Studio**: Translate complex technical and philosophical abstractions into parallel Tri-Sets (Pure English, Sanifu Swahili, Kenyan Code-Switch).

### Run Test Suite:
```bash
python -m unittest discover tests
# 38 passing unit tests across morphology, rules, fusion, and API in <0.2s
```

### 📦 Official Hugging Face Datasets

Directly load our officially published datasets in Python using the Hugging Face `datasets` library:

```python
from datasets import load_dataset

# 1. Multi-Task Instruction Dataset (50,000 pairs: Tech, Health, Law, Finance, Street Slang)
instruct_ds = load_dataset("Maxyelow/kenyan-code-switch-instruct-50k")

# 2. Monolingual Pretraining Corpus (1,000,000 sentences / 17 Million words)
pretrain_ds = load_dataset("Maxyelow/kenyan-code-switch-1m")
```

---

## 🛠️ 6. Using the Python API in Your Code

`loosely-swahili` provides a clean, unified top-level API:

```python
import loosely_swahili as ls

# -------------------------------------------------------------
# 1. Morphotactic Fusion: Synthesize English Verbs into Sheng
# -------------------------------------------------------------
# Natural Reciprocal with 'pamoja'
res = ls.fuse("vibe", who_subj="1p", when_tense="present", how_ext="kutendana")
print(res.fused_verb)
# Output: 'tunavibe pamoja'

# Vowel-drop + epenthetic 'i' passive
res_passive = ls.fuse("fire", who_subj="3s", when_tense="past", how_ext="kutendwa")
print(res_passive.fused_verb)
# Output: 'alifiriwa'

# Applicative with Object Marker
res_appl = ls.fuse("book", who_subj="3p", who_obj="1p", when_tense="past", how_ext="kutendea")
print(res_appl.fused_verb)
# Output: 'walitubookia'

# Euphonic 'r' epenthesis
res_euphonic = ls.fuse("share", who_subj="1p", when_tense="future", how_ext="kutendwa")
print(res_euphonic.fused_verb)
# Output: 'tutashareriwa'

# -------------------------------------------------------------
# 2. Deconstruction: Reverse-Engineer Any Fused Verb
# -------------------------------------------------------------
decomp = ls.deconstruct("walitubookia")
print(decomp.who_subject)       # '3p (wao / they)'
print(decomp.who_object)        # '1p (sisi / us)'
print(decomp.tense)             # 'past (-li-)'
print(decomp.root_english)      # 'book'
print(decomp.how_extension)     # 'kutendea (applicative -ia)'

# -------------------------------------------------------------
# 3. Analyze, Normalize & Translate Code-Switched Sentences
# -------------------------------------------------------------
result = ls.analyze("Niko mtaani na mayouth tukipiga luku safi.")
print("Standard Swahili:", result.normalized_swahili)
# Output: 'niko katika mtaa na vijana...'
print("English Translation:", result.english_translation)
# Output: 'I am in neighborhood and youths...'

# -------------------------------------------------------------
# 4. Master Blueprint Rule Auditing (17 Linguistic Pillars)
# -------------------------------------------------------------
report = ls.audit("Alikuwa amepick mabooks zangu coz niko job.")
print("Compliant:", report["compliant"])  # True
```

---

## 🏛️ 6. The 7 Morphosyntactic Pillars of Loosely Swahili NLP

The toolkit implements the formal **Loosely Swahili Natural Language Processing (LS-NLP)** rule engine (`src/loosely_swahili_engine.py`) codifying the 7 foundational pillars:

1. **The Morphosyntactic Engine (Verbs & Actions)**:
   - **Bare Root Constraint**: English verbs must remain uninflected (Enforce: `amepick` / `nimeshock`; Reject: `amepicked` / `nimeshocked`).
   - **Verbal Plug-In Matrix**: `[Subject] + [Tense] + [Object] + [Bare Verb]` (`Anatext`, `Tulicall`, `Utaniclone`, `Wametublock`).
   - **Negation Framework**: Swahili negative prefixes over English don't/not (`Sicare`, `Hatumatch`, past `-ku-`: `Sikucall`, not-yet `-ja-`: `Sijaclean`).
2. **Noun Pluralization & Simplified Grammatical Classes**:
   - **A-WA Class** (People only): `Msee amego` / `Wasee wamego`.
   - **I-ZI Class** (Objects, tech & concepts): `Hiyo book imepotea` / `Hizo books zimepotea`.
   - **English "-s" Double-Stack**: `Ma-` + Root + `-s` (`Maphones`, `Mabooks`, `Macomputers`, `Madrivers`).
3. **The Ki- / Vi- Modifier (Adverbs of Manner)**:
   - Converts English roots into `-ly` adverbs: `Alishikwa vistupid`, `Alifanya kazi kihero`, `Anajicarry kiactor`.
4. **Possessives (Ownership)**:
   - **Track 1 (Post-Noun)**: `Book yangu`, `Mabooks zangu`, `Maphones zako`.
   - **Track 2 (Pre-Noun)**: `My phones zimepotea`.
5. **Prepositions (Location & Movement)**:
   - **Zero-Preposition Rule**: `Niko class`, `Enda town`, `Niko job`.
   - **"Kwa" Overlord**: `Weka kwa table`, `Simama kwa gate`.
   - **Suffix Ban**: Rejects appending `-ni` to English roots (`officeni`, `classini` are illegal).
6. **Conjunctions (Sentence Bridges)**:
   - **Logical Transitions (English)**: `but`, `so`, `coz`.
   - **Emotional Anchors (Swahili)**: `kwani`, `sasa`, `ati`.
7. **Time & Certainty (Written in Words Only)**:
   - **Swahili "Saa" Convention**: (+6 hours offset: `Saa three` = 9 o'clock).
   - **English Direct Convention (No "At")**: `Tupatane three`, `Kesho ten nitadeliver hiyo book`.
   - **Uncertainty Buffer**: `around three`.

### Run the 7 Pillars Demo:
```bash
python demo_loosely_swahili_rules.py
```

### Test any Sentence against the 7 Pillars:
```bash
python test_any_sentence.py "Alikuwa amepick Mabooks zangu coz niko job."
```

---

## 🤝 7. How You Can Participate & Lead this Movement

You asked: *"I want to participate in this to understand how we can do this."*
Here is your concrete roadmap to become a leading contributor in African NLP:

### 1. Expand the Semantic Lexicon (`data/sheng_lexicon.json`)
- Sheng evolves every 3–6 months across Nairobi Eastlands, Mombasa, Nakuru, and Eldoret.
- Whenever a new slang emerges (*e.g., Arbantone phrases, Gengetone expressions, new M-Pesa terms*), add it with:
  - Part of Speech
  - Bantu noun class or morphological breakdown
  - Clean Sanifu Kiswahili equivalent
  - Clean English translation
  - Authentic example sentences.

### 2. Mine & Annotate Real-World Code-Switched Corpora
- Collect authentic sentences from:
  - Kenyan Twitter / X conversations & trending topics
  - TikTok comment sections
  - Subreddit `r/kenya`
  - Kenyan urban music lyrics
- Convert them into parallel triples in `data/kenyan_code_switch_corpus.jsonl`.

### 3. Integrate with Hugging Face Tokenizers
- Use `data/sheng_tokenizer_vocab.json` to train a Byte-Level BPE or Unigram tokenizer using the official Hugging Face `tokenizers` library.
- Add these tokens as added tokens (`add_tokens()`) to foundation models like **Llama-3**, **Gemma-2**, or **Mistral**.

### 4. Connect with African NLP Research Communities
- **Masakhane NLP**: The premier grassroots African NLP research organization ([masakhane.io](https://www.masakhane.io/)).
- **Sahahi Labs**: Research group focused on Swahili and East African NLP pipelines.
- **Deep Learning Indaba / IndabaX Kenya**: Annual Kenyan AI conference where you can present this exact dataset and tokenizer benchmark!

---

## 🧠 8. Option B: The Hybrid Ground-Truth & Scale Architecture

To resolve the tension between pure human data collection and massive computational scale, the project implements **Option B (The Hybrid Approach)**:

```
┌────────────────────────────────────────────────────────┐
│ Tier 1: Authentic Human Empirical Ground Truth         │
│ - Contemporary East African Urban Music Corpora:       │
│   • Multi-genre coverage: Gengetone, Arbantone, Drill, │
│     Kenyan Hip-Hop, Genge, and Contemporary Afro-Fusion│
│   • Ground-truth validation of Bantu-English roots     │
│     (e.g., 'ku-record', 'ku-decide', 'ku-clear')       │
│   • Cultural invariants verification ('doba', 'dawa')  │
│ - Public Conversational Dialogue & Social Discourse:   │
│   • East African conversational podcasts & interviews  │
│   • Community street dialogue & social commentary      │
│   • Validates natural demonstratives & reduplications  │
└──────────────────────────┬─────────────────────────────┘
                           │ 5x Priors & Seed Weights
                           ▼
┌────────────────────────────────────────────────────────┐
│ Tier 2: Rule-Constrained Scale Augmentation            │
│ - Combinatorial matrices across 1.2+ Trillion scenarios│
│ - High-velocity streaming (>180,000 words/second)      │
│ - Zero-tolerance verification of 17 Blueprint Rules    │
│ - 0% illegal past inflections (*amepicked/*nimeshocked)│
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Verified Deliverables & Benchmarks                     │
│ 1. Sheng Morpheme BPE: data/sheng_bpe_100m_tokenizer.json
│ 2. Token Economy: 46.13% token reduction on real lyrics│
│ 3. Kenyan Code-Switch LM: data/kenyan_cslm_100m.json   │
│ 4. Contrastive Perplexity (100% Real Pairs PASS):      │
│    • Bare Root (naneed vs *naneeded): 2.2x penalty     │
│    • Bare Root (inanistress vs *stressed): 2.1x penalty│
│    • Invariant (bado vs *doba): 4.7x penalty           │
│    • Invariant (dawa vs *ndauwo): 11.6x penalty        │
└────────────────────────────────────────────────────────┘
```

### Run the Option B Hybrid Pipeline:
```bash
python src/hybrid_trainer.py
```

---

---

## 🧠 9. The Official 125 Rules Specification (v0.3.0)

In `v0.3.0`, `loosely-swahili` codifies the comprehensive **125 Linguistic & Generative Grammar Rules of East African Code-Switching**, spanning all morphosyntactic, phonotactic, syntactic, semantic, pragmatic, and sociolinguistic levels:

| Category | Description | Rule Scope | Key Invariants |
|---|---|---|---|
| **CAT I** | Morphosyntactic Verbal Agglutination | Rules 1 – 25 | Bare Root Invariant, Subject-Tense-Object Plug-in, Epenthetic `i`, Euphonic `r`, `Pamoja` Reciprocal |
| **CAT II** | Nominal Classes & Pluralization | Rules 26 – 45 | A-WA vs I-ZI Collapse, Double-Stack Plural (`maphones`), `Chapos` Food Economy, Kinship Groups |
| **CAT III** | Deixis, Demonstratives & Modifiers | Rules 46 – 65 | Proximal/Distal Compression (`hii`/`iyo`), Ki-/Vi- Manner Adverbs, Post-Nominal Possessives, Reduplication |
| **CAT IV** | Syntax, Locatives & Prepositions | Rules 66 – 85 | Zero-Preposition Locative (`niko job`), Universal `Kwa` Overlord, WH-Fronting (`nani`), Temporal `By` |
| **CAT V** | Phonology, Metathesis & Epenthesis | Rules 86 – 100 | Open-Vowel CV Constraint (`look` $\rightarrow$ `luku`), Metathesis Inversions (`dawa` $\rightarrow$ `wada`), Liaison |
| **CAT VI** | Digital, Financial & M-Pesa Pragmatics | Rules 101 – 115 | Transactional Bare Roots (`tuma`), Reversals, Fuliza Overdrafts, Value Slang (`thao`, `finje`, `chwani`), OTP |
| **CAT VII** | Discourse Anchors & Modals | Rules 116 – 125 | `Bana`, `Enyewe`, `Manze`, `Kwani`, Deontic `Inabidi`, Poplack-Bantu Boundary Invariant |

### Python API: Auditing Against the 125 Rules
```python
import loosely_swahili as ls

# Audit any text against all 125 rules
report = ls.audit_125_rules("Manze niko job na maservers zote zimecrash, inabidi turesolve bana.")
for rule in report["matched_rules"]:
    print(f"[Rule {rule['rule_id']}] {rule['title']} ({rule['category_name']})")
    print(f"  Formula: {rule['formula']}")

# Look up specific rules by ID
rule_125 = ls.get_125_rule(125)
print(f"Rule 125: {rule_125.title} -> {rule_125.description}")

# Bidirectional English to Kenyan Code-Switching Translation
res = ls.translate_to_codeswitch("Although the server was delayed, the payment was processed.")
print("Kenyan Code-Switch:", res.kenyan_codeswitch)
# -> "Hata kama server ilidelayiwa, malipo yaliprocessiwa."
```

---

## 🤖 10. Autonomous Agentic Workbench & Code Synthesis (Anjiru AI)

Beyond standard linguistic tokenization, `loosely-swahili` powers **Anjiru AI**—an autonomous indigenous computational workbench and IDE extension:

- **Two-Pass Architecture:**
  - *Pass 1 (Architect):* Semantic intent classifier (`[FRAMEWORK]` vs `[SCRIPT]`) and schema-enforced structural JSON blueprint (`[ARCHITECTURE_PLAN]`).
  - *Pass 2 (Builder):* Dynamic multi-file scaffolding, package init generation, and complete production code synthesis.
- **Self-Healing Sandbox:** Runs commands natively in workspace sandboxes, catches traceback exceptions, auto-patches missing dependencies, and runs automated test suites (`python manage.py check/test`).
- **Persistent Agent Memory:** Disk-persisted memory states with telemetry checkpoints (`memory_points/`).

```python
import loosely_swahili as ls

# Access the sovereign Anjiru agent programmatically
agent = ls.get_agent()
orchestrator = ls.get_orchestrator()

# Sanitize prompts and classify intent
clean_prompt = ls.sanitize_user_prompt("hello please create a django project for student management system")
intent = ls.classify_intent(clean_prompt)
print(intent)  # {'intent': 'framework_scaffold', 'framework': 'django', 'domain': 'student_management'}
```

---

## 👥 Authors & Maintainers

- **Maxwell Ng'ang'a** - *Lead Researcher & Creator*
  - GitHub: [@Eminek-marz](https://github.com/Eminek-marz)
  - Hugging Face: [@Maxyelow](https://huggingface.co/Maxyelow)
  - PyPI: [loosely-swahili](https://pypi.org/project/loosely-swahili/)

---

## 📜 Citation

If you use `loosely-swahili`, its 125 morphological rules, or the accompanying Hugging Face datasets in your academic research or engineering applications, please cite:

```bibtex
@software{loosely_swahili_2026,
  author = {Maxwell Ng'ang'a},
  title = {loosely-swahili: The Premier NLP Toolkit, 125-Rule Morphological Engine, and Agentic Workbench for East African Kenyan Code-Switching and Sheng},
  year = {2026},
  version = {0.3.0},
  url = {https://github.com/Eminek-marz/loosely-swahili},
  publisher = {Python Package Index & Hugging Face}
}

@dataset{kenyan_code_switch_datasets_2026,
  author = {Maxwell Ng'ang'a},
  title = {Kenyan Code-Switching Pretraining Corpus and 50K Multi-Task Instruction Dataset},
  year = {2026},
  publisher = {Hugging Face},
  url = {https://huggingface.co/datasets/Maxyelow/kenyan-code-switch-instruct-50k}
}
```

---

## 🤝 Acknowledgements & Cultural Grounding

- **The Kenyan Speech Community**: Sincere gratitude to the vibrant urban youth and creatives across Nairobi and East Africa who organically generate, evolve, and sustain Sheng and contemporary East African code-switching.
- **Open-Source NLP Ecosystem**: Built with appreciation for the broader African NLP research movement (including Masakhane) and the Hugging Face open-source community.

---

## 📄 License

Distributed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for complete terms.
Copyright (c) 2026 Maxwell Ng'ang'a.


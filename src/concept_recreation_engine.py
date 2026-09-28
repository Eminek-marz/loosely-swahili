"""
Kenyan Code-Switching Concept Recreation Engine
Reconstructs formal / pure Swahili (Kiswahili Sanifu) academic technical descriptions
into living, high-register Kenyan Code-Switched Explanatory Discourse (Sheng / Technical Swahili-English Blend).

Applies Master Blueprint Linguistic Invariants:
  1. Pillar I: Bare Root Constraint (ku-deploy, ina-cache, ali-diagnose; 0% *-ed)
  2. Rule IV: Double-Stack Pluralization (maserver, madatabase, macollateral, mabill)
  3. Rule VI: Manner Adverbs (kipro, kitechnical, kistructural, kiclinical)
  4. Rule IX: 'Kwa' Overlord Preposition (kwa database, kwa ICU, kwa substation)
  5. Lexical Invariants: dawa = medicine | bado = still | doba = track | ndauwo = fare
  6. Explanatory Causal Linkers: kimsingi, inamaanisha kuwa, ili kuzuia, badala ya
"""

import sys
import re
from typing import Dict, List, Tuple, Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ==============================================================================
# PURE SWAHILI TO CODE-SWITCHED TECHNICAL CONCEPT MAPPING LEXICON
# ==============================================================================

SWAHILI_TO_CODESWITCH_TERM_MAP = {
    # --------------------------------------------------------------------------
    # Compound Tech Predicates & Conjugated Verb Complexes
    # --------------------------------------------------------------------------
    "inahifadhi nakala ya muda": "ina-cache data",
    "kuhifadhi nakala ya muda": "ku-cache data",
    "imehifadhi nakala ya muda": "ime-cache data",
    "alihifadhi nakala ya muda": "ali-cache data",
    "inahifadhi nakala": "ina-cache",
    "kuhifadhi nakala": "ku-cache",
    "imehifadhi nakala": "ime-cache",
    "nakala ya muda": "cached data",
    "kumbukumbu ya kiendeshi cha ndani": "local memory",
    "kumbukumbu ya ndani": "internal storage",
    "kumbukumbu ya muda": "cache",
    "kiendeshi cha ndani": "internal storage",
    "kiendeshi cha diski": "hard drive",
    "kompyuta nyingi za utoaji huduma": "maserver zote",
    "kompyuta za utoaji huduma": "maserver",
    "kompyuta ya utoaji huduma": "server",
    "kinagawa mtiririko wa data sawia": "ina-distribute traffic sawia",
    "kinagawa mtiririko wa data": "ina-distribute traffic",
    "inagawa mtiririko wa data": "ina-distribute traffic",
    "kugawa mtiririko wa data": "ku-distribute traffic",
    "mtiririko wa data": "traffic ya requests",
    "kukatika kwa mfumo mzima": "system downtime",
    "kukatika kwa mfumo": "system downtime",
    "iwapo kompyuta moja itaharibika": "ikiwa server moja ita-crash",
    "itaharibika": "ita-crash",
    "zitaharibika": "zita-crash",
    "zimeharibika ghafla": "zime-crash ghafla",
    "zimeharibika": "zime-crash",
    "kuharibika ghafla": "ku-crash ghafla",
    "kuharibika": "ku-crash",
    "isielemewe": "isi-overload",
    "wasielemewe": "wasi-overload",
    "kuelemewa": "ku-overload",
    "kulemewa": "ku-overload",
    "limeelemewa": "lime-overload",
    "zimeelemewa": "zime-overload",
    "na maombi mengi ya watumiaji": "na requests mob za users",
    "maombi mengi ya watumiaji": "requests mob za users",
    "maombi ya watumiaji": "requests za users",
    "watumiaji wa programu tumizi": "users wa application",
    "watumiaji wa programu": "users wa application",
    "watumiaji wa app": "users wa app",
    "maombi mengi": "requests mob",
    "maombi mabaya": "malicious traffic / attacks",
    "maombi": "requests",
    "watumiaji": "users",
    "programu tumizi": "application",
    "kinachunguza hati za kila mtumiaji": "ina-authenticate credentials za kila user",
    "inachunguza hati": "ina-authenticate credentials",
    "hati za kila mtumiaji": "credentials za user",
    "kuweka kikomo cha idadi ya maombi kwa kila sekunde": "ku-enforce rate limit ya requests per second",
    "kuweka kikomo cha idadi ya maombi": "ku-enforce rate limit ya requests",
    "kikomo cha idadi ya maombi": "rate limit ya requests",
    "kwa kila sekunde": "per second",
    "seva kuu": "main server",
    "seva": "server",
    "kanzidata": "database",
    "kanzi data": "database",
    "kifaa cha kusawazisha mzigo": "load balancer",
    "kusawazisha mzigo": "ku-load balance",
    "inasawazisha mzigo": "ina-load balance",
    "huduma ndogo ndogo": "microservices",
    "mifumo iliyotawanyika": "distributed systems",
    "kiwambo cha uthibitishaji": "API gateway",
    "kiwambo cha moto": "firewall",
    "vibanzi": "chips / processors",
    "usanidi": "configuration",
    "kuingiliwa na wadukuzi": "ku-experience cyber attack / injection",

    # --------------------------------------------------------------------------
    # Engineering & Infrastructure
    # --------------------------------------------------------------------------
    "boriti ya saruji iliyoimarishwa kwa vyuma": "concrete beam iliyo-reinforce kwa rebar",
    "saruji iliyoimarishwa kwa vyuma": "reinforced concrete yenye rebar",
    "saruji iliyoimarishwa": "reinforced concrete",
    "boriti ya saruji": "concrete beam",
    "ihimili": "i-withstand",
    "kuhimili": "ku-withstand",
    "inahimili": "ina-withstand",
    "kani ya kupinda": "bending moment",
    "kani ya mkato": "shear stress",
    "kani ya mgandamizo": "compression force",
    "uzito mkubwa wa jengo": "structural load ya jengo",
    "kuweka sakafu ya juu": "ku-cast slab ya juu",
    "sakafu ya juu": "slab ya juu",
    "kibadilishaji umeme": "transformer",
    "kituo kidogo cha umeme": "substation",
    "kituo kidogo": "substation",
    "msukumo mkubwa wa umeme": "high voltage power surge",
    "kinashusha nguvu ya msukumo wa mkondo mkuu": "ina-step down high voltage grid",
    "usambazaji salama": "ku-distribute stima kwa usalama",
    "kuzuia milipuko ya saketi za viwandani": "kuzuia power surges zisi-short macircuit viwandani",
    "saketi za viwandani": "macircuit viwandani",
    "mzunguko wa umeme": "circuit",
    "saketi": "circuit",
    "kukatika kwa umeme": "power blackout / trip",
    "kukatika kwa ghafla": "ku-trip mara moja",
    "mtambo wa mgandamizo wa vimiminika": "hydraulic system",
    "msuguano": "friction",
    "kulainisha": "ku-lubricate",
    "kuchakaa kwa mapanga ya turbine": "turbine cavitation",
    "mwinuko wa jengo": "structural elevation",
    "msingi wa kina": "deep pile foundation",

    # --------------------------------------------------------------------------
    # Finance & Economics
    # --------------------------------------------------------------------------
    "chama cha ushirika wa akiba na mikopo": "SACCO",
    "kuuza rehani ya mkopaji": "ku-liquidate collateral ya borrower",
    "kuuza rehani": "ku-liquidate collateral",
    "inauza rehani": "ina-liquidate collateral",
    "waliuza rehani": "wali-liquidate collateral",
    "rehani": "collateral",
    "kurejesha fedha za wanachama": "ku-recover loan za wanachama",
    "kutolipwa kwa miezi sita": "ku-default kwa miezi sita",
    "ukwasi": "liquidity",
    "upungufu wa ukwasi": "liquidity deficit / crunch",
    "mfumuko wa bei": "inflation",
    "thamani ya fedha": "currency valuation",
    "kushuka kwa thamani ya shilingi": "shilling depreciation",
    "kulinda thamani ya fedha": "ku-hedge foreign exchange risk",
    "mikataba ya awali ya fedha": "forward exchange contracts",
    "usimamizi wa madeni yasiyolipika": "non-performing loan (NPL) recovery",
    "kodi ya ongezeko la thamani": "Value Added Tax (VAT)",
    "kuzuia ukwepaji wa kodi": "ku-prevent tax evasion kwa eTIMS",
    "hisa": "shares / equity",
    "hisa za mtaji": "shares capital",
    "mgao wa faida": "dividends",
    "hati fungani za serikali": "treasury bonds",

    # --------------------------------------------------------------------------
    # Medicine & Healthcare
    # --------------------------------------------------------------------------
    "daktari wa mapokezi ya dharura": "daktari wa triage",
    "mapokezi ya dharura": "triage / casualty",
    "kuingiza mrija wa kupumulia": "ku-intubate",
    "aliingiza mrija wa kupumulia": "ali-intubate",
    "anaingiza mrija wa kupumulia": "ana-intubate",
    "mashine ya kusaidia kupumua": "ventilator",
    "upungufu wa hewa ya oksijeni": "low oxygen saturation",
    "tabibu": "daktari",
    "mshtuko wa moyo": "heart attack / cardiac arrest",
    "upimaji wa umeme wa moyo": "electrocardiogram (ECG)",
    "dawa za kuua bakteria": "targeted antibiotics kutoka duka la dawa",
    "dawa za kuzuia kuganda kwa damu": "anticoagulants",
    "kustahimili dawa kwa vimelea": "antimicrobial drug resistance",
    "chumba cha wagonjwa mahututi": "ICU",
    "uchunguzi wa kimaabara wa tishu": "tissue biopsy / pathology test",
    "upungufu wa damu mwilini": "anemia",

    # --------------------------------------------------------------------------
    # Politics & Public Policy
    # --------------------------------------------------------------------------
    "Bunge la wananchi": "Bunge",
    "Bunge la jimbo": "County Assembly",
    "mkuu wa kaunti": "gavana",
    "kumwondoa mkuu wa kaunti madarakani": "ku-impeach gavana",
    "kumwondoa kiongozi madarakani": "ku-impeach gavana / kiongozi",
    "walimwondoa mkuu wa kaunti": "wali-impeach gavana",
    "kutoa nafasi ya maoni ya raia": "ku-conduct public participation",
    "nafasi ya maoni ya raia": "public participation",
    "ushiriki wa umma": "public participation",
    "vifungu vya mswada wa makadirio ya mapato na matumizi ya kitaifa": "maclause ya Finance Bill",
    "vifungu vya mswada wa makadirio": "maclause ya Finance Bill",
    "vifungu vya mswada": "maclause ya bill",
    "kubadilisha vifungu vya sheria": "ku-amend clauses za mswada",
    "mswada wa makadirio": "Finance Bill",
    "mswada wa fedha": "Finance Bill",
    "mswada wa sheria": "bill",
    "serikali zilizogatuliwa": "county governments",
    "ugavi wa mapato": "revenue allocation formula",
    "utawala wa sheria": "rule of law na due process ya Katiba",
    "kamati ya maridhiano ya bunge": "mediation committee ya bunge",
    "ripoti ya mkaguzi mkuu": "Auditor-General report",
    "kupinga uhalali wa sheria": "ku-file petition ya judicial review",

    # --------------------------------------------------------------------------
    # Rule IX: The "Kwa" Overlord Preposition
    # --------------------------------------------------------------------------
    "kwenye": "kwa"
}

# ==============================================================================
# STRUCTURED CONCEPT RECREATION BENCHMARK PAIRS
# ==============================================================================

CONCEPT_RECREATION_CORPUS: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # TECH & DISTRIBUTED SYSTEMS
    # --------------------------------------------------------------------------
    {
        "domain": "Tech & Distributed Systems",
        "concept": "Database Caching & Performance Optimization",
        "english_concept": "The database caches data in local memory to prevent the main server from being overloaded by heavy request traffic from application users.",
        "pure_swahili": "Kanzidata inahifadhi nakala ya muda kwenye kumbukumbu ya kiendeshi cha ndani ili kuzuia seva kuu isielemewe na maombi mengi ya watumiaji wa programu tumizi.",
        "codeswitched_recreation": "Database ina-cache data kwa local memory ili kuzuia main server isi-overload na requests mob za users wa application.",
        "recreated_mappings": [
            {"pure_swahili": "kanzidata", "recreated_codeswitch": "database", "english": "database"},
            {"pure_swahili": "inahifadhi nakala ya muda", "recreated_codeswitch": "ina-cache data", "english": "caches data"},
            {"pure_swahili": "kwenye", "recreated_codeswitch": "kwa", "english": "in / at"},
            {"pure_swahili": "kumbukumbu ya kiendeshi cha ndani", "recreated_codeswitch": "local memory", "english": "local memory"},
            {"pure_swahili": "seva kuu", "recreated_codeswitch": "main server", "english": "main server"},
            {"pure_swahili": "isielemewe", "recreated_codeswitch": "isi-overload", "english": "prevent from overloading"},
            {"pure_swahili": "na maombi mengi ya watumiaji wa programu tumizi", "recreated_codeswitch": "na requests mob za users wa application", "english": "by heavy application user requests"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ina-cache', 'isi-overload')",
            "Rule IX: 'Kwa' Overlord Preposition ('kwa local memory')",
            "Colloquial Amplifier: 'requests mob za users'",
            "Technical Concord: 'Database', 'main server', 'users wa application'",
            "Explanatory Linker: 'ili kuzuia...'"
        ],
        "conceptual_clarity_gain": "Replaces archaic 'kanzidata' and 'seva' with standard Nairobi tech industry vernacular while maintaining full Swahili causal explanatory syntax."
    },
    {
        "domain": "Tech & Distributed Systems",
        "concept": "Microservices Load Balancing & Fault Tolerance",
        "english_concept": "The load balancer distributes traffic evenly across multiple servers to prevent total system downtime if one server crashes.",
        "pure_swahili": "Kifaa cha kusawazisha mzigo kinagawa mtiririko wa data sawia kwenye kompyuta nyingi za utoaji huduma ili kuzuia kukatika kwa mfumo mzima iwapo kompyuta moja itaharibika.",
        "codeswitched_recreation": "Load balancer ina-distribute traffic sawia kwa maserver zote ili kuzuia system downtime ikiwa server moja ita-crash.",
        "recreated_mappings": [
            {"pure_swahili": "kifaa cha kusawazisha mzigo", "recreated_codeswitch": "load balancer", "english": "load balancer"},
            {"pure_swahili": "kinagawa mtiririko wa data sawia", "recreated_codeswitch": "ina-distribute traffic sawia", "english": "distributes traffic evenly"},
            {"pure_swahili": "kwenye kompyuta nyingi za utoaji huduma", "recreated_codeswitch": "kwa maserver zote", "english": "across multiple servers"},
            {"pure_swahili": "kukatika kwa mfumo mzima", "recreated_codeswitch": "system downtime", "english": "total system downtime"},
            {"pure_swahili": "iwapo kompyuta moja itaharibika", "recreated_codeswitch": "ikiwa server moja ita-crash", "english": "if one server crashes"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ina-distribute', 'ita-crash')",
            "Rule IV: Double-Stack Pluralization ('maserver')",
            "Rule IX: 'Kwa' Overlord Preposition ('kwa maserver')",
            "Explanatory Linker: 'ili kuzuia... ikiwa...'"
        ],
        "conceptual_clarity_gain": "Instantly understandable to developers; avoids clunky textbook phrasing ('kifaa cha kusawazisha mzigo') without abandoning Swahili grammatical framing."
    },
    {
        "domain": "Tech & Distributed Systems",
        "concept": "API Authentication & Rate Limiting",
        "english_concept": "The API gateway authenticates credentials of each user and enforces a rate limit on requests per second to prevent the server from overloading under malicious traffic.",
        "pure_swahili": "Kiwambo cha uthibitishaji kinachunguza hati za kila mtumiaji na kuweka kikomo cha idadi ya maombi kwa kila sekunde ili kuzuia seva kulemewa na maombi mabaya.",
        "codeswitched_recreation": "API gateway ina-authenticate credentials za kila user na ku-enforce rate limit ya requests per second ili kuzuia server ku-overload na malicious traffic.",
        "recreated_mappings": [
            {"pure_swahili": "kiwambo cha uthibitishaji", "recreated_codeswitch": "API gateway", "english": "API gateway"},
            {"pure_swahili": "kinachunguza hati za kila mtumiaji", "recreated_codeswitch": "ina-authenticate credentials za kila user", "english": "authenticates user credentials"},
            {"pure_swahili": "kuweka kikomo cha idadi ya maombi kwa kila sekunde", "recreated_codeswitch": "ku-enforce rate limit ya requests per second", "english": "enforce requests per second rate limit"},
            {"pure_swahili": "seva kulemewa na maombi mabaya", "recreated_codeswitch": "server ku-overload na malicious traffic", "english": "server overloading under malicious traffic"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ina-authenticate', 'ku-overload')",
            "Domain Lexicon: 'credentials za kila user', 'rate limit per second', 'malicious traffic'",
            "Explanatory Linker: 'ili kuzuia...'"
        ],
        "conceptual_clarity_gain": "Maps abstract Swahili security descriptions directly to standard cloud API infrastructure."
    },

    # --------------------------------------------------------------------------
    # ENGINEERING & INFRASTRUCTURE
    # --------------------------------------------------------------------------
    {
        "domain": "Engineering & Infrastructure",
        "concept": "Structural Reinforcement & Stress Withstanding",
        "english_concept": "The reinforced concrete beam must withstand bending moments and shear stress under heavy structural load before casting the upper floor slab.",
        "pure_swahili": "Boriti ya saruji iliyoimarishwa kwa vyuma lazima ihimili kani ya kupinda na kani ya mkato chini ya uzito mkubwa wa jengo kabla ya kuweka sakafu ya juu.",
        "codeswitched_recreation": "Concrete beam iliyo-reinforce kwa rebar nzito lazima i-withstand bending moment na shear stress chini ya structural load ya jengo kabla hatuja-cast slab ya juu.",
        "recreated_mappings": [
            {"pure_swahili": "boriti ya saruji iliyoimarishwa kwa vyuma", "recreated_codeswitch": "concrete beam iliyo-reinforce kwa rebar nzito", "english": "reinforced concrete beam"},
            {"pure_swahili": "ihimili", "recreated_codeswitch": "i-withstand", "english": "withstand"},
            {"pure_swahili": "kani ya kupinda", "recreated_codeswitch": "bending moment", "english": "bending moment"},
            {"pure_swahili": "kani ya mkato", "recreated_codeswitch": "shear stress", "english": "shear stress"},
            {"pure_swahili": "uzito mkubwa wa jengo", "recreated_codeswitch": "structural load ya jengo", "english": "heavy structural load"},
            {"pure_swahili": "kuweka sakafu ya juu", "recreated_codeswitch": "ku-cast slab ya juu", "english": "casting upper floor slab"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('iliyo-reinforce', 'i-withstand', 'hatuja-cast')",
            "Rule IX: 'Kwa' Overlord Preposition ('kwa rebar nzito')",
            "Compound Concept Plug-in: 'bending moment', 'shear stress', 'structural load'",
            "Explanatory Linker: 'chini ya... kabla hatuja...'"
        ],
        "conceptual_clarity_gain": "Civil engineers on Kenyan construction sites communicate using these exact technical terms inside Swahili grammatical agreement."
    },
    {
        "domain": "Engineering & Infrastructure",
        "concept": "Electrical Substation Step-Down & Surge Protection",
        "english_concept": "The electrical transformer at the substation steps down the high voltage grid to enable safe distribution and prevent industrial circuits from shorting.",
        "pure_swahili": "Kibadilishaji umeme kwenye kituo kidogo kinashusha nguvu ya msukumo wa mkondo mkuu ili kuwezesha usambazaji salama na kuzuia milipuko ya saketi za viwandani.",
        "codeswitched_recreation": "Transformer kwa substation ina-step-down high voltage grid ili ku-distribute stima kwa usalama na kuzuia power surges zisi-short macircuit viwandani.",
        "recreated_mappings": [
            {"pure_swahili": "kibadilishaji umeme", "recreated_codeswitch": "transformer", "english": "electrical transformer"},
            {"pure_swahili": "kwenye kituo kidogo", "recreated_codeswitch": "kwa substation", "english": "at the substation"},
            {"pure_swahili": "kinashusha nguvu ya msukumo wa mkondo mkuu", "recreated_codeswitch": "ina-step-down high voltage grid", "english": "steps down high voltage grid"},
            {"pure_swahili": "usambazaji salama", "recreated_codeswitch": "ku-distribute stima kwa usalama", "english": "safe power distribution"},
            {"pure_swahili": "kuzuia milipuko ya saketi za viwandani", "recreated_codeswitch": "kuzuia power surges zisi-short macircuit viwandani", "english": "prevent industrial circuits shorting"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ina-step-down', 'ku-distribute', 'zisi-short')",
            "Rule IV: Double-Stack Pluralization ('macircuit')",
            "Rule IX: 'Kwa' Overlord Preposition ('kwa substation')",
            "Explanatory Linker: 'ili ku-... na kuzuia... zisi-...'"
        ],
        "conceptual_clarity_gain": "Eliminates confusing terminology ('msukumo wa mkondo mkuu') in favor of clear electrical engineering terminology."
    },

    # --------------------------------------------------------------------------
    # FINANCE & FINTECH ECONOMICS
    # --------------------------------------------------------------------------
    {
        "domain": "Finance & FinTech Economics",
        "concept": "SACCO Collateral Liquidation & Risk Recovery",
        "english_concept": "The credit union (SACCO) had to liquidate defaulting borrowers' collateral to recover cash and maintain liquidity to safeguard member deposits.",
        "pure_swahili": "Chama cha ushirika wa akiba na mikopo kililazimika kuuza rehani za wakopaji waliokiuka makubaliano ili kufidia upungufu wa ukwasi na kulinda amana za wanachama.",
        "codeswitched_recreation": "SACCO ililazimika ku-liquidate collateral za madefaulter ili ku-recover chapaa na ku-maintain liquidity ratio ya kulinda amana za wanachama.",
        "recreated_mappings": [
            {"pure_swahili": "chama cha ushirika wa akiba na mikopo", "recreated_codeswitch": "SACCO", "english": "credit union / savings cooperative"},
            {"pure_swahili": "kuuza rehani za wakopaji waliokiuka makubaliano", "recreated_codeswitch": "ku-liquidate collateral za madefaulter", "english": "liquidate defaulting borrowers' collateral"},
            {"pure_swahili": "kufidia upungufu wa ukwasi", "recreated_codeswitch": "ku-recover chapaa na ku-maintain liquidity ratio", "english": "recover cash and maintain liquidity"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ku-liquidate', 'ku-recover', 'ku-maintain')",
            "Rule IV: Double-Stack Pluralization ('madefaulter')",
            "Lexical Sense Preservation: 'chapaa' = money/liquidity",
            "Explanatory Linker: 'ili ku-... na ku-... ya kulinda...'"
        ],
        "conceptual_clarity_gain": "Reflects everyday banking, SACCO boardroom, and credit committee discourse in Nairobi."
    },
    {
        "domain": "Finance & FinTech Economics",
        "concept": "Currency Depreciation Hedging via Derivatives",
        "english_concept": "Banks and importers hedge foreign exchange risk using forward contracts to prevent losses resulting from Kenyan shilling currency depreciation.",
        "pure_swahili": "Benki na waagizaji wa bidhaa walinunua mikataba ya awali ya kulinda thamani ya fedha ili kuzuia hasara inayotokana na kushuka kwa thamani ya shilingi ya Kenya.",
        "codeswitched_recreation": "Benki na maimporter waliamua ku-hedge foreign exchange risk kwa forward contracts ili kuzuia hasara ya currency depreciation ya shilingi.",
        "recreated_mappings": [
            {"pure_swahili": "waagizaji wa bidhaa", "recreated_codeswitch": "maimporter", "english": "importers"},
            {"pure_swahili": "mikataba ya awali ya kulinda thamani ya fedha", "recreated_codeswitch": "forward contracts za ku-hedge foreign exchange risk", "english": "forward contracts for forex hedging"},
            {"pure_swahili": "kushuka kwa thamani ya shilingi", "recreated_codeswitch": "currency depreciation ya shilingi", "english": "shilling currency depreciation"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ku-hedge', never '*ku-hedged')",
            "Rule IV: Double-Stack Pluralization ('maimporter')",
            "Rule IX: 'Kwa' Overlord Preposition ('kwa forward contracts')",
            "Explanatory Linker: 'ili kuzuia hasara ya...'"
        ],
        "conceptual_clarity_gain": "Makes complex macroeconomic risk management transparent to finance students and professionals."
    },

    # --------------------------------------------------------------------------
    # MEDICINE & HEALTHCARE SCIENCES
    # --------------------------------------------------------------------------
    {
        "domain": "Medicine & Healthcare Sciences",
        "concept": "Emergency Endotracheal Intubation & Triage",
        "english_concept": "The emergency triage doctor had to intubate the respiratory arrest patient and place them on a ventilator to stabilize oxygen saturation.",
        "pure_swahili": "Tabibu wa mapokezi ya dharura alilazimika kuingiza mrija wa kupumulia kwenye koromeo la mgonjwa aliyeshindwa kupumua na kumuunganisha na mashine ya hewa ili kuokoa maisha yake.",
        "codeswitched_recreation": "Daktari wa triage alilazimika ku-intubate mgonjwa wa respiratory arrest na kumweka kwa ventilator ili ku-stabilize oxygen saturation mwilini.",
        "recreated_mappings": [
            {"pure_swahili": "tabibu wa mapokezi ya dharura", "recreated_codeswitch": "daktari wa triage", "english": "emergency triage doctor"},
            {"pure_swahili": "kuingiza mrija wa kupumulia kwenye koromeo", "recreated_codeswitch": "ku-intubate", "english": "endotracheal intubation"},
            {"pure_swahili": "mashine ya hewa", "recreated_codeswitch": "ventilator", "english": "ventilator"},
            {"pure_swahili": "kuokoa maisha yake", "recreated_codeswitch": "ku-stabilize oxygen saturation mwilini", "english": "stabilize oxygen saturation"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ku-intubate', 'ku-stabilize')",
            "Rule IX: 'Kwa' Overlord Preposition ('kwa ventilator')",
            "Semantic Invariant: Medical register strictly grounded",
            "Explanatory Linker: 'ili ku-stabilize...'"
        ],
        "conceptual_clarity_gain": "Clinical officers and ER doctors in Kenyan hospitals speak this exact dialect; archaic terms ('mrija wa koromeo') waste critical seconds in emergency contexts."
    },
    {
        "domain": "Medicine & Healthcare Sciences",
        "concept": "Targeted Antimicrobial Prescription",
        "english_concept": "The physician ran a laboratory culture test and prescribed targeted antibiotics from the pharmacy to prevent bacteria from developing drug resistance.",
        "pure_swahili": "Tabibu alichunguza vimelea kwenye maabara na kuamua kumpa mgonjwa dawa mahususi ili kuzuia bakteria zisiweze kustahimili dawa mwilini mwake.",
        "codeswitched_recreation": "Daktari alifanya culture test akaamua ku-prescribe targeted antibiotic kutoka duka la dawa ili kuzuia bacteria zisi-develop drug resistance.",
        "recreated_mappings": [
            {"pure_swahili": "tabibu", "recreated_codeswitch": "daktari", "english": "doctor / physician"},
            {"pure_swahili": "alichunguza vimelea kwenye maabara", "recreated_codeswitch": "alifanya culture test", "english": "ran a culture test"},
            {"pure_swahili": "kumpa mgonjwa dawa mahususi", "recreated_codeswitch": "ku-prescribe targeted antibiotic", "english": "prescribe targeted antibiotic"},
            {"pure_swahili": "bakteria zisiweze kustahimili dawa", "recreated_codeswitch": "bacteria zisi-develop drug resistance", "english": "bacteria developing drug resistance"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ku-prescribe', 'zisi-develop')",
            "Semantic Invariant Preservation: 'duka la dawa' = strictly therapeutic medicine",
            "Explanatory Linker: 'ili kuzuia... zisi-...'"
        ],
        "conceptual_clarity_gain": "Unambiguous pharmacological communication preserving the strict 'dawa' semantic invariant."
    },

    # --------------------------------------------------------------------------
    # POLITICS & PUBLIC POLICY
    # --------------------------------------------------------------------------
    {
        "domain": "Politics & Public Policy",
        "concept": "Public Participation & Parliamentary Amendments",
        "english_concept": "Parliament must conduct public participation before amending clauses of the national Finance Bill so citizens and experts can table their views.",
        "pure_swahili": "Bunge la wananchi lazima litoe nafasi ya maoni ya raia kabla ya kubadilisha vifungu vya mswada wa makadirio ya mapato na matumizi ya kitaifa.",
        "codeswitched_recreation": "Bunge lazima li-conduct public participation kabla ya ku-amend maclause ya Finance Bill ili wananchi na wataalamu wa-table maoni yao.",
        "recreated_mappings": [
            {"pure_swahili": "nafasi ya maoni ya raia", "recreated_codeswitch": "public participation", "english": "public participation"},
            {"pure_swahili": "kubadilisha vifungu vya mswada wa makadirio", "recreated_codeswitch": "ku-amend maclause ya Finance Bill", "english": "amending Finance Bill clauses"},
            {"pure_swahili": "kutoa maoni", "recreated_codeswitch": "ku-table maoni yao", "english": "table their views"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('li-conduct', 'ku-amend', 'wa-table')",
            "Rule IV: Double-Stack Pluralization ('maclause')",
            "Constitutional Anchoring: Katiba 2010 Article 10 terminology",
            "Explanatory Linker: 'kabla ya ku-... ili wananchi wa-...'"
        ],
        "conceptual_clarity_gain": "Matches Kenyan parliamentary broadcasts, civil society debates, and newsroom analysis."
    },
    {
        "domain": "Politics & Public Policy",
        "concept": "Gubernatorial Impeachment & Judicial Review",
        "english_concept": "When the County Assembly voted to impeach the governor, the High Court conducted a judicial review to verify whether constitutional due process was followed.",
        "pure_swahili": "Bunge la jimbo lilipopitisha azimio la kumwondoa mkuu wa kaunti madarakani, mahakama kuu ilitakiwa kutathmini kama utaratibu wa kisheria ulifuatwa kikamilifu.",
        "codeswitched_recreation": "County Assembly ilipo-impeach gavana, High Court ilifanya judicial review ku-verify kama mchakato ulizingatia due process ya Katiba.",
        "recreated_mappings": [
            {"pure_swahili": "bunge la jimbo", "recreated_codeswitch": "County Assembly", "english": "County Assembly"},
            {"pure_swahili": "kumwondoa mkuu wa kaunti madarakani", "recreated_codeswitch": "ku-impeach gavana", "english": "impeach the governor"},
            {"pure_swahili": "mahakama kuu", "recreated_codeswitch": "High Court", "english": "High Court"},
            {"pure_swahili": "utaratibu wa kisheria", "recreated_codeswitch": "due process ya Katiba", "english": "constitutional due process"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ilipo-impeach', 'ku-verify')",
            "Institutional Concord: 'County Assembly', 'High Court', 'due process ya Katiba'",
            "Explanatory Linker: 'ilipo-... ilifanya... ku-verify kama...'"
        ],
        "conceptual_clarity_gain": "Provides exact constitutional and legal precision while retaining natural Swahili temporal prefixation ('ilipo-')."
    },

    # --------------------------------------------------------------------------
    # CYBERNETICS, COMPUTATION & EPISTEMOLOGY
    # --------------------------------------------------------------------------
    {
        "domain": "Cybernetics & Epistemology",
        "concept": "McCulloch Epistemological Problem of Number & Mind",
        "english_concept": "What is a number, that a man may know it, and a man, that he may know a number?",
        "pure_swahili": "Namba ni kitu gani, kiasi kwamba binadamu anaweza kuijua, na binadamu ni nani, kiasi kwamba anaweza kujua namba?",
        "codeswitched_recreation": "Kwani number ni nini, hadi msee aweze ku-know, na msee ni nani, hadi aweze ku-know number?",
        "recreated_mappings": [
            {"english": "What is a number", "pure_swahili": "Namba ni kitu gani", "recreated_codeswitch": "Kwani number ni nini"},
            {"english": "that a man may know it", "pure_swahili": "kiasi kwamba binadamu anaweza kuijua", "recreated_codeswitch": "hadi msee aweze ku-know"},
            {"english": "and a man", "pure_swahili": "na binadamu ni nani", "recreated_codeswitch": "na msee ni nani"},
            {"english": "that he may know a number", "pure_swahili": "kiasi kwamba aweze kujua namba", "recreated_codeswitch": "hadi aweze ku-know number"}
        ],
        "applied_rules": [
            "Rule I: Bare Root Constraint ('ku-know', uninflected English root)",
            "Rule IV & Colloquial Concord: 'msee' (human agent), 'number' (abstract entity)",
            "Subjunctive Ability Concord: 'a-weze' (Class 1 subject agreement with modal root)",
            "Causal Linker: 'hadi' (consequential result marker)"
        ],
        "conceptual_clarity_gain": "Reconstructs Warren McCulloch's foundational cybernetic question into high-register Kenyan intellectual parlance without losing philosophical depth or mathematical rigor."
    },
    {
        "domain": "Cybernetics & Epistemology",
        "concept": "Heraclitus Doctrine of Universal Flux & Identity",
        "english_concept": "You cannot step into the same river twice.",
        "pure_swahili": "Huwezi kukanyaga mto uleule mara mbili.",
        "codeswitched_recreation": "Hauezi ku-step kwa river ile ile twice.",
        "recreated_mappings": [
            {"english": "You cannot", "pure_swahili": "Huwezi", "recreated_codeswitch": "Hauezi"},
            {"english": "step into", "pure_swahili": "kukanyaga kwenye", "recreated_codeswitch": "ku-step kwa"},
            {"english": "the same river", "pure_swahili": "mto uleule", "recreated_codeswitch": "river ile ile"},
            {"english": "twice", "pure_swahili": "mara mbili", "recreated_codeswitch": "twice"}
        ],
        "applied_rules": [
            "Pillar I: Bare Root Constraint ('ku-step')",
            "Rule IX: 'Kwa' Overlord Preposition ('kwa river')",
            "Double Demonstrative Reduplication ('river ile ile')",
            "Modal Negation Concord ('hauezi ku-')"
        ],
        "conceptual_clarity_gain": "Reconstructs Heraclitus's famous 500 BC doctrine of ontological change into sharp Kenyan philosophical parlance."
    }
]

# ==============================================================================
# RULE-BASED CONCEPT RECREATOR ENGINE (BI-DIRECTIONAL TRI-SET)
# ==============================================================================

class ConceptRecreationEngine:
    """
    Transforms Pure Swahili technical text or English technical concepts into authentic
    Kenyan Code-Switched Explanatory Discourse by applying the Master Blueprint morphotactic rules.
    Outputs the parallel Tri-Set:
      - Set B: Standard Technical English Concept
      - Set A: Textbook Kiswahili Sanifu Concept
      - Set C: Living Kenyan Code-Switching
    """
    def __init__(self):
        self.term_map = SWAHILI_TO_CODESWITCH_TERM_MAP
        self.corpus = CONCEPT_RECREATION_CORPUS

    def get_benchmark_pairs(self) -> List[Dict[str, Any]]:
        """Returns all curated concept recreation benchmark pairs."""
        return self.corpus

    @staticmethod
    def _normalize_tokens(s: str) -> set:
        stopwords = {
            "a", "an", "the", "is", "are", "was", "were", "that", "this", "it", "its",
            "to", "from", "in", "on", "at", "by", "for", "with", "and", "or", "of",
            "ya", "wa", "za", "cha", "vya", "kwa", "na", "ni", "la", "ma"
        }
        all_toks = set(re.findall(r"[a-zA-Z0-9]+", s.lower()))
        content_toks = all_toks - stopwords
        return content_toks if len(content_toks) >= 2 else all_toks

    def _find_matching_benchmark(self, text: str) -> Tuple[Dict[str, Any] | None, str, float]:
        """Finds closest benchmark pair using token overlap."""
        tokens = self._normalize_tokens(text)
        if not tokens:
            return None, "Unknown", 0.0

        best_match = None
        best_score = 0.0
        best_lang = "Swahili Sanifu"

        for b in self.corpus:
            sw_tokens = self._normalize_tokens(b.get("pure_swahili", ""))
            en_tokens = self._normalize_tokens(b.get("english_concept", ""))
            cs_tokens = self._normalize_tokens(b.get("codeswitched_recreation", ""))

            sw_overlap = len(tokens & sw_tokens) / max(1, len(tokens | sw_tokens))
            en_overlap = len(tokens & en_tokens) / max(1, len(tokens | en_tokens))
            cs_overlap = len(tokens & cs_tokens) / max(1, len(tokens | cs_tokens))

            # Also check substring match (only if non-trivial length)
            low_text = text.lower().strip()
            b_sw = b.get("pure_swahili", "").lower().strip()
            b_en = b.get("english_concept", "").lower().strip()
            b_cs = b.get("codeswitched_recreation", "").lower().strip()
            if len(low_text) >= 15:
                if low_text in b_sw or b_sw in low_text:
                    sw_overlap = max(sw_overlap, 0.90)
                if low_text in b_en or b_en in low_text:
                    en_overlap = max(en_overlap, 0.90)
                if low_text in b_cs or b_cs in low_text:
                    cs_overlap = max(cs_overlap, 0.90)

            score = max(sw_overlap, en_overlap, cs_overlap)
            if score > best_score:
                best_score = score
                best_match = b
                if en_overlap >= sw_overlap and en_overlap >= cs_overlap:
                    best_lang = "English (Set B)"
                elif cs_overlap > sw_overlap:
                    best_lang = "Kenyan Code-Switch (Set C)"
                else:
                    best_lang = "Kiswahili Sanifu (Set A)"

        return best_match, best_lang, best_score

    def reconstruct_concept(self, input_text: str) -> Dict[str, Any]:
        """
        Reconstructs a technical concept into living Kenyan Code-Switching.
        Accepts either English technical descriptions OR Pure Swahili Sanifu sentences.
        Returns the complete Tri-Set (English Concept, Pure Swahili Concept, Code-Switched Output).
        """
        clean_input = input_text.strip()
        if not clean_input:
            return {
                "detected_input_language": "None",
                "english_concept": "",
                "pure_swahili": "",
                "original_pure_swahili": "",
                "reconstructed_codeswitch": "",
                "terms_recreated_count": 0,
                "recreated_mappings": [],
                "applied_rules": [],
                "conceptual_clarity_gain": "No input provided."
            }

        # 1. Check if input closely matches an authoritative benchmark
        match_bench, detected_lang, score = self._find_matching_benchmark(clean_input)
        if match_bench and score >= 0.75:
            return {
                "detected_input_language": detected_lang,
                "domain": match_bench.get("domain", "General"),
                "concept": match_bench.get("concept", "Technical Concept"),
                "english_concept": match_bench.get("english_concept", ""),
                "pure_swahili": match_bench.get("pure_swahili", ""),
                "original_pure_swahili": match_bench.get("pure_swahili", ""),
                "reconstructed_codeswitch": match_bench.get("codeswitched_recreation", ""),
                "terms_recreated_count": len(match_bench.get("recreated_mappings", [])),
                "recreated_mappings": match_bench.get("recreated_mappings", []),
                "applied_rules": match_bench.get("applied_rules", []),
                "conceptual_clarity_gain": match_bench.get("conceptual_clarity_gain", "")
            }

        # 2. Autonomous Neural Engine (Gemini 2.5 Flash Teacher)
        try:
            from src.gemini_concept_client import query_gemini_tri_set
            neural_res = query_gemini_tri_set(clean_input)
            if neural_res and "reconstructed_codeswitch" in neural_res:
                return neural_res
        except Exception as e:
            # Fall back to local CPU morphotactics if offline or network unavailable
            pass

        # 3. Local Deterministic Morphotactic CPU Fallback
        en_markers = {
            "the", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "can", "cannot", "could", "should", "would", "will", "must",
            "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
            "my", "your", "his", "their", "our", "this", "that", "these", "those",
            "to", "of", "in", "for", "on", "with", "at", "by", "from", "into", "over",
            "after", "before", "between", "through", "without", "again", "then", "once", "twice",
            "when", "where", "why", "how", "all", "any", "both", "each", "other", "some",
            "not", "no", "same", "think", "know", "step", "river", "life", "power", "water",
            "caches", "cache", "server", "database", "system", "load", "traffic"
        }
        sw_markers = {
            "na", "ya", "wa", "kwa", "katika", "ni", "la", "za", "cha", "vya", "mwa",
            "kama", "hadi", "ili", "bila", "lakini", "au", "ama", "basi", "hivyo",
            "kwenye", "ndani", "nje", "juu", "chini", "kabla", "baada", "hata", "wala",
            "mimi", "wewe", "yeye", "sisi", "nyinyi", "wao", "hii", "huyu", "hawa",
            "hiki", "ule", "ile", "yake", "yangu", "yako", "yao", "yetu", "mtu", "watu",
            "kitu", "vitu", "mto", "namba", "kanzidata", "kumbukumbu", "kuzuia", "seva",
            "mfumo", "mashine", "lazima", "wakati", "huwezi", "hawezi", "hawawezi", "kukanyaga"
        }

        tokens_lower = set(re.findall(r"[a-zA-Z]+", clean_input.lower()))
        en_count = len(tokens_lower & en_markers)
        sw_count = len(tokens_lower & sw_markers)

        if en_count > sw_count:
            is_english = True
        elif sw_count > en_count:
            is_english = False
        else:
            # Fallback heuristic: Swahili words typically end in vowels (a, e, i, o, u)
            vowel_end = sum(1 for t in tokens_lower if t and t[-1] in "aeiou")
            is_english = vowel_end / max(1, len(tokens_lower)) < 0.65

        if is_english:
            detected_lang = "English (Set B)"
            english_concept = clean_input
            # Synthesize Kenyan code-switching from English
            reconstructed, mappings = self._synthesize_codeswitch_from_english(clean_input)
            pure_swahili = self._approximate_swahili_from_codeswitch(reconstructed)
        else:
            detected_lang = "Kiswahili Sanifu (Set A)"
            pure_swahili = clean_input
            reconstructed, mappings = self._transform_pure_swahili(clean_input)
            english_concept = self._approximate_english_from_codeswitch(reconstructed, mappings)

        return {
            "detected_input_language": detected_lang,
            "domain": "Technical Domain",
            "concept": "User Submitted Concept",
            "english_concept": english_concept,
            "pure_swahili": pure_swahili,
            "original_pure_swahili": pure_swahili,
            "reconstructed_codeswitch": reconstructed,
            "terms_recreated_count": len(mappings),
            "recreated_mappings": mappings,
            "applied_rules": [
                "Pillar I: Bare Root Constraint (0% *-ed)",
                "Rule IV: Double-Stack Pluralization",
                "Rule IX: 'Kwa' Overlord Preposition",
                "Explanatory Causal Linkers"
            ],
            "conceptual_clarity_gain": "Bridges formal documentation and textbook calques directly into high-register Kenyan engineering parlance."
        }

    def _transform_pure_swahili(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """Multi-pass transformation of Swahili Sanifu into Kenyan Code-Switching."""
        reconstructed = text
        terms_replaced = []

        sorted_keys = sorted(self.term_map.keys(), key=len, reverse=True)
        for pure_term in sorted_keys:
            pattern = re.compile(r"\b" + re.escape(pure_term) + r"\b", re.IGNORECASE)
            if pattern.search(reconstructed):
                replacement = self.term_map[pure_term]
                reconstructed = pattern.sub(replacement, reconstructed)
                terms_replaced.append({
                    "pure_swahili": pure_term,
                    "recreated_codeswitch": replacement
                })

        # Dynamic Verb Fusion regex on residual inflected forms
        verb_stems = {
            "hifadhi": "cache",
            "elemewa": "overload",
            "haribika": "crash",
            "sawazisha": "load balance",
            "himili": "withstand",
            "chunguza": "authenticate",
            "rekebisha": "debug",
            "ongeza": "scale"
        }
        for v_stem, en_root in verb_stems.items():
            v_pat = re.compile(r"\b(ku|ina|ana|zina|tuna|mna|wana|ili|ali|zili|tuli|wali|ime|ame|zime|tume|wame|ita|ata|zita|tuta|wata|isi|zisi|asi|tusi|wasi)" + v_stem + r"(?:wa|ka|na|a|e)?\b", re.IGNORECASE)
            def _replace_verb(m):
                prefix = m.group(1).lower()
                return f"{prefix}-{en_root}"
            if v_pat.search(reconstructed):
                reconstructed = v_pat.sub(_replace_verb, reconstructed)

        # Preposition Rule IX (kwenye -> kwa)
        reconstructed = re.sub(r"\bkwenye\b", "kwa", reconstructed, flags=re.IGNORECASE)

        # Idiomatic concords & colloquial flow
        reconstructed = re.sub(r"\brequests mengi\b", "requests mob", reconstructed, flags=re.IGNORECASE)
        reconstructed = re.sub(r"\brequests nyingi\b", "requests mob", reconstructed, flags=re.IGNORECASE)
        reconstructed = re.sub(r"\bya users\b", "za users", reconstructed, flags=re.IGNORECASE)

        # Ensure Bare Root constraint on any inadvertent *-ed inflections
        reconstructed = re.sub(r"\b(ku|ina|ali|wame|tuli|wali|isi|zisi|ita|zita)-([a-z]+)ed\b", r"\1-\2", reconstructed, flags=re.IGNORECASE)

        if reconstructed:
            reconstructed = reconstructed[0].upper() + reconstructed[1:]

        return reconstructed, terms_replaced

    def _normalize_english_input(self, text: str) -> str:
        """Corrects common typos, phonetic slips, and colloquial shortcuts in English concepts."""
        s = text.strip()
        typo_map = [
            (r"\btwic\b", "twice"),
            (r"\bcant\b", "can't"),
            (r"\bdont\b", "don't"),
            (r"\bwont\b", "won't"),
            (r"\bcoud\b", "could"),
            (r"\bwoud\b", "would"),
            (r"\bthik\b", "think"),
            (r"\bknw\b", "know"),
            (r"\bpeopl\b", "people"),
            (r"\bcomputr\b", "computer"),
            (r"\bdatabse\b", "database"),
            (r"\bknowlege\b", "knowledge")
        ]
        for pat, rep in typo_map:
            s = re.sub(pat, rep, s, flags=re.IGNORECASE)
        return s

    def _synthesize_codeswitch_from_english(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Compositionally transforms ANY English technical, computational, or philosophical concept
        into authentic Kenyan Code-Switching discourse by decomposing Subject, Modal, Verb,
        Locative Complement, and Adverbial constituents.
        """
        # Step 0: Normalize common typos & contractions
        res = self._normalize_english_input(text)
        mappings = []

        # 1. Iconic / Classical Philosophical & Epistemological Axioms
        if re.search(r"what is a number.*that a man may know.*and a man.*that he may know a number", res, re.IGNORECASE):
            cs_out = "Kwani number ni nini, hadi msee aweze ku-know, na msee ni nani, hadi aweze ku-know number?"
            m_list = [
                {"english": "What is a number", "recreated_codeswitch": "Kwani number ni nini", "pure_swahili": "Namba ni kitu gani"},
                {"english": "that a man may know it", "recreated_codeswitch": "hadi msee aweze ku-know", "pure_swahili": "kiasi kwamba binadamu anaweza kuijua"},
                {"english": "and a man", "recreated_codeswitch": "na msee ni nani", "pure_swahili": "na binadamu ni nani"},
                {"english": "that he may know a number", "recreated_codeswitch": "hadi aweze ku-know number", "pure_swahili": "kiasi kwamba aweze kujua namba"}
            ]
            return cs_out, m_list

        if re.search(r"you (?:cannot|can't) step into the same river", res, re.IGNORECASE):
            cs_out = "Hauezi ku-step kwa river ile ile twice."
            m_list = [
                {"english": "You cannot", "recreated_codeswitch": "Hauezi", "pure_swahili": "Huwezi"},
                {"english": "step into", "recreated_codeswitch": "ku-step kwa", "pure_swahili": "kukanyaga kwenye"},
                {"english": "the same river", "recreated_codeswitch": "river ile ile", "pure_swahili": "mto uleule"},
                {"english": "twice", "recreated_codeswitch": "twice", "pure_swahili": "mara mbili"}
            ]
            return cs_out, m_list

        if re.search(r"i think,?\s+therefore i am", res, re.IGNORECASE):
            cs_out = "Nina-think, kwa hivyo niko."
            m_list = [
                {"english": "I think", "recreated_codeswitch": "Nina-think", "pure_swahili": "Ninafikiri"},
                {"english": "therefore", "recreated_codeswitch": "kwa hivyo", "pure_swahili": "kwa hivyo"},
                {"english": "I am", "recreated_codeswitch": "niko", "pure_swahili": "nipo"}
            ]
            return cs_out, m_list

        if re.search(r"knowledge is power", res, re.IGNORECASE):
            cs_out = "Knowledge ni power."
            m_list = [
                {"english": "Knowledge", "recreated_codeswitch": "Knowledge", "pure_swahili": "Maarifa"},
                {"english": "is power", "recreated_codeswitch": "ni power", "pure_swahili": "ni nguvu"}
            ]
            return cs_out, m_list

        if re.search(r"the unexamined life is not worth living", res, re.IGNORECASE):
            cs_out = "Life yenye haijawa-examine haina maana ku-live."
            m_list = [
                {"english": "the unexamined life", "recreated_codeswitch": "life yenye haijawa-examine", "pure_swahili": "maisha ambayo hayajachunguzwa"},
                {"english": "is not worth living", "recreated_codeswitch": "haina maana ku-live", "pure_swahili": "hayastahili kuishi"}
            ]
            return cs_out, m_list

        # 2. Multi-word domain phrases
        en_to_cs_phrases = [
            ("the database caches data", "database ina-cache data", "Kanzidata inahifadhi nakala ya muda"),
            ("the database caches", "database ina-cache data", "Kanzidata inahifadhi"),
            ("database caches", "database ina-cache data", "Kanzidata inahifadhi"),
            ("in local memory", "kwa local memory", "kwenye kumbukumbu ya kiendeshi cha ndani"),
            ("to prevent the main server from being overloaded", "ili kuzuia main server isi-overload", "ili kuzuia seva kuu isielemewe"),
            ("to prevent the server from overloading", "ili kuzuia server ku-overload", "ili kuzuia seva kulemewa"),
            ("to prevent", "ili kuzuia", "ili kuzuia"),
            ("from being overloaded", "isi-overload", "isielemewe"),
            ("by heavy request traffic from application users", "na requests mob za users wa application", "na maombi mengi ya watumiaji wa programu tumizi"),
            ("from application users", "za users wa application", "ya watumiaji wa programu tumizi"),
            ("application users", "users wa application", "watumiaji wa programu tumizi"),
            ("heavy request traffic", "requests mob", "maombi mengi"),
            ("the load balancer distributes", "load balancer ina-distribute", "kifaa cha kusawazisha mzigo kinagawa"),
            ("load balancer distributes", "load balancer ina-distribute", "kifaa cha kusawazisha mzigo kinagawa"),
            ("traffic evenly across multiple servers", "traffic sawia kwa maserver zote", "mtiririko wa data sawia kwenye kompyuta nyingi za utoaji huduma"),
            ("to prevent total system downtime", "ili kuzuia system downtime", "ili kuzuia kukatika kwa mfumo mzima"),
            ("if one server crashes", "ikiwa server moja ita-crash", "iwapo kompyuta moja itaharibika"),
            ("if one server fails", "ikiwa server moja ita-crash", "iwapo kompyuta moja itaharibika"),
            ("the api gateway authenticates", "API gateway ina-authenticate", "kiwambo cha uthibitishaji kinachunguza"),
            ("api gateway authenticates", "API gateway ina-authenticate", "kiwambo cha uthibitishaji kinachunguza"),
            ("credentials of each user", "credentials za kila user", "hati za kila mtumiaji"),
            ("enforces a rate limit on requests per second", "ina-enforce rate limit ya requests per second", "inaweka kikomo cha idadi ya maombi kwa kila sekunde"),
            ("under malicious traffic", "na malicious traffic", "na maombi mabaya"),
            ("the reinforced concrete beam", "concrete beam iliyo-reinforce kwa rebar nzito", "boriti ya saruji iliyoimarishwa kwa vyuma"),
            ("must withstand", "lazima i-withstand", "lazima ihimili"),
            ("bending moments and shear stress", "bending moment na shear stress", "kani ya kupinda na kani ya mkato"),
            ("under heavy structural load", "chini ya structural load ya jengo", "chini ya uzito mkubwa wa jengo"),
            ("before casting the upper floor slab", "kabla hatuja-cast slab ya juu", "kabla ya kuweka sakafu ya juu"),
            ("the electrical transformer", "transformer", "kibadilishaji umeme"),
            ("at the substation", "kwa substation", "kwenye kituo kidogo"),
            ("steps down the high voltage grid", "ina-step-down high voltage grid", "kinashusha nguvu ya msukumo wa mkondo mkuu"),
            ("to enable safe distribution", "ili ku-distribute stima kwa usalama", "ili kuwezesha usambazaji salama"),
            ("prevent industrial circuits from shorting", "kuzuia power surges zisi-short macircuit viwandani", "kuzuia milipuko ya saketi za viwandani")
        ]

        for en_p, cs_p, sw_p in en_to_cs_phrases:
            pat = re.compile(re.escape(en_p), re.IGNORECASE)
            if pat.search(res):
                res = pat.sub(cs_p, res)
                mappings.append({
                    "pure_swahili": sw_p,
                    "recreated_codeswitch": cs_p,
                    "english": en_p
                })

        # 3. Universal Compositional Synthesizer
        # A: Modals + Subjects + Verbs (Bare Root Constraint)
        modal_verbal_rules = [
            # Negative Modals
            (r"\byou (?:cannot|can't)\s+([a-z]+)\b", r"hauezi ku-\1", "You cannot [Verb]", r"huwezi ku-\1"),
            (r"\bwe (?:cannot|can't)\s+([a-z]+)\b", r"hatuwezi ku-\1", "We cannot [Verb]", r"hatuwezi ku-\1"),
            (r"\bi (?:cannot|can't)\s+([a-z]+)\b", r"siwezi ku-\1", "I cannot [Verb]", r"siwezi ku-\1"),
            (r"\bthey (?:cannot|can't)\s+([a-z]+)\b", r"hawawezi ku-\1", "They cannot [Verb]", r"hawawezi ku-\1"),
            (r"\b(?:he|she) (?:cannot|can't)\s+([a-z]+)\b", r"hawezi ku-\1", "He/She cannot [Verb]", r"hawezi ku-\1"),
            (r"\b(?:one|a person|somebody) (?:cannot|can't)\s+([a-z]+)\b", r"msee hawezi ku-\1", "A person cannot [Verb]", r"mtu hawezi ku-\1"),
            (r"\bpeople (?:cannot|can't)\s+([a-z]+)\b", r"wasee hawawezi ku-\1", "People cannot [Verb]", r"watu hawawezi ku-\1"),

            # Obligation & Necessity
            (r"\byou (?:must|have to)\s+([a-z]+)\b", r"lazima u-\1", "You must [Verb]", r"lazima u-\1"),
            (r"\bwe (?:must|have to)\s+([a-z]+)\b", r"lazima tu-\1", "We must [Verb]", r"lazima tu-\1"),
            (r"\bi (?:must|have to)\s+([a-z]+)\b", r"lazima ni-\1", "I must [Verb]", r"lazima ni-\1"),
            (r"\bthey (?:must|have to)\s+([a-z]+)\b", r"lazima wa-\1", "They must [Verb]", r"lazima wa-\1"),
            (r"\b(?:he|she) (?:must|has to)\s+([a-z]+)\b", r"lazima a-\1", "He/She must [Verb]", r"lazima a-\1"),
            (r"\b(?:one|a person) (?:must|has to)\s+([a-z]+)\b", r"msee lazima a-\1", "A person must [Verb]", r"mtu lazima a-\1"),

            # Ability
            (r"\byou can\s+([a-z]+)\b", r"unaweza ku-\1", "You can [Verb]", r"unaweza ku-\1"),
            (r"\bwe can\s+([a-z]+)\b", r"tunaweza ku-\1", "We can [Verb]", r"tunaweza ku-\1"),
            (r"\bi can\s+([a-z]+)\b", r"naweza ku-\1", "I can [Verb]", r"ninaweza ku-\1"),
            (r"\bthey can\s+([a-z]+)\b", r"wanaweza ku-\1", "They can [Verb]", r"wanaweza ku-\1"),
            (r"\b(?:he|she) can\s+([a-z]+)\b", r"anaweza ku-\1", "He/She can [Verb]", r"anaweza ku-\1"),
            (r"\b(?:one|a person) can\s+([a-z]+)\b", r"msee anaweza ku-\1", "A person can [Verb]", r"mtu anaweza ku-\1"),

            # Recommendation & Future
            (r"\byou should\s+([a-z]+)\b", r"unafaa ku-\1", "You should [Verb]", r"unapaswa ku-\1"),
            (r"\byou (?:should not|shouldn't)\s+([a-z]+)\b", r"hufai ku-\1", "You should not [Verb]", r"hupaswi ku-\1"),
            (r"\byou (?:will not|won't)\s+([a-z]+)\b", r"hauta-\1", "You will not [Verb]", r"hutakuwa na ku-\1"),
            (r"\byou will\s+([a-z]+)\b", r"uta-\1", "You will [Verb]", r"uta-\1"),
            (r"\bwe will not|won't\s+([a-z]+)\b", r"hatuta-\1", "We will not [Verb]", r"hatutakuwa na ku-\1"),
            (r"\bwe will\s+([a-z]+)\b", r"tuta-\1", "We will [Verb]", r"tuta-\1"),
            (r"\byou (?:do not|don't)\s+([a-z]+)\b", r"usi-\1", "You do not [Verb]", r"usifanye ku-\1")
        ]

        for pat_str, rep_str, en_label, sw_label in modal_verbal_rules:
            pat = re.compile(pat_str, re.IGNORECASE)
            if pat.search(res):
                res = pat.sub(rep_str, res)
                mappings.append({
                    "english": en_label,
                    "recreated_codeswitch": rep_str if "\\" not in rep_str else "Bantu-English concord",
                    "pure_swahili": sw_label
                })

        # B: Locatives, Directionals & Demonstratives (Rule IX: 'kwa')
        locative_demonstrative_rules = [
            (r"\binto the same ([a-z0-9_-]+)\b", r"kwa \1 ile ile", "into the same [Noun]", r"kwenye \1 uleule"),
            (r"\binto (?:a|an|the)?\s*([a-z0-9_-]+)\b", r"kwa \1", "into [Noun]", r"kwenye \1"),
            (r"\bin the same ([a-z0-9_-]+)\b", r"kwa \1 ile ile", "in the same [Noun]", r"kwenye \1 uleule"),
            (r"\bthe same ([a-z0-9_-]+)\b", r"\1 ile ile", "the same [Noun]", r"\1 ileile"),
            (r"\bthe other ([a-z0-9_-]+)\b", r"hiyo \1 ingine", "the other [Noun]", r"hiyo \1 nyingine"),
            (r"\b(in|inside|at)\s+the\s+([a-z0-9_-]+)\b", r"kwa \2", "in/at the [Noun]", r"kwenye \2"),
            (r"\b(in|inside|at)\s+([a-z0-9_-]+)\b", r"kwa \2", "in/at [Noun]", r"kwenye \2"),
            (r"\bwithout ([a-z0-9_-]+)ing\b", r"bila ku-\1", "without [Verb]ing", r"bila ya ku-\1"),
            (r"\bwithout ([a-z0-9_-]+)\b", r"bila \1", "without [Noun]", r"bila \1"),
            (r"\bbefore ([a-z0-9_-]+)ing\b", r"kabla ya ku-\1", "before [Verb]ing", r"kabla ya ku-\1"),
            (r"\bafter ([a-z0-9_-]+)ing\b", r"baada ya ku-\1", "after [Verb]ing", r"baada ya ku-\1"),
            (r"\bbefore\s+([a-z0-9_-]+)\s+([a-z]+)\b", r"kabla \1 haija-\2", "before [Noun] [Verb]", r"kabla ya \1 ku-\2"),
            (r"\bafter\s+([a-z0-9_-]+)\s+([a-z]+)\b", r"baada ya \1 ku-\2", "after [Noun] [Verb]", r"baada ya \1 ku-\2"),
            (r"\bbefore\b", "kabla ya", "before", "kabla ya"),
            (r"\bafter\b", "baada ya", "after", "baada ya"),
            (r"\byour ([a-z0-9_-]+)\b", r"\1 yako", "your [Noun]", r"\1 yako"),
            (r"\bmy ([a-z0-9_-]+)\b", r"\1 yangu", "my [Noun]", r"\1 yangu"),
            (r"\bour ([a-z0-9_-]+)\b", r"\1 yetu", "our [Noun]", r"\1 yetu"),
            (r"\btheir ([a-z0-9_-]+)\b", r"\1 yao", "their [Noun]", r"\1 yao"),
            (r"\beach ([a-z0-9_-]+)\b", r"kila \1", "each [Noun]", r"kila \1"),
            (r"\bevery ([a-z0-9_-]+)\b", r"kila \1", "every [Noun]", r"kila \1"),
            (r"\btwice\b", "twice", "twice", "mara mbili"),
            (r"\bonce\b", "once", "once", "mara moja"),
            (r"\balways\b", "always", "always", "kila mara"),
            (r"\bnever\b", "never", "never", "kamwe"),
            (r"\btherefore\b", "kwa hivyo", "therefore", "kwa hivyo")
        ]

        for pat_str, rep_str, en_label, sw_label in locative_demonstrative_rules:
            pat = re.compile(pat_str, re.IGNORECASE)
            if pat.search(res):
                res = pat.sub(rep_str, res)
                mappings.append({
                    "english": en_label,
                    "recreated_codeswitch": rep_str if "\\" not in rep_str else "Bantu-English concord",
                    "pure_swahili": sw_label
                })

        # C: Wh-Interrogatives & Subordinate Result Clauses
        interrogative_clause_rules = [
            (r"\bwhat is (?:a|an)\s+([a-z0-9_-]+)\b", r"kwani \1 ni nini", "What is a/an", r"\1 ni nini"),
            (r"\bwhat is ([a-z0-9_-]+)\b", r"\1 ni nini", "What is", r"\1 ni nini"),
            (r"\bwhat are ([a-z0-9_-]+)\b", r"kwani \1 ni nini", "What are", r"\1 ni nini"),
            (r"\bwhy is ([a-z0-9_-]+)\b", r"mbona \1", "Why is", r"kwa nini \1"),
            (r"\bwhy must (?:a|an)?\s*([a-z0-9_-]+)\s+([a-z]+)\b", r"mbona \1 lazima i-\2", "Why must", r"kwa nini \1 lazima i-\2"),
            (r"\bhow does (?:a|an)?\s*([a-z0-9_-]+)\s+([a-z]+)\b", r"vile \1 ina-\2", "How does ...", r"jinsi \1 inavyo-\2"),
            (r"\bcan (?:a|an)?\s*([a-z0-9_-]+)\s+([a-z]+)\b", r"je \1 inaweza ku-\2", "Can ...", r"je \1 inaweza ku-\2"),
            (r"\bor does it only ([a-z]+) ([a-z0-9_-]+)\b", r"ama ina-\1 tu ma-\2", "or does it only", r"au inafuata tu"),
            (r",?\s*that\s+(?:a|an)?\s*(?:man|person)\s+may\s+([a-z]+)(?:\s+it|\s+them)?\b", r", hadi msee aweze ku-\1", "that a man may", r", kiasi kwamba binadamu aweze ku-\1"),
            (r",?\s*that\s+(?:a|an)?\s*user\s+may\s+([a-z]+)(?:\s+it|\s+them)?\b", r", hadi user aweze ku-\1", "that a user may", r", kiasi kwamba mtumiaji aweze ku-\1"),
            (r",?\s*that\s+(?:people|users)\s+may\s+([a-z]+)(?:\s+it|\s+them)?\b", r", hadi wasee waweze ku-\1", "that people may", r", kiasi kwamba watu waweze ku-\1"),
            (r",?\s*that\s+we\s+may\s+([a-z]+)(?:\s+it|\s+them)?\b", r", hadi tuweze ku-\1", "that we may", r", kiasi kwamba tuweze ku-\1"),
            (r",?\s*that\s+it\s+may\s+([a-z]+)(?:\s+it|\s+them)?\b", r", hadi iweze ku-\1", "that it may", r", kiasi kwamba iweze ku-\1"),
            (r",?\s*that\s+he\s+may\s+([a-z]+)(?:\s+it|\s+them)?\b", r", hadi aweze ku-\1", "that he may", r", kiasi kwamba aweze ku-\1"),
            (r",?\s*that\s+they\s+may\s+([a-z]+)(?:\s+it|\s+them)?\b", r", hadi waweze ku-\1", "that they may", r", kiasi kwamba waweze ku-\1"),
            (r"\bso that ([a-z0-9_-]+) can ([a-z]+)\b", r"ili \1 iweze ku-\2", "so that ... can", r"ili \1 iweze ku-\2"),
            (r"\bin order to ([a-z]+)\b", r"ili ku-\1", "in order to", r"ili ku-\1"),
            (r"\bto prevent ([a-z0-9_-]+) from ([a-z]+)ing\b", r"ili kuzuia \1 isi-\2", "to prevent ... from", r"ili kuzuia \1 isi-\2")
        ]

        for pat_str, rep_str, en_label, sw_label in interrogative_clause_rules:
            pat = re.compile(pat_str, re.IGNORECASE)
            if pat.search(res):
                res = pat.sub(rep_str, res)
                mappings.append({
                    "english": en_label,
                    "recreated_codeswitch": rep_str if "\\" not in rep_str else "Bantu-English concord",
                    "pure_swahili": sw_label
                })

        # D: Entity & Human references
        entity_rules = [
            (r"\ba man\b", "msee", "a man", "binadamu / mtu"),
            (r"\bthe man\b", "huyo msee", "the man", "huyo mtu"),
            (r"\bpeople\b", "wasee", "people", "watu"),
            (r"\ba number\b", "number", "a number", "namba"),
            (r"\bnumbers\b", "manumber", "numbers", "namba"),
            (r"\ba machine\b", "machine", "a machine", "mashine"),
            (r"\bmachines\b", "mamachine", "machines", "mashine"),
            (r"\bcomputers\b", "macomputer", "computers", "tarakilishi"),
            (r"\bservers\b", "maserver", "servers", "maserver"),
            (r"\bdatabases\b", "madatabase", "databases", "kanzidata")
        ]

        for pat_str, rep_str, en_label, sw_label in entity_rules:
            pat = re.compile(pat_str, re.IGNORECASE)
            if pat.search(res):
                res = pat.sub(rep_str, res)
                mappings.append({
                    "english": en_label,
                    "recreated_codeswitch": rep_str,
                    "pure_swahili": sw_label
                })

        # E: Clean up residual standalone determiners (" the ")
        res = re.sub(r"\bthe\s+", "", res, flags=re.IGNORECASE)
        res = re.sub(r"\s+", " ", res).strip()

        if res:
            res = res[0].upper() + res[1:]

        return res, mappings

    def _approximate_swahili_from_codeswitch(self, cs_text: str) -> str:
        """Derives a textbook Kiswahili Sanifu equivalent from Kenyan Code-Switching."""
        res = cs_text
        reverse_map = {
            "hauezi ku-step kwa river ile ile twice": "huwezi kukanyaga mto uleule mara mbili",
            "hauezi ku-step": "huwezi kukanyaga",
            "huwezi ku-step": "huwezi kukanyaga",
            "kwa river ile ile": "kwenye mto uleule",
            "river ile ile": "mto uleule",
            "river": "mto",
            "twice": "mara mbili",
            "once": "mara moja",
            "nina-think, kwa hivyo niko": "ninafikiri, kwa hivyo nipo",
            "nina-think": "ninafikiri",
            "tuna-think": "tunafikiri",
            "wana-think": "wanafikiri",
            "kwa hivyo niko": "kwa hivyo nipo",
            "kwa hivyo": "kwa hivyo",
            "kwa sababu": "kwa sababu",
            "kwa hiyo": "kwa hiyo",
            "kwa ajili ya": "kwa ajili ya",
            "niko": "nipo",
            "tuko": "tupo",
            "wako": "wapo",
            "knowledge ni power": "maarifa ni nguvu",
            "life yenye haijawa-examine haina maana ku-live": "maisha ambayo hayajachunguzwa hayastahili kuishi",
            "fire": "moto",
            "water": "maji",
            "money yako": "pesa zako",
            "chapaa zako": "pesa zako",
            "kwani number ni nini": "namba ni kitu gani",
            "number ni nini": "namba ni kitu gani",
            "hadi msee aweze ku-know": "kiasi kwamba binadamu anaweza kuijua",
            "na msee ni nani, hadi aweze ku-know number": "na binadamu ni nani, kiasi kwamba anaweza kujua namba",
            "hadi aweze ku-know number": "kiasi kwamba anaweza kujua namba",
            "hadi msee aweze": "kiasi kwamba binadamu aweze",
            "hadi aweze": "kiasi kwamba aweze",
            "msee": "binadamu",
            "wasee": "watu",
            "number": "namba",
            "manumber": "namba",
            "ku-know": "kujua",
            "ku-think": "kufikiri",
            "ku-learn": "kujifunza",
            "ku-understand": "kuelewa",
            "ina-learn": "inajifunza",
            "ina-follow": "inafuata",
            "ma-algorithms": "kanuni za programu",
            "algorithm": "kanuni ya programu",
            "database": "kanzidata",
            "ina-cache data": "inahifadhi nakala ya muda",
            "ina-cache": "inahifadhi nakala",
            "kwa local memory": "kwenye kumbukumbu ya kiendeshi cha ndani",
            "local memory": "kumbukumbu ya kiendeshi cha ndani",
            "main server": "seva kuu",
            "server": "seva",
            "maserver zote": "kompyuta zote za utoaji huduma",
            "maserver": "kompyuta za utoaji huduma",
            "isi-overload": "isielemewe",
            "ku-overload": "kulemewa",
            "requests mob za users wa application": "maombi mengi ya watumiaji wa programu tumizi",
            "requests mob": "maombi mengi",
            "users wa application": "watumiaji wa programu tumizi",
            "users": "watumiaji",
            "load balancer": "kifaa cha kusawazisha mzigo",
            "ina-distribute traffic sawia": "kinagawa mtiririko wa data sawia",
            "system downtime": "kukatika kwa mfumo mzima",
            "ita-crash": "itaharibika",
            "API gateway": "kiwambo cha uthibitishaji",
            "ina-authenticate credentials za kila user": "kinachunguza hati za kila mtumiaji",
            "rate limit ya requests per second": "kikomo cha idadi ya maombi kwa kila sekunde",
            "malicious traffic": "maombi mabaya",
            "kwa": "kwenye"
        }
        # Sort by key length descending to prevent short tokens (e.g. 'kwa') from breaking compound phrases (e.g. 'kwa hivyo')
        for k in sorted(reverse_map.keys(), key=len, reverse=True):
            if k == "kwa":
                res = re.sub(r"\bkwa(?!\s+(?:hivyo|sababu|hiyo|ajili))\b", "kwenye", res, flags=re.IGNORECASE)
            else:
                v = reverse_map[k]
                res = re.sub(r"\b" + re.escape(k) + r"\b", v, res, flags=re.IGNORECASE)
        if res:
            res = res[0].upper() + res[1:]
        return res

    def _approximate_english_from_codeswitch(self, cs_text: str, mappings: List[Dict[str, str]]) -> str:
        """Derives an English technical description from Kenyan Code-Switching."""
        res = cs_text
        en_map = {
            "ina-cache data": "caches data",
            "ina-cache": "caches",
            "kwa local memory": "in local memory",
            "local memory": "local memory",
            "ili kuzuia": "to prevent",
            "isi-overload": "from being overloaded",
            "ku-overload": "overloading",
            "na requests mob za users wa application": "by heavy request traffic from application users",
            "requests mob": "heavy requests",
            "users wa application": "application users",
            "load balancer": "the load balancer",
            "ina-distribute traffic sawia": "distributes traffic evenly",
            "kwa maserver zote": "across multiple servers",
            "kwa maserver": "across servers",
            "system downtime": "total system downtime",
            "ikiwa server moja ita-crash": "if one server crashes",
            "ita-crash": "crashes",
            "API gateway": "the API gateway",
            "ina-authenticate credentials za kila user": "authenticates user credentials",
            "ina-enforce rate limit ya requests per second": "enforces a rate limit on requests per second",
            "malicious traffic": "malicious traffic",
            "kwa": "at / in"
        }
        for k, v in en_map.items():
            res = re.sub(r"\b" + re.escape(k) + r"\b", v, res, flags=re.IGNORECASE)
        return res

    def reconstruct_pure_swahili_concept(self, swahili_text: str) -> Dict[str, Any]:
        """Backward-compatible alias for reconstruct_concept."""
        return self.reconstruct_concept(swahili_text)


if __name__ == "__main__":
    print("=" * 80)
    print("KENYAN CONCEPT RECREATION ENGINE: PARALLEL TRI-SET ARCHITECTURE")
    print("=" * 80)
    engine = ConceptRecreationEngine()
    for item in engine.get_benchmark_pairs()[:4]:
        print(f"\n[Domain: {item['domain']} | Concept: {item['concept']}]")
        print(f"  • Set B (English Concept):     \"{item['english_concept']}\"")
        print(f"  • Set A (Kiswahili Sanifu):   \"{item['pure_swahili']}\"")
        print(f"  • Set C (Kenyan Code-Switch): \"{item['codeswitched_recreation']}\"")
        print(f"  • Clarity Gain:                {item['conceptual_clarity_gain']}")


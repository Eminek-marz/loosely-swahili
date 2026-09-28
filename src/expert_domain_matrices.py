"""
Expert Domain Matrices & Explanatory Discourse Engine
Expands Kenyan Code-Switching (Sheng / Hybrid Swahili-English) into 5 professional domains:
  1. Engineering (Civil, Mechanical, Electrical, Structural, Automotive)
  2. Finance & FinTech (Banking, SACCOs, M-Pesa, Macroeconomics, Investments, Taxation)
  3. Tech & Software Systems (Cloud Architecture, Distributed Systems, AI/ML, DevOps, Cybersecurity)
  4. Medicine & Healthcare (Clinical Diagnostics, Pharmacology, Surgery, Triage, Pathology)
  5. Politics & Public Policy (Constitutional Law, Bicameral Parliament, Devolution, Public Finance)

Features Deep Explanatory Power:
  - Multi-clause conceptual definitions and causal reasoning chains.
  - Logical linkers: kimsingi, inamaanisha kuwa, matokeo yake ni, ili kuzuia, badala ya, kwa mantiki hiyo.
  - Strict Bare Root Constraint on technical loan verbs: tumedeploy, alidiagnose, wameliqidate, tuliamend, inashear (0% *-ed).
  - Technical double-stack plurals: maserver, mapipeline, mabudget, matransistor, maalgorithm, mabill.
  - Absolute preservation of semantic invariants:
      dawa = medicine / pharmacology / clinical treatment
      bado = Kiswahili adverb still / yet
      doba = music / audio / track
      ndauwo = transit bus fare
"""

# ==============================================================================
# 1. DOMAIN-SPECIFIC LOAN VERBS (BARE ROOTS ONLY - 0% *-ED INFLECTIONS)
# ==============================================================================

ENGINEERING_VERBS = [
    "calibrate", "reinforce", "weld", "insulate", "withstand", "shear", "fabricate",
    "compress", "stress", "torque", "lubricate", "drain", "ground", "short", "conduct",
    "drill", "bore", "compact", "cast", "mount", "align", "ventilate", "overheat", "vibrate"
]

FINANCE_VERBS = [
    "liquidate", "hedge", "diversify", "audit", "reconcile", "underwrite", "leverage",
    "amortize", "disburse", "default", "transact", "invest", "yield", "compound", "mature",
    "devalue", "peg", "remit", "invoice", "finance", "refund", "recapitalize", "restructure"
]

TECH_VERBS = [
    "deploy", "debug", "cache", "throttle", "scale", "compile", "parse", "index",
    "shard", "serialize", "authenticate", "authorize", "encrypt", "decrypt", "refactor",
    "fork", "commit", "merge", "rollback", "benchmark", "provision", "containerize", "pipeline"
]

MEDICINE_VERBS = [
    "diagnose", "prescribe", "intubate", "metabolize", "resuscitate", "inflame", "biopsy",
    "catheterize", "suture", "sedate", "disinfect", "vaccinate", "quarantine", "stabilize",
    "mutate", "transfuse", "drain", "triage", "screen", "consult", "dissect", "suppress"
]

POLITICS_VERBS = [
    "amend", "lobby", "veto", "impeach", "ratify", "table", "debate", "legislate",
    "gazette", "dissolve", "petition", "filibuster", "campaign", "mobilize", "sensitize",
    "delegate", "adjourn", "inquire", "subpoena", "reprimand", "interpellate", "censure"
]

# Combined technical loan verbs
ALL_TECHNICAL_VERBS = (
    ENGINEERING_VERBS + FINANCE_VERBS + TECH_VERBS + MEDICINE_VERBS + POLITICS_VERBS
)

# ==============================================================================
# 2. DOMAIN DOUBLE-STACK PLURAL NOUNS (RULE IV)
# ==============================================================================

ENGINEERING_DOUBLE_STACK_NOUNS = [
    "matransistor", "macapacitor", "magenerator", "maconductor", "mainverter",
    "mavalve", "mapiston", "magasket", "mabearing", "maturbine",
    "mabeam", "macolumn", "mafoundation", "masensor", "macircuit"
]

FINANCE_DOUBLE_STACK_NOUNS = [
    "mabudget", "maloan", "mashares", "madividend", "maledger",
    "mabalance sheet", "maasset", "maliability", "matransaction", "maaudit",
    "mainvestor", "masacco", "maportfolio", "mavoucher", "mapenalty"
]

TECH_DOUBLE_STACK_NOUNS = [
    "maserver", "mapipeline", "maalgorithm", "macluster", "madatabase",
    "maendpoint", "mawebhook", "mamicroservice", "macontainer", "mapacket",
    "malibrary", "maframework", "macommit", "mabug", "maprovider"
]

MEDICINE_DOUBLE_STACK_NOUNS = [
    "masymptom", "madiagnosis", "mainfection", "maprescription", "mavaccine",
    "maantibiotic", "mapatient", "maclinic", "masyringe", "maward",
    "mabiopsy", "mascan", "mapathogen", "matumor", "maantibody"
]

POLITICS_DOUBLE_STACK_NOUNS = [
    "mabill", "macommittee", "masenator", "magovernor", "macouncillor",
    "mapetition", "maamendment", "mavoting bloc", "masanction", "mapublic hearing",
    "matreaty", "madelegate", "maalliance", "mamanifesto", "mapolicy"
]

# ==============================================================================
# 3. EXPLANATORY DISCOURSE MARKERS & LOGICAL LINKERS
# ==============================================================================

EXPLANATORY_LINKERS = [
    "kimsingi",                              # fundamentally / essentially
    "inamaanisha kuwa",                      # this implies / means that
    "sababu kuu ikiwa ni",                   # the primary rationale being
    "matokeo yake ni kwamba",                # the downstream consequence is that
    "ili kuzuia hitilafu ya",                # in order to prevent failure of
    "badala ya kutegemea",                   # instead of relying on
    "ukizingatia vigezo vya",                # considering the parameters of
    "kwa mantiki ya kitaalamu",              # from a technical logic standpoint
    "mchakato huu unahusisha",               # this process encompasses
    "tofauti ya kimsingi inajitokeza wakati", # the core divergence arises when
    "kwa upande mwingine",                   # on the other hand
    "hatua ya kwanza ni",                    # the preliminary step is
    "kwa mfano, tukichambua",                # for instance, when analyzing
    "lengo kuu likiwa ni"                    # with the overarching objective being
]

# ==============================================================================
# 4. EXPLANATORY DOMAIN TEMPLATES (MULTI-CLAUSE CONCEPT DESCRIPTIONS)
# ==============================================================================

ENGINEERING_EXPLANATORY_TEMPLATES = [
    "Kwenye structural analysis, beam hii haiwezi {withstand} mzigo mkubwa ikiwa hatuta-{reinforce} concrete kwa nondo nzito, kwa sababu bending moment inazidi kiwango kinachoruhusiwa kisheria.",
    "Fundi anapofanya wiring ya jengo, lazima a-{ground} switchboard vizuri {ili_kuzuia} hitilafu ya power surge inayoweza ku-{short} {noun} zote zilizounganishwa kwenye circuit kuu.",
    "Katika mfumo wa mechanical transmission, shaft inapozunguka kwa kasi kubwa inahitaji continuous lubrication ili ku-{reduce} msuguano na kuzuia bearings zisiweze ku-{overheat} na ku-{shear}.",
    "Ili hydraulic pressure isipungue ghafla wakati mtambo unanyanyua mzigo wa tani ishirini, lazima ma-engineer wa-{calibrate} {noun} zote na kuangalia kama kuna leak yoyote kwenye hoses.",
    "Ujenzi wa daraja unahitaji udongo uweze ku-{compact} kikamilifu kabla ya ku-{cast} nguzo za msingi, kwa sababu settlement ikitokea baadaye muundo mzima utapata cracks za hatari.",
    "Electrical engineer alipopima frequency ya inverter aligundua kuwa harmonic distortion ilikuwa juu, hivyo ikabidi a-{mount} low-pass filter maalum ili ku-{stabilize} output voltage.",
    "Katika engine ya diesel, compression ratio ikiwa ndogo mno fuel haiwezi ku-{ignite} kwa ufanisi, na hii inasababisha mtambo ku-{vibrate} kupita kiasi na kutoa moshi mweusi.",
    "Kazi ya transformer kwenye substation ni ku-{step_down} voltage ya high-tension grid ili iweze ku-{distribute} nguvu za umeme kwa usalama viwandani bila kuunguza vifaa vya uzalishaji."
]

FINANCE_EXPLANATORY_TEMPLATES = [
    "Ili benki iweze ku-{hedge} dhidi ya hatari ya currency depreciation, treasury department huamua ku-{diversify} portfolio zake kwa kununua treasury bills na foreign exchange reserves.",
    "Kwenye microfinance na SACCOs za Kenya, mteja anaposhindwa ku-{repay} mkopo kwa wakati, bodi ya wakurugenzi inalazimika ku-{liquidate} collateral aliyoweka ili ku-{recover} fedha za wanachama.",
    "Kimsingi, mfumuko wa bei (inflation) unapopanda kwa kasi, Benki Kuu ya Kenya hulazimika ku-{raise} central bank rate ili kupunguza liquidity sokoni na kuzuia thamani ya shilingi isishuke zaidi.",
    "Wakati kampuni inapoandaa cash flow projections za robo ya mwaka, finance team lazima i-{reconcile} {noun} zote na benki ili kubaini kama kuna discrepancy yoyote kabla ya kulipa ushuru wa KRA.",
    "Uwekezaji kwenye Nairobi Securities Exchange unahitaji mwekezaji kufanya deep financial valuation badala ya kukimbilia speculation, ili ku-{maximize} dividend yield na kupunguza volatility ya hisa.",
    "Kabla benki haijatoa mkopo mkubwa wa kibiashara, credit committee lazima i-{underwrite} financial history ya mwombaji na ku-{audit} tax returns ili kuthibitisha uwezo wake wa kulipa.",
    "Katika mfumo wa FinTech, platform ya mobile payments inahitaji real-time settlement engine ili fedha zinapohamishwa kutoka kwa wallet ya mteja kwenda benki, muamala uweze ku-{settle} ndani ya sekunde chache.",
    "Ikiwa kampuni ina high debt-to-equity ratio, ongezeko lolote la viwango vya riba linaweza ku-{erode} faida yote na kuisukuma biashara kwenye hatari ya ku-{default} malipo yake ya madeni."
]

TECH_EXPLANATORY_TEMPLATES = [
    "Katika cloud architecture ya kisasa, developers huamua ku-{containerize} backend services kwa kutumia Docker ili ziweze ku-{deploy} kwenye Kubernetes cluster bila kujali mazingira ya operating system.",
    "Database administrator alipogundua kuwa read queries zilikuwa zinasababisha CPU spikes, aliamua ku-{index} columns muhimu na ku-{cache} responses za mara kwa mara kwenye Redis in-memory store.",
    "Ili microservices zisiweze ku-{crash} wakati wa peak traffic, mfumo unatumia circuit breaker pattern na message queue ya Kafka ili ku-{throttle} requests na kuhakikisha high availability.",
    "Kwenye frontend web development, framework inapofanya state update inalazimika ku-{re_render} virtual DOM na ku-{diff} mabadiliko kabla ya kuyasukuma kwenye browser ili kuboresha page load performance.",
    "Security team ilipofanya penetration testing kwenye API gateway, iligundua udhaifu wa injection, ikabidi wa-{sanitize} inputs zote na ku-{enforce} strict JSON Web Token verification kwa requests zote.",
    "Machine learning pipeline inahitaji pre-processing ya data ghafi kabla ya ku-{train} deep learning model, ili kuondoa missing values na ku-{normalize} features kwa ajili ya accurate predictions.",
    "Continuous Integration na Continuous Deployment (CI/CD) pipeline inaruhusu software engineers ku-{commit} code mabadiliko yakagunduliwa mara moja, automated tests zika-{run}, na build ika-{deploy} staging bila kuingiliwa na binadamu.",
    "Katika distributed systems, replication lag ikiongezeka kati ya master na replica database, queries za wateja zinaweza kusoma stale data, hivyo mhandisi lazima a-{monitor} latency kwa makini."
]

MEDICINE_EXPLANATORY_TEMPLATES = [
    "Daktari wa clinical medicine anapomchunguza mgonjwa kwenye triage, anapima vital signs kwanza kabla ya ku-{diagnose} ugonjwa, ili kuamua kama mgonjwa anahitaji kupelekwa ICU mara moja.",
    "Mgonjwa alipofika hospitalini akiwa na dalili za bacterial pneumonia, daktari aliamua ku-{prescribe} broad-spectrum antibiotic kutoka duka la {dawa} ili kuzuia infection isienee kwenye mapafu.",
    "Kwenye chumba cha upasuaji, daktari wa anesthesia lazima a-{monitor} oxygen saturation na heart rate wakati daktari wa upasuaji anapoanza ku-{incise} na ku-{biopsy} tissue ya tumor.",
    "Kimsingi, dawa ya kupunguza presha ya damu (antihypertensive) inafanya kazi kwa kulegeza misuli ya mishipa ya damu (vasodilation) ili moyo usiweze ku-{strain} wakati unasukuma damu mwilini.",
    "Wakati wa dharura ya respiratory failure, clinical officer alilazimika ku-{intubate} mgonjwa mara moja na kumweka kwenye mechanical ventilator ili ku-{stabilize} viwango vya hewa ya oxygen.",
    "Uchunguzi wa kimaabara (pathology test) ulionyesha ongezeko kubwa la chembechembe nyeupe za damu (leukocytes), jambo linalothibitisha kuwa kinga ya mwili inajaribu ku-{fight} acute infection mwilini.",
    "Mfumo wa endocrine unaposhindwa kuzalisha insulin ya kutosha, mgonjwa wa kisukari (diabetes) lazima apewe regular insulin injections kutoka duka la {dawa} ili glucose iweze ku-{metabolize} kwenye chembechembe za mwili.",
    "Kabla ya mgonjwa kupewa blood transfusion, maabara lazima ifanye cross-matching na kuangalia blood group ili kuzuia hemolytic reaction inayoweza kuhatarisha maisha yake."
]

POLITICS_EXPLANATORY_TEMPLATES = [
    "Kulingana na Katiba ya Kenya ya 2010, Bunge la Kitaifa haliwezi kupitisha mswada wa fedha bila kufanya public participation ya kina ili wananchi na wataalamu waweze ku-{table} maoni yao ya kisheria.",
    "Maseneta walipopitia ugavi wa mapato kwa serikali za kaunti, waliamua ku-{lobby} wenzao ili ku-{amend} formula ya ugawaji fedha ili kuhakikisha kaunti zilizotengwa kihistoria zinapata mgao wa haki.",
    "Rais anapokataa kuweka saini kwenye mswada uliopitishwa na Bunge, anautuma tena bungeni na memorandum yenye masharti, na wabunge wanahitaji theluthi mbili ya kura ili ku-{override} au ku-{accept} mapendekezo yake.",
    "Kwenye devolved governance, bunge la kaunti (County Assembly) lina wajibu wa kikatiba wa ku-{vet} mawaziri wa kaunti walioteuliwa na Gavana kabla ya kuidhinishwa kuanza kazi ofisini.",
    "Tume Huru ya Uchaguzi na Mipaka (IEBC) inalazimika ku-{audit} daftari la wapiga kura na kuweka mifumo ya kidijitali wazi kwa ukaguzi wa umma ili ku-{boost} uaminifu wa mchakato mzima wa kidemokrasia.",
    "Wakati viongozi wa civil society walipopinga uhalali wa sheria hiyo katika Mahakama Kuu, mawakili walidai kuwa vipengele kadhaa vya mswada huo vilikuwa vina-{infringe} haki za kimsingi za kibinadamu.",
    "Mchakato wa kumshtaki kiongozi wa umma (impeachment) unahitaji ushahidi thabiti wa kukiuka katiba au matumizi mabaya ya ofisi kabla ya Seneti kuamua ku-{uphold} au kutupilia mbali mashtaka hayo.",
    "Katika sera za kigeni na diplomasia ya kikanda, Serikali ya Kenya mara nyingi hujaribu ku-{mediate} mizozo ya nchi jirani ili kudumisha amani na ku-{promote} biashara huru kwenye kanda ya Afrika Mashariki."
]

# Mapping of all domain explanatory frames
ALL_EXPLANATORY_DOMAINS = [
    ("Engineering & Infrastructure", ENGINEERING_EXPLANATORY_TEMPLATES, 0.20),
    ("Finance & FinTech Economics", FINANCE_EXPLANATORY_TEMPLATES, 0.20),
    ("Tech & Distributed Systems", TECH_EXPLANATORY_TEMPLATES, 0.20),
    ("Medicine & Healthcare Sciences", MEDICINE_EXPLANATORY_TEMPLATES, 0.20),
    ("Politics & Constitutional Governance", POLITICS_EXPLANATORY_TEMPLATES, 0.20),
]

EXPERT_DOMAIN_MATRICES = {
    "Engineering & Structural Physics": {
        "loan_verbs": ENGINEERING_VERBS,
        "double_stack_nouns": ENGINEERING_DOUBLE_STACK_NOUNS,
        "manner_adverbs": ["kistructural", "kimechanical", "kielectrical", "kihydraulic"],
        "locative_nouns": ["kwa site", "kwa workshop", "kwa substation", "kwa foundation"],
        "templates": ENGINEERING_EXPLANATORY_TEMPLATES
    },
    "Finance, Banking & FinTech": {
        "loan_verbs": FINANCE_VERBS,
        "double_stack_nouns": FINANCE_DOUBLE_STACK_NOUNS,
        "manner_adverbs": ["kifinancial", "kieconomic", "kiaudit", "kistatutory"],
        "locative_nouns": ["kwa balance sheet", "kwa bank", "kwa SACCO", "kwa ledger"],
        "templates": FINANCE_EXPLANATORY_TEMPLATES
    },
    "Tech, Cloud Architecture & Distributed Systems": {
        "loan_verbs": TECH_VERBS,
        "double_stack_nouns": TECH_DOUBLE_STACK_NOUNS,
        "manner_adverbs": ["kitechnical", "kipro", "kicloud", "kisystem"],
        "locative_nouns": ["kwa server", "kwa database", "kwa cluster", "kwa endpoint"],
        "templates": TECH_EXPLANATORY_TEMPLATES
    },
    "Medicine, Pharmacology & Healthcare Sciences": {
        "loan_verbs": MEDICINE_VERBS,
        "double_stack_nouns": MEDICINE_DOUBLE_STACK_NOUNS,
        "manner_adverbs": ["kiclinical", "kipharmacological", "kisurgical", "kimedical"],
        "locative_nouns": ["kwa ICU", "kwa ward", "kwa triage", "kwa lab"],
        "templates": MEDICINE_EXPLANATORY_TEMPLATES
    },
    "Politics, Governance & Constitutional Law": {
        "loan_verbs": POLITICS_VERBS,
        "double_stack_nouns": POLITICS_DOUBLE_STACK_NOUNS,
        "manner_adverbs": ["kikatiba", "kiparlia", "kilegislative", "kipolitical"],
        "locative_nouns": ["kwa bunge", "kwa senate", "kwa county", "kwa committee"],
        "templates": POLITICS_EXPLANATORY_TEMPLATES
    }
}

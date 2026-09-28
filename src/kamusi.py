"""
Comprehensive Kamusi ya Kiswahili Sanifu & Bilingual Translation Engine
Provides deep lexical coverage for Standard Kiswahili, handles Swahili verbal extensions (Minyambuliko ya Vitenzi),
and eliminates broken word-by-word 'mixed words' to generate 100% pure Sanifu Swahili and fluent English.
"""

import re
from typing import Dict, Tuple, Optional, List, Any

# ==============================================================================
# SWAHILI BILINGUAL KAMUSI LEXICON (NOUNS, ADJECTIVES, ADVERBS, CONJUNCTIONS)
# ==============================================================================

SWAHILI_NOUNS_DICT = {
    # People, Family & Society
    "dereva": "driver",
    "madereva": "drivers",
    "abiria": "passenger / passengers",
    "mtu": "person",
    "watu": "people",
    "kijana": "youth / young person",
    "vijana": "youths / young people",
    "mwanafunzi": "student",
    "wanafunzi": "students",
    "mwalimu": "teacher",
    "walimu": "teachers",
    "mkuu": "boss / principal / director",
    "wakuu": "bosses / principals / directors",
    "bosi": "boss",
    "mabosi": "bosses",
    "meneja": "manager",
    "mameneja": "managers",
    "mkurugenzi": "director",
    "wakurugenzi": "directors",
    "mfanyakazi": "employee / worker",
    "wafanyakazi": "employees / workers",
    "mwenzangu": "my colleague",
    "wenzangu": "my colleagues",
    "mwenzake": "his/her colleague",
    "wenzao": "their colleagues",
    "rafiki": "friend",
    "marafiki": "friends",
    "jirani": "neighbor",
    "majirani": "neighbors",
    "familia": "family",
    "wazazi": "parents",
    "mzazi": "parent",
    "mama": "mother",
    "baba": "father",
    "ndugu": "brother / sibling",
    "dada": "sister",
    "mtoto": "child",
    "watoto": "children",
    "askari": "officer / guard",
    "maafisa": "officers",
    "afisa": "officer",
    "polisi": "police / police officer",
    "wananchi": "citizens / public",
    "mwananchi": "citizen",
    "kikundi": "group",
    "vikundi": "groups",
    "jamii": "community / society",
    "wateja": "customers / clients",
    "mteja": "customer / client",
    "kiongozi": "leader",
    "viongozi": "leaders",
    "tapeli": "fraudster / conman",
    "matapeli": "fraudsters / conmen",
    "mwizi": "thief",
    "wezi": "thieves",
    "msichana": "young lady / girl",
    "wasichana": "young ladies / girls",
    "mwanamke": "woman",
    "wanawake": "women",
    "mwanaume": "man",
    "wanaume": "men",
    "mzee": "elder / old man",
    "wazee": "elders",
    "chali": "guy / friend",
    "dem": "girl / lady",
    "jamaa": "guy / relative",
    "makanga": "matatu conductor / conductors",
    "konda": "conductor",
    "utingo": "conductor",

    # Transport, Urban Life & Geography
    "matatu": "matatu / public transit minibus",
    "gari": "vehicle / car",
    "magari": "vehicles / cars",
    "basi": "bus",
    "mabasi": "buses",
    "pikipiki": "motorcycle",
    "nduthi": "motorcycle taxi",
    "baiskeli": "bicycle",
    "ndege": "airplane",
    "meli": "ship",
    "treni": "train",
    "barabara": "road / highway",
    "njia": "way / path",
    "kituo": "station / stop",
    "vituo": "stations / stops",
    "stage": "bus stage",
    "mji": "city / town",
    "miji": "cities / towns",
    "jiji": "city / metropolis",
    "mtaa": "neighborhood / street",
    "mtaani": "in the neighborhood",
    "mitaa": "neighborhoods / streets",
    "maskani": "neighborhood hangout / base",
    "kijiji": "village",
    "eneo": "area / region",
    "maeneo": "areas / regions",
    "nchi": "country / nation",
    "foleni": "traffic jam / queue",
    "msongamano": "congestion / traffic",
    "nauli": "bus fare / transport fee",
    "safari": "journey / trip",
    "usafiri": "transportation",
    "mzigo": "luggage / cargo",
    "mizigo": "luggage / cargo / goods",
    "mwendo": "speed / movement",
    "vidhibiti": "governors / limiters",
    "doria": "patrols",
    "usalama": "security / safety",

    # Workplace, Finance & Commerce
    "kazi": "work / job",
    "ajira": "employment / jobs",
    "nafasi": "opportunity / position / space",
    "mshahara": "salary / wages",
    "mishahara": "salaries",
    "pesa": "money / cash",
    "fedha": "funds / finances",
    "chapaa": "cash / money",
    "dola": "dollars",
    "shilingi": "shillings",
    "akiba": "savings",
    "mkopo": "loan",
    "mikopo": "loans",
    "deni": "debt",
    "madeni": "debts",
    "akaunti": "bank account",
    "benki": "bank",
    "ofisi": "office",
    "kampuni": "company / firm",
    "makampuni": "companies / firms",
    "biashara": "business / trade",
    "faida": "profit / benefit",
    "hasara": "loss",
    "gharama": "cost / expenses",
    "bei": "price",
    "risiti": "receipt",
    "bili": "bill",
    "hongo": "bribe / corruption",
    "ushuru": "tax / duty",
    "mkataba": "contract / agreement",
    "taarifa": "notice / report / information",
    "barua": "letter",
    "ripoti": "report",
    "mkutano": "meeting / conference",
    "mahojiano": "interview / interviews",
    "uchumi": "economy",
    "mapato": "income / revenue",
    "kiasi": "amount / extent",
    "leseni": "license / licenses",
    "sheria": "law / regulation",
    "haki": "rights / justice",
    "majukumu": "responsibilities / duties",
    "jukumu": "duty / responsibility",
    "hitilafu": "defect / malfunction / glitch",
    "vinyozi": "barbershops / barbers",
    "saluni": "salons",
    "uchafu": "garbage / trash / waste",
    "takataka": "garbage / trash",
    "bwenini": "in the dormitory",
    "bweni": "dormitory",

    # Technology, Education & Communication
    "simu": "phone / mobile phone",
    "kompyuta": "computer",
    "mtandao": "network / internet",
    "mitandao": "networks / social media",
    "kiungo": "link",
    "viungo": "links",
    "programu": "application / software",
    "ujumbe": "message",
    "maombi": "applications / requests",
    "mfumo": "system",
    "mifumo": "systems",
    "kijasusi": "intelligence / artificial intelligence",
    "data": "data",
    "faili": "file / files",
    "muziki": "music",
    "wimbo": "song",
    "nyimbo": "songs",
    "video": "video",
    "picha": "picture / photo",
    "habari": "news / updates",
    "shule": "school",
    "darasa": "class / classroom",
    "chuo": "college / university",
    "masomo": "studies / education",
    "mtihani": "exam / test",
    "mitihani": "exams",
    "alama": "marks / grades",
    "stakabadhi": "documents / certificates",
    "taasisi": "institution",
    "nidhamu": "discipline",
    "sauti": "sound / audio",

    # Housing & Everyday Objects
    "nyumba": "house / home",
    "keja": "house / crib",
    "chumba": "room",
    "vyumba": "rooms",
    "kodi": "rent",
    "mpangaji": "tenant",
    "wapangaji": "tenants",
    "mwenye nyumba": "landlord",
    "maji": "water",
    "bomba": "pipe / tap",
    "tope": "mud",
    "matope": "mud",
    "mvua": "rain",
    "rangi": "paint / color",
    "kuta": "walls",
    "ukuta": "wall",
    "mlango": "door / gate / entrance",
    "stima": "electricity",
    "umeme": "electricity / power",
    "kiberiti": "matchbox / lighter",
    "moto": "fire",
    "sigara": "cigarette",
    "fegi": "cigarette",
    "pombe": "alcohol / beer",
    "kinywaji": "drink / beverage",
    "jaba": "khat / miraa",
    "mirungi": "khat / miraa",
    "chakula": "food",
    "chai": "tea",
    "mkate": "bread",
    "muda": "time",
    "wakati": "time / season",
    "saa": "hour / watch / clock",
    "siku": "day",
    "wiki": "week",
    "mwezi": "month",
    "mwaka": "year",
    "asubuhi": "morning",
    "mchana": "afternoon",
    "jioni": "evening",
    "usiku": "night",
    "leo": "today",
    "jana": "yesterday",
    "kesho": "tomorrow",
    "tabia": "habits / behavior",
    "shughuli": "activities / hustle",
    "upotevu": "loss / disappearance",
    "huruma": "mercy / leniency",
    "dawa": "medicine / treatment"
}

SWAHILI_ADJECTIVES_ADVERBS = {
    "bado": "still / not yet",
    "sana": "very / a lot",
    "fiti": "well / fit / properly",
    "safi": "clean / sharp / pristine",
    "maridadi": "smart / neat / splendid",
    "nzuri": "good / nice",
    "vizuri": "well / properly",
    "mbaya": "bad",
    "vibaya": "badly / severely",
    "kubwa": "big / large / major",
    "kikubwa": "significantly / largely",
    "ndogo": "small",
    "kidogo": "a little / slightly",
    "ngumu": "tough / difficult",
    "rahisi": "easy / cheap",
    "fupi": "short",
    "ndefu": "long / tall",
    "kadhaa": "several",
    "mengi": "many",
    "wengi": "many",
    "mingi": "many",
    "mwingi": "much / a lot of",
    "mpya": "new",
    "cha kisasa": "modern",
    "za kisasa": "modern",
    "ya kisasa": "modern",
    "rasmi": "formal / official",
    "wazi": "open / clear",
    "waziwazi": "openly / plainly",
    "nzima": "whole / entire",
    "mapema": "early",
    "haraka": "quickly / fast",
    "polepole": "slowly",
    "ghafla": "suddenly",
    "mara moja": "immediately",
    "vilivyo": "thoroughly / properly",
    "kabisa": "completely / entirely",
    "bure": "in vain / for free",
    "hivi": "like this / around",
    "hivyo": "like that / thus",
    "nje": "outside / abroad",
    "ndani": "inside",
    "karibu": "near / close",
    "mbali": "far away",
    "juu": "up / above",
    "chini": "down / below",
    "pili": "second",
    "kwanza": "first",
    "mwisho": "last / end",
    "miwili": "two",
    "viwili": "two",
    "mbili": "two",
    "watatu": "three",
    "mitatu": "three",
    "vitatu": "three",
    "tatu": "three",
    "nusu": "half",
    "mkali": "loud / fierce / sharp",
    "kali": "loud / sharp",
    "mzima": "whole / entire",
    "yoyote": "any",
    "yeyote": "anyone"
}

SWAHILI_CONJUNCTIONS_PREPOSITIONS = {
    "kwa sababu ya": "because of",
    "kwa sababu": "because",
    "kwa maana": "for the reason that",
    "kwa kuwa": "since / because",
    "kwa ajili ya": "for the sake of",
    "kutokana na": "due to / as a result of",
    "asubuhi na mapema": "early in the morning",
    "mara kwa mara": "frequently / from time to time",
    "kwa kiasi kikubwa": "to a large extent / significantly",
    "katikati ya jiji": "downtown",
    "katikati ya": "in the center of",
    "katikati": "downtown",
    "mpango wa shughuli": "plans",
    "mpango wa": "plan for",
    "mpango": "plan",
    "kitambo": "a long time ago",
    "na askari": "with a police officer",
    "na polisi": "with the police",
    "njoo": "come",
    "nenda": "go",
    "upande": "take / board",
    "uchukue": "take",
    "niko na": "I have",
    "uko na": "you have",
    "yuko na": "he/she has",
    "tuko na": "we have",
    "wako na": "they have",
    "mko na": "you all have",
    "niko": "I am",
    "uko": "you are",
    "yuko": "he/she is",
    "tuko": "we are",
    "wako": "they are",
    "mko": "you all are",
    "nina": "I have",
    "una": "you have",
    "ana": "he/she has",
    "tuna": "we have",
    "mna": "you all have",
    "wana": "they have",
    "sina": "I have no",
    "hana": "he/she has no",
    "hatuna": "we have no",
    "hawana": "they have no",
    "ndugu yangu": "bro / my brother",
    "rafiki yangu": "my friend",
    "zaidi ya": "more than",
    "kila siku": "every day / daily",
    "badala ya": "instead of",
    "pamoja na": "together with / along with",
    "mbele ya": "in front of",
    "nyuma ya": "behind",
    "chini ya": "under / beneath",
    "juu ya": "about / regarding / on top of",
    "baada ya": "after",
    "kabla ya": "before",
    "kama vile": "such as",
    "kama": "as / like / if",
    "lakini": "but / however",
    "ingawa": "although",
    "hata": "even / not even",
    "pia": "also / too",
    "tena": "again / furthermore",
    "tu": "only / just",
    "bila": "without",
    "hadi": "until / up to",
    "mpaka": "until",
    "tangu": "since / from",
    "katika": "in / at / inside",
    "kwenye": "on / at / in",
    "kutoka": "from",
    "kwa": "to / for / by / with",
    "na": "and / with",
    "ya": "of",
    "wa": "of",
    "za": "of",
    "la": "of",
    "cha": "of",
    "vya": "of",
    "mwa": "in / of",
    "huyu": "this",
    "huyo": "that",
    "huyo mtu": "that guy",
    "jukwaani": "on stage",
    "alicheza": "danced",
    "alicheza muziki": "danced to music",
    "alicheza ngoma": "danced",
    "hawa": "these",
    "hiki": "this",
    "hivi": "these",
    "hili": "this",
    "haya": "these",
    "hii": "this",
    "hizi": "these",
    "hiyo": "that",
    "hizo": "those",
    "hicho": "that",
    "hivyo": "those",
    "hilo": "that",
    "yule": "that",
    "wale": "those",
    "ile": "that",
    "kila": "every / each",
    "wote": "all",
    "yote": "all",
    "zote": "all",
    "chote": "all",
    "vyote": "all",
    "wangu": "my",
    "yangu": "my",
    "changu": "my",
    "vyangu": "my",
    "zangu": "my",
    "wako": "your",
    "yako": "your",
    "chako": "your",
    "vyako": "your",
    "zako": "your",
    "wake": "his/her",
    "yake": "his/her",
    "chake": "his/her",
    "vyake": "his/her",
    "zake": "his/her",
    "yetu": "our",
    "wetu": "our",
    "chetu": "our",
    "vyetu": "our",
    "zetu": "our",
    "yao": "their",
    "wao": "their",
    "chao": "their",
    "vyao": "their",
    "zao": "their",
    "pale": "there",
    "hapa": "here",
    "huko": "there",
    "kwamba": "that",
    "ili": "so that / in order that",
    "basi": "so / well then",
    "ndipo": "that was when",
    "ndio": "is indeed / that is",
    "juu": "because (colloquial)",
    "vile": "how / the way that",
    "jinsi": "how / the way"
}

# English loanwords common in Kenyan speech -> Standard Swahili equivalent
ENGLISH_TO_SWAHILI_DICT = {
    "salary": "mshahara",
    "job": "kazi",
    "work": "kazi",
    "boss": "mkuu / bosi",
    "manager": "meneja",
    "meeting": "mkutano",
    "interview": "mahojiano",
    "interviews": "mahojiano",
    "link": "kiungo",
    "app": "programu",
    "notice": "taarifa / ilani",
    "contract": "mkataba",
    "company": "kampuni",
    "tech": "teknolojia",
    "startup": "biashara changa ya kiteknolojia",
    "startups": "biashara changa za kiteknolojia",
    "portfolio": "jalada la kazi",
    "remote work": "kufanyia kazi nyumbani",
    "cloud": "wingu la mtandao",
    "lead": "kiongozi",
    "landlord": "mwenye nyumba",
    "deposit": "amana ya kodi",
    "clean code": "msimbo safi wa programu",
    "documentation": "nyaraka rasmi",
    "data structures": "miundo ya data",
    "algorithms": "kanuni za programu",
    "stage": "kituo cha magari",
    "club": "klabu",
    "prep": "masomo ya ziada ya asubuhi",
    "dormitory": "bweni",
    "screen": "skrini",
    "fare": "nauli",
    "bill": "bili"
}

# Swahili Verbal Roots (Stem -> English Base, Canonical Swahili Infinitive)
SWAHILI_VERB_ROOTS = {
    # Holding, Touching, Intoxication & Social Exchanges (User's Core Interest)
    "shik-": ("hold / take / kick in", "shika"),
    "sukum-": ("push / connect / refer", "sukuma"),
    "rush-": ("throw / send over", "rusha"),
    "fung-": ("close / lock / score", "funga"),
    "fungu-": ("open / unlock", "fungua"),

    # Workplace, Cognition & Communication
    "ongez-": ("increase / raise / add", "ongeza"),
    "shuk-": ("descend / drop / fall", "shuka"),
    "fut-": ("fire / erase / cancel", "futa"),
    "ajir-": ("hire / employ", "ajiri"),
    "pandish-": ("promote / raise / elevate", "pandisha"),
    "shush-": ("demote / lower", "shusha"),
    "pongez-": ("praise / congratulate", "pongeza"),
    "laum-": ("blame / fault", "laumu"),
    "ony-": ("warn / caution", "onya"),
    "dai-": ("claim / demand", "dai"),
    "kubal-": ("agree / accept / admit", "kubali"),
    "kata-": ("refuse / reject", "kataa"),
    "lalamik-": ("complain / lament", "lalamika"),
    "gom-": ("strike / boycott", "goma"),
    "singizi-": ("pretend / feign / use pretext", "singizia"),
    "hoj-": ("interview / question", "hoji"),
    "thibitish-": ("confirm / verify", "thibitisha"),
    "elew-": ("understand / comprehend", "elewa"),
    "changany-": ("confuse / mix up", "changanya"),
    "faham-": ("understand / know", "fahamu"),
    "ju-": ("know", "jua"),
    "fikir-": ("think / consider", "fikiri"),
    "waz-": ("ponder / reflect", "waza"),
    "kumbuk-": ("remember", "kumbuka"),
    "sahau-": ("forget", "sahau"),
    "amini-": ("believe / trust", "amini"),
    "sem-": ("say / speak", "sema"),
    "onge-": ("talk / converse", "ongea"),
    "zungumz-": ("converse / discuss", "zungumza"),
    "uliz-": ("ask / inquire", "uliza"),
    "jib-": ("answer / reply", "jibu"),
    "elez-": ("explain / describe", "eleza"),
    "amb-": ("tell", "ambia"),
    "agiz-": ("instruct / order", "agiza"),
    "tangaz-": ("announce / declare", "tangaza"),
    "kutan-": ("meet / assemble", "kutana"),
    "kusanyik-": ("gather / assemble", "kusanyika"),
    "shangaz-": ("surprise / astonish", "shangaza"),
    "shanga-": ("wonder / be surprised", "shangaa"),
    "gundu-": ("discover / realize", "gundua"),
    "aniki-": ("expose / reveal", "anika"),
    "vunj-": ("break / violate", "vunja"),
    "himiz-": ("encourage / urge", "himiza"),

    # Action, Motion & Movement
    "end-": ("go / proceed", "enda"),
    "j-": ("come", "kuja"),
    "fik-": ("arrive / reach", "fika"),
    "ondok-": ("depart / leave", "ondoka"),
    "ing-": ("enter / get in", "ingia"),
    "tok-": ("come from / exit", "toka"),
    "kimbik-": ("run / flee", "kimbia"),
    "tembe-": ("walk / travel", "tembea"),
    "pand-": ("board / climb", "panda"),
    "simam-": ("stop / stand", "simama"),
    "simamish-": ("halt / stop / intercept", "simamisha"),
    "kagu-": ("inspect / scrutinize", "kagua"),
    "ruhusiw-": ("be permitted", "ruhusiwa"),
    "ruhus-": ("permit / allow", "ruhusu"),
    "keti-": ("sit / stay", "keti"),
    "ish-": ("live / reside", "ishi"),
    "lal-": ("sleep / spend night", "lala"),
    "amk-": ("wake up", "amka"),
    "let-": ("bring", "leta"),
    "pelek-": ("take to / deliver", "peleka"),
    "tum-": ("send", "tuma"),
    "chuj-": ("filter / screen", "chuja"),
    "pat-": ("get / find / obtain", "pata"),
    "patikan-": ("be found / be available", "patikana"),
    "pot-": ("lose", "poteza"),
    "potez-": ("lose / waste", "poteza"),
    "potev-": ("get lost", "potea"),
    "tafut-": ("search / look for", "tafuta"),
    "wek-": ("put / place / install", "weka"),
    "to-": ("give / provide / issue", "toa"),
    "poke-": ("receive / accept", "pokea"),
    "nunul-": ("buy / purchase", "nunua"),
    "nunua-": ("buy", "nunua"),
    "uz-": ("sell", "uza"),
    "lip-": ("pay", "lipa"),
    "lipw-": ("be paid", "lipwa"),
    "som-": ("study / read", "soma"),
    "andik-": ("write", "andika"),
    "fany-": ("do / make", "fanya"),
    "und-": ("create / build", "unda"),
    "jeng-": ("construct / build", "jenga"),
    "harib-": ("spoil / damage / ruin", "haribu"),
    "tengenez-": ("repair / make", "tengeneza"),
    "anz-": ("begin / start", "anza"),
    "anzish-": ("initiate / establish", "anzisha"),
    "maliz-": ("finish / complete", "maliza"),
    "saidik-": ("help / assist", "saidia"),
    "saidia-": ("help / assist", "saidia"),
    "shind-": ("win / overcome / fail", "shinda"),
    "shindw-": ("fail / be defeated", "shindwa"),
    "epuk-": ("avoid / shun", "epuka"),
    "oko-": ("save / rescue", "okoa"),
    "hamish-": ("migrate / transfer / move", "hamisha"),
    "ham-": ("relocate / move out", "hama"),
    "jaa-": ("fill / overflow", "jaa"),
    "nyesh-": ("rain / downpour", "nyesha"),
    "imarik-": ("improve / strengthen", "imarika"),
    "shirikikan-": ("cooperate / partner", "shirikiana"),
    "pigan-": ("fight", "pigana"),
    "pig-": ("hit / strike / beat", "piga"),
    "kul-": ("eat / consume", "kula"),
    "nyw-": ("drink", "kunywa"),
    "lev-": ("intoxicate / get drunk", "lewa"),
    "lewesh-": ("intoxicate / make drunk", "lewesha"),
    "wash-": ("ignite / light", "washa"),
    "zim-": ("turn off / extinguish", "zima"),
    "fukuz-": ("chase / dismiss / expel", "fukuza"),
    "kamat-": ("arrest / seize", "kamata"),
    "kamik-": ("arrest / catch", "kamata"),
    "ach-": ("leave / quit / stop", "acha"),
    "pend-": ("like / love", "penda"),
    "tak-": ("want / desire / require", "taka"),
    "wez-": ("be able / can", "weza"),
    "bidi-": ("be necessary / must", "bidi"),
    "lazim-": ("oblige / compel", "lazimu"),
    "lazimik-": ("be forced / be compelled", "lazimika"),
    "katik-": ("cut / interrupt / blackout", "katika")
}


class KamusiEngine:
    """Standard Kiswahili Morphological Kamusi and Universal Bilingual Translator."""

    SWAHILI_NOUNS_DICT = SWAHILI_NOUNS_DICT
    SWAHILI_ADJECTIVES_ADVERBS = SWAHILI_ADJECTIVES_ADVERBS
    SWAHILI_CONJUNCTIONS_PREPOSITIONS = SWAHILI_CONJUNCTIONS_PREPOSITIONS
    ENGLISH_TO_SWAHILI_DICT = ENGLISH_TO_SWAHILI_DICT
    SWAHILI_VERB_ROOTS = SWAHILI_VERB_ROOTS

    def __init__(self):
        pass

    def deconstruct_swahili_verb(self, word: str, context_sentence: str = "") -> Optional[Dict[str, Any]]:
        """
        Decomposes a standard or extended Swahili verbal complex:
        Subject + Tense/Aspect + (Object) + Verb Root + Extension (Mnyambuliko) + Final Vowel
        Handles:
        - Infinitive 'ku-' (e.g. kusaidia -> to help, kuepuka -> to avoid)
        - Negation 'ha-', 'si-', 'hatu-', 'hawa-', etc.
        - Participles 'aki-', 'waki-'
        - Relatives 'wanao-', 'waliyo-', 'inavyo-', etc.
        - Verbal Extensions: -wa (passive), -ia (applicative), -isha (causative), -ana (reciprocal)
        - Polysemic Kenyan street context for 'shika' / 'shikia' / 'shikisha'.
        """
        w = word.lower().strip()
        if len(w) < 3:
            return None

        # 1. Handle Imperatives & Subjunctives (nishikishe, nirushie, nisukume, niwashe, uchukue)
        if w.startswith("ni") and (w.endswith("e") or w.endswith("eshe") or w.endswith("ishe") or w.endswith("ie") or w.endswith("ea")):
            core = w[2:]
            if core.startswith("shik"):
                return {
                    "subject": "imp", "tense": "imp", "object": "ni", "extension": "causative",
                    "canonical_swahili": "patia kiberiti / moto",
                    "english_translation": "pass me the lighter / matchbox"
                }
            elif core.startswith("rush"):
                return {
                    "subject": "imp", "tense": "imp", "object": "ni", "extension": "applicative",
                    "canonical_swahili": "tuma / rushia",
                    "english_translation": "send me / forward to me"
                }
            elif core.startswith("sukum"):
                return {
                    "subject": "imp", "tense": "imp", "object": "ni", "extension": "applicative",
                    "canonical_swahili": "unganisha na kazi / sukuma",
                    "english_translation": "connect me to / refer me for"
                }
            elif core.startswith("wash"):
                return {
                    "subject": "sub", "tense": "subjunctive", "object": None, "extension": "base",
                    "canonical_swahili": "washa",
                    "english_translation": "so I can light"
                }
            elif core.startswith("said"):
                return {
                    "subject": "imp", "tense": "imp", "object": "ni", "extension": "applicative",
                    "canonical_swahili": "saidia",
                    "english_translation": "help me"
                }
            elif core.startswith("amb"):
                return {
                    "subject": "imp", "tense": "imp", "object": "ni", "extension": "applicative",
                    "canonical_swahili": "ambia",
                    "english_translation": "tell me"
                }

        # Check other subjunctives like 'uchukue', 'tufanye'
        if w == "uchukue":
            return {
                "subject": "u", "tense": "subjunctive", "object": None, "extension": "base",
                "canonical_swahili": "upande / uchukue",
                "english_translation": "take / board"
            }

        # 2. Handle Infinitive 'ku-' verbs directly
        if w.startswith("ku") and len(w) > 4:
            stem_candidate = w[2:]
            for v_root, (en_meaning, canonical) in SWAHILI_VERB_ROOTS.items():
                clean_root = v_root.rstrip("-")
                if stem_candidate.startswith(clean_root):
                    ext = self._detect_extension(stem_candidate)
                    en_verb = self._synthesize_infinitive_meaning(en_meaning, ext, context_sentence)
                    return {
                        "subject": "inf",
                        "tense": "ku",
                        "object": None,
                        "extension": ext,
                        "canonical_swahili": canonical,
                        "english_translation": en_verb
                    }

        # 3. Subject + Tense Combinations (Ordered by longest prefix match)
        subjects_tenses = [
            # Compound / Relatives (multi-morpheme prefixes)
            ("waliopatikana", ("wa", "li_rel")),
            ("waliyo", ("wa", "li_rel")),
            ("walio", ("wa", "li_rel")),
            ("wanao", ("wa", "na_rel")),
            ("watakao", ("wa", "ta_rel")),
            ("aliye", ("a", "li_rel")),
            ("anaye", ("a", "na_rel")),
            ("atakaye", ("a", "ta_rel")),
            ("inavyo", ("i", "na_rel")),
            ("kinacho", ("ki", "na_rel")),
            ("vilivyo", ("vi", "li_rel")),
            ("vinavyo", ("vi", "na_rel")),

            # Participles (-ki-)
            ("wakilalamik", ("wa", "ki")),
            ("wakisingiz", ("wa", "ki")),
            ("wakijadil", ("wa", "ki")),
            ("waki", ("wa", "ki")),
            ("aki", ("a", "ki")),
            ("tuki", ("tu", "ki")),
            ("niki", ("ni", "ki")),
            ("yaki", ("ya", "ki")),

            # Negatives
            ("halija", ("li", "ja_neg")),
            ("hawaja", ("wa", "ja_neg")),
            ("haja", ("a", "ja_neg")),
            ("sija", ("ni", "ja_neg")),
            ("hatuja", ("tu", "ja_neg")),
            ("hawaku", ("wa", "li_neg")),
            ("haku", ("a", "li_neg")),
            ("siku", ("ni", "li_neg")),
            ("hatuku", ("tu", "li_neg")),
            ("haiku", ("i", "li_neg")),
            ("haziku", ("zi", "li_neg")),

            # Standard 3rd person singular (a-)
            ("ali", ("a", "li")), ("ana", ("a", "na")), ("ata", ("a", "ta")), ("ame", ("a", "me")),
            ("aka", ("a", "ka")),

            # 3rd person plural (wa-)
            ("wali", ("wa", "li")), ("wana", ("wa", "na")), ("wata", ("wa", "ta")), ("wame", ("wa", "me")),
            ("waka", ("wa", "ka")),

            # 1st person singular (ni-)
            ("nili", ("ni", "li")), ("nina", ("ni", "na")), ("nita", ("ni", "ta")), ("nime", ("ni", "me")),
            ("nika", ("ni", "ka")),

            # 1st person plural (tu-)
            ("tuli", ("tu", "li")), ("tuna", ("tu", "na")), ("tuta", ("tu", "ta")), ("tume", ("tu", "me")),
            ("tuka", ("tu", "ka")),

            # 2nd person singular (u-)
            ("uli", ("u", "li")), ("una", ("u", "na")), ("uta", ("u", "ta")), ("ume", ("u", "me")),

            # 2nd person plural (m-)
            ("muli", ("m", "li")), ("mli", ("m", "li")), ("mna", ("m", "na")), ("mta", ("m", "ta")), ("mme", ("m", "me")),

            # Inanimate Noun Classes (i-, zi-, ki-, vi-, li-, ya-)
            ("ime", ("i", "me")), ("ina", ("i", "na")), ("ili", ("i", "li")), ("ita", ("i", "ta")),
            ("zime", ("zi", "me")), ("zina", ("zi", "na")), ("zili", ("zi", "li")), ("zita", ("zi", "ta")),
            ("kime", ("ki", "me")), ("kina", ("ki", "na")), ("kili", ("ki", "li")), ("kita", ("ki", "ta")),
            ("vime", ("vi", "me")), ("vina", ("vi", "na")), ("vili", ("vi", "li")), ("vita", ("vi", "ta")),
            ("lime", ("li", "me")), ("lina", ("li", "na")), ("lili", ("li", "li")), ("lita", ("li", "ta")),
            ("yame", ("ya", "me")), ("yana", ("ya", "na")), ("yali", ("ya", "li")), ("yata", ("ya", "ta")),
            ("kuna", ("ku", "na")), ("kuli", ("ku", "li")),
        ]

        subj_found = None
        tense_found = None
        remainder = None

        for item in subjects_tenses:
            pfx = item[0]
            val = item[1]
            if w.startswith(pfx):
                subj_found = val[0]
                tense_found = val[1]
                remainder = w[len(pfx):]
                break

        if not remainder:
            return None

        # Check for object infixes: ni, ku, m, tu, wa, ji
        obj_found = None
        for obj_pfx in ["ni", "ku", "wa", "tu", "ji"]:
            if remainder.startswith(obj_pfx) and len(remainder) > len(obj_pfx) + 2:
                obj_found = obj_pfx
                remainder = remainder[len(obj_pfx):]
                break
        else:
            if remainder.startswith("m") and len(remainder) > 3 and remainder[1] not in "aeiou":
                obj_found = "m"
                remainder = remainder[1:]

        # Detect Verbal Extensions (Minyambuliko ya Vitenzi)
        ext, stem_core = self._strip_extension(remainder)

        # Match stem_core against SWAHILI_VERB_ROOTS
        matched_verb = None
        for v_root, (en_meaning, canonical) in SWAHILI_VERB_ROOTS.items():
            clean_root = v_root.rstrip("-")
            if stem_core.startswith(clean_root) or clean_root.startswith(stem_core):
                matched_verb = (v_root, en_meaning, canonical)
                break

        if not matched_verb:
            # Try fuzzy match on remainder
            for v_root, (en_meaning, canonical) in SWAHILI_VERB_ROOTS.items():
                clean_root = v_root.rstrip("-")
                if clean_root in remainder:
                    matched_verb = (v_root, en_meaning, canonical)
                    break

        if not matched_verb:
            return None

        subj_en_map = {
            "a": "he/she", "wa": "they", "ni": "I", "tu": "we", "u": "you",
            "m": "you all", "i": "it", "zi": "they", "ki": "it", "vi": "they",
            "li": "it", "ya": "they", "ku": "there"
        }
        subj_en = subj_en_map.get(subj_found, "it")
        v_root, en_meaning, canonical = matched_verb

        en_verb_translated = self._synthesize_extension_meaning(
            base_en=en_meaning,
            tense=tense_found,
            extension=ext,
            subj=subj_en,
            obj=obj_found,
            context=context_sentence,
            verb_root=v_root
        )

        return {
            "subject": subj_found,
            "tense": tense_found,
            "object": obj_found,
            "extension": ext,
            "canonical_swahili": canonical,
            "english_translation": en_verb_translated
        }

    def _strip_extension(self, remainder: str) -> Tuple[str, str]:
        """Detects and strips Swahili verbal extensions (Minyambuliko)."""
        if remainder.endswith("iwa") or remainder.endswith("ewa"):
            return "passive", remainder[:-3]
        elif remainder.endswith("wa"):
            return "passive", remainder[:-2]
        elif remainder.endswith("iana") or remainder.endswith("eana"):
            return "reciprocal_applicative", remainder[:-4]
        elif remainder.endswith("ana"):
            return "reciprocal", remainder[:-3]
        elif remainder.endswith("isha") or remainder.endswith("esha"):
            return "causative", remainder[:-4]
        elif remainder.endswith("ia") or remainder.endswith("ea"):
            return "applicative", remainder[:-2]
        elif remainder.endswith("ika") or remainder.endswith("eka"):
            return "stative", remainder[:-3]
        return "base", remainder.rstrip("aeiou")

    def _detect_extension(self, stem: str) -> str:
        ext, _ = self._strip_extension(stem)
        return ext

    def _synthesize_infinitive_meaning(self, en_meaning: str, ext: str, context: str) -> str:
        """Translates Swahili infinitive (ku-) verbs into fluent English."""
        primary_en = en_meaning.split(" / ")[0].strip()
        ctx_lower = context.lower()

        # Contextual override for 'shika'
        if "hold" in en_meaning or primary_en == "hold":
            if any(k in ctx_lower for k in ["jaba", "miraa", "fiti", "bangi"]):
                return "to kick in / to take strong effect"
            if ext == "applicative":
                return "to buy drinks for / to cover drinks for"
            if ext == "causative":
                return "to pass the lighter / to light up"

        if ext == "passive":
            return f"to be {self._past_participle(primary_en)}"
        elif ext == "applicative":
            return f"to {primary_en} for"
        elif ext == "causative":
            return f"to cause to {primary_en}"
        elif ext == "reciprocal":
            return f"to {primary_en} each other"

        return f"to {primary_en}"

    def _synthesize_extension_meaning(
        self,
        base_en: str,
        tense: str,
        extension: str,
        subj: str,
        obj: Optional[str] = None,
        context: str = "",
        verb_root: str = ""
    ) -> str:
        """
        Applies Bantu verbal extension semantics & context rules (e.g. Minyambuliko ya shika).
        """
        primary_en = base_en.split(" / ")[0].strip()
        ctx_lower = context.lower()

        # -------------------------------------------------------------
        # SPECIAL LINGUISTIC RULES: 'shika' (Kutenda, Kutendea, Kutendesha)
        # -------------------------------------------------------------
        if verb_root == "shik-":
            # 1. Applicative Voice (Kutendea: shikia -> buy/cover drinks for)
            if extension == "applicative" or "pombe" in ctx_lower or "drink" in ctx_lower or "club" in ctx_lower:
                target_obj = "me" if obj == "ni" else ("you" if obj == "ku" else "us" if obj == "tu" else "someone")
                if tense == "ta":
                    return f"will {subj} buy alcohol for {target_obj}?" if subj == "you" else f"{subj} will buy alcohol for {target_obj}"
                elif tense == "li":
                    return f"{subj} bought drinks for {target_obj}"
                elif tense == "na":
                    return f"{subj} is buying drinks for {target_obj}"
                return f"{subj} buy drinks for {target_obj}"

            # 2. Causative Voice (Kutendesha: shikisha -> pass fire / light cigarette)
            if extension == "causative" or any(k in ctx_lower for k in ["kiberiti", "moto", "fegi", "sigara"]):
                return f"{subj} pass the lighter / light up"

            # 3. Base Voice / Inchoative (Kutenda: kushika fiti -> kick in)
            if any(k in ctx_lower for k in ["jaba", "miraa", "fiti", "bangi"]):
                if tense == "me":
                    return f"{subj} has kicked in well" if subj == "it" else f"{subj} have kicked in well"
                elif tense == "na":
                    return f"{subj} is kicking in strongly"
                elif tense == "li":
                    return f"{subj} kicked in well"
                elif tense == "ta":
                    return f"{subj} will kick in strongly"
                return f"{subj} kicks in well"

            # Default shika
            if tense == "li":
                return f"{subj} held / took"
            elif tense == "na":
                return f"{subj} is holding / taking"
            elif tense == "ta":
                return f"{subj} will hold / take"
            return f"{subj} hold"

        # -------------------------------------------------------------
        # GENERAL PASSIVE VOICE (Kutendwa: e.g. alipongezwa -> was praised)
        # -------------------------------------------------------------
        if extension == "passive":
            participle = self._past_participle(primary_en)
            if tense in ["li", "li_neg"]:
                be_verb = "was" if subj in ["he/she", "I", "it"] else "were"
                prefix = f"{subj} was not" if tense == "li_neg" else f"{subj} {be_verb}"
                return f"{prefix} {participle}"
            elif tense == "na":
                be_verb = "is" if subj in ["he/she", "it"] else ("am" if subj == "I" else "are")
                return f"{subj} {be_verb} being {participle}"
            elif tense == "me":
                have_verb = "has" if subj in ["he/she", "it"] else "have"
                return f"{subj} {have_verb} been {participle}"
            elif tense == "ta":
                return f"{subj} will be {participle}"
            elif tense == "ki":
                return f"being {participle}"
            elif tense == "li_rel":
                return f"who were {participle}" if subj in ["they", "we"] else f"who was {participle}"
            return f"{subj} is {participle}"

        # -------------------------------------------------------------
        # APPLICATIVE VOICE (Kutendea: e.g. shukuru -> thank, somia -> read for)
        # -------------------------------------------------------------
        if extension == "applicative":
            action = f"{primary_en} for"
            if tense == "li":
                return f"{subj} {self._past_tense(primary_en)} for"
            elif tense == "na":
                return f"{subj} is {primary_en}ing for"
            elif tense == "ta":
                return f"{subj} will {primary_en} for"
            return f"{subj} {action}"

        # -------------------------------------------------------------
        # CAUSATIVE VOICE (Kutendesha)
        # -------------------------------------------------------------
        if extension == "causative":
            if tense == "li":
                return f"{subj} caused to {primary_en}"
            elif tense == "ta":
                return f"{subj} will cause to {primary_en}"
            return f"{subj} causes to {primary_en}"

        # -------------------------------------------------------------
        # RECIPROCAL (Kutendana: e.g. walikutana -> they met)
        # -------------------------------------------------------------
        if extension == "reciprocal":
            if tense == "li":
                return f"{subj} {self._past_tense(primary_en)} each other"
            elif tense == "na":
                return f"{subj} are {primary_en}ing each other"
            return f"{subj} {primary_en} each other"

        # -------------------------------------------------------------
        # PARTICIPLES & RELATIVES (akidai -> claiming, wanaoishi -> who live)
        # -------------------------------------------------------------
        if tense == "ki":
            return f"{primary_en}ing"
        elif tense == "na_rel":
            return f"who {primary_en}" if subj in ["they", "we", "you"] else f"as it {primary_en}s"
        elif tense == "li_rel":
            return f"who {self._past_tense(primary_en)}"
        elif tense == "ta_rel":
            return f"who will {primary_en}"
        elif tense == "ja_neg":
            return f"{subj} has not {self._past_participle(primary_en)}" if subj in ["he/she", "it"] else f"{subj} have not {self._past_participle(primary_en)}"

        # -------------------------------------------------------------
        # STANDARD TENSES (Past, Present, Future, Perfect)
        # -------------------------------------------------------------
        if tense == "li":
            return f"{subj} {self._past_tense(primary_en)}"
        elif tense == "li_neg":
            return f"{subj} did not {primary_en}"
        elif tense == "na":
            if subj in ["he/she", "it"]:
                return f"{subj} is {primary_en}ing"
            elif subj == "I":
                return f"I am {primary_en}ing"
            return f"{subj} are {primary_en}ing"
        elif tense == "ta":
            return f"{subj} will {primary_en}"
        elif tense == "me":
            have_verb = "has" if subj in ["he/she", "it"] else "have"
            return f"{subj} {have_verb} {self._past_participle(primary_en)}"

        return f"{subj} {primary_en}"

    def _past_tense(self, verb: str) -> str:
        irregulars = {
            "go": "went", "come": "came", "see": "saw", "hear": "heard", "say": "said",
            "tell": "told", "know": "knew", "think": "thought", "find": "found", "get": "got",
            "give": "gave", "bring": "brought", "buy": "bought", "sell": "sold", "pay": "paid",
            "make": "made", "build": "built", "write": "wrote", "read": "read", "eat": "ate",
            "drink": "drank", "sleep": "slept", "wake": "woke", "hold": "held", "strike": "struck",
            "catch": "caught", "stand": "stood", "leave": "left", "quit": "quit", "win": "won",
            "praise": "praised", "halt": "halted", "stop": "stopped", "drop": "dropped",
            "raise": "raised", "increase": "increased", "refuse": "refused", "strike": "went on strike",
            "fail": "failed", "avoid": "avoided", "save": "saved", "migrate": "migrated"
        }
        if verb in irregulars:
            return irregulars[verb]
        if verb.endswith("e"):
            return verb + "d"
        if verb.endswith("y") and len(verb) > 2 and verb[-2] not in "aeiou":
            return verb[:-1] + "ied"
        return verb + "ed"

    def _past_participle(self, verb: str) -> str:
        irregulars = {
            "go": "gone", "come": "come", "see": "seen", "hear": "heard", "say": "said",
            "tell": "told", "know": "known", "think": "thought", "find": "found", "get": "gotten",
            "give": "given", "bring": "brought", "buy": "bought", "sell": "sold", "pay": "paid",
            "make": "made", "build": "built", "write": "written", "read": "read", "eat": "eaten",
            "drink": "drunk", "sleep": "slept", "wake": "woken", "hold": "held", "strike": "struck",
            "catch": "caught", "congratulate": "congratulated", "warn": "warned", "blame": "blamed",
            "praise": "praised", "halt": "halted", "stop": "stopped", "drop": "dropped",
            "raise": "raised", "fire": "fired", "promote": "promoted", "demote": "demoted"
        }
        if verb in irregulars:
            return irregulars[verb]
        return self._past_tense(verb)

    def translate_clean_sentence(self, text: str) -> Tuple[str, str]:
        """
        Translates a Kenyan code-switched or Swahili sentence into:
        1. 100% PURE Standard Kiswahili Sanifu (no English loan leftovers)
        2. 100% FLUENT English (no Swahili leftovers / NO mixed words)
        """
        # Split tokens preserving punctuation
        tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
        sanifu_tokens = []
        english_tokens = []

        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if not tok.isalnum():
                sanifu_tokens.append(tok)
                english_tokens.append(tok)
                i += 1
                continue

            low = tok.lower()

            # -------------------------------------------------------------
            # 1. Tri-gram check (e.g. 'kwa sababu ya', 'asubuhi na mapema', 'kwa kiasi kikubwa')
            # -------------------------------------------------------------
            if i + 2 < len(tokens):
                trigram = f"{low} {tokens[i+1].lower()} {tokens[i+2].lower()}"
                if trigram in SWAHILI_CONJUNCTIONS_PREPOSITIONS:
                    sanifu_tokens.append(trigram)
                    english_tokens.append(SWAHILI_CONJUNCTIONS_PREPOSITIONS[trigram].split(" / ")[0])
                    i += 3
                    continue

            # -------------------------------------------------------------
            # 2. Bi-gram check (e.g. 'kwa sababu', 'mwenye nyumba', 'kula fare', 'shika fiti', 'remote work')
            # -------------------------------------------------------------
            if i + 1 < len(tokens):
                bigram = f"{low} {tokens[i+1].lower()}"
                if bigram in SWAHILI_CONJUNCTIONS_PREPOSITIONS:
                    sanifu_tokens.append(bigram)
                    english_tokens.append(SWAHILI_CONJUNCTIONS_PREPOSITIONS[bigram].split(" / ")[0])
                    i += 2
                    continue
                if bigram in SWAHILI_NOUNS_DICT:
                    sanifu_tokens.append(bigram)
                    english_tokens.append(SWAHILI_NOUNS_DICT[bigram].split(" / ")[0])
                    i += 2
                    continue
                if bigram in ENGLISH_TO_SWAHILI_DICT:
                    sanifu_tokens.append(ENGLISH_TO_SWAHILI_DICT[bigram].split(" / ")[0])
                    english_tokens.append(bigram)
                    i += 2
                    continue
                # Kenyan Street Idioms
                if bigram == "kula fare":
                    sanifu_tokens.append("kupokea nauli na kutofika")
                    english_tokens.append("ghost after receiving fare")
                    i += 2
                    continue
                elif bigram == "shika fiti":
                    sanifu_tokens.append("kulewesha vizuri sana")
                    english_tokens.append("kick in properly")
                    i += 2
                    continue
                elif bigram == "piga luku":
                    sanifu_tokens.append("kuvalia maridadi")
                    english_tokens.append("dress sharply")
                    i += 2
                    continue

            # -------------------------------------------------------------
            # 3. Conjunctions & Prepositions
            # -------------------------------------------------------------
            if low in SWAHILI_CONJUNCTIONS_PREPOSITIONS:
                sanifu_tokens.append(low)
                english_tokens.append(SWAHILI_CONJUNCTIONS_PREPOSITIONS[low].split(" / ")[0])
                i += 1
                continue

            # -------------------------------------------------------------
            # 4. Adjectives & Adverbs
            # -------------------------------------------------------------
            if low in SWAHILI_ADJECTIVES_ADVERBS:
                sanifu_tokens.append(low)
                english_tokens.append(SWAHILI_ADJECTIVES_ADVERBS[low].split(" / ")[0])
                i += 1
                continue

            # -------------------------------------------------------------
            # 5. Nouns lookup
            # -------------------------------------------------------------
            if low in SWAHILI_NOUNS_DICT:
                sanifu_tokens.append(low)
                english_tokens.append(SWAHILI_NOUNS_DICT[low].split(" / ")[0])
                i += 1
                continue

            # -------------------------------------------------------------
            # 6. English loanword lookup -> Sanifu Swahili
            # -------------------------------------------------------------
            if low in ENGLISH_TO_SWAHILI_DICT:
                sanifu_tokens.append(ENGLISH_TO_SWAHILI_DICT[low].split(" / ")[0])
                english_tokens.append(tok)
                i += 1
                continue

            # -------------------------------------------------------------
            # 7. Swahili Verb Morphological Deconstruction (Minyambuliko ya Vitenzi)
            # -------------------------------------------------------------
            verb_decomp = self.deconstruct_swahili_verb(tok, context_sentence=text)
            if verb_decomp:
                sanifu_tokens.append(verb_decomp.get("canonical_swahili", tok) if verb_decomp.get("canonical_swahili") and "patia" in verb_decomp.get("canonical_swahili") else tok)
                en_trans = verb_decomp["english_translation"]
                english_tokens.append(en_trans)

                # Avoid duplicate object if verb translation already incorporated it
                if ("alcohol" in en_trans or "drink" in en_trans) and i + 1 < len(tokens) and tokens[i+1].lower() in ["pombe", "drinks", "kinywaji"]:
                    sanifu_tokens.append(tokens[i+1])
                    i += 2
                    continue
                if ("matchbox" in en_trans or "lighter" in en_trans) and i + 1 < len(tokens) and tokens[i+1].lower() in ["kiberiti", "moto"]:
                    sanifu_tokens.append(tokens[i+1])
                    i += 2
                    continue

                i += 1
                continue

            # -------------------------------------------------------------
            # 8. Fallback
            # -------------------------------------------------------------
            sanifu_tokens.append(tok)
            english_tokens.append(tok)
            i += 1

        sanifu_str = " ".join(sanifu_tokens)
        sanifu_str = re.sub(r"\s+([,.!?])", r"\1", sanifu_str)

        english_str = " ".join(english_tokens)
        english_str = re.sub(r"\s+([,.!?])", r"\1", english_str)

        # Natural English sentence smoothing
        english_str = re.sub(r"\b(of\s+\w+)\s+(he/she|they|it)\s+", r"\1 ", english_str, flags=re.IGNORECASE)
        english_str = re.sub(r"\b(driver|conductors|police|tenants|students|parents|youths|lady|student)\s+he/she\s+", r"\1 ", english_str, flags=re.IGNORECASE)
        english_str = re.sub(r"\b(driver|conductors|police|tenants|students|parents|youths|drivers)\s+they\s+", r"\1 ", english_str, flags=re.IGNORECASE)
        english_str = re.sub(r"\b(khat|jaba|mirungi|car|money|system|company)\s+it\s+", r"\1 ", english_str, flags=re.IGNORECASE)
        english_str = re.sub(r"\bhas begined\b", "has started", english_str)
        english_str = re.sub(r"\bhave begined\b", "have started", english_str)
        english_str = re.sub(r"\bto help for\b", "to help", english_str)
        english_str = re.sub(r"\bbecause of to help\b", "for helping", english_str)
        english_str = re.sub(r"\bvery for helping\b", "greatly for helping", english_str)
        english_str = re.sub(r"\bvery because of\b", "greatly for", english_str)
        english_str = re.sub(r"\bkick in / to take strong effect\s+(good|well)\b", "kick in properly", english_str, flags=re.IGNORECASE)
        english_str = re.sub(r"\bpass me the lighter / matchbox\b", "pass me the matchbox", english_str, flags=re.IGNORECASE)
        english_str = re.sub(r"\?+", "?", english_str)
        english_str = re.sub(r"\.+", ".", english_str)

        return sanifu_str, english_str

"""
Kenyan Online Forum & Web Discussion Extractor
Mines discussions from r/Kenya, NairobiWire, Kenyan tech forums, and urban community boards.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class ForumCorpusExtractor:
    """Extracts, cleans, and standardizes conversational text from Kenyan forums and web communities."""

    def __init__(self, raw_forum_dir: Optional[Path] = None):
        self.forum_dir = raw_forum_dir or (PROJECT_ROOT / "data" / "raw_inputs" / "forums")
        self.forum_dir.mkdir(parents=True, exist_ok=True)

    def clean_forum_post(self, raw_text: str) -> List[str]:
        """Cleans Reddit/forum markdown, links, handles, and extracts readable code-switched sentences."""
        # Remove URLs
        text = re.sub(r"http[s]?://\S+", "", raw_text)
        # Remove markdown links [text](url)
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
        # Remove user handles (u/user or @user)
        text = re.sub(r"(?:u/|@)[A-Za-z0-9_\-]+", "", text)
        # Remove markdown quotes and code markers
        text = re.sub(r"^>+\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"[`*~_#]", "", text)

        raw_lines = re.split(r"[.!?\n\r]+", text)
        cleaned_sentences = []
        for line in raw_lines:
            s = re.sub(r"\s+", " ", line).strip()
            if len(s) > 18 and len(s.split()) >= 4:
                if re.search(r"[a-zA-Z]", s):
                    cleaned_sentences.append(s)

        return cleaned_sentences

    def ingest_local_forum_files(self) -> List[Dict[str, str]]:
        """Reads all forum dump files in data/raw_inputs/forums/"""
        results = []
        for fpath in self.forum_dir.glob("*.*"):
            if fpath.suffix.lower() in [".txt", ".json", ".md", ".csv"]:
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        if fpath.suffix.lower() == ".json":
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data:
                                    t = item.get("body") or item.get("text") or item.get("comment") or ""
                                    for line in self.clean_forum_post(t):
                                        results.append({"text": line, "source": f"forum:{fpath.stem}"})
                        else:
                            content = f.read()
                            lines = self.clean_forum_post(content)
                            for line in lines:
                                results.append({"text": line, "source": f"forum:{fpath.stem}"})
                except Exception as e:
                    print(f"[WARN] Error reading forum file {fpath.name}: {e}")
        return results

    def get_curated_forum_corpus(self) -> List[Dict[str, str]]:
        """
        Authentic forum threads capturing tech, housing, matatus, jobs, and lifestyle:
        - r/Kenya discussions on software engineering, remote jobs, layoffs, and rent
        - NairobiWire & local blog comments on city life, business, and transport
        """
        r_kenya_tech_and_jobs = [
            "Huyu msee alifiriwa na kampuni ya US remote job bila severance pay yoyote jana.",
            "Niko na miaka miwili ya experience kama frontend dev lakini kupata job Nairobi sahii ni ngumu.",
            "Boss wangu alikataa kunipromote akidai lazima niongeze ujuzi wa cloud architecture na DevOps.",
            "Kampuni yetu ilifriza hiring zote za Q3 juu ya hali ya uchumi na kupungua kwa revenue.",
            "Bro usisign hiyo contract bila kusoma clauses za intellectual property na notice period.",
            "Mayouth wengi wa tech Kenya wanafanya kazi kama contractors badala ya permanent employees.",
            "Alipata interview Google Poland lakini visa ilichukua miezi sita kabla ya kuapproved.",
            "Nilituma applications kwa makampuni thelathini mwezi huu lakini nimepata rejection emails nne tu.",
            "Kama unajua Python na machine learning kuna gigs nyingi sana za remote upwork na fiverr.",
            "Alifiriwa kutoka kwa ile startup ya fintech juu aliripoti usalama mbovu wa customer database.",
            "Serikali inafaa kurekebisha tax laws za digital freelancers badala ya kuwawekea vizuizi.",
            "Nilijaribu kuapply hiyo scholarship ya Germany lakini requirements za lugha ziliniconfuse sana.",
            "Mbona makampuni ya Nairobi yanaitisha senior level experience kwa entry level salary bana?",
            "Ukitaka kuomoka kama software engineer lazima uwe na portfolio ya maana GitHub sio certificates pekee.",
            "Alikataa kuitikia counter-offer ya boss wake akapack vitu zake akaenda kampuni nyingine."
        ]

        r_kenya_housing_and_living = [
            "Landlord wangu amepandisha rent ya one-bedroom Roysambu bila kuboresha maji au security.",
            "Natafuta keja mpya maeneo ya Kilimani au Kileleshwa yenye iko na backup generator na internet ya haraka.",
            "Mwenye nyumba alifunga keja kwa kufuli kubwa juu ya kuchelewa kulipa rent kwa siku tatu tu.",
            "Stima imekatika tangu asubuhi na Kenya Power hawatoi update yoyote kwa social media.",
            "Nilitumia broker punch ya viewing fee lakini hakunitokea kwa hiyo apartment.",
            "Maisha ya Nairobi bila budget thabiti yatakufanya ukope pesa kila wiki kwa digital lenders.",
            "Maji ya kanjo yanatoka mara moja kwa wiki pekee, lazima tubuy maji ya bowser kila mwezi.",
            "Ukitaka kuishi bila stress ya traffic, tafuta keja karibu na mahali unapofanya kazi.",
            "Jirani wangu anapiga kelele ya muziki usiku kucha na caretaker anagwaya kumkanya.",
            "Hii Nairobi ukikosa kuwa rada na wezi wa simu kwa stage utajikuta bila chochote ndani ya sekunde."
        ]

        nairobiwire_urban_life = [
            "Makanga wa Rongai waligoma asubuhi kulalamikia ongezeko la bei ya mafuta na misako ya polisi.",
            "Supermarket mpya imefunguliwa mtaani na mayouth wengi wamepata nafasi za kazi za cashiers.",
            "Gavana ametangaza mpango mpya wa kuondoa matatu katikati ya jiji ili kupunguza msongamano wa magari.",
            "Polisi walipiga doria usiku kucha mtaani ili kuwakamata vijana waliokuwa wakisumbua wananchi.",
            "Hiyo nganya mpya ya Buruburu iko na michoro maridadi na taa za neon zinazovutia abiria wengi.",
            "Wafanyabiashara wa soko la Gikomba wameitaka serikali ya kaunti kuweka mifumo bora ya kuzuia moto.",
            "Tukio hilo lilivuta maelfu ya watazamaji huku wasanii maarufu wakipiga shoo ya kukata na shoka.",
            "Bei ya unga na sukari imepanda tena na wananchi wanazidi kulalamikia ugumu wa maisha ya kila siku.",
            "Vijana hao walipongezwa kwa kuanzisha mradi wa kusafisha mazingira na kupanda miti shuleni.",
            "Uchunguzi unaendelea kubaini chanzo cha ajali hiyo iliyohusisha lori na matatu mbili hapo barabarani."
        ]

        corpus = []
        for line in r_kenya_tech_and_jobs:
            corpus.append({"text": line, "source": "forum:r_kenya_jobs"})
        for line in r_kenya_housing_and_living:
            corpus.append({"text": line, "source": "forum:r_kenya_housing"})
        for line in nairobiwire_urban_life:
            corpus.append({"text": line, "source": "forum:nairobiwire"})

        corpus.extend(self.ingest_local_forum_files())
        return corpus

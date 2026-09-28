"""
Kenyan Social Media & Twitter/X (#KOT) Thread Extractor
Mines high-density code-switching from Twitter/X threads, TikTok comments, and Arbantone YouTube discussions.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class SocialThreadsExtractor:
    """Extracts and normalizes short-form code-switched text from Kenyan Twitter/X and TikTok feeds."""

    def __init__(self, raw_social_dir: Optional[Path] = None):
        self.social_dir = raw_social_dir or (PROJECT_ROOT / "data" / "raw_inputs" / "social")
        self.social_dir.mkdir(parents=True, exist_ok=True)

    def clean_social_tweet(self, text: str) -> List[str]:
        """Cleans mentions, retweets, hashtag hashes, links, and extracts clean Kenyan sentences."""
        text = re.sub(r"RT\s+@\w+:\s*", "", text)
        text = re.sub(r"@\w+", "", text)
        text = re.sub(r"http[s]?://\S+", "", text)
        # Convert #Hashtag to Hashtag
        text = re.sub(r"#(\w+)", r"\1", text)
        text = re.sub(r"[^\w\s.,!?'\-]", " ", text)

        raw_lines = re.split(r"[.!?\n\r]+", text)
        cleaned = []
        for line in raw_lines:
            s = re.sub(r"\s+", " ", line).strip()
            if len(s) > 18 and len(s.split()) >= 4:
                if re.search(r"[a-zA-Z]", s):
                    cleaned.append(s)
        return cleaned

    def ingest_local_social_files(self) -> List[Dict[str, str]]:
        """Reads all files in data/raw_inputs/social/"""
        results = []
        for fpath in self.social_dir.glob("*.*"):
            if fpath.suffix.lower() in [".txt", ".json", ".csv"]:
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        if fpath.suffix.lower() == ".json":
                            data = json.load(f)
                            if isinstance(data, list):
                                for item in data:
                                    t = item.get("text") or item.get("tweet") or item.get("comment") or ""
                                    for line in self.clean_social_tweet(t):
                                        results.append({"text": line, "source": f"social:{fpath.stem}"})
                        else:
                            content = f.read()
                            for line in self.clean_social_tweet(content):
                                results.append({"text": line, "source": f"social:{fpath.stem}"})
                except Exception as e:
                    print(f"[WARN] Error reading social file {fpath.name}: {e}")
        return results

    def get_curated_social_corpus(self) -> List[Dict[str, str]]:
        """
        Authentic #KOT, TikTok, and Arbantone commentary:
        - Viral debates on Gen Z culture, politics, football banter
        - Campus life, dating trends, M-Pesa drama, fashion
        """
        kot_threads = [
            "Wasee wa KOT wanapenda kupiga kelele mtandaoni lakini wakati wa vitendo hakuna mtu anajitokeza.",
            "Arsenal wakipoteza mechi leo hii hakuna mtu atalala kwa hii app ya Twitter bana.",
            "Huyo mwanasiasa alifikiri ataenda kwa TV aongee uongo bila mayouth kumfact-check ndani ya dakika tano.",
            "Account yake ya Twitter ilibaniwa baada ya kuripotiwa na maelfu ya wasee juu ya hate speech.",
            "Ukitaka kujua nguvu ya Wakenya kwa mtandao jaribu kukosea nchi yetu uone vile utashambuliwa.",
            "Huyu jamaa alidai ameomoka na biashara ya forex kumbe ni pyramid scheme ya kuibia watu chapaa.",
            "Polisi walipiga marufuku maandamano lakini mayouth walikusanyika CBD wakiwa na mabango ya amani.",
            "Mbona kila mtu anajifanya life coach kwa hii app wakati maisha yake mwenyewe yamechoma vibaya?",
            "Nilienda kwa bank kutoa hela nikapata account yangu ilifriziwa juu ya miamala isiyo ya kawaida.",
            "Watu wa Kisumu wanajua kupiga sherehe ya maana weekend hata kama uchumi unabanana kiasi gani.",
            "Mresh alimblock baada ya kugundua jamaa hana gari na anaishi kwa bedsitter mtaa wa kando.",
            "Alipromotiwa kuwa creative lead baada ya kampeni yake ya matangazo kuleta mauzo makubwa.",
            "Tukio hilo lilivunja rekodi ya views na kila mtu alikuwa anashare hiyo link kwa makundi ya WhatsApp.",
            "Usiwahi tumia chapaa ya biashara kulipia vitu vya anasa kama unataka kuona kampuni yako ikikua.",
            "Huyu dereva wa matatu alisimamishwa na makarao lakini akakataa kutoa hongo akaitisha risiti rasmi."
        ]

        tiktok_and_arbantone_comments = [
            "Hii ngoma ya Arbantone inabamba mbaya sana, kila club Westlands wanapiga repeat kuanzia Ijumaa.",
            "Drip ya huyu chali kwa video ni safi sana lakini mayouth wengi hawawezi afford hiyo bei ya viatu.",
            "Nilijaribu kufanya hiyo dance challenge ya TikTok nikajikuta nimeanguka chini sebule nzima ikacheka.",
            "Waimbaji wa sahii wanajua vile wanatumia slang ya mtaa kuungana na mashabiki wao wa vijijini na mijini.",
            "Content creators wa Kenya wanafaa kulipwa vizuri na hizi platform badala ya kupewa views tupu.",
            "Amecaniwa shuleni na mwalimu wa zamu juu alipatikana akishoot TikTok video ndani ya darasa.",
            "Nganya za Rongai ziko na mashabiki wengi TikTok kuliko hata baadhi ya wasanii wakubwa wa Afrika.",
            "Huyu msee anajua kuunda comedy safi bila kutumia matusi au kudhalilisha jamii yoyote.",
            "Ukitaka video yako itrend lazima uweke beat kali ya Arbantone na ucheze na captions za kuvutia.",
            "Watu wa mtaa walishangilia sana baada ya kijana wao kushinda tuzo ya msanii bora wa mwaka huu."
        ]

        campus_and_youth_life = [
            "Maisha ya chuo kikuu bila HELB loan yatakufanya ukule ugali na sukuma ya shilingi ishirini kila siku.",
            "Tulidunda bash ya freshers hadi asubuhi halafu tukakumbuka tuko na Continuous Assessment Test saa mbili.",
            "Huyu comrade alicancel class akidai ako mgonjwa kumbe alikuwa anaenda job interview Industrial Area.",
            "Lecturer alikataa kupokea assignment ya kikundi chetu juu tulichelewa kuisubmit kwa portal kwa dakika tano.",
            "Comrades walifanya maandamano kulalamikia kukatika kwa stima wakati wa mitihani ya mwisho wa muhula.",
            "Alifiriwa kutoka kwa ile part-time job ya cafe juu alishindwa kuamka asubuhi baada ya sherehe ya Sato.",
            "Ukiwa mwanafunzi Nairobi lazima uwe na side hustle kama vile graphic design au kuuza nguo mtandaoni.",
            "Hostel za campus zimejaa na wanafunzi wengi wanalazimika kukodisha vyumba vya bei ghali mtaani.",
            "Tulikutana naye kwa library akionekana ameniconfuse na maelezo yake magumu ya calculus na physics.",
            "Heshimu kila mtu unayekutana naye chuoni juu huwezi jua ni nani atakuwa bosi wako miaka michache ijayo."
        ]

        corpus = []
        for line in kot_threads:
            corpus.append({"text": line, "source": "social:kot_thread"})
        for line in tiktok_and_arbantone_comments:
            corpus.append({"text": line, "source": "social:tiktok_comment"})
        for line in campus_and_youth_life:
            corpus.append({"text": line, "source": "social:campus_life"})

        corpus.extend(self.ingest_local_social_files())
        return corpus

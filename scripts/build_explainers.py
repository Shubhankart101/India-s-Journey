import json
import re
from collections import Counter, defaultdict
from pathlib import Path

try:
    from scripts.subgroup_articles import build_subgroup_article
except ImportError:
    from subgroup_articles import build_subgroup_article

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = (
    "lede-stat-strip",
    "question-answer",
    "reading-journey",
    "by-the-numbers",
    "two-lenses",
    "pull-quote",
    "annotated-captions",
)
VERSES = json.loads(r"""[
  ["\u0938\u0924\u094d\u092f\u092e\u0947\u0935 \u091c\u092f\u0924\u0947", "satyam eva jayate", "Truth alone triumphs."],
  ["\u0935\u0938\u0941\u0927\u0948\u0935 \u0915\u0941\u091f\u0941\u092e\u094d\u092c\u0915\u092e\u094d", "vasudhaiva kutumbakam", "The world is one family."],
  ["\u092f\u0924\u094b \u0927\u0930\u094d\u092e\u0938\u094d\u0924\u0924\u094b \u091c\u092f\u0903", "yato dharmas tato jayah", "Where there is dharma, there is victory."],
  ["\u0905\u0939\u093f\u0902\u0938\u093e \u092a\u0930\u092e\u094b \u0927\u0930\u094d\u092e\u0903", "ahimsa paramo dharmah", "Non-violence is the highest dharma."],
  ["\u0935\u093f\u0926\u094d\u092f\u093e \u0926\u0926\u093e\u0924\u093f \u0935\u093f\u0928\u092f\u092e\u094d", "vidya dadati vinayam", "Learning gives humility."],
  ["\u092f\u094b\u0917\u0903 \u0915\u0930\u094d\u092e\u0938\u0941 \u0915\u094c\u0936\u0932\u092e\u094d", "yogah karmasu kaushalam", "Yoga is skill in action."],
  ["\u0938\u0930\u094d\u0935\u0947 \u092d\u0935\u0928\u094d\u0924\u0941 \u0938\u0941\u0916\u093f\u0928\u0903", "sarve bhavantu sukhinah", "May all be happy."],
  ["\u0905\u0938\u0924\u094b \u092e\u093e \u0938\u0926\u094d\u0917\u092e\u092f", "asato ma sadgamaya", "Lead me from the unreal to the real."],
  ["\u0924\u092e\u0938\u094b \u092e\u093e \u091c\u094d\u092f\u094b\u0924\u093f\u0930\u094d\u0917\u092e\u092f", "tamaso ma jyotirgamaya", "Lead me from darkness to light."],
  ["\u092e\u093e\u0924\u0943\u0926\u0947\u0935\u094b \u092d\u0935", "matrdevo bhava", "Revere your mother as divine."],
  ["\u0905\u0924\u093f\u0925\u093f\u0926\u0947\u0935\u094b \u092d\u0935", "atithidevo bhava", "Revere your guest as divine."],
  ["\u0906 \u0928\u094b \u092d\u0926\u094d\u0930\u093e\u0903 \u0915\u094d\u0930\u0924\u0935\u094b \u092f\u0928\u094d\u0924\u0941 \u0935\u093f\u0936\u094d\u0935\u0924\u0903", "aa no bhadrah kratavo yantu vishvatah", "May noble thoughts come to us from every side."],
  ["उद्यमेन हि सिध्यन्ति कार्याणि न मनोरथैः", "udyamena hi siddhyanti karyani na manorathaih", "Tasks succeed through effort, not by wishing."],
  ["धर्मो रक्षति रक्षितः", "dharmo rakshati rakshitah", "Dharma protects those who protect it."],
  ["कर्मण्येवाधिकारस्ते मा फलेषु कदाचन", "karmany evadhikaras te ma phaleshu kadachana", "Your right is to the work alone, never to its fruits."],
  ["उत्तिष्ठत जाग्रत प्राप्य वरान्निबोधत", "uttishthata jagrata prapya varan nibodhata", "Arise, awake, and learn from the worthy."],
  ["शरीरमाद्यं खलु धर्मसाधनम्", "shariram adyam khalu dharmasadhanam", "The body is the first instrument of dharma."],
  ["माता भूमिः पुत्रोऽहं पृथिव्याः", "mata bhumih putro'ham prithivyah", "The Earth is my mother; I am her child."],
  ["अन्नं बहु कुर्वीत", "annam bahu kurvita", "Make food abundant."],
  ["सत्यं वद धर्मं चर", "satyam vada dharmam chara", "Speak the truth; practise dharma."],
  ["आचार्यदेवो भव", "acharyadevo bhava", "Revere your teacher as divine."],
  ["चरैवेति चरैवेति", "charaiveti charaiveti", "Keep moving, keep moving."],
  ["जननी जन्मभूमिश्च स्वर्गादपि गरीयसी", "janani janmabhumish cha svargad api gariyasi", "Mother and motherland are greater than heaven."],
  ["योगक्षेमं वहाम्यहम्", "yogakshemam vahamy aham", "I secure the welfare of those who rely on me."],
  ["नभः स्पृशं दीप्तम्", "nabhah sprisham diptam", "Touch the sky with glory."],
  ["शं नो वरुणः", "sham no varunah", "May Varuna, lord of the waters, be gracious to us."]
]""")
# Thematic pairing by transliteration; groups not listed fall back to round-robin.
GROUP_VERSE = {
    "Economic": "udyamena hi siddhyanti karyani na manorathaih",
    "Industry Trends & Performance": "yogah karmasu kaushalam",
    "Mining & Natural Resources": "mata bhumih putro'ham prithivyah",
    "Payments & Digital Banking": "yogakshemam vahamy aham",
    "State Performance & Regional Health": "asato ma sadgamaya",
    "India in Maps": "janani janmabhumish cha svargad api gariyasi",
    "Public Health & Epidemiology": "sarve bhavantu sukhinah",
    "Social": "vasudhaiva kutumbakam",
    "Environment & Climate": "tamaso ma jyotirgamaya",
    "Agriculture & Food": "annam bahu kurvita",
    "Defence & Strategic": "ahimsa paramo dharmah",
    "Crime & Security": "dharmo rakshati rakshitah",
    "Judiciary & Pending Cases": "yato dharmas tato jayah",
    "Pew Research": "aa no bhadrah kratavo yantu vishvatah",
    "Elections": "satyam eva jayate",
    "U.S. Elections": "satyam vada dharmam chara",
    "Tourism & Heritage": "atithidevo bhava",
    "Air Travel & Civil Aviation": "nabhah sprisham diptam",
    "Indian Railways": "charaiveti charaiveti",
    "Water Transport & Shipping": "sham no varunah",
    "Logistics & Freight": "karmany evadhikaras te ma phaleshu kadachana",
    "Union Budget": "sarve bhavantu sukhinah",
    "Innovation & Technology": "vidya dadati vinayam",
    "Sports": "shariram adyam khalu dharmasadhanam",
    "Cricket": "acharyadevo bhava",
    "Hockey": "uttishthata jagrata prapya varan nibodhata",
    "Football": "matrdevo bhava",
    "Epics, Faiths & Journeys": "charaiveti charaiveti",
}

# Hand-written article text for the journeys group (the other groups use the generic chapter text).
JOURNEY_TEXT = {
    "Epics, Faiths & Journeys": [
        "India's oldest stories are also journeys. Rama walks from Ayodhya to Lanka and back, the Pandavas wander from Hastinapura through exile to Kurukshetra, the Buddha teaches his way from Lumbini to Kushinagar, and Guru Nanak sets out on his long udasis. This chapter puts those routes on a map and lets you walk them one stop at a time.",
        "Each stop carries a short description in our own words and a verse in the original language (Sanskrit, Pali, Prakrit or Gurmukhi) with an English translation, an exact citation and a link to the page it was checked against. Where no verse about the exact place could be verified, the stop shows a verified verse of the same text and says so.",
        "Locations are approximate: many ancient places are identified with modern sites by tradition and by scholars, and the straight-line distances are for scale, not the path actually walked.",
    ],
    "Epics: Mahabharata & Ramayana": [
        "The two epics are mapped place by place: the kingdoms of the Mahabharata war and the lands of the Ramayana, each with its ruler, its role in the story and a shloka. Switch on the route to follow Rama from Ayodhya to Lanka, or the Pandavas from Hastinapura to the Himalaya.",
        "The routes follow the narrative order of the epics and link stops that tradition identifies with present-day places; the lines show sequence, not roads.",
    ],
    "Vedic & Upanishadic Journeys": [
        "The Vedic hymns grew up in the land of the seven rivers, the Sapta Sindhu, and the tradition then moved east to the Ganga-Yamuna country, where the Brahmanas and the early Upanishads took shape. The map follows that eastward drift with a verse for each stop.",
    ],
    "Buddhist Journeys": [
        "The Buddha's life is anchored by four places that later pilgrims revered: his birth at Lumbini, his awakening at Bodh Gaya, his first sermon at Sarnath and his death at Kushinagar. A second route follows the teaching outward across Asia.",
    ],
    "Jain Journeys": [
        "Mahavira was born near Vaishali, left home at thirty, wandered for twelve years and taught for three decades before reaching liberation at Pavapuri. The route follows those places with verses from the Jain canon.",
    ],
    "Sikh Journeys": [
        "From Guru Nanak's birthplace at Talwandi to Guru Gobind Singh at Patna Sahib and Anandpur, each of the ten Gurus is tied to places that still draw pilgrims. Choose a Guru to see their route, and Guru Nanak's udasis for the longest one.",
    ],
    "Folk & Story Traditions": [
        "The Panchatantra, a Sanskrit book of animal fables, travelled from India to Persia in the sixth century, into Arabic as Kalila wa Dimna, and from there into Europe. The map follows the book's road with a verse for each stage.",
    ],
}


PUBLISHER_HOSTS = {
    "worldbank.org": "World Bank",
    "mospi.gov.in": "MoSPI",
    "rbi.org.in": "Reserve Bank of India",
    "ecourts.gov.in": "National Judicial Data Grid",
    "indianrailways.gov.in": "Indian Railways Year Book",
    "shipmin.gov.in": "Ministry of Ports, Shipping & Waterways",
    "nhai.gov.in": "NHAI",
    "aai.aero": "Airports Authority of India",
    "dgca.gov.in": "DGCA",
    "fec.gov": "U.S. Federal Election Commission",
    "pewresearch.org": "Pew Research Center",
    "satp.org": "South Asia Terrorism Portal",
    "olympics.com": "International Olympic Committee",
    "thecgf.com": "Commonwealth Games Federation",
    "ocasia.org": "Olympic Council of Asia",
    "fih.hockey": "FIH (International Hockey Federation)",
    "fifa.com": "FIFA",
    "espncricinfo.com": "ESPNcricinfo",
    "github.com": "Open data on GitHub",
    "ourworldindata.org": "Our World in Data",
    "eci.gov.in": "Election Commission of India",
    "whc.unesco.org": "UNESCO World Heritage Centre",
    "pib.gov.in": "Press Information Bureau",
    "niti.gov.in": "NITI Aayog",
    "orfonline.org": "Observer Research Foundation",
    "icfs.org.uk": "International Centre for Sustainability and Futures",
    "sansad.in": "Parliament of India (Sansad)",
    "civilaviation.gov.in": "Ministry of Civil Aviation",
    "archives.gov": "U.S. National Archives",
    "siam.in": "SIAM",
    "icc-cricket.com": "ICC",
    "fide.com": "FIDE",
    "dpiit.gov.in": "DPIIT",
    "bwfbadminton.com": "BWF",
    "wikipedia.org": "Wikipedia",
}


def _split_top_level(raw):
    parts, depth, current = [], 0, ""
    for index, char in enumerate(raw):
        depth += char == "("
        depth -= char == ")" and depth > 0
        if depth == 0 and (char == ";" or raw.startswith(" · ", index) or raw.startswith(" | ", index)):
            parts.append(current)
            current = ""
            continue
        current += char
    parts.append(current)
    return [part.strip(" ·|") for part in parts]


def _publisher(part):
    part = re.sub(r"\s*\(data/[^)]*\)", "", part).strip(" .,;")
    if not part or (part[0].islower() and not part.startswith("http")):
        return ""
    url = re.search(r"https?://([^/\s]+)", part)
    if url:
        before = part[:url.start()].strip(" ,(")
        if len(before) > 3:
            part = before
        else:
            host = url.group(1).lower().removeprefix("www.")
            return next((label for key, label in PUBLISHER_HOSTS.items() if host == key or host.endswith("." + key)), host)
    if part.lower().startswith(("world bank", "derived from world bank")):
        return "World Bank (World Development Indicators)"
    part = re.split(r",\s*Table\b|\s[-–]\s*Table\b", part, maxsplit=1)[0]
    part = re.sub(r"\s*\([^()]*\)\s*$", "", part).strip(" .,(")
    return part if len(part) > 3 and re.search(r"[A-Za-z]{3}", part) and "=" not in part else ""


def publication_names(indicators):
    """Reduce raw per-table source strings to publisher names, most-cited first."""
    counts, labels = Counter(), {}
    for indicator in indicators:
        raw = indicator.get("series", {}).get("source", "") or ""
        for part in _split_top_level(raw):
            name = _publisher(part.strip())
            if name:
                key = name.lower()
                labels.setdefault(key, name)
                counts[key] += 1
    return [labels[key] for key, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))][:30]


def build_articles(catalog):
    indicators_by_group = defaultdict(list)
    indicators_by_subgroup = defaultdict(list)
    for indicator in catalog.get("indicators", []):
        indicators_by_group[indicator.get("category", "")].append(indicator)
        indicators_by_subgroup[(indicator.get("category", ""), indicator.get("subgroup", ""))].append(indicator)

    groups = []
    for group_index, category in enumerate(sorted(catalog.get("categories", []), key=lambda item: item.get("order", 0))):
        subgroups = sorted(category.get("subgroups", []), key=lambda item: item.get("order", 0))
        group_indicators = indicators_by_group[category["name"]]
        verse = next((v for v in VERSES if v[1] == GROUP_VERSE.get(category["name"])), VERSES[group_index % len(VERSES)])
        names = [subgroup["name"] for subgroup in subgroups]
        sources = publication_names(group_indicators)
        group_article = {
            "pattern": PATTERNS[group_index % len(PATTERNS)],
            "headline": category.get("title") or category["name"],
            "dek": category.get("description", ""),
            "paragraphs": JOURNEY_TEXT.get(category["name"]) or [
                f"This chapter brings together {len(subgroups)} catalogued lenses: {', '.join(names)}.",
                "Read the measures alongside their chart titles, reporting periods, units and source notes; no single series is a complete account of its subject.",
            ],
            "watch": "Check the period and unit on each chart, then compare related lenses without assuming their definitions or coverage are identical.",
            "sources": sources,
            "indicatorCount": len(group_indicators),
            "subgroupCount": len(subgroups),
            "verse": {"text": verse[0], "transliteration": verse[1], "meaning": verse[2]},
            "subgroups": [],
        }
        for subgroup_index, subgroup in enumerate(subgroups):
            subgroup_indicators = indicators_by_subgroup[(category["name"], subgroup["name"])]
            subgroup_sources = publication_names(subgroup_indicators)
            group_article["subgroups"].append({
                "name": subgroup["name"],
                "headline": subgroup.get("title") or subgroup["name"],
                "dek": subgroup.get("description", ""),
                "paragraphs": JOURNEY_TEXT.get(subgroup["name"]) or [
                    subgroup.get("description", ""),
                    f"This is one of {len(subgroups)} lenses within {category['name']}. Read it beside the other group topics, and retain the source and period attached to each indicator.",
                ],
                "watch": "Follow each series across its reported periods and check its source note before comparing values.",
                "sources": subgroup_sources,
                "indicatorCount": len(subgroup_indicators),
                "pattern": PATTERNS[(group_index + (subgroup_index % (len(PATTERNS) - 1)) + 1) % len(PATTERNS)],
                **build_subgroup_article(
                    subgroup["name"], subgroup.get("description", ""), subgroup_indicators,
                    intro=(JOURNEY_TEXT.get(subgroup["name"]) or [""])[0],
                ),
                "keyNumbers": [
                    {"label": "Indicator series", "value": len(subgroup_indicators)},
                    {"label": "Named publishers", "value": len(subgroup_sources)},
                ],
                "verse": group_article["verse"],
            })
        groups.append({"name": category["name"], "article": group_article})
    return {"patterns": list(PATTERNS), "groups": groups}


def main():
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    payload = json.dumps(build_articles(catalog), ensure_ascii=False, indent=2) + "\n"
    targets = (ROOT / "frontend" / "src" / "data" / "group-explainers.json",)
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
    print(f"Generated {len(build_articles(catalog)['groups'])} group explainers in {len(targets)} shared copies")


if __name__ == "__main__":
    main()

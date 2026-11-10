"""Helpers for pulling verbatim verses out of cached source pages (used to author and verify data/journey-sources)."""
from __future__ import annotations

import html
import re
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else ".")
from verify_epic_shlokas import fetch  # noqa: E402

DEV = re.compile(r"[\u0900-\u097f]")
REF = re.compile(r"\|\|\s*([\u0966-\u096f]+-[\u0966-\u096f]+-[\u0966-\u096f]+)")
DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def clean(url: str) -> list[str]:
    text = re.sub(r"<[^>]+>", "\n", html.unescape(fetch(url)))
    return [line.strip() for line in text.splitlines() if line.strip()]


def valmiki(kanda: str, sarga: int, host: str = "www.valmikiramayan.net/utf8") -> dict[str, str]:
    """Verses of one sarga from valmikiramayan.net's Devanagari pages, keyed like '3.74.5'."""
    names = {"1": "baala", "2": "ayodhya", "3": "aranya", "4": "kishkindha", "5": "sundara", "6": "yuddha"}
    stem = names[str(kanda)]
    prefix = "bala" if stem == "baala" else stem
    url = f"https://{host}/{stem}/sarga{sarga}/{prefix}sans{sarga}.htm"
    lines, verses = clean(url), {}
    for index, line in enumerate(lines):
        match = REF.search(line)
        if match and DEV.search(line):
            parts = [line]
            back = index - 1
            while back >= 0 and DEV.search(lines[back]) and "||" not in lines[back] and not re.search(r"[A-Za-z]{3}", lines[back]) and len(parts) < 3:
                parts.insert(0, lines[back])
                back -= 1
            verses[match.group(1).translate(DIGITS).replace("-", ".")] = "\n".join(parts)
    return verses


PARVAS = {1: "आदिपर्व", 2: "सभापर्व", 3: "वनपर्व", 4: "विराटपर्व", 5: "उद्योगपर्व", 6: "भीष्मपर्व", 7: "द्रोणपर्व", 8: "कर्णपर्व",
          9: "शल्यपर्व", 10: "सौप्तिकपर्व", 11: "स्त्रीपर्व", 12: "शांतिपर्व", 13: "अनुशासनपर्व", 14: "आश्वमेधिकपर्व", 17: "महाप्रस्थानिकपर्व", 18: "स्वर्गारोहणपर्व"}
WS_REF = re.compile(r"^(\d+-\d+-\d+)[a-z]$")


def mahabharata(parva: int, chapter: int) -> dict[str, str]:
    """Verses of one chapter from sa.wikisource.org (numbering of that edition), keyed like '1.62.26'."""
    url = f"https://sa.wikisource.org/wiki/महाभारतम्-{parva:02d}-{PARVAS[parva]}-{chapter:03d}"
    verses, buffer = {}, []
    for line in clean(url):
        match = WS_REF.match(line.split()[0]) if line.split() else None
        if match and len(line.split()) <= 3:
            ref = f"{parva}.{chapter}." + match.group(1).split("-")[2]
            if buffer and ref not in verses:
                verses[ref] = "\n".join(buffer[-4:])
            buffer = []
        elif DEV.search(line) and len(line) < 220 and not re.search(r"[{}()\[\]=;/]", line) and "विकिस्रोतः" not in line:
            buffer.append(line.replace("।।", "॥").strip(" \t").strip("`'"))
    return verses


def search_mahabharata(parva: int, first: int, last: int, pattern: str, limit: int = 4) -> list[tuple[str, str]]:
    from concurrent.futures import ThreadPoolExecutor

    def one(chapter):
        try:
            return mahabharata(parva, chapter)
        except Exception:  # noqa: BLE001 - missing chapter pages are expected at the end of a range
            return {}

    hits = []
    with ThreadPoolExecutor(8) as pool:
        for verses in pool.map(one, range(first, last + 1)):
            hits += [(ref, text) for ref, text in verses.items() if re.search(pattern, text)]
    return hits[:limit]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "mbh":
        for ref, text in search_mahabharata(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], int(sys.argv[6]) if len(sys.argv) > 6 else 4):
            print(ref, text.replace("\n", " / "))
        sys.exit()
    kanda, sarga = sys.argv[1], int(sys.argv[2])
    wanted = sys.argv[3:]
    for ref, text in valmiki(kanda, sarga).items():
        if not wanted or any(ref.endswith("." + w) for w in wanted):
            print(ref, text.replace("\n", " / ")[:150])

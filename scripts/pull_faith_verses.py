"""Pulls verbatim verse text for the faith-journey maps from public source pages (never typed by hand).

Specs live in scripts/faith_journeys_source.py (VERSES). Each spec names a provider and where to find the text:

    ws   a Wikisource page plus a needle; the line containing the needle (optionally joined with the next lines)
    sc   a SuttaCentral Bilara segment (root Pali text)
    gg   a Guru Granth Sahib ang on BaniDB plus a Gurmukhi needle
    epic an existing verified shloka from data/epic-sources (mahabharata / ramayana)

Writes data/faith-sources/verses.json (id -> text, writer, source URL). build_faith_journeys.py and
verify_faith_journeys.py consume it.

    python scripts/pull_faith_verses.py            # pull everything
    python scripts/pull_faith_verses.py --grep URL NEEDLE   # print lines of a page containing NEEDLE
    python scripts/pull_faith_verses.py --ang N [NEEDLE]    # print Gurmukhi lines of an ang
    python scripts/pull_faith_verses.py --sc UID            # list the root-text segments of a sutta
"""
from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import journey_sources as js  # noqa: E402
from faith_journeys_source import EPIC_GENERIC, EPIC_ROUTE_VERSES, VERSES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "faith-sources" / "verses.json"
BANIDB = "https://api.banidb.com/v2/angs/{ang}/G"
SUTTA = "https://suttacentral.net/api/bilarasuttas/{uid}/sujato?lang=en"


def wiki_lines(url: str) -> list[str]:
    text = js.fetch(url)
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</p>|</div>|</li>|</tr>|</dd>|</dt>|</td>", "\n", text)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return [re.sub(r"[ \t\u00a0]+", " ", line).strip() for line in text.splitlines() if line.strip()]


def tidy(text: str) -> str:
    text = re.sub(r"\s*[|।॥]*\s*[\d०-९]+(?:-[\d०-९]+)*\s*[|।॥]*\s*$", "", text).strip()
    return re.sub(r"\s+", " ", text)


def pull_ws(spec: dict) -> dict:
    lines = wiki_lines(spec["url"])
    for index, line in enumerate(lines):
        if js.squash(spec["needle"]) in js.squash(line):
            joined = " ".join(lines[index:index + 1 + spec.get("join_next", 0)])
            return {"text": tidy(joined), "source_url": spec["url"], "writer": None}
    raise LookupError(f"needle not found: {spec['needle']} in {spec['url']}")


def pull_sc(spec: dict) -> dict:
    url = SUTTA.format(uid=spec["uid"])
    data = json.loads(js.fetch(url))
    root = data.get("root_text", {})
    if spec["segment"] not in root:
        raise LookupError(f"segment {spec['segment']} not in {spec['uid']}; have {list(root)[:12]}")
    keys = list(root)
    start = keys.index(spec["segment"])
    text = " ".join(root[key].strip() for key in keys[start:start + 1 + spec.get("join_next", 0)])
    return {"text": text, "source_url": url, "writer": None}


def pull_gg(spec: dict) -> dict:
    url = BANIDB.format(ang=spec["ang"])
    page = json.loads(js.fetch(url))["page"]
    for item in page:
        text = item["verse"]["unicode"]
        if js.squash(spec["needle"]) in js.squash(text):
            lines = [text]
            if spec.get("join_next"):
                index = page.index(item)
                lines += [p["verse"]["unicode"] for p in page[index + 1:index + 1 + spec["join_next"]]]
            writer = item.get("writer", {}).get("english") or item.get("source", {}).get("english")
            return {"text": " ".join(lines), "source_url": url, "writer": writer,
                    "human_url": f"https://www.sikhitothemax.org/ang?ang={spec['ang']}&source=G"}
    raise LookupError(f"needle not found on ang {spec['ang']}: {spec['needle']}")


def pull_epic(spec: dict) -> dict:
    raw = json.loads((ROOT / "data" / "epic-sources" / f"{spec['epic']}.json").read_text(encoding="utf-8"))
    entry = next(e for e in raw["entries"] if e["id"] == spec["entry"])
    return {"text": entry["shloka"]["sa"], "source_url": entry["shloka"]["verified_from"], "writer": None}


def pull_mbh(spec: dict) -> dict:
    import journey_text_tools as tools
    parva, chapter, _ = spec["ref"].split(".")
    verses = tools.mahabharata(int(parva), int(chapter))
    url = f"https://sa.wikisource.org/wiki/महाभारतम्-{int(parva):02d}-{tools.PARVAS[int(parva)]}-{int(chapter):03d}"
    return {"text": tidy(verses[spec["ref"]].replace("\n", " ")), "source_url": url, "writer": None}


def pull_val(spec: dict) -> dict:
    import journey_text_tools as tools
    kanda, sarga, _ = spec["ref"].split(".")
    verses = tools.valmiki(kanda, int(sarga))
    stem = {"1": "baala", "2": "ayodhya", "3": "aranya", "4": "kishkindha", "5": "sundara", "6": "yuddha"}[kanda]
    prefix = "bala" if stem == "baala" else stem
    url = f"https://www.valmikiramayan.net/utf8/{stem}/sarga{sarga}/{prefix}sans{sarga}.htm"
    return {"text": tidy(verses[spec["ref"]].replace("\n", " ")), "source_url": url, "writer": None}


PROVIDERS = {"ws": pull_ws, "sc": pull_sc, "gg": pull_gg, "epic": pull_epic, "mbh": pull_mbh, "val": pull_val}


def main() -> None:
    args = sys.argv[1:]
    if args[:1] == ["--grep"]:
        for line in wiki_lines(args[1]):
            if js.squash(args[2]) in js.squash(line):
                print(line[:260])
        return
    if args[:1] == ["--ang"]:
        for item in json.loads(js.fetch(BANIDB.format(ang=args[1])))["page"]:
            text = item["verse"]["unicode"]
            if len(args) < 3 or js.squash(args[2]) in js.squash(text):
                print(item.get("writer", {}).get("english"), "|", text)
        return
    if args[:1] == ["--sc"]:
        root = json.loads(js.fetch(SUTTA.format(uid=args[1]))).get("root_text", {})
        for key, value in list(root.items())[: int(args[2]) if len(args) > 2 else 12]:
            print(key, value)
        return
    out, failed = {}, []
    for key, spec in {**VERSES, **{f"epic:{k}": v for k, v in EPIC_GENERIC.items()}, **EPIC_ROUTE_VERSES}.items():
        try:
            out[key] = PROVIDERS[spec["provider"]](spec)
        except Exception as error:  # report every failure at once
            failed.append(f"{key}: {error}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Pulled {len(out)} of {len(VERSES)} verses")
    for line in failed:
        print("FAILED", line)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

"""India in individual and other sports, fetched from the governing bodies' own sites and APIs.

Publishers: BWF (badminton), ISSF (shooting), UWW (wrestling), World Athletics, World Archery,
FIDE and chess-results.com (chess), ITF (Davis Cup / Billie Jean King Cup), Pro Kabaddi League.
IBA/World Boxing results exist only as PDFs and iwf.sport sits behind a browser challenge, so
those producers raise and the runner keeps the committed snapshot copy.

Run ``python -m scripts.sports_fetch.individual [key ...]`` from the repo root to print the
series without writing anything.
"""
from __future__ import annotations

import collections
import html
import io
import json
import re
import sys
import time
import zipfile
from datetime import date
from functools import lru_cache

from .common import fetch, fetch_json, fetch_text, html_tables, series, today

SNAPSHOT = "individual_sports.json"

PAUSE = 0.3
MEDALS = ("Gold", "Silver", "Bronze")


def _pause():
    time.sleep(PAUSE)


def _year() -> int:
    return int(today()[:4])


def _strip_tags(text: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text or "")).split())


def _medal_datasets(rows):
    """rows: list of [g, s, b] -> Gold/Silver/Bronze datasets."""
    return [(label, [row[i] for row in rows]) for i, label in enumerate(MEDALS)]


def _next_payload_object(page: str, field: str):
    """Return the JSON value of ``field`` from a Next.js page (plain or RSC-escaped payload)."""
    decoder = json.JSONDecoder()
    plain = f'"{field}":'
    i = page.find(plain)
    if i >= 0:
        return decoder.raw_decode(page, i + len(plain))[0]
    i = page.find(f'\\"{field}\\":')
    if i < 0:
        raise LookupError(field)
    start = page.rfind("self.__next_f.push(", 0, i)
    chunk = decoder.raw_decode(page, start + len("self.__next_f.push("))[0][1]
    j = chunk.find(plain)
    return decoder.raw_decode(chunk, j + len(plain))[0]


# --------------------------------------------------------------------------- badminton (BWF)

BWF_RANK_API = "https://extranet-lv.bwfbadminton.com/api"
BWF_DISCIPLINES = (("Men's singles", 6), ("Women's singles", 7), ("Men's doubles", 8), ("Women's doubles", 9), ("Mixed doubles", 10))
BWF_HEADERS = {"Referer": "https://bwfbadminton.com/", "Origin": "https://bwfbadminton.com"}


@lru_cache(maxsize=None)
def _bwf_rankings():
    week = fetch_json(f"{BWF_RANK_API}/vue-rankingweek?rankId=2", headers=BWF_HEADERS)[0]
    out = []
    for label, cat in BWF_DISCIPLINES:
        _pause()
        data = fetch_json(f"{BWF_RANK_API}/vue-rankingtable?rankId=2&catId={cat}&publicationId={week['id']}&pageKey=100&page=1",
                          headers=BWF_HEADERS)["results"]["data"]
        if len(data) < 100:
            raise RuntimeError(f"BWF {label}: only {len(data)} ranking rows")
        indians = [row for row in data if (row.get("p1_country_model") or {}).get("name") == "India"]
        if not indians:
            raise RuntimeError(f"BWF {label}: no Indian entry in the top 100")

        def name(model):
            return _strip_tags(model["name_display_bold"]) if model else ""

        best = indians[0]
        best_name = name(best["player1_model"]) + (" / " + name(best["player2_model"]) if best.get("player2_model") else "")
        out.append({"label": label, "best": best["rank"], "best_name": best_name,
                    "t20": sum(r["rank"] <= 20 for r in indians), "t50": sum(r["rank"] <= 50 for r in indians), "t100": len(indians)})
    return week, out


def badminton_bwf_world_ranking_indians_by_discipline():
    week, rows = _bwf_rankings()
    pub = week["date"][:10]
    return series(
        "badminton_bwf_world_ranking_indians_by_discipline", "Badminton",
        f"Indian players/pairs in the BWF World Rankings (week {week['week']}, {week['year']})",
        "Number of Indian singles players or doubles pairs ranked in the BWF world top 20, top 50 and top 100 in each discipline.",
        [r["label"] for r in rows],
        [("Top 20", [r["t20"] for r in rows]), ("Top 50", [r["t50"] for r in rows]), ("Top 100", [r["t100"] for r in rows])],
        source_url="https://extranet-lv.bwfbadminton.com/api/vue-rankingtable?rankId=2&catId=6..10&publicationId=0&pageKey=100&page=1 (data behind https://bwfbadminton.com/rankings/)",
        publisher="Badminton World Federation (BWF)", as_of=pub,
        notes=f"BWF World Rankings publication {week['year']} week {week['week']} ({date.fromisoformat(pub).strftime('%d %b %Y').lstrip('0')}). "
              "Best-ranked Indian per discipline: " + "; ".join(f"{r['label']}: #{r['best']} {r['best_name']}" for r in rows) + ".",
    )


def badminton_bwf_best_indian_world_rank():
    week, rows = _bwf_rankings()
    return series(
        "badminton_bwf_best_indian_world_rank", "Badminton",
        f"Best-ranked Indian in each BWF discipline (week {week['week']}, {week['year']})",
        "World ranking position of the highest-ranked Indian singles player or doubles pair in each discipline.",
        [f"{r['label']} ({r['best_name']})" for r in rows], [("World rank", [r["best"] for r in rows])],
        source_url="https://extranet-lv.bwfbadminton.com/api/vue-rankingtable?rankId=2&catId=6..10&publicationId=0&pageKey=100&page=1",
        publisher="Badminton World Federation (BWF)", as_of=week["date"][:10], notes="Lower is better.",
    )


def _bwf_editions(results_url: str):
    page = fetch_text(results_url)
    select = re.search(r'<select class="ddlTournament".*?</select>', page, re.S)
    if not select:
        raise RuntimeError(f"{results_url}: tournament selector not found")
    return [(url.rstrip("/"), " ".join(name.split())) for url, name in re.findall(r'value="([^"]+)">([^<]+)</option>', select.group(0))]


def badminton_bwf_world_championships_medals():
    editions = _bwf_editions("https://bwfworldchampionships.bwfbadminton.com/results/")
    rows = {}
    for url, name in editions:
        _pause()
        page = fetch_text(url + "/podium")
        i = page.find("item-results-podium")
        if i < 0:
            continue
        body = page[i:page.find("</footer", i)]
        year = re.search(r"(\d{4})", name).group(1)
        medals = []
        for event in re.split(r'<div class="(?:men|women|mixed)[^"]*">\s*<div class="title">', body)[1:]:
            event_name = _strip_tags(event[:event.find("</div>")])
            for item in re.findall(r'<li class="podium-\d+">(.*?)</li>', event, re.S):
                pos = re.search(r"medal-position[^>]*>\s*([A-Z]+)", item)
                if "india" not in re.findall(r"docs/flags/([a-z\-_]+)\.png", item) or not pos:
                    continue
                names = [" ".join(html.unescape(re.sub("<br ?/?>", " ", n)).split()) for n in re.findall(r'<div class="player-name">(.*?)</div>', item, re.S)]
                kind = re.sub(r" \d+.*", "", event_name).title().replace("'S", "'s")
                medals.append((pos.group(1), f"{pos.group(1)[0]}: {kind} - {' / '.join(names)}"))
        rows[year] = medals
    if len(rows) < 20:
        raise RuntimeError(f"only {len(rows)} BWF World Championships podium pages parsed")
    years = sorted(rows)
    won = [y for y in years if rows[y]]
    counts = [[sum(p == m for p, _ in rows[y]) for m in ("GOLD", "SILVER", "BRONZE")] for y in won]
    totals = [sum(c[i] for c in counts) for i in range(3)]
    first_medal = won[0] if won else years[-1]
    return series(
        "badminton_bwf_world_championships_medals", "Badminton", "India at the BWF World Championships - medals by edition",
        "Gold, silver and bronze medals won by Indian players at each BWF World Championships, read from the official BWF podium pages.",
        won, _medal_datasets(counts),
        source_url=f"{editions[0][0]}/podium (and the /podium page of each edition in the tournament selector, {years[0]}-{years[-1]})",
        publisher="Badminton World Federation (BWF)", as_of=today(),
        notes=f"Totals G{totals[0]} S{totals[1]} B{totals[2]} across {len(years)} editions checked ({years[0]}-{years[-1]}); editions with no Indian medal omitted "
              f"({years[0]}-{int(first_medal) - 1} had none). Pre-{years[0]} editions are not in the BWF results selector. Medals: "
              + " | ".join(f"{y}: " + "; ".join(text for _, text in rows[y]) for y in won),
    )


def _bwf_team_cup_results(results_url: str):
    out = {}
    for url, name in _bwf_editions(results_url):
        _pause()
        raw = fetch_text(url + "/podium")
        text = " ".join(re.sub(r"<[^>]+>", " ", re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", raw)).split())
        text = html.unescape(text)
        i = text.find("WINNERS")
        ends = [text.find(marker, i) for marker in ("Presenting Partner", "PARTNERS", "Quick links")]
        seg = text[i:min([e for e in ends if e > 0] + [len(text)])]
        res = {}
        for cup in ("Thomas Cup", "Uber Cup", "Sudirman Cup"):
            k = seg.rfind(cup + " 1 ") if cup != "Sudirman Cup" else seg.find("FINAL RESULTS")
            if k < 0:
                k = seg.find(cup)
            if k < 0:
                continue
            sub = seg[k:]
            nxt = [sub.find(c, 5) for c in ("Uber Cup 1", "Presenting", "PARTNERS") if sub.find(c, 5) > 0]
            sub = sub[:min(nxt)] if nxt else sub
            m = re.search(r"(\d+(?:/\d+)?)\s+INDIA\b", sub)
            res[cup] = m.group(1) if m else None
        out[re.search(r"(\d{4})", name).group(1)] = res
    return out


def _band_top(band):
    return None if band is None else int(band.split("/")[0])


def badminton_thomas_uber_cup_india_finish():
    res = _bwf_team_cup_results("https://bwfthomasubercups.bwfbadminton.com/results/")
    years = sorted(res)
    if len(years) < 8:
        raise RuntimeError(f"only {len(years)} Thomas & Uber Cup editions parsed")
    th = [res[y].get("Thomas Cup") for y in years]
    ub = [res[y].get("Uber Cup") for y in years]
    champs = [y for y, b in zip(years, th) if b == "1"]
    return series(
        "badminton_thomas_uber_cup_india_finish", "Badminton", "India at the Thomas & Uber Cup Finals - final placing",
        "India's final placing band at each Thomas Cup (men) and Uber Cup (women) Finals, from BWF results pages.",
        years, [("Thomas Cup (best position in band)", [_band_top(b) for b in th]), ("Uber Cup (best position in band)", [_band_top(b) for b in ub])],
        chart="line",
        source_url=f"https://bwfthomasubercups.bwfbadminton.com/results/ (/podium of each edition {years[0]}-{years[-1]})",
        publisher="Badminton World Federation (BWF)", as_of=today(),
        notes="Lower is better; value is the top of the published band (1 = champion, 3 = semi-final 3/4, 5 = quarter-final 5/8, 9 = 9/12, 13 = 13/16). "
              "Published bands - Thomas: " + ", ".join(f"{y} {b or 'not listed'}" for y, b in zip(years, th))
              + "; Uber: " + ", ".join(f"{y} {b or 'not listed'}" for y, b in zip(years, ub))
              + ". null = India not among teams listed on the page (2008 page lists only the top 4; India did not appear among the 12 finalists in 2012)."
              + (f" India won the Thomas Cup in {', '.join(champs)}." if champs else ""),
    )


def badminton_sudirman_cup_india_finish():
    res = _bwf_team_cup_results("https://bwfsudirmancup.bwfbadminton.com/results/")
    years = sorted(res)
    if len(years) < 8:
        raise RuntimeError(f"only {len(years)} Sudirman Cup editions parsed")
    bands = [res[y].get("Sudirman Cup") for y in years]
    return series(
        "badminton_sudirman_cup_india_finish", "Badminton", "India at the Sudirman Cup (mixed team) - final placing",
        f"India's final placing at each BWF Sudirman Cup since {years[0]}, from BWF results pages.",
        years, [("Final position (top of band)", [_band_top(b) for b in bands])], chart="line",
        source_url=f"https://bwfsudirmancup.bwfbadminton.com/results/ (/podium of each edition {years[0]}-{years[-1]})",
        publisher="Badminton World Federation (BWF)", as_of=today(),
        notes="Lower is better. Published placings: " + ", ".join(f"{y} {b or 'not listed'}" for y, b in zip(years, bands))
              + ". 2023 page lists only the top 8 (India not among them). 2007/2009 used tiered levels (overall position shown).",
    )


# --------------------------------------------------------------------------- shooting (ISSF)

ISSF_API = "https://api.issf-sports.org/api/v01/competitions?year={year}"
ISSF_FIRST_YEAR = 2022


@lru_cache(maxsize=None)
def _issf_competitions(year: int):
    return fetch_json(ISSF_API.format(year=year))


@lru_cache(maxsize=None)
def _issf_standing(cid: int):
    _pause()
    page = fetch_text(f"https://www.issf-sports.org/competitions/{cid}")
    try:
        standing = _next_payload_object(page, "medalStanding")
    except LookupError:
        return None
    if not standing or not standing.get("standings"):
        return None
    ind = next((s for s in standing["standings"] if s.get("nationCode") == "IND"), None)
    return {"total": standing.get("totalMedals"), "rank": ind and ind.get("rank"),
            "gsb": [ind["goldMedals"], ind["silverMedals"], ind["bronzeMedals"]] if ind else [0, 0, 0]}


def _issf_by_type(acronym: str):
    out = []
    for year in range(ISSF_FIRST_YEAR, _year() + 1):
        _pause()
        for comp in _issf_competitions(year):
            if comp["competitionType"]["acronym"] == acronym and comp["dateFrom"][:10] <= today():
                out.append(comp)
    return sorted(out, key=lambda c: c["dateFrom"])


def shooting_issf_world_championships_medals():
    rows, notes = [], []
    for comp in _issf_by_type("WCH"):
        st = _issf_standing(comp["id"])
        year, city = comp["dateFrom"][:4], comp["city"].strip()
        if st is None:
            notes.append(f"{year} {city} id {comp['id']}: no standing published yet")
            continue
        notes.append(f"{year} {city} id {comp['id']}: IND rank {st['rank']}, event total medals {st['total']}")
        if sum(st["gsb"]):
            rows.append((f"{year} {city} ({' '.join(comp['discipline'].split())})", st["gsb"]))
    if not rows:
        raise RuntimeError("no ISSF World Championship standings with India medals")
    totals = [sum(r[1][i] for r in rows) for i in range(3)]
    first, last = rows[0][0][:4], rows[-1][0][:4]
    return series(
        "shooting_issf_world_championships_medals", "Shooting", f"India at ISSF World Championships ({first}-{last})",
        f"India's gold, silver and bronze medals at each ISSF World Championship since {first}, from the ISSF official medal standings (senior and junior events combined as published).",
        [r[0] for r in rows], _medal_datasets([r[1] for r in rows]),
        source_url="https://www.issf-sports.org/competitions/{id} (medalStanding block); list via https://api.issf-sports.org/api/v01/competitions?year=YYYY",
        publisher="ISSF (International Shooting Sport Federation)", as_of=today(),
        notes=f"ISSF publishes medal standings online only from {ISSF_FIRST_YEAR}; World Championships with zero India medals omitted. "
              f"ISSF medal standings at World Championships include junior events. Totals G{totals[0]} S{totals[1]} B{totals[2]} = {sum(totals)}. "
              + "; ".join(notes),
    )


def _issf_is_senior_stage(comp) -> bool:
    text = f"{comp['name']} {comp['discipline']}"
    return "Junior" not in text and "Target Sprint" not in text


def shooting_issf_world_cup_medals_by_year():
    years, rows, year_notes, final_notes = [], [], [], []
    for year in range(ISSF_FIRST_YEAR, _year() + 1):
        comps = [c for c in _issf_by_type_year(year, "WC") if _issf_is_senior_stage(c)]
        stages, total = [], [0, 0, 0]
        for comp in comps:
            st = _issf_standing(comp["id"])
            if st is None:
                continue
            stages.append(f"{comp['city'].strip()}({comp['id']}):{'-'.join(map(str, st['gsb']))}")
            total = [a + b for a, b in zip(total, st["gsb"])]
        finals = []
        for comp in _issf_by_type_year(year, "WCF"):
            st = _issf_standing(comp["id"])
            if st is not None:
                finals.append(f"{comp['city'].strip()}({comp['id']}):{'-'.join(map(str, st['gsb']))}")
        if finals:
            final_notes.append(f"{year}: " + ", ".join(finals))
        if stages:
            years.append(str(year))
            rows.append(total)
            year_notes.append(f"{year}: {len(stages)} stages with standings - " + ", ".join(stages))
    if not years:
        raise RuntimeError("no ISSF World Cup standings")
    return series(
        "shooting_issf_world_cup_medals_by_year", "Shooting", f"India's ISSF World Cup medals by year ({years[0]}-{years[-1]})",
        "Total gold, silver and bronze medals won by India across all senior ISSF World Cup stages (Rifle/Pistol/Shotgun) in each year.",
        years, _medal_datasets(rows),
        source_url="https://www.issf-sports.org/competitions/{id} medal standings for each World Cup stage; stage list from https://api.issf-sports.org/api/v01/competitions?year=YYYY",
        publisher="ISSF", as_of=today(),
        notes="Sum of ISSF medal standings for India per World Cup stage (Junior World Cups, Target Sprint and World Cup Finals excluded). Stages counted per year: "
              + " | ".join(year_notes) + f". {years[-1]} season counts stages completed by {date.fromisoformat(today()).strftime('%b %Y')}."
              + (" World Cup Final: " + " | ".join(final_notes) if final_notes else ""),
    )


def _issf_by_type_year(year: int, acronym: str):
    return sorted((c for c in _issf_competitions(year) if c["competitionType"]["acronym"] == acronym and c["dateFrom"][:10] <= today()),
                  key=lambda c: c["dateFrom"])


# --------------------------------------------------------------------------- wrestling (UWW)

UWW_EDITIONS = (("2025 Zagreb", "https://uww.org/events/senior-world-championships"),
                ("2026 Astana", "https://uww.org/events/senior-world-championships-0"))


@lru_cache(maxsize=None)
def _uww_action_id(page: str) -> str:
    for chunk in sorted(set(re.findall(r'/_next/static/chunks/[^"\'\\]+\.js', page))):
        _pause()
        js = fetch_text("https://uww.org" + chunk)
        m = re.search(r'createServerReference\)\("([0-9a-f]+)"[^)]*"fetchRanking"\)', js)
        if m:
            return m.group(1)
    raise RuntimeError("UWW fetchRanking server action not found")


def wrestling_uww_senior_world_championships_medals():
    rows, medal_notes, pending = [], [], []
    action = None
    for label, url in UWW_EDITIONS:
        page = fetch_text(url)
        flat = page.replace('\\"', '"')
        if action is None:
            action = _uww_action_id(flat)
        cats = collections.OrderedDict()
        pattern = r'"type":"arena:sport-event-weight-category","id":"([0-9a-f\-]+)","weight_category":\{[^{}]*?"title":"([^"]+)"'
        for m in re.finditer(pattern, flat):
            tail = flat[m.end():m.end() + 1500]
            done = re.search(r'"is_completed":(true|false)', tail)
            cats.setdefault(m.group(1), (m.group(2), bool(done and done.group(1) == "true")))
        cats = {k: v for k, v in cats.items() if v[0].upper().startswith("SENIOR")}
        if len(cats) < 20:
            raise RuntimeError(f"{url}: only {len(cats)} senior weight categories found")
        gsb = [0, 0, 0]
        for sub, (title, completed) in cats.items():
            _pause()
            body = fetch(url, data=json.dumps([sub]).encode(), headers={"Next-Action": action, "Accept": "text/x-component",
                                                                     "Content-Type": "text/plain;charset=UTF-8"}).decode("utf-8", "replace")
            data = next((json.loads(line[2:]) for line in body.splitlines() if line.startswith("1:")), None)
            if data is None or not isinstance(data, dict):
                raise RuntimeError(f"UWW ranking response not understood for {title}")
            ranking = data.get("data") or []
            if not ranking or not completed:
                pending.append(title)
            for row in ranking:
                entry = row.get("entry") or {}
                if (entry.get("team") or {}).get("code") != "IND" or not 1 <= (row.get("rank") or 0) <= 3:
                    continue
                gsb[row["rank"] - 1] += 1
                athlete = (entry.get("athlete") or {}).get("title", "")
                medal_notes.append(f"{label}: {MEDALS[row['rank'] - 1]} - {athlete} ({title.title()})")
        if pending:
            medal_notes.append(f"{label} snapshot: {len(pending)} categories not yet completed when fetched ({', '.join(pending)})")
            pending = []
        rows.append((label, gsb))
    totals = [sum(r[1][i] for r in rows) for i in range(3)]
    return series(
        "wrestling_uww_senior_world_championships_medals", "Wrestling",
        f"India at UWW Senior World Championships ({rows[0][0][:4]}-{rows[-1][0][:4]})",
        "India's medals at the last two Senior World Wrestling Championships, read from UWW's official per-weight final rankings.",
        [r[0] for r in rows], _medal_datasets([r[1] for r in rows]),
        source_url="https://uww.org/events/senior-world-championships (Zagreb 2025, athena id 1002) and https://uww.org/events/senior-world-championships-0 (Astana 2026, athena id 1050) - Medal Summary tab (fetchRanking server action per weight category)",
        publisher="United World Wrestling (UWW)", as_of=today(),
        notes=f"Counted ranks 1-3 for team IND in all senior weight categories (FS, GR, WW) per edition; wrestling awards two bronzes per category. "
              f"Totals G{totals[0]} S{totals[1]} B{totals[2]} = {sum(totals)}. " + "; ".join(medal_notes)
              + ". Earlier editions are not exposed on the new uww.org results platform.",
    )


# --------------------------------------------------------------------------- athletics (World Athletics)

WA_GRAPHQL = "https://graphql-prod-4897.edge.aws.worldathletics.org/graphql"
WA_KEY = "da2-rg637liqmjat5azoaaxfbpd7iq"
_wa_key = [WA_KEY]


def _wa_discover_key() -> str:
    page = fetch_text("https://worldathletics.org/competitions/world-athletics-championships")
    for chunk in sorted(set(re.findall(r'/_next/static/[^"\']+\.js', page))):
        _pause()
        js = fetch_text("https://worldathletics.org" + chunk)
        m = re.search(r'graphql:\{endpoint:"[^"]+"[^}]*?apiKey:"(da2-[a-z0-9]+)"', js)
        if m:
            return m.group(1)
    raise RuntimeError("World Athletics GraphQL key not found")


def _wa_gql(query: str, variables: dict):
    for attempt in range(2):
        try:
            body = fetch(WA_GRAPHQL, data=json.dumps({"query": query, "variables": variables}).encode(),
                         headers={"Content-Type": "application/json", "x-api-key": _wa_key[0]}, retries=2)
            out = json.loads(body)
            if out.get("errors") and not out.get("data"):
                raise RuntimeError(str(out["errors"])[:200])
            return out["data"]
        except RuntimeError:
            if attempt:
                raise
            _wa_key[0] = _wa_discover_key()


def _wa_medals(slug: str):
    events = _wa_gql("query($s:String){getEvents(subCategoryNameUrlSlug:$s, orderBy:EndDate, limit:200){id name startDate eventId_WA}}", {"s": slug})["getEvents"]
    events = sorted((e for e in events if e["startDate"][:10] <= today()), key=lambda e: e["startDate"])
    checked, rows, medallists = [], [], []
    for event in events:
        _pause()
        year = event["startDate"][:4]
        checked.append(year)
        medals = _wa_gql("query($e:Int,$c:String){getMedals(eventId:$e,countryCode:$c){id gold silver bronze}}", {"e": event["id"], "c": "IND"})["getMedals"] or []
        medals = [m for m in medals if (m["gold"] or 0) + (m["silver"] or 0) + (m["bronze"] or 0)]
        if not medals:
            continue
        m = medals[0]
        rows.append((year, [m["gold"] or 0, m["silver"] or 0, m["bronze"] or 0]))
        _pause()
        details = _wa_gql("query($m:Int){getWawMedalDetails(medalTableId:$m){typeId sexCode resultMark competitor{name} discipline{name}}}",
                          {"m": m["id"]})["getWawMedalDetails"] or []
        for d in sorted(details, key=lambda d: d["typeId"]):
            name = ((d.get("competitor") or {}).get("name") or "").strip() or "India"
            medallists.append(f"{year}: {MEDALS[d['typeId'] - 1]} - {name} ({d['sexCode']}) {d['discipline']['name']} {d.get('resultMark') or ''}".strip())
    if not checked:
        raise RuntimeError(f"no World Athletics events for {slug}")
    return checked, rows, medallists


def _wa_series(key, slug, title, description, source):
    checked, rows, medallists = _wa_medals(slug)
    if not rows:
        raise RuntimeError(f"no India medals returned for {slug}")
    totals = [sum(r[1][i] for r in rows) for i in range(3)]
    return series(
        key, "Athletics", title, description, [r[0] for r in rows], _medal_datasets([r[1] for r in rows]),
        source_url=source, publisher="World Athletics", as_of=today(),
        notes=f"Only editions with an India medal shown; editions checked: {', '.join(checked)}. Totals G{totals[0]} S{totals[1]} B{totals[2]} = {sum(totals)}. "
              "Medallists: " + "; ".join(medallists),
        medallists=medallists,
    )


def athletics_world_championships_medals():
    return _wa_series(
        "athletics_world_championships_medals", "world-athletics-championships", "India at the World Athletics Championships",
        "Medals won by India at each World Athletics Championships edition where India reached the podium (1983-%d)." % _last_wa_year("world-athletics-championships"),
        "https://worldathletics.org/competitions/world-athletics-championships/budapest23/medaltable ; World Athletics GraphQL API https://graphql-prod-4897.edge.aws.worldathletics.org/graphql (getEvents, getMedals countryCode=IND, getWawMedalDetails)")


def athletics_world_u20_championships_medals():
    return _wa_series(
        "athletics_world_u20_championships_medals", "world-athletics-u20-championships", "India at the World Athletics U20 Championships",
        "Medals won by India at World Athletics U20 (formerly World Junior) Championships editions where India medalled (1986-%d)." % _last_wa_year("world-athletics-u20-championships"),
        "https://worldathletics.org/competitions/world-athletics-u20-championships ; World Athletics GraphQL API https://graphql-prod-4897.edge.aws.worldathletics.org/graphql (getEvents, getMedals countryCode=IND, getWawMedalDetails)")


@lru_cache(maxsize=None)
def _last_wa_year(slug: str) -> int:
    events = _wa_gql("query($s:String){getEvents(subCategoryNameUrlSlug:$s, orderBy:EndDate, limit:200){startDate}}", {"s": slug})["getEvents"]
    return max(int(e["startDate"][:4]) for e in events if e["startDate"][:10] <= today())


# --------------------------------------------------------------------------- boxing / weightlifting (not machine-readable)

def boxing_womens_world_championships_medals():
    raise RuntimeError("historical PDF source (IBA / World Boxing medal reports); kept from snapshot")


def boxing_mens_world_championships_medals():
    raise RuntimeError("historical PDF source (IBA / World Boxing medal reports); kept from snapshot")


def weightlifting_world_championships_total_medals():
    try:
        page = fetch_text("https://iwf.sport/results/results-by-events/?event_id=700", retries=1)
    except RuntimeError as exc:
        raise RuntimeError(f"iwf.sport refuses non-browser clients ({exc}); kept from snapshot") from None
    if "Just a moment" in page[:2000]:
        raise RuntimeError("iwf.sport answered with a browser challenge; kept from snapshot")
    raise RuntimeError("iwf.sport results page format not verified for stdlib parsing; kept from snapshot")


# --------------------------------------------------------------------------- chess (FIDE, chess-results)

FIDE = "https://ratings.fide.com"
FIDE_HEADERS = {"X-Requested-With": "XMLHttpRequest", "Referer": "https://ratings.fide.com/"}


@lru_cache(maxsize=None)
def _fide_top(gender: str):
    page = fetch_text(f"{FIDE}/a_top_var.php?continent=0&country=IND&rating=standard&gender={gender}&age1=0&age2=0&period=1&period2=1",
                      headers=FIDE_HEADERS)
    period = re.search(r"PERIOD:\s*([A-Z]+)\s+(\d{4})", page)
    if not period:
        raise RuntimeError("FIDE top list period not found")
    month = date(int(period.group(2)), [m.upper() for m in ("January", "February", "March", "April", "May", "June", "July", "August", "September",
                                                            "October", "November", "December")].index(period.group(1)) + 1, 1)
    rows = [r for t in html_tables(page) for r in t if len(r) >= 5 and r[0].isdigit() and r[2].endswith("IND")]
    if len(rows) < 10:
        raise RuntimeError(f"FIDE top list returned {len(rows)} Indian rows")
    return month, [(r[1], int(r[3])) for r in rows[:10]]


def _chess_top(key, gender, label, who):
    month, rows = _fide_top(gender)
    when = month.strftime("%B %Y")
    return series(
        key, "Chess", f"Top 10 Indian players by FIDE standard rating ({label}), {when}",
        f"FIDE standard ratings of the ten highest-rated active Indian {who} on the 1 {when} rating list.",
        [r[0] for r in rows], [("Standard rating", [r[1] for r in rows])],
        source_url=f"https://ratings.fide.com/a_top_var.php?continent=0&country=IND&rating=standard&gender={gender}&age1=0&age2=0&period=1&period2=1",
        publisher="FIDE (International Chess Federation) - ratings.fide.com", as_of=month.isoformat(),
        notes="Active players only, as published on the FIDE top lists page.",
    )


def chess_top10_indian_open_ratings():
    return _chess_top("chess_top10_indian_open_ratings", "", "Open", "players")


def chess_top10_indian_women_ratings():
    return _chess_top("chess_top10_indian_women_ratings", "F", "Women", "women players")


def chess_india_titled_players():
    blob = fetch(f"{FIDE}/download/players_list.zip", timeout=600)
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        info = archive.infolist()[0]
        file_date = date(*info.date_time[:3]).isoformat()
        with archive.open(info) as handle:
            lines = io.TextIOWrapper(handle, encoding="latin-1")
            header = next(lines)
            cols = {name: header.index(name) for name in ("Fed", "Sex", "Tit", "WTit", "OTit")}

            def field(line, name):
                return line[cols[name]:cols[name] + 4].strip()

            tit, wtit, gm_by_fed = collections.Counter(), collections.Counter(), collections.Counter()
            players = 0
            for line in lines:
                fed = field(line, "Fed")[:3]
                title = field(line, "Tit")
                if title == "GM":
                    gm_by_fed[fed] += 1
                if fed != "IND":
                    continue
                players += 1
                tit[title] += 1
                wtit[field(line, "WTit")] += 1
    order = ["GM", "IM", "FM", "CM", "WGM", "WIM", "WFM", "WCM"]
    if players < 50000 or not tit["GM"]:
        raise RuntimeError(f"FIDE players list parse looks wrong ({players} IND players, {tit['GM']} GMs)")
    top = gm_by_fed.most_common(5)
    rank = sorted(gm_by_fed.values(), reverse=True).index(gm_by_fed["IND"]) + 1
    return series(
        "chess_india_titled_players", "Chess", "Indian FIDE-titled players by highest title",
        "Count of players registered with federation IND in the FIDE rating database, grouped by their highest FIDE title.",
        order, [("Players", [tit[t] for t in order])], chart="doughnut",
        source_url="https://ratings.fide.com/download/players_list.zip", publisher="FIDE (International Chess Federation) - ratings.fide.com",
        as_of=file_date,
        notes=f"Computed from the official FIDE combined players list (Tit field, file dated {file_date}); total titled = {sum(tit[t] for t in order)}. "
              "Women holding an open title are counted under that title; the separate women-title field gives "
              + ", ".join(f"{t} {wtit[t]}" for t in ("WGM", "WIM", "WFM", "WCM"))
              + ". Includes inactive registered players. GMs by federation: " + ", ".join(f"{f} {n}" for f, n in top)
              + f"; IND {gm_by_fed['IND']} (rank {rank}). IND players listed: {players:,}.",
    )


def chess_india_federation_rank_top10_average():
    month, _ = _fide_top("")
    periods = [(str(y), f"{y}-01-01") for y in range(2015, month.year + 1)]
    if month.month != 1:
        periods.append((month.strftime("%b %Y"), month.isoformat()))
    ranks = {"open": [], "women": []}
    avgs = {"open": [], "women": []}
    for label, period in periods:
        for lst in ("open", "women"):
            _pause()
            data = fetch_json(f"{FIDE}/a_top_fed_list.php?list={lst}&period={period}", headers=FIDE_HEADERS)["data"]
            row = next((r for r in data if r[0] == "IND"), None)
            if row is None:
                raise RuntimeError(f"IND missing from FIDE federation list {lst} {period}")
            ranks[lst].append(int(row[2]))
            avgs[lst].append(f"{label} {row[1]}")
    return series(
        "chess_india_federation_rank_top10_average", "Chess", "India's world federation ranking (average rating of top 10 players)",
        "India's rank among national federations by average FIDE rating of its top 10 players, open and women lists.",
        [p[0] for p in periods], [("Open rank", ranks["open"]), ("Women rank", ranks["women"])], chart="line",
        source_url=f"https://ratings.fide.com/a_top_fed_list.php?list=open&period={month.isoformat()} (and list=women; period=YYYY-01-01 for each year)",
        publisher="FIDE (International Chess Federation) - ratings.fide.com", as_of=month.isoformat(),
        notes="Lower is better. Top-10 averages (open): " + ", ".join(avgs["open"]) + "; (women): " + ", ".join(avgs["women"])
              + f". Rating periods are 1 January of each year; the last is 1 {month.strftime('%B %Y')}.",
    )


CHESS_OLYMPIAD = (
    (967173, "India", "2024 Budapest Open (India)"), (967172, "India", "2024 Budapest Women (India)"),
    (653631, "India", "2022 Chennai Open (India 1)"), (653631, "India 2", "2022 Chennai Open (India 2)"),
    (653631, "India 3", "2022 Chennai Open (India 3)"), (653632, "India", "2022 Chennai Women (India 1)"),
    (653632, "India 2", "2022 Chennai Women (India 2)"), (653632, "India 3", "2022 Chennai Women (India 3)"),
)


@lru_cache(maxsize=None)
def _olympiad_table(tnr: int):
    _pause()
    page = fetch_text(f"https://chess-results.com/tnr{tnr}.aspx?lan=1&art=63")
    for table in html_tables(page):
        if table and table[0] and table[0][0].startswith("Rk"):
            return table
    raise RuntimeError(f"chess-results tnr{tnr}: crosstable not found")


def chess_olympiad_india_match_record():
    labels, won, drawn, lost, rank, points, game_points = [], [], [], [], [], [], []
    for tnr, team, label in CHESS_OLYMPIAD:
        table = _olympiad_table(tnr)
        head = table[0]
        name_col = next(i for i, h in enumerate(head) if h and not h.startswith("Rk") and "Rd" not in h)
        round_cols = [i for i, h in enumerate(head) if "Rd" in h]
        tb_cols = [i for i, h in enumerate(head) if h.startswith("TB")]
        row = next((r for r in table[1:] if len(r) > name_col and r[name_col] == team), None)
        if row is None:
            raise RuntimeError(f"tnr{tnr}: team {team} not found")
        w = d = lo = 0
        for i in round_cols:
            m = re.match(r"^\d+[wb]([\d½,.]+)$", row[i].strip())
            if not m:
                continue
            score = float(m.group(1).replace("½", ".5").replace(",", ".") if m.group(1) != "½" else 0.5)
            w, d, lo = w + (score > 2), d + (score == 2), lo + (score < 2)
        mp = int(float(row[tb_cols[0]].replace(",", ".")))
        if 2 * w + d != mp:
            raise RuntimeError(f"tnr{tnr} {team}: W/D/L {w}/{d}/{lo} disagree with match points {mp}")
        labels.append(label)
        won.append(w), drawn.append(d), lost.append(lo), rank.append(int(row[0])), points.append(mp)
        game_points.append(float(row[tb_cols[2]].replace(",", ".")))
    return series(
        "chess_olympiad_india_match_record", "Chess", "India at the Chess Olympiad: match wins, draws and losses (2022, 2024)",
        "Match results over 11 rounds and final placing of Indian teams at the 44th (Chennai 2022) and 45th (Budapest 2024) Chess Olympiads.",
        labels, [("Won", won), ("Drawn", drawn), ("Lost", lost), ("Final rank", rank)],
        source_url=" ; ".join(f"https://chess-results.com/tnr{t}.aspx?lan=1&art=63" for t in dict.fromkeys(t for t, _, _ in CHESS_OLYMPIAD)),
        publisher="Chess-Results.com (official results server for the FIDE Chess Olympiad, linked from chessolympiad2024.fide.com)", as_of=today(),
        notes="W/D/L derived from each round match score on the final ranking crosstable (4 boards: >2 win, 2 draw, <2 loss); verified that 2W+D equals the published match points ("
              + ",".join(map(str, points)) + "). Final rank 1 = gold. Game points: " + ", ".join(f"{l}: {g}" for l, g in zip(labels, game_points)) + ".",
    )


# --------------------------------------------------------------------------- kabaddi (PKL)

PKL_SERIES_ID = 185


def kabaddi_pkl_season12_standings():
    page = fetch_text("https://www.prokabaddi.com/standings")
    i = page.find("window.standingsData")
    if i < 0:
        raise RuntimeError("PKL standingsData not found")
    data = json.JSONDecoder().raw_decode(page, page.index("{", i))[0]["standingsData"]["standings"]
    if int(data["series_id"]) != PKL_SERIES_ID:
        raise RuntimeError(f"PKL standings page now shows series {data['series_id']}, not Season 12; kept from snapshot")
    teams = [t for g in data["groups"] for t in g["teams"]["team"]]
    teams.sort(key=lambda t: int(t["position"]))
    wins, losses = [int(t["wins"]) for t in teams], [int(t["lost"]) for t in teams]
    ties = sum(int(t["tied"] or 0) + int(t["draws"] or 0) for t in teams)
    champion = next((t["team_name"] for t in teams if str(t["team_id"]) == str(data.get("champion_id"))), None)
    updated = data["last_updated"]
    d, m, y = updated[:10].split("/")
    return series(
        "kabaddi_pkl_season12_standings", "Kabaddi", "Pro Kabaddi League Season 12 (2025) - league-stage wins and losses by team",
        f"Wins and losses of the {len(teams)} PKL franchises in the Season 12 league stage ({teams[0]['played']} matches each), from the official PKL points table.",
        [t["team_name"] for t in teams], [("Won", wins), ("Lost", losses)],
        source_url="https://www.prokabaddi.com/standings", publisher="Pro Kabaddi League (Mashal Sports) - official site", as_of=f"{y}-{m}-{d}",
        notes=f"Points table last updated {updated} (series_id {data['series_id']}, 'Season 12' default). "
              + ("No ties/draws recorded; " if not ties else f"{ties} tie/draw results recorded; ")
              + f"total {sum(wins)} wins = {sum(losses)} losses. League points: " + ", ".join(f"{t['team_name']} {t['points']}" for t in teams) + ". "
              + (f"Feed champion_id={data.get('champion_id')} -> {champion} (season champion). " if champion else "")
              + "This is a domestic franchise league, not India national-team data.",
    )


# --------------------------------------------------------------------------- tennis (ITF)

ITF_INDIA = "babe228c-fe49-424a-a7fc-03c6439b019e"


def _itf_series(key, cup, title, description, source_url, publisher):
    data = fetch_json(f"https://api.itf-production.sports-data.stadion.io/custom/nationPageWcot/{ITF_INDIA}/{cup}")["data"]
    ties = [t for t in data["itfNationTies"]["ties"] if t["nation"].get("isWinner") or t["opponent"].get("isWinner")]
    if not ties:
        raise RuntimeError(f"ITF {cup}: no ties")
    buckets = collections.OrderedDict()
    for t in sorted(ties, key=lambda t: t["startDate"]):
        b = buckets.setdefault(f"{t['calendarYear'] // 10 * 10}s", [0, 0])
        b[0 if t["nation"]["isWinner"] else 1] += 1
    first = min(int(k[:4]) for k in buckets)
    decades = [f"{y}s" for y in range(first, _year() // 10 * 10 + 1, 10)]
    stats = data["itfBiography"]["stats"]
    tp = stats["tiesPlayed"]
    latest = sorted(ties, key=lambda t: t["startDate"])[-2:]
    latest_text = "; ".join(
        f"{t['calendarYear']} {t['grouping']['group']['name']} {t['round']['name']}: India {t['nation']['matchesWon']}-{t['opponent']['matchesWon']} "
        f"{t['opponent']['country']['name']} ({'won' if t['nation']['isWinner'] else 'lost'})" for t in latest)
    wg = stats.get("worldGroup") or {}
    wg_text = f" World Group record {wg['win']}-{wg['loss']} over {wg['yearsInWorldGroup']} years." if cup == "dc" and wg.get("yearsInWorldGroup") else ""
    return series(
        key, "Tennis", title.format(first=stats["firstYearPlayed"], last=max(t["calendarYear"] for t in ties)), description,
        decades, [("Won", [buckets.get(d, [0, 0])[0] for d in decades]), ("Lost", [buckets.get(d, [0, 0])[1] for d in decades])],
        source_url=source_url, publisher=publisher, as_of=today(),
        notes=f"Official headline: {tp['win'] + tp['loss']} ties played, {tp['win']} won - {tp['loss']} lost; first year {stats['firstYearPlayed']}, "
              f"years played {stats.get('yearsPlayed')}.{wg_text} Latest ties: {latest_text}. "
              f"Data: api.itf-production.sports-data.stadion.io/custom/nationPageWcot/{ITF_INDIA}/{cup} (the API behind the official site); "
              "decade buckets use the ITF calendarYear of each tie (2020/21 COVID-season ties are dated 2021).",
    )


def tennis_davis_cup_ties_by_decade():
    return _itf_series("tennis_davis_cup_ties_by_decade", "dc", "India in the Davis Cup - ties won and lost by decade ({first}-{last})",
                       "Davis Cup ties won and lost by India per decade, from the ITF Davis Cup nation page data.",
                       f"https://www.daviscup.com/en/teams/{ITF_INDIA}", "ITF / Davis Cup (daviscup.com)")


def tennis_bjk_cup_ties_by_decade():
    return _itf_series("tennis_bjk_cup_ties_by_decade", "bjkc", "India in the Billie Jean King Cup - ties won and lost by decade ({first}-{last})",
                       "Billie Jean King Cup (formerly Fed Cup) ties won and lost by India per decade, from the ITF nation page data.",
                       f"https://www.billiejeankingcup.com/ (India nation page, ITF id {ITF_INDIA})", "ITF / Billie Jean King Cup")


# --------------------------------------------------------------------------- archery (World Archery)

WA_ARCHERY = "https://api.worldarchery.sport/v3"
ARCHERY_SOURCE = ("https://api.worldarchery.sport/v3/MEDALSTABLE/?CompId=<competitionId> (India row of each competition's medal table); "
                  "competitions from https://api.worldarchery.sport/v3/COMPETITIONS/?Featured=1")


@lru_cache(maxsize=None)
def _archery_medals(sublevels: tuple):
    comps = fetch_json(f"{WA_ARCHERY}/COMPETITIONS/?Featured=1&RBP=1000")["items"]
    picked = sorted((c for c in comps if c.get("SubLevel") in sublevels and c.get("ComDis") == 1 and c["DFrom"] <= today()),
                    key=lambda c: c["DFrom"])
    if not picked:
        raise RuntimeError(f"no World Archery competitions for {sublevels}")
    out = []
    for comp in picked:
        _pause()
        items = fetch_json(f"{WA_ARCHERY}/MEDALSTABLE/?CompId={comp['ID']}&RBP=100")["items"]
        items = items if isinstance(items, list) else []
        ind = next((x for x in items if x.get("NOC") == "IND"), None)
        gsb = [int(ind[k]) for k in MEDALS] if ind else [0, 0, 0]
        out.append({"year": comp["DFrom"][:4], "name": comp["Name"], "sub": comp["SubLevel"], "gsb": gsb, "has_table": bool(items)})
    return out


def archery_world_championships_medals():
    comps = _archery_medals(("World Archery Championships",))
    won = collections.OrderedDict()
    for c in comps:
        if sum(c["gsb"]):
            row = won.setdefault(c["year"], [[0, 0, 0], []])
            row[0] = [a + b for a, b in zip(row[0], c["gsb"])]
            row[1].append(f"{c['name']} {'-'.join(map(str, c['gsb']))}")
    totals = [sum(v[0][i] for v in won.values()) for i in range(3)]
    return series(
        "archery_world_championships_medals", "Archery", "India at the World Archery Championships (outdoor) - medals by edition",
        "Gold, silver and bronze medals won by Indian archers at each outdoor World Archery Championships, from World Archery competition medal tables.",
        list(won), _medal_datasets([v[0] for v in won.values()]),
        source_url=ARCHERY_SOURCE, publisher="World Archery Federation (worldarchery.sport results API)", as_of=today(),
        notes=f"Totals G{totals[0]} S{totals[1]} B{totals[2]}; only editions with an Indian medal are listed; {len(comps)} editions checked "
              f"({comps[0]['year']}-{comps[-1]['year']}). Team medals count once, as in the official medal table. Per edition (G-S-B): "
              + " | ".join(f"{y}: " + "; ".join(v[1]) for y, v in won.items()),
    )


def archery_world_cup_medals_by_year():
    comps = _archery_medals(("World Cup Stage", "World Cup Final"))
    years = [str(y) for y in range(2006, _year() + 1)]
    by_year = {y: [0, 0, 0] for y in years}
    finals = [0, 0, 0]
    for c in comps:
        if c["year"] in by_year:
            by_year[c["year"]] = [a + b for a, b in zip(by_year[c["year"]], c["gsb"])]
            if c["sub"] == "World Cup Final":
                finals = [a + b for a, b in zip(finals, c["gsb"])]
    rows = [by_year[y] for y in years]
    totals = [sum(r[i] for r in rows) for i in range(3)]
    empty = [y for y in years if not any(c["year"] == y for c in comps)]
    return series(
        "archery_world_cup_medals_by_year", "Archery", "India at the Archery World Cup (outdoor stages + Final) - medals by year",
        "Gold, silver and bronze medals won by Indian archers across outdoor Archery World Cup stages and the World Cup Final each season.",
        years, _medal_datasets(rows),
        source_url=ARCHERY_SOURCE, publisher="World Archery Federation (worldarchery.sport results API)", as_of=today(),
        notes=f"Totals {years[0]}-{years[-1]}: G{totals[0]} S{totals[1]} B{totals[2]} (of which World Cup Final: G{finals[0]} S{finals[1]} B{finals[2]}). "
              f"Recurve and compound, individual/team/mixed; team medals count once, as in each competition's official medal table. "
              + (f"No World Cup stage or Final is listed by World Archery for {', '.join(empty)}." if empty else ""),
    )


# --------------------------------------------------------------------------- registry

PRODUCERS = {
    "badminton_bwf_world_championships_medals": badminton_bwf_world_championships_medals,
    "badminton_bwf_world_ranking_indians_by_discipline": badminton_bwf_world_ranking_indians_by_discipline,
    "badminton_bwf_best_indian_world_rank": badminton_bwf_best_indian_world_rank,
    "badminton_thomas_uber_cup_india_finish": badminton_thomas_uber_cup_india_finish,
    "badminton_sudirman_cup_india_finish": badminton_sudirman_cup_india_finish,
    "shooting_issf_world_championships_medals": shooting_issf_world_championships_medals,
    "shooting_issf_world_cup_medals_by_year": shooting_issf_world_cup_medals_by_year,
    "wrestling_uww_senior_world_championships_medals": wrestling_uww_senior_world_championships_medals,
    "athletics_world_championships_medals": athletics_world_championships_medals,
    "athletics_world_u20_championships_medals": athletics_world_u20_championships_medals,
    "boxing_womens_world_championships_medals": boxing_womens_world_championships_medals,
    "boxing_mens_world_championships_medals": boxing_mens_world_championships_medals,
    "weightlifting_world_championships_total_medals": weightlifting_world_championships_total_medals,
    "chess_top10_indian_open_ratings": chess_top10_indian_open_ratings,
    "chess_top10_indian_women_ratings": chess_top10_indian_women_ratings,
    "chess_india_titled_players": chess_india_titled_players,
    "chess_india_federation_rank_top10_average": chess_india_federation_rank_top10_average,
    "chess_olympiad_india_match_record": chess_olympiad_india_match_record,
    "kabaddi_pkl_season12_standings": kabaddi_pkl_season12_standings,
    "tennis_davis_cup_ties_by_decade": tennis_davis_cup_ties_by_decade,
    "tennis_bjk_cup_ties_by_decade": tennis_bjk_cup_ties_by_decade,
    "archery_world_championships_medals": archery_world_championships_medals,
    "archery_world_cup_medals_by_year": archery_world_cup_medals_by_year,
}

NOT_AVAILABLE = [
    {"item": "Wrestling - UWW Senior World Championships before 2025",
     "reason": "UWW's current results platform only exposes 2025-2026 editions; older-edition APIs require authentication."},
    {"item": "Shooting - ISSF medal standings before 2022",
     "reason": "ISSF results site does not publish nation medal standings for earlier competitions."},
    {"item": "Badminton - BWF World Championships before 1989 (e.g. 1983)",
     "reason": "Editions before 1989 are not in the official BWF World Championships results selector."},
    {"item": "Badminton - Thomas/Uber Cup 2008 and 2012, Sudirman Cup 2023 India placings",
     "reason": "Official podium pages list only top teams (India not shown)."},
    {"item": "Chess - Chess Olympiad results before 2022",
     "reason": "Not collected; only 2022 and 2024 crosstables were parsed from chess-results.com."},
    {"item": "Boxing - Women's Worlds 2001-2006, 2010, 2012; Men's Worlds 2009, 2011, 2013 and earlier",
     "reason": "iba.sport event pages for these editions have no medallist/medal-standing reports."},
    {"item": "Boxing - IBA Men's World Championships Dubai 2025",
     "reason": "Not included; only per-weight bracket PDFs are published, and Indian boxers competed under World Boxing (Liverpool 2025)."},
    {"item": "Weightlifting - IWF World Championships before 2011; snatch/clean & jerk small medals",
     "reason": "Earlier editions not located in the IWF results-by-events archive; only Total-ranking medals were counted."},
    {"item": "Weightlifting - 2026 IWF World Championships (Ningbo) final medals",
     "reason": "Event was in progress when fetched (7 categories published, no Indian medal yet)."},
    {"item": "Kabaddi - India's Asian Games and Kabaddi World Cup results (W/L)",
     "reason": "No official IKF/AKFI/OCA results page with match data was found reachable; only PKL standings were collected."},
    {"item": "Tennis - ATP/WTA rankings of top Indians",
     "reason": "Not collected (ATP/WTA sites are not federation/government sources in scope and were not fetched)."},
]


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(PRODUCERS)
    for key in wanted:
        try:
            item = PRODUCERS[key]()
            print(f"ok    {key}: {item['title']}")
            print(f"      labels: {item['labels']}")
            for ds in item["datasets"]:
                print(f"      {ds['label']}: {ds['values']}")
            print(f"      notes: {item['notes'][:400]}")
        except Exception as exc:  # debug runner: report and continue
            print(f"FAIL  {key}: {type(exc).__name__}: {exc}"[:400])

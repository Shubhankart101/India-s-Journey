"""India cricket: ESPNcricinfo Statsguru records and the ICC rankings feed.

Series produced:

* all-time results by format (men and women) and men's results by opposition;
* ICC team rankings (top 10 per format) and India's position in each;
* India's record by edition at the ICC world events;
* leading India run-scorers and wicket-takers per format, each player tagged past or current;
* India's players in the ICC player rankings (batting, bowling, all-rounder).

Run ``python -m scripts.sports_fetch.cricket`` to try every producer without writing anything.
"""
from __future__ import annotations

import re
import time
from urllib.parse import quote

try:
    from .common import fetch_json, fetch_text, html_tables, number, series, today
except ImportError:  # executed as a plain script
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from scripts.sports_fetch.common import fetch_json, fetch_text, html_tables, number, series, today

SNAPSHOT = "cricket.json"
SPORT = "Cricket"

STATSGURU = "https://stats.espncricinfo.com/ci/engine"
TEAM_URL = STATSGURU + "/team/{team}.html?class={cls};template=results;type=team"
PLAYERS_URL = STATSGURU + "/stats/index.html?class={cls};team={team};template=results;type={kind};orderby={order}"
PLAYER_PAGE_URL = STATSGURU + "/player/{pid}.html?class={cls};template=results;type={kind}"
TROPHY_URL = STATSGURU + "/records/team/match_results.html?class={cls};id={tid};type=trophy"

ICC_FEED = "https://assets-icc.sportz.io/cricket/v1/ranking?client_id={cid}&feed_format=json&lang=en&comp_type={comp}&type={kind}"
ICC_PAGE = "https://www.icc-cricket.com/rankings/team-rankings/mens/test"
ICC_CLIENT_ID = "tPZJbRgIub3Vua93/DWtyQ=="  # public widget id embedded in icc-cricket.com pages
ICC_HEADERS = {"Referer": "https://www.icc-cricket.com/", "Origin": "https://www.icc-cricket.com"}

PUB_STATSGURU = "ESPNcricinfo Statsguru"
PUB_STATSGURU_TEAM = "ESPNcricinfo Statsguru (ESPN; cricket record-of-match database)"
PUB_STATSGURU_TROPHY = "ESPNcricinfo Statsguru (match results by tournament)"
PUB_ICC = "ICC (International Cricket Council) rankings feed"

MEN, WOMEN = 6, 1812
WOMEN_PLAYER_TEAM = 1863  # Statsguru's player-records filter knows India Women by this id, not 1812
FORMATS = {MEN: ((1, "Test"), (2, "ODI"), (3, "T20I")), WOMEN: ((8, "Test"), (9, "ODI"), (10, "T20I"))}
TOP_PLAYERS = 12
PLAYER_RANK_CUTOFF = 25

NOT_AVAILABLE = [
    {"item": "ICC women's Test team ranking", "reason": "ICC does not publish a women's Test team ranking (feed not served)."},
    {"item": "World Test Championship finals (India)", "reason": "No official/ESPN WTC result source was fetched in this pass; not filled from memory."},
    {"item": "ICC women's Test player rankings", "reason": "The ICC rankings feed returns 404 for women's Test batting, bowling and all-rounder rankings."},
]

_cache: dict[str, object] = {}


def _get_text(url: str) -> str:
    """Cached, polite Statsguru/ICC page fetch (one request per URL per run)."""
    if url not in _cache:
        time.sleep(0.6)
        _cache[url] = fetch_text(url)
    return _cache[url]  # type: ignore[return-value]


# --------------------------------------------------------------------------- Statsguru team pages

def _team_page(team: int, cls: int) -> tuple[str, list[list[str]], list[list[str]]]:
    """Return (url, header, rows) of the team results page; rows include 'overall' and 'v <team>' rows."""
    url = TEAM_URL.format(team=team, cls=cls)
    rows: list[list[str]] = []
    header: list[str] = []
    for table in html_tables(_get_text(url)):
        if table and len(table[0]) > 6 and table[0][1] == "Span" and table[0][2] == "Mat":
            header = header or table[0]
            rows.extend(r for r in table[1:] if len(r) > 6)
    if not rows:
        raise RuntimeError(f"{url}: Statsguru results table not found")
    return url, header, rows


def _row_counts(row: list[str]) -> dict:
    n = lambda i: number(row[i], 0)  # noqa: E731
    return {"m": n(2), "w": n(3), "l": n(4), "t": n(5), "x": n(6), "span": row[1]}


def _alltime(team: int, who: str, key: str) -> dict:
    data, urls = [], []
    for cls, _fmt in FORMATS[team]:
        url, _header, rows = _team_page(team, cls)
        overall = [r for r in rows if r[0].lower() == "overall"]
        if not overall:
            raise RuntimeError(f"{url}: no overall row")
        data.append(_row_counts(overall[0]))
        urls.append(url)
    fmts = [f for _c, f in FORMATS[team]]
    check = [(a["m"], a["w"] + a["l"] + a["t"] + a["x"]) for a in data]
    extra = "".join(f" Statsguru lists {who} {f} {m} matches but W+L+T+Draw/NR={s} ({m - s} match(es) unaccounted in the source; figures shown as published)."
                    for f, (m, s) in zip(fmts, check) if m != s)
    datasets = [("Matches", [a["m"] for a in data]), ("Won", [a["w"] for a in data]), ("Lost", [a["l"] for a in data]),
                ("Tied", [a["t"] for a in data]), ("Draw", [data[0]["x"], 0, 0]), ("No result", [0, data[1]["x"], data[2]["x"]])]
    return series(key, SPORT, f"{who}: all-time results by format",
                  f"{who} lifetime Test, ODI and T20I match results from the ESPNcricinfo Statsguru record database.",
                  fmts, datasets, source_url=" | ".join(urls), publisher=PUB_STATSGURU_TEAM,
                  notes="Spans: " + ", ".join(f"{f}: {a['span']}" for f, a in zip(fmts, data))
                  + f". Consistency (matches vs W+L+T+Draw/NR): {check}." + extra)


def men_alltime() -> dict:
    return _alltime(MEN, "India men", "cricket_men_alltime_results")


def women_alltime() -> dict:
    return _alltime(WOMEN, "India women", "cricket_women_alltime_results")


def _by_opposition(cls: int, fmt: str) -> dict:
    url, _header, rows = _team_page(MEN, cls)
    opp = {}
    for r in rows:
        if r[0].startswith("v ") and r[0] not in opp:
            opp[r[0]] = r
    top = sorted(opp.values(), key=lambda r: -number(r[2], 0))[:10]
    last = "Draw" if fmt == "Test" else "No result"
    counts = [_row_counts(r) for r in top]
    bad = [(r[0], c["m"]) for r, c in zip(top, counts) if c["m"] != c["w"] + c["l"] + c["t"] + c["x"]]
    datasets = [("Matches", [c["m"] for c in counts]), ("Won", [c["w"] for c in counts]), ("Lost", [c["l"] for c in counts]),
                ("Tied", [c["t"] for c in counts]), (last, [c["x"] for c in counts])]
    return series(f"cricket_men_{fmt.lower()}_by_opposition", SPORT, f"India men {fmt}: results by opposition (top 10 by matches)",
                  f"India men's all-time {fmt} record against their ten most-played opponents.",
                  [r[0][2:] for r in top], datasets, source_url=url, publisher=PUB_STATSGURU,
                  notes="Spans per opponent: " + "; ".join(f"{r[0][2:]} {r[1]}" for r in top)
                  + f". Rows failing played=W+L+T+{last}: {bad or 'none'}.")


def men_test_by_opposition() -> dict:
    return _by_opposition(1, "Test")


def men_odi_by_opposition() -> dict:
    return _by_opposition(2, "ODI")


def men_t20i_by_opposition() -> dict:
    return _by_opposition(3, "T20I")


# --------------------------------------------------------------------------- ICC rankings feed

def _icc_client_id() -> str:
    if "icc_client_id" not in _cache:
        found = None
        try:
            found = re.search(r'clientId\\?":\\?"([^"\\]+)', _get_text(ICC_PAGE))
        except Exception:  # the fallback id below is the one the page has embedded for years
            found = None
        _cache["icc_client_id"] = found.group(1) if found else ICC_CLIENT_ID
    return _cache["icc_client_id"]  # type: ignore[return-value]


def _icc_feed(comp: str, kind: str) -> dict:
    """Return {'rank_date', 'rows': [...]} for one ICC ranking table, with tied ranks ('=') resolved."""
    key = f"icc:{comp}:{kind}"
    if key not in _cache:
        time.sleep(0.5)
        url = ICC_FEED.format(cid=quote(_icc_client_id(), safe=""), comp=comp, kind=kind)
        block = fetch_json(url, headers=ICC_HEADERS)["data"]["bat-rank"]
        rows, previous = [], 0
        for item in block["rank"]:
            rank = number(item.get("no"))
            rank = previous if rank is None else rank
            previous = rank
            rows.append(dict(item, rank=rank))
        if not rows:
            raise RuntimeError(f"ICC feed {comp}/{kind}: empty ranking")
        _cache[key] = {"rank_date": block.get("rank_date") or rows[0].get("rankdate"), "rows": rows}
    return _cache[key]  # type: ignore[return-value]


TEAM_RANKINGS = {  # comp_type -> (series key, display name, page path)
    "test": ("icc_rank_men_test_top10", "Men Test", "mens/test"),
    "odi": ("icc_rank_men_odi_top10", "Men ODI", "mens/odi"),
    "t20": ("icc_rank_men_t20i_top10", "Men T20I", "mens/t20i"),
    "odiw": ("icc_rank_women_odi_top10", "Women ODI", "womens/odi"),
    "t20w": ("icc_rank_women_t20i_top10", "Women T20I", "womens/t20i"),
}


def _team_name(row: dict) -> str:
    return row.get("Country") or row.get("team_name") or ""


def _india_team_row(comp: str) -> dict:
    feed = _icc_feed(comp, "team")
    india = [r for r in feed["rows"] if _team_name(r) == "India"]
    if not india:
        raise RuntimeError(f"India missing from ICC {comp} team ranking")
    return india[0]


def _team_top10(comp: str) -> dict:
    key, name, path = TEAM_RANKINGS[comp]
    feed = _icc_feed(comp, "team")
    top = feed["rows"][:10]
    me = _india_team_row(comp)
    num = lambda r, f: number(r.get(f), 0)  # noqa: E731
    return series(key, SPORT, f"ICC {name} team rankings: top 10 ratings",
                  f"Official ICC {name} team ratings (top 10); India ranked #{me['rank']} with {num(me, 'Rating')} rating points.",
                  [_team_name(r) for r in top],
                  [("Rating", [num(r, "Rating") for r in top]), ("Points", [num(r, "Points") for r in top]),
                   ("Matches", [num(r, "Matches") for r in top])],
                  source_url=f"https://assets-icc.sportz.io/cricket/v1/ranking?comp_type={comp}&type=team (feed behind https://www.icc-cricket.com/rankings/team-rankings/{path})",
                  publisher=PUB_ICC, as_of=feed["rank_date"],
                  notes=f"India: rank {me['rank']}, rating {num(me, 'Rating')}, points {num(me, 'Points')}, matches {num(me, 'Matches')}.")


def icc_rank_men_test() -> dict:
    return _team_top10("test")


def icc_rank_men_odi() -> dict:
    return _team_top10("odi")


def icc_rank_men_t20i() -> dict:
    return _team_top10("t20")


def icc_rank_women_odi() -> dict:
    return _team_top10("odiw")


def icc_rank_women_t20i() -> dict:
    return _team_top10("t20w")


def icc_rank_india_summary() -> dict:
    rows = [(TEAM_RANKINGS[c][1], _india_team_row(c), _icc_feed(c, "team")["rank_date"]) for c in TEAM_RANKINGS]
    num = lambda r, f: number(r.get(f), 0)  # noqa: E731
    return series("icc_rank_india_summary", SPORT, "India's current ICC team rankings (all formats)",
                  "India's rank and rating in each ICC team ranking (no official women's Test ranking exists).",
                  [n for n, _r, _d in rows],
                  [("Rank", [r["rank"] for _n, r, _d in rows]), ("Rating", [num(r, "Rating") for _n, r, _d in rows]),
                   ("Points", [num(r, "Points") for _n, r, _d in rows]), ("Matches", [num(r, "Matches") for _n, r, _d in rows])],
                  source_url="https://www.icc-cricket.com/rankings/team-rankings/{mens|womens}/{test|odi|t20i}", publisher="ICC",
                  as_of="; ".join(f"{n} {d}" for n, _r, d in rows),
                  notes="Data from the ICC rankings widget feed (assets-icc.sportz.io) used by icc-cricket.com.")


PLAYER_RANK_TABLES = {  # gender -> [(comp_type, format label)]
    "men": (("test", "Test"), ("odi", "ODI"), ("t20", "T20I")),
    "women": (("odiw", "ODI"), ("t20w", "T20I")),
}
DISCIPLINES = (("bat", "batting"), ("bowl", "bowling"), ("allrounder", "all-rounder"))


def _player_rankings(gender: str) -> dict:
    entries, dates, total = [], [], 0
    for comp, fmt in PLAYER_RANK_TABLES[gender]:
        for kind, discipline in DISCIPLINES:
            feed = _icc_feed(comp, kind)
            dates.append(f"{fmt} {discipline} {feed['rank_date']}")
            indians = [r for r in feed["rows"] if r.get("Country_name") == "India" or r.get("Country") == "IND"]
            total += len(indians)
            for r in indians:
                if r["rank"] <= PLAYER_RANK_CUTOFF:
                    entries.append((f"{r['Player-name']} ({fmt} {discipline})", number(r.get("Points"), 0), r["rank"]))
    who = "men's" if gender == "men" else "women's"
    return series(f"cricket_icc_player_rankings_india_{gender}", SPORT,
                  f"India's players in the ICC {who} player rankings (world top {PLAYER_RANK_CUTOFF})",
                  f"Indian players currently in the world top {PLAYER_RANK_CUTOFF} of the ICC {who} batting, bowling and all-rounder rankings, with their rating points.",
                  [e[0] for e in entries], [("Rating", [e[1] for e in entries]), ("World rank", [e[2] for e in entries])],
                  source_url=" | ".join(f"https://assets-icc.sportz.io/cricket/v1/ranking?comp_type={c}&type={{bat|bowl|allrounder}}"
                                        for c, _f in PLAYER_RANK_TABLES[gender])
                  + f" (feed behind https://www.icc-cricket.com/rankings/{'mens' if gender == 'men' else 'womens'})",
                  publisher=PUB_ICC, as_of="; ".join(dates),
                  notes=f"Only players ranked {PLAYER_RANK_CUTOFF} or better are shown ({len(entries)} of {total} Indian entries in the published top 100 lists). "
                  "Tied ranks ('=') take the rank of the player above. "
                  + ("The ICC publishes no women's Test player rankings." if gender == "women" else ""))


def icc_player_rankings_men() -> dict:
    return _player_rankings("men")


def icc_player_rankings_women() -> dict:
    return _player_rankings("women")


# --------------------------------------------------------------------------- ICC events by edition

EVENTS = (  # (series key, class, trophy id, title, India's name in the source)
    ("icc_mens_odi_world_cup_india", 2, 12, "Men's ODI World Cup", "India"),
    ("icc_champions_trophy_india", 2, 44, "ICC Champions Trophy (men's ODI)", "India"),
    ("icc_mens_t20_world_cup_india", 3, 89, "Men's T20 World Cup", "India"),
    ("icc_womens_odi_world_cup_india", 9, 68, "Women's ODI World Cup", "India Women"),
    ("icc_womens_t20_world_cup_india", 10, 136, "Women's T20 World Cup", "India Women"),
)


def _event(key: str) -> dict:
    key, cls, tid, title, me = [e for e in EVENTS if e[0] == key][0]
    url = TROPHY_URL.format(cls=cls, tid=tid)
    matches = []
    for table in html_tables(_get_text(url)):
        if table and table[0][:3] == ["Team 1", "Team 2", "Winner"]:
            matches.extend(r for r in table[1:] if len(r) >= 6 and r[0] != "Team 1")
    if not matches:
        raise RuntimeError(f"{url}: match results table not found")
    editions: dict[str, dict] = {}
    for row in matches:
        t1, t2, winner, date = row[0], row[1], row[2], row[-2]
        years = re.findall(r"\b(\d{4})\b", date)
        if not years:
            continue
        year = years[0]
        ed = editions.setdefault(year, {"m": 0, "w": 0, "l": 0, "t": 0, "nr": 0, "india": False})
        ed["last"] = (t1, t2, winner)
        if me not in (t1, t2):
            continue
        ed["india"] = True
        ed["m"] += 1
        result = winner.lower()
        if winner == me:
            ed["w"] += 1
        elif result == "tied":
            ed["t"] += 1
        elif result in ("no result", "abandoned"):
            ed["nr"] += 1
        else:
            ed["l"] += 1
    years = sorted((y for y, e in editions.items() if e["india"]), key=int)
    finish = []
    for y in years:
        t1, t2, winner = editions[y]["last"]
        played = me in (t1, t2)
        finish.append("Champions" if played and winner == me else
                      "Runner-up" if played and winner in (t1, t2) else
                      "Final: no result" if played else "Did not play the final")
    tot = {a: sum(editions[y][a] for y in years) for a in ("m", "w", "l", "t", "nr")}
    titles = [y for y, f in zip(years, finish) if f == "Champions"]
    fields = (("Matches", "m"), ("Won", "w"), ("Lost", "l"), ("Tied", "t"), ("No result", "nr"))
    return series(key, SPORT, f"India at the {title}: record by edition",
                  f"India's results in each {title} edition entered; totals {tot['m']} played, {tot['w']} won, {tot['l']} lost, {tot['t']} tied, {tot['nr']} no result.",
                  years, [(label, [editions[y][f] for y in years]) for label, f in fields],
                  source_url=url, publisher=PUB_STATSGURU_TROPHY,
                  notes=f"Titles (final won): {titles or 'none'} ({len(titles)}). Finish by edition, derived from whether India played/won the last match of the edition in the source: "
                  + "; ".join(f"{y}: {f}" for y, f in zip(years, finish))
                  + f". Exact exit round for non-finalists not read. Totals: {tot}. Editions grouped by calendar year of match date; each edition checked played=W+L+T+NR.")


# --------------------------------------------------------------------------- players: past vs current

def _full_name(pid: str, cls: int, kind: str, fallback: str) -> str:
    """Statsguru tables show scorecard names ('SR Tendulkar'); the player page carries the full name."""
    try:
        page = _get_text(PLAYER_PAGE_URL.format(pid=pid, cls=cls, kind=kind))
    except Exception:
        return fallback
    found = re.search(r'omniPageName\s*=\s*"[^"]*:([^":]+)"', page)
    return found.group(1).strip() if found else fallback


def _clean_name(name: str) -> str:
    return re.sub(r"\s*\((?:INDIA|IND|INDIA WOMEN|INDIA-W)\)\s*$", "", name, flags=re.I).strip()


def _players(team: int, cls: int, fmt: str, kind: str) -> dict:
    gender = "men" if team == MEN else "women"
    batting = kind == "batting"
    order = "runs" if batting else "wickets"
    url = PLAYERS_URL.format(cls=cls, team=MEN if team == MEN else WOMEN_PLAYER_TEAM, kind=kind, order=order)
    html = _get_text(url)
    table = next((t for t in html_tables(html) if t and t[0][:2] == ["Player", "Span"]), None)
    if not table:
        raise RuntimeError(f"{url}: Statsguru player table not found")
    header = table[0]
    col = {name: header.index(name) for name in header if name}
    wanted = (("Runs", "Runs"), ("Average", "Ave"), ("Hundreds", "100")) if batting else \
             (("Wickets", "Wkts"), ("Average", "Ave"), ("Economy", "Econ"))
    for _label, name in wanted:
        if name not in col:
            raise RuntimeError(f"{url}: column {name} missing from {header}")
    ids = dict((name, pid) for pid, name in re.findall(r'href="/ci/content/player/(\d+)\.html"[^>]*>([^<]+)</a>', html))
    rows = [r for r in table[1:] if len(r) >= len(header) - 1 and number(r[col[wanted[0][1]]]) is not None][:TOP_PLAYERS]
    current_from = int(today()[:4]) - 1
    labels, status, spans = [], [], []
    for r in rows:
        name = _clean_name(r[0])
        if name in ids:
            name = _clean_name(_full_name(ids[name], cls, kind, name))
        end = number(r[col["Span"]].split("-")[-1], 0)
        state = "current" if end >= current_from else "past"
        labels.append(f"{name} ({state})")
        status.append(state)
        spans.append(f"{name} {r[col['Span']]}")
    datasets = [(label, [number(r[col[name]], 0) for r in rows]) for label, name in wanted]
    who = f"India {gender}"
    noun = "run-scorers" if batting else "wicket-takers"
    metric = "runs" if batting else "wickets"
    return series(f"cricket_players_{gender}_{fmt.lower()}_{kind}", SPORT,
                  f"{who} {fmt}: leading {noun}, past and current",
                  f"India's leading {gender}'s {fmt} {noun}, with retired players marked past and active players marked current.",
                  labels, datasets, source_url=url, publisher=PUB_STATSGURU,
                  notes=f"Top {len(rows)} India {gender}'s {fmt} players by career {metric} in Statsguru. A player is marked current when their "
                  f"{fmt} career span ends in {current_from} or later, otherwise past (retired or not picked since). "
                  f"Chart the first dataset ({wanted[0][0]}); the others are on different scales. Spans: " + "; ".join(spans) + ".",
                  player_status=status)


PLAYER_SERIES = [(team, cls, fmt, kind) for team in (MEN, WOMEN) for cls, fmt in FORMATS[team] for kind in ("batting", "bowling")]


def _player_producer(team: int, cls: int, fmt: str, kind: str):
    return lambda: _players(team, cls, fmt, kind)


# --------------------------------------------------------------------------- registry

PRODUCERS = {
    "cricket_men_alltime_results": men_alltime,
    "cricket_women_alltime_results": women_alltime,
    "cricket_men_test_by_opposition": men_test_by_opposition,
    "cricket_men_odi_by_opposition": men_odi_by_opposition,
    "cricket_men_t20i_by_opposition": men_t20i_by_opposition,
    "icc_rank_men_test_top10": icc_rank_men_test,
    "icc_rank_men_odi_top10": icc_rank_men_odi,
    "icc_rank_men_t20i_top10": icc_rank_men_t20i,
    "icc_rank_women_odi_top10": icc_rank_women_odi,
    "icc_rank_women_t20i_top10": icc_rank_women_t20i,
    "icc_rank_india_summary": icc_rank_india_summary,
}
PRODUCERS.update({key: (lambda k=key: _event(k)) for key, *_ in EVENTS})
PRODUCERS.update({f"cricket_players_{'men' if t == MEN else 'women'}_{f.lower()}_{k}": _player_producer(t, c, f, k)
                  for t, c, f, k in PLAYER_SERIES})
PRODUCERS["cricket_icc_player_rankings_india_men"] = icc_player_rankings_men
PRODUCERS["cricket_icc_player_rankings_india_women"] = icc_player_rankings_women


if __name__ == "__main__":
    for producer_key, producer in PRODUCERS.items():
        try:
            result = producer()
            for item in result if isinstance(result, list) else [result]:
                print(f"ok    {item['key']}: {len(item['labels'])} labels; datasets {[d['label'] for d in item['datasets']]}")
        except Exception as exc:
            print(f"FAIL  {producer_key}: {type(exc).__name__}: {exc}")

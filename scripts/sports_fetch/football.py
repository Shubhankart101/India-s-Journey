"""India football (soccer) from FIFA's official data: rankings, results and player records.

Sources: inside.fifa.com (ranking pages and ranking-overview JSON) and api.fifa.com v3
(calendar of matches and per-match live/lineup data, the feed behind inside.fifa.com).
Only the standard library is used. Match data is fetched once per run and shared by all producers.
"""
from __future__ import annotations

import json
import re
import time
from collections import Counter, OrderedDict
from datetime import datetime, timedelta, timezone

from .common import fetch_json, fetch_text, series, today

SNAPSHOT = "football.json"

SPORT = "Football"
IND_MEN = "43815"
IND_WOMEN = "1885024"
API = "https://api.fifa.com/api/v3"
PAGE = "https://inside.fifa.com/fifa-rankings/world-ranking/IND?gender={gender}"
RANKING_API = "https://inside.fifa.com/api/ranking-overview?locale=en&dateId={date_id}"
CALENDAR = API + "/calendar/matches?idTeam={team}&count=500&language=en&from=1990-01-01T00:00:00Z&to=2026-12-31T23:59:59Z"
LIVE = API + "/live/football/{comp}/{season}/{stage}/{match}?language=en"
PUBLISHER = "FIFA (api.fifa.com v3 calendar and match data; data source of inside.fifa.com)"
PLAYER_NOTE_WINDOW_YEARS = 2
PAUSE = 0.15

NOT_AVAILABLE = [
    {"item": "AIFF (the-aiff.com) / AFC match records", "reason": "No structured results API located; FIFA API used instead."},
    {"item": "Official all-time international caps and goals for India players (AIFF / FIFA)",
     "reason": "Neither AIFF nor FIFA publishes a career caps-and-goals table. Player series are totals counted from FIFA's "
              "per-match line-ups and goal events, which only cover the matches FIFA lists, so they are lower than "
              "career records for players who also played before that coverage began."},
    {"item": "India women's player goals and appearances (past vs current)",
     "reason": "FIFA publishes line-ups for only a handful of India women's matches (9 of 71 listed), so any player ranking "
               "would misrepresent careers; it is not charted."},
    {"item": "Current FIFA ranking table (latest update)",
     "reason": "The ranking-overview endpoint returns an empty table for the newest update ids, so the Asia comparison "
              "uses the latest update FIFA still serves in full."},
]

_cache: dict = {}


def _desc(items) -> str:
    return (items[0].get("Description") if items else "") or ""


def _clean(text: str) -> str:
    return " ".join(text.replace("\u00a0", " ").replace("\ufffd", "").replace("\u2122", "").split())


def _calendar(team: str) -> list[dict]:
    """Completed India matches (oldest first) as dicts, from FIFA's calendar feed."""
    key = ("calendar", team)
    if key not in _cache:
        time.sleep(PAUSE)
        results = fetch_json(CALENDAR.format(team=team))["Results"]
        rows = []
        for m in results:
            home, away = m.get("Home") or {}, m.get("Away") or {}
            if m.get("HomeTeamScore") is None or m.get("AwayTeamScore") is None or not home or not away:
                continue
            india_home = home.get("IdTeam") == team
            if not india_home and away.get("IdTeam") != team:
                continue
            gf, ga = (m["HomeTeamScore"], m["AwayTeamScore"]) if india_home else (m["AwayTeamScore"], m["HomeTeamScore"])
            competition = _clean(_desc(m.get("CompetitionName")))
            season = _clean(_desc(m.get("SeasonName"))) or competition
            rows.append({
                "date": m["Date"], "year": int(m["Date"][:4]), "gf": gf, "ga": ga,
                "group": "Friendlies" if competition == "Friendlies" else season,
                "ids": (m["IdCompetition"], m["IdSeason"], m["IdStage"], m["IdMatch"]),
            })
        rows.sort(key=lambda r: r["date"])
        _cache[key] = rows
    return _cache[key]


def _record(rows: list[dict]) -> dict:
    return {
        "Played": len(rows),
        "Won": sum(r["gf"] > r["ga"] for r in rows),
        "Drawn": sum(r["gf"] == r["ga"] for r in rows),
        "Lost": sum(r["gf"] < r["ga"] for r in rows),
        "Goals for": sum(r["gf"] for r in rows),
        "Goals against": sum(r["ga"] for r in rows),
    }


RECORD_LABELS = ["Played", "Won", "Drawn", "Lost", "Goals for", "Goals against"]


def _record_series(key, title, description, groups: "OrderedDict[str, list]", source_url, notes):
    records = {name: _record(rows) for name, rows in groups.items()}
    return series(key, SPORT, title, description, list(records),
                  [(label, [records[name][label] for name in records]) for label in RECORD_LABELS],
                  chart="bar", source_url=source_url, publisher=PUBLISHER, as_of=f"fetched {today()}", notes=notes)


def _rank_page(gender: str) -> dict:
    key = ("page", gender)
    if key not in _cache:
        time.sleep(PAUSE)
        html = fetch_text(PAGE.format(gender=gender))
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
        if not match:
            raise RuntimeError("FIFA ranking page has no __NEXT_DATA__ block")
        _cache[key] = json.loads(match.group(1))["props"]["pageProps"]["pageData"]
    return _cache[key]


def _rank_history(gender: str, group: str, label: str) -> dict:
    page = _rank_page(gender)
    rows = page["historyRanking"][group]["historyTable"]["rows"][::-1]
    current = next(x for x in page["ranking"]["rankings"][gender + "Ranking"]["rows"] if x["countryCode"] == "IND")
    highlights = "; ".join(f"{x['label']} {x['value']}" for x in page["historyRanking"][group]["statistic"]["highlightsItems"][:4])
    return series(
        f"fifa_rank_history_india_{gender}", SPORT, f"India {label} FIFA ranking: year-end, best and worst rank",
        f"India {label} FIFA World Ranking by year (final, best and worst rank during the year).",
        [r["year"] for r in rows],
        [("Final rank", [r["finalRank"] for r in rows]), ("Best rank", [r["bestRank"] for r in rows]),
         ("Worst rank", [r["worstRank"] for r in rows])],
        chart="line", source_url=PAGE.format(gender=gender), publisher="FIFA (inside.fifa.com)",
        as_of=f"ranking updated {current['lastUpdateDate'][:10]}; fetched {today()}",
        notes=f"Current rank {current['rank']} with {current['totalPoints']} points (previous rank {current['previousRank']}). "
              f"Lower number is better. {rows[-1]['year']} row is year-to-date. Page highlights: {highlights}")


def rank_history_men():
    return _rank_history("men", "1", "men's")


def rank_history_women():
    return _rank_history("women", "2", "women's")


def results_by_competition(team: str, gender: str, since: int | None = None):
    rows = [r for r in _calendar(team) if since is None or r["year"] >= since]
    groups: OrderedDict[str, list] = OrderedDict()
    for r in rows:
        groups.setdefault(r["group"], []).append(r)
    first, last = rows[0]["year"], rows[-1]["year"]
    word = "men" if gender == "men" else "women"
    return _record_series(
        f"fifa_india_{word}_results_by_competition",
        f"India {word}: results by competition, {first}-{last} (FIFA-listed matches)",
        f"W/D/L and goals for India {word} in FIFA-listed matches from {first} to {last}, grouped by competition/season.",
        groups, CALENDAR.format(team=team),
        f"{len(rows)} completed matches returned by the FIFA calendar; regular-time scores. The feed does not list every match "
        f"India {word} played, so treat as FIFA-listed matches only."
        + (" 'Asian Nations Cup 2027 Prel. Comp.' is FIFA's label for the AFC Asian Cup 2027 qualifiers." if gender == "men" else ""))


def results_by_year(team: str, gender: str):
    rows = _calendar(team)
    groups: OrderedDict[str, list] = OrderedDict()
    for r in rows:
        groups.setdefault(str(r["year"]), []).append(r)
    word = "men" if gender == "men" else "women"
    return _record_series(
        f"fifa_india_{word}_results_by_year",
        f"India {word}: results by year, {rows[0]['year']}-{rows[-1]['year']} (FIFA-listed matches)",
        f"Matches played, won, drawn and lost, with goals for and against, for India {word} in each calendar year FIFA lists matches.",
        groups, CALENDAR.format(team=team),
        f"{len(rows)} completed matches in {len(groups)} calendar years; years with no FIFA-listed match are omitted. "
        "Regular-time scores. FIFA's feed does not list every match, so early years are incomplete.")


def asia_top10(gender: str):
    page = _rank_page(gender)
    dates = [d for block in page["ranking"]["rankings"][gender + "Ranking"]["dates"] for d in block["dates"]]
    table = update = None
    for d in dates[:14]:
        time.sleep(PAUSE)
        data = fetch_json(RANKING_API.format(date_id=d["id"])).get("rankings") or []
        if data:
            table, update = data, d
            break
    if not table:
        raise RuntimeError("no FIFA ranking table returned for any recent update")
    asia = [x for x in table if (x.get("tag") or {}).get("id") == "AFC" and x["rankingItem"].get("rank") is not None]
    asia.sort(key=lambda x: x["rankingItem"]["rank"])
    chosen = asia[:10]
    india = next((x for x in asia if x["rankingItem"]["countryCode"] == "IND"), None)
    if india and india not in chosen:
        chosen.append(india)
    word = "men's" if gender == "men" else "women's"
    stamp = update["iso"][:10]
    update_date = table[0]["lastUpdateDate"][:10]
    return series(
        f"fifa_current_rank_asia_top10_{gender}", SPORT,
        f"FIFA {word} ranking: top 10 Asian teams and India ({update_date} update)",
        f"Ranking points of the ten highest-ranked AFC {word} teams and India in the FIFA World Ranking, with each team's world rank.",
        [x["rankingItem"]["name"] for x in chosen],
        [("Ranking points", [x["rankingItem"]["totalPoints"] for x in chosen]),
         ("World rank", [x["rankingItem"]["rank"] for x in chosen])],
        chart="bar", source_url=PAGE.format(gender=gender), publisher="FIFA (inside.fifa.com ranking-overview)",
        as_of=f"ranking update of {update_date}; fetched {today()}",
        notes=f"AFC members only, ordered by FIFA rank; India is {india['rankingItem']['rank'] if india else 'n/a'} in the world and "
              f"{asia.index(india) + 1 if india else 'n/a'} of {len(asia)} ranked AFC teams. This is the latest full table FIFA's "
              f"ranking-overview feed serves (id {update['id']}, listed {stamp}); newer updates return an empty table.")


# ---- player statistics from per-match line-ups and goal events ----

def _normal_name(raw: str) -> str:
    words = _clean(raw).split()
    return " ".join(w.capitalize() if w.isupper() and len(w) > 1 else w for w in words)


def _players(team: str) -> dict:
    key = ("players", team)
    if key in _cache:
        return _cache[key]
    players: dict[str, dict] = {}
    covered = goals_ok = 0
    first_year = None
    matches = _calendar(team)
    for m in matches:
        time.sleep(PAUSE)
        try:
            live = fetch_json(LIVE.format(comp=m["ids"][0], season=m["ids"][1], stage=m["ids"][2], match=m["ids"][3]))
        except RuntimeError:
            continue
        if not isinstance(live, dict):
            continue
        side = next((live.get(k) for k in ("HomeTeam", "AwayTeam") if (live.get(k) or {}).get("IdTeam") == team), None)
        if not side or not side.get("Players"):
            continue
        covered += 1
        first_year = first_year or m["year"]
        names = {p["IdPlayer"]: _normal_name(_desc(p.get("PlayerName"))) for p in side["Players"]}
        appeared = {p["IdPlayer"] for p in side["Players"] if p.get("Status") == 1}
        appeared |= {s["IdPlayerOn"] for s in side.get("Substitutions") or [] if s.get("IdPlayerOn")}
        scored = Counter(g["IdPlayer"] for g in side.get("Goals") or []
                         if g.get("IdPlayer") and g.get("Type") in (1, 2) and g.get("IdTeam") == team)
        goals_ok += sum(scored.values()) == m["gf"]
        for pid in appeared | set(scored):
            entry = players.setdefault(pid, {"names": Counter(), "apps": 0, "goals": 0, "last": ""})
            entry["names"][names.get(pid) or pid] += 1
            entry["apps"] += pid in appeared
            entry["goals"] += scored.get(pid, 0)
            entry["last"] = max(entry["last"], m["date"])
    # the same person can carry two FIFA ids; merge identical normalised names
    merged: dict[str, dict] = {}
    for entry in players.values():
        name = entry["names"].most_common(1)[0][0]
        slot = merged.setdefault(name.casefold(), {"name": name, "apps": 0, "goals": 0, "last": ""})
        slot["apps"] += entry["apps"]
        slot["goals"] += entry["goals"]
        slot["last"] = max(slot["last"], entry["last"])
    _cache[key] = {"players": list(merged.values()), "matches": len(matches), "covered": covered,
                   "goals_ok": goals_ok, "first_year": first_year}
    return _cache[key]


def _player_series(team: str, gender: str, metric: str):
    data = _players(team)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=365 * PLAYER_NOTE_WINDOW_YEARS)).strftime("%Y-%m-%d")
    primary, other = ("goals", "apps") if metric == "scorers" else ("apps", "goals")
    ranked = sorted(data["players"], key=lambda p: (-p[primary], -p[other], p["name"]))
    ranked = [p for p in ranked if p[primary] > 0][:10]
    if not ranked:
        raise RuntimeError("no player records")
    labels = [f"{p['name']} ({'current' if p['last'][:10] >= cutoff else 'past'})" for p in ranked]
    goals = ("Goals", [p["goals"] for p in ranked])
    apps = ("Appearances", [p["apps"] for p in ranked])
    word = "men" if gender == "men" else "women"
    kind = "top scorers" if metric == "scorers" else "most appearances"
    since = data["first_year"]
    return series(
        f"football_players_{word}_{'top_scorers' if metric == 'scorers' else 'most_appearances'}",
        SPORT, f"India {word}: {kind}, past and current players (FIFA match records since {since})",
        f"The ten India {word} players with the most {'goals' if metric == 'scorers' else 'appearances'} in international "
        f"matches FIFA has line-up records for since {since}, marked as past or current players.",
        labels, [goals, apps] if metric == "scorers" else [apps, goals],
        chart="bar", source_url=CALENDAR.format(team=team) + " + " + LIVE.format(comp="{idCompetition}", season="{idSeason}", stage="{idStage}", match="{idMatch}"),
        publisher=PUBLISHER, as_of=f"fetched {today()}",
        notes=f"Counted from the line-ups and goal events of {data['covered']} of the {data['matches']} completed India {word} "
              f"matches in FIFA's feed ({since} onwards); a player counts as an appearance if he or she started or came on as a "
              f"substitute. Own goals and shoot-out penalties are excluded. 'Current' means the player featured in a FIFA-listed "
              f"match in the last {PLAYER_NOTE_WINDOW_YEARS} years (since {cutoff}); everyone else is 'past'. Goal events matched the final "
              f"score in {data['goals_ok']} of those matches. These are totals within FIFA's coverage, not official career "
              f"caps, so players who also played earlier or in unlisted matches have higher career figures.")


def _make(fn, *args):
    return lambda: fn(*args)


PRODUCERS = {
    "fifa_rank_history_india_men": rank_history_men,
    "fifa_rank_history_india_women": rank_history_women,
    "fifa_india_men_results_by_competition": _make(results_by_competition, IND_MEN, "men", 2018),
    "fifa_india_women_results_by_competition": _make(results_by_competition, IND_WOMEN, "women"),
    "fifa_india_men_results_by_year": _make(results_by_year, IND_MEN, "men"),
    "fifa_india_women_results_by_year": _make(results_by_year, IND_WOMEN, "women"),
    "fifa_current_rank_asia_top10_men": _make(asia_top10, "men"),
    "fifa_current_rank_asia_top10_women": _make(asia_top10, "women"),
    "football_players_men_top_scorers": _make(_player_series, IND_MEN, "men", "scorers"),
    "football_players_men_most_appearances": _make(_player_series, IND_MEN, "men", "apps"),
}


if __name__ == "__main__":
    for name, producer in PRODUCERS.items():
        try:
            result = producer()
            for item in result if isinstance(result, list) else [result]:
                print(item["key"], "|", item["title"], "|", len(item["labels"]), [d["label"] for d in item["datasets"]])
                print("   ", item["labels"][:12])
                print("   ", item["datasets"][0]["values"][:12])
        except Exception as exc:
            print("FAILED", name, type(exc).__name__, exc)

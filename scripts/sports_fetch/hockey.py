"""India field hockey fetcher: official FIH (fih.hockey) data feeds and ranking pages.

Everything is read live from the public FIH data feeds that power fih.hockey:
``8_/6_/30_series_listing.json`` (World Cup / Olympics / Pro League editions),
``standings/{series_id}_standings.json``, ``squads/{series_id}_{team_id}_squad.json``,
``players/{player_id}_player.json``, ``stats/{series_id}_allstats.json`` and the
``window.outdoorRanking`` object embedded in the FIH outdoor-ranking pages.
"""
from __future__ import annotations

import json
import re
import time
from collections import defaultdict
from datetime import date

from .common import fetch_json, fetch_text, series, today

SNAPSHOT = "hockey.json"

FEEDS = "https://www.fih.hockey/datafeeds/static/json/en/"
RANK_PAGE = "https://www.fih.hockey/outdoor-rankings/india-{g}-hockey-rankings-35"
PUBLISHER_FEED = "FIH (official data feeds on fih.hockey)"
PAUSE = 0.05

PRO_LEAGUE, OLYMPICS, WORLD_CUP = 30, 6, 8

# Competitions outside the three parent series that FIH records player stats for.
EXTRA_PLAYER_SERIES = {"M": [1942, 6486], "F": [1851]}
# Squad feeds before this year rarely carry player stats, so older editions are not crawled.
FIRST_SQUAD_YEAR = 1998
CURRENT_WINDOW_MONTHS = 24

_cache: dict[str, object] = {}


def _pause():
    time.sleep(PAUSE)


def _json(path: str):
    if path not in _cache:
        _pause()
        _cache[path] = fetch_json(FEEDS + path)
    return _cache[path]


def _rank_data(g: str) -> dict:
    key = f"rank_{g}"
    if key not in _cache:
        _pause()
        html = fetch_text(RANK_PAGE.format(g=g), timeout=90)
        marker = "window.outdoorRanking = "
        pos = html.find(marker)
        if pos < 0:
            raise RuntimeError(f"{RANK_PAGE.format(g=g)}: window.outdoorRanking not found")
        _cache[key], _ = json.JSONDecoder().raw_decode(html[pos + len(marker):])
        _cache[key] = _cache[key]["outdoorRanking"]
    return _cache[key]


def _listing(parent_id: int) -> list[dict]:
    return _json(f"{parent_id}_series_listing.json")["series"]


def _india_editions(parent_id: int, gender: str) -> list[dict]:
    rows = [s for s in _listing(parent_id)
            if s.get("gender") == gender and any(p.get("team_name") == "India" for p in s.get("participants") or [])]
    return sorted(rows, key=lambda s: (s["startdt"], s["series_id"]))


def _standings(series_id: int) -> dict | None:
    try:
        return _json(f"standings/{series_id}_standings.json")["standings"]
    except RuntimeError:
        return None


def _india_group_row(st: dict) -> dict | None:
    for group in st.get("groups") or []:
        for team in (group.get("teams") or {}).get("team") or []:
            if team.get("team_short_name") == "IND":
                return team
    return None


def _ranking_matches(g: str, competition_id: int) -> list[dict]:
    out = []
    for block in _rank_data(g)["selectedTeam"]["vs"]:
        out += [m for m in block["vs_teams"] if m["competition_id"] == competition_id]
    return out


def _wdl(matches: list[dict]) -> tuple[int, int, int, int]:
    won = sum(m["home_team_score"] > m["away_team_score"] for m in matches)
    drawn = sum(m["home_team_score"] == m["away_team_score"] for m in matches)
    lost = sum(m["home_team_score"] < m["away_team_score"] for m in matches)
    return len(matches), won, drawn, lost


# ---------------------------------------------------------------- rankings

def _ranking_top10(g: str, label: str):
    def produce():
        data = _rank_data(g)
        ranks = data["ranks"]
        top = ranks[:10]
        india = next(r for r in ranks if r["team_short_code"] == "IND")
        return series(
            f"fih_rank_{g}_top10", "Hockey", f"FIH Outdoor World Ranking - {label} top 10",
            f"FIH outdoor world ranking points for the top 10 {label} teams; India is {india['rank']}th with {round(india['points'], 2)} points.",
            [r["team"].title() for r in top], [("Ranking points", [round(r["points"], 2) for r in top])],
            source_url=RANK_PAGE.format(g=g), publisher="FIH (International Hockey Federation)", as_of=data["last_updated"],
            notes=f"India: rank {india['rank']}, {round(india['points'], 2)} points (last match {india['last_match_played_on']}). "
                  "Data embedded in the official page as window.outdoorRanking.")
    return produce


# ------------------------------------------------- World Cup / Olympic positions

def _positions(parent_id: int, g_code: str, g: str, name: str, key: str, title: str):
    def produce():
        rows, missing, bad = [], [], []
        for ed in _india_editions(parent_id, g_code):
            st = _standings(ed["series_id"])
            final = next((x for x in (st or {}).get("final_standings") or [] if x.get("team_short_name") == "IND"), None)
            if not final:
                if st is not None and _india_group_row(st):
                    final = {"position": None, "GP": None, "win": None, "draw": None, "loss": None}
                else:
                    missing.append(f"{ed['year']} ({ed['series_name']})")
                    continue
            rows.append((ed, dict(final)))
        extra = ""
        for ed, row in rows:
            matches = _ranking_matches(g, ed["series_id"])
            if row["position"] is None:
                if parent_id == OLYMPICS and ed["year"] == "2024" and g == "men":
                    row["position"] = 3
                    extra += (" 2024 Olympic men: the FIH final_standings feed is empty; position 3 (bronze) is inferred from the FIH match "
                              "results (India won the bronze-medal match against Spain 2-1), and played/won/drawn/lost are counted from "
                              "FIH match records (shootouts count as draws).")
                else:
                    continue
            if matches and (not row["GP"]):
                row["GP"], row["win"], row["draw"], row["loss"] = _wdl(matches)
                if not extra.count("counted from"):
                    extra += (f" {ed['year']} {g}: final_standings has no played/won/drawn/lost, so they are counted from FIH match records "
                              "(shootouts count as draws).")
        rows = [(ed, row) for ed, row in rows if row["position"] is not None]
        bad = [(ed["year"], row["GP"], row["win"] + row["draw"] + row["loss"]) for ed, row in rows
               if row["GP"] is not None and row["GP"] != row["win"] + row["draw"] + row["loss"]]
        if not rows:
            raise RuntimeError(f"{key}: FIH feeds returned no standings for India {g}")
        labels = [ed["year"] for ed, _ in rows]
        cols = [("Final position", "position"), ("Played", "GP"), ("Won", "win"), ("Drawn", "draw"), ("Lost", "loss")]
        notes = ("Lower position is better. W/D/L as in final_standings. Series ids: "
                 + ", ".join(f"{ed['year']}={ed['series_id']}" for ed, _ in rows)
                 + f". Rows failing GP=W+D+L: {bad or 'none'}." + extra)
        if missing:
            notes += f" Editions with India in the listing but no standings data from the feed: {missing}."
        return series(
            key, "Hockey", title,
            f"India {g}'s final tournament position (1 = champions) at each {name} edition in the FIH feed, with played/won/drawn/lost.",
            labels, [(lab, [row[k] for _, row in rows]) for lab, k in cols], chart="line",
            source_url=f"{FEEDS}standings/{{series_id}}_standings.json (final_standings); ids from {FEEDS}{parent_id}_series_listing.json",
            publisher=PUBLISHER_FEED, notes=notes)
    return produce


# ----------------------------------------------------------------- Pro League

def _pro_league_standings(g_code: str, g: str):
    def produce():
        rows = []
        for ed in _india_editions(PRO_LEAGUE, g_code):
            st = _standings(ed["series_id"])
            row = _india_group_row(st) if st else None
            if row and int(row.get("played") or 0) > 0:
                m = re.search(r"20\d\d-\d\d", ed["series_name"])
                rows.append((m.group(0) if m else ed["year"], ed["series_id"], st["last_updated"], row))
        if not rows:
            raise RuntimeError(f"FIH Pro League feeds returned no standings for India {g}")
        cols = [("Position", "position"), ("Played", "played"), ("Won", "wins"), ("Drawn (as listed)", "draws"), ("Lost", "lost"),
                ("Shootout wins", "so_win"), ("Shootout losses", "so_loss"), ("Points", "points")]
        return series(
            f"fih_pro_league_india_{g}_standings", "Hockey", f"FIH Pro League - India {g}: league standing by season",
            f"India {g}'s FIH Pro League position, record and points per season in the FIH feed.",
            [r[0] for r in rows], [(lab, [int(r[3][k] or 0) for r in rows]) for lab, k in cols],
            source_url=f"{FEEDS}standings/{{series_id}}_standings.json; series " + ", ".join(f"{r[0]}={r[1]}" for r in rows),
            publisher="FIH (official Pro League standings feed)", as_of="; ".join(f"{r[0]}: feed updated {r[2]}" for r in rows),
            notes="Lower position is better (9 teams, 16 matches each in a full season). Pro League points: 3 regulation win, 2 shootout win, "
                  "1 shootout loss. The feed's Won/Drawn/Lost and shootout columns are not consistent across seasons (e.g. men 2025-26: "
                  "4W+5D+7L=16 with 2 shootout wins and 19 pts; men 2023-24: 5W+0D+5L plus 3 SO wins and 3 SO losses), so "
                  "Position/Played/Points are authoritative. 2020-21 men played only 8 matches (COVID-affected). Seasons in which "
                  "India is absent from the FIH feed are skipped.")
    return produce


# ---------------------------------------------------------------- head-to-head

def fih_india_men_head_to_head_2020_2026():
    data = _rank_data("men")
    table: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    first_year = last_year = None
    for block in data["selectedTeam"]["vs"]:
        first_year = min(first_year or block["year"], block["year"])
        last_year = max(last_year or block["year"], block["year"])
        for m in block["vs_teams"]:
            gf, ga = m["home_team_score"], m["away_team_score"]
            row = table[m["vs_team_name"]]
            row[0] += 1
            row[1 if gf > ga else 2 if gf == ga else 3] += 1
            row[4] += gf
            row[5] += ga
    top = sorted(table.items(), key=lambda kv: -kv[1][0])[:10]
    names = ["Played", "Won", "Drawn", "Lost", "Goals for", "Goals against"]
    return series(
        "fih_india_men_head_to_head_2020_2026", "Hockey", "India men vs major opponents: head-to-head (FIH match records, 2020-2026)",
        f"India men's W/D/L and goals against the ten most-played opponents in FIH's ranking match history ({first_year} - {data['last_updated'].split()[0]}).",
        [k for k, _ in top], [(n, [v[i] for _, v in top]) for i, n in enumerate(names)],
        source_url=RANK_PAGE.format(g="men"), publisher="FIH (match history embedded in official ranking page)", as_of=data["last_updated"],
        notes="Not an all-time table: aggregated from the match history FIH lists for India's ranking window (2020 to the latest match; "
              "Pro League, Olympics, World Cups, Asian events, Test series). Drawn includes matches decided by shootout (regulation score level).")


# -------------------------------------------------------------------- players

COMMON_SURNAMES = {"singh", "kaur", "kumar", "kumari", "devi", "sharma", "lakra", "tirkey", "yadav", "rani", "minz", "toppo"}


def _person_name(raw: str) -> str:
    """'SINGH Harmanpreet' / 'Singh Harmanpreet' -> 'Harmanpreet Singh'; given-name-first names are kept."""
    parts = raw.split()
    if len(parts) < 2:
        return raw.title() if raw.isupper() else raw
    n = 0
    while n < len(parts) - 1 and parts[n].isupper():
        n += 1
    if n == 0 and parts[0].lower() in COMMON_SURNAMES and parts[-1].lower() not in COMMON_SURNAMES:
        n = 1
    parts = parts[n:] + parts[:n]
    return " ".join(p.title() if p.isupper() else p for p in parts)


def _india_squad_players(series_ids: list[int], g_code: str) -> dict[int, tuple[str, int]]:
    """person id -> (squad name, highest caps listed in any squad) for India players in the given competitions."""
    found: dict[int, tuple[str, int]] = {}
    for sid in series_ids:
        st = _standings(sid)
        row = _india_group_row(st) if st else None
        if not row:
            continue
        try:
            squad = _json(f"squads/{sid}_{row['team_id']}_squad.json")["squads"]["players"]
        except RuntimeError:
            continue
        for p in squad:
            pid = p.get("person_id") or p.get("id")
            if p.get("gender") != g_code or not pid or p.get("nationality") not in ("India", ""):
                continue
            caps = int(p.get("caps") or 0)
            found[int(pid)] = (p["name"], max(caps, found.get(int(pid), ("", 0))[1]))
    return found


def _player_records(g_code: str) -> list[dict]:
    key = f"players_{g_code}"
    if key in _cache:
        return _cache[key]
    ids = [e["series_id"] for parent in (PRO_LEAGUE, OLYMPICS, WORLD_CUP) for e in _india_editions(parent, g_code)
           if int(e["year"]) >= FIRST_SQUAD_YEAR]
    ids += EXTRA_PLAYER_SERIES[g_code]
    candidates = _india_squad_players(sorted(set(ids)), g_code)
    cutoff = _current_cutoff()
    records = []
    for pid, (squad_name, squad_caps) in candidates.items():
        try:
            p = _json(f"players/{pid}_player.json")
        except RuntimeError:
            continue
        bio = p.get("bio") or {}
        if bio.get("nationality_country_code") not in ("IND", None, ""):
            continue
        stats = p.get("stats") or {}
        overall = next((o for o in stats.get("over_all_stats") or [] if o.get("display_name") == "all"), {})
        caps_info = p.get("caps") or {}
        senior = sum(b["caps"] or 0 for b in caps_info.get("breakdown") or [] if b.get("ageGroup") == "SENIOR")
        india_dates = []
        for s in stats.get("series_stats") or []:
            if s.get("team_short_name") == "IND" and s.get("series_enddate"):
                m, d, y = s["series_enddate"].split()[0].split("/")
                india_dates.append(date(int(y), int(m), int(d)))
        records.append({
            "id": pid, "name": _person_name(bio.get("player_name") or squad_name),
            "goals": int(overall.get("goals") or 0), "caps": senior or int(caps_info.get("total") or 0) or squad_caps,
            "current": bool(india_dates) and max(india_dates) >= cutoff,
        })
    _cache[key] = records
    return records


def _player_series(g_code: str, g: str, label: str, key: str, metric: str, other: str, per_group: int = 6):
    metric_name = {"goals": "Goals", "caps": "Caps"}
    def produce():
        records = _player_records(g_code)
        if not records:
            raise RuntimeError(f"FIH feeds returned no India {g} squad players")
        picked = []
        for current in (True, False):
            group = [r for r in records if r["current"] == current and r[metric] > 0]
            picked += sorted(group, key=lambda r: (-r[metric], -r[other], r["name"]))[:per_group]
        picked.sort(key=lambda r: (-r[metric], r["name"]))
        labels = [f"{r['name']} ({'current' if r['current'] else 'past'})" for r in picked]
        what = "goals" if metric == "goals" else "international caps"
        title = (f"India {g} hockey: top scorers, current vs past players (goals in FIH-recorded matches)" if metric == "goals"
                 else f"India {g} hockey: most-capped players, current vs past (FIH-listed caps)")
        desc = (f"The {per_group} highest goal-scorers among India {g} players still in the national squad and the {per_group} among those who "
                "have moved on, using career totals on their FIH player profiles."
                if metric == "goals" else
                f"The {per_group} most-capped India {g} players still in the national squad and the {per_group} among those who have "
                "moved on, using senior caps on their FIH player profiles.")
        return series(
            key, "Hockey", title, desc, labels,
            [(metric_name[metric], [r[metric] for r in picked]), (metric_name[other], [r[other] for r in picked])],
            source_url=f"{FEEDS}players/{{player_id}}_player.json; players from {FEEDS}squads/{{series_id}}_{{team_id}}_squad.json",
            publisher="International Hockey Federation (FIH)",
            notes=("Current = the player has India appearances recorded in an FIH competition that ended in the last 24 months "
                   f"(since {today_d_minus()}); past = anyone else who was in an India squad for a Pro League, World Cup, Olympic Games or "
                   "2026 Asian/qualifier event listed in the FIH feeds. Goals are the career total on the FIH player profile "
                   "(competitions FIH has recorded, mainly since the 2010s) so they understate the full careers of older players. "
                   "Caps are senior caps from the same profile. Only players who appeared in squads of those FIH events are considered, "
                   "so players who retired before the FIH squad feeds start are not covered. "
                   f"Ranked by {what}; the second dataset is shown for context."),
            chart="bar")
    return produce


def _current_cutoff() -> date:
    d = date.fromisoformat(today())
    return date(d.year - CURRENT_WINDOW_MONTHS // 12, d.month, min(d.day, 28))


def today_d_minus() -> str:
    return _current_cutoff().isoformat()


def _pro_league_top_scorers(g_code: str, g: str):
    def produce():
        rows = []
        for ed in _india_editions(PRO_LEAGUE, g_code):
            try:
                stats = _json(f"stats/{ed['series_id']}_allstats.json")["all_stats"]
            except RuntimeError:
                continue
            block = next((b for b in stats if b.get("stat") == "Players Goals"), None)
            ours = [d for d in (block or {}).get("data") or [] if d.get("team_short") == "IND" or d.get("team_name") == "India"]
            if not ours:
                continue
            best = max(ours, key=lambda d: d["value"])
            m = re.search(r"20\d\d-\d\d", ed["series_name"])
            rows.append((m.group(0) if m else ed["year"], _person_name(best["player_name"]), best["value"], ed["series_id"]))
        if not rows:
            raise RuntimeError(f"FIH Pro League stats feeds returned no India {g} scorers")
        return series(
            f"hockey_pro_league_india_{g}_top_scorers_by_season", "Hockey", f"FIH Pro League: India {g}'s top scorer each season",
            f"Goals by India {g}'s leading scorer in each FIH Pro League season, with the player's name.",
            [f"{r[0]}: {r[1]}" for r in rows], [("Goals", [r[2] for r in rows])],
            source_url=f"{FEEDS}stats/{{series_id}}_allstats.json (Players Goals); series " + ", ".join(f"{r[0]}={r[3]}" for r in rows),
            publisher="International Hockey Federation (FIH)",
            notes="Goals by the highest-scoring India player in the FIH Pro League player-goals leaderboard of each season in the FIH feed. "
                  "Seasons where India is absent from the feed, or where FIH published no player leaderboard (e.g. men 2024-25), are skipped.")
    return produce


PRODUCERS = {
    "fih_rank_men_top10": _ranking_top10("men", "men's"),
    "fih_rank_women_top10": _ranking_top10("women", "women's"),
    "fih_world_cup_india_men_positions": _positions(
        WORLD_CUP, "M", "men", "World Cup", "fih_world_cup_india_men_positions",
        "India men at the FIH Hockey World Cup: final position by edition"),
    "fih_world_cup_india_women_positions": _positions(
        WORLD_CUP, "F", "women", "World Cup", "fih_world_cup_india_women_positions",
        "India women at the FIH Hockey World Cup: final position by edition"),
    "fih_olympics_india_men_positions": _positions(
        OLYMPICS, "M", "men", "Olympic Games", "fih_olympics_india_men_positions",
        "India men at the Olympic Games: final position by edition"),
    "fih_olympics_india_women_positions": _positions(
        OLYMPICS, "F", "women", "Olympic Games", "fih_olympics_india_women_positions",
        "India women at the Olympic Games: final position by edition"),
    "fih_pro_league_india_men_standings": _pro_league_standings("M", "men"),
    "fih_pro_league_india_women_standings": _pro_league_standings("F", "women"),
    "fih_india_men_head_to_head_2020_2026": fih_india_men_head_to_head_2020_2026,
    "hockey_players_men_top_scorers": _player_series("M", "men", "men's", "hockey_players_men_top_scorers", "goals", "caps"),
    "hockey_players_women_top_scorers": _player_series("F", "women", "women's", "hockey_players_women_top_scorers", "goals", "caps"),
    "hockey_players_men_most_capped": _player_series("M", "men", "men's", "hockey_players_men_most_capped", "caps", "goals"),
    "hockey_players_women_most_capped": _player_series("F", "women", "women's", "hockey_players_women_most_capped", "caps", "goals"),
    "hockey_pro_league_india_men_top_scorers_by_season": _pro_league_top_scorers("M", "men"),
    "hockey_pro_league_india_women_top_scorers_by_season": _pro_league_top_scorers("F", "women"),
}

NOT_AVAILABLE = [
    {"item": "India men Olympic Games editions: 1932 (1932 Mens Olympic Games), 1952 (1952 Mens Olympic Games), 1980 (1980 Mens Olympic Games)",
     "reason": "FIH series listing includes India but the standings feed returned no data."},
    {"item": "India women Olympic Games editions: 1980 (1980 Womens Olympic Games)",
     "reason": "FIH series listing includes India but the standings feed returned no data."},
    {"item": "FIH all-time head-to-head records for India men",
     "reason": "No all-time H2H endpoint located; replaced by head-to-head aggregated from FIH 2020-2026 match history."},
    {"item": "olympics.com Olympic hockey results", "reason": "olympics.com request timed out; FIH official feeds used instead."},
    {"item": "All-time career goals and caps for India's hockey legends (e.g. Dhanraj Pillay, Dhyan Chand, Jyoti Sharma)",
     "reason": "FIH player profiles only carry goals from competitions FIH has recorded in its feeds and caps from the FIH era; "
              "Hockey India's site publishes no structured career-statistics table, so older players are missing or understated."},
    {"item": "Hockey India (hockeyindia.org) player career statistics",
     "reason": "No structured goals/caps listing is exposed by the Hockey India site; FIH player profiles are used instead."},
]


if __name__ == "__main__":
    import sys
    for name, producer in PRODUCERS.items():
        if len(sys.argv) > 1 and name not in sys.argv[1:]:
            continue
        try:
            result = producer()
            for s in result if isinstance(result, list) else [result]:
                print(f"{s['key']}: {len(s['labels'])} labels; datasets {[d['label'] for d in s['datasets']]}")
                print("   ", s["labels"][:14])
                print("   ", s["datasets"][0]["values"][:14])
        except Exception as exc:
            print(f"{name}: FAILED {exc}")

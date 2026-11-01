"""Build the Sports, Cricket and Hockey overlays (medal tallies, win/loss records, rankings) for both sites.

Every figure is attributed to the official body that publishes it: the IOC, IPC, Olympic Council of
Asia and Commonwealth Games Federation for Games medals (recent editions cross-checked against PIB,
Government of India), and the ICC, FIH, FIFA and each sport's world federation for team and individual
records. Federation data snapshots live in ``data/sports_sources/`` with their URLs and fetch dates;
``games_verification.json`` records which Games tallies were confirmed on an official page.
Medal tables are reconciled against their totals by the assertions below.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = (ROOT / "data" / "sports.json", ROOT / "docs" / "data" / "sports.json")
SNAPSHOTS = ROOT / "data" / "sports_sources"
CATEGORY = "Sports"
CRICKET, HOCKEY, FOOTBALL = "Cricket", "Hockey", "Football"
SUB_OLYMPIC = "Olympic & Paralympic Medals"
SUB_GAMES = "Asian & Commonwealth Games"
SUB_BATTING, SUB_BOWLING = "Batting: Past vs Current", "Bowling: Past vs Current"
SUB_HOCKEY_PLAYERS, SUB_FOOTBALL_PLAYERS = "Hockey Players: Past vs Current", "Footballers: Past vs Current"
CRICKET_SUBGROUPS = ("Men's Cricket", "Women's Cricket", "ICC Tournaments", "ICC Rankings", SUB_BATTING, SUB_BOWLING)
HOCKEY_SUBGROUPS = ("Men's Hockey", "Women's Hockey", "FIH Rankings & Pro League", SUB_HOCKEY_PLAYERS)
FOOTBALL_SUBGROUPS = ("Men's Football", "Women's Football", "FIFA Rankings", SUB_FOOTBALL_PLAYERS)
TEAM_SNAPSHOTS = ("cricket.json", "hockey.json", "football.json")

SRC_OLYMPICS = "https://www.olympics.com/en/olympic-games/olympic-results"
SRC_PARALYMPICS = "https://www.paralympic.org/india"
SRC_ASIAN = "https://www.ocasia.org/games/"
SRC_CWG = "https://thecgf.com/results"

GOLD, SILVER, BRONZE = "#e3b341", "#c0c6cf", "#cd7f32"

# Summer Olympics: (Games, athletes, gold, silver, bronze). India did not compete in 1904, 1908 or 1912.
OLYMPICS = [
    ("1900", 1, 0, 2, 0), ("1920", 6, 0, 0, 0), ("1924", 14, 0, 0, 0), ("1928", 21, 1, 0, 0),
    ("1932", 20, 1, 0, 0), ("1936", 27, 1, 0, 0), ("1948", 79, 1, 0, 0), ("1952", 64, 1, 0, 1),
    ("1956", 59, 1, 0, 0), ("1960", 45, 0, 1, 0), ("1964", 53, 1, 0, 0), ("1968", 25, 0, 0, 1),
    ("1972", 41, 0, 0, 1), ("1976", 20, 0, 0, 0), ("1980", 76, 1, 0, 0), ("1984", 48, 0, 0, 0),
    ("1988", 46, 0, 0, 0), ("1992", 53, 0, 0, 0), ("1996", 49, 0, 0, 1), ("2000", 65, 0, 0, 1),
    ("2004", 73, 0, 1, 0), ("2008", 56, 1, 0, 2), ("2012", 83, 0, 2, 4), ("2016", 117, 0, 1, 1),
    ("2020", 119, 1, 2, 4), ("2024", 110, 0, 1, 5),
]
OLYMPIC_SPORTS = [
    ("Field hockey", 8, 1, 4), ("Shooting", 1, 2, 4), ("Athletics", 1, 3, 0), ("Wrestling", 0, 2, 6),
    ("Badminton", 0, 1, 2), ("Boxing", 0, 0, 3), ("Weightlifting", 0, 1, 1), ("Tennis", 0, 0, 1),
]
OLYMPIC_TOTAL = (10, 10, 21)

# Summer Paralympics: (Games, athletes, gold, silver, bronze).
PARALYMPICS = [
    ("1968", 10, 0, 0, 0), ("1972", 10, 1, 0, 0), ("1984", 5, 0, 2, 2), ("1988", 2, 0, 0, 0),
    ("1992", 9, 0, 0, 0), ("1996", 9, 0, 0, 0), ("2000", 4, 0, 0, 0), ("2004", 12, 1, 0, 1),
    ("2008", 5, 0, 0, 0), ("2012", 10, 0, 1, 0), ("2016", 19, 2, 1, 1), ("2020", 54, 5, 8, 6),
    ("2024", 84, 7, 9, 13),
]
# The source's athletics row reads 8/16/13 against a row total of 35; 8/15/12 is the split that matches
# both that row total and the published column totals (16/21/23), and the Games-by-Games athletics medals.
PARALYMPIC_SPORTS = [
    ("Athletics", 8, 15, 12), ("Badminton", 3, 3, 3), ("Shooting", 3, 2, 4), ("Archery", 1, 0, 2),
    ("Swimming", 1, 0, 0), ("Table tennis", 0, 1, 0), ("Para powerlifting", 0, 0, 1), ("Judo", 0, 0, 1),
]
PARALYMPIC_TOTAL = (16, 21, 23)

# Asian Games: (edition, gold, silver, bronze).
ASIAN_GAMES = [
    ("1951", 15, 16, 20), ("1954", 5, 4, 8), ("1958", 5, 4, 4), ("1962", 10, 13, 10), ("1966", 7, 3, 11),
    ("1970", 6, 9, 10), ("1974", 4, 12, 12), ("1978", 11, 11, 6), ("1982", 13, 19, 25), ("1986", 5, 9, 23),
    ("1990", 1, 8, 14), ("1994", 4, 3, 16), ("1998", 7, 11, 17), ("2002", 11, 12, 13), ("2006", 10, 17, 26),
    ("2010", 14, 17, 34), ("2014", 11, 9, 37), ("2018", 16, 23, 31), ("2022", 28, 38, 41), ("2026", 21, 27, 37),
]
ASIAN_SPORTS = [
    ("Archery", 11, 8, 9), ("Athletics", 86, 111, 110), ("Badminton", 1, 2, 11), ("Boxing", 12, 17, 38),
    ("Bridge", 1, 1, 2), ("Canoeing", 0, 0, 2), ("Chess", 2, 2, 2), ("Cricket", 4, 0, 0), ("Cue sports", 5, 4, 6),
    ("Cycling", 0, 1, 2), ("Diving", 2, 1, 2), ("Equestrian", 4, 3, 7), ("Field hockey", 7, 11, 7),
    ("Football", 2, 0, 1), ("Golf", 4, 5, 0), ("Gymnastics", 0, 0, 1), ("Judo", 0, 0, 5), ("Kabaddi", 13, 1, 1),
    ("Kurash", 0, 1, 2), ("Mixed martial arts", 0, 0, 1), ("Roller sports", 0, 0, 4), ("Rowing", 2, 7, 20),
    ("Sailing", 1, 9, 16), ("Sepaktakraw", 0, 0, 3), ("Shooting", 19, 38, 38), ("Squash", 3, 6, 14),
    ("Soft tennis", 0, 0, 1), ("Swimming", 1, 2, 6), ("Table tennis", 0, 0, 4), ("Taekwondo", 0, 0, 1),
    ("Tennis", 10, 7, 17), ("Volleyball", 0, 1, 2), ("Water polo", 1, 1, 1), ("Weightlifting", 0, 6, 9),
    ("Wrestling", 13, 17, 41), ("Wushu", 0, 3, 8),
]
ASIAN_TOTAL = (204, 265, 395)

# Commonwealth Games: (edition, gold, silver, bronze, medal-table position or None when no medals).
# India did not compete in 1930, 1950, 1962 or 1986.
CWG = [
    ("1934", 0, 0, 1, 12), ("1938", 0, 0, 0, None), ("1954", 0, 0, 0, None), ("1958", 2, 1, 0, 8),
    ("1966", 3, 4, 3, 8), ("1970", 5, 3, 4, 6), ("1974", 4, 8, 3, 6), ("1978", 5, 5, 5, 6), ("1982", 5, 8, 3, 6),
    ("1990", 13, 8, 11, 5), ("1994", 6, 11, 7, 6), ("1998", 7, 10, 8, 7), ("2002", 30, 22, 17, 4),
    ("2006", 22, 17, 11, 4), ("2010", 38, 27, 36, 2), ("2014", 15, 30, 19, 5), ("2018", 26, 20, 20, 3),
    ("2022", 22, 16, 23, 4), ("2026", 13, 17, 9, 4),
]
CWG_SPORTS = [
    ("Shooting", 63, 44, 28), ("Wrestling", 49, 39, 26), ("Weightlifting", 47, 57, 37), ("Boxing", 18, 16, 20),
    ("Badminton", 10, 8, 13), ("Athletics", 9, 21, 22), ("Table tennis", 10, 5, 13), ("Archery", 3, 1, 4),
    ("Judo", 2, 6, 7), ("Field hockey", 1, 4, 1), ("Squash", 1, 2, 2), ("Tennis", 1, 1, 2), ("Lawn bowls", 1, 1, 0),
    ("Para powerlifting", 0, 0, 2), ("Gymnastics", 0, 1, 2), ("Cricket", 0, 1, 0), ("Swimming", 0, 0, 1),
]
CWG_TOTAL = (216, 207, 180)

def _sum(rows, start):
    return tuple(sum(row[index] for row in rows) for index in range(start, start + 3))


# Per-sport splits come from the federations' cumulative tables; the official edition tallies above add
# one medal each for Hangzhou 2022 (bronze) and Birmingham 2022 (gold), so those splits are one short.
SPLIT_GAPS = {"Asian Games": (0, 0, 1), "Commonwealth Games": (1, 0, 0)}


def validate() -> None:
    assert _sum(OLYMPICS, 2) == OLYMPIC_TOTAL == _sum(OLYMPIC_SPORTS, 1)
    assert _sum(PARALYMPICS, 2) == PARALYMPIC_TOTAL == _sum(PARALYMPIC_SPORTS, 1)
    assert _sum(ASIAN_GAMES, 1) == ASIAN_TOTAL
    assert _sum(CWG, 1) == CWG_TOTAL
    for total, rows, gap in ((ASIAN_TOTAL, ASIAN_SPORTS, SPLIT_GAPS["Asian Games"]), (CWG_TOTAL, CWG_SPORTS, SPLIT_GAPS["Commonwealth Games"])):
        assert tuple(t - g for t, g in zip(total, gap)) == _sum(rows, 1)


def medal_datasets(rows, start):
    return [
        {"label": label, "color": color, "values": [row[start + offset] for row in rows]}
        for offset, (label, color) in enumerate((("Gold", GOLD), ("Silver", SILVER), ("Bronze", BRONZE)))
    ]


def series(labels, *, title, subtitle, subgroup, source, note, explain, color=GOLD, suffix=" medals",
           frequency="Each edition", unit="medals", values=None, datasets=None, chart_type="bar", horizontal=False,
           category=CATEGORY):
    item = {"labels": labels}
    if datasets is not None:
        item["datasets"] = datasets
    else:
        item["values"] = values
    item["chartType"] = chart_type
    if horizontal:
        item["indexAxis"] = "y"
    if chart_type == "bar" and datasets is None:
        item["scope"] = "category"
    item.update(source=source, unit=unit, note=note, meta={
        "title": title, "subtitle": subtitle, "frequency": frequency, "color": color, "suffix": suffix,
        "category": category, "subgroup": subgroup, "explain": explain,
    })
    return item


def by_total(rows):
    return sorted(rows, key=lambda row: (-(row[1] + row[2] + row[3]), -row[1], row[0]))


def medals_by_sport_across_events(limit=24):
    events = (("Olympics", OLYMPIC_SPORTS, "#58a6ff"), ("Paralympics", PARALYMPIC_SPORTS, "#bc8cff"),
              ("Asian Games", ASIAN_SPORTS, "#ff9933"), ("Commonwealth Games", CWG_SPORTS, "#3fb950"))
    totals: dict[str, dict[str, int]] = {}
    for event, rows, _ in events:
        for sport, gold, silver, bronze in rows:
            totals.setdefault(sport, {})[event] = gold + silver + bronze
    ranked = sorted(totals, key=lambda sport: (-sum(totals[sport].values()), sport))
    shown, rest = ranked[:limit], ranked[limit:]
    labels = shown + ([f"Other sports ({len(rest)})"] if rest else [])
    datasets = []
    for event, _, color in events:
        values = [totals[sport].get(event, 0) for sport in shown]
        if rest:
            values.append(sum(totals[sport].get(event, 0) for sport in rest))
        datasets.append({"label": event, "color": color, "values": values})
    return labels, datasets, len(ranked)


LABEL_COLORS = {
    "won": "#3fb950", "lost": "#ff7b72", "drawn": "#8b949e", "draw": "#8b949e", "tied": "#f6c344", "no result": "#58a6ff",
    "gold": GOLD, "silver": SILVER, "bronze": BRONZE, "points": "#ff9933", "rating": "#58a6ff", "ranking points": "#58a6ff",
    "goals for": "#3fb950", "goals against": "#ff7b72", "final rank": "#58a6ff", "best rank": "#3fb950", "worst rank": "#ff7b72",
    "shootout wins": "#a5d6a7", "shootout losses": "#f4a6a0",
}
PALETTE = ("#58a6ff", "#ff9933", "#3fb950", "#bc8cff", "#f778ba", "#e3b341", "#39c5cf", "#ff7b72")
RESULT_LABELS = {"won", "lost", "drawn", "draw", "tied", "no result", "drawn (as listed)", "shootout wins", "shootout losses"}
TOTAL_LABELS = {"matches", "played"}
RANK_LABELS = {"final position", "position", "rank", "final rank", "best rank", "worst rank", "world rank", "ranking"}


def load_snapshot(name: str) -> dict:
    path = SNAPSHOTS / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"series": [], "not_available": []}


def clean_url(raw: str, fallback: str) -> str:
    first = str(raw or "").split(" | ")[0].split("; ")[0].split(" (")[0].strip()
    return fallback if not first.startswith("http") or "{" in first or "<" in first or "/api" in first or "graphql" in first else first


def colour_for(label: str, index: int) -> str:
    return LABEL_COLORS.get(label.lower().replace(" (as listed)", ""), PALETTE[index % len(PALETTE)])


def numeric(values) -> list:
    return [value if isinstance(value, (int, float)) else None for value in values]


def official_note(item: dict, extra: str = "") -> str:
    parts = [f"Official source: {item['publisher']} ({item['as_of']})."]
    if item.get("notes"):
        parts.append(item["notes"])
    if extra:
        parts.append(extra)
    return " ".join(parts)


def pick(item: dict, wanted) -> list:
    return [ds for ds in item["datasets"] if ds["label"].lower() in wanted]


def as_of_label(raw: str) -> str:
    dates = [f"{y}-{m}-{d}" for y, m, d in re.findall(r"(\d{4})-(\d{2})-(\d{2})", raw)]
    dates += [f"{y}-{int(m):02d}-{int(d):02d}" for m, d, y in re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{4})", raw)]
    return f"As of {max(dates)}" if dates else f"As of {raw[:40]}"


def snapshot_series(item: dict, *, category: str, subgroup: str, source: str, why: str, unit: str = "matches",
                    mode: str = "auto", title: str | None = None, extra_note: str = "") -> dict[str, dict]:
    """Turn one federation snapshot into one or two chart series (rank line + record bars)."""
    labels = [str(label) for label in item["labels"]]
    prefix = "sports" if category == CATEGORY else category.lower()
    key = item["key"] if item["key"].startswith(prefix + "_") else f"{prefix}_{item['key']}"
    common = dict(category=category, subgroup=subgroup, source=source, frequency=as_of_label(str(item['as_of'])))
    out: dict[str, dict] = {}
    ranks = pick(item, RANK_LABELS)
    results = pick(item, RESULT_LABELS)
    medals = pick(item, {"gold", "silver", "bronze"})
    horizontal = len(labels) > 8 and mode != "line"
    if mode == "player":
        for index, ds in enumerate(item["datasets"][:2]):
            metric = ds["label"]
            values = numeric(ds["values"])
            if not any(value is not None for value in values):
                continue
            chart_key = key if index == 0 else f"{key}_{re.sub(r'[^a-z0-9]+', '_', metric.lower()).strip('_')}"
            chart_title = title or item["title"] if index == 0 else f"{title or item['title']} — {metric.lower()}"
            out[chart_key] = series(labels, values=values, horizontal=True, title=chart_title, subtitle=item["description"],
                                    suffix="", unit=metric.lower(), color="#ff9933" if index == 0 else "#58a6ff",
                                    note=official_note(item, "Players are marked (current) or (past) using the rule in this note. " + extra_note),
                                    explain={"what": item["description"],
                                             "read": f"Each bar is one player's {metric.lower()}; the label says whether they are a current or a past India player.",
                                             "why": why}, **common)
        return out
    if mode == "rankbar":
        rank = ranks[0]
        out[key] = series(labels, values=numeric(rank["values"]), title=title or item["title"], subtitle=item["description"], suffix="", unit="rank",
                          color="#58a6ff", note=official_note(item, "Lower is better: 1 is the top-ranked team. " + extra_note),
                          explain={"what": item["description"], "read": "Shorter bars are better; a bar of 1 means India is ranked No. 1.", "why": why}, **common)
        return out
    if mode == "line" or (ranks and not results and not medals):
        datasets = ranks or item["datasets"]
        out[key] = series(labels, datasets=[{"label": ds["label"], "color": colour_for(ds["label"], i), "values": numeric(ds["values"])} for i, ds in enumerate(datasets)],
                          chart_type="line", title=title or item["title"], subtitle=item["description"], suffix="", unit="rank", color="#58a6ff",
                          note=official_note(item, "Lower is better. " + extra_note),
                          explain={"what": item["description"], "read": "Each point is a position or rank; a falling line means India moved up.", "why": why}, **common)
        return out
    if ranks and (results or pick(item, {"points"})):
        rank = ranks[0]
        out[f"{key}_position"] = series(labels, values=numeric(rank["values"]), chart_type="line", title=f"{title or item['title']} — {rank['label'].lower()}",
                                        subtitle=f"{rank['label']} by edition (1 = top)", suffix="", unit="position", color="#58a6ff",
                                        note=official_note(item, "Lower is better. " + extra_note),
                                        explain={"what": item["description"], "read": "A lower point means a better finish; 1 is the winner.", "why": why}, **common)
        key = f"{key}_record"
    if medals:
        datasets = [{"label": ds["label"], "color": colour_for(ds["label"], i), "values": numeric(ds["values"])} for i, ds in enumerate(medals)]
        out[key] = series(labels, datasets=datasets, horizontal=horizontal, title=title or item["title"], subtitle=item["description"],
                          note=official_note(item, extra_note), color=GOLD,
                          explain={"what": item["description"], "read": "Bars are split into gold, silver and bronze; hover for exact counts.", "why": why}, **common)
        return out
    if results:
        datasets = [{"label": ds["label"].replace(" (as listed)", ""), "color": colour_for(ds["label"], i), "values": numeric(ds["values"])} for i, ds in enumerate(results)
                    if any(value for value in numeric(ds["values"]))]
        totals = pick(item, TOTAL_LABELS)
        played = f" Matches played: {', '.join(f'{l} {v}' for l, v in zip(labels, totals[0]['values']) if v is not None)}." if totals and len(labels) <= 12 else ""
        out[key] = series(labels, datasets=datasets, horizontal=horizontal, title=title or item["title"], subtitle=item["description"],
                          suffix=" matches", unit="matches", color="#3fb950", note=official_note(item, (played + " " + extra_note).strip()),
                          explain={"what": item["description"], "read": "Compare the green (won) and red (lost) bars for each row; hover for exact counts.", "why": why}, **common)
        goals = pick(item, {"goals for", "goals against"})
        if goals:
            out[f"{key}_goals"] = series(labels, datasets=[{"label": ds["label"], "color": colour_for(ds["label"], i), "values": numeric(ds["values"])} for i, ds in enumerate(goals)],
                                         horizontal=horizontal, title=f"{title or item['title']} — goals", subtitle="Goals scored and conceded",
                                         suffix=" goals", unit="goals", color="#3fb950", note=official_note(item, extra_note),
                                         explain={"what": "Goals scored and conceded in the same matches.", "read": "Green above red means India outscored opponents.", "why": why}, **common)
        return out
    value_ds = pick(item, {"rating", "ranking points", "points", "elo", "rating points"})
    if not value_ds and len(item["datasets"]) > 1:
        datasets = [{"label": ds["label"], "color": colour_for(ds["label"], i), "values": numeric(ds["values"])} for i, ds in enumerate(item["datasets"])]
        out[key] = series(labels, datasets=datasets, horizontal=horizontal, title=title or item["title"], subtitle=item["description"],
                          suffix="", unit="count" if unit == "medals" else unit, color="#58a6ff", note=official_note(item, extra_note),
                          explain={"what": item["description"], "read": "Each colour is a separate measure; hover for exact values.", "why": why}, **common)
        return out
    ds = (value_ds or item["datasets"])[0]
    out[key] = series(labels, values=numeric(ds["values"]), horizontal=horizontal or len(labels) > 5, title=title or item["title"], subtitle=item["description"],
                      suffix="", unit=ds["label"].lower() if unit in ("matches", "medals") else unit, color="#58a6ff", note=official_note(item, extra_note),
                      explain={"what": item["description"], "read": f"Bars show {ds['label'].lower()}; India's bar is the one to compare against the leaders.", "why": why}, **common)
    return out


ICC_RANKINGS = "https://www.icc-cricket.com/rankings"
FIH_EVENTS = "https://www.fih.hockey/events"
TEAM_CONFIG = {
    "cricket_men_alltime_results": (CRICKET, "Men's Cricket", "India men's all-time international record across Test, ODI and T20I.", {}),
    "cricket_men_test_by_opposition": (CRICKET, "Men's Cricket", "Head-to-head Test records show where India dominates and where it still struggles away from home.", {}),
    "cricket_men_odi_by_opposition": (CRICKET, "Men's Cricket", "ODI records against the strongest opponents, the format India has played most.", {}),
    "cricket_men_t20i_by_opposition": (CRICKET, "Men's Cricket", "T20Is are India's strongest format; these are the records against its most frequent opponents.", {}),
    "cricket_women_alltime_results": (CRICKET, "Women's Cricket", "India women's complete international record across all three formats.", {}),
    "icc_mens_odi_world_cup_india": (CRICKET, "ICC Tournaments", "India won the ODI World Cup in 1983 and 2011.", {}),
    "icc_champions_trophy_india": (CRICKET, "ICC Tournaments", "The Champions Trophy is the ICC's elite eight-team ODI event.", {}),
    "icc_mens_t20_world_cup_india": (CRICKET, "ICC Tournaments", "India won the first T20 World Cup in 2007.", {}),
    "icc_womens_odi_world_cup_india": (CRICKET, "ICC Tournaments", "The women's ODI World Cup is the oldest world cup in cricket (1973).", {}),
    "icc_womens_t20_world_cup_india": (CRICKET, "ICC Tournaments", "Women's T20 World Cup results by edition.", {}),
    "icc_rank_india_summary": (CRICKET, "ICC Rankings", "India's position in every ICC team table at a glance.", {"source": ICC_RANKINGS, "mode": "rankbar"}),
    "icc_rank_men_test_top10": (CRICKET, "ICC Rankings", "Ratings weight recent series more heavily, so they show current form.", {"source": "https://www.icc-cricket.com/rankings/team-rankings/mens/test"}),
    "icc_rank_men_odi_top10": (CRICKET, "ICC Rankings", "Current ODI pecking order among the top ten teams.", {"source": "https://www.icc-cricket.com/rankings/team-rankings/mens/odi"}),
    "icc_rank_men_t20i_top10": (CRICKET, "ICC Rankings", "Current T20I pecking order among the top ten teams.", {"source": "https://www.icc-cricket.com/rankings/team-rankings/mens/t20i"}),
    "icc_rank_women_odi_top10": (CRICKET, "ICC Rankings", "Current women's ODI pecking order.", {"source": "https://www.icc-cricket.com/rankings/team-rankings/womens/odi"}),
    "icc_rank_women_t20i_top10": (CRICKET, "ICC Rankings", "Current women's T20I pecking order.", {"source": "https://www.icc-cricket.com/rankings/team-rankings/womens/t20i"}),
    "fih_rank_men_top10": (HOCKEY, "FIH Rankings & Pro League", "FIH ranking points decide seedings for the Olympics and World Cup.", {}),
    "fih_rank_women_top10": (HOCKEY, "FIH Rankings & Pro League", "Where India's women stand against the world's best.", {}),
    "fih_pro_league_india_men_standings": (HOCKEY, "FIH Rankings & Pro League", "The Pro League is hockey's top-tier home-and-away competition.", {"source": FIH_EVENTS}),
    "fih_pro_league_india_women_standings": (HOCKEY, "FIH Rankings & Pro League", "India women's seasons in the Pro League.", {"source": FIH_EVENTS}),
    "fih_world_cup_india_men_positions": (HOCKEY, "Men's Hockey", "India won the 1975 World Cup in Kuala Lumpur.", {"source": FIH_EVENTS}),
    "fih_olympics_india_men_positions": (HOCKEY, "Men's Hockey", "Eight Olympic golds make hockey India's most successful Olympic sport.",
                                         {"source": FIH_EVENTS, "extra_note": "1932, 1952 and 1980 (all gold medals) are missing from the FIH standings feed; see the Olympic medals series in the Sports group."}),
    "fih_india_men_head_to_head_2020_2026": (HOCKEY, "Men's Hockey", "Recent head-to-heads show how India fares against the top European and Oceanian sides.", {}),
    "fih_world_cup_india_women_positions": (HOCKEY, "Women's Hockey", "India women's World Cup finishes.", {"source": FIH_EVENTS}),
    "fih_olympics_india_women_positions": (HOCKEY, "Women's Hockey", "India women reached the Olympic semi-finals at Tokyo 2020.", {"source": FIH_EVENTS}),
    "fifa_rank_history_india_men": (FOOTBALL, "FIFA Rankings", "FIFA rankings track India's standing among 211 member associations.", {"mode": "line"}),
    "fifa_rank_history_india_women": (FOOTBALL, "FIFA Rankings", "India women's FIFA ranking over time.", {"mode": "line"}),
    "fifa_india_men_results_by_competition": (FOOTBALL, "Men's Football", "Results by competition separate friendlies from World Cup and Asian Cup qualifying.",
                                              {"source": "https://inside.fifa.com/fifa-rankings/world-ranking/IND?gender=men"}),
}
HOMES = {CRICKET: ICC_RANKINGS, HOCKEY: FIH_EVENTS, FOOTBALL: "https://inside.fifa.com/fifa-rankings/world-ranking/IND?gender=men"}


def route(item: dict) -> tuple[str, str, str, dict] | None:
    """Place a snapshot series that has no explicit TEAM_CONFIG entry (new fetcher output)."""
    key, sport = item["key"], item.get("sport")
    category = {"Cricket": CRICKET, "Hockey": HOCKEY, "Football": FOOTBALL}.get(sport)
    if not category:
        return None
    why = item.get("why") or {
        CRICKET: "Official cricket statistics put today's India players alongside the greats who came before them.",
        HOCKEY: "FIH records show who has carried India's attack and defence across eras.",
        FOOTBALL: "FIFA and AIFF records show how India's footballers compare across generations.",
    }[category]
    women = "women" in key
    players = SUB_HOCKEY_PLAYERS if category == HOCKEY else SUB_FOOTBALL_PLAYERS
    if "players" in key or "player_" in key:
        if "rank" in key:
            return category, "ICC Rankings" if category == CRICKET else players, why, {}
        if category == CRICKET:
            return category, SUB_BOWLING if "bowl" in key else SUB_BATTING, why, {"mode": "player"}
        return category, players, why, {"mode": "player"}
    if category == CRICKET:
        subgroup = "ICC Rankings" if "rank" in key else "ICC Tournaments" if key.startswith("icc_") else "Women's Cricket" if women else "Men's Cricket"
    elif category == HOCKEY:
        subgroup = "FIH Rankings & Pro League" if ("rank" in key or "pro_league" in key) else "Women's Hockey" if women else "Men's Hockey"
    else:
        subgroup = "FIFA Rankings" if "rank" in key else "Women's Football" if women else "Men's Football"
    return category, subgroup, why, {"mode": "line"} if "rank_history" in key else {}


def team_series() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for name in TEAM_SNAPSHOTS:
        for item in load_snapshot(name)["series"]:
            if not item.get("labels") or not item.get("datasets"):
                continue
            config = TEAM_CONFIG.get(item["key"]) or route(item)
            if not config:
                continue
            category, subgroup, why, options = config
            options = dict(options)
            source = options.pop("source", None) or clean_url(item["source_url"], HOMES[category])
            out.update(snapshot_series(item, category=category, subgroup=subgroup, source=source, why=why, **options))
    return out


INDIVIDUAL_SUBGROUPS = {
    "Badminton": "Racket Sports", "Tennis": "Racket Sports",
    "Wrestling": "Combat & Strength", "Boxing": "Combat & Strength", "Weightlifting": "Combat & Strength",
    "Athletics": "Athletics", "Shooting": "Shooting & Archery", "Archery": "Shooting & Archery",
    "Chess": "Chess & Kabaddi", "Kabaddi": "Chess & Kabaddi",
}
SPORTS_SUBGROUPS = (SUB_OLYMPIC, SUB_GAMES, "Athletics", "Shooting & Archery", "Combat & Strength", "Racket Sports", "Chess & Kabaddi")


INDIVIDUAL_HOMES = {
    "Badminton": "https://bwfbadminton.com/rankings/", "Tennis": "https://www.daviscup.com/",
    "Wrestling": "https://uww.org/events/senior-world-championships", "Boxing": "https://www.iba.sport/",
    "Weightlifting": "https://iwf.sport/results/results-by-events/", "Athletics": "https://worldathletics.org/competitions",
    "Shooting": "https://www.issf-sports.org/competitions", "Archery": "https://www.worldarchery.sport/events",
    "Chess": "https://ratings.fide.com/", "Kabaddi": "https://www.prokabaddi.com/standings",
}
INDIVIDUAL_OPTIONS = {
    "badminton_bwf_world_ranking_indians_by_discipline": {"source": "https://bwfbadminton.com/rankings/"},
    "badminton_bwf_best_indian_world_rank": {"mode": "rankbar", "source": "https://bwfbadminton.com/rankings/"},
    "badminton_thomas_uber_cup_india_finish": {"mode": "line"},
    "badminton_sudirman_cup_india_finish": {"mode": "line"},
    "chess_india_federation_rank_top10_average": {"mode": "line"},
    "tennis_bjk_cup_ties_by_decade": {"source": "https://www.billiejeankingcup.com/"},
    "kabaddi_pkl_season12_standings": {"extra_note": "The Pro Kabaddi League is a franchise league run under the Amateur Kabaddi Federation of India; official national-team results for the Asian Games are in the Asian & Commonwealth Games subgroup."},
}


def individual_series() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for item in load_snapshot("individual_sports.json")["series"]:
        subgroup = INDIVIDUAL_SUBGROUPS.get(item.get("sport"))
        if not subgroup or not item.get("labels") or not item.get("datasets"):
            continue
        options = dict(INDIVIDUAL_OPTIONS.get(item["key"], {}))
        source = options.pop("source", None) or clean_url(item.get("source_url"), INDIVIDUAL_HOMES.get(item["sport"], "https://yas.gov.in/sports"))
        why = item.get("why") or f"{item['sport']} results published by its world governing body."
        out.update(snapshot_series(item, category=CATEGORY, subgroup=subgroup, source=source, why=why, unit="medals", **options))
    return out


def build() -> dict:
    validate()
    out: dict[str, dict] = {}
    olympic_note = "IOC official results database; Paris 2024 (0/1/5) and Tokyo 2020 (1/2/4) are confirmed by olympics.com and PIB (PRID 2045963). Summer Games only; India has not won a Winter Olympic medal. 1904, 1908 and 1912 had no Indian team; 1940 and 1944 were cancelled."

    all_events = [("Olympics", OLYMPIC_TOTAL), ("Paralympics", PARALYMPIC_TOTAL), ("Asian Games", ASIAN_TOTAL), ("Commonwealth Games", CWG_TOTAL)]
    out["sports_medals_by_event"] = series(
        [name for name, _ in all_events], datasets=medal_datasets([(name, *total) for name, total in all_events], 1),
        title="All-Time Medals by Multi-Sport Event", subtitle="India's gold, silver and bronze across the four major multi-sport Games",
        subgroup=SUB_OLYMPIC, frequency="All-time totals", source=SRC_OLYMPICS,
        note="Summer Olympics, Summer Paralympics, Asian Games (to Aichi–Nagoya 2026) and Commonwealth Games (to Glasgow 2026), from the IOC, IPC, OCA and CGF records. Recent editions were checked against IPC result pages and PIB (Government of India) releases.",
        explain={"what": "India's all-time medal haul at each of the four major multi-sport events, split by medal colour.",
                 "read": "Each group of bars is one event; compare heights to see where India wins most and how golds compare with silvers and bronzes.",
                 "why": "Regional Games are far less competitive than the Olympics, so medal counts are only comparable within an event, not across them."})

    labels, datasets, sport_count = medals_by_sport_across_events()
    out["sports_medals_by_sport_all_events"] = series(
        labels, datasets=datasets, horizontal=True,
        title="Medals by Sport Across All Major Games", subtitle=f"Total medals in each of the {sport_count} sports India has medalled in, by event",
        subgroup=SUB_OLYMPIC, frequency="All-time totals", source=SRC_ASIAN, color="#ff9933",
        note="Sum of gold, silver and bronze from the IOC, IPC, OCA and CGF medals-by-sport tables. Sports beyond the top 24 are combined. The OCA and CGF per-sport splits are one medal short of the official 2022 edition tallies (one Hangzhou bronze, one Birmingham gold).",
        explain={"what": "Every sport in which India has won a medal at the Olympics, Paralympics, Asian Games or Commonwealth Games.",
                 "read": "Bars are split by event; hover a bar to see how many medals each Games contributed.",
                 "why": "Shooting, wrestling, athletics, weightlifting and boxing carry India's medal tally across every level of competition."})

    out["sports_olympic_medals_by_games"] = series(
        [row[0] for row in OLYMPICS], datasets=medal_datasets(OLYMPICS, 2),
        title="Olympic Medals by Games", subtitle="Gold, silver and bronze won by India at each Summer Olympics",
        subgroup=SUB_OLYMPIC, source=SRC_OLYMPICS, note=olympic_note,
        explain={"what": "India's medals at every Summer Olympics it has entered, from Paris 1900 to Paris 2024.",
                 "read": "Each year is one Games. Every gold before 2008 came in men's field hockey; individual medals arrive at every Games from 1996.",
                 "why": "Shows the shift from a single-sport hockey dynasty to a broader base in shooting, wrestling, badminton, boxing and athletics."})
    out["sports_olympic_medals_by_sport"] = series(
        [row[0] for row in OLYMPIC_SPORTS], datasets=medal_datasets(OLYMPIC_SPORTS, 1), horizontal=True,
        title="Olympic Medals by Sport", subtitle="India's 41 Summer Olympic medals by sport and colour",
        subgroup=SUB_OLYMPIC, frequency="All-time totals", source=SRC_OLYMPICS, note=olympic_note,
        explain={"what": "All 41 of India's Olympic medals grouped by sport.",
                 "read": "Field hockey holds 8 of India's 10 golds; the other two came in shooting (2008) and athletics (2020).",
                 "why": "Highlights where Olympic success has been concentrated and where it is spreading."})
    out["sports_olympic_medal_split"] = series(
        ["Gold", "Silver", "Bronze"], values=list(OLYMPIC_TOTAL), chart_type="doughnut",
        title="Olympic Medal Colour Split", subtitle="Share of gold, silver and bronze in India's 41 Olympic medals",
        subgroup=SUB_OLYMPIC, frequency="All-time totals", source=SRC_OLYMPICS, note=olympic_note,
        explain={"what": "How India's Olympic medals divide between gold, silver and bronze.",
                 "read": "Slices show each colour's share; hover for counts.",
                 "why": "Half of India's medals are bronze, a sign of podium depth rather than event dominance."})
    out["sports_olympic_athletes_by_games"] = series(
        [row[0] for row in OLYMPICS], values=[row[1] for row in OLYMPICS], chart_type="line",
        title="Indian Athletes at the Olympics", subtitle="Size of India's contingent at each Summer Olympics",
        subgroup=SUB_OLYMPIC, source=SRC_OLYMPICS, suffix=" athletes", unit="athletes", color="#58a6ff", note=olympic_note,
        explain={"what": "The number of athletes India sent to each Summer Olympics.",
                 "read": "Contingents passed 100 for the first time in Rio 2016.",
                 "why": "Qualification breadth is a leading indicator for medal counts."})
    out["sports_paralympic_medals_by_games"] = series(
        [row[0] for row in PARALYMPICS], datasets=medal_datasets(PARALYMPICS, 2),
        title="Paralympic Medals by Games", subtitle="Gold, silver and bronze won by India at each Summer Paralympics",
        subgroup=SUB_OLYMPIC, source=SRC_PARALYMPICS,
        note="IPC historical results database. 1972, 1984, 2004, 2012, 2016, 2020 and 2024 were checked against the IPC medal standings pages. India did not compete in 1976 or 1980. Tokyo 2020 (19 medals) and Paris 2024 (29) account for most of the 60-medal total.",
        explain={"what": "India's medals at every Summer Paralympics it has entered, from Tel Aviv 1968 to Paris 2024.",
                 "read": "Murlikant Petkar's 1972 swimming gold was the first; the surge comes after 2016.",
                 "why": "India's Paralympic programme now wins more medals per Games than its Olympic one."})
    out["sports_paralympic_medals_by_sport"] = series(
        [row[0] for row in PARALYMPIC_SPORTS], datasets=medal_datasets(PARALYMPIC_SPORTS, 1), horizontal=True,
        title="Paralympic Medals by Sport", subtitle="India's 60 Summer Paralympic medals by sport and colour",
        subgroup=SUB_OLYMPIC, frequency="All-time totals", source=SRC_PARALYMPICS,
        note="IPC historical results by sport. IPC confirms 8 athletics golds; the athletics split 8/15/12 is the one that reconciles with India's 60-medal IPC total.",
        explain={"what": "All 60 of India's Paralympic medals grouped by sport.",
                 "read": "Athletics (javelin, high jump, club and discus throws) supplies well over half of all medals.",
                 "why": "Shows the sports where India's para-athletes have become world-class."})

    out["sports_asian_games_medals_by_edition"] = series(
        [row[0] for row in ASIAN_GAMES], datasets=medal_datasets(ASIAN_GAMES, 1),
        title="Asian Games Medals by Edition", subtitle="Gold, silver and bronze won by India at every Asian Games since 1951",
        subgroup=SUB_GAMES, source=SRC_ASIAN,
        note="Olympic Council of Asia records. 2014, Hangzhou 2022 (28/38/41 — 107 medals, India's best) and Aichi–Nagoya 2026 are confirmed by PIB releases; for Jakarta 2018 the OCA table (16/23/31) is used, while a 2026 PIB summary lists 15/24/30 from before a medal reallocation.",
        explain={"what": "India's medals at each Asian Games, from the inaugural 1951 New Delhi Games to 2026.",
                 "read": "Group heights track the size of India's haul; bronzes have grown fastest as the programme has expanded.",
                 "why": "The Asian Games are India's main benchmark against China, Japan and Korea."})
    rows = by_total(ASIAN_SPORTS)
    out["sports_asian_games_medals_by_sport"] = series(
        [row[0] for row in rows], datasets=medal_datasets(rows, 1), horizontal=True,
        title="Asian Games Medals by Sport", subtitle=f"India's {sum(ASIAN_TOTAL)} Asian Games medals across {len(ASIAN_SPORTS)} sports",
        subgroup=SUB_GAMES, frequency="All-time totals", source=SRC_ASIAN, note="Sorted by total medals.",
        explain={"what": "Every sport in which India has won an Asian Games medal.",
                 "read": "Athletics alone accounts for over a third of all medals; kabaddi has 13 golds from 15 medals.",
                 "why": "Shows both the depth sports (athletics, shooting, wrestling, boxing) and the dominant niches (kabaddi, cricket)."})
    out["sports_cwg_medals_by_edition"] = series(
        [row[0] for row in CWG], datasets=medal_datasets(CWG, 1),
        title="Commonwealth Games Medals by Edition", subtitle="Gold, silver and bronze won by India at each Commonwealth Games",
        subgroup=SUB_GAMES, source=SRC_CWG,
        note="Commonwealth Games Federation results. 2014, 2018, Birmingham 2022 (22/16/23) and Glasgow 2026 are confirmed by PIB releases. India did not compete in 1930, 1950, 1962 or 1986. Best finish: 2nd at Delhi 2010 (101 medals). Glasgow 2026 had a reduced sports programme.",
        explain={"what": "India's medals at each Commonwealth Games it has entered, from London 1934 to Glasgow 2026.",
                 "read": "Peaks align with programmes rich in shooting, wrestling and weightlifting, and with the home Games of 2010.",
                 "why": "Programme changes (for example, shooting's absence in 2022) move India's tally as much as performance does."})
    out["sports_cwg_medal_table_rank"] = series(
        [row[0] for row in CWG if row[4]], values=[row[4] for row in CWG if row[4]], chart_type="line",
        title="Commonwealth Games Medal-Table Position", subtitle="India's rank in the overall medal table at each Games (1 = top)",
        subgroup=SUB_GAMES, source=SRC_CWG, suffix="", unit="rank", color="#3fb950",
        note="Lower is better. 1938 and 1954 are omitted because India won no medals there.",
        explain={"what": "Where India finished in the Commonwealth Games medal table.",
                 "read": "A falling line means improvement; India has been in the top five at every Games since 2002.",
                 "why": "Rank normalises for changes in the number of events between Games."})
    rows = by_total(CWG_SPORTS)
    out["sports_cwg_medals_by_sport"] = series(
        [row[0] for row in rows], datasets=medal_datasets(rows, 1), horizontal=True,
        title="Commonwealth Games Medals by Sport", subtitle=f"India's {sum(CWG_TOTAL)} Commonwealth Games medals across {len(CWG_SPORTS)} sports",
        subgroup=SUB_GAMES, frequency="All-time totals", source=SRC_CWG, note="Sorted by total medals.",
        explain={"what": "Every sport in which India has won a Commonwealth Games medal.",
                 "read": "Shooting, wrestling and weightlifting together account for nearly two thirds of all medals.",
                 "why": "These three sports are the backbone of India's Commonwealth success, which is why their inclusion in a Games matters."})

    out.update(team_series())
    out.update(individual_series())
    return out


def main() -> None:
    result = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": "Official records of the IOC, IPC, OCA, CGF, PIB (Government of India), ICC, FIH, FIFA and the world federation of each sport",
        "series": build(),
    }
    result["series_count"] = len(result["series"])
    text = json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n"
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(f"Wrote {result['series_count']} sports series")


if __name__ == "__main__":
    main()

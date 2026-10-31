"""Build Indian election composition indices from the recent constituency snapshot."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "recent-indian-elections.json"
OUTPUTS = (ROOT / "data" / "election-indices.json", ROOT / "docs" / "data" / "election-indices.json")
NOTA = "None of the Above"
TOP_SLICES = 10
MIN_STATE_SEATS = 4
MARGIN_BANDS = ((1, "Under 1 point"), (5, "1–5 points"), (10, "5–10 points"), (20, "10–20 points"), (float("inf"), "20+ points"))
WINNER_BANDS = ((30, "Under 30%"), (40, "30–40%"), (50, "40–50%"), (60, "50–60%"), (float("inf"), "60% or more"))
CANDIDATE_BANDS = ((5, "Up to 5"), (10, "6–10"), (15, "11–15"), (20, "16–20"), (float("inf"), "21 or more"))
SUBGROUP_LS = "Lok Sabha 2024 — National"
SUBGROUP_LS_STATES = "Lok Sabha 2024 — States"
SUBGROUP_COMPARE = "Election Comparisons Across States"
SUBGROUP_ASSEMBLY = "State Assembly Results 2022–2026"


def _band(value: float, bands) -> str:
    return next(label for limit, label in bands if value < limit)


def _ranked(counter: Counter, limit: int = TOP_SLICES) -> tuple[list[str], list[float]]:
    ranked = [(label, value) for label, value in counter.most_common() if value > 0]
    top, rest = ranked[:limit], ranked[limit:]
    labels = [label for label, _ in top]
    values = [value for _, value in top]
    if rest:
        labels.append(f"Other ({len(rest)})")
        values.append(sum(value for _, value in rest))
    return labels, values


def _ordered(counter: Counter, bands) -> tuple[list[str], list[int]]:
    labels = [label for _, label in bands if counter[label]]
    return labels, [counter[label] for label in labels]


def _contests(observations: list[dict]) -> dict[tuple, list[dict]]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in observations:
        seat = row["constituency"].casefold() if row["election_type"] == "Lok Sabha" else row["constituency_number"] or row["constituency"].casefold()
        grouped[(row["year"], row["election_type"], row["state_or_ut"], seat)].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: row["votes"] if row["votes"] is not None else float("inf"), reverse=True)
    return grouped


def _series(key: str, labels, values, *, title: str, subtitle: str, frequency: str, unit: str,
            subgroup: str, note: str, source: str, color: str = "#ff9933", chart: str = "doughnut") -> tuple[str, dict]:
    shape = {"chartType": "doughnut", "scope": "category"} if chart == "doughnut" else {"chartType": "bar", "indexAxis": "y", "scope": "state"}
    return key, {
        "labels": labels,
        "values": values,
        **shape,
        "source": source,
        "unit": unit.strip(),
        "note": note,
        "meta": {
            "title": title,
            "subtitle": subtitle,
            "frequency": frequency,
            "color": color,
            "suffix": unit,
            "category": "Elections",
            "subgroup": subgroup,
        },
    }


def _slug(text: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in text.casefold()).strip("_")


def _election_summary(contests: list[list[dict]]) -> dict[str, Counter]:
    seats, votes, margins, winners, sizes = Counter(), Counter(), Counter(), Counter(), Counter()
    nota = Counter()
    for rows in contests:
        winner = rows[0]
        seats[winner["party"]] += 1
        counted = [row for row in rows if row["votes"] is not None]
        total = sum(row["votes"] for row in counted)
        sizes[_band(len([row for row in rows if row["party"] != NOTA]), CANDIDATE_BANDS)] += 1
        for row in counted:
            votes["NOTA" if row["party"] == NOTA else row["party"]] += row["votes"]
            nota["NOTA" if row["party"] == NOTA else "Candidates"] += row["votes"]
        if total and len(counted) >= 2:
            margins[_band((counted[0]["votes"] - counted[1]["votes"]) / total * 100, MARGIN_BANDS)] += 1
            winners[_band(counted[0]["votes"] / total * 100, WINNER_BANDS)] += 1
    party_mix = Counter()
    for party, value in votes.items():
        party_mix["Independent candidates" if party == "Independent" else "NOTA" if party == "NOTA" else "Party candidates"] += value
    margin_points = []
    for rows in contests:
        counted = [row for row in rows if row["votes"] is not None]
        total = sum(row["votes"] for row in counted)
        if total and len(counted) >= 2:
            margin_points.append((counted[0]["votes"] - counted[1]["votes"]) / total * 100)
    candidates = [len([row for row in rows if row["party"] != NOTA]) for rows in contests]
    return {"seats": seats, "votes": votes, "margins": margins, "winners": winners, "sizes": sizes, "nota": nota,
            "mix": party_mix, "margin_points": margin_points, "candidates": candidates}


def _stats(summary: dict[str, Counter]) -> dict[str, float | None]:
    total = summary["nota"]["Candidates"] + summary["nota"]["NOTA"]
    margins, candidates = summary["margin_points"], summary["candidates"]
    seats = sum(summary["seats"].values())
    return {
        "nota": round(summary["nota"]["NOTA"] / total * 100, 2) if total else None,
        "independent": round(summary["mix"]["Independent candidates"] / total * 100, 2) if total else None,
        "close": round(sum(1 for value in margins if value < 5) / len(margins) * 100, 1) if margins else None,
        "margin": round(sorted(margins)[len(margins) // 2], 2) if margins else None,
        "candidates": round(sum(candidates) / len(candidates), 1) if candidates else None,
        "largest": round(summary["seats"].most_common(1)[0][1] / seats * 100, 1) if seats else None,
        "parties": len([party for party, count in summary["seats"].items() if count]),
    }


def build_indices(payload: dict) -> dict:
    observations = payload["observations"]
    source = f"https://github.com/{payload.get('source_repository', 'thecont1/india-votes-data')}/tree/{payload.get('source_commit', 'main')}"
    grouped = _contests(observations)
    series: dict[str, dict] = {}

    def add(item: tuple[str, dict]) -> None:
        series[item[0]] = item[1]

    calc = "Calculated from listed candidate vote totals in ECI-derived constituency results"
    ls = [rows for (year, kind, _, _), rows in grouped.items() if year == 2024 and kind == "Lok Sabha"]
    if len(ls) != 543:
        raise ValueError(f"Expected 543 Lok Sabha 2024 contests, found {len(ls)}")
    summary = _election_summary(ls)
    base = dict(frequency="General election 2024", source=source)
    add(_series("india_ls2024_party_seats", *_ranked(summary["seats"]), title="Lok Sabha 2024: Seats Won by Party",
                subtitle="Constituencies won by each party across all 543 seats", unit=" seats", subgroup=SUBGROUP_LS,
                note="Seat winner is the highest-vote candidate in each constituency; Surat's uncontested winner is included. The ten largest parties are shown individually.", **base))
    add(_series("india_ls2024_party_votes", *_ranked(summary["votes"]), title="Lok Sabha 2024: Votes by Party",
                subtitle="Listed candidate votes by party, including NOTA", unit=" votes", subgroup=SUBGROUP_LS, color="#58a6ff",
                note=f"{calc}. Surat has no reported votes. Independents are combined under one label.", **base))
    add(_series("india_ls2024_margin_bands", *_ordered(summary["margins"], MARGIN_BANDS), title="Lok Sabha 2024: Victory Margin Bands",
                subtitle="Seats by winner's lead over the runner-up, in percentage points", unit=" seats", subgroup=SUBGROUP_LS, color="#3fb950",
                note=f"{calc}. Surat (uncontested) is excluded.", **base))
    add(_series("india_ls2024_winner_share_bands", *_ordered(summary["winners"], WINNER_BANDS), title="Lok Sabha 2024: Winner Vote-Share Bands",
                subtitle="Seats by the winning candidate's share of listed votes", unit=" seats", subgroup=SUBGROUP_LS, color="#bc8cff",
                note=f"{calc}. Surat (uncontested) is excluded.", **base))
    add(_series("india_ls2024_candidate_field_bands", *_ordered(summary["sizes"], CANDIDATE_BANDS), title="Lok Sabha 2024: Candidates per Constituency",
                subtitle="Seats grouped by the number of contesting candidates (NOTA excluded)", unit=" seats", subgroup=SUBGROUP_LS, color="#f6c344",
                note="Counts candidates listed in each constituency result; NOTA is not a candidate.", **base))
    add(_series("india_ls2024_nota_share", ["Candidates", "NOTA"], [summary["nota"]["Candidates"], summary["nota"]["NOTA"]],
                title="Lok Sabha 2024: NOTA Share of Votes", subtitle="None of the Above compared with votes for all candidates", unit=" votes",
                subgroup=SUBGROUP_LS, color="#ff7b72", note=f"{calc}.", **base))
    state_seats = Counter(rows[0]["state_or_ut"] for rows in ls)
    add(_series("india_ls2024_seats_by_state", *_ranked(state_seats, 12), title="Lok Sabha 2024: Seats by State/UT",
                subtitle="Distribution of the 543 parliamentary constituencies", unit=" seats", subgroup=SUBGROUP_LS, color="#39c5bb",
                note="Constituency counts by State/UT in the 2024 general election results.", **base))
    party_mix = Counter()
    for party, value in summary["votes"].items():
        party_mix["Independent candidates" if party == "Independent" else "NOTA" if party == "NOTA" else "Party candidates"] += value
    add(_series("india_ls2024_independent_vote_share", *_ranked(party_mix), title="Lok Sabha 2024: Party vs Independent Votes",
                subtitle="Votes for party candidates, independents and NOTA", unit=" votes", subgroup=SUBGROUP_LS, color="#f778ba",
                note=f"{calc}.", **base))

    for state in sorted(state for state, count in state_seats.items() if count >= MIN_STATE_SEATS):
        state_summary = _election_summary([rows for rows in ls if rows[0]["state_or_ut"] == state])
        slug = _slug(state)
        add(_series(f"india_ls2024_{slug}_party_seats", *_ranked(state_summary["seats"], 8), title=f"Lok Sabha 2024 {state}: Seats by Party",
                    subtitle=f"{state_seats[state]} parliamentary constituencies", unit=" seats", subgroup=SUBGROUP_LS_STATES,
                    note="Seat winner is the highest-vote candidate in each constituency.", **base))
        add(_series(f"india_ls2024_{slug}_party_votes", *_ranked(state_summary["votes"], 8), title=f"Lok Sabha 2024 {state}: Votes by Party",
                    subtitle="Listed candidate votes by party, including NOTA", unit=" votes", subgroup=SUBGROUP_LS_STATES, color="#58a6ff",
                    note=f"{calc}.", **base))
        add(_series(f"india_ls2024_{slug}_margin_bands", *_ordered(state_summary["margins"], MARGIN_BANDS), title=f"Lok Sabha 2024 {state}: Victory Margins",
                    subtitle="Seats by winner's lead over the runner-up, in percentage points", unit=" seats", subgroup=SUBGROUP_LS_STATES, color="#3fb950",
                    note=f"{calc}.", **base))

    ls_stats = {state: _stats(_election_summary([rows for rows in ls if rows[0]["state_or_ut"] == state])) for state in state_seats}
    compare = dict(frequency="General election 2024", source=source, subgroup=SUBGROUP_COMPARE, chart="bar")
    for metric, key, title, subtitle, unit, color in (
        ("nota", "india_ls2024_state_nota_share", "Lok Sabha 2024: NOTA Share by State/UT", "NOTA votes as a share of all listed votes", "%", "#ff7b72"),
        ("close", "india_ls2024_state_close_contests", "Lok Sabha 2024: Close Contests by State/UT", "Share of seats decided by under 5 percentage points", "%", "#3fb950"),
        ("margin", "india_ls2024_state_median_margin", "Lok Sabha 2024: Median Victory Margin by State/UT", "Median winner lead over the runner-up", " pts", "#58a6ff"),
        ("candidates", "india_ls2024_state_candidates_per_seat", "Lok Sabha 2024: Candidates per Seat by State/UT", "Average contesting candidates per constituency (NOTA excluded)", " candidates", "#f6c344"),
        ("independent", "india_ls2024_state_independent_share", "Lok Sabha 2024: Independent Vote Share by State/UT", "Votes for independent candidates as a share of all listed votes", "%", "#f778ba"),
        ("largest", "india_ls2024_state_largest_party_seat_share", "Lok Sabha 2024: Largest Party's Seat Share by State/UT", "Share of a State/UT's seats won by its leading party", "%", "#bc8cff"),
    ):
        ranked = sorted(((state, values[metric]) for state, values in ls_stats.items() if values[metric] is not None), key=lambda item: item[1], reverse=True)
        add(_series(key, [state for state, _ in ranked], [value for _, value in ranked], title=title, subtitle=subtitle, unit=unit, color=color,
                    note=f"{calc}. All {len(ranked)} States/UTs with contested seats are shown.", **compare))

    assemblies: dict[tuple[int, str], list[list[dict]]] = defaultdict(list)
    for (year, kind, state, _), rows in grouped.items():
        if kind == "State Assembly":
            assemblies[(year, state)].append(rows)
    for (year, state), contests in sorted(assemblies.items()):
        assembly = _election_summary(contests)
        slug = f"{year}_{_slug(state)}"
        common = dict(frequency=f"Assembly election {year}", source=source, subgroup=SUBGROUP_ASSEMBLY)
        add(_series(f"india_assembly_{slug}_party_seats", *_ranked(assembly["seats"], 8), title=f"{state} Assembly {year}: Seats by Party",
                    subtitle=f"{len(contests)} Assembly constituencies", unit=" seats",
                    note="Seat winner is the highest-vote candidate (EVM plus postal votes) in each constituency.", **common))
        add(_series(f"india_assembly_{slug}_party_votes", *_ranked(assembly["votes"], 8), title=f"{state} Assembly {year}: Votes by Party",
                    subtitle="EVM plus postal votes by party, including NOTA", unit=" votes", color="#58a6ff", note=f"{calc}.", **common))
        add(_series(f"india_assembly_{slug}_margin_bands", *_ordered(assembly["margins"], MARGIN_BANDS), title=f"{state} Assembly {year}: Victory Margins",
                    subtitle="Seats by winner's lead over the runner-up, in percentage points", unit=" seats", color="#3fb950",
                    note=f"{calc}.", **common))
        add(_series(f"india_assembly_{slug}_winner_share_bands", *_ordered(assembly["winners"], WINNER_BANDS), title=f"{state} Assembly {year}: Winner Vote-Share Bands",
                    subtitle="Seats by the winning candidate's share of listed votes", unit=" seats", color="#bc8cff", note=f"{calc}.", **common))
        add(_series(f"india_assembly_{slug}_candidate_field_bands", *_ordered(assembly["sizes"], CANDIDATE_BANDS), title=f"{state} Assembly {year}: Candidates per Seat",
                    subtitle="Seats grouped by the number of contesting candidates (NOTA excluded)", unit=" seats", color="#f6c344",
                    note="Counts candidates listed in each constituency result; NOTA is not a candidate.", **common))
        add(_series(f"india_assembly_{slug}_vote_mix", *_ranked(assembly["mix"]), title=f"{state} Assembly {year}: Party, Independent & NOTA Votes",
                    subtitle="Votes for party candidates, independents and NOTA", unit=" votes", color="#f778ba", note=f"{calc}.", **common))

    latest: dict[str, tuple[int, dict]] = {}
    for (year, state), contests in assemblies.items():
        if state not in latest or year > latest[state][0]:
            latest[state] = (year, _election_summary(contests))
    assembly_compare = dict(frequency="Latest Assembly election, 2022?2026", source=source, subgroup=SUBGROUP_COMPARE)
    seats_total = Counter()
    for _, summary in latest.values():
        seats_total.update(summary["seats"])
    add(_series("india_assembly_latest_party_seats", *_ranked(seats_total, 12), title="Latest Assembly Elections: Seats by Party",
                subtitle=f"Seats won across the latest Assembly election in {len(latest)} States/UTs", unit=" seats", color="#ff9933",
                note="Sums seat winners from each State/UT's most recent Assembly election in the 2022?2026 ECI-derived results.", **assembly_compare))
    states_won = Counter(summary["seats"].most_common(1)[0][0] for _, summary in latest.values() if summary["seats"])
    add(_series("india_assembly_latest_largest_party_states", *_ranked(states_won, 10), title="Latest Assembly Elections: States Led by Party",
                subtitle="Number of States/UTs where each party won the most seats", unit=" States/UTs", color="#39c5bb",
                note="Largest single party by seats in each State/UT's most recent Assembly election.", **assembly_compare))
    assembly_stats = {f"{state} ({year})": _stats(summary) for state, (year, summary) in latest.items()}
    for metric, key, title, subtitle, unit, color in (
        ("nota", "india_assembly_state_nota_share", "Assembly Elections: NOTA Share by State/UT", "NOTA votes as a share of all listed votes, latest election", "%", "#ff7b72"),
        ("close", "india_assembly_state_close_contests", "Assembly Elections: Close Contests by State/UT", "Share of seats decided by under 5 percentage points, latest election", "%", "#3fb950"),
        ("margin", "india_assembly_state_median_margin", "Assembly Elections: Median Victory Margin by State/UT", "Median winner lead over the runner-up, latest election", " pts", "#58a6ff"),
        ("candidates", "india_assembly_state_candidates_per_seat", "Assembly Elections: Candidates per Seat by State/UT", "Average contesting candidates per constituency, latest election", " candidates", "#f6c344"),
        ("largest", "india_assembly_state_largest_party_seat_share", "Assembly Elections: Largest Party's Seat Share", "Share of Assembly seats won by the leading party, latest election", "%", "#bc8cff"),
        ("parties", "india_assembly_state_parties_winning", "Assembly Elections: Parties Winning Seats", "Number of distinct parties (independents as one) winning at least one seat", " parties", "#f778ba"),
    ):
        ranked = sorted(((state, values[metric]) for state, values in assembly_stats.items() if values[metric] is not None), key=lambda item: item[1], reverse=True)
        add(_series(key, [state for state, _ in ranked], [value for _, value in ranked], title=title, subtitle=subtitle, unit=unit, color=color,
                    note=f"{calc}. Each State/UT's most recent Assembly election is used (year in brackets).", **{**assembly_compare, "chart": "bar"}))

    return {
        "generated_at_utc": payload.get("generated_at_utc") or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "Derived from data/recent-indian-elections.json",
        "source_commit": payload.get("source_commit"),
        "collection_status": "ok",
        "series_count": len(series),
        "series": series,
    }


def main() -> None:
    result = build_indices(json.loads(SOURCE.read_text(encoding="utf-8")))
    text = json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n"
    for output in OUTPUTS:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(f"Built {result['series_count']} election indices")


if __name__ == "__main__":
    main()

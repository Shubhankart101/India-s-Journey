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
            subgroup: str, note: str, source: str, color: str = "#ff9933") -> tuple[str, dict]:
    return key, {
        "labels": labels,
        "values": values,
        "chartType": "doughnut",
        "scope": "category",
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
    return {"seats": seats, "votes": votes, "margins": margins, "winners": winners, "sizes": sizes, "nota": nota}


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

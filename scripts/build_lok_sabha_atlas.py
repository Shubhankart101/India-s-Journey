"""Builds the Lok Sabha elections atlas dataset (state-by-state winners, 1952-2024).

Sources
* 1951-2019: constituency-level results from ``data/raw/parliament_final.csv`` (CC0, normalised from ECI reports by
  https://github.com/gitcheckoutnikhil/india-elections-data). ``data/historical-elections.json`` only holds the
  2021-2023 assembly elections, so it cannot supply earlier Lok Sabha years.
* 2024: ``data/recent-indian-elections.json`` (ECI constituency-wise detailed result, statistical report 33).

Old states are mapped onto modern map geometry (see METHODOLOGY). Output: ``data/lok-sabha-atlas.json`` and
copies in ``frontend/public/data/`` and ``frontend/src/data/``.

    python scripts/build_lok_sabha_atlas.py
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "raw" / "parliament_final.csv"
RECENT_PATH = ROOT / "data" / "recent-indian-elections.json"
OUT_DIRS = [ROOT / "data", ROOT / "frontend" / "public" / "data", ROOT / "frontend" / "src" / "data"]
OUT_NAME = "lok-sabha-atlas.json"

# (code, display name, colour, family)
PARTIES = [
    ("INC", "Indian National Congress", "#1e88e5", "Congress"),
    ("BJP", "Bharatiya Janata Party", "#ff9933", "BJP"),
    ("BJS", "Bharatiya Jana Sangh", "#b8651b", "BJP"),
    ("BLD", "Bharatiya Lok Dal (Janata alliance, 1977)", "#6d9c2f", "Janata"),
    ("JNP", "Janata Party", "#9ccc65", "Janata"),
    ("JNP(S)", "Janata Party (Secular)", "#c5e1a5", "Janata"),
    ("JD", "Janata Dal", "#00897b", "Janata"),
    ("JD(U)", "Janata Dal (United)", "#26a69a", "Janata"),
    ("JD(S)", "Janata Dal (Secular)", "#4db6ac", "Janata"),
    ("CPI", "Communist Party of India", "#d32f2f", "Left"),
    ("CPM", "Communist Party of India (Marxist)", "#8e0000", "Left"),
    ("RSP", "Revolutionary Socialist Party", "#e57373", "Left"),
    ("FBL", "All India Forward Bloc", "#ef9a9a", "Left"),
    ("PSP", "Praja Socialist Party", "#ad1457", "Socialist"),
    ("SSP", "Samyukta Socialist Party", "#f06292", "Socialist"),
    ("SP", "Samajwadi Party", "#c2185b", "Regional"),
    ("RJD", "Rashtriya Janata Dal", "#00acc1", "Regional"),
    ("BSP", "Bahujan Samaj Party", "#3949ab", "Regional"),
    ("DMK", "Dravida Munnetra Kazhagam", "#455a64", "Regional"),
    ("AIADMK", "All India Anna Dravida Munnetra Kazhagam", "#388e3c", "Regional"),
    ("TDP", "Telugu Desam Party", "#fdd835", "Regional"),
    ("YSRCP", "YSR Congress Party", "#0288d1", "Regional"),
    ("TRS", "Telangana Rashtra Samithi / BRS", "#f48fb1", "Regional"),
    ("SHS", "Shiv Sena", "#bf360c", "Regional"),
    ("NCP", "Nationalist Congress Party", "#5e35b1", "Regional"),
    ("NCP(SP)", "Nationalist Congress Party (Sharadchandra Pawar)", "#9575cd", "Regional"),
    ("SHS(UBT)", "Shiv Sena (Uddhav Balasaheb Thackeray)", "#ff7043", "Regional"),
    ("AITC", "All India Trinamool Congress", "#66bb6a", "Regional"),
    ("BJD", "Biju Janata Dal", "#1b5e20", "Regional"),
    ("SAD", "Shiromani Akali Dal", "#ffa726", "Regional"),
    ("JKN", "Jammu & Kashmir National Conference", "#7b1fa2", "Regional"),
    ("JMM", "Jharkhand Mukti Morcha", "#689f38", "Regional"),
    ("AAP", "Aam Aadmi Party", "#00bcd4", "Regional"),
    ("AGP", "Asom Gana Parishad", "#827717", "Regional"),
    ("IUML", "Indian Union Muslim League", "#4db6ac", "Regional"),
    ("KEC", "Kerala Congress", "#9e9d24", "Regional"),
    ("PMK", "Pattali Makkal Katchi", "#ffb300", "Regional"),
    ("SWA", "Swatantra Party", "#8d6e63", "Historical"),
    ("INC(U)", "Indian National Congress (Urs)", "#64b5f6", "Congress"),
    ("IND", "Independents", "#a1887f", "Independent"),
    ("OTH", "Other parties", "#78909c", "Other"),
]
PARTY_INDEX = {code for code, *_ in PARTIES}
CODE_ALIASES = {
    "INC(I)": "INC", "CPI(M)": "CPM", "JP": "JNP", "ADK": "AIADMK", "ADMK": "AIADMK", "TD": "TDP", "MUL": "IUML",
    "TMC(M)": "AITC", "": "IND", "NONE": "IND",
}
NAME_TO_CODE = {
    "Bharatiya Janata Party": "BJP", "Indian National Congress": "INC", "Samajwadi Party": "SP",
    "All India Trinamool Congress": "AITC", "Dravida Munnetra Kazhagam": "DMK", "Telugu Desam": "TDP",
    "Janata Dal (United)": "JD(U)", "Shiv Sena (Uddhav Balasaheb Thackrey)": "SHS(UBT)", "Shiv Sena": "SHS",
    "Nationalist Congress Party - Sharadchandra Pawar": "NCP(SP)", "Nationalist Congress Party": "NCP",
    "Independent": "IND", "Rashtriya Janata Dal": "RJD", "Communist Party of India (Marxist)": "CPM",
    "Jharkhand Mukti Morcha": "JMM", "Indian Union Muslim League": "IUML", "Aam Aadmi Party": "AAP",
    "Communist Party of India": "CPI", "Jammu & Kashmir National Conference": "JKN", "Janata Dal (Secular)": "JD(S)",
    "Asom Gana Parishad": "AGP", "Shiromani Akali Dal": "SAD", "Kerala Congress": "KEC",
    "Yuvajana Sramika Rythu Congress Party": "YSRCP", "Bahujan Samaj Party": "BSP",
    "Biju Janata Dal": "BJD", "Revolutionary Socialist Party": "RSP",
}

MODERN = {
    "Andaman & Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chandigarh", "Chhattisgarh",
    "Dadra & Nagar Haveli and Daman & Diu", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jammu & Kashmir", "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh", "Maharashtra",
    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
}
MODERN_BY_UPPER = {name.upper(): name for name in MODERN}
STATE_ALIASES = {
    "NCT OF DELHI": "Delhi", "JAMMU AND KASHMIR": "Jammu & Kashmir", "DADRA & NAGAR HAVELI": "Dadra & Nagar Haveli and Daman & Diu",
    "DAMAN & DIU": "Dadra & Nagar Haveli and Daman & Diu", "ODISHA": "Odisha", "ORISSA": "Odisha",
}
# Historical state -> (default modern state, other modern states its constituencies may belong to).
HISTORICAL = {
    "BOMBAY": ("Maharashtra", ["Gujarat", "Karnataka"]),
    "MADRAS": ("Tamil Nadu", ["Andhra Pradesh", "Kerala", "Karnataka"]),
    "MYSORE": ("Karnataka", []),
    "HYDERABAD": ("Telangana", ["Maharashtra", "Karnataka"]),
    "MADHYA BHARAT": ("Madhya Pradesh", ["Rajasthan"]),
    "VINDHYA PRADESH": ("Madhya Pradesh", []),
    "BHOPAL": ("Madhya Pradesh", []),
    "PATIALA AND EAST PUNJAB STATES UNION": ("Punjab", ["Haryana", "Himachal Pradesh"]),
    "TRAVANCORE COCHIN": ("Kerala", ["Tamil Nadu"]),
    "SAURASHTRA": ("Gujarat", []),
    "KUTCH": ("Gujarat", []),
    "AJMER": ("Rajasthan", []),
    "BILASPUR": ("Himachal Pradesh", []),
    "COORG": ("Karnataka", []),
    "GOA, DAMAN & DIU": ("Goa", ["Dadra & Nagar Haveli and Daman & Diu"]),
}
# Modern states that were carved out of a parent: constituencies are re-assigned by name when they appear later.
SPLITS = {
    "Punjab": ["Haryana", "Himachal Pradesh", "Chandigarh"], "Andhra Pradesh": ["Telangana"],
    "Bihar": ["Jharkhand"], "Madhya Pradesh": ["Chhattisgarh"], "Uttar Pradesh": ["Uttarakhand"],
    "Assam": ["Meghalaya", "Mizoram", "Nagaland", "Arunachal Pradesh"], "Jammu & Kashmir": ["Ladakh"],
}
# raw dataset year -> election year (late polls in Assam/Punjab belong to the same general election)
ELECTION_OF = {1951: 1952, 1985: 1984, 1992: 1991}
LABELS = {1952: "1951–52"}
YEAR_NOTES = {
    1952: "First general election (Oct 1951 – Feb 1952). Many constituencies elected two members; only the top vote-getter of each constituency is counted here.",
    1957: "Many constituencies still elected two members; only the top vote-getter of each constituency is counted here.",
    1984: "Held Dec 1984; Assam and Punjab polled in 1985 and are included.",
    1991: "Held May–Jun 1991; Punjab polled in Feb 1992 and is included.",
}
METHODOLOGY = [
    "Each State/UT is shaded by the party that won the most Lok Sabha constituencies there in that general election (party, not alliance; ties go to the party with more votes).",
    "Constituency winner = candidate with the most votes. Margin = winner's votes minus the runner-up's. Vote share = party's candidate votes divided by all candidate votes counted in the dataset for that State/UT.",
    "Turnout = votes cast divided by electors, summed over constituencies where both figures are present; it is not available for 2024 and is withheld where the source repeats votes cast as electors (2014 and 2019).",
    "Boundaries are today's State/UT outlines. Historical states are mapped onto them: Bombay → Maharashtra + Gujarat (+ Karnataka), Madras → Tamil Nadu (+ Andhra/Kerala/Karnataka), Mysore → Karnataka, Travancore-Cochin → Kerala, Hyderabad → Telangana (+ Maharashtra/Karnataka), Madhya Bharat, Vindhya Pradesh and Bhopal → Madhya Pradesh, PEPSU → Punjab, Saurashtra and Kutch → Gujarat. Constituencies are re-assigned to the modern state by matching their name against 2004–2024 constituencies (e.g. Rohtak → Haryana, Hyderabad city → Telangana, Ranchi → Jharkhand); unmatched ones go to the default state.",
    "1951–52 and 1957 elected two members in many constituencies and 1962+ elected one; only the leading candidate is counted, so seat totals for 1952 and 1957 are below the 489 and 494 seats actually filled.",
    "Dataset gaps: a few constituencies per year are missing in the source CSV (see 'seats_counted' per year); Assam 1980 and J&K 1991 were not polled. Results before 1996 were extracted from scanned ECI reports and may contain isolated errors.",
    "1951–52 is shown as 1952; late polls in Assam/Punjab (1985, 1992) are merged into 1984 and 1991.",
]


def norm_state(name: str) -> str:
    text = " ".join(str(name or "").replace("&amp;", "&").split())
    return STATE_ALIASES.get(text.upper()) or MODERN_BY_UPPER.get(text.upper(), text)


def pc_key(name: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", re.sub(r"\(.*?\)", "", str(name or "").upper()))


def party_code(raw: str) -> str:
    code = NAME_TO_CODE.get(raw) or CODE_ALIASES.get(raw.strip().upper(), raw.strip())
    return code if code in PARTY_INDEX else "OTH"


def to_int(value) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def load_rows() -> list[dict]:
    rows = []
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        for rec in csv.DictReader(handle):
            year = int(rec["YEAR"])
            rows.append({
                "raw_year": year, "year": ELECTION_OF.get(year, year), "state_raw": rec["STATE"].strip(), "pc": rec["PC"].strip(),
                "name": rec["NAME"].strip(), "party_raw": rec["PARTY"].strip(), "votes": to_int(rec["VOTES"]),
                "cast": to_int(rec["VOTES_CAST"]), "electors": to_int(rec["ELECTORS"]),
            })
    recent = json.loads(RECENT_PATH.read_text(encoding="utf-8"))
    for obs in recent["observations"]:
        if obs.get("election_type") != "Lok Sabha":
            continue
        rows.append({
            "raw_year": 2024, "year": 2024, "state_raw": obs["state_or_ut"], "pc": obs["constituency"].strip(),
            "name": obs["candidate"].strip(), "party_raw": obs["party"].strip(), "votes": to_int(obs.get("votes")),
            "cast": None, "electors": None, "full_party": True,
        })
    return rows


def build() -> dict:
    rows = load_rows()
    # name -> modern state, from recent general elections (2004+), used to re-assign constituencies of old/parent states
    modern_index: dict[str, str] = {}
    for row in sorted(rows, key=lambda item: item["year"]):
        state = norm_state(row["state_raw"])
        if row["year"] >= 2004 and state in MODERN:
            modern_index[pc_key(row["pc"])] = state  # latest election wins

    def modern_state(row: dict) -> str:
        raw = norm_state(row["state_raw"])
        upper = raw.upper()
        if upper in HISTORICAL:
            default, others = HISTORICAL[upper]
            allowed = {default, *others}
        elif raw in MODERN:
            default, allowed = raw, {raw, *SPLITS.get(raw, [])}
            if row["year"] >= 2019 or (row["year"] >= 2004 and raw != "Andhra Pradesh"):
                return raw
        else:
            raise ValueError(f"Unmapped state {raw!r}")
        hit = modern_index.get(pc_key(row["pc"]))
        return hit if hit in allowed else default

    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        row["state"] = modern_state(row)
        row["party"] = party_code(row["party_raw"])
        grouped[(row["year"], row["state_raw"], row["pc"])].append(row)

    seats: dict[tuple, dict] = {}
    for (year, _, pc), cands in grouped.items():
        ranked = sorted(cands, key=lambda item: item["votes"] if item["votes"] is not None else -1, reverse=True)
        top = ranked[0]
        runner = ranked[1]["votes"] if len(ranked) > 1 else None
        margin = top["votes"] - runner if top["votes"] is not None and runner is not None else None
        seats[(year, top["state"], pc, top["state_raw"])] = {"top": top, "margin": margin, "cands": cands}

    states: dict[str, dict] = defaultdict(dict)
    national: dict[int, Counter] = defaultdict(Counter)
    for (year, state, pc, _), seat in sorted(seats.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
        entry = states[state].setdefault(str(year), {"seats": Counter(), "list": [], "votes": Counter(), "cast": 0, "electors": 0, "total_votes": 0, "old": set()})
        top = seat["top"]
        entry["seats"][top["party"]] += 1
        national[year][top["party"]] += 1
        entry["list"].append([pc.title() if pc.isupper() else pc, top["name"].title() if top["name"].isupper() else top["name"], top["party"], seat["margin"]])
        for cand in seat["cands"]:
            if cand["votes"] is not None:
                entry["votes"][cand["party"]] += cand["votes"]
                entry["total_votes"] += cand["votes"]
        if top["cast"] and top["electors"] and top["cast"] < top["electors"]:  # 2014+ rows repeat votes as electors
            entry["cast"] += top["cast"]
            entry["electors"] += top["electors"]
        if top["state_raw"].upper() != state.upper():
            entry["old"].add(top["state_raw"].title())

    out_states = {}
    for state in sorted(states):
        out_states[state] = {}
        for year, entry in sorted(states[state].items()):
            total = sum(entry["seats"].values())
            lead = max(entry["seats"], key=lambda code: (entry["seats"][code], entry["votes"][code]))
            shares = {code: round(votes / entry["total_votes"] * 100, 1) for code, votes in entry["votes"].most_common(6)} if entry["total_votes"] else {}
            out_states[state][year] = {
                "total": total, "lead": lead, "seats": dict(entry["seats"].most_common()),
                "turnout": round(entry["cast"] / entry["electors"] * 100, 1) if entry["electors"] else None,
                "vote_share": shares, "from": sorted(entry["old"]) or None,
                "list": sorted(entry["list"], key=lambda item: item[0]),
            }
    years = []
    for year in sorted(national):
        counted = sum(national[year].values())
        years.append({
            "year": year, "label": LABELS.get(year, str(year)), "seats_counted": counted,
            "national": dict(national[year].most_common()), "note": YEAR_NOTES.get(year, ""),
        })
    used = {code for item in years for code in item["national"]} | {e["lead"] for s in out_states.values() for e in s.values()}
    parties = {code: {"name": name, "colour": colour, "family": family} for code, name, colour, family in PARTIES if code in used}
    return {
        "meta": {
            "title": "Lok Sabha elections by state, 1952–2024",
            "sources": [
                {"name": "ECI-derived constituency results 1951–2019 (CC0)", "url": "https://github.com/gitcheckoutnikhil/india-elections-data"},
                {"name": "ECI GE 2024 Constituency Wise Detailed Result", "url": "https://www.eci.gov.in/eci-backend/public/all_files/GE-2024-statistical-report/33-Constituency-Wise-Detailed-Result.xls"},
                {"name": "State/UT outlines: DataMeet", "url": "https://github.com/datameet/maps"},
            ],
            "years_available": [item["year"] for item in years],
            "missing_years": [],
            "methodology": METHODOLOGY,
            "unlisted_party_note": "Parties outside the legend are grouped as 'Other parties' on the map.",
        },
        "years": years,
        "parties": parties,
        "states": out_states,
    }


def main() -> None:
    data = build()
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    for folder in OUT_DIRS:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / OUT_NAME).write_text(text, encoding="utf-8")
    print(f"Wrote {OUT_NAME}: {len(data['years'])} elections, {len(data['states'])} States/UTs, {len(text) // 1024} KB")


if __name__ == "__main__":
    main()

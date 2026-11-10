"""Builds per-State Vidhan Sabha (Assembly) election histories for the Lok Sabha atlas "state view".

Sources (constituency winners are aggregated; only winners, margins and party tallies are stored)
* TCPD Lok Dhaba assembly elections (AE), mostly 1962-2023: ``data/raw/tcpd_ae_all_states.csv.gz``
  (https://github.com/tcpd/tcpd-ld-data-archive, Trivedi Centre for Political Data, Ashoka University; free for
  non-commercial use with citation, no endorsement, no warranty).
* ECI statistical reports "10 - Detailed Results" (primary source) for the elections TCPD does not yet cover:
  Andhra Pradesh, Arunachal Pradesh, Odisha and Sikkim 2024 and Chhattisgarh, Madhya Pradesh, Mizoram, Rajasthan and
  Telangana 2023 (``data/raw/eci/*.xlsx``).
* 2024-2026 assembly elections already normalised in ``data/recent-indian-elections.json`` (India Votes Data, MIT,
  built from ECI results) for Haryana, Jharkhand, J&K, Maharashtra (2024), Bihar, Delhi (2025), Assam, Kerala,
  Puducherry, Tamil Nadu and West Bengal (2026).

Output: ``frontend/public/data/state-elections/index.json`` plus one ``<slug>.json`` per State/UT with an assembly, copied to
``frontend/public/data/state-elections/``.

    python scripts/build_state_elections.py

Requires openpyxl; install the builder dependency with ``python -m pip install -r scripts/requirements-build.txt``.
"""
from __future__ import annotations

import colorsys
import csv
import gzip
import json
import re
import shutil
import sys
import zlib
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_lok_sabha_atlas as lok  # noqa: E402

TCPD_PATH = ROOT / "data" / "raw" / "tcpd_ae_all_states.csv.gz"
ECI_DIR = ROOT / "data" / "raw" / "eci"
RECENT_PATH = ROOT / "data" / "recent-indian-elections.json"
OUT_DIRS = [ROOT / "frontend" / "public" / "data" / "state-elections"]

SOURCES = {
    "TCPD": {
        "name": "TCPD Lok Dhaba, Trivedi Centre for Political Data, Ashoka University: Assembly Elections (AE) dataset, constituency-level results",
        "url": "https://github.com/tcpd/tcpd-ld-data-archive/tree/main/downloads/All_States",
        "licence": "Free to use for non-commercial purposes with citation; no endorsement or warranty implied (TCPD terms of use). Derived from ECI statistical reports.",
    },
    "ECI": {
        "name": "Election Commission of India, Statistical Reports: 10 - Detailed Results",
        "url": "https://www.eci.gov.in/statistical-reports",
        "licence": "Official public ECI statistical report (government publication).",
    },
    "IVD": {
        "name": "India Votes Data (ECI results, normalised)",
        "url": "https://github.com/thecont1/india-votes-data",
        "licence": "MIT",
    },
}
# state (modern name) -> (ECI statistical report file, election year)
ECI_FILES = {
    "OR-2024": ("Odisha", 2024), "AP-2024": ("Andhra Pradesh", 2024), "AR-2024": ("Arunachal Pradesh", 2024),
    "SK-2024": ("Sikkim", 2024), "chhattisgarh-2023": ("Chhattisgarh", 2023), "mizoram-2023": ("Mizoram", 2023),
    "mp-2023": ("Madhya Pradesh", 2023), "rajasthan-2023": ("Rajasthan", 2023), "telangana-2023": ("Telangana", 2023),
}
TCPD_STATE_MAP = {"Madras": "Tamil Nadu", "Mysore": "Karnataka", "Goa Daman & Diu": "Goa"}
SEATS_NOW = {
    "Andhra Pradesh": 175, "Arunachal Pradesh": 60, "Assam": 126, "Bihar": 243, "Chhattisgarh": 90, "Delhi": 70, "Goa": 40,
    "Gujarat": 182, "Haryana": 90, "Himachal Pradesh": 68, "Jammu & Kashmir": 90, "Jharkhand": 81, "Karnataka": 224,
    "Kerala": 140, "Madhya Pradesh": 230, "Maharashtra": 288, "Manipur": 60, "Meghalaya": 60, "Mizoram": 40,
    "Nagaland": 60, "Odisha": 147, "Puducherry": 30, "Punjab": 117, "Rajasthan": 200, "Sikkim": 32, "Tamil Nadu": 234,
    "Telangana": 119, "Tripura": 60, "Uttar Pradesh": 403, "Uttarakhand": 70, "West Bengal": 294,
}
STATE_NOTES = {
    "Andhra Pradesh": "Elections up to 2009 cover undivided Andhra Pradesh including the present Telangana region; Telangana has its own history from 2014.",
    "Bihar": "Elections up to 2000 include the seats of present-day Jharkhand. Two elections were held in 2005 (February and October-November).",
    "Madhya Pradesh": "Elections up to 1998 include the seats of present-day Chhattisgarh.",
    "Uttar Pradesh": "Elections up to 1993 include the hill seats of present-day Uttarakhand (up to 1996 in the source).",
    "Tamil Nadu": "1962 and 1967 are the Madras State elections; the state was renamed Tamil Nadu in 1969.",
    "Karnataka": "1962-1972 are the Mysore State elections; the state was renamed Karnataka in 1973.",
    "Goa": "1967-1984 are the Goa, Daman & Diu Union Territory elections; Goa became a state in 1987.",
    "Punjab": "1962 includes the seats of present-day Haryana (separated in 1966).",
    "Delhi": "No assembly existed between 1956 and 1993 (the 1972-1983 entries are Metropolitan Council elections in the source).",
    "Jammu & Kashmir": "No assembly election was held between 2014 and 2024; the 2024 poll was the first after the 2019 reorganisation.",
    "Himachal Pradesh": "Earlier Territorial Council elections (before 1967) are not in the source.",
    "Puducherry": "Earlier Pondicherry Representative Assembly polls (before 1964) are not in the source.",
}
NO_ASSEMBLY = {
    "Andaman & Nicobar Islands": "Union Territory without a legislative assembly.",
    "Chandigarh": "Union Territory without a legislative assembly.",
    "Dadra & Nagar Haveli and Daman & Diu": "Union Territory without a legislative assembly.",
    "Ladakh": "Union Territory without a legislative assembly.",
    "Lakshadweep": "Union Territory without a legislative assembly.",
}
METHODOLOGY = [
    "Each election is one general election to the Vidhan Sabha of that State/UT; by-elections are excluded. The 'lead' party is the party with most seats (no alliance or coalition data in the open sources); a majority is half the seats plus one.",
    "Seat-by-seat rows come from the constituency winner (position 1) with a margin over the runner-up; vote share is the party's share of all candidate votes (NOTA excluded) in the contested seats.",
    "Turnout is valid votes divided by electors, summed over constituencies where both are published; it is blank for 2024-2026 elections taken from the India Votes Data export, which has no electors.",
    "Coverage: assembly elections from 1962 (1961 for Odisha) to 2026 in the TCPD, ECI and India Votes Data sources. The first assembly elections of 1951-1961 are not in any open constituency-level dataset used here and are left out, so some states' history begins later than the first Lok Sabha election.",
    "Not available: chief minister and alliance/coalition (government) data. No open, structured, redistributable source with every state's chief ministers was found; the lead party is shown instead.",
    "Boundaries: assembly constituencies are shown as a seat strip and list, not a map, because open assembly boundary files cover only recent delimitations. Constituency names are as published at the time of the election.",
    "Party colours match the Lok Sabha atlas; parties outside the atlas palette get a stable generated colour. Party codes follow the source (TCPD/ECI abbreviations); some historic codes are not expanded.",
    "TCPD data may differ slightly from ECI originals; the 1962-1990s results were digitised from scanned ECI reports and may contain isolated errors.",
]

EXTRA_NAMES = {
    "LKD": "Lok Dal", "BKD": "Bharatiya Kranti Dal", "SDF": "Sikkim Democratic Front", "SKM": "Sikkim Krantikari Morcha",
    "NPF": "Naga People's Front", "MNF": "Mizo National Front", "ZPM": "Zoram People's Movement", "INLD": "Indian National Lok Dal",
    "JJP": "Jannayak Janta Party", "NPP": "National People's Party", "AIMIM": "All India Majlis-E-Ittehadul Muslimeen",
    "PWP": "Peasants and Workers Party of India", "ICS": "Indian Congress (Socialist)", "AHL": "All India Hill Leaders Union",
    "NCO": "Indian National Congress (Organisation)", "RLD": "Rashtriya Lok Dal", "LJP": "Lok Janshakti Party",
    "NDPP": "Nationalist Democratic Progressive Party", "TIPRA": "Tipra Motha Party", "JKPDP": "Jammu & Kashmir Peoples Democratic Party",
    "NTK": "Naam Tamilar Katchi", "TVK": "Tamilaga Vettri Kazhagam", "JSP": "Jan Suraaj Party", "AIFB": "All India Forward Bloc",
    "BRS": "Bharat Rashtra Samithi", "UDP": "United Democratic Party", "MGP": "Maharashtrawadi Gomantak Party",
    "MNS": "Maharashtra Navnirman Sena", "VBA": "Vanchit Bahujan Aaghadi", "JKPC": "Jammu & Kashmir People's Conference",
    "PDP": "Jammu & Kashmir Peoples Democratic Party", "HVP": "Haryana Vikas Party", "AIUDF": "All India United Democratic Front",
    "DMDK": "Desiya Murpokku Dravida Kazhagam", "AINRC": "All India N.R. Congress", "RPI": "Republican Party of India",
    "KEC(M)": "Kerala Congress (M)", "GP": "Ganatantra Parishad", "JAC": "Jana Congress (Odisha)", "SAP": "Samata Party",
    "JNP(SC)": "Janata Party (Secular - Charan Singh)",     "CPI(ML)(L)": "CPI (Marxist-Leninist) Liberation",
}
CODE_FIX = {
    "KC": "KEC",
    "BHRS": "TRS", "BRS": "TRS", "AAAP": "AAP", "INC(I)": "INC", "ADK": "AIADMK", "ADMK": "AIADMK", "MUL": "IUML", "JP": "JNP",
    "CPI(M)": "CPM", "TD": "TDP", "AIFB": "FBL", "MAG": "MGP", "TIPRA": "TIPRA", "MNM": "MNS",
}
FULL_NAME_CODES = {
    "ALL INDIA MAJLIS-E-ITTEHADUL MUSLIMEEN": "AIMIM", "NAAM TAMILAR KATCHI": "NTK", "TAMILAGA VETTRI KAZHAGAM": "TVK",
    "JAN SURAAJ PARTY": "JSP", "RASHTRIYA LOK DAL": "RLD", "INDIAN NATIONAL LOK DAL": "INLD", "JANNAYAK JANTA PARTY": "JJP",
    "NATIONAL PEOPLE'S PARTY": "NPP", "NATIONALIST CONGRESS PARTY - SHARADCHANDRA PAWAR": "NCP(SP)",
    "COMMUNIST PARTY OF INDIA (MARXIST-LENINIST) (LIBERATION)": "CPI(ML)L", "LOK JANSHAKTI PARTY(RAM VILAS)": "LJP(RV)",
    "JAMMU & KASHMIR PEOPLES DEMOCRATIC PARTY": "JKPDP", "MAHARASHTRA NAVNIRMAN SENA": "MNS", "VANCHIT BAHUJAN AAGHADI": "VBA",
    "ALL INDIA MAJLIS-E-ITTEHADUL MUSLIMEEN ": "AIMIM", "TIPRA MOTHA PARTY": "TIPRA", "NAGA PEOPLES FRONT": "NPF",
    "NATIONALIST DEMOCRATIC PROGRESSIVE PARTY": "NDPP", "MIZO NATIONAL FRONT": "MNF", "ZORAM PEOPLE'S MOVEMENT": "ZPM",
    "ALL INDIA FORWARD BLOC": "FBL", "UNITED DEMOCRATIC PARTY": "UDP", "REVOLUTIONARY SOCIALIST PARTY": "RSP",
    "SHIV SENA (UDDHAV BALASAHEB THACKERAY)": "SHS(UBT)", "ASOM GANA PARISHAD": "AGP", "JAMMU & KASHMIR NATIONAL CONFERENCE": "JKN",
    "BHARAT RASHTRA SAMITHI": "TRS", "JHARKHAND MUKTI MORCHA": "JMM", "BIJU JANATA DAL": "BJD", "YUVAJANA SRAMIKA RYTHU CONGRESS PARTY": "YSRCP",
    "JANATA DAL (SECULAR)": "JD(S)", "JANATA DAL (UNITED)": "JD(U)",
}
NOT_PARTY = {"NOTA", "NONE OF THE ABOVE"}

PALETTE = {code: (name, colour) for code, name, colour, _ in lok.PARTIES}
UPPER_NAME_TO_CODE = {name.upper(): code for name, code in lok.NAME_TO_CODE.items()}


def clean(text) -> str:
    return " ".join(str(text or "").replace("–", "-").replace("’", "'").split())


def acronym(name: str) -> str:
    words = [w for w in re.split(r"[\s\-/]+", re.sub(r"\(.*?\)", "", name)) if w and w[0].isalpha() and w.lower() not in {"of", "the", "and", "&"}]
    return "".join(w[0].upper() for w in words)[:8] or name[:6]


def party_code(raw: str) -> str:
    text = clean(raw)
    upper = text.upper()
    if upper in FULL_NAME_CODES:
        return FULL_NAME_CODES[upper]
    if upper in UPPER_NAME_TO_CODE:
        return UPPER_NAME_TO_CODE[upper]
    if upper in {"INDEPENDENT", "IND"}:
        return "IND"
    if " " in text and len(text) > 8:  # full party name without a known code
        return acronym(text)
    code = CODE_FIX.get(upper) or lok.CODE_ALIASES.get(upper, text)
    return CODE_FIX.get(code, code) or "IND"


def generated_colour(code: str) -> str:
    hue = (zlib.crc32(code.encode()) % 360) / 360
    r, g, b = colorsys.hls_to_rgb(hue, 0.42, 0.55)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


def to_int(value):
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


def title(text: str) -> str:
    text = clean(text)
    return text.title() if text.isupper() else text


def tidy_name(text: str) -> str:
    text = re.sub(r"^\d+\s+", "", clean(text))
    return title(text)


class Election:
    def __init__(self, state: str, year: int, source: str, month: int | None = None):
        self.state, self.year, self.source, self.month = state, year, source, month
        self.constituencies: dict = {}

    def add(self, key, name: str, candidate: str, party: str, votes, electors=None, valid=None):
        entry = self.constituencies.setdefault(key, {"name": name, "cands": [], "electors": electors, "valid": valid})
        if electors and not entry["electors"]:
            entry["electors"] = electors
        entry["cands"].append((candidate, party, votes))

    def summarise(self) -> tuple[dict, list]:
        seats: Counter = Counter()
        votes: Counter = Counter()
        rows = []
        valid_sum = electors_sum = 0
        for key, entry in sorted(self.constituencies.items(), key=lambda item: (str(item[0]).zfill(4))):
            cands = sorted(entry["cands"], key=lambda c: -(c[2] if c[2] is not None else -1))
            if not cands:
                continue
            top = cands[0]
            runner = cands[1][2] if len(cands) > 1 else None
            margin = top[2] - runner if top[2] is not None and runner is not None else None
            seats[top[1]] += 1
            rows.append([entry["name"], top[0], top[1], margin])
            for _, party, count in cands:
                if count:
                    votes[party] += count
            valid = entry["valid"] if entry["valid"] else sum(c[2] or 0 for c in cands)
            if valid and entry["electors"] and valid < entry["electors"]:
                valid_sum += valid
                electors_sum += entry["electors"]
        total_votes = sum(votes.values())
        parties_only = {code: n for code, n in seats.items() if code not in {"IND", "OTH"}} or seats
        lead = max(parties_only, key=lambda code: (seats[code], votes[code]))
        record = {
            "total": len(rows), "lead": lead, "seats": dict(seats.most_common()),
            "turnout": round(valid_sum / electors_sum * 100, 1) if electors_sum else None,
            "vote_share": {code: round(count / total_votes * 100, 1) for code, count in votes.most_common(8)} if total_votes else {},
            "source": self.source,
        }
        return record, rows


def load_tcpd() -> list[Election]:
    groups: dict = {}
    with gzip.open(TCPD_PATH, "rt", encoding="utf-8", newline="") as handle:
        for rec in csv.DictReader(handle):
            if rec["Poll_No"] != "0" or not rec["Assembly_No"] or not rec["Year"]:
                continue
            raw_state = rec["State_Name"].replace("_", " ")
            state = TCPD_STATE_MAP.get(raw_state) or lok.norm_state(raw_state)
            key = (rec["State_Name"], rec["Assembly_No"])
            group = groups.setdefault(key, {"state": state, "years": Counter(), "months": Counter(), "rows": []})
            year, month = to_int(rec["Year"]), to_int(rec["month"])
            group["years"][year] += 1
            group["months"][(year, month)] += 1
            group["rows"].append(rec)
    elections = []
    for group in groups.values():
        year = group["years"].most_common(1)[0][0]
        month = max((m for (y, m), n in group["months"].items() if y == year), key=lambda m: group["months"][(year, m)])
        election = Election(group["state"], year, "TCPD", month)
        for rec in group["rows"]:
            party = party_code(rec["Party"])
            if party.upper() in NOT_PARTY:
                continue
            votes = to_int(rec["Votes"])
            key = (rec["Constituency_No"], rec["Constituency_Name"])
            election.add(key, title(rec["Constituency_Name"]), title(rec["Candidate"]), party, votes,
                         to_int(rec["Electors"]), to_int(rec["Valid_Votes"]))
        elections.append(election)
    return elections


def load_eci() -> list[Election]:
    elections = []
    for stem, (state, year) in ECI_FILES.items():
        sheet = openpyxl.load_workbook(ECI_DIR / f"{stem}.xlsx", read_only=True, data_only=True).worksheets[0]
        election = Election(state, year, "ECI")
        for row in sheet.iter_rows(min_row=5, values_only=True):
            if not row[0] or not isinstance(row[1], int) or row[0] == "TURN OUT":
                continue
            party = party_code(row[7])
            if party.upper() in NOT_PARTY:
                continue
            election.add(row[1], re.sub(r"\s*\((SC|ST|BL|GEN)\)$", "", title(row[2])), tidy_name(row[3]), party, to_int(row[11]), to_int(row[14] if len(row) > 14 else row[13]))
        elections.append(election)
    return elections


def load_recent() -> list[Election]:
    data = json.loads(RECENT_PATH.read_text(encoding="utf-8"))
    groups: dict = {}
    for obs in data["observations"]:
        if obs.get("election_type") != "State Assembly":
            continue
        state = lok.norm_state(obs["state_or_ut"])
        election = groups.setdefault((state, obs["year"]), Election(state, obs["year"], "IVD"))
        party = party_code(obs["party"])
        if party.upper() in NOT_PARTY:
            continue
        election.add(obs["constituency_number"], title(obs["constituency"]), title(obs["candidate"]), party, to_int(obs.get("votes")))
    return list(groups.values())


def build() -> tuple[dict, dict]:
    by_state: dict[str, dict] = defaultdict(dict)
    for loader in (load_tcpd, load_eci, load_recent):  # earlier loaders win when two sources overlap
        for election in loader():
            existing = by_state[election.state]
            if any(e.year == election.year and (e.month is None or election.month is None or e.month == election.month) for e in existing.values()):
                continue
            existing[(election.year, election.month, election.source)] = election

    files, index_states = {}, {}
    for state in sorted(by_state):
        elections = sorted(by_state[state].values(), key=lambda e: (e.year, e.month or 0))
        year_counts = Counter(e.year for e in elections)
        years, lists, used = [], {}, set()
        for election in elections:
            record, rows = election.summarise()
            if not rows:
                continue
            eid = str(election.year) if year_counts[election.year] == 1 else f"{election.year}-{election.month or 0:02d}"
            label = str(election.year) if year_counts[election.year] == 1 else f"{election.year} ({date(2000, election.month or 1, 1):%b})"
            record = {"id": eid, "year": election.year, "label": label, **record}
            years.append(record)
            lists[eid] = sorted(rows, key=lambda row: row[0])
            used.update(record["seats"])
            used.update(record["vote_share"])
        parties = {}
        for code in sorted(used):
            if code in PALETTE:
                parties[code] = {"name": PALETTE[code][0], "colour": PALETTE[code][1]}
            else:
                parties[code] = {"name": EXTRA_NAMES.get(code, code), "colour": generated_colour(code)}
        slug = re.sub(r"[^a-z0-9]+", "-", state.lower()).strip("-")
        sources = [{"key": key, **SOURCES[key]} for key in SOURCES if key in {y["source"] for y in years}]
        files[slug] = {
            "state": state, "slug": slug, "house": "AE", "house_name": f"{state} Vidhan Sabha (Legislative Assembly)",
            "seats_now": SEATS_NOW.get(state), "note": STATE_NOTES.get(state, ""), "sources": sources,
            "source": " · ".join(s["name"] for s in sources), "source_url": sources[0]["url"],
            "parties": parties, "years": years, "elections": {eid: {"list": rows} for eid, rows in lists.items()},
        }
        latest = years[-1]
        latest_party = parties[latest["lead"]]
        index_states[state] = {
            "slug": slug, "first": years[0]["year"], "last": latest["year"], "elections": len(years),
            "seats_now": SEATS_NOW.get(state), "lead_latest": latest["lead"],
            "lead_latest_name": latest_party["name"], "lead_latest_colour": latest_party["colour"],
            "latest_label": latest["label"], "latest_seats": latest["seats"][latest["lead"]],
            "latest_total": latest["total"], "latest_vote_share": latest["vote_share"].get(latest["lead"]),
            "latest_headline": f"{latest_party['name']} led with {latest['seats'][latest['lead']]} of {latest['total']} seats in {latest['label']}",
        }
    index = {
        "meta": {
            "title": "Vidhan Sabha (Assembly) election history by State/UT",
            "generated": date.today().isoformat(),
            "sources": [{"key": key, **value} for key, value in SOURCES.items()],
            "methodology": METHODOLOGY,
            "citation": "Lok Dhaba, Trivedi Centre for Political Data, Ashoka University (https://lokdhaba.ashoka.edu.in/); Election Commission of India statistical reports; India Votes Data.",
        },
        "states": index_states,
        "no_assembly": NO_ASSEMBLY,
    }
    return index, files


def write(index: dict, files: dict) -> None:
    payloads = {"index.json": index, **{f"{slug}.json": data for slug, data in files.items()}}
    for out in OUT_DIRS:
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        for name, payload in payloads.items():
            (out / name).write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> None:
    index, files = build()
    write(index, files)
    total = sum(len(f["years"]) for f in files.values())
    print(f"{len(files)} states/UTs, {total} assembly elections")


if __name__ == "__main__":
    main()

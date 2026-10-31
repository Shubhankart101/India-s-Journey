from __future__ import annotations

import csv
import io
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "recent-indian-elections.json"
REPOSITORY = "thecont1/india-votes-data"
API_BASE = f"https://api.github.com/repos/{REPOSITORY}"
RAW_BASE = f"https://raw.githubusercontent.com/{REPOSITORY}"
USER_AGENT = "IndiaJourney public election data collector"
PARLIAMENTARY_FILE = "archive/2024 Parliamentary Elections India.csv"
ASSEMBLY_FILE_PATTERN = re.compile(r"data/csv/20(?:22|23|24|25|26)Assembly-[A-Z]{2}\.csv")


def fetch_bytes(url: str, accept: str = "*/*") -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    with urlopen(request, timeout=60) as response:
        return response.read()


def source_snapshot() -> tuple[str, str, list[str]]:
    commit = json.loads(fetch_bytes(f"{API_BASE}/commits/main", "application/vnd.github+json"))
    commit_sha = commit["sha"]
    tree_sha = commit["commit"]["tree"]["sha"]
    tree = json.loads(fetch_bytes(
        f"{API_BASE}/git/trees/{tree_sha}?recursive=1",
        "application/vnd.github+json",
    ))
    files = sorted(
        path for path in (item.get("path", "") for item in tree.get("tree", []))
        if ASSEMBLY_FILE_PATTERN.fullmatch(path)
    )
    if not files:
        raise ValueError("The election data repository contains no supported recent Assembly CSV files")
    if PARLIAMENTARY_FILE not in {item.get("path") for item in tree.get("tree", [])}:
        raise ValueError("The election data repository is missing the 2024 Lok Sabha results CSV")
    return commit_sha, commit["commit"]["committer"]["date"], [PARLIAMENTARY_FILE, *files]


def _read_csv_rows(content: bytes, source_url: str) -> list[dict[str, str]]:
    text = content.decode("utf-8-sig")
    if not text.strip():
        raise ValueError(f"Election CSV is empty: {source_url}")
    header = text.splitlines()[0]
    delimiter = ";" if header.count(";") > header.count(",") else ","
    rows = list(csv.DictReader(io.StringIO(text), delimiter=delimiter))
    if not rows:
        raise ValueError(f"Election CSV has no candidate rows: {source_url}")
    return [
        {str(key).strip().lstrip("\ufeff"): (value or "").strip() for key, value in row.items() if key}
        for row in rows
    ]


def _integer(value: str, field: str, source_url: str) -> int:
    try:
        result = int(value.replace(",", "").strip())
    except (ValueError, AttributeError) as error:
        raise ValueError(f"Invalid {field} value in {source_url}: {value!r}") from error
    if result < 0:
        raise ValueError(f"Negative {field} value in {source_url}: {value!r}")
    return result


def parse_recent_csv(
    content: bytes,
    relative_path: str,
    commit_sha: str,
    state_names: dict[str, str],
) -> list[dict]:
    source_url = f"{RAW_BASE}/{commit_sha}/{quote(relative_path, safe='/')}"
    rows = _read_csv_rows(content, source_url)
    parliamentary = relative_path == PARLIAMENTARY_FILE
    required = (
        {"State", "Constituency", "Party", "Candidate", "Votes"}
        if parliamentary
        else {"election_year", "election_state", "constituency", "constituency_no",
              "candidate", "party", "evm_votes", "postal_votes"}
    )
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Election CSV is missing columns {sorted(missing)}: {source_url}")

    seats: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        candidate = row.get("Candidate" if parliamentary else "candidate", "").strip()
        constituency = row.get("Constituency" if parliamentary else "constituency", "").strip()
        if not candidate or not constituency or candidate.casefold() == "total":
            continue
        if parliamentary:
            year = 2024
            election_type = "Lok Sabha"
            state = row["State"].strip()
            # The source "Constituency ID" repeats across seats, so it is not an ECI PC number.
            number = ""
            raw_votes = row.get("Votes", "").strip()
            uncontested = raw_votes.casefold().startswith("uncontest")
            votes = None if uncontested else _integer(raw_votes, "votes", source_url)
        else:
            year = _integer(row["election_year"], "election year", source_url)
            if year not in range(2022, 2027):
                raise ValueError(f"Unexpected Assembly election year {year}: {source_url}")
            election_type = "State Assembly"
            state_code = row["election_state"].strip().upper()
            state = state_names.get(state_code, "")
            if not state:
                raise ValueError(f"Unknown ECI state code {state_code!r}: {source_url}")
            number = row["constituency_no"].strip()
            votes = (
                _integer(row["evm_votes"], "EVM votes", source_url)
                + _integer(row["postal_votes"], "postal votes", source_url)
            )
        seat_id = constituency.casefold() if parliamentary else number or constituency.casefold()
        seat_key = (str(year), election_type, state.casefold(), seat_id)
        seats[seat_key].append({
            "year": year,
            "election_type": election_type,
            "state_or_ut": state,
            "constituency_number": number,
            "constituency": constituency,
            "candidate": candidate,
            "party": row.get("Party" if parliamentary else "party", "").strip(),
            "votes": votes,
            "result_status": "uncontested" if parliamentary and uncontested else "reported",
            "electors": None,
            "source": source_url,
            "vote_share_method": None,
        })
    if not seats:
        raise ValueError(f"Election CSV contains no usable constituency results: {source_url}")
    observations = []
    for candidates in seats.values():
        total_votes = sum(candidate["votes"] or 0 for candidate in candidates)
        for candidate in candidates:
            candidate["vote_share_percent"] = (
                round(candidate["votes"] / total_votes * 100, 4)
                if candidate["votes"] is not None and total_votes > 0
                else None
            )
            if candidate["votes"] is not None and total_votes > 0:
                candidate["vote_share_method"] = "calculated_from_listed_candidate_votes"
            observations.append(candidate)
    return observations


def parse_state_names(content: bytes, commit_sha: str) -> dict[str, str]:
    source_url = f"{RAW_BASE}/{commit_sha}/data/states.csv"
    rows = _read_csv_rows(content, source_url)
    if not {"state_code", "state_name"} <= set(rows[0]):
        raise ValueError(f"State lookup is missing required columns: {source_url}")
    return {
        row["state_code"].strip().upper(): row["state_name"].strip()
        for row in rows
        if row.get("state_code") and row.get("state_name")
    }


def collect_recent_results() -> dict:
    commit_sha, commit_date, paths = source_snapshot()
    states_url = f"{RAW_BASE}/{commit_sha}/data/states.csv"
    state_names = parse_state_names(fetch_bytes(states_url), commit_sha)
    observations: list[dict] = []
    source_index = {}
    for index, path in enumerate(paths):
        source_url = f"{RAW_BASE}/{commit_sha}/{quote(path, safe='/')}"
        source_index[source_url] = index
        observations.extend(parse_recent_csv(fetch_bytes(source_url), path, commit_sha, state_names))

    unique: dict[tuple, dict] = {}
    for row in observations:
        key = (
            row["year"],
            row["election_type"],
            row["state_or_ut"].casefold(),
            row["constituency"].casefold()
            if row["election_type"] == "Lok Sabha"
            else row["constituency_number"] or row["constituency"].casefold(),
            row["candidate"].casefold(),
        )
        unique[key] = row
    observations = list(unique.values())

    parliamentary_seats = {
        (row["state_or_ut"].casefold(), row["constituency"].casefold())
        for row in observations
        if row["year"] == 2024 and row["election_type"] == "Lok Sabha"
    }
    if len(parliamentary_seats) != 543:
        raise ValueError(
            f"Expected results for all 543 2024 Lok Sabha constituencies; found {len(parliamentary_seats)}"
        )
    for row in observations:
        row["source_file"] = source_index[row.pop("source")]
        row.pop("electors", None)
        if row.get("vote_share_method") == "calculated_from_listed_candidate_votes":
            row.pop("vote_share_method")
        if row.get("result_status") == "reported":
            row.pop("result_status")
    observations.sort(key=lambda row: (
        row["year"], row["election_type"], row["state_or_ut"], row["constituency_number"],
        -(row["votes"] or 0), row["candidate"].casefold(),
    ))
    return {
        "source": "ECI results normalized by the India Votes Data project; candidate records are linked to the exact source CSV",
        "source_repository": f"https://github.com/{REPOSITORY}",
        "source_commit": commit_sha,
        "source_commit_date": commit_date,
        "refresh_frequency": "Daily",
        "collection_status": "ok",
        "vote_share_method": "Calculated from the listed candidate vote totals for that constituency; uncontested candidates without a reported vote count have no calculated share.",
        "source_files": [
            {
                "path": path,
                "url": f"{RAW_BASE}/{commit_sha}/{quote(path, safe='/')}",
            }
            for path in paths
        ],
        "observation_count": len(observations),
        "lok_sabha_2024_constituency_count": len(parliamentary_seats),
        "assembly_election_years": sorted({
            row["year"] for row in observations if row["election_type"] == "State Assembly"
        }),
        "observations": observations,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def main() -> int:
    try:
        payload = collect_recent_results()
    except (HTTPError, URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"Unable to refresh recent Indian election results: {error}", file=sys.stderr)
        return 1
    try:
        previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except FileNotFoundError:
        previous = {}
    except json.JSONDecodeError as error:
        print(f"Unable to read existing recent election snapshot at {OUTPUT}: {error}", file=sys.stderr)
        return 1
    if previous.get("source_commit") == payload["source_commit"]:
        payload["generated_at_utc"] = previous.get("generated_at_utc", payload["generated_at_utc"])
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(serialized, encoding="utf-8")
    (ROOT / "docs" / "data" / OUTPUT.name).write_text(serialized, encoding="utf-8")
    print(json.dumps({
        "collection_status": payload["collection_status"],
        "source_files": len(payload["source_files"]),
        "candidate_observations": payload["observation_count"],
        "2024_lok_sabha_constituencies": payload["lok_sabha_2024_constituency_count"],
        "assembly_years": payload["assembly_election_years"],
        "source_commit": payload["source_commit"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

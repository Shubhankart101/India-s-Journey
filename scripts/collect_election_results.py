from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "election-results.json"
USER_AGENT = "IndiaJourney public election data collector"
ECI_LANDING = "https://results.eci.gov.in/"
US_ARCHIVES_URL = "https://www.archives.gov/electoral-college/{year}"
PRESIDENTIAL_YEARS = range(2000, 2025, 4)


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.rows: list[list[str]] = []
        self.text: list[str] = []
        self._link_href: str | None = None
        self._link_text: list[str] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._refresh: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "a":
            self._link_href = attributes.get("href")
            self._link_text = []
        elif tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
        elif tag == "meta" and (attributes.get("http-equiv") or "").lower() == "refresh":
            match = re.search(r"url\s*=\s*['\"]?([^'\";]+)", attributes.get("content", ""), re.I)
            if match:
                self._refresh = match.group(1).strip()

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self._link_href is not None:
            self._link_text.append(data)
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._link_href is not None:
            label = " ".join("".join(self._link_text).split())
            self.links.append((label, self._link_href))
            self._link_href = None
            self._link_text = []
        elif tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None


def parse_page(html: str) -> _PageParser:
    parser = _PageParser()
    parser.feed(html)
    return parser


def eci_index_urls() -> list[str]:
    landing = parse_page(fetch_text(ECI_LANDING))
    redirect = landing._refresh
    if not redirect:
        raise ValueError("ECI landing page did not provide a results redirect")
    index_url = urljoin(ECI_LANDING, redirect)
    root = parse_page(fetch_text(index_url))
    urls = [index_url]
    for label, href in root.links:
        if "pc bye" in label.lower() and href.lower().endswith("index.htm"):
            urls.append(urljoin(index_url, href))
    return list(dict.fromkeys(urls))


def parse_constituency_results(html: str, source_url: str, election_type: str) -> dict:
    page = parse_page(html)
    header = next(
        (
            row for row in page.rows
            if "candidate" in [cell.lower() for cell in row]
            and "total votes" in [cell.lower() for cell in row]
        ),
        None,
    )
    if header is None:
        raise ValueError(f"Candidate results table was not found at {source_url}")
    columns = [cell.lower() for cell in header]
    candidate_index = columns.index("candidate")
    party_index = columns.index("party") if "party" in columns else None
    votes_index = columns.index("total votes")
    percent_index = columns.index("% of votes") if "% of votes" in columns else None
    contest = " ".join(page.text)
    match = re.search(
        r"(?:Assembly|Parliament(?:ary)?)\s+Constituency\s+(\d+)\s*-\s*(.*?)\s*\(([^()]*)\)",
        contest,
        re.I,
    )
    constituency = match.group(2).strip() if match else urlparse(source_url).path.rsplit("/", 1)[-1]
    state = match.group(3).strip() if match else ""
    candidates = []
    for row in page.rows:
        if len(row) <= votes_index or row == header:
            continue
        try:
            votes = int(row[votes_index].replace(",", "").strip())
        except ValueError:
            continue
        percent = None
        if percent_index is not None and len(row) > percent_index:
            try:
                percent = float(row[percent_index].replace(",", "").strip())
            except ValueError:
                pass
        candidates.append({
            "candidate": row[candidate_index],
            "party": row[party_index] if party_index is not None and len(row) > party_index else "",
            "votes": votes,
            "vote_share_percent": percent,
        })
    if not candidates:
        raise ValueError(f"No candidate vote rows were found at {source_url}")
    candidates.sort(key=lambda item: item["votes"], reverse=True)
    return {
        "election_type": election_type,
        "constituency": constituency,
        "state_or_ut": state,
        "source": source_url,
        "candidates": candidates,
    }


def collect_eci_results() -> list[dict]:
    constituencies: list[dict] = []
    seen: set[str] = set()
    for index_url in eci_index_urls():
        index_page = parse_page(fetch_text(index_url))
        election_type = "Lok Sabha by-election" if "resultpc" in index_url.lower() else "State Assembly by-election"
        for _, href in index_page.links:
            match = re.search(r"candidateswise-([^/?#]+)\.htm", href, re.I)
            if not match:
                continue
            candidate_url = urljoin(index_url, href)
            result_url = urljoin(candidate_url, f"Constituencywise{match.group(1)}.htm")
            if result_url in seen:
                continue
            seen.add(result_url)
            result = parse_constituency_results(fetch_text(result_url), result_url, election_type)
            constituencies.append(result)
    if not constituencies:
        raise ValueError("No constituency-level candidate results were found on the current ECI portal")
    return constituencies


def collect_us_presidential_results() -> list[dict]:
    results = []
    for year in PRESIDENTIAL_YEARS:
        url = US_ARCHIVES_URL.format(year=year)
        page = parse_page(fetch_text(url))
        rows = page.rows
        president = next((row[1] for row in rows if row and row[0].strip().lower() == "president" and len(row) > 1), "")
        opponent = next((row[1] for row in rows if row and row[0].strip().lower() == "main opponent" and len(row) > 1), "")
        electoral_vote = next((row for row in rows if row and row[0].strip().lower().startswith("electoral vote")), None)
        vote_text = " ".join(electoral_vote or [])
        counts = re.search(r"Winner:\s*(\d+).*?Main Opponent:\s*(\d+)", vote_text, re.I)
        if not president or not opponent or not counts:
            raise ValueError(f"Electoral College totals were not found for {year}: {url}")
        results.append({
            "year": year,
            "winner": president,
            "winner_electoral_votes": int(counts.group(1)),
            "main_opponent": opponent,
            "opponent_electoral_votes": int(counts.group(2)),
            "source": url,
        })
    return results


def _series_from_results(constituencies: list[dict], presidential: list[dict]) -> dict:
    candidates = [
        (record, candidate)
        for record in constituencies
        for candidate in record["candidates"]
    ]
    candidates.sort(key=lambda item: item[1]["votes"], reverse=True)
    top_candidates = candidates[:30]
    candidates_by_share = sorted(
        ((record, candidate) for record, candidate in candidates if candidate["vote_share_percent"] is not None),
        key=lambda item: item[1]["vote_share_percent"],
        reverse=True,
    )[:30]
    contests = [
        (record, sorted(record["candidates"], key=lambda candidate: candidate["votes"], reverse=True))
        for record in constituencies
        if len(record["candidates"]) > 1
    ]
    contests.sort(key=lambda item: item[1][0]["votes"] - item[1][1]["votes"], reverse=True)
    winner_labels = [
        f"{record['state_or_ut']} · {record['constituency']}" for record, candidates_in_contest in contests
    ]
    party_wins: dict[str, int] = {}
    for record in constituencies:
        if record["candidates"]:
            party = record["candidates"][0]["party"] or "Unspecified"
            party_wins[party] = party_wins.get(party, 0) + 1
    ranked_parties = sorted(party_wins.items(), key=lambda item: (-item[1], item[0]))
    return {
        "india_live_candidate_votes": {
            "labels": [
                f"{record['state_or_ut']} · {record['constituency']} · {candidate['candidate']}"
                for record, candidate in top_candidates
            ],
            "values": [candidate["votes"] for _, candidate in top_candidates],
            "chartType": "bar",
            "indexAxis": "y",
            "source": "Election Commission of India live results portal",
            "note": "Top 30 candidates by reported vote total across the currently published Lok Sabha and Assembly by-election constituencies. The ECI portal labels displayed results provisional until Form 20 is published. Full candidate tables are retained in election-results.json.",
        },
        "india_live_candidate_vote_share": {
            "labels": [
                f"{record['state_or_ut']} · {record['constituency']} · {candidate['candidate']}"
                for record, candidate in candidates_by_share
            ],
            "values": [candidate["vote_share_percent"] for _, candidate in candidates_by_share],
            "chartType": "bar",
            "indexAxis": "y",
            "source": "Election Commission of India live results portal",
            "unit": "% of votes",
            "note": "Top 30 candidates by reported vote share across currently published constituencies. ECI displays provisional results until Form 20.",
        },
        "india_live_constituency_margin": {
            "labels": winner_labels,
            "values": [
                candidates_in_contest[0]["votes"] - candidates_in_contest[1]["votes"]
                for _, candidates_in_contest in contests
            ],
            "chartType": "bar",
            "indexAxis": "y",
            "source": "Calculated from Election Commission of India live constituency candidate totals",
            "unit": "votes",
            "note": "Reported-vote lead between the top two candidates in each currently published constituency. The ECI portal labels displayed results provisional until Form 20.",
        },
        "india_live_winner_vote_share": {
            "labels": winner_labels,
            "values": [candidates_in_contest[0]["vote_share_percent"] for _, candidates_in_contest in contests],
            "chartType": "bar",
            "indexAxis": "y",
            "source": "Election Commission of India live results portal",
            "unit": "% of votes",
            "note": "Reported vote share of the leading candidate in each currently published constituency. ECI displays provisional results until Form 20.",
        },
        "india_live_party_seats": {
            "labels": [party for party, _ in ranked_parties],
            "values": [seats for _, seats in ranked_parties],
            "chartType": "bar",
            "indexAxis": "y",
            "source": "Election Commission of India live constituency results",
            "unit": "constituencies",
            "note": "Count of currently published constituencies in which each party's candidate has the highest reported vote total. This is a provisional snapshot, not an all-election seat tally.",
        },
        "us_presidential_electoral_votes": {
            "labels": [str(result["year"]) for result in presidential],
            "datasets": [
                {
                    "label": "Electoral votes — winner",
                    "values": [result["winner_electoral_votes"] for result in presidential],
                    "color": "#58a6ff",
                },
                {
                    "label": "Electoral votes — main opponent",
                    "values": [result["opponent_electoral_votes"] for result in presidential],
                    "color": "#ff7b72",
                },
            ],
            "source": "U.S. National Archives, Electoral College results",
            "note": "Official Electoral College totals for the winner and main opponent in each presidential election from 2000 through 2024. These are electoral votes, not popular votes.",
        },
    }


def main() -> int:
    previous: dict = {}
    if OUTPUT.is_file():
        try:
            previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"Warning: ignoring invalid cache at {OUTPUT}", file=sys.stderr)
    errors: list[str] = []
    try:
        constituencies = collect_eci_results()
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        errors.append(f"ECI: {error}")
        constituencies = previous.get("india_constituencies", [])
    try:
        presidential = collect_us_presidential_results()
    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        errors.append(f"U.S. National Archives: {error}")
        presidential = previous.get("us_presidential_elections", [])
    if not constituencies and not presidential:
        print("; ".join(errors) or "No election sources returned records", file=sys.stderr)
        return 1
    data = {
        "refresh_frequency": "Every 3 hours",
        "collection_status": "partial" if errors else "ok",
        "collection_errors": errors,
        "india_constituencies": constituencies,
        "us_presidential_elections": presidential,
        "series": _series_from_results(constituencies, presidential),
    }
    for source_prefix, series_keys in (
        ("ECI:", (
            "india_live_candidate_votes",
            "india_live_candidate_vote_share",
            "india_live_constituency_margin",
            "india_live_winner_vote_share",
            "india_live_party_seats",
        )),
        ("U.S. National Archives:", ("us_presidential_electoral_votes",)),
    ):
        error = next((item for item in errors if item.startswith(source_prefix)), None)
        if error:
            for key in series_keys:
                data["series"][key]["note"] += f" Latest collection failed; showing cached data. {error}"
    data_changed = any(
        data[key] != previous.get(key)
        for key in (
            "collection_status",
            "collection_errors",
            "india_constituencies",
            "us_presidential_elections",
            "series",
        )
    )
    data["generated_at_utc"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        if data_changed or not previous.get("generated_at_utc")
        else previous["generated_at_utc"]
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.write_text(serialized, encoding="utf-8")
    (ROOT / "docs" / "data" / OUTPUT.name).write_text(serialized, encoding="utf-8")
    print(json.dumps({
        "collection_status": data["collection_status"],
        "constituencies": len(constituencies),
        "US presidential elections": len(presidential),
        "collection_errors": errors,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

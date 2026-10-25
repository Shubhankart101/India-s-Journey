from __future__ import annotations

import json
import posixpath
import re
import sys
import time
import zipfile
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "historical-elections.json"
CATALOG_URL = "https://old.eci.gov.in/statistical-report/statistical-reports/"
USER_AGENT = "IndiaJourney public historical election data collector"
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _request_text(opener, url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(request, timeout=45) as response:
        return response.read().decode("utf-8", errors="replace")


def _request_bytes(opener, url: str, referer: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Referer": referer})
    with opener.open(request, timeout=60) as response:
        data = response.read()
        if not response.headers.get("Content-Type", "").startswith(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ) and not data.startswith(b"PK"):
            raise ValueError(f"Expected public XLSX download from {url}")
        return data


class _CatalogParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._anchor: tuple[str, list[str]] | None = None
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._anchor = (dict(attrs).get("href") or "", [])

    def handle_data(self, data: str) -> None:
        if self._anchor is not None:
            self._anchor[1].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._anchor is not None:
            href, text = self._anchor
            self.links.append((" ".join("".join(text).split()), href))
            self._anchor = None


class _DownloadPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self._title_parts: list[str] = []
        self._current_title = ""
        self._anchor: tuple[str, list[str], str] | None = None
        self.downloads: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "h4":
            self._in_title = True
            self._title_parts = []
        elif tag == "a":
            self._anchor = (attributes.get("href") or "", [], self._current_title)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        if self._anchor is not None:
            self._anchor[1].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h4":
            self._current_title = " ".join("".join(self._title_parts).split())
            self._in_title = False
        elif tag == "a" and self._anchor is not None:
            href, _, title = self._anchor
            if "confirm=1" in href and title:
                self.downloads.append((title, href))
            self._anchor = None


def _catalog_entries(opener) -> list[tuple[int, str, str]]:
    parser = _CatalogParser()
    parser.feed(_request_text(opener, CATALOG_URL))
    found = {}
    for title, href in parser.links:
        match = re.search(r"/files/file/(\d+)-([^/?#]+)/?", href, re.I)
        if not match:
            continue
        slug = match.group(2)
        searchable = f"{title} {slug}".lower()
        if not any(term in searchable for term in (
            "election", "lok-sabha", "assembly", "legislative", "state-wise",
        )):
            continue
        file_id = int(match.group(1))
        found[file_id] = (file_id, title or slug, urljoin(CATALOG_URL, href))
    return sorted(found.values())


def _column_index(reference: str) -> int:
    match = re.match(r"([A-Z]+)", reference)
    if not match:
        return 0
    index = 0
    for character in match.group(1):
        index = index * 26 + ord(character) - ord("A") + 1
    return index - 1


def read_xlsx_rows(content: bytes) -> list[list[str]]:
    try:
        archive = zipfile.ZipFile(BytesIO(content))
    except zipfile.BadZipFile as error:
        raise ValueError("ECI workbook is not a valid XLSX archive") from error
    with archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            shared_strings = [
                "".join(node.text or "" for node in item.findall(f".//{{{MAIN_NS}}}t"))
                for item in strings.findall(f"{{{MAIN_NS}}}si")
            ]
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            relation.attrib["Id"]: relation.attrib["Target"]
            for relation in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
        }
        sheets = workbook.findall(f".//{{{MAIN_NS}}}sheet")
        if not sheets:
            raise ValueError("ECI workbook contains no worksheets")
        first_nonempty_rows: list[list[str]] = []
        for sheet_info in sheets:
            target = targets[sheet_info.attrib[f"{{{REL_NS}}}id"]]
            sheet_path = (
                target.lstrip("/")
                if target.startswith("/")
                else posixpath.normpath(posixpath.join("xl", target))
            )
            sheet = ElementTree.fromstring(archive.read(sheet_path))
            rows: list[list[str]] = []
            for row in sheet.findall(f".//{{{MAIN_NS}}}sheetData/{{{MAIN_NS}}}row"):
                cells: dict[int, str] = {}
                for cell in row.findall(f"{{{MAIN_NS}}}c"):
                    value = cell.find(f"{{{MAIN_NS}}}v")
                    inline = cell.find(f"{{{MAIN_NS}}}is")
                    text = value.text if value is not None and value.text else ""
                    if cell.attrib.get("t") == "s" and text:
                        text = shared_strings[int(text)]
                    elif cell.attrib.get("t") == "inlineStr" and inline is not None:
                        text = "".join(
                            node.text or "" for node in inline.findall(f".//{{{MAIN_NS}}}t")
                        )
                    cells[_column_index(cell.attrib.get("r", ""))] = text
                if cells:
                    rows.append([cells.get(index, "") for index in range(max(cells) + 1)])
            if rows and not first_nonempty_rows:
                first_nonempty_rows = rows
            if rows and _find_result_header(rows) is not None:
                return rows
        return first_nonempty_rows


def _find_result_header(rows: list[list[str]]) -> tuple[int, dict[str, int]] | None:
    for row_index, row in enumerate(rows):
        normalized = [re.sub(r"[^a-z0-9]+", " ", cell.lower()).strip() for cell in row]
        candidate = next((i for i, cell in enumerate(normalized) if "candidate" in cell), None)
        total_votes = next(
            (
                i for i, cell in enumerate(normalized)
                if cell in ("total", "total votes", "votes polled") or "total votes" in cell
            ),
            None,
        )
        if candidate is None or total_votes is None:
            continue
        aliases = {
            "state": ("state ut name", "state ut", "state name", "state"),
            "constituency_number": ("ac no", "pc no", "constituency no", "ac number", "pc number"),
            "constituency": ("ac name", "pc name", "constituency"),
            "candidate": ("candidate name", "candidate"),
            "party": ("party", "party name"),
            "votes": ("total", "total votes", "votes polled"),
            "vote_share": (
                "% votes polled",
                "of votes polled",
                "votes polled",
                "vote share",
                "votes percent",
                "percent votes",
            ),
            "electors": ("total electors", "electors"),
        }
        columns = {}
        for field, terms in aliases.items():
            index = next((i for i, cell in enumerate(normalized) if cell in terms), None)
            if index is None and field == "votes":
                index = total_votes
            if index is not None:
                columns[field] = index
        columns["candidate"] = candidate
        columns["votes"] = total_votes
        if "constituency" in columns:
            return row_index, columns
    return None


def parse_historical_workbook(
    content: bytes,
    report_title: str,
    report_url: str,
    year_label: str,
) -> list[dict]:
    rows = read_xlsx_rows(content)
    header = _find_result_header(rows)
    if header is None:
        raise ValueError(f"No candidate-vote result table in {report_url}")
    header_index, columns = header
    title_context = f"{report_title} {urlparse(report_url).path}".lower().replace("-", " ").replace("_", " ")
    is_lok_sabha = any(term in title_context for term in ("lok sabha", "parliament")) or (
        "general election" in title_context
        and not any(term in title_context for term in ("assembly", "legislative"))
    )
    election_type = "Lok Sabha" if is_lok_sabha else "State Assembly"
    year_match = re.search(r"\b(19|20)\d{2}\b", f"{year_label} {report_title} {report_url}")
    year = int(year_match.group(0)) if year_match else None
    if year is None:
        raise ValueError(f"Election year could not be identified for {report_url}")
    results = []
    for row in rows[header_index + 1:]:
        if len(row) <= columns["votes"] or len(row) <= columns["candidate"]:
            continue
        candidate = row[columns["candidate"]].strip()
        if not candidate:
            continue
        try:
            votes = int(float(row[columns["votes"]].replace(",", "").strip()))
        except ValueError:
            continue
        def value(field: str) -> str:
            column = columns.get(field)
            return row[column].strip() if column is not None and column < len(row) else ""

        try:
            vote_share = float(value("vote_share").replace("%", "").replace(",", "")) if value("vote_share") else None
        except ValueError:
            vote_share = None
        try:
            electors = int(float(value("electors").replace(",", ""))) if value("electors") else None
        except ValueError:
            electors = None
        results.append({
            "year": year,
            "election_type": election_type,
            "state_or_ut": value("state"),
            "constituency_number": value("constituency_number"),
            "constituency": value("constituency"),
            "candidate": candidate,
            "party": value("party"),
            "votes": votes,
            "vote_share_percent": vote_share,
            "electors": electors,
            "source": report_url,
        })
    if not results:
        raise ValueError(f"No candidate vote observations parsed from {report_url}")
    return results


def _detailed_result_download(opener, report_url: str) -> tuple[str, str] | None:
    listing_url = urljoin(report_url, "?do=download")
    listing = _DownloadPageParser()
    listing.feed(_request_text(opener, listing_url))
    candidates = [
        (title, urljoin(listing_url, href))
        for title, href in listing.downloads
        if "detailed result" in title.lower() and title.lower().endswith(".xlsx")
    ]
    return candidates[0] if candidates else None


def collect_historical_results() -> tuple[list[dict], int, int, int, list[str]]:
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    catalog = _catalog_entries(opener)
    observations: list[dict] = []
    covered_reports = 0
    reports_without_download = 0
    errors: list[str] = []
    for index, (_, title, report_url) in enumerate(catalog, start=1):
        try:
            detail = _detailed_result_download(opener, report_url)
            if detail is None:
                reports_without_download += 1
                continue
            _, download_url = detail
            content = _request_bytes(opener, download_url, urljoin(report_url, "?do=download"))
            report_rows = parse_historical_workbook(content, title, report_url, title)
            observations.extend(report_rows)
            covered_reports += 1
            if index % 25 == 0:
                print(f"Processed {index}/{len(catalog)} official ECI archive entries; {len(observations)} candidate results")
            time.sleep(0.15)
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as error:
            errors.append(f"{report_url}: {error}")
            if len(errors) <= 20:
                print(f"Could not parse official ECI archive {report_url}: {error}", file=sys.stderr)
    unique: dict[tuple, dict] = {}
    for row in observations:
        key = (
            row["year"],
            row["election_type"],
            row["state_or_ut"].casefold(),
            row["constituency_number"],
            row["candidate"].casefold(),
        )
        unique[key] = row
    return list(unique.values()), covered_reports, reports_without_download, len(catalog), errors


def main() -> int:
    try:
        observations, covered_reports, reports_without_download, catalog_entries, errors = collect_historical_results()
    except (HTTPError, URLError, TimeoutError) as error:
        print(f"Unable to load official ECI historical election archive: {error}", file=sys.stderr)
        return 1
    if not observations:
        print("Official ECI catalog yielded no parseable detailed candidate-result workbooks.", file=sys.stderr)
        return 1
    payload = {
        "source_catalog": CATALOG_URL,
        "source": "Election Commission of India statistical reports and detailed-result XLSX downloads",
        "collection_status": "partial" if errors or reports_without_download else "ok",
        "catalog_entries_scanned": catalog_entries,
        "reports_with_candidate_results": covered_reports,
        "reports_without_supported_download": reports_without_download,
        "collection_errors": errors[:20],
        "observation_count": len(observations),
        "observations": observations,
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(serialized, encoding="utf-8")
    (ROOT / "docs" / "data" / OUTPUT.name).write_text(serialized, encoding="utf-8")
    print(json.dumps({
        "collection_status": payload["collection_status"],
        "catalog_entries_scanned": catalog_entries,
        "reports_with_candidate_results": covered_reports,
        "reports_without_supported_download": reports_without_download,
        "candidate_observations": len(observations),
        "errors": len(errors),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Fetch normalized public dashboard data from the three official NJDG portals."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = ROOT / "data" / "legal" / "njdg_snapshot.json"
HISTORY_PATH = ROOT / "data" / "legal" / "njdg_history.json"
PORTALS = {
    "supreme_court": "https://scdg.sci.gov.in/scnjdg/",
    "high_courts": "https://njdg.ecourts.gov.in/hcnjdg_v2/",
    "lower_courts": "https://njdg.ecourts.gov.in/njdg_v3/",
}
FLAGS = ("ins", "disp", "citizen", "women", "delay", "insCurr", "dispCurr")
CASE_TYPES = {"1": "Total", "2": "Civil", "3": "Criminal"}
DASHBOARD_YEARS = range(2018, datetime.now(timezone.utc).year + 1)
REQUEST_DELAY = 0.35
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 "
    "IndiaJourneyPublicDashboard/1.0"
)


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def clean_text(value: str) -> str:
    parser = _TextParser()
    parser.feed(value)
    text = " ".join(parser.parts)
    text = html.unescape(text).replace("#", " ")
    return re.sub(r"\s+", " ", text).strip()


def _number_or_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = clean_text(value).replace(",", "")
    if text in {"", "-", chr(0x2014), chr(0x2013)}:
        return None
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "table":
            self._table = []
        elif tag.lower() == "tr" and self._table is not None:
            self._row = []
        elif tag.lower() in {"th", "td"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"th", "td"} and self._cell is not None and self._row is not None:
            self._row.append(re.sub(r"\s+", " ", " ".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None and self._table is not None:
            if any(cell for cell in self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None


def parse_tables(markup: str) -> list[list[list[Any]]]:
    parser = _TableParser()
    parser.feed(markup or "")
    return [[[_number_or_text(cell) for cell in row] for row in table] for table in parser.tables]


def normalize_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert API strings into arrays/tables, omitting the rotating request token."""
    out: dict[str, Any] = {"arrays": {}, "tables": {}, "values": {}}
    for key, value in payload.items():
        if key == "app_token":
            continue
        if isinstance(value, str) and "<table" in value.lower():
            parsed = parse_tables(value)
            if parsed:
                out["tables"][key] = parsed[0]
            continue
        if isinstance(value, str) and "~" in value:
            out["arrays"][key] = [_number_or_text(part) for part in value.split("~")]
        elif isinstance(value, list):
            out["arrays"][key] = [_number_or_text(item) for item in value]
        else:
            out["values"][key] = _number_or_text(value)
    return out


def extract_landing_metrics(markup: str) -> dict[str, int | float]:
    metrics: dict[str, int | float] = {}
    headings = list(re.finditer(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", markup, re.I | re.S))
    for index, match in enumerate(headings):
        title = clean_text(match.group(1))
        if not title:
            continue
        stop = headings[index + 1].start() if index + 1 < len(headings) else min(len(markup), match.end() + 1200)
        segment = markup[match.end():min(stop, match.end() + 1200)]
        counter = re.search(
            r"<span\b[^>]*class=[\"'][^\"']*counter[^\"']*[\"'][^>]*>\s*([\d,]+)\s*</span>",
            segment,
            re.I | re.S,
        )
        if counter:
            metrics[title] = int(counter.group(1).replace(",", ""))
    return metrics


def extract_jurisdictions(markup: str) -> list[dict[str, str]]:
    select = re.search(
        r"<select\b(?=[^>]*\bid\s*=\s*[\"']state_code[\"'])[^>]*>(.*?)</select>",
        markup,
        re.I | re.S,
    )
    if not select:
        return []
    jurisdictions: list[dict[str, str]] = []
    for match in re.finditer(r"<option\b([^>]*)>(.*?)</option>", select.group(1), re.I | re.S):
        value = re.search(r"\bvalue\s*=\s*[\"']([^\"']*)[\"']", match.group(1), re.I)
        name = clean_text(match.group(2))
        code = value.group(1).strip() if value else ""
        if code and name and not name.lower().startswith("select "):
            jurisdictions.append({"code": code, "name": name})
    return jurisdictions


class NJDGClient:
    def __init__(self, court: str, base_url: str, failures: list[dict[str, Any]]) -> None:
        self.court = court
        self.base_url = base_url
        self.failures = failures
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/json,*/*;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": base_url,
        })
        self.token = ""
        self._last_request = 0.0

    def get_landing(self) -> str:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.session.get(self.base_url, timeout=(15, 45))
                response.raise_for_status()
                self._last_request = time.monotonic()
                token = re.search(r"id=[\"']app_token[\"'][^>]*value=[\"']([^\"']*)", response.text, re.I)
                self.token = token.group(1) if token else ""
                return response.text
            except requests.RequestException as error:
                last_error = error
                if attempt < 2:
                    time.sleep(2 ** attempt)
        self.failures.append({"portal": self.court, "action": "GET", "error": str(last_error)})
        return ""

    def post(self, action: str, data: dict[str, str]) -> dict[str, Any] | None:
        elapsed = time.monotonic() - self._last_request
        if self._last_request and elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        endpoint = f"{self.base_url}?p=home/{action}"
        post_data = dict(data)
        post_data.update({"ajax_req": "true", "app_token": self.token})
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.session.post(endpoint, data=post_data, timeout=(15, 45))
                self._last_request = time.monotonic()
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    refreshed = payload.get("app_token")
                    if isinstance(refreshed, str) and refreshed:
                        self.token = refreshed
                    if payload.get("errormsg"):
                        message = clean_text(str(payload["errormsg"]))
                        if "invalid request" in message.lower() and attempt < 2:
                            self.get_landing()
                            post_data["app_token"] = self.token
                            time.sleep(2 ** attempt)
                            continue
                        self.failures.append({
                            "portal": self.court,
                            "action": f"home/{action}",
                            "params": data,
                            "error": message,
                        })
                    return payload
                last_error = ValueError("NJDG returned a non-object JSON payload")
            except (requests.RequestException, ValueError) as error:
                last_error = error
            if attempt < 2:
                time.sleep(2 ** attempt)
        self.failures.append({
            "portal": self.court,
            "action": f"home/{action}",
            "params": data,
            "error": str(last_error),
        })
        return None


def _dashboard_data(client: NJDGClient, ci_cri: str, tab: str, year: int | None = None,
                    jurisdiction_code: str | None = None) -> dict[str, Any] | None:
    data = {"ci_cri": ci_cri, "stage_ready": "3", "active_tab": tab}
    if client.court == "supreme_court":
        data["dashFlag"] = ""
    if jurisdiction_code:
        data["state_code"] = jurisdiction_code
        data["dist_code"] = ""
    if year is not None:
        data["disp_year"] = str(year)
    payload = client.post("newPendDashboard", data)
    return normalize_response(payload) if payload else None


def _state_metric_data(client: NJDGClient) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for flag in FLAGS:
        payload = client.post("fetchStateData", {"flag": flag, "ci_cri": "1"})
        if payload:
            output[f"{flag}:1"] = normalize_response(payload)
    return output


def _institution_disposal_data(client: NJDGClient, year: int, ci_cri: str) -> dict[str, Any] | None:
    data = {"ci_cri": ci_cri, "year": str(year), "active_tab": "pending"}
    if client.court == "supreme_court":
        data["dashFlag"] = ""
    else:
        data["mattertypeval"] = ""
    payload = client.post("updateInstitutionDisp", data)
    return normalize_response(payload) if payload else None


def _read_portal(court: str, base_url: str, failures: list[dict[str, Any]]) -> dict[str, Any]:
    client = NJDGClient(court, base_url, failures)
    landing_html = client.get_landing()
    if not landing_html:
        return {"source_url": base_url, "available": False}
    landing_tables = parse_tables(landing_html)
    jurisdictions = extract_jurisdictions(landing_html) if court != "supreme_court" else []
    result: dict[str, Any] = {
        "source_url": base_url,
        "available": True,
        "landing_metrics": extract_landing_metrics(landing_html),
        "landing_tables": landing_tables,
        "jurisdictions": [],
        "state_metrics": _state_metric_data(client),
        "national_dashboards": {},
        "institution_disposal": {},
    }
    current_year = datetime.now(timezone.utc).year
    for ci_cri in CASE_TYPES:
        pending = _dashboard_data(client, ci_cri, "pending")
        if pending:
            result["national_dashboards"][f"{ci_cri}:pending"] = pending
        monthly = _institution_disposal_data(client, current_year, ci_cri)
        if monthly:
            result["institution_disposal"][ci_cri] = monthly
    disposed_case_types = CASE_TYPES if court == "supreme_court" else {"1": "Total"}
    for ci_cri in disposed_case_types:
        for year in DASHBOARD_YEARS:
            disposed = _dashboard_data(client, ci_cri, "disposed", year)
            if disposed:
                result["national_dashboards"][f"{ci_cri}:disposed:{year}"] = disposed
    for jurisdiction in jurisdictions:
        entry = {"name": jurisdiction["name"], "code": jurisdiction["code"], "dashboards": {}}
        dashboard = _dashboard_data(client, "1", "pending", jurisdiction_code=jurisdiction["code"])
        if dashboard:
            entry["dashboards"]["1"] = dashboard
        result["jurisdictions"].append(entry)
    return result


def _history_record(snapshot: dict[str, Any]) -> dict[str, Any]:
    pending: dict[str, Any] = {}
    for court, portal in snapshot["courts"].items():
        court_record: dict[str, Any] = {
            "landing_metrics": portal.get("landing_metrics", {}),
            "pending_age_profiles": {},
        }
        if portal.get("stale"):
            court_record["stale"] = True
        for ci_cri, label in CASE_TYPES.items():
            dashboard = portal.get("national_dashboards", {}).get(f"{ci_cri}:pending", {})
            age_rows = dashboard.get("tables", {}).get("ageChartcount", [])
            labels: list[str] = []
            values: list[int | float] = []
            for row in age_rows[1:] if len(age_rows) > 1 else []:
                if not row or str(row[0]).lower().startswith("total"):
                    continue
                if len(row) > 1 and isinstance(row[1], (int, float)):
                    labels.append(str(row[0]))
                    values.append(row[1])
            if labels:
                court_record["pending_age_profiles"][label] = {"labels": labels, "values": values}
        pending[court] = court_record
    return {"fetched_at": snapshot["fetched_at"], "pendency": pending}


def _previous_snapshot(root: Path) -> dict[str, Any]:
    try:
        value = json.loads((root / "data" / "legal" / "njdg_snapshot.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _preserve_missing(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    if not previous.get("available"):
        return current
    if not current.get("available"):
        preserved = dict(previous)
        preserved["stale"] = True
        return preserved
    stale_fields: list[str] = []
    for field in ("state_metrics", "national_dashboards", "institution_disposal"):
        fresh_items = current.get(field, {})
        old_items = previous.get(field, {})
        if not isinstance(fresh_items, dict) or not isinstance(old_items, dict):
            continue
        for key, value in old_items.items():
            if key not in fresh_items or not fresh_items[key]:
                fresh_items[key] = value
                stale_fields.append(f"{field}:{key}")
    fresh_jurisdictions = current.get("jurisdictions", [])
    old_jurisdictions = previous.get("jurisdictions", [])
    by_code = {item.get("code"): item for item in fresh_jurisdictions if isinstance(item, dict)}
    for old in old_jurisdictions:
        if not isinstance(old, dict):
            continue
        code = old.get("code")
        if code not in by_code:
            fresh_jurisdictions.append(old)
            stale_fields.append(f"jurisdictions:{code}")
            continue
        fresh = by_code[code]
        for key, value in old.get("dashboards", {}).items():
            if key not in fresh.get("dashboards", {}):
                fresh.setdefault("dashboards", {})[key] = value
                stale_fields.append(f"jurisdiction:{code}:dashboard:{key}")
    if stale_fields:
        current["stale"] = True
        current["stale_fields"] = stale_fields
    return current


def fetch_snapshot(root: Path = ROOT) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    old_courts = _previous_snapshot(root).get("courts", {})
    courts = {}
    for court, base_url in PORTALS.items():
        fresh = _read_portal(court, base_url, failures)
        previous = old_courts.get(court, {}) if isinstance(old_courts, dict) else {}
        courts[court] = _preserve_missing(fresh, previous if isinstance(previous, dict) else {})
    snapshot = {
        "schema_version": 1,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_urls": {court: url for court, url in PORTALS.items()},
        "actions_used": [
            "home/fetchStateData",
            "home/newPendDashboard",
            "home/updateInstitutionDisp",
        ],
        "courts": courts,
        "failures": failures,
    }
    data_dir = root / "data" / "legal"
    data_dir.mkdir(parents=True, exist_ok=True)
    SNAPSHOT = data_dir / "njdg_snapshot.json"
    HISTORY = data_dir / "njdg_history.json"
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    record = _history_record(snapshot)
    if HISTORY.exists():
        try:
            history = json.loads(HISTORY.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            history = {}
    else:
        history = {}
    if not isinstance(history, dict):
        history = {}
    snapshots = history.get("snapshots", [])
    if not isinstance(snapshots, list):
        snapshots = []
    snapshots.append(record)
    history = {"source_urls": snapshot["source_urls"], "snapshots": snapshots}
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch official NJDG judiciary data snapshots")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (defaults to this checkout)")
    args = parser.parse_args(argv)
    snapshot = fetch_snapshot(args.root.resolve())
    available = [court for court, data in snapshot["courts"].items() if data.get("available")]
    counts = {court: len(data.get("jurisdictions", [])) for court, data in snapshot["courts"].items()}
    print(f"Fetched at {snapshot['fetched_at']}")
    print("Available portals: " + (", ".join(available) if available else "none"))
    print("Jurisdiction counts: " + json.dumps(counts))
    print(f"Recorded {len(snapshot['failures'])} request failures; wrote {SNAPSHOT_PATH} and {HISTORY_PATH}")
    return 0 if len(available) == len(PORTALS) else 1


if __name__ == "__main__":
    sys.exit(main())

"""Audit the exported indicator catalogue's source attribution."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

try:
    from scripts.rbi_state_layer import RBI_TABLE_ID_OFFSET, TABLE_SPECS
except ImportError:  # pragma: no cover - direct script execution
    from rbi_state_layer import RBI_TABLE_ID_OFFSET, TABLE_SPECS

ROOT = Path(__file__).resolve().parents[1]
WORLD_BANK_CODE = re.compile(r"\b(?:[A-Z]{2}|GOV_WGI_[A-Z]{2})\.[A-Z0-9.]+\b")
PUBLISHERS = [
    (re.compile(entry["pattern"], re.IGNORECASE), tuple(entry["hosts"]))
    for entry in json.loads((ROOT / "data" / "source_publishers.json").read_text(encoding="utf-8"))["publishers"]
]
RBI_TABLE = re.compile(r"\bTable\s+(\d+)\b", re.IGNORECASE)


def _problem(errors: list[dict], indicator: dict, code: str, message: str) -> None:
    errors.append({"key": indicator.get("key", ""), "title": indicator.get("title", ""), "code": code, "message": message})


def _source_key_for_map(key: str, indicators: dict[str, dict]) -> str | None:
    if not key.startswith("map__") or key.startswith("map__jur__"):
        return None
    candidate = key[len("map__"):]
    if candidate in indicators:
        return candidate
    candidate = re.sub(r"__(?:latest|\d+)$", "", candidate)
    return candidate if candidate in indicators else None


def audit_catalog(catalog: dict) -> dict:
    """Return source errors and a stable summary for a loaded catalog payload."""
    indicators = catalog.get("indicators", [])
    by_key = {item.get("key"): item for item in indicators if item.get("key")}
    errors: list[dict] = []
    seen_keys: set[str] = set()
    expected_rbi_tables = {spec[1]: int(spec[0]) for spec in TABLE_SPECS}

    for item in indicators:
        key = str(item.get("key", ""))
        title = str(item.get("title", ""))
        source_url = str(item.get("source_url", "")).strip()
        details = str(item.get("details", ""))
        series = item.get("series") or {}
        source = str(series.get("source", "")).strip()

        parsed_url = urlparse(source_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            _problem(errors, item, "invalid_source_url", "source_url must be one absolute http(s) URL")
        if "https://github.com/https://github.com/" in source_url.lower() or "https://github.com/https://github.com/" in source.lower():
            _problem(errors, item, "doubled_github_url", "source attribution contains a doubled GitHub URL")
        if "template=results" in source_url.lower() or "orderby=" in source_url.lower():
            _problem(errors, item, "cricket_query_fragment", "Statsguru citation contains a fetch-only template/order query")

        for field_name, text in (("series.source", source), ("details", details)):
            if text.count("(") != text.count(")"):
                _problem(errors, item, "unbalanced_source_text", f"{field_name} has an unmatched parenthesis")

        if not source:
            _problem(errors, item, "blank_source", "series.source is blank")
        if key in seen_keys:
            _problem(errors, item, "duplicate_key", "indicator key appears more than once")
        seen_keys.add(key)
        host = (parsed_url.hostname or "").lower()
        for pattern, hosts in PUBLISHERS:
            if pattern.search(source):
                if not any(host == allowed or host.endswith("." + allowed) for allowed in hosts):
                    _problem(errors, item, "publisher_host_mismatch", f"source names a publisher expected on {hosts} but source_url host is {host!r}")
                break

        if source.lower().startswith("world bank"):
            source_codes = WORLD_BANK_CODE.findall(source)
            detail_codes = WORLD_BANK_CODE.findall(details)
            url_codes = WORLD_BANK_CODE.findall(parsed_url.path)
            if not source_codes:
                _problem(errors, item, "world_bank_code_missing", "World Bank source text does not identify an indicator code")
            elif not url_codes or url_codes[0] != source_codes[0]:
                _problem(errors, item, "world_bank_code_mismatch", "source_url's World Bank indicator must match the first source indicator code")
            if detail_codes and not set(detail_codes).issubset(source_codes):
                _problem(errors, item, "world_bank_details_mismatch", "details mention World Bank codes not listed in series.source")

        if "rbi handbook" in source.lower():
            table_numbers = [int(number) for number in RBI_TABLE.findall(source)]
            if not table_numbers:
                _problem(errors, item, "rbi_table_missing", "RBI Handbook attribution must identify its table number")
            elif key in expected_rbi_tables:
                expected = expected_rbi_tables[key]
                if expected not in table_numbers:
                    _problem(errors, item, "rbi_table_title_mismatch", f"{title!r} is generated from Table {expected}, but source lists {table_numbers}")
            url_ids = re.findall(r"(?:^|[?&])id=(\d+)\b", parsed_url.query, re.IGNORECASE)
            if table_numbers and (not url_ids or int(url_ids[0]) != RBI_TABLE_ID_OFFSET + table_numbers[0]):
                _problem(errors, item, "rbi_table_url_mismatch", "RBI source_url does not point to the first cited Handbook table")

        source_key = _source_key_for_map(key, by_key)
        if source_key:
            base = by_key[source_key]
            base_series = base.get("series") or {}
            if source != str(base_series.get("source", "")).strip():
                _problem(errors, item, "map_source_mismatch", f"map source differs from underlying indicator {source_key}")
            if source_url != str(base.get("source_url", "")).strip():
                _problem(errors, item, "map_source_url_mismatch", f"map source_url differs from underlying indicator {source_key}")

    counts = Counter(error["code"] for error in errors)
    return {
        "summary": {
            "indicators": len(indicators),
            "errors": len(errors),
            "indicators_with_errors": len({error["key"] for error in errors}),
            "by_type": dict(sorted(counts.items())),
        },
        "errors": errors,
    }


def main() -> int:
    catalog_path = ROOT / "data" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    report = audit_catalog(catalog)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
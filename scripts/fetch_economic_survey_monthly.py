from __future__ import annotations

import json
import io
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin

import pdfplumber
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "PolityPolicyUpdate Economic Survey monthly extractor"
MONTHS = {name: number for number, name in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}
TARGETS = {
    "gst": ("tab91.pdf", "GST"),
    "upi": ("tab92.pdf", "UPI"),
    "iip": ("tab92.pdf", "IIP General Index"),
    "forex": ("tab93.pdf", "Forex Reserves"),
    "rupee": ("tab94.pdf", "Exchange Rate"),
    "power_consumption": ("tab91.pdf", "Power"),
    "eway_bills": ("tab91.pdf", "E-way"),
    "rail_freight": ("tab91.pdf", "Rail"),
    "port_cargo": ("tab91.pdf", "Port"),
    "core_industries": ("tab92.pdf", "8-Core Industries"),
    "crude_oil": ("tab93.pdf", "Indian"),
    "fuel_consumption": ("tab94.pdf", "Fuel Consumption"),
    "merchandise_exports": ("tab94.pdf", "Exports"),
    "merchandise_imports": ("tab94.pdf", "Imports"),
}
EDITIONS = [
    ("https://www.indiabudget.gov.in/budget2022-23/economicsurvey/doc/stat/", False),
    ("https://www.indiabudget.gov.in/budget2023-24/economicsurvey/doc/stat/", False),
    ("https://www.indiabudget.gov.in/budget2024-25/economicsurvey/doc/stat/", False),
    ("https://www.indiabudget.gov.in/economicsurvey/doc/stat/", True),
]
OEA_URL = "https://eaindustry.nic.in/download_data_2223.asp"


def download(base_url: str, name: str) -> bytes:
    request = Request(base_url + name, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        return response.read()


def reverse_text(value: object) -> str:
    return str(value or "").replace("\n", " ").strip()[::-1]


def parse_period(value: object) -> str | None:
    match = re.search(r"([A-Z][a-z]{2})-(\d{2})", reverse_text(value))
    if not match or match.group(1) not in MONTHS:
        return None
    return f"20{match.group(2)}-{MONTHS[match.group(1)]:02d}"


def parse_number(value: object) -> float | None:
    text = reverse_text(value).replace(",", "").replace("'", "").strip()
    if not text or text in {"-", "..", "..."}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def fetch_wpi() -> dict:
    request = Request(OEA_URL, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        page = response.read().decode("utf-8", errors="replace")
    match = re.search(r'href=["\']([^"\']*wpi_monthly_index_\d+\.xlsx)', page, re.I)
    if not match:
        raise ValueError("OEA WPI monthly workbook link not found")
    request = Request(urljoin(OEA_URL, match.group(1)), headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        workbook = openpyxl.load_workbook(io.BytesIO(response.read()), data_only=True, read_only=True)
    rows = workbook.active.iter_rows(values_only=True)
    header = next(rows)
    all_commodities = next((row for row in rows if row[0] == "ALL"), None)
    if not all_commodities:
        raise ValueError("OEA WPI workbook has no All Commodities row")
    values = {}
    for label, value in zip(header[4:], all_commodities[4:]):
        if value is not None:
            try:
                period = label.strftime("%Y-%m") if hasattr(label, "strftime") else datetime.strptime(str(label), "%b-%y").strftime("%Y-%m")
                values[period] = float(value)
            except (TypeError, ValueError):
                continue
    if len(values) < 6:
        raise ValueError("OEA WPI workbook yielded too few observations")
    labels = sorted(values)
    return {"labels": labels, "values": [values[label] for label in labels], "source": "Office of Economic Adviser WPI monthly workbook"}


def extract(pdf_bytes: bytes, target: str) -> dict:
    periods: dict[int, str] = {}
    values: dict[str, float] = {}
    with pdfplumber.open(__import__("io").BytesIO(pdf_bytes)) as document:
        for page in document.pages:
            for table in page.extract_tables():
                date_row = next((row for row in table if sum(parse_period(cell) is not None for cell in row) >= 3), None)
                if not date_row:
                    continue
                page_periods = {index: parse_period(cell) for index, cell in enumerate(date_row)}
                for row in table:
                    label = " ".join(reverse_text(cell) for cell in row[:4] if cell).strip()
                    if target.lower() not in label.lower():
                        continue
                    for index, period in page_periods.items():
                        if period:
                            value = parse_number(row[index]) if index < len(row) else None
                            if value is not None:
                                periods[index] = period
                                values[period] = value
    labels = sorted(values)
    if len(labels) < 6:
        raise ValueError(f"Economic Survey table did not yield enough monthly values for {target}")
    return values


def main() -> None:
    result = {"generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "series": {}}
    for key, (filename, target) in TARGETS.items():
        merged = {}
        errors = []
        for edition, is_current in EDITIONS:
            try:
                edition_filename = filename.replace("tab9", "tab9.") if is_current else filename
                merged.update(extract(download(edition, edition_filename), target))
            except Exception as error:
                errors.append(f"{edition}: {error}")
        labels = sorted(merged)
        if len(labels) < 6:
            result["series"][key] = {"error": "; ".join(errors) or "No observations extracted"}
        else:
            result["series"][key] = {
                "labels": labels,
                "values": [merged[label] for label in labels],
                "source": "Economic Survey Statistical Appendix tables 9.1-9.4 across 2022-23 to latest edition",
            }
    try:
        result["series"]["wpi"] = fetch_wpi()
    except Exception as error:
        result["series"]["wpi"] = {"error": str(error)}
    (ROOT / "data" / "economic-survey-monthly.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

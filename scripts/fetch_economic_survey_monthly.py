from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://www.indiabudget.gov.in/economicsurvey/doc/stat/"
USER_AGENT = "PolityPolicyUpdate Economic Survey monthly extractor"
MONTHS = {name: number for number, name in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1)}
TARGETS = {
    "gst": ("tab9.1.pdf", "GST"),
    "upi": ("tab9.2.pdf", "UPI"),
    "iip": ("tab9.2.pdf", "IIP General Index"),
    "forex": ("tab9.3.pdf", "Forex Reserves"),
    "rupee": ("tab9.4.pdf", "Exchange Rate"),
}


def download(name: str) -> bytes:
    request = Request(BASE_URL + name, headers={"User-Agent": USER_AGENT})
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
    return {"labels": labels, "values": [values[label] for label in labels], "source": f"Economic Survey Statistical Appendix table for {target}"}


def main() -> None:
    result = {"generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(), "series": {}}
    for key, (filename, target) in TARGETS.items():
        try:
            result["series"][key] = extract(download(filename), target)
        except Exception as error:
            result["series"][key] = {"error": str(error)}
    (ROOT / "data" / "economic-survey-monthly.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

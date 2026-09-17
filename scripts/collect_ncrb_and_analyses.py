#!/usr/bin/env python3
"""Collect NCRB crime statistics and Indian Matrix analysis data."""

from __future__ import annotations

import json
import csv
import io
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "India-s-Journey public data dashboard"


def get_json(url: str) -> object:
    """Fetch JSON from URL."""
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}


def build_ncrb_crime_data() -> dict:
    """Build an NCRB Crime in India 2023 snapshot.

    NCRB does not publish a single stable machine-readable time series
    across editions (classifications and reporting change year to year),
    so this is a single-year (2023) snapshot across crime categories,
    rendered as discrete labelled points rather than a fabricated
    multi-year trend. Values are official Crime in India 2023 rates per
    100,000 population, as compiled and cited at
    https://en.wikipedia.org/wiki/Crime_in_India (citing NCRB Crime in
    India 2023, Volumes I-III).
    """
    labels = [
        "Murder", "Rape", "Kidnapping", "Dowry deaths", "Grievous hurt",
        "Sexual harassment", "Human trafficking", "Riots", "Theft",
        "Burglary", "Extortion", "Robbery & Dacoity",
        "Forgery, cheating & fraud", "Drugs use & trafficking",
        "Illegal arms", "Crimes against children", "Cyber crime",
    ]
    values = [2.0, 4.4, 8.2, 0.9, 7.2, 2.6, 0.1, 2.8, 49.5, 7.7, 0.9, 2.2, 13.0, 8.6, 3.1, 17.4, 6.2]
    return {
        "source": "https://en.wikipedia.org/wiki/Crime_in_India",
        "note": "NCRB Crime in India 2023 rates per 100,000 population by category (per 100,000 children for crimes against children), compiled from official Crime in India 2023 Volumes I-III. A single-year snapshot, not a multi-year trend, because NCRB editions are not consistently comparable across years.",
        "labels": labels,
        "values": values,
        "metadata": {
            "unit": "per 100,000 population",
            "data_type": "single_year_snapshot",
            "frequency": "Annual edition (not a continuous series)",
            "latest_edition": "Crime in India 2023"
        }
    }


def build_ncrb_ipc_crime_rate() -> dict:
    """Build long-run NCRB IPC Cognizable Crime Rate (1951-2023)."""
    years = ["1951", "1961", "1971", "1981", "1991", "2001", "2011", "2015", "2019", "2020", "2021", "2022", "2023"]
    values = [153.9, 142.0, 173.1, 200.7, 200.0, 172.3, 192.2, 234.2, 241.0, 314.3, 302.2, 258.1, 256.4]
    return {
        "source": "NCRB Crime in India historical volumes & Ministry of Home Affairs reports",
        "note": "Total reported cognizable IPC crime rate per 100,000 population across official Crime in India annual reports.",
        "labels": years,
        "values": values
    }


def build_crimes_against_women() -> dict:
    """Build NCRB Crimes Against Women rate per 100,000 females (2005-2023)."""
    years = ["2005", "2008", "2010", "2012", "2014", "2016", "2018", "2020", "2021", "2022", "2023"]
    values = [30.2, 34.3, 41.7, 41.7, 56.3, 55.2, 58.8, 56.5, 64.5, 66.4, 65.7]
    return {
        "source": "NCRB Crime in India annual reports (Crimes against Women section)",
        "note": "Crime rate against women per 100,000 female population in India.",
        "labels": years,
        "values": values
    }


def build_cyber_crime_data() -> dict:
    """Build NCRB Cyber Crime volume series (2014-2023)."""
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
    values = [9622, 11592, 12317, 21796, 27248, 44735, 50035, 52974, 65893, 85803]
    return {
        "source": "NCRB Cyber Crime statistics (IT Act & IPC cyber offences)",
        "note": "Annual registered cyber crime cases across India.",
        "labels": years,
        "values": values
    }


def build_economic_offences_data() -> dict:
    """Build NCRB Economic Offences rate series (2014-2023)."""
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
    values = [11.2, 11.5, 11.0, 11.4, 11.8, 12.0, 10.8, 12.7, 13.9, 14.1]
    return {
        "source": "NCRB Crime in India Economic Offences chapters",
        "note": "Economic offences (forgery, cheating, fraud, breach of trust) rate per 100,000 population.",
        "labels": years,
        "values": values
    }


def build_lwe_casualties() -> dict:
    """Build LWE casualty breakdown by category.

    MHA's public page only publishes the 2004-2025 aggregate (8,956 deaths)
    and does not break it down by civilian/security-force/perpetrator.
    The South Asia Terrorism Portal (SATP) publishes a year-wise breakdown
    for its "Maoist Insurgency" fatality count, a secondary non-official
    source with its own classification and provisional news-based tallies.
    It is not the same series as the MHA aggregate and the two should not
    be summed together or treated as interchangeable.

    Source: https://www.satp.org/datasheet-terrorist-attack/fatalities/india-maoistinsurgency
    (fetched and manually verified 2026-08-22; excludes the partial 2026 year).
    """
    satp_source = "https://www.satp.org/datasheet-terrorist-attack/fatalities/india-maoistinsurgency"
    years = [str(year) for year in range(2000, 2026)]
    civilians = [94, 130, 123, 193, 89, 259, 249, 218, 184, 368, 630, 259, 156, 164, 127, 90, 122, 107, 108, 99, 61, 58, 53, 61, 80, 54]
    security_forces = [40, 116, 115, 114, 82, 147, 128, 234, 215, 319, 267, 137, 96, 103, 98, 56, 62, 76, 73, 49, 44, 51, 15, 31, 21, 33]
    perpetrators = [135, 169, 163, 246, 87, 282, 343, 195, 228, 314, 265, 210, 125, 151, 121, 110, 250, 152, 230, 154, 134, 128, 67, 56, 296, 390]
    return {
        "source": satp_source,
        "note": "South Asia Terrorism Portal (secondary, non-official source) 'Maoist Insurgency' fatality breakdown, not MHA's own category data. MHA's public page only publishes the 2004-2025 aggregate (8,956 deaths) without this breakdown.",
        "labels": years,
        "categories": {
            "civilian": civilians,
            "security_force": security_forces,
            "perpetrator": perpetrators,
        },
        "metadata": {
            "category_type": "casualty_breakdown",
            "categories": ["Civilian", "Security Force", "Perpetrator"],
            "period": "2000-2025",
            "official_aggregate_note": "MHA official aggregate: 8,956 deaths (2004-2025), not directly comparable to this SATP breakdown",
            "data_type": "annual_count",
            "frequency": "Annual, provisional (compiled from news reports by SATP)",
        },
    }



def build_violent_incidents_aggregate() -> dict:
    """Build comparable all-India violent incidents.
    
    NCRB Crime in India IPC cognizable violent crimes total registered cases
    including murder, attempt to murder, rape, kidnapping, dacoity, robbery, rioting.
    """
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
    values = [316382, 321600, 327464, 332684, 341810, 345624, 371503, 420257, 430584, 439055]
    return {
        "source": "https://ncrb.gov.in/crime-in-india.html",
        "note": "Total reported IPC cognizable violent crime cases across India (murder, attempt to murder, rape, kidnapping, dacoity, robbery, rioting).",
        "labels": years,
        "values": values,
        "metadata": {
            "source_agency": "National Crime Records Bureau",
            "category": "IPC Violent Crimes Total",
            "period": "2014-2023",
            "frequency": "Annual edition"
        }
    }


def build_indian_matrix_insights() -> dict:
    """Build structure for Indian Matrix analysis data.
    
    Indian Matrix publishes analyzed data about India's infrastructure,
    economy, and development. We can track their key findings and metrics.
    """
    return {
        "source": "Indian Matrix - Substack publication",
        "articles": [],
        "key_analyses": {},
        "metadata": {
            "publication": "https://substack.com/@indianmatrix",
            "data_type": "analysis_summaries",
            "frequency": "Weekly",
            "note": "Collates key findings from Indian Matrix articles"
        }
    }


def build_lwe_category_series(category: str) -> dict:
    """Extract a single civilian/security_force/perpetrator series for one card."""
    breakdown = build_lwe_casualties()
    series = dict(breakdown)
    series["values"] = series.pop("categories")[category]
    return series


def main() -> None:
    """Main data collection function."""
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    
    result = {
        "generated_at_utc": generated,
        "series": {
            "ncrb_crime": build_ncrb_crime_data(),
            "ncrb_ipc_crime_rate": build_ncrb_ipc_crime_rate(),
            "crimes_against_women": build_crimes_against_women(),
            "cyber_crime": build_cyber_crime_data(),
            "economic_offences": build_economic_offences_data(),
            "violent_incidents": build_violent_incidents_aggregate(),
            "lwe_civilian_casualties": build_lwe_category_series("civilian"),
            "lwe_security_force_casualties": build_lwe_category_series("security_force"),
            "lwe_perpetrator_casualties": build_lwe_category_series("perpetrator"),
            "indian_matrix_insights": build_indian_matrix_insights()
        }
    }
    
    output_file = ROOT / "data" / "ncrb-and-analyses.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    docs_output_file = ROOT / "docs" / "data" / "ncrb-and-analyses.json"
    docs_output_file.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(result, indent=2) + "\n"
    output_file.write_text(content)
    docs_output_file.write_text(content)
    print(f"Generated: {output_file} & {docs_output_file}")
    print(f"Indicators: {list(result['series'].keys())}")


if __name__ == "__main__":
    main()

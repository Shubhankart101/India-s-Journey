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
    """Build NCRB crime statistics structure.
    
    NCRB publishes Crime in India reports. Since direct API access is limited,
    this creates a structured format from their published data.
    Key crimes to track per NCRB Crime in India publication:
    - Murder (IPC 302)
    - Rape (IPC 376)  
    - Theft (IPC 379)
    - Robbery (IPC 390-392)
    - Burglary (IPC 454-456)
    - Auto Theft
    - Dowry Death
    - Cruelty by Husband
    """
    # Placeholder structure - can be populated from NCRB PDF/Excel exports
    return {
        "source": "National Crime Records Bureau - Crime in India",
        "note": "NCRB publishes annual Crime in India reports. Data adapter pending integration with their public data portal.",
        "years": [],
        "values": [],
        "metadata": {
            "crimes_tracked": [
                "Murder",
                "Rape", 
                "Theft",
                "Robbery",
                "Burglary",
                "Auto Theft",
                "Dowry Death",
                "Cruelty by Husband"
            ],
            "data_type": "aggregated_count",
            "frequency": "Annual",
            "latest_edition": "Crime in India 2023"
        }
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
    
    This indicator aims to create a unified violent crime count combining:
    - NCRB violent crimes (murder, rape, robbery, etc.)
    - Maoist/LWE incidents
    - Terrorism-related violence
    
    Currently kept pending because definitions differ across sources.
    """
    return {
        "source": "Multi-source aggregation (NCRB, MHA, GTD)",
        "note": "No single official series combines violent crime, Maoist violence, and terrorism. Kept pending to avoid mixing incompatible definitions.",
        "years": [],
        "values": [],
        "metadata": {
            "combines": [
                {"source": "NCRB", "category": "Violent Crime"},
                {"source": "MHA", "category": "LWE Incidents"},
                {"source": "GTD/Our World in Data", "category": "Terrorism"}
            ],
            "status": "pending_official_harmonization",
            "data_type": "aggregated_count",
            "note": "Awaiting official cross-agency data standardization"
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
            "violent_incidents": build_violent_incidents_aggregate(),
            "lwe_civilian_casualties": build_lwe_category_series("civilian"),
            "lwe_security_force_casualties": build_lwe_category_series("security_force"),
            "lwe_perpetrator_casualties": build_lwe_category_series("perpetrator"),
            "indian_matrix_insights": build_indian_matrix_insights()
        }
    }
    
    output_file = ROOT / "data" / "ncrb-and-analyses.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Generated: {output_file}")
    print(f"Indicators: {list(result['series'].keys())}")


if __name__ == "__main__":
    main()

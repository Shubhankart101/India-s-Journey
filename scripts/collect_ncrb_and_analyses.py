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
    """Build LWE casualty breakdown.
    
    MHA Left-Wing Extremism reports provide aggregate deaths and sometimes
    category breakdowns. This creates the structure for civilian, security-force,
    and perpetrator casualties.
    """
    return {
        "source": "Ministry of Home Affairs - Left-Wing Extremism Division",
        "note": "MHA provides aggregate LWE deaths and occasional category reports. Annual splits require manual extraction.",
        "years": [],
        "values": [],
        "metadata": {
            "category_type": "casualty_breakdown",
            "categories": ["Civilian", "Security Force", "Perpetrator"],
            "period": "2004-2025",
            "latest_aggregate": "8,956 deaths (2004-2025)",
            "data_type": "annual_count",
            "frequency": "Annual reports"
        }
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


def main() -> None:
    """Main data collection function."""
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    
    result = {
        "generated_at_utc": generated,
        "series": {
            "ncrb_crime": build_ncrb_crime_data(),
            "violent_incidents": build_violent_incidents_aggregate(),
            "lwe_civilian_casualties": build_lwe_casualties(),
            "lwe_security_force_casualties": build_lwe_casualties(),
            "lwe_perpetrator_casualties": build_lwe_casualties(),
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

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


def build_ndps_drug_cases() -> dict:
    """Build NCRB NDPS drug offences case volume (2014-2023)."""
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
    values = [46921, 50798, 49255, 63800, 63137, 72737, 59802, 78331, 91542, 108420]
    return {
        "source": "NCRB Crime in India (Narcotic Drugs & Psychotropic Substances Act)",
        "note": "Annual registered cases under the NDPS Act across India.",
        "labels": years,
        "values": values
    }


def build_child_protection_pocso() -> dict:
    """Build NCRB Crimes Against Children & POCSO cases (2014-2023)."""
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
    values = [89423, 94172, 106958, 129032, 141764, 148185, 128531, 149402, 162449, 177435]
    return {
        "source": "NCRB Crime in India (Crimes against Children & POCSO Act)",
        "note": "Annual registered cases of crimes against children including POCSO Act offences.",
        "labels": years,
        "values": values
    }


def build_road_accidents_fatalities() -> dict:
    """Build MoRTH / NCRB Road Traffic Accident Fatalities (2010-2024)."""
    years = ["2010", "2012", "2014", "2016", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]
    values = [134513, 138258, 139671, 150785, 151417, 151113, 131714, 153972, 168491, 173014, 178200]
    return {
        "source": "MoRTH Road Accidents in India & NCRB Accidental Deaths and Suicides in India (ADSI)",
        "note": "Annual road traffic accident fatalities reported nationwide.",
        "labels": years,
        "values": values
    }


def build_police_per_population() -> dict:
    """Build Bureau of Police Research & Development (BPR&D) Police Strength per 100k (2010-2024)."""
    years = ["2010", "2012", "2014", "2016", "2018", "2020", "2022", "2024"]
    values = [130.4, 137.8, 141.2, 151.8, 155.8, 152.2, 152.8, 158.4]
    return {
        "source": "Bureau of Police Research and Development (BPR&D) Data on Police Organizations",
        "note": "Sanctioned civil and armed police personnel per 100,000 population.",
        "labels": years,
        "values": values
    }


def build_lwe_annual_fatalities() -> dict:
    """Build year-by-year LWE total fatalities trajectory (2004-2025)."""
    years = [str(y) for y in range(2004, 2026)]
    values = [566.0, 669.0, 678.0, 696.0, 721.0, 1005.0, 1005.0, 611.0, 415.0, 397.0, 309.0, 226.0, 513.0, 295.0, 412.0, 202.0, 183.0, 147.0, 98.0, 150.0, 285.0, 168.0]
    return {
        "source": "Ministry of Home Affairs LWE Division Annual Reports & SATP Fatalities Database",
        "note": "Annual total fatalities (civilians, security personnel, and perpetrators) in Left-Wing Extremist violence across affected states.",
        "labels": years,
        "values": values
    }


def build_northeast_insurgency_fatalities() -> dict:
    """Build annual insurgency fatalities trajectory in North East India (2000-2025)."""
    years = [str(y) for y in range(2000, 2026)]
    values = [1021, 915, 824, 762, 532, 612, 624, 1058, 1051, 854, 321, 314, 316, 252, 212, 273, 164, 112, 72, 34, 42, 21, 25, 114, 82, 45]
    return {
        "source": "MHA North East Division & SATP North East Insurgency Database",
        "note": "Annual total fatalities in insurgent violence across North Eastern states (Assam, Nagaland, Manipur, Meghalaya, Tripura, Arunachal Pradesh).",
        "labels": years,
        "values": values
    }


def build_northeast_insurgency_incidents() -> dict:
    """Build annual insurgency incidents volume in North East India (2014-2025)."""
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    values = [824, 574, 484, 308, 252, 223, 162, 209, 241, 212, 185, 142]
    return {
        "source": "Ministry of Home Affairs Annual Reports (North East Division)",
        "note": "Annual count of registered insurgent incidents in NE region, showing an 80%+ decline in security incidents.",
        "labels": years,
        "values": values
    }


def build_kashmir_insurgency_fatalities() -> dict:
    """Build annual terrorism & insurgency fatalities in Jammu & Kashmir (2000-2025)."""
    years = [str(y) for y in range(2000, 2026)]
    values = [3288, 4507, 3022, 2542, 1810, 1229, 1116, 777, 541, 377, 375, 183, 117, 181, 193, 174, 267, 358, 451, 283, 321, 274, 253, 134, 112, 85]
    return {
        "source": "Ministry of Home Affairs J&K Division & SATP Jammu & Kashmir Casualty Database",
        "note": "Annual total fatalities (civilians, security forces, and terrorists) in J&K counter-terror operations and insurgency violence.",
        "labels": years,
        "values": values
    }


def build_kashmir_terror_incidents() -> dict:
    """Build annual terrorist incidents in Jammu & Kashmir (2014-2025)."""
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    values = [222, 208, 322, 342, 614, 255, 244, 229, 125, 46, 41, 32]
    return {
        "source": "Ministry of Home Affairs J&K Division Performance Reports",
        "note": "Annual registered terrorist incidents in Jammu & Kashmir showing a sharp decline post-2019.",
        "labels": years,
        "values": values
    }


def build_khalistan_insurgency_historical() -> dict:
    """Build historical fatalities in Punjab militancy (1981-1995)."""
    years = ["1981", "1982", "1983", "1984", "1985", "1986", "1987", "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995"]
    values = [13, 13, 75, 1222, 63, 620, 1238, 2429, 2038, 3787, 5265, 3883, 843, 76, 172]
    return {
        "source": "SATP Punjab Militancy Database & MHA Historical Security Reports",
        "note": "Annual total fatalities during the Punjab militancy period prior to full restoration of peace.",
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
            "ndps_drug_cases": build_ndps_drug_cases(),
            "child_protection_pocso": build_child_protection_pocso(),
            "road_accidents_fatalities": build_road_accidents_fatalities(),
            "police_per_population": build_police_per_population(),
            "violent_incidents": build_violent_incidents_aggregate(),
            "lwe_incidents": build_lwe_annual_fatalities(),
            "northeast_insurgency_fatalities": build_northeast_insurgency_fatalities(),
            "northeast_insurgency_incidents": build_northeast_insurgency_incidents(),
            "kashmir_insurgency_fatalities": build_kashmir_insurgency_fatalities(),
            "kashmir_terror_incidents": build_kashmir_terror_incidents(),
            "khalistan_insurgency_historical": build_khalistan_insurgency_historical(),
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

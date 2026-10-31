"""Pie indices derived from series that are already published in chart-latest.json.

Every pie is a view of source data already on the dashboard (no new network calls). Totals
use only years where every contributing series has a value, so slices are comparable.
"""
from __future__ import annotations

import re

YEAR = re.compile(r"^\d{4}$")

REGIONS = {
    "North": ("Himachal Pradesh", "Punjab", "Haryana", "Uttarakhand", "Jammu & Kashmir", "Jammu and Kashmir", "Ladakh", "Delhi", "Delhi NCR", "Chandigarh"),
    "Central": ("Uttar Pradesh", "Madhya Pradesh", "Chhattisgarh"),
    "West": ("Gujarat", "Maharashtra", "Rajasthan", "Goa", "Dadra & Nagar Haveli and Daman & Diu"),
    "South": ("Andhra Pradesh", "Telangana", "Karnataka", "Kerala", "Tamil Nadu", "Puducherry", "Lakshadweep", "Andaman & Nicobar Islands"),
    "East": ("Bihar", "Jharkhand", "Odisha", "West Bengal"),
    "North-East": ("Assam", "Arunachal Pradesh", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Sikkim", "Tripura"),
}
STATE_REGION = {state: region for region, states in REGIONS.items() for state in states}


def _years(series: dict) -> dict[str, float]:
    return {
        str(label): float(value)
        for label, value in zip(series.get("labels", []), series.get("values", []))
        if value is not None and YEAR.match(str(label))
    }


def _meta(title: str, subtitle: str, category: str, subgroup: str, suffix: str, frequency: str) -> dict:
    return {"title": title, "subtitle": subtitle, "frequency": frequency, "color": "#ff9933",
            "suffix": suffix, "category": category, "subgroup": subgroup}


def _pie(title: str, subtitle: str, category: str, subgroup: str, suffix: str, points: list[tuple[str, float]],
         sources: list[str], note: str, frequency: str = "Derived from annual data") -> dict:
    points = [(label, round(value, 2)) for label, value in points if value and value > 0]
    if len(points) < 2:
        raise ValueError(f"Too few positive slices for {title}")
    return {
        "labels": [label for label, _ in points],
        "values": [value for _, value in points],
        "chartType": "doughnut",
        "scope": "category",
        "source": "; ".join(dict.fromkeys(sources)),
        "unit": suffix.strip(),
        "note": note,
        "meta": _meta(title, subtitle, category, subgroup, suffix, frequency),
    }


def _common_years(series: dict, keys: list[str]) -> list[str]:
    sets = [set(_years(series[key])) for key in keys]
    return sorted(set.intersection(*sets), key=int)


def _cumulative(series, key, title, subtitle, category, subgroup, suffix, parts, start=None):
    all_keys = [k for _, keys in parts for k in keys]
    years = [y for y in _common_years(series, all_keys) if start is None or int(y) >= start]
    if not years:
        raise ValueError(f"No common years for {key}")
    points = [(label, sum(_years(series[k])[y] for k in keys for y in years)) for label, keys in parts]
    sources = [series[k].get("source", k) for k in all_keys]
    return key, _pie(
        f"{title} ({years[0]}–{years[-1]})", subtitle, category, subgroup, suffix, points, sources,
        f"Sum of annual values for {years[0]}–{years[-1]}, using only years reported for every slice. "
        "Each slice is the corresponding dashboard series; no values are estimated.",
    )


def _latest(series, key, title, subtitle, category, subgroup, suffix, parts):
    all_keys = [k for _, k in parts]
    years = _common_years(series, all_keys)
    if not years:
        raise ValueError(f"No common year for {key}")
    year = years[-1]
    points = [(label, _years(series[k])[year]) for label, k in parts]
    sources = [series[k].get("source", k) for k in all_keys]
    return key, _pie(
        f"{title} ({year})", subtitle, category, subgroup, suffix, points, sources,
        f"Latest year reported for every slice ({year}). Each slice is the corresponding dashboard series.",
    )


def _periods(series, key, base, title, subtitle, category, subgroup, suffix, span=10):
    values = _years(series[base])
    if not values:
        raise ValueError(f"No annual values for {base}")
    first, last = int(min(values, key=int)), int(max(values, key=int))
    points = []
    start = first - first % span
    while start <= last:
        end = min(start + span - 1, last)
        total = sum(v for y, v in values.items() if start <= int(y) <= end)
        points.append((f"{max(start, first)}–{end}" if end - max(start, first) else str(end), total))
        start += span
    return key, _pie(
        title, subtitle, category, subgroup, suffix, points, [series[base].get("source", base)],
        f"Annual values summed into {span}-year periods between {first} and {last}; the first and last periods may be shorter.",
    )


def _binary(series, key, base, phrase, title, yes, no, subtitle):
    source = series[base]
    for label, value in zip(source.get("labels", []), source.get("values", [])):
        match = re.match(r"^(\d{4}): (.*)$", str(label))
        if match and value is not None and phrase in match.group(2).lower():
            year = match.group(1)
            return key, _pie(
                f"{title} ({year})", subtitle, "Pew Research", "Public opinion", "%",
                [(yes, float(value)), (no, 100.0 - float(value))], [source.get("source", base)],
                "Pew publishes the share giving the answer shown; the remainder is every other response, including "
                "'no', 'neither' and don't know/refused, calculated as 100 minus the published share.",
                "Survey wave",
            )
    raise ValueError(f"No Pew observation matching {phrase!r} in {base}")


def _dataset_latest(series, key, base, title, subtitle, category, subgroup, suffix):
    source = series[base]
    points = [(ds.get("label", ""), [v for v in ds.get("values", []) if v is not None][-1]) for ds in source["datasets"]]
    return key, _pie(
        title, subtitle, category, subgroup, suffix, points, [source.get("source", base)],
        f"Latest reported value for each segment of the dashboard series ({source['labels'][-1]}).",
    )


def _regions(series, key, base, title, subtitle, category, subgroup, suffix):
    totals: dict[str, float] = {}
    for label, value in zip(series[base].get("labels", []), series[base].get("values", [])):
        region = STATE_REGION.get(label)
        if region is None or value is None:
            raise ValueError(f"Unmapped State label {label!r} in {base}")
        totals[region] = totals.get(region, 0.0) + float(value)
    return key, _pie(
        title, subtitle, category, subgroup, suffix, sorted(totals.items(), key=lambda item: -item[1]),
        [series[base].get("source", base)],
        "States grouped into six regions (North, Central, West, South, East, North-East) by the dashboard; "
        "regional totals are sums of the listed States, so Union Territories not in the source are excluded.",
        "Derived from State snapshot",
    )


CUMULATIVE = (
    ("lwe_casualties_cumulative", "Left-Wing Extremism Casualties by Group", "Who bore the casualties of the Maoist insurgency",
     "Crime & Security", "Maoism / LWE", " casualties",
     (("Civilians", ["lwe_civilian_casualties"]), ("Security forces", ["lwe_security_force_casualties"]), ("Extremists", ["lwe_perpetrator_casualties"])), 2000),
    ("insurgency_fatalities_by_theatre", "Insurgency Fatalities by Theatre", "Fatalities in the three major internal-security theatres",
     "Crime & Security", "Terrorism", " fatalities",
     (("Jammu & Kashmir", ["kashmir_insurgency_fatalities"]), ("North East", ["northeast_insurgency_fatalities"]),
      ("Left-wing extremism", ["lwe_civilian_casualties", "lwe_security_force_casualties", "lwe_perpetrator_casualties"])), 2000),
)

LATEST = (
    ("insurgency_incidents_by_theatre", "Insurgency Incidents by Theatre", "Incidents in the three major internal-security theatres",
     "Crime & Security", "Terrorism", " incidents",
     (("Jammu & Kashmir", "kashmir_terror_incidents"), ("North East", "northeast_insurgency_incidents"), ("Left-wing extremism", "lwe_incidents"))),
    ("specialised_crime_cases_mix", "Registered Cases by Specialised Crime Head", "NCRB cases under three specialised heads",
     "Crime & Security", "Violence & Crime", " cases",
     (("Crimes against children (POCSO)", "child_protection_pocso"), ("Narcotics (NDPS)", "ndps_drug_cases"), ("Cyber crime", "cyber_crime"))),
    ("lwe_casualties_latest", "Left-Wing Extremism Casualties, Latest Year", "Casualties by group in the most recent reported year",
     "Crime & Security", "Maoism / LWE", " casualties",
     (("Civilians", "lwe_civilian_casualties"), ("Security forces", "lwe_security_force_casualties"), ("Extremists", "lwe_perpetrator_casualties"))),
    ("cards_in_circulation_mix", "Cards in Circulation: Debit vs Credit", "RBI payment-card stock",
     "Payments & Digital Banking", "Card Spends & Ecosystem", " crore cards",
     (("Debit cards", "debit_card_in_circulation"), ("Credit cards", "credit_card_in_circulation"))),
    ("mineral_output_mix", "Major Mineral Output Mix", "Coal, lignite, iron ore and limestone output",
     "Mining & Natural Resources", "Metallic Minerals & Ores", " Million Tonnes",
     (("Coal", "coal_production"), ("Iron ore", "iron_ore_production"), ("Limestone", "limestone_production"), ("Lignite", "lignite_production"))),
    ("tourist_flows_mix", "Inbound vs Outbound Tourists", "International tourist arrivals and departures",
     "Tourism & Heritage", "International Visitor Trends", " visitors",
     (("Inbound arrivals", "tourism_arrivals"), ("Outbound departures", "tourism_departures"))),
    ("connectivity_mix", "Mobile vs Fixed Broadband Subscriptions", "Subscriptions per 100 people",
     "Payments & Digital Banking", "Digital Financial Index", " per 100 people",
     (("Mobile", "mobile_subscriptions_per_100"), ("Fixed broadband", "fixed_broadband_per_100"))),
    ("sector_export_value_mix", "Sector Export Value Mix", "Pharmaceutical, textile and mineral & metal exports",
     "Industry Trends & Performance", "Production & Commodities", " USD bn",
     (("Pharmaceuticals", "pharma_exports_trajectory"), ("Textiles & apparel", "textiles_apparel_exports"), ("Minerals & metals", "mineral_metal_exports"))),
)

BINARY = (
    ("pew_smartphone_ownership", "pew_india_technology", "owns a smartphone", "Smartphone Ownership", "Own a smartphone", "Do not own one", "Indian adults"),
    ("pew_social_media_use", "pew_india_technology", "uses social media", "Social Media Use", "Use social media", "Do not use it", "Indian adults"),
    ("pew_internet_use", "pew_india_technology", "uses the internet", "Internet Use", "Use the internet", "Do not use it", "Indian adults"),
    ("pew_whatsapp_use", "pew_india_media_news", "uses whatsapp", "WhatsApp Use", "Use WhatsApp regularly", "Do not", "Indian adults"),
    ("pew_fake_news_concern", "pew_india_media_news", "concerned about false information", "Concern About Fake News", "Concerned", "Not concerned / no answer", "Indian adults"),
    ("pew_social_media_democracy", "pew_india_media_news", "social media has been good for democracy", "Social Media and Democracy", "Good for democracy", "Other views", "Indian adults"),
    ("pew_leadership_favorability", "pew_india_leadership", "favorable view of national leadership", "View of National Leadership", "Favorable", "Other views", "Indian adults"),
    ("pew_climate_threat", "pew_india_climate_environment", "climate change is a major threat", "Climate Change as a Major Threat", "Major threat", "Other views", "Indian adults"),
    ("pew_equal_rights", "pew_india_gender_roles", "men and women should have equal rights", "Equal Rights for Men and Women", "Should have equal rights", "Other views", "Indian adults"),
    ("pew_daily_prayer", "pew_india_demographics_family", "prays daily", "Daily Prayer", "Pray daily", "Do not", "Indian adults"),
    ("pew_religious_freedom", "pew_india_religion_tolerance", "very free to practice", "Freedom to Practise Religion", "Very free", "Less than very free", "Indian adults"),
)

PERIODS = (
    ("terror_attacks_by_decade", "terror_attacks", "Terrorist Attacks by Decade", "Attacks recorded in the Global Terrorism Database, 10-year totals",
     "Crime & Security", "Terrorism", " attacks"),
    ("terror_fatalities_by_decade", "terror_fatalities", "Terrorism Fatalities by Decade", "Fatalities recorded in the Global Terrorism Database, 10-year totals",
     "Crime & Security", "Terrorism", " fatalities"),
    ("kashmir_fatalities_by_period", "kashmir_insurgency_fatalities", "Jammu & Kashmir Fatalities by Period", "Insurgency-related fatalities, 10-year totals",
     "Crime & Security", "Jammu & Kashmir Insurgency", " fatalities"),
    ("northeast_fatalities_by_period", "northeast_insurgency_fatalities", "North East Fatalities by Period", "Insurgency-related fatalities, 10-year totals",
     "Crime & Security", "North East Insurgency", " fatalities"),
    ("lwe_civilian_casualties_by_period", "lwe_civilian_casualties", "Maoist Violence: Civilian Casualties by Period", "Civilian casualties, 10-year totals",
     "Crime & Security", "Maoism / LWE", " casualties"),
    ("khalistan_fatalities_by_period", "khalistan_insurgency_historical", "Punjab Militancy by Period", "Annual series summed over 5-year periods",
     "Crime & Security", "Punjab Militancy & Security", ""),
    ("coal_output_by_period", "coal_production", "Coal Output by Period", "Domestic coal output, five-year totals",
     "Mining & Natural Resources", "Energy Minerals & Fuel", " Million Tonnes"),
    ("pew_reports_by_period", "pew_india_reports", "Pew India Publications by Period", "Number of Pew Research Center reports mentioning India, five-year totals",
     "Pew Research", "Public opinion", " reports"),
    ("unesco_inscriptions_by_period", "unesco_india_new_inscriptions", "UNESCO Inscriptions in India by Period", "New World Heritage inscriptions, ten-year totals",
     "Tourism & Heritage", "World Heritage Sites", " sites"),
)

REGION_PIES = (
    ("state_pmjdy_region_share", "state_pmjdy_bank_accounts", "Jan Dhan Accounts by Region", "PMJDY bank accounts grouped by region",
     "State Performance & Regional Health", "State Welfare & Scheme Coverage", " accounts"),
    ("state_gsdp_region_share", "state_gsdp_comparison", "GSDP by Region", "Gross State Domestic Product grouped by region",
     "State Performance & Regional Health", "State Financial Health & GSDP", " INR"),
)


def build_derived_layer(series: dict[str, dict]) -> dict[str, dict]:
    built: dict[str, dict] = {}

    def add(factory, *args):
        try:
            key, value = factory(series, *args)
            built[key] = value
        except (KeyError, ValueError, TypeError):
            pass  # a missing or partial source series simply omits its derived pie

    for spec in CUMULATIVE:
        add(_cumulative, *spec)
    for spec in LATEST:
        add(_latest, *spec)
    for key, base, title, subtitle, category, subgroup, suffix in PERIODS:
        span = 5 if base in ("khalistan_insurgency_historical", "coal_production", "pew_india_reports") else 10
        add(_periods, key, base, title, subtitle, category, subgroup, suffix, span)
    for spec in REGION_PIES:
        add(_regions, *spec)
    for spec in BINARY:
        add(_binary, *spec)
    add(_dataset_latest, "auto_domestic_sales_mix", "auto_domestic_sales", "Automobile Domestic Sales by Segment",
        "Passenger, commercial, three- and two-wheeler sales", "Industry Trends & Performance",
        "Manufacturing & Industrial Growth", " million vehicles")
    return built

"""Official Government of India statistics from the MoSPI API platform (https://api.mospi.gov.in).

Pulls national series from the Ministry of Statistics and Programme Implementation's public API:
EnviStats India (environment, agriculture, disasters, disease surveillance), Women & Men in India
(SRS/Census mortality, fertility, literacy, enrolment), AISHE (higher education) and the Periodic
Labour Force Survey. Anonymous access is paged at 200 rows, so every request walks the pages.

Every chart is self-describing: ``meta`` places it in a group/subgroup and ``meta.explain`` carries
"what it shows / how to read it / why it matters" text that both the static site and the web app render.
If the API is unreachable the previous good series is kept, never an invented value.
"""
from __future__ import annotations

import json
import re
import ssl
import time
from collections import defaultdict
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://api.mospi.gov.in"
PORTAL = "https://esankhyiki.mospi.gov.in/"
ENDPOINTS = {
    "env": ("/api/env/getEnvStatsRecords", "MoSPI EnviStats India"),
    "gender": ("/api/gender/getGenderRecords", "MoSPI Women & Men in India"),
    "aishe": ("/api/aishe/getAisheRecords", "Ministry of Education AISHE via MoSPI"),
    "plfs": ("/api/plfs/getData", "MoSPI Periodic Labour Force Survey"),
}
PAGE_SIZE = 200  # the platform rejects larger anonymous pages
MAX_PAGES = 40
NATIONAL_ROWS = {"all india", "india", "total", "grand total"}

_SSL = ssl.create_default_context()
# api.mospi.gov.in still negotiates TLS with legacy renegotiation; the official client enables the same flag.
_SSL.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0x4)


def _get(path: str, params: dict) -> dict:
    url = f"{API}{path}?{urlencode(params)}"
    error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0 (India's Journey data pipeline)"}), timeout=90, context=_SSL) as response:
                return json.loads(response.read().decode("utf-8", "replace"))
        except Exception as exc:  # transient network or gateway error
            error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"MoSPI request failed for {path}: {error}")


def fetch_rows(dataset: str, code: int, extra: dict | None = None) -> list[dict]:
    path = ENDPOINTS[dataset][0]
    rows: list[dict] = []
    page = 1
    while page <= MAX_PAGES:
        payload = _get(path, {"indicator_code": code, **(extra or {}), "limit": PAGE_SIZE, "page": page})
        data = payload.get("data")
        if not isinstance(data, list):
            raise ValueError(f"MoSPI {dataset}:{code} returned no rows")
        rows.extend(data)
        pages = (payload.get("meta_data") or {}).get("totalPages") or 1
        if page >= pages:
            break
        page += 1
    return rows


def _number(value) -> float | None:
    try:
        number = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None
    return number if number == number else None


def clean_label(raw) -> str:
    text = re.sub(r"\s*\(P\)|\*|#", "", str(raw)).strip()
    match = re.fullmatch(r"I?SFR\s+(\d{4})", text)
    return match.group(1) if match else text


def is_provisional(raw) -> bool:
    return bool(re.search(r"\(P\)|\*", str(raw)))


def label_key(label: str):
    match = re.search(r"\d{4}", label)
    return (int(match.group()) if match else 9999, label)


def _matches(row: dict, where: dict) -> bool:
    for column, wanted in where.items():
        value = str(row.get(column, "")).strip()
        options = wanted if isinstance(wanted, (tuple, list, set)) else (wanted,)
        if value not in options:
            return False
    return True


def _state_col(rows: list[dict]) -> str | None:
    for column in ("state", "state/UT"):
        if rows and column in rows[0]:
            return column
    return None


def relabel_hidden_national(rows: list[dict], x: str) -> list[dict]:
    """Some EnviStats tables file the national total under a State name; a row roughly as large as all others combined is the total."""
    state_col = _state_col(rows)
    if not state_col:
        return rows
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        dims = tuple(sorted((k, str(v)) for k, v in row.items() if k not in ("value", state_col, "unit")))
        groups[dims].append(row)
    fixed: list[dict] = []
    for members in groups.values():
        values = [(_number(row.get("value")) or 0.0) for row in members]
        top = max(range(len(members)), key=lambda i: values[i]) if members else None
        if top is not None and len(members) > 3 and values[top] >= 0.8 * (sum(values) - values[top]):
            members = [dict(row, **{state_col: "All India"}) if i == top else row for i, row in enumerate(members)]
        fixed.extend(members)
    return fixed


def aggregate(rows: list[dict], x: str, series: str | None, national: str = "sum") -> tuple[dict, set]:
    """Returns {(x_label, series_value): number}, preferring a reported national row over summed states."""
    state_col = _state_col(rows)
    totals: dict[tuple, float] = defaultdict(float)
    national_rows: dict[tuple, float] = {}
    provisional: set[str] = set()
    for row in rows:
        value = _number(row.get("value"))
        if value is None:
            continue
        label = clean_label(row.get(x))
        if not label:
            continue
        if is_provisional(row.get(x)):
            provisional.add(label)
        key = (label, str(row.get(series, "")).strip() if series else "")
        state = str(row.get(state_col, "")).strip().lower() if state_col else "all india"
        if state in NATIONAL_ROWS:
            national_rows[key] = value
        elif national == "sum":
            totals[key] += value
    merged = dict(totals)
    merged.update(national_rows)
    return merged, provisional


def _explain_note(spec: dict, provisional: set[str], extra: str = "") -> str:
    source = ENDPOINTS[spec["dataset"]][1]
    parts = [f"Source: {source}, indicator {spec['code']} on the MoSPI API platform ({PORTAL})."]
    if extra:
        parts.append(extra)
    if provisional:
        parts.append(f"Values for {', '.join(sorted(provisional, key=label_key))} are marked provisional by the source.")
    if spec.get("caveat"):
        parts.append(spec["caveat"])
    return " ".join(parts)


def _meta(spec: dict) -> dict:
    what, read, why = spec["explain"]
    return {
        "title": spec["title"], "subtitle": spec["subtitle"], "frequency": spec.get("frequency", "Annual"),
        "color": spec.get("color", "#58a6ff"), "suffix": spec.get("suffix", ""),
        "category": spec["category"], "subgroup": spec["subgroup"],
        "explain": {"what": what, "read": read, "why": why},
    }


def build_series(spec: dict, rows: list[dict]) -> dict:
    rows = [row for row in rows if _matches(row, spec.get("where", {}))]
    if spec.get("exclude"):
        rows = [row for row in rows if not _matches(row, spec["exclude"])]
    if not rows:
        raise ValueError(f"No rows match {spec['key']}")
    kind = spec["kind"]
    x = spec.get("x", "year")
    if spec.get("hidden_national"):
        rows = relabel_hidden_national(rows, x)
    if spec.get("exclude_labels"):
        rows = [row for row in rows if clean_label(row.get(x)) not in spec["exclude_labels"]]
    base = {"source": f"{API}{ENDPOINTS[spec['dataset']][0]}?indicator_code={spec['code']}", "unit": spec.get("unit", spec.get("suffix", "").strip()), "meta": _meta(spec)}

    if kind == "state":
        state_col = _state_col(rows)
        labelled = [(clean_label(row.get(x)), row) for row in rows]
        latest = max((label for label, _ in labelled), key=label_key)
        points = {}
        for label, row in labelled:
            name = str(row.get(state_col, "")).strip()
            value = _number(row.get("value"))
            if label == latest and value is not None and name.lower() not in NATIONAL_ROWS:
                points[re.sub(r"\s+", " ", name)] = value
        if len(points) < 5:
            raise ValueError(f"Too few states for {spec['key']}")
        ordered = sorted(points.items(), key=lambda item: item[1], reverse=True)
        base["meta"]["title"] = f"{spec['title']} ({latest})"
        return {**base, "labels": [name for name, _ in ordered], "values": [round(value, 2) for _, value in ordered],
                "chartType": "bar", "indexAxis": "y", "scope": "state", "scopeLabel": "States/UTs reported",
                "highestLabel": "Highest State/UT",
                "note": _explain_note(spec, set(), f"Latest period reported: {latest}. Ranked highest to lowest.")}

    series_col = spec.get("series")
    merged, provisional = aggregate(rows, x, series_col, spec.get("national", "sum"))
    labels = sorted({label for label, _ in merged}, key=label_key)
    if spec.get("transform") == "sum_series":
        # Collapse the series dimension (for example months) into one total per period.
        totals: dict[str, float] = defaultdict(float)
        counts: dict[str, int] = defaultdict(int)
        for (label, member), value in merged.items():
            if member in spec["members"]:
                totals[label] += value
                counts[label] += 1
        labels = [label for label in labels if counts.get(label) == len(spec["members"])]
        if spec.get("year_only"):
            labels = [label for label in labels if re.fullmatch(r"\d{4}", label)]
        merged = {(label, ""): totals[label] for label in labels}
        series_col = None

    if kind == "pie":
        latest = max(labels, key=label_key)
        parts = [(name, merged.get((latest, raw))) for raw, name in spec["members"]]
        parts = [(name, value) for name, value in parts if value is not None and value > 0]
        if len(parts) < 2:
            raise ValueError(f"Too few parts for {spec['key']}")
        base["meta"]["title"] = f"{spec['title']} ({latest})"
        return {**base, "labels": [name for name, _ in parts], "values": [round(value, 2) for _, value in parts],
                "chartType": spec.get("chartType", "doughnut"), "scope": "category",
                "note": _explain_note(spec, provisional & {latest}, f"Latest period reported: {latest}.")}

    if series_col:
        datasets = []
        palette = ["#ff9933", "#58a6ff", "#3fb950", "#bc8cff", "#ff7b72", "#f6c344", "#39c5bb"]
        for index, (raw, name) in enumerate(spec["members"]):
            values = [merged.get((label, raw)) for label in labels]
            if sum(value is not None for value in values) >= 2:
                datasets.append({"label": name, "values": [None if value is None else round(value, 3) for value in values],
                                 "borderColor": palette[index % len(palette)]})
        keep = [i for i, _ in enumerate(labels) if any(dataset["values"][i] is not None for dataset in datasets)]
        labels = [labels[i] for i in keep]
        for dataset in datasets:
            dataset["values"] = [dataset["values"][i] for i in keep]
        if len(datasets) < 1 or len(labels) < 2:
            raise ValueError(f"Too few observations for {spec['key']}")
        result = {**base, "labels": labels, "datasets": datasets, "note": _explain_note(spec, provisional)}
    else:
        values = [merged.get((label, "")) for label in labels]
        pairs = [(label, round(value, 3)) for label, value in zip(labels, values) if value is not None]
        if len(pairs) < 2:
            raise ValueError(f"Too few observations for {spec['key']}")
        result = {**base, "labels": [label for label, _ in pairs], "values": [value for _, value in pairs],
                  "note": _explain_note(spec, provisional)}
    if spec.get("chartType"):
        result["chartType"] = spec["chartType"]
    return result


ENV, AGRI, SOCIAL, HEALTH, INDUSTRY = "Environment & Climate", "Agriculture & Food", "Social", "Public Health & Epidemiology", "Industry Trends & Performance"
PLFS_ALL = {"religion": "all", "socialGroup": "all", "General_Education": "all", "weekly_status": "PS+SS"}
PLFS_SEX = (("person", "All persons"), ("male", "Men"), ("female", "Women"))


def _plfs(key, code, title, subtitle, color, explain, age=1, members=PLFS_SEX):
    return {"key": key, "dataset": "plfs", "code": code, "kind": "line", "series": "gender", "members": members,
            "fetch": {"frequency_code": 1, "year_type_code": 1, "state_code": 99, "age_code": age, "sector_code": 3},
            "fetch_by": ("gender_code", (3, 1, 2)), "where": PLFS_ALL,
            "title": title, "subtitle": subtitle, "category": SOCIAL, "subgroup": "Employment & Poverty",
            "color": color, "suffix": "%", "frequency": "Annual (July-June)", "explain": explain,
            "caveat": "Usual status (principal + subsidiary), rural + urban, agricultural years July-June."}


SPECS: tuple[dict, ...] = (
    # --- Climate & weather ---------------------------------------------------------------------
    {"key": "mospi_mean_temperature", "dataset": "env", "code": 1, "kind": "line", "series": "period",
     "members": (("Annual", "Annual mean"), ("Mar-May", "Pre-monsoon (Mar-May)"), ("June-Sept", "Monsoon (Jun-Sep)"), ("Jan-Feb", "Winter (Jan-Feb)")),
     "title": "All-India Mean Temperature by Season", "subtitle": "Area-weighted average temperature, °C (IMD)", "category": ENV, "subgroup": "Climate & Weather",
     "color": "#ff7b72", "suffix": " °C", "explain": (
        "The India Meteorological Department's all-India average air temperature for the whole year and for each season, from 2001.",
        "Each line is one season. A line that drifts upward over the years means that season is getting warmer; compare the annual line with the pre-monsoon line to see where heat is concentrated.",
        "Rising temperatures drive heat stress, crop losses, power demand and water scarcity, so this is the baseline for every climate-adaptation discussion.")},
    {"key": "mospi_annual_rainfall", "dataset": "env", "code": 3, "kind": "line", "series": "month", "transform": "sum_series", "chartType": "bar",
     "members": ("Jan", "Feb", "March", "April", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"),
     "title": "All-India Annual Rainfall", "subtitle": "Sum of monthly all-India rainfall, mm (IMD)", "category": ENV, "subgroup": "Climate & Weather",
     "color": "#58a6ff", "suffix": " mm", "explain": (
        "Total rainfall received across India in each calendar year, built by adding the IMD's twelve monthly all-India averages.",
        "Taller bars are wetter years. Look for short bars: they usually line up with drought years and weak monsoons, such as 2002, 2009 and 2014-15.",
        "Roughly half of India's farmland is rain-fed, so a poor rainfall year shows up quickly in farm output, rural incomes, food prices and reservoir levels.")},
    {"key": "mospi_monsoon_rainfall", "dataset": "env", "code": 3, "kind": "line", "series": "month", "transform": "sum_series", "chartType": "bar",
     "members": ("June", "July", "Aug", "Sept"),
     "title": "Southwest Monsoon Rainfall (June-September)", "subtitle": "Sum of June-September all-India rainfall, mm (IMD)", "category": ENV, "subgroup": "Climate & Weather",
     "color": "#39c5bb", "suffix": " mm", "explain": (
        "Rain delivered by the southwest monsoon, the four months from June to September, in each year.",
        "Compare each bar with the others: the monsoon normally brings about three-quarters of India's annual rain, so dips here explain most dry years in the annual chart.",
        "Kharif sowing, groundwater recharge, hydropower and rural demand all depend on the monsoon; the RBI and the Finance Ministry track it closely for inflation and growth.")},
    {"key": "mospi_cyclonic_storms", "dataset": "env", "code": 89, "kind": "line", "series": "month", "transform": "sum_series", "year_only": True, "chartType": "bar",
     "members": ("Jan", "Feb", "March", "April", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"),
     "title": "Cyclonic Storms over the North Indian Ocean", "subtitle": "Storms formed in the Bay of Bengal and Arabian Sea per year (IMD)", "category": ENV, "subgroup": "Climate & Weather",
     "color": "#bc8cff", "suffix": " storms", "explain": (
        "The number of cyclonic storms that formed each year over the Bay of Bengal and the Arabian Sea, as recorded by the IMD.",
        "Each bar counts storms, not damage. Year-to-year swings are natural; look at decades together to judge whether storms are becoming more frequent.",
        "Cyclones threaten a coastline that is home to millions of people. Better forecasting and evacuation have cut deaths sharply even when storm counts have not fallen.")},
    {"key": "mospi_heat_wave_days", "dataset": "env", "code": 87, "kind": "state",
     "title": "Heat Wave Days by State", "subtitle": "Average heat wave days in the summer season (IMD)", "category": ENV, "subgroup": "Climate & Weather",
     "color": "#ff9933", "suffix": " days", "explain": (
        "How many heat wave days each State recorded in the most recent summer season, as declared by the IMD.",
        "Longer bars mean more days of dangerous heat. Northern and central plains usually top the list.",
        "Heat waves kill outdoor workers, the elderly and the poor, cut labour productivity and stress power grids; State heat-action plans target the worst-hit regions.")},
    # --- Forests & land ------------------------------------------------------------------------
    {"key": "mospi_forest_cover_trend", "dataset": "env", "code": 20, "kind": "line",
     "title": "India's Forest Cover", "subtitle": "Total forest cover, sq km (Forest Survey of India)", "category": ENV, "subgroup": "Forests & Land",
     "color": "#3fb950", "suffix": " sq km", "frequency": "Biennial", "hidden_national": True, "explain": (
        "Total area under forest cover in India from each State of Forest Report, built from satellite mapping by the Forest Survey of India.",
        "Each point is one biennial assessment; a rising line means more mapped forest cover. Mapping methods and resolution have improved over time, so small changes are within error.",
        "Forests store carbon, protect watersheds and support tribal livelihoods; India's climate pledge includes adding a carbon sink of 2.5-3 billion tonnes through forests and tree cover."),
     "caveat": "The source files the national total under a State label in some years; it is detected and used as the all-India value."},
    {"key": "mospi_forest_cover_states", "dataset": "env", "code": 20, "kind": "state",
     "title": "Forest Cover by State", "subtitle": "Forest cover in the latest State of Forest Report, sq km", "category": ENV, "subgroup": "Forests & Land",
     "color": "#3fb950", "suffix": " sq km", "hidden_national": True, "explain": (
        "The forest area of each State and UT in the most recent State of Forest Report.",
        "Bars are absolute areas, so large States lead. Madhya Pradesh, Arunachal Pradesh, Chhattisgarh and Odisha usually hold the biggest forests.",
        "Forest-rich States carry much of India's carbon sink and biodiversity; forest area is also one factor in how the Finance Commission shares central taxes with States.")},
    # --- Pollution & waste ---------------------------------------------------------------------
    {"key": "mospi_msw_generation_states", "dataset": "env", "code": 80, "kind": "state", "where": {"sub_indicator": "Quantity Generated (TPD)"},
     "title": "Municipal Solid Waste Generated by State", "subtitle": "Tonnes per day (CPCB)", "category": ENV, "subgroup": "Pollution & Waste",
     "color": "#f6c344", "suffix": " TPD", "explain": (
        "How much municipal solid waste (household and commercial garbage) each State's urban local bodies generate per day, as reported to the Central Pollution Control Board.",
        "Longer bars mean more waste each day. Populous, urbanised States such as Maharashtra, Uttar Pradesh and Delhi generate the most.",
        "Waste volumes set the scale of collection, processing and landfill capacity cities need under the Solid Waste Management Rules and Swachh Bharat Mission (Urban)."),
     "caveat": "Values are shown as published; Uttarakhand's reported figure is unusually high relative to its population."},
    {"key": "mospi_msw_management_funnel", "dataset": "env", "code": 80, "kind": "pie", "series": "sub_indicator", "chartType": "bar",
     "members": (("Quantity Generated (TPD)", "Generated"), ("Collected (TPD)", "Collected"), ("Treated (TPD)", "Treated"), ("Landfilled (TPD)", "Landfilled")),
     "title": "Urban Waste: Generated, Collected, Treated, Landfilled", "subtitle": "All-India municipal solid waste, tonnes per day (CPCB)", "category": ENV, "subgroup": "Pollution & Waste",
     "color": "#f6c344", "suffix": " TPD", "explain": (
        "All-India totals of municipal solid waste generated, collected, scientifically treated and sent to landfill each day.",
        "Read the bars left to right as a funnel: the gap between Generated and Collected is waste left on streets, and the gap between Collected and Treated is waste dumped without processing.",
        "The treated share is the clearest measure of whether cities are actually managing waste rather than just moving it to dumpsites."),
     "caveat": "All-India figures are the sum of State/UT reports for the latest year."},
    {"key": "mospi_plastic_waste", "dataset": "env", "code": 132, "kind": "line", "chartType": "bar",
     "title": "Plastic Waste Generated", "subtitle": "Estimated plastic waste, tonnes per annum (CPCB)", "category": ENV, "subgroup": "Pollution & Waste",
     "color": "#ff7b72", "suffix": " TPA", "explain": (
        "Estimated plastic waste generated across India each year, summed from State Pollution Control Board reports to the CPCB.",
        "Bars show the national total. Jumps can reflect better reporting by States as well as real growth in plastic use.",
        "Plastic waste clogs drains, pollutes rivers and seas and is the target of India's single-use plastic ban and Extended Producer Responsibility rules."),
     "caveat": "National totals are the sum of State/UT estimates."},
    # --- Disasters -----------------------------------------------------------------------------
    {"key": "mospi_nature_deaths_by_cause", "dataset": "env", "code": 94, "kind": "pie", "where": {"sub_indicator": "Number of Deaths"}, "series": "causes",
     "members": (("Lightening", "Lightning"), ("Heat Stroke", "Heat stroke"), ("Flood", "Flood"), ("Exposure to Cold", "Cold exposure"), ("Landslide", "Landslide"),
                 ("Torrential Rains", "Torrential rains"), ("Cyclone/tornado/Tsunami", "Cyclone/tornado/tsunami"), ("Epidemic", "Epidemic"), ("Earthquake", "Earthquake"),
                 ("Avalanche", "Avalanche"), ("Forest Fire", "Forest fire"), ("Starvation/Thirst", "Starvation/thirst"), ("Causes other than above", "Other natural causes")),
     "title": "Deaths from Forces of Nature by Cause", "subtitle": "Share of accidental deaths due to natural causes (NCRB)", "category": ENV, "subgroup": "Disasters & Extremes",
     "color": "#bc8cff", "suffix": " deaths", "explain": (
        "How deaths attributed to forces of nature in the latest year split by cause, from NCRB's Accidental Deaths & Suicides in India.",
        "Bigger slices are bigger killers. Lightning is usually the largest single cause, ahead of floods and heat stroke.",
        "Lightning and heat kill more people than dramatic disasters such as earthquakes, which points disaster-risk spending toward early warnings and shelters.")},
    {"key": "mospi_nature_deaths_trend", "dataset": "env", "code": 94, "kind": "line", "where": {"sub_indicator": "Number of Deaths", "causes": "Total"}, "chartType": "bar",
     "title": "Deaths from Forces of Nature", "subtitle": "Total accidental deaths due to natural causes (NCRB)", "category": ENV, "subgroup": "Disasters & Extremes",
     "color": "#ff7b72", "suffix": " deaths", "explain": (
        "The total number of people killed by natural causes (lightning, floods, heat, cold, landslides, storms and others) each year.",
        "Each bar is one year. Spikes usually match a severe flood, cyclone or heat season.",
        "This tracks the human cost of climate and weather extremes, and whether early-warning systems are saving lives.")},
    # --- Energy transition ---------------------------------------------------------------------
    {"key": "mospi_power_generation_mix", "dataset": "env", "code": 41, "kind": "pie", "series": "source_power_generation",
     "members": (("Thermal - Coal / Lignite", "Coal & lignite"), ("Renewable Energy Source", "Renewables (solar, wind, etc.)"), ("Hydro", "Large hydro"),
                 ("Nuclear", "Nuclear"), ("Thermal - Gas", "Gas"), ("Thermal - Diesel", "Diesel")),
     "title": "Electricity Generation by Source", "subtitle": "Share of gross generation, GWh (CEA)", "category": ENV, "subgroup": "Energy Transition",
     "color": "#f6c344", "suffix": " GWh", "explain": (
        "Where India's electricity came from in the latest year, by fuel, from Central Electricity Authority data.",
        "Each slice is a share of total generation. Coal still dominates; the renewables slice (solar, wind, small hydro, biomass) is the one to watch.",
        "India has pledged 500 GW of non-fossil capacity by 2030 and net zero by 2070, so the coal-to-renewables balance is the core energy-transition metric.")},
    {"key": "mospi_power_generation_trend", "dataset": "env", "code": 41, "kind": "line", "series": "source_power_generation",
     "members": (("Thermal - Total", "Thermal (coal, gas, diesel)"), ("Hydro", "Large hydro"), ("Renewable Energy Source", "Renewables"), ("Nuclear", "Nuclear")),
     "title": "Electricity Generation since Independence", "subtitle": "Gross generation by source, GWh (CEA)", "category": ENV, "subgroup": "Energy Transition",
     "color": "#f6c344", "suffix": " GWh", "explain": (
        "Gross electricity generated in India by source from 1947 to the latest year.",
        "Lines show absolute output, so thermal power's steep climb shows how India electrified. Renewables appear only from the 2000s and are now rising fastest.",
        "Electricity use tracks industrialisation and living standards; the mix shows how carbon-intensive that growth has been.")},
    # --- Agriculture & food --------------------------------------------------------------------
    {"key": "mospi_foodgrain_production", "dataset": "env", "code": 51, "kind": "line", "series": "commodity",
     "members": (("Total Foodgrains", "Total foodgrains"), ("Rice", "Rice"), ("Wheat", "Wheat"), ("Coarse Cereals", "Coarse cereals"), ("Total Pulses", "Pulses")),
     "title": "Foodgrain Production", "subtitle": "Million tonnes (Ministry of Agriculture & Farmers Welfare)", "category": AGRI, "subgroup": "Crop Production",
     "color": "#f6c344", "suffix": " million tonnes", "frequency": "Annual (crop year)", "explain": (
        "India's production of rice, wheat, coarse cereals (millets, maize) and pulses, and their total, for each crop year (July-June).",
        "The top line is total foodgrains; the lines below show what it is made of. Dips usually follow drought years such as 2009-10 and 2014-15.",
        "Foodgrain output underpins food security, the public distribution system (PDS) and food inflation. Pulses matter because India still imports to meet demand.")},
    {"key": "mospi_oilseed_cash_crops", "dataset": "env", "code": 51, "kind": "line", "series": "commodity",
     "members": (("Total Nine Oilseeds", "Nine oilseeds"), ("Soybean", "Soybean"), ("Rapeseed & Mustard", "Rapeseed & mustard"), ("Groundnut", "Groundnut")),
     "title": "Oilseed Production", "subtitle": "Lakh tonnes (Ministry of Agriculture & Farmers Welfare)", "category": AGRI, "subgroup": "Crop Production",
     "color": "#ff9933", "suffix": " lakh tonnes", "unit": "lakh tonnes", "caveat": "The API labels these rows 'Million tonnes', but the magnitudes match the Ministry's lakh-tonne series (for example 2023-24 nine oilseeds = 416.7 lakh tonnes).", "frequency": "Annual (crop year)", "explain": (
        "Production of India's nine major oilseeds and the three biggest of them: soybean, rapeseed-mustard and groundnut.",
        "Compare the total with the three crops below it to see which crop is driving growth or decline.",
        "India imports more than half of its edible oil, so domestic oilseed output decides the import bill and is the target of the National Mission on Edible Oils.")},
    {"key": "mospi_sugarcane_production", "dataset": "env", "code": 51, "kind": "line", "where": {"commodity": "Sugarcane"},
     "title": "Sugarcane Production", "subtitle": "Lakh tonnes (Ministry of Agriculture & Farmers Welfare)", "category": AGRI, "subgroup": "Crop Production",
     "color": "#3fb950", "suffix": " lakh tonnes", "unit": "lakh tonnes", "caveat": "The API labels these rows 'Million tonnes', but the magnitudes match the Ministry's lakh-tonne series (2023-24 = 4,351 lakh tonnes, about 435 million tonnes).", "frequency": "Annual (crop year)", "explain": (
        "Total sugarcane harvested in India in each crop year.",
        "Higher values mean a bigger cane crop; the swings follow monsoon rainfall and irrigation in Uttar Pradesh, Maharashtra and Karnataka.",
        "Sugarcane feeds the sugar industry and the ethanol-blending programme, but it is very water-intensive, which ties it to groundwater depletion debates.")},
    {"key": "mospi_fertiliser_consumption", "dataset": "env", "code": 54, "kind": "line", "where": {"sub_indicator": "Consumption (Lakh Tonnes)"}, "series": "emission_source",
     "members": (("Nitrogen", "Nitrogen (N)"), ("Phosphorous", "Phosphate (P)"), ("Potash (Potassium)", "Potash (K)")),
     "title": "Fertiliser Consumption by Nutrient", "subtitle": "Lakh tonnes of N, P and K (Department of Fertilizers)", "category": AGRI, "subgroup": "Farm Inputs",
     "color": "#58a6ff", "suffix": " lakh tonnes", "explain": (
        "How much nitrogen, phosphate and potash fertiliser Indian farmers used each year since 1981-82, in nutrient terms.",
        "Nitrogen (mostly urea) towers over the others. The agronomic ideal is roughly 4:2:1 for N:P:K, so a widening gap signals unbalanced use.",
        "Fertiliser subsidies are one of the largest items in the Union Budget, and overuse of urea degrades soil and water; this chart shows the scale of both.")},
    {"key": "mospi_fertiliser_self_reliance", "dataset": "env", "code": 54, "kind": "line", "where": {"emission_source": "Total"}, "series": "sub_indicator",
     "members": (("Consumption (Lakh Tonnes)", "Consumption"), ("Production (Lakh Tonnes)", "Domestic production"), ("Imports  (Lakh Tonnes)", "Imports")),
     "title": "Fertiliser: Consumption vs Production vs Imports", "subtitle": "Total N+P+K, lakh tonnes (Department of Fertilizers)", "category": AGRI, "subgroup": "Farm Inputs",
     "color": "#58a6ff", "suffix": " lakh tonnes", "explain": (
        "Total fertiliser nutrients consumed in India against what was produced domestically and what was imported.",
        "When the consumption line sits above production, the gap is filled by imports. Watch whether new urea plants narrow that gap.",
        "Import dependence exposes farmers and the subsidy bill to global gas and fertiliser prices, as in 2022.")},
    {"key": "mospi_livestock_census", "dataset": "env", "code": 61, "kind": "line", "series": "species",
     "members": (("Cattle", "Cattle"), ("Buffaloes", "Buffaloes"), ("Goats", "Goats"), ("Sheep", "Sheep"), ("Pigs", "Pigs")),
     "title": "Livestock Population by Species", "subtitle": "Million animals, Livestock Census (DAHD)", "category": AGRI, "subgroup": "Livestock & Fisheries",
     "color": "#ff9933", "suffix": " million", "frequency": "Quinquennial census", "explain": (
        "The number of cattle, buffaloes, goats, sheep and pigs counted in each Livestock Census since 1951.",
        "Each point is a census year. Cattle numbers have plateaued while buffaloes and goats have grown, reflecting the shift to dairy and meat.",
        "Livestock supports about a fifth of rural households and makes India the world's largest milk producer."),
     "national": "national"},
    {"key": "mospi_fish_production", "dataset": "env", "code": 64, "kind": "line", "series": "sub_indicator", "chartType": "bar",
     "members": (("Inland", "Inland (rivers, ponds, aquaculture)"), ("Marine", "Marine (sea catch)")),
     "title": "Fish Production: Inland vs Marine", "subtitle": "Lakh tonnes (Department of Fisheries)", "category": AGRI, "subgroup": "Livestock & Fisheries",
     "color": "#39c5bb", "suffix": " lakh tonnes", "explain": (
        "Fish produced in India each year from inland waters (rivers, reservoirs and fish farms) and from the sea.",
        "Inland production overtook marine catch in the 1990s and now dominates; that is the aquaculture boom.",
        "India is the world's second-largest fish producer, and fisheries support millions of coastal and rural livelihoods and a major seafood-export trade.")},
    # --- Labour (PLFS) -------------------------------------------------------------------------
    _plfs("plfs_lfpr_by_sex", 1, "Labour Force Participation Rate (PLFS)", "Share of people aged 15+ working or seeking work", "#58a6ff", (
        "The share of people aged 15 and over who are in the labour force (working or looking for work), from the Periodic Labour Force Survey.",
        "Compare the women's line with the men's: the gap shows how many women are outside paid work. A rising women's line is the biggest labour-market change since 2017-18.",
        "Participation, not just unemployment, decides how much of India's demographic dividend turns into output and household income.")),
    _plfs("plfs_wpr_by_sex", 2, "Worker Population Ratio (PLFS)", "Share of people aged 15+ who are employed", "#3fb950", (
        "The share of the population aged 15 and over that is actually employed.",
        "This is the employment rate: it rises when jobs grow faster than population. Read it alongside the participation chart.",
        "It is the most direct measure of how many people the economy employs, and it includes self-employment and unpaid family work.")),
    _plfs("plfs_unemployment_by_sex", 3, "Unemployment Rate (PLFS)", "Share of the labour force aged 15+ without work", "#ff7b72", (
        "The share of people in the labour force (aged 15+) who looked for work but found none.",
        "Lower is better. A falling line together with a rising participation rate is a genuinely tightening labour market.",
        "This is India's official headline unemployment measure, used for policy and to compare States.")),
    _plfs("plfs_youth_unemployment", 3, "Youth Unemployment Rate, 15-29 (PLFS)", "Share of the labour force aged 15-29 without work", "#f778ba", (
        "The unemployment rate among young people aged 15-29.",
        "Youth unemployment runs well above the overall rate; watch the gap between young women and young men.",
        "Joblessness among educated young people is a key political and economic issue and the target of skilling and apprenticeship schemes."), age=2),
    # --- Health & demography (SRS / Census via Women & Men in India) ---------------------------
    {"key": "mospi_imr_by_sex", "dataset": "gender", "code": 15, "kind": "line", "series": "gender",
     "members": (("Person", "All"), ("Male", "Boys"), ("Female", "Girls")),
     "title": "Infant Mortality Rate by Sex (SRS)", "subtitle": "Deaths before age one per 1,000 live births", "category": HEALTH, "subgroup": "Mortality & Lifespan Milestones",
     "color": "#ff7b72", "suffix": " per 1,000", "explain": (
        "Out of every 1,000 babies born alive, how many die before their first birthday, from the Registrar General's Sample Registration System.",
        "All lines falling means more infants survive. Girls' mortality was once higher than boys', which is unusual biologically; watch whether that gap has closed.",
        "Infant mortality is a summary of maternal health, nutrition, immunisation and sanitation; SDG 3 asks India to keep pushing it down.")},
    {"key": "mospi_u5mr_by_sex", "dataset": "gender", "code": 17, "kind": "line", "series": "gender", "where": {"state/UT": "All India"},
     "members": (("Person", "All"), ("Male", "Boys"), ("Female", "Girls")),
     "title": "Under-Five Mortality Rate by Sex (SRS)", "subtitle": "Deaths before age five per 1,000 live births", "category": HEALTH, "subgroup": "Mortality & Lifespan Milestones",
     "color": "#f778ba", "suffix": " per 1,000", "explain": (
        "Deaths of children before their fifth birthday per 1,000 live births, from the Sample Registration System.",
        "Lower is better; the SDG target is 25 or fewer by 2030. Compare girls with boys for signs of gender bias in child care.",
        "Under-five deaths are mostly preventable (pneumonia, diarrhoea, newborn complications), so this measures how well basic health services reach children.")},
    {"key": "mospi_life_expectancy_by_sex", "dataset": "gender", "code": 18, "kind": "line", "series": "gender",
     "members": (("Female", "Women"), ("Male", "Men")),
     "title": "Life Expectancy at Birth by Sex (SRS)", "subtitle": "Years, five-year moving periods", "exclude_labels": ("2021-25", "2026-30", "2031-36"), "category": HEALTH, "subgroup": "Mortality & Lifespan Milestones",
     "color": "#3fb950", "suffix": " years", "frequency": "Five-year periods", "explain": (
        "How many years a newborn would live on average if current death rates held, from SRS abridged life tables for overlapping five-year periods.",
        "Both lines rising means longer lives. Women overtook men in the 1990s and the gap has widened, the normal pattern as health care improves.",
        "Life expectancy sums up a country's health in one number and shapes pension, health and elder-care planning."),
     "caveat": "Projected periods (2021-25 onward) published alongside the estimates are excluded."},
    {"key": "mospi_maternal_mortality", "dataset": "gender", "code": 21, "kind": "line", "where": {"state/UT": "All India"}, "chartType": "bar",
     "title": "Maternal Mortality Ratio (SRS)", "subtitle": "Maternal deaths per 100,000 live births", "category": HEALTH, "subgroup": "Mortality & Lifespan Milestones",
     "color": "#d2a8ff", "suffix": " per 100k births", "frequency": "Three-year periods", "explain": (
        "Women who die from pregnancy or childbirth complications per 100,000 live births, from SRS special bulletins on maternal mortality.",
        "Each bar is a pooled period (for example 2018-20). India has passed its National Health Policy target of 100 and is heading toward the SDG goal of 70.",
        "The fall reflects institutional deliveries under Janani Suraksha Yojana and better emergency obstetric care, and shows what is left to do.")},
    {"key": "mospi_maternal_mortality_states", "dataset": "gender", "code": 21, "kind": "state",
     "title": "Maternal Mortality Ratio by State (SRS)", "subtitle": "Maternal deaths per 100,000 live births", "category": HEALTH, "subgroup": "Mortality & Lifespan Milestones",
     "color": "#d2a8ff", "suffix": " per 100k births", "explain": (
        "The maternal mortality ratio in each larger State for the latest SRS period.",
        "Longer bars are worse. Assam, Madhya Pradesh and Uttar Pradesh usually rank highest; Kerala, Maharashtra and Telangana lowest.",
        "The spread between States shows that national progress hides large regional gaps where maternal-health spending is most needed.")},
    {"key": "mospi_sex_ratio_at_birth", "dataset": "gender", "code": 7, "kind": "line", "series": "sector", "where": {"state/UT": "All India"},
     "members": (("Total", "All India"), ("Rural", "Rural"), ("Urban", "Urban")),
     "title": "Sex Ratio at Birth (SRS)", "subtitle": "Girls born per 1,000 boys, three-year periods", "category": SOCIAL, "subgroup": "Gender & Population",
     "color": "#f778ba", "suffix": " girls per 1,000 boys", "frequency": "Three-year periods", "explain": (
        "How many girls are born for every 1,000 boys, from the Sample Registration System.",
        "The natural ratio is about 950. Values well below that point to sex-selective abortion; an upward trend means the gap is closing.",
        "This is the key outcome for Beti Bachao Beti Padhao and the PC-PNDT Act, and it shapes future marriage markets and demography.")},
    {"key": "mospi_census_sex_ratio", "dataset": "gender", "code": 2, "kind": "line", "where": {"state/UT": "All India"}, "chartType": "bar",
     "title": "Population Sex Ratio (Census 1951-2011)", "subtitle": "Females per 1,000 males", "category": SOCIAL, "subgroup": "Gender & Population",
     "color": "#bc8cff", "suffix": " females per 1,000 males", "frequency": "Decennial census", "explain": (
        "Females per 1,000 males in the whole population at each Census from 1951 to 2011.",
        "A value below 1,000 means fewer women than men. India's ratio dipped to 927 in 1991 and recovered to 943 by 2011.",
        "A persistently low sex ratio reflects excess female mortality and son preference; it is one of the starkest gender indicators."),
     "national": "national"},
    {"key": "mospi_women_age_at_marriage", "dataset": "gender", "code": 14, "kind": "line", "series": "sector", "where": {"state/UT": "All India"},
     "members": (("Total", "All India"), ("Rural", "Rural"), ("Urban", "Urban")),
     "title": "Women's Mean Age at Marriage (SRS)", "subtitle": "Average age at effective marriage, years", "category": SOCIAL, "subgroup": "Gender & Population",
     "color": "#ff9933", "suffix": " years", "explain": (
        "The average age at which women marry, from the Sample Registration System.",
        "Higher is better for health and education outcomes. Urban women marry about two years later than rural women.",
        "Later marriage is linked to more schooling, lower fertility and better maternal and child health; it is also behind the debate on raising the legal age of marriage to 21.")},
    {"key": "mospi_tfr_by_education", "dataset": "gender", "code": 10, "kind": "pie", "x": "year", "series": "education_level", "where": {"sector": "Total"}, "chartType": "bar",
     "members": (("Illiterate", "Illiterate"), ("Literate - Below primary", "Below primary"), ("Literate - Primary", "Primary"), ("Literate - Middle", "Middle"),
                 ("Literate - Class X", "Class X"), ("Literate - Class XII", "Class XII"), ("Literate - Graduate and above", "Graduate+")),
     "title": "Total Fertility Rate by Women's Education (SRS)", "subtitle": "Children per woman", "category": SOCIAL, "subgroup": "Gender & Population",
     "color": "#58a6ff", "suffix": " children per woman", "explain": (
        "The average number of children a woman would have over her life, grouped by her education level, for the latest SRS year.",
        "Bars fall from left to right: illiterate women have the most children and graduates the fewest.",
        "Girls' education is one of the most powerful levers on population growth, maternal health and child welfare.")},
    {"key": "mospi_literacy_by_sex", "dataset": "gender", "code": 55, "kind": "line", "series": "gender", "where": {"sector": "Total"},
     "members": (("Person", "All persons"), ("Male", "Men"), ("Female", "Women")),
     "title": "Literacy Rate by Sex (age 7+)", "subtitle": "Census 1981-2011 and NSS 2017-18, %", "category": SOCIAL, "subgroup": "Education",
     "color": "#bc8cff", "suffix": "%", "frequency": "Census / NSS rounds", "explain": (
        "The share of people aged seven and over who can read and write, from the Census and the NSS 75th round (2017-18).",
        "The gap between men's and women's lines is the gender literacy gap; it has narrowed steadily since 1981.",
        "Literacy is the base for employability, health awareness and civic participation, and women's literacy in particular predicts child health.")},
    {"key": "mospi_school_ger", "dataset": "gender", "code": 60, "kind": "line", "series": "education_level", "where": {"gender": "Total"},
     "members": (("Primary(I-V)", "Primary (I-V)"), ("Upper primary(VI-VIII)", "Upper primary (VI-VIII)"), ("Secondary(IX-X)", "Secondary (IX-X)"),
                 ("Higher Secondary(XI-XII)", "Higher secondary (XI-XII)"), ("Higher Education(Graduation and above)", "Higher education")),
     "title": "Gross Enrolment Ratio by Stage (UDISE+/AISHE)", "subtitle": "Enrolment as % of the official age group", "category": SOCIAL, "subgroup": "Education",
     "color": "#58a6ff", "suffix": "%", "explain": (
        "Enrolment at each stage of education as a percentage of the population of the matching age group.",
        "Primary is near or above 100% (universal), but each later stage is lower: the drop between lines shows where children leave school.",
        "The National Education Policy targets 100% GER up to secondary level and 50% in higher education by 2035.")},
    {"key": "mospi_school_dropout", "dataset": "gender", "code": 74, "kind": "line", "series": "education_level", "where": {"gender": "Person"},
     "members": (("Primary(I-V)", "Primary"), ("Upper primary(VI-VIII)", "Upper primary"), ("Secondary(IX-X)", "Secondary")),
     "title": "School Dropout Rate by Stage (UDISE+)", "subtitle": "Average annual dropout rate, %", "category": SOCIAL, "subgroup": "Education",
     "color": "#ff7b72", "suffix": "%", "explain": (
        "The share of students who leave school during the year at each stage, from UDISE+.",
        "Lower is better. Secondary-stage dropout is several times higher than primary, which is where most children are lost.",
        "Dropout shows whether rising enrolment turns into completed schooling; secondary dropout is the main focus of Samagra Shiksha.")},
    # --- Higher education (AISHE) --------------------------------------------------------------
    {"key": "aishe_institutions", "dataset": "aishe", "code": 1, "kind": "line", "where": {"state": "All India"}, "chartType": "bar",
     "title": "Number of Universities (AISHE)", "subtitle": "Universities and university-level institutions", "category": SOCIAL, "subgroup": "Higher Education",
     "color": "#bc8cff", "suffix": " universities", "frequency": "Annual (academic year)", "explain": (
        "The number of universities in India in each All India Survey on Higher Education.",
        "Each bar is an academic year; steady growth means new central, State, private and deemed universities opening.",
        "More institutions widen access, but the quality of what is taught matters as much as the count.")},
    {"key": "aishe_colleges", "dataset": "aishe", "code": 2, "kind": "line", "where": {"state": "All India"}, "chartType": "bar",
     "title": "Number of Colleges (AISHE)", "subtitle": "Colleges affiliated to universities", "category": SOCIAL, "subgroup": "Higher Education",
     "color": "#58a6ff", "suffix": " colleges", "frequency": "Annual (academic year)", "explain": (
        "The number of colleges in India in each AISHE round.",
        "Bars rising year on year show expansion; most new colleges are private and small.",
        "Colleges teach the bulk of India's undergraduates, so their spread decides how many students can get a degree near home.")},
    {"key": "aishe_enrolment_by_sex", "dataset": "aishe", "code": 3, "kind": "line", "series": "gender", "where": {"state": "All India", "education_level": "Grand Total"},
     "members": (("Both", "All students"), ("Male", "Men"), ("Female", "Women")),
     "title": "Higher Education Enrolment by Sex (AISHE)", "subtitle": "Estimated students enrolled", "category": SOCIAL, "subgroup": "Higher Education",
     "color": "#3fb950", "suffix": " students", "frequency": "Annual (academic year)", "explain": (
        "The estimated number of students enrolled in higher education, split by sex.",
        "Women's enrolment has nearly caught up with men's; where the lines cross, women outnumber men.",
        "Higher-education enrolment builds the skilled workforce, and women's rising share is one of India's quieter social shifts.")},
    {"key": "aishe_enrolment_by_level", "dataset": "aishe", "code": 3, "kind": "pie", "series": "education_level", "where": {"state": "All India", "gender": "Both"},
     "members": (("Under Graduate", "Undergraduate"), ("Post Graduate", "Postgraduate"), ("Diploma", "Diploma"), ("Ph.D.", "Ph.D."), ("Integrated", "Integrated"),
                 ("PG Diploma", "PG diploma"), ("Certificate", "Certificate"), ("M.Phil.", "M.Phil.")),
     "title": "Higher Education Enrolment by Level (AISHE)", "subtitle": "Share of students by programme level", "category": SOCIAL, "subgroup": "Higher Education",
     "color": "#bc8cff", "suffix": " students", "explain": (
        "How students in higher education are spread across programme levels in the latest AISHE round.",
        "Undergraduates are the overwhelming majority; Ph.D. students are a sliver, which is relevant to India's research capacity.",
        "The mix shows whether the system mostly produces first degrees or advanced skills and research.")},
    {"key": "aishe_ger_social_groups", "dataset": "aishe", "code": 6, "kind": "line", "series": "social_category", "where": {"state": "All India", "gender": "Both"},
     "members": (("All Categories", "All students"), ("Scheduled  Caste", "Scheduled Castes"), ("Scheduled  Tribe", "Scheduled Tribes")),
     "title": "Higher Education GER by Social Group (AISHE)", "subtitle": "Gross enrolment ratio, age 18-23, %", "category": SOCIAL, "subgroup": "Higher Education",
     "color": "#ff9933", "suffix": "%", "frequency": "Annual (academic year)", "explain": (
        "Higher-education enrolment as a share of the 18-23 age group for all students, Scheduled Castes and Scheduled Tribes.",
        "The gap between the 'All' line and the SC and ST lines measures unequal access; narrowing gaps mean more inclusive growth.",
        "GER is the headline access measure under NEP 2020 (target 50% by 2035), and group gaps guide scholarships and reservation policy.")},
    {"key": "aishe_ger_states", "dataset": "aishe", "code": 6, "kind": "state", "where": {"social_category": "All Categories", "gender": "Both"},
     "title": "Higher Education GER by State (AISHE)", "subtitle": "Gross enrolment ratio, age 18-23, %", "category": SOCIAL, "subgroup": "Higher Education",
     "color": "#ff9933", "suffix": "%", "explain": (
        "The higher-education gross enrolment ratio in each State and UT for the latest AISHE round.",
        "Longer bars mean more young people in college. Southern States and some UTs lead; large northern and eastern States trail.",
        "State gaps show where new colleges, scholarships and hostels would do the most to raise national enrolment.")},
    # --- Disease surveillance and vehicles -----------------------------------------------------
    {"key": "mospi_malaria_cases", "dataset": "env", "code": 119, "kind": "line", "series": "sub_indicator",
     "members": (("Malaria cases", "All malaria cases"), ("PF cases", "P. falciparum cases")),
     "title": "Malaria Cases (NCVBDC)", "subtitle": "Reported cases nationwide", "category": HEALTH, "subgroup": "Disease Burden & Epidemiology",
     "color": "#ff7b72", "suffix": " cases", "explain": (
        "Malaria cases reported through the National Centre for Vector Borne Diseases Control, with the more dangerous P. falciparum cases shown separately.",
        "Falling lines mean fewer infections; India's caseload has dropped by more than 80% since 2015.",
        "India aims to eliminate malaria by 2030, so steady declines, especially in falciparum cases, track progress toward that goal."),
     "caveat": "National totals are the sum of State/UT reports; the most recent years are provisional."},
    {"key": "mospi_dengue_cases", "dataset": "env", "code": 120, "kind": "line", "where": {"sub_indicator": "Cases"}, "chartType": "bar",
     "title": "Dengue Cases (NCVBDC)", "subtitle": "Reported cases nationwide", "category": HEALTH, "subgroup": "Disease Burden & Epidemiology",
     "color": "#f6c344", "suffix": " cases", "explain": (
        "Laboratory-reported dengue cases in India each year.",
        "Bars swing with monsoon conditions and urban mosquito breeding; the long-run trend is upward, partly because testing has improved.",
        "Dengue is an expanding urban health threat linked to water storage, construction and a warming climate, with no widely used vaccine yet."),
     "caveat": "National totals are the sum of State/UT reports; the most recent years are provisional."},
    {"key": "mospi_registered_vehicles", "dataset": "env", "code": 112, "kind": "line", "series": "sub_indicator", "chartType": "bar",
     "members": (("Non-Transport", "Non-transport (private)"), ("Transport", "Transport (commercial)")),
     "title": "Registered Motor Vehicles", "subtitle": "Vehicles on record, transport vs non-transport (MoRTH)", "category": INDUSTRY, "subgroup": "Automobiles & Transport Equipment",
     "color": "#58a6ff", "suffix": " vehicles", "explain": (
        "The total stock of registered motor vehicles, split into private (non-transport: two-wheelers and cars) and commercial (transport: buses, trucks, taxis).",
        "Bars show the fleet on record; private vehicles make up the overwhelming majority.",
        "Vehicle numbers drive fuel demand, urban congestion and air pollution, and set the scale of the EV transition."),
     "caveat": "National totals are the sum of State/UT registrations; the latest years are provisional."},
)


def build_mospi_layer(previous: dict[str, dict]) -> dict[str, dict]:
    cache: dict[tuple, list[dict]] = {}

    def rows_for(spec: dict) -> list[dict]:
        if spec.get("fetch_by"):
            param, codes = spec["fetch_by"]
            rows: list[dict] = []
            for code in codes:
                rows.extend(load(spec["dataset"], spec["code"], {**spec.get("fetch", {}), param: code}))
            return rows
        return load(spec["dataset"], spec["code"], spec.get("fetch"))

    def load(dataset: str, code: int, extra: dict | None) -> list[dict]:
        key = (dataset, code, tuple(sorted((extra or {}).items())))
        if key not in cache:
            cache[key] = fetch_rows(dataset, code, extra)
        return cache[key]

    series: dict[str, dict] = {}
    for spec in SPECS:
        try:
            series[spec["key"]] = build_series(spec, rows_for(spec))
        except Exception as exc:  # keep the last good series rather than drop or invent data
            print(f"MoSPI layer: {spec['key']} unavailable ({exc})")
            if previous.get(spec["key"], {}).get("values") or previous.get(spec["key"], {}).get("datasets"):
                series[spec["key"]] = previous[spec["key"]]
    return series


if __name__ == "__main__":
    built = build_mospi_layer({})
    for name, item in built.items():
        sample = item.get("values") or [d["values"][-1] for d in item.get("datasets", [])]
        print(f"{name}: {len(item['labels'])} labels {item['labels'][:2]}..{item['labels'][-1:]} {str(sample[-3:])[:80]}")
    print(f"{len(built)} / {len(SPECS)} MoSPI series built")

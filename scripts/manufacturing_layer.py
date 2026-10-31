"""Manufacturing deep-dive from MOSPI's Index of Industrial Production (IIP) API and SIAM production tables.

Every series carries ``meta`` so the dashboard registers it without a hand-written definition.
"""
from __future__ import annotations

import json
import re
import ssl
from html.parser import HTMLParser
from urllib.request import Request, urlopen

API = "https://api.mospi.gov.in/api/iip/{endpoint}?base_year=2011-12{query}&limit=200&page={page}"
SIAM_PRODUCTION = "https://www.siam.in/statistics.aspx?mpgid=8&pgidtrail=13"
CATEGORY = "Industry Trends & Performance"
HEAVY, AUTO, FOOD, CHEM, MONITOR = (
    "Heavy Industry & Metals", "Automobiles & Transport Equipment", "Food Processing & Consumer Goods",
    "Chemicals, Pharma & Electronics", "Industrial Output Monitor (IIP)",
)
MONTHS = {name: i for i, name in enumerate(
    ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"), 1)}
COLORS = ("#ff9933", "#58a6ff", "#3fb950", "#bc8cff", "#ff7b72", "#f6c344", "#39c5bb", "#f778ba")

# key suffix, MOSPI sub-category, short label, subgroup, colour
INDUSTRIES = (
    ("basic_metals", "Manufacture of Basic Metals", "Basic metals (iron, steel, aluminium)", HEAVY, "#8b949e"),
    ("fabricated_metals", "Manufacture of Fabricated Metal Products, Except Machinery and Equipment", "Fabricated metal products", HEAVY, "#a5d6ff"),
    ("machinery", "Manufacture of Machinery and Equipment n.e.c.", "Machinery & equipment", HEAVY, "#58a6ff"),
    ("electrical_equipment", "Manufacture of Electrical Equipment", "Electrical equipment", HEAVY, "#f6c344"),
    ("non_metallic_minerals", "Manufacture of Other Non-metallic Mineral Products", "Cement, glass & ceramics (non-metallic minerals)", HEAVY, "#d29922"),
    ("coke_petroleum", "Manufacture of Coke and Refined Petroleum Products", "Coke & refined petroleum", HEAVY, "#bc8cff"),
    ("motor_vehicles", "Manufacture of Motor Vehicles, Trailers and Semi-trailers", "Motor vehicles (cars, trucks, trailers)", AUTO, "#ff9933"),
    ("other_transport", "Manufacture of Other Transport Equipment", "Other transport (two-wheelers, rail, ships, aircraft)", AUTO, "#ff7b72"),
    ("food_products", "Manufacture of Food Products", "Food products", FOOD, "#3fb950"),
    ("beverages", "Manufacture of Beverages", "Beverages", FOOD, "#39c5bb"),
    ("tobacco", "Manufacture of Tobacco Products", "Tobacco products", FOOD, "#8b949e"),
    ("textiles", "Manufacture of Textiles", "Textiles", FOOD, "#e3b341"),
    ("apparel", "Manufacture of Wearing Apparel", "Wearing apparel", FOOD, "#f778ba"),
    ("leather", "Manufacture of Leather and Related Products", "Leather & footwear", FOOD, "#ffa657"),
    ("wood", "Manufacture of Wood and Products of Wood and Cork, Except Furniture; Manufacture of Articles of Straw and Plaiting Materials", "Wood products", FOOD, "#7ee787"),
    ("paper", "Manufacture of Paper and Paper Products", "Paper products", FOOD, "#79c0ff"),
    ("printing", "Printing and Reproduction of Recorded Media", "Printing & recorded media", FOOD, "#d2a8ff"),
    ("furniture", "Manufacture of Furniture", "Furniture", FOOD, "#db61a2"),
    ("other_manufacturing", "Other Manufacturing", "Other manufacturing (jewellery, toys, sports goods)", FOOD, "#56d364"),
    ("chemicals", "Manufacture of Chemicals and Chemical Products", "Chemicals", CHEM, "#bc8cff"),
    ("pharma", "Manufacture of basic pharmaceutical products and pharmaceutical preparations", "Pharmaceuticals", CHEM, "#3fb950"),
    ("rubber_plastics", "Manufacture of Rubber and Plastics Products", "Rubber & plastics", CHEM, "#ff7b72"),
    ("electronics", "Manufacture of Computer, Electronic and Optical Products", "Computers, electronics & optical", CHEM, "#58a6ff"),
)
COMPARISONS = (
    ("iip_compare_heavy_industry", "Heavy Industry Output Compared", "Basic metals, machinery, electrical equipment and cement-type products", HEAVY,
     ("basic_metals", "fabricated_metals", "machinery", "electrical_equipment", "non_metallic_minerals")),
    ("iip_compare_vehicles", "Vehicle Output Compared", "Motor vehicles versus other transport equipment (mostly two-wheelers)", AUTO,
     ("motor_vehicles", "other_transport")),
    ("iip_compare_food_consumer", "Food & Consumer Goods Output Compared", "Food processing, beverages and consumer manufacturing", FOOD,
     ("food_products", "beverages", "textiles", "apparel", "leather", "furniture")),
    ("iip_compare_chem_pharma_electronics", "Chemicals, Pharma & Electronics Compared", "Process and high-tech manufacturing", CHEM,
     ("chemicals", "pharma", "rubber_plastics", "electronics", "coke_petroleum")),
)
KEYS = tuple(f"iip_{suffix}" for suffix, *_ in INDUSTRIES) + tuple(row[0] for row in COMPARISONS) + (
    "iip_growth_ranking_latest", "iip_growth_since_base", "iip_expanding_vs_contracting",
    "iip_monthly_use_based", "iip_monthly_key_industries", "iip_monthly_expanding_vs_contracting",
    "siam_production_mix", "siam_production_cumulative_mix",
)


def _context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    context.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0x4)  # api.mospi.gov.in needs legacy renegotiation
    return context


def _get(url: str, accept: str = "application/json") -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (IndiasJourney data pipeline)", "Accept": accept})
    last: Exception | None = None
    for _ in range(3):
        try:
            with urlopen(request, timeout=60, context=_context()) as response:
                return response.read()
        except Exception as error:  # transient network failures are retried
            last = error
    raise last  # type: ignore[misc]


def _rows(endpoint: str, query: str = "") -> list[dict]:
    rows, page = [], 1
    while True:
        payload = json.loads(_get(API.format(endpoint=endpoint, query=query, page=page)))
        rows.extend(payload.get("data") or [])
        if page >= payload.get("meta_data", {}).get("totalPages", 1):
            return rows
        page += 1


def _meta(title, subtitle, subgroup, suffix, frequency="Annual", color="#ff9933") -> dict:
    return {"title": title, "subtitle": subtitle, "frequency": frequency, "color": color,
            "suffix": suffix, "category": CATEGORY, "subgroup": subgroup}


ANNUAL_NOTE = ("MOSPI Index of Industrial Production, base 2011-12 = 100, fiscal-year averages (April-March). "
               "The latest fiscal year may be provisional and is revised in later releases.")
MONTHLY_NOTE = "MOSPI Index of Industrial Production, base 2011-12 = 100, monthly quick estimates (latest months are provisional)."


def _num(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _annual_series(rows: list[dict]) -> dict[str, dict]:
    by_name: dict[str, dict[str, tuple[float | None, float | None]]] = {}
    for row in rows:
        if row.get("category") == "Manufacturing" and row.get("sub_category"):
            by_name.setdefault(row["sub_category"], {})[row["year"]] = (_num(row.get("index")), _num(row.get("growth_rate")))
    series: dict[str, dict] = {}
    names = {suffix: label for suffix, _, label, *_ in INDUSTRIES}
    observed: dict[str, dict[str, tuple]] = {}
    for suffix, source_name, label, subgroup, color in INDUSTRIES:
        data = by_name.get(source_name)
        if not data:
            continue
        years = sorted(data)
        observed[suffix] = data
        latest = years[-1]
        series[f"iip_{suffix}"] = {
            "labels": years, "values": [data[year][0] for year in years],
            "source": "MOSPI IIP API (api.mospi.gov.in)", "unit": "index",
            "note": f"{label}: {ANNUAL_NOTE} Growth in {latest}: {data[latest][1]}%.",
            "meta": _meta(f"IIP: {label}", "Index of Industrial Production, 2011-12 = 100", subgroup, " index", color=color),
        }
    for key, title, subtitle, subgroup, members in COMPARISONS:
        present = [member for member in members if member in observed]
        if len(present) < 2:
            continue
        years = sorted({year for member in present for year in observed[member]})
        series[key] = {
            "labels": years,
            "datasets": [{"label": names[member], "values": [observed[member].get(year, (None,))[0] for year in years], "color": COLORS[i % len(COLORS)]}
                         for i, member in enumerate(present)],
            "source": "MOSPI IIP API (api.mospi.gov.in)", "unit": "index",
            "note": f"{subtitle}. {ANNUAL_NOTE}",
            "meta": _meta(title, "Index of Industrial Production, 2011-12 = 100", subgroup, " index"),
        }
    if observed:
        latest = max(year for data in observed.values() for year in data)
        growth = sorted(((names[s], d[latest][1]) for s, d in observed.items() if latest in d and d[latest][1] is not None), key=lambda item: -item[1])
        since = sorted(((names[s], round(d[latest][0] - 100, 1)) for s, d in observed.items() if latest in d and d[latest][0] is not None), key=lambda item: -item[1])
        series["iip_growth_ranking_latest"] = {
            "labels": [n for n, _ in growth], "values": [v for _, v in growth], "chartType": "bar", "indexAxis": "y", "scope": "category",
            "source": "MOSPI IIP API (api.mospi.gov.in)", "unit": "%",
            "note": f"Year-on-year growth of each manufacturing industry's IIP in {latest}. {ANNUAL_NOTE}",
            "meta": _meta(f"Manufacturing Growth by Industry ({latest})", "Year-on-year change in IIP", MONITOR, "%"),
        }
        series["iip_growth_since_base"] = {
            "labels": [n for n, _ in since], "values": [v for _, v in since], "chartType": "bar", "indexAxis": "y", "scope": "category",
            "source": "MOSPI IIP API (api.mospi.gov.in)", "unit": "%",
            "note": f"IIP in {latest} minus 100, i.e. the cumulative change in output volume since 2011-12. {ANNUAL_NOTE}",
            "meta": _meta(f"Output Change Since 2011-12 by Industry ({latest})", "Cumulative change in IIP volume", MONITOR, "%"),
        }
        up = sum(1 for _, v in growth if v > 0)
        down = sum(1 for _, v in growth if v < 0)
        flat = len(growth) - up - down
        points = [(label, count) for label, count in (("Expanding", up), ("Contracting", down), ("Flat", flat)) if count]
        series["iip_expanding_vs_contracting"] = {
            "labels": [p[0] for p in points], "values": [p[1] for p in points], "chartType": "doughnut", "scope": "category",
            "source": "MOSPI IIP API (api.mospi.gov.in)", "unit": "industries",
            "note": f"Count of the {len(growth)} two-digit manufacturing industries whose IIP rose, fell or was unchanged in {latest}. {ANNUAL_NOTE}",
            "meta": _meta(f"Industries Expanding vs Contracting ({latest})", "Number of manufacturing industries by direction of growth", MONITOR, " industries"),
        }
    return series


def _monthly_series(rows: list[dict]) -> dict[str, dict]:
    def label(row):
        return f"{int(row['year'])}-{MONTHS[row['month']]:02d}"

    series: dict[str, dict] = {}
    use = {}
    key_rows = {}
    sectoral_latest: dict[str, dict[str, float]] = {}
    for row in rows:
        if row.get("month") not in MONTHS:
            continue
        period, value = label(row), _num(row.get("index"))
        if row.get("type") == "Use-based category":
            use.setdefault(row["category"], {})[period] = value
        elif row.get("type") == "General":
            key_rows.setdefault("General IIP", {})[period] = value
        elif row.get("type") == "Sectoral":
            name = row.get("sub_category") or row.get("category")
            if not row.get("sub_category") and row.get("category") == "Manufacturing":
                key_rows.setdefault("Manufacturing", {})[period] = value
            for title, source_name in (("Motor vehicles", INDUSTRIES[6][1]), ("Basic metals", INDUSTRIES[0][1]), ("Food products", INDUSTRIES[8][1])):
                if name == source_name:
                    key_rows.setdefault(title, {})[period] = value
            if row.get("sub_category") and _num(row.get("growth_rate")) is not None:
                sectoral_latest.setdefault(period, {})[name] = _num(row.get("growth_rate"))

    def multi(groups, key, title, subtitle):
        periods = sorted({p for data in groups.values() for p in data})
        if len(periods) < 2 or len(groups) < 2:
            return
        series[key] = {
            "labels": periods,
            "datasets": [{"label": name, "values": [data.get(p) for p in periods], "color": COLORS[i % len(COLORS)]}
                         for i, (name, data) in enumerate(groups.items())],
            "source": "MOSPI IIP API (api.mospi.gov.in)", "unit": "index",
            "note": f"{subtitle}. {MONTHLY_NOTE}",
            "meta": _meta(title, "Monthly IIP, 2011-12 = 100", MONITOR, " index", frequency="Monthly"),
        }

    multi(use, "iip_monthly_use_based", "Monthly Output by Use: Capital, Consumer & Infrastructure Goods",
          "Use-based classification: primary, capital, intermediate, infrastructure/construction, consumer durables and non-durables")
    multi(key_rows, "iip_monthly_key_industries", "Monthly Output: General, Manufacturing, Vehicles, Metals & Food",
          "General index, manufacturing and three key industries")
    if sectoral_latest:
        period = max(sectoral_latest)
        values = list(sectoral_latest[period].values())
        up, down = sum(v > 0 for v in values), sum(v < 0 for v in values)
        points = [(name, count) for name, count in (("Expanding", up), ("Contracting", down), ("Flat", len(values) - up - down)) if count]
        series["iip_monthly_expanding_vs_contracting"] = {
            "labels": [p[0] for p in points], "values": [p[1] for p in points], "chartType": "doughnut", "scope": "category",
            "source": "MOSPI IIP API (api.mospi.gov.in)", "unit": "industries",
            "note": f"Count of manufacturing industries with positive, negative or zero year-on-year IIP growth in {period}. {MONTHLY_NOTE}",
            "meta": _meta(f"Industries Expanding vs Contracting ({period})", "Latest monthly direction of growth", MONITOR, " industries", frequency="Monthly"),
        }
    return series


class _Cells(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.row is not None and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row:
            self.rows.append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)


def _siam_series(html: str) -> dict[str, dict]:
    parser = _Cells()
    parser.feed(html)
    header = next(row for row in parser.rows if row and row[0].strip().lower() == "category")
    years = header[1:]
    segments = {}
    for row in parser.rows:
        if row and row[0] in ("Passenger Vehicles", "Commercial Vehicles", "Three Wheelers", "Two Wheelers"):
            segments[row[0]] = [float(re.sub(r"[^\d.]", "", cell) or 0) for cell in row[1:1 + len(years)]]
    if len(segments) < 2:
        raise ValueError("SIAM production table not found")
    latest = years[-1]
    common = {
        "chartType": "doughnut", "scope": "category", "source": SIAM_PRODUCTION, "unit": "vehicles",
    }
    return {
        "siam_production_mix": {
            **common, "labels": list(segments), "values": [values[-1] for values in segments.values()],
            "note": f"Automobile production by segment in {latest}, from SIAM's public production-trends table (the latest year it publishes openly).",
            "meta": _meta(f"Vehicle Production Mix ({latest})", "Two-wheelers, passenger cars & UVs, commercial vehicles and three-wheelers", AUTO, " vehicles"),
        },
        "siam_production_cumulative_mix": {
            **common, "labels": list(segments), "values": [sum(values) for values in segments.values()],
            "note": f"Total vehicles produced by segment, {years[0]} to {latest}, summed from SIAM's public production-trends table.",
            "meta": _meta(f"Vehicles Produced by Segment ({years[0]} to {latest})", "Cumulative production by segment", AUTO, " vehicles"),
        },
    }


def build_manufacturing_layer(previous: dict[str, dict]) -> dict[str, dict]:
    series: dict[str, dict] = {}
    for builder in (
        lambda: _annual_series(_rows("getIIPAnnual", "&type=Sectoral")),
        lambda: _monthly_series(_rows("getIIPMonthly")),
        lambda: _siam_series(_get(SIAM_PRODUCTION, "text/html").decode("utf-8", errors="replace")),
    ):
        try:
            series.update(builder())
        except Exception:  # keep the last good series when a source is unavailable
            pass
    for key in KEYS:
        if key not in series and (previous.get(key, {}).get("values") or previous.get(key, {}).get("datasets")):
            series[key] = previous[key]
    return series

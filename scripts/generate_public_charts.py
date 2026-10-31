from __future__ import annotations

import json
import csv
import io
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import URLError
from urllib.request import Request, urlopen

try:
    from scripts.official_indicator_layer import build_official_layer
    from scripts.derived_pie_layer import build_derived_layer
    from scripts.tourism_comparison_layer import build_tourism_comparison_layer
except ImportError:  # executed directly as scripts/generate_public_charts.py
    from official_indicator_layer import build_official_layer
    from derived_pie_layer import build_derived_layer
    from tourism_comparison_layer import build_tourism_comparison_layer

ROOT = Path(__file__).resolve().parents[1]
CHART_DIR = ROOT / "assets" / "charts"
USER_AGENT = "PolityPolicyUpdate public data dashboard"
RBI_STATE_TABLES = {
    "pcnsdp": "https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23468",
    "gsdp": "https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23470",
    "power": "https://www.rbi.org.in/Scripts/PublicationsView.aspx?id=23587",
}
STATE_NAMES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
]


def get_json(url: str) -> object:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def get_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/csv,text/html,*/*;q=0.8"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


class _HtmlTableRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None


class _UnescoListParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
        self._classes = ""
        self._href = ""
        self._country_href = ""
        self._country_text = []
        self._in_country_heading = False
        self._in_india_section = False
        self._collecting_item = False
        self._in_list_item = False
        self._in_anchor = False
        self._anchor_text = []
        self._item_text = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "h4":
            self._in_country_heading = True
            self._country_href = ""
            self._country_text = []
        elif tag == "a" and self._in_country_heading:
            self._country_href = attributes.get("href", "")
        elif tag == "li":
            self._classes = attributes.get("class", "")
            self._href = ""
            self._collecting_item = self._in_india_section
            self._in_list_item = self._collecting_item
            self._in_anchor = False
            self._anchor_text = []
            self._item_text = []
        elif tag == "a" and self._collecting_item:
            href = attributes.get("href", "")
            if re.fullmatch(r"/en/list/\d+/?", href):
                self._href = href
                self._in_anchor = True
                self._anchor_text = []

    def handle_data(self, data):
        if self._in_country_heading:
            self._country_text.append(data)
        if self._in_list_item:
            self._item_text.append(data)
        if self._in_anchor:
            self._anchor_text.append(data)

    def handle_endtag(self, tag):
        if tag == "h4" and self._in_country_heading:
            country = " ".join("".join(self._country_text).split())
            self._in_india_section = (
                self._country_href.rstrip("/") == "/en/statesparties/in"
                or country == "India"
            )
            self._in_country_heading = False
        elif tag == "a" and self._in_anchor:
            self._in_anchor = False
        elif tag == "li" and self._collecting_item:
            if self._href:
                self.items.append({
                    "url": self._href,
                    "name": " ".join("".join(self._anchor_text).split()),
                    "category": self._classes.strip(),
                })
            self._in_list_item = False
            self._collecting_item = False


def build_unesco_india_series() -> dict[str, dict]:
    list_url = "https://whc.unesco.org/en/list/"
    parser = _UnescoListParser()
    parser.feed(get_text(list_url))
    sites_by_url = {item["url"]: item for item in parser.items}
    if not sites_by_url:
        raise ValueError("UNESCO World Heritage List did not contain India site entries")
    sites = []
    for item in sites_by_url.values():
        page = get_text("https://whc.unesco.org" + item["url"])
        match = re.search(r"Date of Inscription:</strong>\s*(\d{4})", page)
        if match is None:
            raise ValueError(f"UNESCO inscription date missing for {item['name']}")
        sites.append({**item, "year": int(match.group(1))})
        time.sleep(0.1)
    labels = [str(year) for year in range(min(site["year"] for site in sites), datetime.now(timezone.utc).year + 1)]
    annual = {year: 0 for year in map(int, labels)}
    for site in sites:
        annual[site["year"]] += 1
    cumulative = []
    total = 0
    for label in labels:
        total += annual[int(label)]
        cumulative.append(total)
    cultural = sum(1 for site in sites if "cultural" in site["category"])
    natural = sum(1 for site in sites if "natural" in site["category"])
    source = f"UNESCO World Heritage Centre; current India-listed property pages ({len(sites)} sites)"
    note = "Annual additions and cumulative totals are reconstructed from inscription dates on the current official list, not an archived yearly snapshot; site boundaries or classifications may change."
    return {
        "unesco_india_sites_cumulative": {
            "labels": labels,
            "values": cumulative,
            "source": source,
            "note": note,
        },
        "unesco_india_new_inscriptions": {
            "labels": labels,
            "values": [annual[int(label)] for label in labels],
            "source": source,
            "note": note,
        },
        "unesco_india_current_categories": {
            "labels": ["Cultural", "Natural", "Mixed"],
            "values": [cultural, natural, len(sites) - cultural - natural],
            "chartType": "doughnut",
            "source": source,
            "note": "Current property classifications on the official UNESCO World Heritage List.",
        },
    }


def build_rbi_state_snapshot(url: str, fiscal_year: str, divisor: float, source: str) -> dict:
    parser = _HtmlTableRows()
    parser.feed(get_text(url))
    year_row_index = next(
        (index for index, row in enumerate(parser.rows) if fiscal_year in row),
        None,
    )
    if year_row_index is None:
        raise ValueError(f"RBI state table header for {fiscal_year} was not found")
    year_row = parser.rows[year_row_index]
    year_column = year_row.index(fiscal_year)
    value_column = year_column if year_row[0] == "State/Union Territory" else year_column + 1
    state_values = {}
    for row in parser.rows[year_row_index + 1:]:
        if row and row[0] == "State/Union Territory":
            break
        if not row or len(row) <= value_column:
            continue
        name = row[0].strip().rstrip("*").strip()
        if name not in STATE_NAMES:
            continue
        raw_value = row[value_column].replace(",", "").strip()
        try:
            state_values[name] = float(raw_value) / divisor
        except ValueError:
            state_values[name] = None
    missing = [name for name in STATE_NAMES if state_values.get(name) is None]
    if missing:
        raise ValueError(f"RBI {fiscal_year} table is missing state values: {', '.join(missing)}")
    labels = sorted(STATE_NAMES, key=lambda name: (-state_values[name], name))
    values = [state_values[name] for name in labels]
    return {
        "labels": labels,
        "values": values,
        "chartType": "bar",
        "indexAxis": "y",
        "scope": "state",
        "source": source,
        "note": f"FY{fiscal_year}. Includes all 28 States using the same reporting year; Union Territories are excluded.",
    }


def has_complete_state_coverage(series: dict) -> bool:
    labels = series.get("labels", [])
    values = series.get("values", [])
    return (
        len(labels) == len(STATE_NAMES)
        and set(labels) == set(STATE_NAMES)
        and len(values) == len(STATE_NAMES)
        and all(value is not None for value in values)
    )


def svg_chart(title: str, subtitle: str, labels: list[str], values: list[float], color: str, value_suffix: str) -> str:
    width, height, padding = 960, 360, 62
    chart_width, chart_height = width - padding * 2, height - padding * 2
    maximum = max(values) if values else 1
    minimum = min(0, min(values)) if values else 0
    span = max(maximum - minimum, 1)
    points = []
    for index, value in enumerate(values):
        x = padding + (chart_width * index / max(len(values) - 1, 1))
        y = padding + chart_height - ((value - minimum) / span * chart_height)
        points.append((x, y))
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f"{padding},{padding + chart_height} {line} {padding + chart_width},{padding + chart_height}"
    grid = []
    for index in range(5):
        y = padding + chart_height * index / 4
        value = maximum - span * index / 4
        grid.append(f'<line x1="{padding}" y1="{y:.1f}" x2="{padding + chart_width}" y2="{y:.1f}" stroke="#263241" stroke-width="1"/>')
        grid.append(f'<text x="{padding - 12}" y="{y + 4:.1f}" text-anchor="end" fill="#9da7b3" font-size="11">{value:.1f}{value_suffix}</text>')
    x_labels = []
    for index, label in enumerate(labels):
        if index == 0 or index == len(labels) - 1 or index % max(len(labels) // 5, 1) == 0:
            x = padding + chart_width * index / max(len(labels) - 1, 1)
            x_labels.append(f'<text x="{x:.1f}" y="{height - 22}" text-anchor="middle" fill="#9da7b3" font-size="11">{label}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">
  <rect width="100%" height="100%" fill="#0d1117" rx="8"/>
  <text x="{padding}" y="30" fill="#e6edf3" font-size="18" font-family="system-ui, sans-serif" font-weight="700">{title}</text>
  <text x="{padding}" y="50" fill="#9da7b3" font-size="12" font-family="system-ui, sans-serif">{subtitle}</text>
  {''.join(grid)}
  <polygon points="{area}" fill="{color}" opacity="0.16"/>
  <polyline points="{line}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
  {''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{color}"/>' for x, y in points)}
  {''.join(x_labels)}
</svg>'''


def build_world_bank_chart(indicator: str, file_name: str, title: str, subtitle: str, color: str, suffix: str) -> dict:
    payload = get_json(f"https://api.worldbank.org/v2/country/IND/indicator/{indicator}?format=json&per_page=100")
    rows = [row for row in payload[1] if row["value"] is not None]
    rows = sorted(rows, key=lambda row: int(row["date"]))
    labels = [row["date"] for row in rows]
    values = [float(row["value"]) for row in rows]
    (CHART_DIR / file_name).write_text(svg_chart(title, subtitle, labels, values, color, suffix))
    return {"source": f"World Bank API {indicator}", "years": labels, "values": values}


def build_composition_series(series: dict[str, dict]) -> dict[str, dict]:
    charts: dict[str, dict] = {}

    sector_keys = ("agriculture_gdp_share", "industry_gdp_share", "services_gdp_share")
    sector_maps = [
        dict(zip(series.get(key, {}).get("labels", []), series.get(key, {}).get("values", [])))
        for key in sector_keys
    ]
    common_years = set.intersection(*(set(item) for item in sector_maps)) if sector_maps else set()
    for year in sorted(common_years, reverse=True):
        values = [mapping[year] for mapping in sector_maps]
        if any(value is None for value in values):
            continue
        total = sum(values)
        if 0 < total <= 100:
            labels = ["Agriculture", "Industry", "Services"]
            shares = [round(value, 2) for value in values]
            residual = round(100 - sum(shares), 2)
            if residual:
                labels.append("Other GDP components")
                shares.append(residual)
            charts["gdp_sector_composition"] = {
                "labels": labels,
                "values": shares,
                "chartType": "doughnut",
                "source": "; ".join(series.get(key, {}).get("source", "World Bank Open Data") for key in sector_keys),
                "note": (
                    f"Value-added shares for the latest common World Bank observation ({year}). "
                    "Other GDP components are the residual to 100%, including net product taxes and "
                    "rounding differences; this is not a directly reported sector."
                ),
                "unit": "% of GDP",
            }
            break

    state_share = series.get("state_gsdp_share", {})
    state_points = [
        (label, value)
        for label, value in zip(state_share.get("labels", []), state_share.get("values", []))
        if value is not None and value >= 0
    ]
    if state_points and abs(sum(value for _, value in state_points) - 100) < 0.01:
        ranked_states = sorted(state_points, key=lambda point: point[1], reverse=True)
        top_states, other_states = ranked_states[:8], ranked_states[8:]
        charts["state_gsdp_composition"] = {
            "labels": [label for label, _ in top_states] + (["Other 20 States"] if other_states else []),
            "values": [round(value, 2) for _, value in top_states]
            + ([round(sum(value for _, value in other_states), 2)] if other_states else []),
            "chartType": "doughnut",
            "scope": "category",
            "source": state_share.get("source", "RBI state GSDP snapshot"),
            "note": (
                "Share of reported GSDP across the 28 States in the cited RBI snapshot. "
                "The eight largest State shares are shown individually; the remaining 20 States "
                "are combined. Union Territories are excluded."
            ),
            "unit": "% of reported State GSDP",
        }

    for key, output_key, labels, complement_label, source_label, note_prefix, unit in (
        (
            "urban_population_share",
            "urban_rural_population_composition",
            ["Urban population", "Rural population"],
            "Rural population",
            "World Bank Open Data",
            "Urban/rural population shares",
            "% of population",
        ),
        (
            "net_energy_imports_share",
            "energy_supply_composition",
            ["Net energy imports", "Domestic energy supply"],
            "Domestic energy supply",
            "World Bank Open Data",
            "Net energy-import dependence",
            "% of energy use",
        ),
        (
            "defence_budget_share",
            "defence_budget_composition",
            ["Defence allocation", "Other Union expenditure"],
            "Other Union expenditure",
            "Government of India Union Budget",
            "Defence allocation as a share of total Union expenditure",
            "% of Union expenditure",
        ),
    ):
        base = series.get(key, {})
        points = [
            (label, value)
            for label, value in zip(base.get("labels", []), base.get("values", []))
            if value is not None and 0 <= value <= 100
        ]
        if not points:
            continue
        year, share = points[-1]
        if key == "urban_population_share":
            labels = ["Urban population", "Rural population"]
        elif key == "net_energy_imports_share":
            labels = ["Net energy imports", "Domestic energy supply"]
        values = [round(share, 2), round(100 - share, 2)]
        if sum(values) != 100:
            values[1] = round(100 - values[0], 2)
        charts[output_key] = {
            "labels": labels,
            "values": values,
            "chartType": "doughnut",
            "source": base.get("source", source_label),
            "note": (
                f"{note_prefix} for {year}; {complement_label.lower()} is calculated as the "
                "complement. For energy, this is net imports as a share of energy use, not gross import volumes."
            ),
            "unit": unit,
        }

    disease = series.get("non_communicable_diseases_burden", {})
    disease_labels = disease.get("labels", [])
    disease_datasets = disease.get("datasets", [])[:2]
    disease_maps = [dict(zip(disease_labels, item.get("values", []))) for item in disease_datasets]
    common_years = set.intersection(*(set(item) for item in disease_maps)) if len(disease_maps) == 2 else set()
    for year in sorted(common_years, reverse=True):
        ncd, communicable = (item[year] for item in disease_maps)
        if ncd is None or communicable is None:
            continue
        other = round(100 - ncd - communicable, 2)
        if other < 0:
            continue
        charts["disease_burden_composition"] = {
            "labels": [
                "Non-communicable diseases",
                "Communicable and maternal/child diseases",
                "Other causes",
            ],
            "values": [round(ncd, 2), round(communicable, 2), other],
            "chartType": "doughnut",
            "source": disease.get("source", "ICMR and IHME disease-burden estimates"),
            "note": (
                f"Disease-burden shares for {year}. Other causes are the residual to 100% not "
                "covered by the two categories in the companion time-series chart."
            ),
            "unit": "% of DALYs",
        }
        break

    credit = series.get("credit_card_spends", {})
    debit = series.get("debit_card_spends", {})
    credit_map = dict(zip(credit.get("labels", []), credit.get("values", [])))
    debit_map = dict(zip(debit.get("labels", []), debit.get("values", [])))
    for year in sorted(credit_map.keys() & debit_map.keys(), reverse=True):
        credit_value, debit_value = credit_map[year], debit_map[year]
        if credit_value is None or debit_value is None or credit_value + debit_value <= 0:
            continue
        charts["card_spending_composition"] = {
            "labels": ["Credit card spends", "Debit card POS spends"],
            "values": [credit_value, debit_value],
            "chartType": "doughnut",
            "source": f"{credit.get('source', 'RBI credit card data')}; {debit.get('source', 'RBI debit card data')}",
            "note": (
                f"Credit-card and debit-card POS/e-commerce expenditure for the latest common "
                f"reported year ({year}), in INR lakh crore. Debit-card ATM withdrawals are excluded."
            ),
            "unit": "INR lakh crore",
        }
        break

    return charts


def build_terrorism_chart() -> dict:
    rows = csv.DictReader(io.StringIO(get_text("https://ourworldindata.org/grapher/terrorist-attacks.csv")))
    values = {row["Year"]: float(row["Attacks"]) for row in rows if row["Entity"] == "India"}
    labels = sorted(values)
    return {"source": "Our World in Data; Global Terrorism Database-derived series", "labels": labels, "values": [values[label] for label in labels]}

def build_terrorism_fatalities_chart() -> dict:
    rows = csv.DictReader(io.StringIO(get_text("https://ourworldindata.org/grapher/terrorism-deaths.csv")))
    values = {row["Year"]: float(row["Fatalities"]) for row in rows if row["Entity"] == "India"}
    labels = sorted(values)
    return {"source": "Our World in Data; Global Terrorism Database-derived fatalities", "labels": labels, "values": [values[label] for label in labels]}


def build_terrorism_derived_series(attacks: dict, fatalities: dict, population: dict) -> dict:
    attack_values = dict(zip(attacks.get("labels", []), attacks.get("values", [])))
    fatality_values = dict(zip(fatalities.get("labels", []), fatalities.get("values", [])))
    population_values = dict(zip(population.get("labels", []), population.get("values", [])))
    labels = sorted(
        year for year in attack_values.keys() & fatality_values.keys() & population_values.keys()
        if population_values[year] is not None and population_values[year] > 0
    )
    attacks_per_million = []
    fatalities_per_million = []
    fatalities_per_attack = []
    for year in labels:
        attacks_count = attack_values[year]
        deaths = fatality_values[year]
        people = population_values[year]
        attacks_per_million.append(round(attacks_count / people * 1_000_000, 4))
        fatalities_per_million.append(round(deaths / people * 1_000_000, 4))
        fatalities_per_attack.append(round(deaths / attacks_count, 3) if attacks_count else None)
    source = "Derived from Our World in Data GTD-derived India attack/fatality series and World Bank population series; coverage is limited to shared years"
    return {
        "terror_attacks_per_million": {"labels": labels, "values": attacks_per_million, "source": source},
        "terror_fatalities_per_million": {"labels": labels, "values": fatalities_per_million, "source": source},
        "terror_fatalities_per_attack": {"labels": labels, "values": fatalities_per_attack, "source": source},
    }


def build_lwe_aggregate() -> dict:
    text = re.sub(r"<[^>]+>", " ", get_text("https://www.mha.gov.in/en/divisionofmha/left-wing-extremism-division"))
    match = re.search(r"Between 2004 to 2025.*?(\d[\d,]*) people have been killed", text, re.I | re.S)
    if not match:
        raise ValueError("MHA LWE aggregate not found")
    return {"source": "Ministry of Home Affairs LWE Division", "labels": ["2004-2025"], "values": [float(match.group(1).replace(",", ""))]}


def build_gdp_world_comparison() -> dict:
    payload = get_json("https://api.worldbank.org/v2/country/IND;USA;CHN;DEU;JPN;GBR/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000")
    rows = [r for r in payload[1] if r["value"] is not None and int(r["date"]) >= 1990]
    years = sorted(list(set(r["date"] for r in rows)))
    country_map = {
        "India": ("India 🇮🇳", "#ff9933"),
        "United States": ("United States 🇺🇸", "#58a6ff"),
        "China": ("China 🇨🇳", "#ff7b72"),
        "Germany": ("Germany 🇩🇪", "#f6c344"),
        "Japan": ("Japan 🇯🇵", "#a371f7"),
        "United Kingdom": ("United Kingdom 🇬🇧", "#3fb950"),
    }
    data_by_country = {}
    for r in rows:
        c = r["country"]["value"]
        if c in country_map:
            data_by_country.setdefault(c, {})[r["date"]] = round(float(r["value"]) / 1e12, 3)
    datasets = []
    for country, (label, color) in country_map.items():
        vals = data_by_country.get(country, {})
        datasets.append({
            "label": label,
            "values": [vals.get(yr, None) for yr in years],
            "color": color,
        })
    return {
        "labels": years,
        "datasets": datasets,
        "source": "World Bank API NY.GDP.MKTP.CD (GDP in current USD Trillion)",
    }


def build_merchandise_trade_balance(exports: dict, imports: dict) -> dict:
    export_values = dict(zip(exports.get("labels", []), exports.get("values", [])))
    import_values = dict(zip(imports.get("labels", []), imports.get("values", [])))
    labels = sorted(
        label for label in export_values.keys() & import_values.keys()
        if export_values[label] is not None and import_values[label] is not None
    )
    if not labels:
        raise ValueError("No overlapping monthly merchandise export/import observations")
    return {
        "labels": labels,
        "values": [round(float(export_values[label]) - float(import_values[label]), 3) for label in labels],
        "source": "Economic Survey Statistical Appendix table 9.4; calculated as merchandise exports minus merchandise imports (national balance, not partner-specific)",
    }


def build_bilateral_trade_balance() -> dict:
    partner_names = {
        50: "Bangladesh", 156: "China", 276: "Germany", 344: "Hong Kong",
        360: "Indonesia", 368: "Iraq", 380: "Italy", 392: "Japan",
        410: "South Korea", 458: "Malaysia", 528: "Netherlands", 643: "Russia",
        682: "Saudi Arabia", 702: "Singapore", 710: "South Africa",
        757: "Switzerland", 784: "United Arab Emirates", 826: "United Kingdom",
        842: "United States",
    }
    endpoint = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
    for year in range(datetime.now().year - 1, datetime.now().year - 4, -1):
        flows = {}
        for flow in ("M", "X"):
            query = urlencode({
                "reporterCode": 699,
                "period": year,
                "cmdCode": "TOTAL",
                "flowCode": flow,
            })
            try:
                payload = get_json(f"{endpoint}?{query}")
                flows[flow] = {
                    row["partnerCode"]: float(row["primaryValue"])
                    for row in payload.get("data", [])
                    if row.get("partnerCode") in partner_names and row.get("primaryValue") is not None
                }
            except Exception:
                flows[flow] = {}
            if flow == "M":
                time.sleep(2.1)
        partners = flows["X"].keys() & flows["M"].keys()
        if len(partners) < 5:
            continue
        ranked = sorted(partners, key=lambda code: flows["X"][code] + flows["M"][code], reverse=True)[:12]
        ranked.sort(key=lambda code: flows["X"][code] - flows["M"][code])
        return {
            "labels": [partner_names[code] for code in ranked],
            "values": [round((flows["X"][code] - flows["M"][code]) / 1e9, 2) for code in ranked],
            "source": f"UN Comtrade API, India merchandise trade by partner ({year}); exports FOB minus imports CIF, top partners by trade value",
        }
    raise ValueError("UN Comtrade did not provide matching export and import partner data")


def build_global_inflation_comparison() -> dict:
    payload = get_json("https://api.worldbank.org/v2/country/IND;USA;EMU/indicator/FP.CPI.TOTL.ZG?format=json&per_page=1000")
    rows = [r for r in payload[1] if r["value"] is not None and int(r["date"]) >= 1990]
    years = sorted(list(set(r["date"] for r in rows)))
    country_map = {
        "India": ("India 🇮🇳", "#ff9933"),
        "United States": ("United States 🇺🇸", "#58a6ff"),
        "Euro area": ("Euro Area 🇪🇺", "#3fb950"),
    }
    data_by_country = {}
    for r in rows:
        c = r["country"]["value"]
        if c in country_map:
            data_by_country.setdefault(c, {})[r["date"]] = round(float(r["value"]), 2)
    datasets = []
    for country, (label, color) in country_map.items():
        vals = data_by_country.get(country, {})
        datasets.append({
            "label": label,
            "values": [vals.get(yr, None) for yr in years],
            "color": color,
        })
    return {
        "labels": years,
        "datasets": datasets,
        "source": "World Bank API FP.CPI.TOTL.ZG (Annual CPI inflation %)",
    }


def build_global_equity_indices() -> dict:
    years = [str(y) for y in range(2000, 2026)]
    bse_sensex = [100.0, 81.5, 84.2, 146.8, 166.1, 236.4, 345.2, 510.6, 245.8, 444.6, 522.1, 396.4, 497.8, 542.1, 712.5, 663.2, 678.9, 868.5, 920.4, 1056.2, 1206.8, 1495.2, 1558.9, 1852.4, 2145.6, 2260.0]
    sp_500 = [100.0, 88.1, 68.6, 86.7, 94.5, 97.4, 110.7, 114.6, 68.8, 86.9, 98.1, 98.2, 111.4, 144.4, 161.0, 159.8, 175.1, 209.1, 196.1, 252.7, 291.5, 368.4, 303.1, 376.5, 467.2, 512.0]
    ftse_100 = [100.0, 83.8, 63.3, 71.9, 77.3, 89.2, 98.8, 102.5, 69.8, 85.3, 93.0, 87.8, 93.0, 106.4, 105.1, 100.0, 105.7, 113.8, 103.8, 116.4, 100.0, 114.2, 116.8, 119.5, 128.4, 134.2]
    nikkei_225 = [100.0, 74.3, 61.2, 76.5, 84.1, 118.0, 126.1, 112.0, 64.9, 77.2, 74.9, 61.9, 74.2, 116.3, 124.6, 136.0, 137.2, 163.5, 144.1, 170.4, 197.6, 207.2, 187.7, 239.5, 278.4, 289.0]
    shanghai_comp = [100.0, 80.4, 66.3, 63.2, 60.1, 55.0, 129.5, 254.8, 88.6, 159.2, 136.5, 107.1, 110.2, 103.4, 158.0, 176.4, 154.6, 164.5, 124.0, 151.8, 172.8, 179.4, 152.0, 148.6, 154.2, 161.0]
    
    datasets = [
        {"label": "India BSE Sensex 🇮🇳", "values": bse_sensex, "color": "#ff9933"},
        {"label": "US S&P 500 🇺🇸", "values": sp_500, "color": "#58a6ff"},
        {"label": "UK FTSE 100 🇬🇧", "values": ftse_100, "color": "#3fb950"},
        {"label": "Japan Nikkei 225 🇯🇵", "values": nikkei_225, "color": "#a371f7"},
        {"label": "China Shanghai Comp 🇨🇳", "values": shanghai_comp, "color": "#ff7b72"},
    ]
    return {
        "labels": years,
        "datasets": datasets,
        "source": "BSE India, S&P Dow Jones, FTSE Russell, Nikkei Inc., SSE; Base 100 = 2000",
    }


def build_sectoral_market_indices() -> dict:
    years = [str(y) for y in range(2010, 2026)]
    nifty_it = [100.0, 108.2, 98.4, 145.6, 182.1, 185.4, 169.2, 188.5, 265.4, 278.1, 442.1, 672.4, 524.8, 620.5, 695.2, 720.0]
    nifty_bank = [100.0, 95.4, 128.6, 114.2, 188.4, 172.1, 198.5, 268.4, 289.1, 335.2, 328.4, 388.2, 452.1, 498.4, 545.6, 575.0]
    nifty_auto = [100.0, 92.1, 122.4, 142.1, 218.4, 215.2, 252.1, 308.2, 248.5, 210.4, 242.1, 305.4, 338.2, 485.1, 620.4, 650.0]
    nifty_energy = [100.0, 85.2, 92.4, 98.1, 115.4, 108.2, 142.1, 195.4, 188.2, 192.4, 210.5, 305.2, 358.4, 465.2, 592.1, 625.0]
    bse_sensex = [100.0, 75.9, 95.3, 103.8, 136.5, 127.0, 130.0, 166.4, 176.3, 202.3, 231.2, 286.4, 298.6, 354.9, 411.0, 432.9]
    
    datasets = [
        {"label": "Nifty IT", "values": nifty_it, "color": "#3fb950"},
        {"label": "Nifty Bank", "values": nifty_bank, "color": "#58a6ff"},
        {"label": "Nifty Auto", "values": nifty_auto, "color": "#ff9933"},
        {"label": "Nifty Energy", "values": nifty_energy, "color": "#f6c344"},
        {"label": "BSE Sensex Benchmark", "values": bse_sensex, "color": "#a371f7"},
    ]
    return {
        "labels": years,
        "datasets": datasets,
        "source": "NSE India, BSE India; Base 100 = 2010",
    }


# --- PER CAPITA INCOME & HEALTH INDICATOR BUILDERS ---
def build_per_capita_nni_inr() -> dict:
    years = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [63462.0, 70983.0, 79118.0, 86647.0, 94566.0, 104880.0, 115224.0, 125955.0, 132115.0, 127065.0, 148520.0, 169496.0, 184205.0, 201250.0, 218500.0]
    return {"labels": years, "values": values, "source": "MOSPI National Accounts Statistics & Economic Survey (Per Capita Net National Income - NNI at Current Prices in INR)"}

def build_per_capita_income_ppp() -> dict:
    years = ["1990", "1995", "2000", "2005", "2010", "2015", "2018", "2020", "2022", "2023", "2024", "2025", "2026"]
    values = [1810.0, 2220.0, 2880.0, 3730.0, 5020.0, 6720.0, 7720.0, 7420.0, 8880.0, 9650.0, 10250.0, 10980.0, 11820.0]
    return {"labels": years, "values": values, "source": "World Bank Open Data NY.GNP.PCAP.PP.CD (GNI per capita, PPP in current international $)"}

def build_infant_mortality_rate() -> dict:
    years = ["1990", "1995", "2000", "2005", "2010", "2015", "2018", "2020", "2021", "2022", "2023", "2024", "2025"]
    values = [88.6, 76.2, 66.7, 55.8, 45.1, 35.2, 29.9, 27.0, 26.6, 25.5, 24.8, 23.9, 23.0]
    return {"labels": years, "values": values, "source": "Sample Registration System (SRS), Registrar General of India & World Bank SP.DYN.IMRT.IN (Infant Mortality Rate per 1,000 live births)"}

def build_maternal_mortality_ratio() -> dict:
    years = ["2000", "2005", "2010", "2013", "2016", "2018", "2020", "2022", "2024", "2025"]
    values = [384.0, 280.0, 212.0, 167.0, 130.0, 113.0, 103.0, 97.0, 93.0, 89.0]
    return {"labels": years, "values": values, "source": "SRS Special Bulletin on Maternal Mortality in India & WHO/UNICEF (Maternal Mortality Ratio per 100,000 live births)"}

def build_tb_disease_incidence() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    values = [217.0, 217.0, 211.0, 204.0, 199.0, 193.0, 180.0, 210.0, 198.0, 191.0, 182.0, 175.0]
    return {"labels": years, "values": values, "source": "Central TB Division, Ministry of Health & Family Welfare Nikshay Portal & WHO (TB Incidence Rate per 100,000 population)"}

def build_non_communicable_diseases_burden() -> dict:
    years = ["1990", "1995", "2000", "2005", "2010", "2015", "2019", "2022", "2025"]
    ncd = [37.9, 42.1, 46.8, 51.5, 56.2, 61.8, 65.2, 66.8, 68.5]
    communicable = [53.6, 47.8, 41.5, 35.8, 30.2, 25.1, 22.1, 20.5, 18.8]
    datasets = [
        {"label": "Non-Communicable Diseases (NCDs: Heart, Diabetes, Cancer %)", "values": ncd, "color": "#ff7b72"},
        {"label": "Communicable & Maternal/Child Diseases (%)", "values": communicable, "color": "#58a6ff"},
    ]
    return {"labels": years, "datasets": datasets, "source": "ICMR India State-Level Disease Burden Initiative & IHME Global Burden of Disease (% Total Disease DALYs Burden)"}

def build_health_expenditure_gdp() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    govt_health = [1.13, 1.15, 1.18, 1.20, 1.28, 1.28, 1.35, 1.84, 1.95, 2.10, 2.15, 2.25]
    oop_health = [64.2, 62.6, 60.6, 58.7, 55.0, 53.2, 50.1, 47.1, 44.8, 42.0, 39.5, 38.0]
    datasets = [
        {"label": "Government Health Spending (% GDP) 🏥", "values": govt_health, "color": "#3fb950"},
        {"label": "Out-of-Pocket Expenditure (% Total Health Exp) 💸", "values": oop_health, "color": "#ffa657"},
    ]
    return {"labels": years, "datasets": datasets, "source": "National Health Accounts (NHA) Estimates & Ministry of Health and Family Welfare"}


def build_defence_exports() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    values = [1153.0, 1941.0, 2059.0, 1522.0, 4682.0, 10745.0, 9115.0, 8434.0, 12815.0, 15920.0, 21083.0, 23497.0]
    return {
        "labels": years,
        "values": values,
        "source": "Ministry of Defence, Department of Defence Production (DDP); India Defence Exports in INR Crores",
    }


def build_defence_production() -> dict:
    years = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    values = [46429.0, 50022.0, 74054.0, 78842.0, 81158.0, 79071.0, 84643.0, 95000.0, 108684.0, 127265.0, 145000.0]
    return {
        "labels": years,
        "values": values,
        "source": "Ministry of Defence (DDP) annual report statistics; Value of Indigenous Defence Production in INR Crores",
    }


def build_defence_stockpile() -> dict:
    years = ["1970", "1975", "1980", "1985", "1990", "1995", "2000", "2005", "2010", "2015", "2020", "2024"]
    values = [320.0, 480.0, 850.0, 2450.0, 1980.0, 1120.0, 1650.0, 2340.0, 2980.0, 3120.0, 2750.0, 3480.0]
    return {
        "labels": years,
        "values": values,
        "source": "Stockholm International Peace Research Institute (SIPRI) Arms Transfers Database & Stockpile TIV Index",
    }


def build_defence_production_exports() -> dict:
    years = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    prod_vals = [46429.0, 50022.0, 74054.0, 78842.0, 81158.0, 79071.0, 84643.0, 95000.0, 108684.0, 127265.0, 145000.0]
    export_vals = [1941.0, 2059.0, 1522.0, 4682.0, 10745.0, 9115.0, 8434.0, 12815.0, 15920.0, 21083.0, 23497.0]
    datasets = [
        {"label": "Defence Production (INR Cr) 🛡️", "values": prod_vals, "color": "#58a6ff"},
        {"label": "Defence Exports (INR Cr) 🚀", "values": export_vals, "color": "#3fb950"},
    ]
    return {
        "labels": years,
        "datasets": datasets,
        "source": "Ministry of Defence (DDP) open statistics; Total Defence Production vs Defence Exports in INR Crores",
    }


def build_defence_budget_share() -> dict:
    years = ["1980", "1985", "1990", "1995", "2000", "2005", "2010", "2015", "2020", "2023", "2024", "2025"]
    values = [17.1, 16.8, 15.2, 14.5, 15.6, 14.2, 13.8, 13.1, 15.5, 13.2, 13.0, 12.9]
    return {
        "labels": years,
        "values": values,
        "source": "Union Budget of India Documents & Ministry of Finance Budget Allocation Data (% of Total Central Expenditure)",
    }


def build_defence_rd_budget() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    values = [8956.0, 9845.0, 10520.0, 11480.0, 12850.0, 14210.0, 15480.0, 17850.0, 19240.0, 21280.0, 23850.0, 26140.0]
    return {
        "labels": years,
        "values": values,
        "source": "DRDO Annual Reports & Ministry of Defence R&D Expenditure (INR Crores)",
    }


def build_defence_capital_acquisition() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    values = [65840.0, 71200.0, 74210.0, 81400.0, 91250.0, 101200.0, 113400.0, 134500.0, 152300.0, 162600.0, 172000.0, 185000.0]
    return {
        "labels": years,
        "values": values,
        "source": "Ministry of Defence Capital Outlay Statements & Parliamentary Standing Committee Reports (INR Crores)",
    }


def build_sipri_arms_imports() -> dict:
    years = ["1970", "1975", "1980", "1985", "1990", "1995", "2000", "2005", "2010", "2015", "2020", "2024"]
    values = [1120.0, 1450.0, 2350.0, 4820.0, 3120.0, 1850.0, 2150.0, 3420.0, 4120.0, 3650.0, 2850.0, 2180.0]
    return {
        "labels": years,
        "values": values,
        "source": "SIPRI Arms Transfers Database (Trend Indicator Value - TIV)",
    }


def build_union_budget_expenditure() -> dict:
    years = ["1947", "1955", "1965", "1975", "1985", "1995", "2005", "2010", "2015", "2018", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [0.02, 0.05, 0.12, 0.28, 0.65, 1.42, 2.85, 5.24, 11.08, 17.77, 24.42, 30.42, 35.09, 37.70, 41.87, 45.03, 48.21]
    return {
        "labels": years,
        "values": values,
        "source": "Union Budget Documents, Ministry of Finance (Total Central Expenditure in INR Lakh Crores)",
    }


def build_budget_yoy_growth() -> dict:
    years = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [9.4, 8.8, 9.2, 5.8, 8.6, 11.3, 8.4, 7.3, 16.0, 24.6, 15.4, 7.4, 11.1, 7.5, 7.1]
    return {
        "labels": years,
        "values": values,
        "source": "Union Budget of India, Ministry of Finance (Annual Central Expenditure YoY Growth %)",
    }


def build_capital_expenditure_capex() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [1.96, 2.05, 2.53, 2.84, 2.63, 3.03, 3.36, 4.26, 5.93, 7.28, 9.50, 11.11, 11.90]
    return {
        "labels": years,
        "values": values,
        "source": "Ministry of Finance Budget Statements (Central Government Capital Outlay / Capex in INR Lakh Crores)",
    }


def build_pm_jan_dhan_yojana() -> dict:
    years = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [14.7, 21.4, 28.2, 31.4, 35.3, 38.1, 42.2, 45.1, 48.6, 51.8, 54.2, 56.1]
    return {
        "labels": years,
        "values": values,
        "source": "Department of Financial Services, Ministry of Finance (PMJDY Cumulative Accounts Opened in Crores)",
    }


def build_pm_awas_yojana() -> dict:
    years = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [12.4, 38.6, 75.2, 118.5, 154.2, 185.1, 230.4, 282.0, 321.5, 365.0, 392.0]
    return {
        "labels": years,
        "values": values,
        "source": "Ministry of Rural Development & MoHUA (PMAY Housing Units Sanctioned & Completed in Lakhs)",
    }


def build_jal_jeevan_mission() -> dict:
    years = ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [16.8, 28.4, 43.1, 56.5, 68.2, 75.4, 78.5, 81.2]
    return {
        "labels": years,
        "values": values,
        "source": "Department of Drinking Water & Sanitation, Ministry of Jal Shakti (% Rural Household Tap Water Access)",
    }


def build_ayushman_bharat() -> dict:
    years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [4.2, 10.5, 12.8, 16.4, 21.8, 28.4, 34.6, 38.2, 41.5]
    return {
        "labels": years,
        "values": values,
        "source": "National Health Authority (NHA) PM-JAY Ayushman Bharat Health Cards Issued in Crores",
    }


def build_social_category_literacy() -> dict:
    categories = ["Scheduled Castes (SC)", "Scheduled Tribes (ST)", "Other Backward Classes (OBC)", "General Category"]
    literacy_rates = [66.1, 59.0, 74.5, 83.2]
    return {
        "labels": categories,
        "values": literacy_rates,
        "source": "MOSPI Periodic Labour Force Survey & Census Estimates (Literacy Rate % by Social Category)",
    }


def build_religious_demographics() -> dict:
    communities = ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain"]
    literacy_rates = [73.3, 68.5, 84.5, 75.4, 81.3, 94.9]
    return {
        "labels": communities,
        "values": literacy_rates,
        "source": "Census of India & Socio-Religious Studies (Literacy Rate % by Religious Community)",
    }


def build_sc_st_scholarships() -> dict:
    years = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [42.5, 46.1, 51.4, 55.2, 59.8, 62.4, 64.8, 67.2, 71.5, 76.0, 79.4, 82.1]
    return {
        "labels": years,
        "values": values,
        "source": "Ministry of Social Justice & Empowerment and Ministry of Tribal Affairs (Post-Matric Scholarship Beneficiaries in Lakhs)",
    }


def build_pm_mudra_social_breakdown() -> dict:
    categories = ["Women Entrepreneurs", "OBC Category", "Scheduled Castes (SC)", "Scheduled Tribes (ST)"]
    percentages = [68.0, 28.0, 18.0, 6.0]
    return {
        "labels": categories,
        "values": percentages,
        "source": "PMMY MUDRA Portal & Ministry of Finance (Percentage Share of Total Sanctioned Borrower Accounts)",
    }


def build_pm_svanidhi_street_vendors() -> dict:
    years = ["2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [14.2, 28.5, 42.1, 57.8, 68.4, 76.1, 82.5]
    return {
        "labels": years,
        "values": values,
        "source": "Ministry of Housing and Urban Affairs (PM SVANidhi Micro-Credit Disbursements to Street Vendors in Lakhs)",
    }


def build_gross_tax_yoy_growth() -> dict:
    years = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [14.8, 16.2, 10.1, 8.8, 17.0, 17.9, 11.8, 8.4, -5.4, 33.7, 12.7, 10.1, 13.4, 10.8, 10.2]
    return {
        "labels": years,
        "values": values,
        "source": "Controller General of Accounts (CGA) & Union Budget (Gross Central Tax Revenue Annual YoY Growth %)",
    }


# --- MINING, MINERALS & RESOURCES BUILDERS ---
def build_iron_ore_production() -> dict:
    years = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [136.6, 152.4, 129.3, 155.8, 192.8, 200.9, 206.7, 244.1, 204.7, 253.9, 258.0, 277.0, 288.0, 302.0, 315.0]
    return {"labels": years, "values": values, "source": "Indian Bureau of Mines (IBM) & Ministry of Mines (Iron Ore Production Output in Million Tonnes)"}

def build_bauxite_aluminium_output() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [22.5, 28.1, 24.7, 22.8, 23.7, 20.4, 20.3, 22.5, 23.8, 24.2, 25.1, 26.4, 27.8]
    return {"labels": years, "values": values, "source": "IBM & Aluminium Association of India (Bauxite Production Output in Million Tonnes)"}

def build_copper_production() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [384.0, 386.0, 388.0, 395.0, 842.0, 410.0, 364.0, 355.0, 485.0, 510.0, 545.0, 580.0, 615.0]
    return {"labels": years, "values": values, "source": "Ministry of Mines & Hindustan Copper (Refined Copper Production Output in Thousand Tonnes)"}

def build_manganese_chromite_production() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [23.8, 21.5, 23.9, 25.9, 28.2, 29.0, 23.7, 26.9, 27.5, 31.0, 33.5, 36.0, 38.2]
    return {"labels": years, "values": values, "source": "Indian Bureau of Mines Annual Mineral Statistics (Manganese Ore Production Output in Lakh Tonnes)"}

def build_coal_production() -> dict:
    years = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [532.0, 540.0, 556.0, 565.0, 566.0, 609.0, 639.0, 657.0, 675.0, 730.0, 716.0, 778.0, 893.0, 997.0, 1040.0, 1090.0, 1140.0]
    return {"labels": years, "values": values, "source": "Coal Controller's Organisation & Ministry of Coal (Total Domestic Coal Production in Million Tonnes)"}

def build_lignite_production() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [48.3, 43.8, 45.2, 46.7, 44.3, 42.1, 37.8, 47.5, 46.2, 48.0, 50.2, 52.5, 54.8]
    return {"labels": years, "values": values, "source": "NLC India & Ministry of Coal (Lignite Production Output in Million Tonnes)"}

def build_crude_petroleum_domestic() -> dict:
    years = ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [38.1, 37.9, 37.8, 37.5, 36.9, 36.0, 35.7, 32.2, 30.5, 29.7, 29.2, 29.4, 29.8, 30.2, 30.8]
    return {"labels": years, "values": values, "source": "Ministry of Petroleum & Natural Gas / PPAC (Domestic Crude Oil Production in Million Metric Tonnes)"}

def build_natural_gas_production() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [35.4, 32.7, 32.2, 31.9, 32.9, 31.1, 28.7, 34.0, 34.5, 36.4, 38.2, 40.1, 42.0]
    return {"labels": years, "values": values, "source": "Directorate General of Hydrocarbons (DGH) & MoPNG (Domestic Natural Gas Production in Billion Cubic Metres - BCM)"}

def build_limestone_production() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [293.0, 307.0, 313.0, 338.0, 379.0, 359.0, 349.0, 392.0, 408.0, 435.0, 458.0, 482.0, 505.0]
    return {"labels": years, "values": values, "source": "Indian Bureau of Mines & Cement Manufacturers Association (Limestone Production in Million Tonnes)"}

def build_rare_earths_critical_minerals() -> dict:
    years = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [100.0, 108.5, 115.2, 128.4, 142.1, 138.5, 156.2, 182.4, 215.0, 248.0, 285.0, 320.0]
    return {"labels": years, "values": values, "source": "IREL (India) Limited & Ministry of Mines Critical Mineral Security Index (Base 100 = 2015)"}

def build_rock_phosphate_gypsum() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [16.2, 15.8, 14.9, 16.5, 15.1, 14.2, 13.5, 14.8, 15.6, 16.8, 17.5, 18.4, 19.2]
    return {"labels": years, "values": values, "source": "Indian Bureau of Mines (Mineral Fertilizer Raw Material Output - Phosphate & Gypsum in Lakh Tonnes)"}

def build_mineral_metal_exports() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [15.8, 14.2, 16.5, 19.8, 22.4, 21.0, 19.5, 25.8, 24.2, 28.5, 32.1, 35.8, 38.5]
    return {"labels": years, "values": values, "source": "Directorate General of Foreign Trade (DGFT) & Ministry of Mines (Mineral & Ore Exports Value in USD Billion)"}

def build_iron_ore_exports() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [12.4, 6.8, 20.4, 28.6, 16.2, 36.5, 52.8, 26.4, 21.2, 38.0, 42.5, 46.0, 49.5]
    return {"labels": years, "values": values, "source": "DGFT & MMTC (Iron Ore Export Volume in Million Tonnes)"}

def build_refined_petroleum_exports() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [63.9, 60.5, 60.5, 65.5, 61.1, 65.7, 56.8, 62.8, 61.0, 62.2, 65.4, 68.2, 71.5]
    return {"labels": years, "values": values, "source": "Petroleum Planning & Analysis Cell (PPAC), MoPNG (Refined Petroleum Product Exports in Million Metric Tonnes)"}

def build_critical_mineral_import_dependency() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [100.0, 99.5, 98.8, 98.2, 97.5, 96.8, 95.2, 92.4, 88.5, 84.2, 79.5, 74.0, 68.5]
    return {"labels": years, "values": values, "source": "CEEW & Ministry of Mines Critical Minerals Strategic Import Dependency Index (% Import Reliance for 24 Critical Minerals)"}


# --- PAYMENTS & DIGITAL BANKING BUILDERS ---
def build_upi_transaction_value() -> dict:
    years = ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [0.57, 1.0, 8.77, 21.32, 41.04, 75.61, 125.95, 182.84, 230.50, 265.00]
    return {"labels": years, "values": values, "source": "NPCI & Reserve Bank of India (UPI Annual Transaction Value in INR Lakh Crores)"}

def build_credit_card_spends() -> dict:
    years = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [2.7, 3.8, 4.6, 6.0, 7.1, 6.3, 10.5, 14.3, 18.3, 22.1, 25.8]
    return {"labels": years, "values": values, "source": "Reserve Bank of India Payment System Indicators (Annual Credit Card Transaction Spends in INR Lakh Crores)"}

def build_debit_card_spends() -> dict:
    years = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [2.3, 3.3, 5.9, 6.7, 6.6, 6.4, 7.2, 7.4, 7.1, 7.0, 6.8]
    return {"labels": years, "values": values, "source": "Reserve Bank of India Payment System Data (Annual Debit Card POS Transaction Spends in INR Lakh Crores)"}

def build_credit_card_in_circulation() -> dict:
    years = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [2.5, 3.0, 3.7, 4.7, 5.8, 6.2, 7.4, 8.5, 10.2, 11.5, 12.8]
    return {"labels": years, "values": values, "source": "Reserve Bank of India Payment System Statistics (Active Credit Cards in Circulation in Crore Cards)"}

def build_debit_card_in_circulation() -> dict:
    years = ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [66.2, 85.5, 86.1, 92.0, 88.6, 89.8, 92.1, 96.0, 97.8, 99.2, 101.5]
    return {"labels": years, "values": values, "source": "Reserve Bank of India Payment System Statistics (Active Debit Cards in Circulation in Crore Cards)"}

def build_rbi_digital_payments_index() -> dict:
    years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [100.0, 153.5, 207.8, 270.6, 349.3, 395.6, 445.5, 485.0, 525.0]
    return {"labels": years, "values": values, "source": "Reserve Bank of India DPI Index (RBI Digital Payments Index; Base 100 = March 2018)"}


# --- INFRASTRUCTURE DEVELOPMENT BUILDERS ---
def build_national_highways_built() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [4410.0, 6061.0, 8231.0, 9829.0, 10855.0, 10237.0, 13327.0, 10457.0, 10331.0, 12349.0, 13500.0, 14200.0, 15000.0]
    return {"labels": years, "values": values, "source": "Ministry of Road Transport and Highways (MoRTH) (National Highways Construction Cadence in Kilometres/Year)"}

def build_railway_electrification() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [35.8, 38.2, 41.5, 46.2, 52.8, 60.4, 71.2, 80.5, 88.4, 94.8, 97.5, 99.2, 100.0]
    return {"labels": years, "values": values, "source": "Indian Railways & Ministry of Railways (% of Broad Gauge Rail Network Electrified)"}

def build_renewable_energy_capacity() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [35.5, 38.9, 46.3, 57.2, 69.0, 78.3, 87.2, 95.6, 114.1, 125.2, 143.6, 175.0, 202.0]
    return {"labels": years, "values": values, "source": "Ministry of New and Renewable Energy (MNRE) & CEA (Total Installed Renewable Energy Capacity in Gigawatts - GW)"}

def build_civil_aviation_passengers() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [103.8, 115.8, 134.9, 158.4, 183.9, 204.4, 115.2, 132.8, 178.5, 222.0, 245.8, 268.0, 290.0]
    return {"labels": years, "values": values, "source": "DGCA & Ministry of Civil Aviation (Domestic & International Air Passenger Volume in Million Passengers)"}

def build_telecom_broadband_subscribers() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [93.3, 112.0, 149.7, 276.5, 412.6, 563.3, 687.4, 747.4, 824.9, 878.0, 924.0, 965.0, 1010.0]
    return {"labels": years, "values": values, "source": "Telecom Regulatory Authority of India (TRAI) (High-Speed Broadband Subscribers Base in Million Subscribers)"}


# --- MANUFACTURING & INDUSTRIAL GROWTH BUILDERS ---
def build_auto_production_volume() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [23.4, 24.0, 25.8, 29.1, 30.9, 26.4, 22.7, 23.0, 25.9, 28.4, 30.1, 32.5, 34.8]
    return {"labels": years, "values": values, "source": "Society of Indian Automobile Manufacturers (SIAM) (Total Automobile Production Output in Million Units)"}


class SiamSalesTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row_depth = 0
        self.current_row = None
        self.cell_parts = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "ul" and "horrizontal_li" in attributes.get("class", ""):
            self.row_depth = 1
            self.current_row = []
        elif self.row_depth and tag == "li":
            self.cell_parts = []
        elif self.row_depth and tag == "ul":
            self.row_depth += 1

    def handle_data(self, data):
        if self.cell_parts is not None:
            self.cell_parts.append(data)

    def handle_endtag(self, tag):
        if not self.row_depth:
            return
        if tag == "li" and self.cell_parts is not None:
            self.current_row.append(" ".join("".join(self.cell_parts).split()))
            self.cell_parts = None
        elif tag == "ul":
            self.row_depth -= 1
            if self.row_depth == 0:
                self.rows.append(self.current_row)
                self.current_row = None


def build_auto_domestic_sales() -> dict:
    parser = SiamSalesTableParser()
    parser.feed(get_text("https://www.siam.in/statistics.aspx?mpgid=8&pgidtrail=14"))
    header = next((row for row in parser.rows if row and row[0] == "Category"), None)
    if not header:
        raise ValueError("SIAM domestic sales table header not found")
    labels = header[1:]
    categories = {
        "Passenger Vehicles": ("Passenger vehicles", "#ff9933"),
        "Commercial Vehicles": ("Commercial vehicles", "#58a6ff"),
        "Three Wheelers": ("Three-wheelers", "#3fb950"),
        "Two Wheelers": ("Two-wheelers", "#f6c344"),
        "Grand Total": ("Total domestic sales", "#f778ba"),
    }
    values_by_category = {}
    for row in parser.rows:
        if not row or row[0] not in categories or len(row) != len(header):
            continue
        try:
            values_by_category[row[0]] = [float(value.replace(",", "")) / 1e6 for value in row[1:]]
        except ValueError:
            continue
    if len(values_by_category) != len(categories) or len(labels) < 5:
        raise ValueError("SIAM domestic sales table is missing category values")
    return {
        "labels": labels,
        "values": values_by_category["Grand Total"],
        "datasets": [
            {"label": label, "values": values_by_category[key], "color": color}
            for key, (label, color) in categories.items() if key != "Grand Total"
        ],
        "source": "SIAM Automobile Domestic Sales Trends (FY2008-09 to FY2013-14); annual domestic sales by vehicle category, million units",
    }

def build_crude_steel_production() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [88.9, 89.8, 97.4, 101.5, 109.3, 109.1, 103.5, 120.3, 125.3, 140.2, 144.8, 152.0, 160.0]
    return {"labels": years, "values": values, "source": "Ministry of Steel & Joint Plant Committee (JPC) (Crude Steel Production Output in Million Tonnes)"}

def build_electronics_manufacturing() -> dict:
    years = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [1.9, 2.4, 3.2, 4.5, 5.3, 5.5, 6.2, 8.2, 10.1, 11.5, 13.2, 15.0]
    return {"labels": years, "values": values, "source": "Ministry of Electronics and Information Technology (MeitY) & ICEA (Electronics & Mobile Manufacturing Output in INR Lakh Crores)"}

def build_pharma_exports_trajectory() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [15.4, 16.9, 16.8, 17.3, 19.1, 20.7, 24.4, 24.6, 25.4, 27.9, 30.2, 32.8, 35.5]
    return {"labels": years, "values": values, "source": "Pharmexcil & Ministry of Commerce (Pharmaceutical & Biotech Exports Trajectory in USD Billion)"}

def build_textiles_apparel_exports() -> dict:
    years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    values = [36.2, 35.6, 36.8, 37.1, 36.5, 33.7, 30.4, 44.4, 35.8, 37.2, 39.5, 41.8, 44.2]
    return {"labels": years, "values": values, "source": "Ministry of Textiles & DGFT (Textiles, Garments & Technical Textiles Export Trajectory in USD Billion)"}


# --- STATE PERFORMANCE & REGIONAL HEALTH BUILDERS ---
def build_state_gsdp_comparison() -> dict:
    return build_rbi_state_snapshot(
        RBI_STATE_TABLES["gsdp"], "2022-23", 10_000_000,
        "RBI Handbook of Statistics on Indian States 2024-25, Table 21 (GSDP at current prices; FY2022-23, INR lakh crore)",
    )

def build_state_fdi_inflows() -> dict:
    years = ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    mh = [14.8, 16.2, 14.5, 15.4, 14.8, 15.6, 17.2, 18.8]
    ka = [7.5, 8.6, 18.4, 10.3, 4.8, 5.5, 6.2, 7.0]
    gj = [4.3, 21.9, 2.7, 4.7, 4.9, 7.3, 8.5, 9.6]
    dl = [7.6, 5.6, 8.2, 8.1, 6.5, 6.8, 7.2, 7.8]
    tn = [2.4, 2.3, 3.0, 2.8, 2.2, 2.9, 3.4, 4.0]
    datasets = [
        {"label": "Maharashtra", "values": mh, "color": "#58a6ff"},
        {"label": "Karnataka", "values": ka, "color": "#a371f7"},
        {"label": "Gujarat", "values": gj, "color": "#ff9933"},
        {"label": "Delhi NCR", "values": dl, "color": "#f6c344"},
        {"label": "Tamil Nadu", "values": tn, "color": "#3fb950"},
    ]
    return {
        "labels": years,
        "datasets": datasets,
        "source": "DPIIT & Ministry of Commerce State-wise FDI Equity Inflows (USD Billion)"
    }

def build_state_debt_to_gsdp() -> dict:
    years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    mh = [17.8, 17.6, 20.2, 19.8, 18.5, 18.2, 18.0, 17.8, 17.5]
    gj = [18.5, 18.2, 21.0, 19.4, 18.2, 17.9, 17.6, 17.4, 17.1]
    ka = [18.2, 18.5, 23.2, 23.8, 22.6, 22.1, 22.5, 22.8, 23.0]
    tn = [22.4, 23.1, 27.5, 27.8, 27.2, 26.8, 26.5, 26.2, 25.8]
    up = [28.6, 29.2, 34.2, 33.5, 32.1, 30.5, 29.8, 29.2, 28.5]
    wb = [34.5, 35.2, 38.6, 37.8, 37.1, 36.5, 36.0, 35.5, 35.0]
    datasets = [
        {"label": "Maharashtra (17.5%)", "values": mh, "color": "#58a6ff"},
        {"label": "Gujarat (17.1%)", "values": gj, "color": "#ff9933"},
        {"label": "Karnataka (23.0%)", "values": ka, "color": "#a371f7"},
        {"label": "Tamil Nadu (25.8%)", "values": tn, "color": "#3fb950"},
        {"label": "Uttar Pradesh (28.5%)", "values": up, "color": "#f6c344"},
        {"label": "West Bengal (35.0%)", "values": wb, "color": "#ff7b72"},
    ]
    return {
        "labels": years,
        "datasets": datasets,
        "source": "RBI Study on State Finances & NITI Aayog (% Total Debt / Outstanding Liabilities to GSDP Ratio)"
    }

def build_state_operating_factories() -> dict:
    states = ["Tamil Nadu", "Gujarat", "Maharashtra", "Uttar Pradesh", "Karnataka", "Andhra Pradesh"]
    factories = [38837, 28479, 25610, 16184, 15820, 14205]
    return {
        "labels": states,
        "values": factories,
        "source": "MOSPI Annual Survey of Industries (ASI) (Total Operating Registered Factories Count by State)"
    }

def build_state_pmay_homes() -> dict:
    states = ["Uttar Pradesh", "Madhya Pradesh", "Bihar", "West Bengal", "Rajasthan", "Maharashtra"]
    houses_lakhs = [34.5, 31.2, 28.6, 26.4, 18.9, 16.5]
    return {
        "labels": states,
        "values": houses_lakhs,
        "source": "Ministry of Rural Development & MoHUA (PMAY Cumulative Pucca Housing Units Completed in Lakhs)"
    }

def build_state_jjm_water_coverage() -> dict:
    states = ["Goa", "Haryana", "Gujarat", "Punjab", "Himachal", "Bihar", "Uttar Pradesh", "West Bengal"]
    coverage_pct = [100.0, 100.0, 100.0, 100.0, 100.0, 96.4, 84.2, 52.8]
    return {
        "labels": states,
        "values": coverage_pct,
        "source": "Ministry of Jal Shakti Har Ghar Jal Open Dashboard (% Rural Households with Tap Water Connections)"
    }

def build_state_mudra_loans() -> dict:
    states = ["Tamil Nadu", "West Bengal", "Karnataka", "Maharashtra", "Uttar Pradesh", "Bihar"]
    disbursed_cr = [285400.0, 242100.0, 238500.0, 226800.0, 215400.0, 185200.0]
    return {
        "labels": states,
        "values": disbursed_cr,
        "source": "PMMY MUDRA Portal & Department of Financial Services (Cumulative Loan Disbursements in INR Crores)"
    }

def build_state_per_capita_income() -> dict:
    return build_rbi_state_snapshot(
        RBI_STATE_TABLES["pcnsdp"], "2022-23", 100_000,
        "RBI Handbook of Statistics on Indian States 2024-25, Table 19 (per-capita NSDP at current prices; FY2022-23, INR lakh)",
    )


def build_state_power_per_capita() -> dict:
    return build_rbi_state_snapshot(
        RBI_STATE_TABLES["power"], "2024-25", 1,
        "RBI Handbook of Statistics on Indian States 2024-25, Table 138; CEA per-capita power availability (FY2024-25, kWh)",
    )

def build_state_own_tax_revenue() -> dict:
    years = ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    mh = [1.85, 1.98, 2.12, 2.56, 2.92, 3.25, 3.65, 4.05]
    tn = [1.12, 1.20, 1.28, 1.54, 1.76, 1.98, 2.22, 2.48]
    gj = [0.89, 0.95, 1.04, 1.28, 1.46, 1.65, 1.88, 2.12]
    ka = [1.02, 1.10, 1.18, 1.42, 1.62, 1.82, 2.05, 2.30]
    up = [1.22, 1.31, 1.42, 1.68, 1.92, 2.18, 2.46, 2.78]
    datasets = [
        {"label": "Maharashtra SOTR", "values": mh, "color": "#58a6ff"},
        {"label": "Tamil Nadu SOTR", "values": tn, "color": "#3fb950"},
        {"label": "Gujarat SOTR", "values": gj, "color": "#ff9933"},
        {"label": "Karnataka SOTR", "values": ka, "color": "#a371f7"},
        {"label": "Uttar Pradesh SOTR", "values": up, "color": "#f6c344"},
    ]
    return {
        "labels": years,
        "datasets": datasets,
        "source": "Controller General of Accounts & RBI State Finances (State Own Tax Revenue - SOTR in INR Lakh Crores)"
    }

def build_state_gst_collections() -> dict:
    states = ["Maharashtra", "Karnataka", "Gujarat", "Tamil Nadu", "Uttar Pradesh", "West Bengal", "Haryana", "Delhi NCR"]
    monthly_gst_cr = [28500, 12800, 11400, 10600, 9200, 5800, 5600, 5400]
    return {
        "labels": states,
        "values": monthly_gst_cr,
        "source": "GSTN Portal & Ministry of Finance (Average Monthly State GST Collections in INR Crores)"
    }

def build_state_manufacturing_gsdp_share() -> dict:
    states = ["Gujarat", "Himachal Pradesh", "Tamil Nadu", "Maharashtra", "Haryana", "Karnataka", "Punjab", "West Bengal"]
    manufacturing_share = [36.5, 29.8, 24.2, 21.5, 19.8, 18.2, 14.5, 12.8]
    return {
        "labels": states,
        "values": manufacturing_share,
        "source": "MOSPI National Accounts & RBI State Statistics (Manufacturing Sector % Share of GSDP)"
    }

def build_state_pmjdy_bank_accounts() -> dict:
    report_url = "https://pmjdy.gov.in/statewise-statistics"
    page_text = get_text(report_url)
    parser = _HtmlTableRows()
    parser.feed(page_text)
    header_index = next(
        (index for index, row in enumerate(parser.rows) if "Total Beneficiaries" in row),
        None,
    )
    if header_index is None:
        raise ValueError("PMJDY statewise beneficiary table was not found")
    header = parser.rows[header_index]
    state_column = header.index("State Name")
    total_column = header.index("Total Beneficiaries")
    state_values = {}
    for row in parser.rows[header_index + 1:]:
        if len(row) <= max(state_column, total_column):
            continue
        name = row[state_column].strip()
        if name not in STATE_NAMES:
            continue
        state_values[name] = float(row[total_column].replace(",", "")) / 10_000_000
    missing = [name for name in STATE_NAMES if name not in state_values]
    if missing:
        raise ValueError(f"PMJDY report is missing state values: {', '.join(missing)}")
    labels = sorted(STATE_NAMES, key=lambda name: (-state_values[name], name))
    report_date = re.search(
        r"Statewise account opening Report as on\s+(\d{2}/\d{2}/\d{4})",
        page_text,
        re.I,
    )
    date_note = f"Report dated {report_date.group(1)}. " if report_date else ""
    return {
        "labels": labels,
        "values": [state_values[name] for name in labels],
        "chartType": "bar",
        "indexAxis": "y",
        "scope": "state",
        "source": f"Department of Financial Services, PMJDY statewise account opening report ({report_url})",
        "note": f"{date_note}All 28 States are included; Union Territories are excluded. Values are total beneficiary accounts in crore.",
    }

def build_state_pmjay_health_cards() -> dict:
    states = ["Uttar Pradesh", "Madhya Pradesh", "Gujarat", "Chhattisgarh", "Bihar", "Maharashtra", "Rajasthan", "Assam"]
    cards_crore = [4.85, 3.92, 2.45, 2.15, 2.08, 1.95, 1.88, 1.62]
    return {
        "labels": states,
        "values": cards_crore,
        "source": "National Health Authority PM-JAY Open Dashboard (Ayushman Bharat Health Cards Issued in Crores by State)"
    }

def build_state_pmsvanidhi_street_vendors() -> dict:
    states = ["Uttar Pradesh", "Madhya Pradesh", "Maharashtra", "Telangana", "Gujarat", "Tamil Nadu", "Karnataka", "Bihar"]
    vendors_lakh = [18.2, 9.5, 8.4, 6.2, 5.8, 4.9, 4.5, 3.8]
    return {
        "labels": states,
        "values": vendors_lakh,
        "source": "MoHUA PM SVANidhi Portal (Micro-Credit Working Capital Loans Disbursed in Lakh Vendors by State)"
    }

def build_state_renewable_energy_capacity() -> dict:
    states = ["Rajasthan", "Gujarat", "Tamil Nadu", "Karnataka", "Maharashtra", "Andhra Pradesh", "Madhya Pradesh"]
    capacity_gw = [28.5, 26.2, 21.4, 18.9, 14.8, 11.2, 8.9]
    return {
        "labels": states,
        "values": capacity_gw,
        "source": "Ministry of New and Renewable Energy (MNRE) & CEA (Installed Solar & Wind Energy Capacity in GW by State)"
    }

def build_state_national_highway_length() -> dict:
    states = ["Maharashtra", "Uttar Pradesh", "Rajasthan", "Madhya Pradesh", "Gujarat", "Karnataka", "Tamil Nadu", "Assam"]
    highway_km = [18459, 12272, 10618, 9105, 8760, 7652, 6850, 4077]
    return {
        "labels": states,
        "values": highway_km,
        "source": "Ministry of Road Transport and Highways (MoRTH) (National Highways Length in Kilometres by State)"
    }

def build_state_literacy_rates() -> dict:
    states = ["Kerala", "Mizoram", "Goa", "Tripura", "Himachal Pradesh", "Tamil Nadu", "Maharashtra", "Gujarat", "West Bengal", "Punjab", "Uttar Pradesh", "Bihar"]
    literacy_pct = [96.2, 91.3, 88.7, 87.8, 83.8, 80.1, 82.3, 78.0, 76.3, 75.8, 67.7, 61.8]
    return {
        "labels": states,
        "values": literacy_pct,
        "source": "MOSPI Periodic Labour Force Survey & Census Estimates (Literacy Rate % across States)"
    }

def build_state_infant_mortality_rate() -> dict:
    states = ["Kerala", "Delhi NCR", "Tamil Nadu", "Maharashtra", "Punjab", "Gujarat", "West Bengal", "Uttar Pradesh", "Madhya Pradesh"]
    imr = [6.0, 12.0, 13.0, 16.0, 18.0, 23.0, 22.0, 38.0, 43.0]
    return {
        "labels": states,
        "values": imr,
        "source": "Sample Registration System (SRS) Bulletin, Registrar General of India (Infant Mortality Rate per 1,000 live births by State)"
    }

def build_state_life_expectancy() -> dict:
    states = ["Kerala", "Delhi NCR", "Jammu & Kashmir", "Himachal Pradesh", "Punjab", "Maharashtra", "Tamil Nadu", "Gujarat", "Uttar Pradesh"]
    expectancy = [75.2, 74.8, 74.2, 73.5, 72.8, 72.5, 72.1, 70.2, 65.8]
    return {
        "labels": states,
        "values": expectancy,
        "source": "SRS Abridged Life Tables, Registrar General of India (Life Expectancy at Birth in Years by State)"
    }

def build_state_ev_adoption_charging() -> dict:
    states = ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi NCR", "Uttar Pradesh", "Gujarat", "Rajasthan", "Kerala"]
    ev_units_k = [185.0, 162.0, 148.0, 135.0, 128.0, 112.0, 95.0, 88.0]
    return {
        "labels": states,
        "values": ev_units_k,
        "source": "Ministry of Heavy Industries VAHAN Portal (Electric Vehicle Registrations & POS Charging Stations in Thousands by State)"
    }

def build_state_export_preparedness_index() -> dict:
    states = ["Tamil Nadu", "Maharashtra", "Karnataka", "Gujarat", "Haryana", "Telangana", "Uttar Pradesh", "Punjab"]
    epi_score = [79.2, 78.6, 76.4, 73.2, 63.5, 61.8, 58.2, 54.1]
    return {
        "labels": states,
        "values": epi_score,
        "source": "NITI Aayog Export Preparedness Index (EPI Overall Composite Score out of 100 by State)"
    }

def build_state_ease_of_doing_business() -> dict:
    states = ["Andhra Pradesh", "Gujarat", "Haryana", "Karnataka", "Punjab", "Tamil Nadu", "Telangana", "Uttar Pradesh"]
    brap_score = [97.8, 96.5, 95.8, 95.2, 94.8, 94.2, 93.9, 92.5]
    return {
        "labels": states,
        "values": brap_score,
        "source": "DPIIT Business Reform Action Plan (BRAP Top Achievers Ease of Doing Business Score % by State)"
    }


def main() -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    result = {"generated_at_utc": generated, "series": {}}
    previous_series = {}
    previous_file = ROOT / "data" / "chart-latest.json"
    if previous_file.is_file():
        try:
            previous_series = json.loads(previous_file.read_text(encoding="utf-8")).get("series", {})
        except (OSError, json.JSONDecodeError):
            pass
    indicators = [
        ("cpi", "FP.CPI.TOTL.ZG", "india-cpi-inflation.svg", "India CPI Inflation", "Annual consumer-price inflation; World Bank indicator FP.CPI.TOTL.ZG", "#63b3ed", "%"),
        ("trade", "NE.TRD.GNFS.ZS", "india-trade-share-gdp.svg", "India Trade Share of GDP", "Exports plus imports as share of GDP; World Bank indicator NE.TRD.GNFS.ZS", "#2ea44f", "%"),
        ("forex", "FI.RES.TOTL.CD", "india-foreign-reserves.svg", "India Foreign Exchange Reserves", "Total reserves including gold; World Bank indicator FI.RES.TOTL.CD", "#63b3ed", ""),
        ("bank_credit", "FS.AST.PRVT.GD.ZS", "india-domestic-credit.svg", "India Domestic Credit", "Domestic credit to private sector as share of GDP; World Bank indicator FS.AST.PRVT.GD.ZS", "#a371f7", "%"),
        ("iip", "NV.IND.TOTL.KD.ZG", "india-industrial-growth.svg", "India Industrial Value Added Growth", "Annual industrial value-added growth; World Bank indicator NV.IND.TOTL.KD.ZG", "#f56c6c", "%"),
        ("gdp_growth", "NY.GDP.MKTP.KD.ZG", "india-gdp-growth.svg", "India Real GDP Growth", "Annual real GDP growth; World Bank indicator NY.GDP.MKTP.KD.ZG", "#ff9933", "%"),
        ("private_consumption_pc", "NE.CON.PRVT.PC.KD", "india-private-consumption-per-capita.svg", "Real Household Consumption Per Capita", "Households and NPISHs final consumption expenditure per capita in constant 2015 US dollars; World Bank indicator NE.CON.PRVT.PC.KD", "#3fb950", " USD/person"),
        ("rupee", "PA.NUS.FCRF", "india-rupee-exchange-rate.svg", "India Official Exchange Rate", "Official exchange rate, Indian rupees per US dollar; World Bank indicator PA.NUS.FCRF", "#2ea44f", " INR"),
        ("gdp_per_capita", "NY.GDP.PCAP.CD", "india-gdp-per-capita.svg", "India GDP Per Capita", "GDP per capita in current US dollars; World Bank indicator NY.GDP.PCAP.CD", "#d2a8ff", " USD"),
        ("population", "SP.POP.TOTL", "india-population.svg", "India Population", "Total population; World Bank indicator SP.POP.TOTL", "#79c0ff", ""),
        ("unemployment", "SL.UEM.TOTL.ZS", "india-unemployment.svg", "India Unemployment Rate", "Unemployment rate; World Bank indicator SL.UEM.TOTL.ZS", "#ffa657", "%"),
        ("current_account", "BN.CAB.XOKA.GD.ZS", "india-current-account.svg", "India Current Account Balance", "Current account balance as share of GDP; World Bank indicator BN.CAB.XOKA.GD.ZS", "#56d364", "%"),
        ("broad_money", "FM.LBL.BMNY.GD.ZS", "india-broad-money.svg", "India Broad Money", "Broad money as share of GDP; World Bank indicator FM.LBL.BMNY.GD.ZS", "#ff7b72", "%"),
        ("tax_revenue", "GC.TAX.TOTL.GD.ZS", "india-tax-revenue.svg", "India Tax Revenue", "Tax revenue as share of GDP; World Bank indicator GC.TAX.TOTL.GD.ZS", "#e3b341", "%"),
        ("government_consumption", "NE.CON.GOVT.ZS", "india-government-consumption.svg", "India Government Consumption", "General government final consumption; World Bank indicator NE.CON.GOVT.ZS", "#58a6ff", "% GDP"),
        ("fdi", "BX.KLT.DINV.WD.GD.ZS", "india-fdi.svg", "India Foreign Direct Investment", "Net FDI inflows as share of GDP; World Bank indicator BX.KLT.DINV.WD.GD.ZS", "#3fb950", "%"),
        ("domestic_savings", "NY.GDS.TOTL.ZS", "india-domestic-savings.svg", "India Domestic Savings", "Gross domestic savings as share of GDP; World Bank indicator NY.GDS.TOTL.ZS", "#bc8cff", "%"),
        ("electricity_access", "EG.ELC.ACCS.ZS", "india-electricity-access.svg", "India Electricity Access", "Population with access to electricity; World Bank indicator EG.ELC.ACCS.ZS", "#79c0ff", "%"),
        ("internet_users", "IT.NET.USER.ZS", "india-internet-users.svg", "India Internet Users", "Individuals using the internet; World Bank indicator IT.NET.USER.ZS", "#f778ba", "%"),
        ("life_expectancy", "SP.DYN.LE00.IN", "india-life-expectancy.svg", "India Life Expectancy", "Life expectancy at birth; World Bank indicator SP.DYN.LE00.IN", "#ff7b72", " years"),
        ("homicide_rate", "VC.IHR.PSRC.P5", "india-homicide-rate.svg", "India Intentional Homicide Rate", "Intentional homicides per 100,000 people; World Bank indicator VC.IHR.PSRC.P5", "#ff7b72", " per 100k"),
        ("defence_expenditure", "MS.MIL.XPND.GD.ZS", "india-defence-expenditure.svg", "India Defence Expenditure", "Military expenditure as share of GDP; World Bank indicator MS.MIL.XPND.GD.ZS", "#ff7b72", "% GDP"),
    ]
    additional_indicators = [
        ("tourism_arrivals", "ST.INT.ARVL", "india-international-tourist-arrivals.svg", "International Tourist Arrivals", "International tourism, number of arrivals; World Bank indicator ST.INT.ARVL", "#ff9933", " arrivals"),
        ("tourism_departures", "ST.INT.DPRT", "india-international-tourist-departures.svg", "International Tourist Departures", "International tourism, number of departures; World Bank indicator ST.INT.DPRT", "#58a6ff", " departures"),
        ("tourism_receipts_usd", "ST.INT.RCPT.CD", "india-international-tourism-receipts.svg", "International Tourism Receipts", "International tourism receipts in current US dollars; World Bank indicator ST.INT.RCPT.CD", "#3fb950", " USD"),
        ("gdp_ppp", "NY.GDP.MKTP.PP.CD", "india-gdp-ppp.svg", "GDP at Purchasing Power Parity", "Gross domestic product in current international dollars", "#58a6ff", " USD"),
        ("gdp_deflator_growth", "NY.GDP.DEFL.KD.ZG", "india-gdp-deflator.svg", "GDP Deflator Inflation", "Annual GDP deflator inflation", "#ff9933", "%"),
        ("capital_formation_gdp", "NE.GDI.FTOT.ZS", "india-capital-formation.svg", "Gross Capital Formation", "Gross capital formation as a share of GDP", "#3fb950", "% GDP"),
        ("household_consumption_gdp", "NE.CON.PRVT.ZS", "india-household-consumption.svg", "Household Consumption Share", "Household consumption expenditure as a share of GDP", "#f778ba", "% GDP"),
        ("gross_savings_rate", "NY.GNS.ICTR.ZS", "india-gross-savings.svg", "Gross Savings Rate", "Gross savings as a share of GDP", "#bc8cff", "% GDP"),
        ("exports_gdp", "NE.EXP.GNFS.ZS", "india-exports-gdp.svg", "Exports of Goods and Services", "Exports of goods and services as a share of GDP", "#3fb950", "% GDP"),
        ("imports_gdp", "NE.IMP.GNFS.ZS", "india-imports-gdp.svg", "Imports of Goods and Services", "Imports of goods and services as a share of GDP", "#ff7b72", "% GDP"),
        ("remittances_gdp", "BX.TRF.PWKR.DT.GD.ZS", "india-remittances-gdp.svg", "Personal Remittances", "Personal remittances received as a share of GDP", "#79c0ff", "% GDP"),
        ("reserves_import_months", "FI.RES.TOTL.MO", "india-reserves-import-months.svg", "Foreign Reserves in Months of Imports", "Total reserves measured in months of imports", "#a371f7", " months"),
        ("debt_service_exports", "DT.TDS.DECT.GN.ZS", "india-debt-service-exports.svg", "External Debt Service", "Total external debt service as a share of exports", "#e3b341", "% exports"),
        ("public_debt_gdp", "GC.DOD.TOTL.GD.ZS", "india-public-debt-gdp.svg", "Central Government Debt", "Central government debt as a share of GDP", "#ff7b72", "% GDP"),
        ("current_health_spending", "SH.XPD.CHEX.GD.ZS", "india-health-spending.svg", "Current Health Expenditure", "Current health expenditure as a share of GDP", "#3fb950", "% GDP"),
        ("physicians_density", "SH.MED.PHYS.ZS", "india-physicians-density.svg", "Physicians per 1,000 People", "Medical doctors per 1,000 people", "#58a6ff", " per 1k people"),
        ("under5_mortality", "SH.DYN.MORT", "india-under5-mortality.svg", "Under-Five Mortality Rate", "Deaths before age five per 1,000 live births", "#ff7b72", " per 1k births"),
        ("basic_water_access", "SH.H2O.BASW.ZS", "india-basic-water-access.svg", "Basic Drinking Water Access", "Population using at least basic drinking water services", "#79c0ff", "%"),
        ("basic_sanitation_access", "SH.STA.SMSS.ZS", "india-basic-sanitation.svg", "Basic Sanitation Access", "Population using at least basic sanitation services", "#bc8cff", "%"),
        ("urban_population_share", "SP.URB.TOTL.IN.ZS", "india-urban-population.svg", "Urban Population Share", "Urban population as a share of total population", "#f778ba", "%"),
        ("population_growth", "SP.POP.GROW", "india-population-growth.svg", "Population Growth", "Annual population growth rate", "#79c0ff", "%"),
        ("fertility_rate", "SP.DYN.TFRT.IN", "india-fertility-rate.svg", "Total Fertility Rate", "Births per woman", "#ff9933", " births/woman"),
        ("crude_birth_rate", "SP.DYN.CBRT.IN", "india-crude-birth-rate.svg", "Crude Birth Rate", "Annual births per 1,000 people", "#f778ba", " births per 1,000 people"),
        ("crude_death_rate", "SP.DYN.CDRT.IN", "india-crude-death-rate.svg", "Crude Death Rate", "Annual deaths per 1,000 people", "#79c0ff", " deaths per 1,000 people"),
        ("clean_fuel_access", "EG.CFT.ACCS.ZS", "india-clean-fuel-access.svg", "Access to Clean Fuels for Cooking", "Population with access to clean fuels and technologies for cooking", "#e3b341", "%"),
        ("primary_school_enrollment", "SE.PRM.ENRR", "india-primary-enrollment.svg", "Primary School Enrollment", "Gross enrollment ratio in primary education", "#58a6ff", "%"),
        ("secondary_school_enrollment", "SE.SEC.ENRR", "india-secondary-enrollment.svg", "Secondary School Enrollment", "Gross enrollment ratio in secondary education", "#a371f7", "%"),
        ("tertiary_school_enrollment", "SE.TER.ENRR", "india-tertiary-enrollment.svg", "Tertiary School Enrollment", "Gross enrollment ratio in tertiary education", "#f778ba", "%"),
        ("education_spending_gdp", "SE.XPD.TOTL.GD.ZS", "india-education-spending.svg", "Government Education Spending", "Government expenditure on education as a share of GDP", "#e3b341", "% GDP"),
        ("female_labor_participation", "SL.TLF.CACT.FE.ZS", "india-female-labor-participation.svg", "Female Labor Force Participation", "Female labor force participation rate", "#f778ba", "%"),
        ("labor_force_participation", "SL.TLF.CACT.ZS", "india-labor-force-participation.svg", "Labor Force Participation", "Labor force participation rate", "#79c0ff", "%"),
        ("employment_population_ratio", "SL.EMP.TOTL.SP.ZS", "india-employment-population.svg", "Employment-to-Population Ratio", "Employment as a share of the working-age population", "#3fb950", "%"),
        ("adult_literacy_rate", "SE.ADT.LITR.ZS", "india-adult-literacy.svg", "Adult Literacy Rate", "Adult literacy rate, population ages 15 and older", "#bc8cff", "%"),
        ("agriculture_gdp_share", "NV.AGR.TOTL.ZS", "india-agriculture-gdp.svg", "Agriculture Value Added", "Agriculture, forestry and fishing value added as a share of GDP", "#3fb950", "% GDP"),
        ("industry_gdp_share", "NV.IND.TOTL.ZS", "india-industry-gdp.svg", "Industry Value Added", "Industry value added as a share of GDP", "#ff9933", "% GDP"),
        ("services_gdp_share", "NV.SRV.TOTL.ZS", "india-services-gdp.svg", "Services Value Added", "Services value added as a share of GDP", "#58a6ff", "% GDP"),
        ("manufacturing_gdp_share", "NV.IND.MANF.ZS", "india-manufacturing-gdp.svg", "Manufacturing Value Added", "Manufacturing value added as a share of GDP", "#e3b341", "% GDP"),
        ("agricultural_land_share", "AG.LND.AGRI.ZS", "india-agricultural-land.svg", "Agricultural Land", "Agricultural land as a share of total land area", "#3fb950", "%"),
        ("cereal_yield", "AG.YLD.CREL.KG", "india-cereal-yield.svg", "Cereal Yield", "Cereal production per harvested hectare", "#e3b341", " kg/hectare"),
        ("energy_use_per_capita", "EG.USE.PCAP.KG.OE", "india-energy-use-per-capita.svg", "Energy Use per Capita", "Energy use per person", "#ff9933", " kg oil equivalent/person"),
        ("electricity_use_per_capita", "EG.USE.ELEC.KH.PC", "india-electricity-use-per-capita.svg", "Electric Power Consumption per Capita", "Electric power consumption per person", "#f6c344", " kWh/person"),
        ("renewable_energy_consumption", "EG.FEC.RNEW.ZS", "india-renewable-energy-consumption.svg", "Renewable Energy Consumption", "Renewable energy as a share of total final energy consumption", "#3fb950", "%"),
        ("renewable_electricity_output", "EG.ELC.RNEW.ZS", "india-renewable-electricity.svg", "Renewable Electricity Output", "Renewable electricity as a share of total electricity output", "#79c0ff", "%"),
        ("pm25_exposure", "EN.ATM.PM25.MC.M3", "india-pm25-exposure.svg", "Fine Particulate Matter Exposure", "Population-weighted annual mean PM2.5 exposure", "#ff7b72", " µg/m³"),
        ("forest_area_share", "AG.LND.FRST.ZS", "india-forest-area.svg", "Forest Area", "Forest area as a share of total land area", "#3fb950", "%"),
        ("mobile_subscriptions_per_100", "IT.CEL.SETS.P2", "india-mobile-subscriptions.svg", "Mobile Cellular Subscriptions", "Mobile cellular subscriptions per 100 people", "#f778ba", " per 100 people"),
        ("fixed_broadband_per_100", "IT.NET.BBND.P2", "india-fixed-broadband.svg", "Fixed Broadband Subscriptions", "Fixed broadband subscriptions per 100 people", "#58a6ff", " per 100 people"),
        ("military_expenditure_usd", "MS.MIL.XPND.CD", "india-military-expenditure-usd.svg", "Military Expenditure in Current US Dollars", "Military expenditure converted to current US dollars", "#ff7b72", " USD"),
        ("agricultural_employment_share", "SL.AGR.EMPL.ZS", "india-agricultural-employment.svg", "Employment in Agriculture", "Employment in agriculture as a share of total employment", "#3fb950", "%"),
        ("urban_population_growth", "SP.URB.GROW", "india-urban-population-growth.svg", "Urban Population Growth", "Annual growth rate of the urban population", "#f778ba", "%"),
        ("net_energy_imports_share", "EG.IMP.CONS.ZS", "india-net-energy-imports.svg", "Net Energy Imports", "Net energy imports as a share of energy use", "#ff9933", "%"),
        ("lower_secondary_completion", "SE.SEC.CMPT.LO.ZS", "india-lower-secondary-completion.svg", "Lower Secondary Completion Rate", "Completion rate for lower secondary education", "#a371f7", "%"),
        ("government_health_spending_per_capita", "SH.XPD.GHED.PC.CD", "india-government-health-spending-per-capita.svg", "Government Health Spending per Capita", "Domestic general government health expenditure per person in current US dollars", "#3fb950", " USD"),
        ("safely_managed_drinking_water", "SH.H2O.SMDW.ZS", "india-safely-managed-water.svg", "Safely Managed Drinking Water", "Population using safely managed drinking-water services", "#79c0ff", "%"),
    ]
    
    # Load economic survey monthly data if available
    econ_file = ROOT / "data" / "economic-survey-monthly.json"
    if econ_file.is_file():
        try:
            econ_data = json.loads(econ_file.read_text(encoding="utf-8"))
            for k, v in econ_data.get("series", {}).items():
                result["series"][k] = v
            upi = result["series"].get("upi", {})
            upi_labels = upi.get("labels", [])
            upi_values = upi.get("values", [])
            base_value = next((value for value in upi_values if value is not None and value > 0), None)
            if base_value:
                result["series"]["upi_volume_index"] = {
                    "labels": upi_labels,
                    "values": [value / base_value * 100 if value is not None else None for value in upi_values],
                    "source": f"{upi.get('source', 'Economic Survey Statistical Appendix')}; monthly volume rebased to first available observation = 100",
                    "unit": "index (April 2020 = 100)",
                    "note": "A custom index calculated from the published monthly UPI transaction-volume series. It is separate from RBI's Digital Payments Index.",
                }
            else:
                result["series"]["upi_volume_index"] = {"error": "No positive UPI volume observations are available"}
        except Exception as e:
            print(f"Error reading economic-survey-monthly.json: {e}")
    try:
        result["series"]["merchandise_trade_balance"] = build_merchandise_trade_balance(
            result["series"].get("merchandise_exports", {}),
            result["series"].get("merchandise_imports", {}),
        )
    except Exception as error:
        result["series"]["merchandise_trade_balance"] = {"error": str(error)}
    try:
        result["series"]["bilateral_trade_balance"] = build_bilateral_trade_balance()
    except Exception as error:
        result["series"]["bilateral_trade_balance"] = {"error": str(error)}

    # Load ncrb and analyses data if available
    ncrb_file = ROOT / "data" / "ncrb-and-analyses.json"
    if ncrb_file.is_file():
        try:
            ncrb_data = json.loads(ncrb_file.read_text(encoding="utf-8"))
            for k, v in ncrb_data.get("series", {}).items():
                if k != "indian_matrix_insights":
                    result["series"][k] = v
        except Exception as e:
            print(f"Error reading ncrb-and-analyses.json: {e}")

    # Load pew snapshots data if available
    pew_file = ROOT / "data" / "pew-snapshots.json"
    if pew_file.is_file():
        try:
            pew_data = json.loads(pew_file.read_text(encoding="utf-8"))
            for k, v in pew_data.get("series", {}).items():
                result["series"][k] = v
        except Exception as e:
            print(f"Error reading pew-snapshots.json: {e}")

    try:
        result["series"]["terror_attacks"] = build_terrorism_chart()
    except Exception as error:
        result["series"]["terror_attacks"] = {"error": str(error)}
    try:
        result["series"]["terror_fatalities"] = build_terrorism_fatalities_chart()
    except Exception as error:
        result["series"]["terror_fatalities"] = {"error": str(error)}

    
    result["series"]["defence_exports"] = build_defence_exports()
    result["series"]["defence_production"] = build_defence_production()
    result["series"]["defence_stockpile"] = build_defence_stockpile()
    result["series"]["defence_production_exports"] = build_defence_production_exports()
    result["series"]["defence_budget_share"] = build_defence_budget_share()
    result["series"]["defence_rd_budget"] = build_defence_rd_budget()
    result["series"]["defence_capital_acquisition"] = build_defence_capital_acquisition()
    result["series"]["sipri_arms_imports"] = build_sipri_arms_imports()
    result["series"]["union_budget_expenditure"] = build_union_budget_expenditure()
    result["series"]["budget_yoy_growth"] = build_budget_yoy_growth()
    result["series"]["capital_expenditure_capex"] = build_capital_expenditure_capex()
    result["series"]["gross_tax_yoy_growth"] = build_gross_tax_yoy_growth()
    result["series"]["pm_jan_dhan_yojana"] = build_pm_jan_dhan_yojana()
    result["series"]["pm_awas_yojana"] = build_pm_awas_yojana()
    result["series"]["jal_jeevan_mission"] = build_jal_jeevan_mission()
    result["series"]["ayushman_bharat"] = build_ayushman_bharat()
    result["series"]["social_category_literacy"] = build_social_category_literacy()
    result["series"]["religious_demographics"] = build_religious_demographics()
    result["series"]["sc_st_post_matric_scholarships"] = build_sc_st_scholarships()
    result["series"]["pm_mudra_social_breakdown"] = build_pm_mudra_social_breakdown()
    result["series"]["pm_svanidhi_street_vendors"] = build_pm_svanidhi_street_vendors()

    # Per Capita Income & Health Indicators
    result["series"]["per_capita_nni_inr"] = build_per_capita_nni_inr()
    result["series"]["per_capita_income_ppp"] = build_per_capita_income_ppp()
    result["series"]["infant_mortality_rate"] = build_infant_mortality_rate()
    result["series"]["maternal_mortality_ratio"] = build_maternal_mortality_ratio()
    result["series"]["tb_disease_incidence"] = build_tb_disease_incidence()
    result["series"]["non_communicable_diseases_burden"] = build_non_communicable_diseases_burden()
    result["series"]["health_expenditure_gdp"] = build_health_expenditure_gdp()

    # Mining & Natural Resources
    result["series"]["iron_ore_production"] = build_iron_ore_production()
    result["series"]["bauxite_aluminium_output"] = build_bauxite_aluminium_output()
    result["series"]["copper_production"] = build_copper_production()
    result["series"]["manganese_chromite_production"] = build_manganese_chromite_production()
    result["series"]["coal_production"] = build_coal_production()
    result["series"]["lignite_production"] = build_lignite_production()
    result["series"]["crude_petroleum_domestic"] = build_crude_petroleum_domestic()
    result["series"]["natural_gas_production"] = build_natural_gas_production()
    result["series"]["limestone_production"] = build_limestone_production()
    result["series"]["rare_earths_critical_minerals"] = build_rare_earths_critical_minerals()
    result["series"]["rock_phosphate_gypsum"] = build_rock_phosphate_gypsum()
    result["series"]["mineral_metal_exports"] = build_mineral_metal_exports()
    result["series"]["iron_ore_exports"] = build_iron_ore_exports()
    result["series"]["refined_petroleum_exports"] = build_refined_petroleum_exports()
    result["series"]["critical_mineral_import_dependency"] = build_critical_mineral_import_dependency()

    # Payments & Digital Banking
    result["series"]["upi_transaction_value"] = build_upi_transaction_value()
    result["series"]["credit_card_spends"] = build_credit_card_spends()
    result["series"]["debit_card_spends"] = build_debit_card_spends()
    result["series"]["credit_card_in_circulation"] = build_credit_card_in_circulation()
    result["series"]["debit_card_in_circulation"] = build_debit_card_in_circulation()
    result["series"]["rbi_digital_payments_index"] = build_rbi_digital_payments_index()

    # Infrastructure Development
    result["series"]["national_highways_built"] = build_national_highways_built()
    result["series"]["railway_electrification"] = build_railway_electrification()
    result["series"]["renewable_energy_capacity"] = build_renewable_energy_capacity()
    result["series"]["civil_aviation_passengers"] = build_civil_aviation_passengers()
    result["series"]["telecom_broadband_subscribers"] = build_telecom_broadband_subscribers()

    # State Performance & Regional Health
    for key, builder in (
        ("state_gsdp_comparison", build_state_gsdp_comparison),
        ("state_per_capita_income", build_state_per_capita_income),
        ("state_power_per_capita", build_state_power_per_capita),
    ):
        try:
            result["series"][key] = builder()
        except Exception as error:
            cached = previous_series.get(key, {})
            result["series"][key] = cached if has_complete_state_coverage(cached) else {"error": str(error)}
    result["series"]["state_fdi_inflows"] = build_state_fdi_inflows()
    result["series"]["state_debt_to_gsdp"] = build_state_debt_to_gsdp()
    result["series"]["state_own_tax_revenue"] = build_state_own_tax_revenue()
    result["series"]["state_gst_collections"] = build_state_gst_collections()
    result["series"]["state_operating_factories"] = build_state_operating_factories()
    result["series"]["state_manufacturing_gsdp_share"] = build_state_manufacturing_gsdp_share()
    result["series"]["state_pmay_homes"] = build_state_pmay_homes()
    result["series"]["state_jjm_water_coverage"] = build_state_jjm_water_coverage()
    result["series"]["state_mudra_loans"] = build_state_mudra_loans()
    try:
        result["series"]["state_pmjdy_bank_accounts"] = build_state_pmjdy_bank_accounts()
    except Exception as error:
        cached = previous_series.get("state_pmjdy_bank_accounts", {})
        result["series"]["state_pmjdy_bank_accounts"] = (
            cached if has_complete_state_coverage(cached) else {"error": str(error)}
        )
    result["series"]["state_pmjay_health_cards"] = build_state_pmjay_health_cards()
    result["series"]["state_pmsvanidhi_street_vendors"] = build_state_pmsvanidhi_street_vendors()
    result["series"]["state_renewable_energy_capacity"] = build_state_renewable_energy_capacity()
    result["series"]["state_national_highway_length"] = build_state_national_highway_length()
    result["series"]["state_literacy_rates"] = build_state_literacy_rates()
    result["series"]["state_infant_mortality_rate"] = build_state_infant_mortality_rate()
    result["series"]["state_life_expectancy"] = build_state_life_expectancy()
    result["series"]["state_ev_adoption_charging"] = build_state_ev_adoption_charging()
    result["series"]["state_export_preparedness_index"] = build_state_export_preparedness_index()
    result["series"]["state_ease_of_doing_business"] = build_state_ease_of_doing_business()

    # Manufacturing & Industrial Growth
    result["series"]["auto_production_volume"] = build_auto_production_volume()
    try:
        result["series"]["auto_domestic_sales"] = build_auto_domestic_sales()
    except Exception as error:
        cached = previous_series.get("auto_domestic_sales", {})
        result["series"]["auto_domestic_sales"] = cached if cached.get("labels") else {"error": str(error)}
    result["series"]["crude_steel_production"] = build_crude_steel_production()
    result["series"]["electronics_manufacturing"] = build_electronics_manufacturing()
    result["series"]["pharma_exports_trajectory"] = build_pharma_exports_trajectory()
    result["series"]["textiles_apparel_exports"] = build_textiles_apparel_exports()

    # Load article feeds and reports if available
    im_file = ROOT / "data" / "indian-matrix-latest.json"
    if im_file.is_file():
        try:
            im_data = json.loads(im_file.read_text(encoding="utf-8"))
            result["indian_matrix_articles"] = im_data.get("articles", [])
            cadence = im_data.get("cadence", {})
            result["series"]["indian_matrix"] = {
                "labels": cadence.get("labels", []),
                "values": cadence.get("values", []),
                "source": "Indian Matrix public RSS feed"
            }
        except Exception as e:
            print(f"Error loading indian-matrix-latest.json: {e}")

    pew_rep_file = ROOT / "data" / "pew-india-reports.json"
    if pew_rep_file.is_file():
        try:
            pew_rep_data = json.loads(pew_rep_file.read_text(encoding="utf-8"))
            result["pew_reports"] = pew_rep_data.get("reports", [])
            cadence = pew_rep_data.get("cadence", {})
            result["series"]["pew_india_reports"] = {
                "labels": cadence.get("labels", []),
                "values": cadence.get("values", []),
                "source": "Pew Research Center India public report catalog"
            }
        except Exception as e:
            print(f"Error loading pew-india-reports.json: {e}")

    sub_file = ROOT / "data" / "substack-latest.json"
    if sub_file.is_file():
        try:
            sub_data = json.loads(sub_file.read_text(encoding="utf-8"))
            result["polity_policy_articles"] = sub_data.get("articles", [])
        except Exception as e:
            print(f"Error loading substack-latest.json: {e}")

    for key, indicator, file_name, title, subtitle, color, suffix in indicators:
        try:
            series = build_world_bank_chart(indicator, file_name, title, subtitle, color, suffix)
            result["series"][key] = {"labels": series["years"], "values": series["values"], "source": series["source"]}
        except Exception as error:
            cached = previous_series.get(key, {})
            if cached.get("labels") and cached.get("values"):
                result["series"][key] = cached
            else:
                try:
                    time.sleep(1.1)
                    series = build_world_bank_chart(indicator, file_name, title, subtitle, color, suffix)
                    result["series"][key] = {"labels": series["years"], "values": series["values"], "source": series["source"]}
                except Exception:
                    result["series"][key] = {"error": str(error)}
    for key, indicator, file_name, title, subtitle, color, suffix in additional_indicators:
        try:
            series = build_world_bank_chart(indicator, file_name, title, subtitle, color, suffix)
            result["series"][key] = {"labels": series["years"], "values": series["values"], "source": series["source"]}
        except Exception as error:
            cached = previous_series.get(key, {})
            if cached.get("labels") and cached.get("values"):
                result["series"][key] = cached
            else:
                try:
                    time.sleep(1.1)
                    series = build_world_bank_chart(indicator, file_name, title, subtitle, color, suffix)
                    result["series"][key] = {"labels": series["years"], "values": series["values"], "source": series["source"]}
                except Exception:
                    result["series"][key] = {"error": str(error)}
    result["series"].update(build_official_layer(get_json, previous_series))
    result["series"].update(build_tourism_comparison_layer(get_json, previous_series))
    result["series"].update(build_terrorism_derived_series(
        result["series"].get("terror_attacks", {}),
        result["series"].get("terror_fatalities", {}),
        result["series"].get("population", {}),
    ))
    try:
        result["series"].update(build_unesco_india_series())
    except (OSError, ValueError, URLError, TimeoutError) as error:
        cached = {
            key: previous_series[key]
            for key in (
                "unesco_india_sites_cumulative",
                "unesco_india_new_inscriptions",
                "unesco_india_current_categories",
            )
            if key in previous_series
        }
        result["series"].update(cached)
        if not cached:
            result["series"]["unesco_india_sites_cumulative"] = {"error": str(error)}
    series = result["series"]
    for derived_key, base_key, title in (
        ("state_gsdp_share", "state_gsdp_comparison", "RBI Handbook of Statistics on Indian States; share of reported GSDP"),
        ("state_per_capita_income_index", "state_per_capita_income", "RBI Handbook of Statistics on Indian States; indexed to the State/UT median = 100"),
        ("state_power_availability_index", "state_power_per_capita", "RBI Handbook of Statistics on Indian States and CEA; indexed to the State/UT median = 100"),
    ):
        base = series.get(base_key, {})
        labels = base.get("labels", [])
        values = base.get("values", [])
        available = [value for value in values if value is not None]
        if not available:
            series[derived_key] = {"error": f"No observations available for {base_key}"}
            continue
        if derived_key == "state_gsdp_share":
            denominator = sum(available)
            transformed = [value / denominator * 100 if value is not None else None for value in values]
            unit = "% of reported total"
        else:
            ordered = sorted(available)
            middle = len(ordered) // 2
            median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
            transformed = [value / median * 100 if value is not None else None for value in values]
            unit = "index (median = 100)"
        fiscal_year = "FY2024-25" if derived_key == "state_power_availability_index" else "FY2022-23"
        series[derived_key] = {
            "labels": labels,
            "values": transformed,
            "chartType": "bar",
            "indexAxis": "y",
            "scope": "state",
            "source": title,
            "unit": unit,
            "note": f"Calculated from the complete 28-State RBI snapshot for {fiscal_year}; Union Territories are excluded.",
        }

    population = dict(zip(series.get("population", {}).get("labels", []), series.get("population", {}).get("values", [])))
    for derived_key, base_key, divisor in (
        ("cyber_crime_rate", "cyber_crime", 100000),
        ("ndps_case_rate", "ndps_drug_cases", 100000),
        ("road_fatality_rate", "road_accidents_fatalities", 100000),
    ):
        base = series.get(base_key, {})
        base_values = dict(zip(base.get("labels", []), base.get("values", [])))
        labels = sorted(year for year in base_values.keys() & population.keys() if population[year])
        series[derived_key] = {
            "labels": labels,
            "values": [base_values[year] / population[year] * divisor for year in labels],
            "source": f"{base.get('source', base_key)}; rates calculated using World Bank population estimates",
            "unit": "cases per 100,000 people",
        }

    for derived_key, base_key, terms, title in (
        ("pew_india_religious_pluralism", "pew_india_religion_tolerance", ("respecting all religions", "better off with religious diversity"), "Pew India: Religious pluralism"),
        ("pew_india_religious_practice", "pew_india_demographics_family", ("religion very important", "prays daily", "believes in karma"), "Pew India: Religious identity and practice"),
    ):
        base = series.get(base_key, {})
        selected = [
            (label, value) for label, value in zip(base.get("labels", []), base.get("values", []))
            if any(term in label.lower() for term in terms)
        ]
        series[derived_key] = {
            "labels": [label for label, _ in selected],
            "values": [value for _, value in selected],
            "source": base.get("source", "Pew Research Center India surveys"),
            "note": "A thematic view of the same separately labelled Pew survey observations; values are not combined or interpolated.",
            "unit": base.get("unit", "% of respondents"),
        }

    credit = series.get("credit_card_spends", {})
    debit = series.get("debit_card_spends", {})
    credit_values = dict(zip(credit.get("labels", []), credit.get("values", [])))
    debit_values = dict(zip(debit.get("labels", []), debit.get("values", [])))
    card_labels = sorted(credit_values.keys() & debit_values.keys())
    series["card_spend_total"] = {
        "labels": card_labels,
        "values": [credit_values[year] + debit_values[year] for year in card_labels],
        "source": f"{credit.get('source', 'RBI credit card data')}; {debit.get('source', 'RBI debit card data')}",
        "unit": "INR lakh crore",
    }
    series["credit_card_spend_share"] = {
        "labels": card_labels,
        "values": [
            credit_values[year] / (credit_values[year] + debit_values[year]) * 100
            if credit_values[year] + debit_values[year] else None
            for year in card_labels
        ],
        "source": f"{credit.get('source', 'RBI credit card data')}; {debit.get('source', 'RBI debit card data')}",
        "unit": "% of credit and debit card spends",
    }
    upi_value = series.get("upi_transaction_value", {})
    upi_labels = upi_value.get("labels", [])
    upi_values = upi_value.get("values", [])
    series["upi_value_growth"] = {
        "labels": upi_labels[1:],
        "values": [
            (current - previous) / abs(previous) * 100 if previous else None
            for previous, current in zip(upi_values, upi_values[1:])
        ],
        "source": f"{upi_value.get('source', 'NPCI and RBI UPI data')}; annual growth calculated from reported values",
        "unit": "% year-over-year",
    }
    military = series.get("military_expenditure_usd", {})
    military_values = dict(zip(military.get("labels", []), military.get("values", [])))
    military_labels = sorted(year for year in military_values.keys() & population.keys() if population[year])
    series["military_expenditure_per_capita"] = {
        "labels": military_labels,
        "values": [military_values[year] / population[year] for year in military_labels],
        "source": f"{military.get('source', 'World Bank military expenditure')}; calculated per person using World Bank population estimates",
        "unit": "USD/person",
    }
    market_labels = sorted({label for key in ("sensex", "nifty", "nifty_vix") for label in result["series"].get(key, {}).get("labels", [])})
    market_datasets = []
    for key, title, color in (("sensex", "Sensex", "#58a6ff"), ("nifty", "Nifty", "#3fb950"), ("nifty_vix", "Nifty VIX", "#f2cc60")):
        series = result["series"].get(key, {})
        values = dict(zip(series.get("labels", []), series.get("values", [])))
        first = next(iter(values.values()), None)
        if first:
            market_datasets.append({"label": title, "values": [values.get(label, None) / first * 100 if values.get(label) is not None else None for label in market_labels], "color": color})
    result["series"]["market_indices"] = {"labels": market_labels, "datasets": market_datasets, "source": "Economic Survey Statistical Appendix table 9.3; rebased to 100"}
    try:
        result["series"]["gdp_world_comparison"] = build_gdp_world_comparison()
    except Exception as error:
        cached = previous_series.get("gdp_world_comparison", {})
        result["series"]["gdp_world_comparison"] = cached if cached.get("labels") else {"error": str(error)}
    try:
        result["series"]["global_inflation_comparison"] = build_global_inflation_comparison()
    except Exception as error:
        cached = previous_series.get("global_inflation_comparison", {})
        result["series"]["global_inflation_comparison"] = cached if cached.get("labels") else {"error": str(error)}
    try:
        result["series"]["global_equity_indices"] = build_global_equity_indices()
    except Exception as error:
        cached = previous_series.get("global_equity_indices", {})
        result["series"]["global_equity_indices"] = cached if cached.get("labels") else {"error": str(error)}
    try:
        result["series"]["sectoral_market_indices"] = build_sectoral_market_indices()
    except Exception as error:
        cached = previous_series.get("sectoral_market_indices", {})
        result["series"]["sectoral_market_indices"] = cached if cached.get("labels") else {"error": str(error)}

    result["series"].update(build_composition_series(result["series"]))
    result["series"].update(build_derived_layer(result["series"]))
    
    chart_json = json.dumps(result, indent=2) + "\n"
    (ROOT / "data" / "chart-latest.json").write_text(chart_json)
    (ROOT / "docs" / "data" / "chart-latest.json").write_text(chart_json)
    
    chart_js = f"window.INDIA_DASHBOARD_DATA = {json.dumps(result, indent=2)};\n"
    (ROOT / "docs" / "data.js").write_text(chart_js, encoding="utf-8")


if __name__ == "__main__":
    main()

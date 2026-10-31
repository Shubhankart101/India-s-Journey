"""Mining & Natural Resources deep-dive from MOSPI's official APIs.

* Wholesale Price Index (base 2011-12): monthly prices of ores, industrial minerals, crude, gas, coal and lignite.
* Index of Industrial Production (base 2011-12): annual and monthly mining output.

Every series carries ``meta`` so the dashboard registers it without a hand-written definition.
"""
from __future__ import annotations

import json

try:
    from scripts.manufacturing_layer import COLORS, MONTHS, _get, _num, _rows
except ImportError:  # executed directly from scripts/
    from manufacturing_layer import COLORS, MONTHS, _get, _num, _rows

WPI_API = "https://api.mospi.gov.in/api/wpi/getWpiRecords?group_code={code}&limit=100&page={page}"
WPI_GROUPS = ("1103000000", "1104000000", "1201000000")  # Minerals, Crude petroleum & natural gas, Coal
CATEGORY = "Mining & Natural Resources"
METALLIC, ENERGY, INDUSTRIAL = "Metallic Minerals & Ores", "Energy Minerals & Fuel", "Non-Metallic & Industrial Minerals"
PRICES, OUTPUT = "Mineral Price Monitor (WPI)", "Mining Output Monitor (IIP)"
WPI_SOURCE = "MOSPI Wholesale Price Index API (api.mospi.gov.in)"
IIP_SOURCE = "MOSPI IIP API (api.mospi.gov.in)"
WPI_NOTE = ("Wholesale Price Index, base 2011-12 = 100, compiled by the Office of the Economic Adviser (DPIIT) and published "
            "through MOSPI. The latest two months are provisional and are revised after eight weeks.")
IIP_NOTE = "MOSPI Index of Industrial Production, base 2011-12 = 100. The latest periods are provisional and revised in later releases."

# key suffix, WPI item name, label, subgroup, colour
ITEMS = (
    ("iron_ore", "Iron ore", "Iron ore", METALLIC, "#ff7b72"),
    ("bauxite", "Bauxite", "Bauxite", METALLIC, "#ffa657"),
    ("copper_concentrate", "Copper concentrate", "Copper concentrate", METALLIC, "#d29922"),
    ("zinc_concentrate", "Zinc concentrate", "Zinc concentrate", METALLIC, "#a5d6ff"),
    ("lead_concentrate", "Lead concentrate", "Lead concentrate", METALLIC, "#8b949e"),
    ("manganese_ore", "Manganese ore", "Manganese ore", METALLIC, "#bc8cff"),
    ("chromite", "Chromite", "Chromite", METALLIC, "#3fb950"),
    ("limestone", "Limestone", "Limestone", INDUSTRIAL, "#e3b341"),
    ("phosphorite", "Phosphorite", "Phosphorite (rock phosphate)", INDUSTRIAL, "#56d364"),
    ("garnet", "Garnet", "Garnet", INDUSTRIAL, "#f778ba"),
    ("sillimanite", "Sillimanite", "Sillimanite", INDUSTRIAL, "#79c0ff"),
    ("crude_petroleum", "Crude petroleum", "Crude petroleum", ENERGY, "#bc8cff"),
    ("natural_gas", "Natural gas", "Natural gas", ENERGY, "#58a6ff"),
    ("coking_coal", "Coking coal", "Coking coal", ENERGY, "#8b949e"),
    ("lignite", "Lignite", "Lignite", ENERGY, "#d29922"),
)
# key, title, subtitle, subgroup, members (item suffixes or aggregate names)
COMPARISONS = (
    ("wpi_compare_metallic_ores", "Metallic Ore Prices Compared", "Iron ore, bauxite, copper, zinc, lead, manganese and chromite", METALLIC,
     ("iron_ore", "bauxite", "copper_concentrate", "zinc_concentrate", "lead_concentrate", "manganese_ore", "chromite")),
    ("wpi_compare_industrial_minerals", "Industrial Mineral Prices Compared", "Limestone, rock phosphate, garnet and sillimanite", INDUSTRIAL,
     ("limestone", "phosphorite", "garnet", "sillimanite")),
    ("wpi_compare_energy_minerals", "Energy Mineral Prices Compared", "Crude oil, natural gas, coking coal, non-coking coal and lignite", ENERGY,
     ("crude_petroleum", "natural_gas", "coking_coal", "non_coking_coal", "lignite")),
    ("wpi_mineral_groups_monthly", "Mineral Price Indices by Group", "WPI minerals, metallic minerals, other minerals, crude & gas, and coal", PRICES,
     ("minerals", "metallic_minerals", "other_minerals", "crude_gas", "coal")),
)
AGGREGATE_LABELS = {
    "minerals": "All minerals", "metallic_minerals": "Metallic minerals", "other_minerals": "Other (non-metallic) minerals",
    "crude_gas": "Crude petroleum & natural gas", "coal": "Coal", "non_coking_coal": "Non-coking coal",
}
# Official IIP 2011-12 sector weights (MOSPI).
IIP_WEIGHTS = (("Manufacturing", 77.63), ("Mining", 14.37), ("Electricity", 7.99))
KEYS = tuple(f"wpi_{suffix}" for suffix, *_ in ITEMS) + ("wpi_non_coking_coal",) + tuple(row[0] for row in COMPARISONS) + (
    "wpi_mineral_yoy_ranking", "wpi_mineral_since_base", "wpi_mineral_rising_vs_falling", "wpi_mineral_price_change_bands",
    "wpi_mineral_fy_inflation",
    "iip_mining_annual", "iip_mining_annual_growth", "iip_mining_monthly_compare", "iip_mining_monthly_growth",
    "iip_mining_months_expanding", "iip_sector_weights",
)


def _meta(title, subtitle, subgroup, suffix, frequency="Monthly", color="#ff9933") -> dict:
    return {"title": title, "subtitle": subtitle, "frequency": frequency, "color": color,
            "suffix": suffix, "category": CATEGORY, "subgroup": subgroup}


def _period(row: dict) -> str | None:
    month = MONTHS.get(str(row.get("month", "")).strip().title())
    return f"{int(row['year'])}-{month:02d}" if month else None


def _wpi_rows() -> list[dict]:
    rows: list[dict] = []
    for code in WPI_GROUPS:
        page = 1
        while True:
            payload = json.loads(_get(WPI_API.format(code=code, page=page)))
            rows.extend(payload.get("data") or [])
            if page >= payload.get("meta_data", {}).get("totalPages", 1):
                break
            page += 1
    return rows


def _aggregate_name(row: dict) -> str | None:
    group, subgroup, item = row.get("group"), row.get("subgroup"), row.get("item")
    if item:
        return None
    if group == "Minerals":
        return {None: "minerals", "Metallic minerals": "metallic_minerals", "Other minerals": "other_minerals"}.get(subgroup)
    if group == "Crude petroleum & natural gas" and not subgroup:
        return "crude_gas"
    if group == "Coal":
        return {None: "coal", "Non-coking coal": "non_coking_coal"}.get(subgroup)
    return None


def _yoy(data: dict[str, float], period: str) -> float | None:
    year, month = period.split("-")
    base = data.get(f"{int(year) - 1}-{month}")
    value = data.get(period)
    if base and value is not None:
        return round((value / base - 1) * 100, 1)
    return None


def _fiscal_year(period: str) -> str:
    year, month = map(int, period.split("-"))
    start = year if month >= 4 else year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def _wpi_series(rows: list[dict]) -> dict[str, dict]:
    item_names = {source: suffix for suffix, source, *_ in ITEMS}
    observed: dict[str, dict[str, float]] = {}
    for row in rows:
        period, value = _period(row), _num(row.get("index_value"))
        if not period or value is None:
            continue
        name = item_names.get(row.get("item")) or _aggregate_name(row)
        if name:
            observed.setdefault(name, {})[period] = value
    labels = {suffix: label for suffix, _, label, *_ in ITEMS} | AGGREGATE_LABELS
    series: dict[str, dict] = {}
    singles = list(ITEMS) + [("non_coking_coal", None, "Non-coking coal", ENERGY, "#ff9933")]
    for suffix, _, label, subgroup, color in singles:
        data = observed.get(suffix)
        if not data or len(data) < 2:
            continue
        periods = sorted(data)
        latest = periods[-1]
        change = _yoy(data, latest)
        series[f"wpi_{suffix}"] = {
            "labels": periods, "values": [data[p] for p in periods], "source": WPI_SOURCE, "unit": "index",
            "note": f"{label} wholesale price index. {WPI_NOTE}" + (f" Year-on-year change in {latest}: {change}%." if change is not None else ""),
            "meta": _meta(f"WPI: {label} Price Index", "Monthly wholesale price index, 2011-12 = 100", subgroup, " index", color=color),
        }
    for key, title, subtitle, subgroup, members in COMPARISONS:
        present = [m for m in members if observed.get(m)]
        if len(present) < 2:
            continue
        periods = sorted({p for m in present for p in observed[m]})
        series[key] = {
            "labels": periods,
            "datasets": [{"label": labels[m], "values": [observed[m].get(p) for p in periods], "color": COLORS[i % len(COLORS)]}
                         for i, m in enumerate(present)],
            "source": WPI_SOURCE, "unit": "index", "note": f"{subtitle}. {WPI_NOTE}",
            "meta": _meta(title, "Monthly wholesale price index, 2011-12 = 100", subgroup, " index"),
        }
    item_keys = [suffix for suffix, *_ in ITEMS if observed.get(suffix)] + (["non_coking_coal"] if observed.get("non_coking_coal") else [])
    if not item_keys:
        return series
    latest = max(max(observed[k]) for k in item_keys)
    yoy = sorted(((labels[k], _yoy(observed[k], latest)) for k in item_keys if _yoy(observed[k], latest) is not None), key=lambda x: -x[1])
    since = sorted(((labels[k], round(observed[k][latest] - 100, 1)) for k in item_keys if latest in observed[k]), key=lambda x: -x[1])
    if yoy:
        series["wpi_mineral_yoy_ranking"] = {
            "labels": [n for n, _ in yoy], "values": [v for _, v in yoy], "chartType": "bar", "indexAxis": "y", "scope": "category",
            "source": WPI_SOURCE, "unit": "%",
            "note": f"Year-on-year change in each mineral's wholesale price index in {latest}. {WPI_NOTE}",
            "meta": _meta(f"Mineral Price Inflation by Commodity ({latest})", "Year-on-year change in WPI", PRICES, "%"),
        }
        up, down = sum(v > 0 for _, v in yoy), sum(v < 0 for _, v in yoy)
        points = [(n, c) for n, c in (("Prices rising", up), ("Prices falling", down), ("Unchanged", len(yoy) - up - down)) if c]
        series["wpi_mineral_rising_vs_falling"] = {
            "labels": [p[0] for p in points], "values": [p[1] for p in points], "chartType": "doughnut", "scope": "category",
            "source": WPI_SOURCE, "unit": "minerals",
            "note": f"How many of the {len(yoy)} tracked minerals and fuels had higher or lower wholesale prices in {latest} than a year earlier. {WPI_NOTE}",
            "meta": _meta(f"Minerals with Rising vs Falling Prices ({latest})", "Count of commodities by year-on-year price direction", PRICES, " minerals"),
        }
    if since:
        series["wpi_mineral_since_base"] = {
            "labels": [n for n, _ in since], "values": [v for _, v in since], "chartType": "bar", "indexAxis": "y", "scope": "category",
            "source": WPI_SOURCE, "unit": "%",
            "note": f"WPI in {latest} minus 100, i.e. the cumulative wholesale price change since 2011-12. {WPI_NOTE}",
            "meta": _meta(f"Mineral Price Change Since 2011-12 ({latest})", "Cumulative change in wholesale price index", PRICES, "%"),
        }
        bands = (("Cheaper than 2011-12", lambda v: v < 0), ("Up to 50% dearer", lambda v: 0 <= v < 50),
                 ("50-100% dearer", lambda v: 50 <= v < 100), ("100-200% dearer", lambda v: 100 <= v < 200), ("More than 200% dearer", lambda v: v >= 200))
        points = [(name, sum(test(v) for _, v in since)) for name, test in bands]
        points = [p for p in points if p[1]]
        series["wpi_mineral_price_change_bands"] = {
            "labels": [p[0] for p in points], "values": [p[1] for p in points], "chartType": "doughnut", "scope": "category",
            "source": WPI_SOURCE, "unit": "minerals",
            "note": f"The {len(since)} tracked minerals and fuels grouped by how far their wholesale price index in {latest} sits above or below 2011-12. {WPI_NOTE}",
            "meta": _meta(f"Minerals by Price Change Since 2011-12 ({latest})", "Count of commodities in each price-change band", PRICES, " minerals"),
        }
    fy_groups = {}
    for name in ("minerals", "metallic_minerals", "other_minerals", "crude_gas", "coal"):
        data = observed.get(name) or {}
        by_year: dict[str, list[float]] = {}
        for period, value in data.items():
            by_year.setdefault(_fiscal_year(period), []).append(value)
        full = {fy: sum(v) / len(v) for fy, v in by_year.items() if len(v) == 12}
        years = sorted(full)
        changes = {years[i]: round((full[years[i]] / full[years[i - 1]] - 1) * 100, 1) for i in range(1, len(years))}
        if changes:
            fy_groups[name] = changes
    if len(fy_groups) >= 2:
        years = sorted({y for d in fy_groups.values() for y in d})
        series["wpi_mineral_fy_inflation"] = {
            "labels": years,
            "datasets": [{"label": labels[n], "values": [d.get(y) for y in years], "color": COLORS[i % len(COLORS)]} for i, (n, d) in enumerate(fy_groups.items())],
            "source": WPI_SOURCE, "unit": "%",
            "note": f"Annual wholesale price inflation by mineral group: the change in the April-March average index over the previous fiscal year (complete fiscal years only). {WPI_NOTE}",
            "meta": _meta("Annual Mineral Price Inflation by Group", "Change in fiscal-year average WPI", PRICES, "%", frequency="Annual"),
        }
    return series


def _iip_annual(rows: list[dict]) -> dict[str, dict]:
    data = {r["year"]: (_num(r.get("index")), _num(r.get("growth_rate"))) for r in rows
            if r.get("category") == "Mining" and not r.get("sub_category") and r.get("year")}
    years = sorted(data)
    if len(years) < 2:
        return {}
    growth_years = [y for y in years if data[y][1] is not None]
    return {
        "iip_mining_annual": {
            "labels": years, "values": [data[y][0] for y in years], "source": IIP_SOURCE, "unit": "index",
            "note": f"Mining and quarrying output (coal, lignite, crude oil, natural gas, metallic and non-metallic minerals), fiscal-year averages. {IIP_NOTE}",
            "meta": _meta("IIP: Mining Output Index", "Annual Index of Industrial Production for mining, 2011-12 = 100", OUTPUT, " index", frequency="Annual", color="#e3b341"),
        },
        "iip_mining_annual_growth": {
            "labels": growth_years, "values": [data[y][1] for y in growth_years], "chartType": "bar", "source": IIP_SOURCE, "unit": "%",
            "note": f"Year-on-year growth in the fiscal-year mining index. {IIP_NOTE}",
            "meta": _meta("Mining Output Growth by Fiscal Year", "Year-on-year change in the mining IIP", OUTPUT, "%", frequency="Annual", color="#ff9933"),
        },
    }


def _iip_monthly(rows: list[dict]) -> dict[str, dict]:
    sectors: dict[str, dict[str, float]] = {}
    mining_growth: dict[str, float] = {}
    for row in rows:
        period = _period(row)
        if not period:
            continue
        value = _num(row.get("index"))
        if row.get("type") == "General":
            name = "General index"
        elif row.get("type") == "Sectoral" and not row.get("sub_category") and row.get("category") in ("Mining", "Manufacturing", "Electricity"):
            name = row["category"]
        else:
            continue
        if value is not None:
            sectors.setdefault(name, {})[period] = value
        if name == "Mining" and _num(row.get("growth_rate")) is not None:
            mining_growth[period] = _num(row.get("growth_rate"))
    series: dict[str, dict] = {}
    if "Mining" in sectors and len(sectors) >= 2:
        periods = sorted({p for d in sectors.values() for p in d})
        order = [n for n in ("Mining", "General index", "Manufacturing", "Electricity") if n in sectors]
        series["iip_mining_monthly_compare"] = {
            "labels": periods,
            "datasets": [{"label": n, "values": [sectors[n].get(p) for p in periods], "color": COLORS[i % len(COLORS)]} for i, n in enumerate(order)],
            "source": IIP_SOURCE, "unit": "index", "note": f"Monthly mining output against the general index, manufacturing and electricity. {IIP_NOTE}",
            "meta": _meta("Monthly Mining Output vs Other Sectors", "Monthly IIP, 2011-12 = 100", OUTPUT, " index"),
        }
    if len(mining_growth) >= 2:
        periods = sorted(mining_growth)
        series["iip_mining_monthly_growth"] = {
            "labels": periods, "values": [mining_growth[p] for p in periods], "chartType": "bar", "source": IIP_SOURCE, "unit": "%",
            "note": f"Year-on-year growth in the monthly mining index. Monsoon months usually dip because open-cast mines slow down. {IIP_NOTE}",
            "meta": _meta("Monthly Mining Output Growth", "Year-on-year change in the monthly mining IIP", OUTPUT, "%", color="#ffa657"),
        }
        recent = periods[-12:]
        up = sum(mining_growth[p] > 0 for p in recent)
        down = sum(mining_growth[p] < 0 for p in recent)
        points = [(n, c) for n, c in (("Months of growth", up), ("Months of contraction", down), ("Flat months", len(recent) - up - down)) if c]
        series["iip_mining_months_expanding"] = {
            "labels": [p[0] for p in points], "values": [p[1] for p in points], "chartType": "doughnut", "scope": "category",
            "source": IIP_SOURCE, "unit": "months",
            "note": f"Of the last {len(recent)} months ({recent[0]} to {recent[-1]}), how many recorded year-on-year growth or contraction in mining output. {IIP_NOTE}",
            "meta": _meta(f"Mining Months Expanding vs Contracting ({recent[0]} to {recent[-1]})", "Count of months by direction of mining growth", OUTPUT, " months"),
        }
    return series


def _iip_weights() -> dict[str, dict]:
    return {"iip_sector_weights": {
        "labels": [n for n, _ in IIP_WEIGHTS], "values": [w for _, w in IIP_WEIGHTS], "chartType": "doughnut", "scope": "category",
        "source": "MOSPI, Index of Industrial Production (base 2011-12) sectoral weights", "unit": "%",
        "note": "Weights of manufacturing, mining and electricity in India's Index of Industrial Production (base 2011-12), as published by MOSPI. They show how much mining moves the headline IIP.",
        "meta": _meta("Mining's Weight in the Index of Industrial Production", "Official sector weights in the IIP, base 2011-12", OUTPUT, "%", frequency="Fixed base-year weights"),
    }}


def build_mining_layer(previous: dict[str, dict]) -> dict[str, dict]:
    series: dict[str, dict] = _iip_weights()
    for builder in (
        lambda: _wpi_series(_wpi_rows()),
        lambda: _iip_annual(_rows("getIIPAnnual", "&type=Sectoral")),
        lambda: _iip_monthly(_rows("getIIPMonthly")),
    ):
        try:
            series.update(builder())
        except Exception:  # keep the last good series when a source is unavailable
            pass
    for key in KEYS:
        if key not in series and (previous.get(key, {}).get("values") or previous.get(key, {}).get("datasets")):
            series[key] = previous[key]
    return series

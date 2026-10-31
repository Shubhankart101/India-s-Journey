"""Compare India with the world's most-visited tourist destinations (World Bank / UN Tourism data).

Each series carries ``meta`` so the dashboard registers it without a hand-written definition.
"""
from __future__ import annotations

from typing import Callable

# Top ten destinations by international arrivals in 2019 (UN Tourism), plus Japan, the UAE and India.
COUNTRIES = (
    ("FRA", "France"), ("ESP", "Spain"), ("USA", "United States"), ("CHN", "China"), ("ITA", "Italy"),
    ("TUR", "Turkiye"), ("MEX", "Mexico"), ("THA", "Thailand"), ("DEU", "Germany"), ("GBR", "United Kingdom"),
    ("JPN", "Japan"), ("ARE", "United Arab Emirates"), ("IND", "India"),
)
NAMES = dict(COUNTRIES)
URL = ("https://api.worldbank.org/v2/country/" + ";".join(code for code, _ in COUNTRIES)
       + "/indicator/{code}?format=json&per_page=2000&date=1995:2025")
CATEGORY, SUBGROUP = "Tourism & Heritage", "Global Tourism Comparison"
LINE_COLORS = ("#ff9933", "#58a6ff", "#3fb950", "#bc8cff", "#ff7b72", "#f6c344", "#39c5bb")
LINE_PEERS = ("IND", "FRA", "ESP", "USA", "CHN", "THA", "ARE")
BENCHMARK = "2019"  # last full year before the pandemic collapse in travel
KEYS = (
    "tourism_compare_arrivals_trend", "tourism_compare_receipts_trend", "tourism_compare_export_share_trend",
    "tourism_compare_arrivals_share", "tourism_compare_receipts_share", "tourism_compare_spending_share",
    "tourism_compare_departures_share", "tourism_compare_arrivals_rank", "tourism_compare_receipts_rank",
    "tourism_compare_receipts_per_arrival", "tourism_compare_arrivals_per_100", "tourism_compare_receipts_gdp",
    "tourism_compare_export_share", "tourism_compare_balance",
)


def _observations(get_json: Callable[[str], object], code: str) -> dict[str, dict[str, float]]:
    payload = get_json(URL.format(code=code))
    if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
        raise ValueError(f"World Bank returned no observations for {code}")
    observed: dict[str, dict[str, float]] = {}
    for row in payload[1]:
        if row.get("value") is not None and row.get("countryiso3code") in NAMES:
            observed.setdefault(row["countryiso3code"], {})[row["date"]] = float(row["value"])
    return observed


def _meta(title: str, subtitle: str, suffix: str, color: str = "#ff9933") -> dict:
    return {"title": title, "subtitle": subtitle, "frequency": "Annual", "color": color,
            "suffix": suffix, "category": CATEGORY, "subgroup": SUBGROUP}


def _note(text: str, codes: str) -> str:
    return (f"{text} Source: World Bank API {codes} (UN Tourism / IMF balance-of-payments data). "
            f"The World Bank stopped updating these indicators after 2020, so {BENCHMARK} is used as the "
            "pre-pandemic benchmark year.")


def _line(observed, key, code, title, subtitle, suffix):
    years = sorted({year for iso in LINE_PEERS for year in observed.get(iso, {})}, key=int)
    datasets = [
        {"label": NAMES[iso], "values": [observed[iso].get(year) for year in years], "color": LINE_COLORS[i]}
        for i, iso in enumerate(LINE_PEERS) if observed.get(iso)
    ]
    if "IND" not in observed or len(datasets) < 2:
        raise ValueError(f"Too few countries for {key}")
    return key, {
        "labels": years, "datasets": datasets, "source": f"World Bank API {code}", "unit": suffix.strip(),
        "note": _note(f"{subtitle} for India and six leading destinations; gaps are years without a reported value.", code),
        "meta": _meta(title, subtitle, suffix),
    }


def _ranked(values: dict[str, float], key, title, subtitle, suffix, codes, chart="bar", note=""):
    points = sorted(((NAMES[iso], round(value, 2)) for iso, value in values.items()), key=lambda item: -item[1])
    if "India" not in dict(points) or len(points) < 3:
        raise ValueError(f"Too few countries for {key}")
    series = {
        "labels": [label for label, _ in points], "values": [value for _, value in points],
        "source": f"World Bank API {codes}", "unit": suffix.strip(),
        "note": _note(f"{subtitle}, {BENCHMARK}. India ranks {[label for label, _ in points].index('India') + 1} "
                      f"of {len(points)}. {note}".strip(), codes),
        "meta": _meta(f"{title} ({BENCHMARK})", subtitle, suffix),
    }
    if chart == "doughnut":
        series.update(chartType="doughnut", scope="category")
    else:
        series.update(chartType="bar", indexAxis="y", scope="category")
    return key, series


def _at(observed, year=BENCHMARK):
    return {iso: rows[year] for iso, rows in observed.items() if year in rows}


def build_tourism_comparison_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    cache: dict[str, dict[str, dict[str, float]]] = {}

    def fetch(code: str):
        if code not in cache:
            for attempt in range(3):
                try:
                    cache[code] = _observations(get_json, code)
                    break
                except ValueError:
                    raise
                except Exception:
                    if attempt == 2:
                        raise
        return cache[code]

    def arrivals_per_100():
        arrivals, population = _at(fetch("ST.INT.ARVL")), _at(fetch("SP.POP.TOTL"))
        return {iso: arrivals[iso] / population[iso] * 100 for iso in arrivals if population.get(iso)}

    def receipts_per_arrival():
        receipts, arrivals = _at(fetch("ST.INT.RCPT.CD")), _at(fetch("ST.INT.ARVL"))
        return {iso: receipts[iso] / arrivals[iso] for iso in receipts if arrivals.get(iso)}

    def receipts_gdp():
        receipts, gdp = _at(fetch("ST.INT.RCPT.CD")), _at(fetch("NY.GDP.MKTP.CD"))
        return {iso: receipts[iso] / gdp[iso] * 100 for iso in receipts if gdp.get(iso)}

    def billions(code):
        return {iso: value / 1e9 for iso, value in _at(fetch(code)).items()}

    def millions(code):
        return {iso: value / 1e6 for iso, value in _at(fetch(code)).items()}

    builders = {
        "tourism_compare_arrivals_trend": lambda: _line(fetch("ST.INT.ARVL"), "tourism_compare_arrivals_trend", "ST.INT.ARVL",
            "International Arrivals: India vs Top Destinations", "Inbound international tourist arrivals", " arrivals"),
        "tourism_compare_receipts_trend": lambda: _line(fetch("ST.INT.RCPT.CD"), "tourism_compare_receipts_trend", "ST.INT.RCPT.CD",
            "Tourism Receipts: India vs Top Destinations", "International tourism receipts, current US dollars", " USD"),
        "tourism_compare_export_share_trend": lambda: _line(fetch("ST.INT.RCPT.XP.ZS"), "tourism_compare_export_share_trend", "ST.INT.RCPT.XP.ZS",
            "Tourism Share of Exports: India vs Top Destinations", "International tourism receipts as a share of total exports", "%"),
        "tourism_compare_arrivals_share": lambda: _ranked(millions("ST.INT.ARVL"), "tourism_compare_arrivals_share",
            "Share of Arrivals Among Top Destinations", "International arrivals across the 13 compared countries", " million arrivals", "ST.INT.ARVL", "doughnut"),
        "tourism_compare_receipts_share": lambda: _ranked(billions("ST.INT.RCPT.CD"), "tourism_compare_receipts_share",
            "Share of Tourism Receipts Among Top Destinations", "International tourism receipts across the compared countries", " USD bn", "ST.INT.RCPT.CD", "doughnut"),
        "tourism_compare_spending_share": lambda: _ranked(billions("ST.INT.XPND.CD"), "tourism_compare_spending_share",
            "Share of Outbound Tourism Spending", "International tourism expenditure by residents of the compared countries", " USD bn", "ST.INT.XPND.CD", "doughnut"),
        "tourism_compare_departures_share": lambda: _ranked(millions("ST.INT.DPRT"), "tourism_compare_departures_share",
            "Share of Outbound Departures", "Residents travelling abroad from the compared countries", " million departures", "ST.INT.DPRT", "doughnut"),
        "tourism_compare_arrivals_rank": lambda: _ranked(millions("ST.INT.ARVL"), "tourism_compare_arrivals_rank",
            "Arrivals Ranking: India vs Top Destinations", "International tourist arrivals", " million arrivals", "ST.INT.ARVL"),
        "tourism_compare_receipts_rank": lambda: _ranked(billions("ST.INT.RCPT.CD"), "tourism_compare_receipts_rank",
            "Tourism Receipts Ranking", "International tourism receipts", " USD bn", "ST.INT.RCPT.CD"),
        "tourism_compare_receipts_per_arrival": lambda: _ranked(receipts_per_arrival(), "tourism_compare_receipts_per_arrival",
            "Tourism Receipts per Arrival", "Receipts divided by international arrivals", " USD per arrival", "ST.INT.RCPT.CD, ST.INT.ARVL",
            note="Derived ratio; receipts include passenger transport where reported."),
        "tourism_compare_arrivals_per_100": lambda: _ranked(arrivals_per_100(), "tourism_compare_arrivals_per_100",
            "Tourist Arrivals per 100 Residents", "International arrivals relative to resident population", " per 100 residents", "ST.INT.ARVL, SP.POP.TOTL",
            note="Derived ratio of arrivals to population."),
        "tourism_compare_receipts_gdp": lambda: _ranked(receipts_gdp(), "tourism_compare_receipts_gdp",
            "Tourism Receipts as Share of GDP", "International tourism receipts relative to GDP", "%", "ST.INT.RCPT.CD, NY.GDP.MKTP.CD",
            note="Derived ratio of receipts to current-dollar GDP."),
        "tourism_compare_export_share": lambda: _ranked(_at(fetch("ST.INT.RCPT.XP.ZS")), "tourism_compare_export_share",
            "Tourism Share of Exports", "International tourism receipts as a share of total exports", "%", "ST.INT.RCPT.XP.ZS"),
        "tourism_compare_balance": lambda: _ranked(
            {iso: value - billions("ST.INT.XPND.CD").get(iso, value) for iso, value in billions("ST.INT.RCPT.CD").items() if iso in billions("ST.INT.XPND.CD")},
            "tourism_compare_balance", "Tourism Balance (Receipts minus Spending)", "Inbound receipts less outbound expenditure; negative means net spender",
            " USD bn", "ST.INT.RCPT.CD, ST.INT.XPND.CD"),
    }

    series: dict[str, dict] = {}
    for key, build in builders.items():
        try:
            built_key, built = build()
            series[built_key] = built
        except Exception:  # keep the last good series when the API is unavailable
            if previous.get(key, {}).get("values") or previous.get(key, {}).get("datasets"):
                series[key] = previous[key]
    return series

from __future__ import annotations

import json
import csv
import io
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CHART_DIR = ROOT / "assets" / "charts"
USER_AGENT = "PolityPolicyUpdate public data dashboard"


def get_json(url: str) -> object:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def get_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/csv,text/html,*/*;q=0.8"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


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


def build_terrorism_chart() -> dict:
    rows = csv.DictReader(io.StringIO(get_text("https://ourworldindata.org/grapher/terrorist-attacks.csv")))
    values = {row["Year"]: float(row["Attacks"]) for row in rows if row["Entity"] == "India"}
    labels = sorted(values)
    return {"source": "Our World in Data; Global Terrorism Database-derived series", "years": labels, "values": [values[label] for label in labels]}


def build_lwe_aggregate() -> dict:
    text = re.sub(r"<[^>]+>", " ", get_text("https://www.mha.gov.in/en/divisionofmha/left-wing-extremism-division"))
    match = re.search(r"Between 2004 to 2025.*?(\d[\d,]*) people have been killed", text, re.I | re.S)
    if not match:
        raise ValueError("MHA LWE aggregate not found")
    return {"source": "Ministry of Home Affairs LWE Division", "years": ["2004-2025"], "values": [float(match.group(1).replace(",", ""))]}


def main() -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    result = {"generated_at_utc": generated, "series": {}}
    indicators = [
        ("cpi", "FP.CPI.TOTL.ZG", "india-cpi-inflation.svg", "India CPI Inflation", "Annual consumer-price inflation; World Bank indicator FP.CPI.TOTL.ZG", "#63b3ed", "%"),
        ("trade", "NE.TRD.GNFS.ZS", "india-trade-share-gdp.svg", "India Trade Share of GDP", "Exports plus imports as share of GDP; World Bank indicator NE.TRD.GNFS.ZS", "#2ea44f", "%"),
        ("forex", "FI.RES.TOTL.CD", "india-foreign-reserves.svg", "India Foreign Exchange Reserves", "Total reserves including gold; World Bank indicator FI.RES.TOTL.CD", "#63b3ed", ""),
        ("bank_credit", "FS.AST.PRVT.GD.ZS", "india-domestic-credit.svg", "India Domestic Credit", "Domestic credit to private sector as share of GDP; World Bank indicator FS.AST.PRVT.GD.ZS", "#a371f7", "%"),
        ("iip", "NV.IND.TOTL.KD.ZG", "india-industrial-growth.svg", "India Industrial Value Added Growth", "Annual industrial value-added growth; World Bank indicator NV.IND.TOTL.KD.ZG", "#f56c6c", "%"),
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
    ]
    for key in ["gst", "fiscal_deficit", "wpi", "upi"]:
        result["series"][key] = {"error": "Official export adapter pending"}
    try:
        result["series"]["terror_attacks"] = build_terrorism_chart()
    except Exception as error:
        result["series"]["terror_attacks"] = {"error": str(error)}
    try:
        result["series"]["lwe_incidents"] = build_lwe_aggregate()
    except Exception as error:
        result["series"]["lwe_incidents"] = {"error": str(error)}
    for key, indicator, file_name, title, subtitle, color, suffix in indicators:
        try:
            series = build_world_bank_chart(indicator, file_name, title, subtitle, color, suffix)
            result["series"][key] = {"labels": series["years"], "values": series["values"], "source": series["source"]}
        except Exception as error:
            result["series"][key] = {"error": str(error)}
    market_labels = sorted({label for key in ("sensex", "nifty", "nifty_vix") for label in result["series"].get(key, {}).get("labels", [])})
    market_datasets = []
    for key, title, color in (("sensex", "Sensex", "#58a6ff"), ("nifty", "Nifty", "#3fb950"), ("nifty_vix", "Nifty VIX", "#f2cc60")):
        series = result["series"].get(key, {})
        values = dict(zip(series.get("labels", []), series.get("values", [])))
        first = next(iter(values.values()), None)
        if first:
            market_datasets.append({"label": title, "values": [values.get(label, None) / first * 100 if values.get(label) is not None else None for label in market_labels], "color": color})
    result["series"]["market_indices"] = {"labels": market_labels, "datasets": market_datasets, "source": "Economic Survey Statistical Appendix table 9.3; rebased to 100"}
    (ROOT / "data" / "chart-latest.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

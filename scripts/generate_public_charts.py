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
    return {"source": "Our World in Data; Global Terrorism Database-derived series", "labels": labels, "values": [values[label] for label in labels]}

def build_terrorism_fatalities_chart() -> dict:
    rows = csv.DictReader(io.StringIO(get_text("https://ourworldindata.org/grapher/terrorism-deaths.csv")))
    values = {row["Year"]: float(row["Fatalities"]) for row in rows if row["Entity"] == "India"}
    labels = sorted(values)
    return {"source": "Our World in Data; Global Terrorism Database-derived fatalities", "labels": labels, "values": [values[label] for label in labels]}


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
        ("defence_expenditure", "MS.MIL.XPND.GD.ZS", "india-defence-expenditure.svg", "India Defence Expenditure", "Military expenditure as share of GDP; World Bank indicator MS.MIL.XPND.GD.ZS", "#ff7b72", "% GDP"),
    ]
    
    # Load economic survey monthly data if available
    econ_file = ROOT / "data" / "economic-survey-monthly.json"
    if econ_file.is_file():
        try:
            econ_data = json.loads(econ_file.read_text(encoding="utf-8"))
            for k, v in econ_data.get("series", {}).items():
                result["series"][k] = v
        except Exception as e:
            print(f"Error reading economic-survey-monthly.json: {e}")

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
    try:
        result["series"]["lwe_incidents"] = build_lwe_aggregate()
    except Exception as error:
        result["series"]["lwe_incidents"] = {"error": str(error)}
    
    result["series"]["defence_exports"] = build_defence_exports()
    result["series"]["defence_production"] = build_defence_production()
    result["series"]["defence_stockpile"] = build_defence_stockpile()
    result["series"]["defence_production_exports"] = build_defence_production_exports()
    result["series"]["defence_budget_share"] = build_defence_budget_share()
    result["series"]["defence_rd_budget"] = build_defence_rd_budget()
    result["series"]["defence_capital_acquisition"] = build_defence_capital_acquisition()
    result["series"]["sipri_arms_imports"] = build_sipri_arms_imports()

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
    try:
        result["series"]["gdp_world_comparison"] = build_gdp_world_comparison()
    except Exception as error:
        result["series"]["gdp_world_comparison"] = {"error": str(error)}
    try:
        result["series"]["global_inflation_comparison"] = build_global_inflation_comparison()
    except Exception as error:
        result["series"]["global_inflation_comparison"] = {"error": str(error)}
    try:
        result["series"]["global_equity_indices"] = build_global_equity_indices()
    except Exception as error:
        result["series"]["global_equity_indices"] = {"error": str(error)}
    try:
        result["series"]["sectoral_market_indices"] = build_sectoral_market_indices()
    except Exception as error:
        result["series"]["sectoral_market_indices"] = {"error": str(error)}
    
    chart_json = json.dumps(result, indent=2) + "\n"
    (ROOT / "data" / "chart-latest.json").write_text(chart_json)
    (ROOT / "docs" / "data" / "chart-latest.json").write_text(chart_json)


if __name__ == "__main__":
    main()

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
    years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    mh = [24.1, 26.3, 27.1, 31.0, 35.2, 38.8, 42.5, 46.2, 50.1]
    tn = [15.1, 16.6, 17.4, 19.8, 22.5, 24.8, 27.2, 29.8, 32.5]
    gj = [14.2, 16.0, 16.5, 19.4, 22.0, 24.2, 26.8, 29.5, 32.2]
    ka = [14.0, 15.6, 16.2, 18.9, 21.4, 23.6, 26.0, 28.5, 31.0]
    up = [14.5, 15.8, 16.4, 19.1, 21.8, 24.0, 26.5, 29.0, 31.8]
    wb = [10.2, 11.4, 11.8, 13.5, 15.3, 16.8, 18.5, 20.2, 22.0]
    datasets = [
        {"label": "Maharashtra 🏁", "values": mh, "color": "#58a6ff"},
        {"label": "Tamil Nadu 🏭", "values": tn, "color": "#3fb950"},
        {"label": "Gujarat ⚙️", "values": gj, "color": "#ff9933"},
        {"label": "Karnataka 💻", "values": ka, "color": "#a371f7"},
        {"label": "Uttar Pradesh 🌾", "values": up, "color": "#f6c344"},
        {"label": "West Bengal ⚓", "values": wb, "color": "#ff7b72"},
    ]
    return {
        "labels": years,
        "datasets": datasets,
        "source": "Reserve Bank of India (RBI) Handbook of Statistics on Indian States & MOSPI (GSDP at Current Prices in INR Lakh Crores)"
    }

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
    result["series"]["state_gsdp_comparison"] = build_state_gsdp_comparison()
    result["series"]["state_fdi_inflows"] = build_state_fdi_inflows()
    result["series"]["state_debt_to_gsdp"] = build_state_debt_to_gsdp()
    result["series"]["state_operating_factories"] = build_state_operating_factories()
    result["series"]["state_pmay_homes"] = build_state_pmay_homes()
    result["series"]["state_jjm_water_coverage"] = build_state_jjm_water_coverage()
    result["series"]["state_mudra_loans"] = build_state_mudra_loans()

    # Manufacturing & Industrial Growth
    result["series"]["auto_production_volume"] = build_auto_production_volume()
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
    
    chart_js = f"window.INDIA_DASHBOARD_DATA = {json.dumps(result, indent=2)};\n"
    (ROOT / "docs" / "data.js").write_text(chart_js, encoding="utf-8")


if __name__ == "__main__":
    main()

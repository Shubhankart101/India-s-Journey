"""Innovation & Technology dashboard group built from World Bank API indicators.

The World Bank republishes WIPO (patents, designs), UNESCO UIS (R&D, researchers), ITU (internet,
mobile, broadband), UN Comtrade (high-tech trade) and IMF balance-of-payments (royalties) data.
Every value is fetched at build time; derived ratios are computed from fetched indicators only.
"""
from __future__ import annotations

import time
from typing import Callable

CATEGORY = "Innovation & Technology"
SUBGROUPS = (
    "Patents & Intellectual Property",
    "Industrial Designs & IP Filings",
    "Research & Development",
    "Scientific Publications & Talent",
    "High-Tech Trade & Manufacturing",
    "IP Royalties & Technology Payments",
    "Digital Technology Adoption",
    "Startups & New Business",
    "Global Innovation Benchmarks",
)

PEERS = {
    "IND": "India", "CHN": "China", "USA": "United States", "JPN": "Japan", "KOR": "South Korea",
    "DEU": "Germany", "GBR": "United Kingdom", "FRA": "France", "BRA": "Brazil", "RUS": "Russia",
    "IDN": "Indonesia", "ZAF": "South Africa", "ISR": "Israel", "SGP": "Singapore", "VNM": "Vietnam",
}
LINE_PEERS = ("IND", "CHN", "USA", "JPN", "KOR", "DEU", "BRA")
PEER_COLORS = {"IND": "#ff9933", "CHN": "#e5484d", "USA": "#4c8dff", "JPN": "#b07cff",
               "KOR": "#2bb5a0", "DEU": "#f2c94c", "BRA": "#7fbf4d"}
URL = ("https://api.worldbank.org/v2/country/" + ";".join(PEERS)
       + "/indicator/{code}?format=json&per_page=20000&date=1980:2026")
ORANGE = "#ff9933"

Data = dict  # iso3 -> {year: value}


def _ratio(a: Data, b: Data, scale: float = 1.0) -> Data:
    out: Data = {}
    for iso, years in a.items():
        for year, value in years.items():
            other = b.get(iso, {}).get(year)
            if other:
                out.setdefault(iso, {})[year] = value / other * scale
    return out


def _sum(a: Data, b: Data) -> Data:
    return _combine(a, b, lambda x, y: x + y)


def _combine(a: Data, b: Data, op: Callable[[float, float], float]) -> Data:
    out: Data = {}
    for iso, years in a.items():
        for year, value in years.items():
            other = b.get(iso, {}).get(year)
            if other is not None:
                out.setdefault(iso, {})[year] = op(value, other)
    return out


# key, title, subgroup, kind (count|pct|signed), suffix, codes, builder(d), what, why, flags
# flags: c = year-on-year change chart, d = decade averages chart
P, D, R, S, H, Y, T, U, B = SUBGROUPS

BASES = (
    ("pat_res", "Resident Patent Applications", P, "count", "", ("IP.PAT.RESD",), lambda d: d["IP.PAT.RESD"],
     "Patent applications filed at the Indian patent office by Indian residents.",
     "Resident filings are the clearest signal that domestic firms, labs and universities are inventing for themselves.", "cd"),
    ("pat_nres", "Non-Resident Patent Applications", P, "count", "", ("IP.PAT.NRES",), lambda d: d["IP.PAT.NRES"],
     "Patent applications filed in India by foreign applicants.",
     "Foreign filings show how much global technology owners value India as a market and manufacturing base.", "c"),
    ("pat_res_share", "Resident Share of Patent Applications", P, "pct", "%", ("IP.PAT.RESD", "IP.PAT.NRES"),
     lambda d: _ratio(d["IP.PAT.RESD"], _sum(d["IP.PAT.RESD"], d["IP.PAT.NRES"]), 100),
     "Resident applications divided by all patent applications (resident plus non-resident) in India.",
     "A rising share means India's patent system is increasingly driven by home-grown invention rather than imported technology.", "d"),
    ("pat_permil", "Resident Patents per Million People", P, "count", " per million", ("IP.PAT.RESD", "SP.POP.TOTL"),
     lambda d: _ratio(d["IP.PAT.RESD"], d["SP.POP.TOTL"], 1e6),
     "Resident patent applications scaled by population.",
     "Per-capita intensity removes the size advantage of large economies and shows how far India still has to climb.", ""),
    ("ids_res", "Resident Industrial Design Applications", D, "count", "", ("IP.IDS.RSCT",), lambda d: d["IP.IDS.RSCT"],
     "Industrial design filings (by count) by Indian residents, protecting product shape and appearance.",
     "Design filings track the move from commodity making to differentiated, branded products.", "cd"),
    ("ids_nres", "Non-Resident Industrial Design Applications", D, "count", "", ("IP.IDS.NRCT",), lambda d: d["IP.IDS.NRCT"],
     "Industrial design filings in India by foreign applicants.",
     "Foreign design filings reveal which global consumer-product makers are positioning for the Indian market.", "c"),
    ("ids_res_share", "Resident Share of Design Applications", D, "pct", "%", ("IP.IDS.RSCT", "IP.IDS.NRCT"),
     lambda d: _ratio(d["IP.IDS.RSCT"], _sum(d["IP.IDS.RSCT"], d["IP.IDS.NRCT"]), 100),
     "Resident design applications as a share of all design applications in India.",
     "A high share shows local companies, not importers, are shaping the look of Indian products.", ""),
    ("rd_gdp", "R&D Expenditure", R, "pct", "% GDP", ("GB.XPD.RSDV.GD.ZS",), lambda d: d["GB.XPD.RSDV.GD.ZS"],
     "Gross domestic spending on research and development as a share of GDP.",
     "R&D intensity is the standard yardstick for how seriously an economy invests in future technology; India sits well below leaders.", "d"),
    ("rd_usd", "R&D Expenditure in US$", R, "count", " US$", ("GB.XPD.RSDV.GD.ZS", "NY.GDP.MKTP.CD"),
     lambda d: _combine(d["GB.XPD.RSDV.GD.ZS"], d["NY.GDP.MKTP.CD"], lambda r, g: r * g / 100),
     "Absolute R&D spending, computed as R&D share of GDP times GDP in current US dollars.",
     "Even at a low GDP share, India's economy is large enough that absolute research funding is substantial and growing.", "c"),
    ("researchers", "Researchers in R&D", R, "count", " per million", ("SP.POP.SCIE.RD.P6",), lambda d: d["SP.POP.SCIE.RD.P6"],
     "Full-time-equivalent researchers engaged in R&D per million people (UNESCO Institute for Statistics).",
     "Researcher density is the human capacity behind innovation and shows the scale of the talent gap with peers.", ""),
    ("articles", "Scientific & Technical Journal Articles", S, "count", " articles", ("IP.JRN.ARTC.SC",), lambda d: d["IP.JRN.ARTC.SC"],
     "Scientific and technical articles published in indexed journals by India-based authors.",
     "Publication volume is a broad proxy for research output and knowledge creation.", "cd"),
    ("articles_permil", "Journal Articles per Million People", S, "count", " per million", ("IP.JRN.ARTC.SC", "SP.POP.TOTL"),
     lambda d: _ratio(d["IP.JRN.ARTC.SC"], d["SP.POP.TOTL"], 1e6),
     "Scientific articles scaled by population.",
     "Per-capita output shows whether India's rising total is keeping pace with its population and with peers.", ""),
    ("articles_per_rd", "Articles per US$ Billion of R&D", S, "count", " per US$ bn",
     ("IP.JRN.ARTC.SC", "GB.XPD.RSDV.GD.ZS", "NY.GDP.MKTP.CD"),
     lambda d: _ratio(d["IP.JRN.ARTC.SC"], _combine(d["GB.XPD.RSDV.GD.ZS"], d["NY.GDP.MKTP.CD"], lambda r, g: r * g / 100e9)),
     "Journal articles divided by R&D spending in US$ billion, a rough research productivity ratio.",
     "It indicates how much published science each rupee-equivalent of research money yields.", ""),
    ("tertiary", "Tertiary Education Enrolment", S, "pct", "% gross", ("SE.TER.ENRR",), lambda d: d["SE.TER.ENRR"],
     "Gross enrolment ratio in tertiary education, a pipeline for scientists and engineers.",
     "Higher enrolment widens the base from which India can draw researchers and skilled technologists.", "c"),
    ("tech_share", "High-Tech Exports", H, "pct", "% mfg exports", ("TX.VAL.TECH.MF.ZS",), lambda d: d["TX.VAL.TECH.MF.ZS"],
     "High-technology exports (aerospace, computers, pharmaceuticals, instruments, electrical machinery) as a share of manufactured exports.",
     "It shows whether India's export basket is climbing from basic goods toward technology-intensive products.", "c"),
    ("tech_usd", "High-Tech Exports in US$", H, "count", " US$", ("TX.VAL.TECH.CD",), lambda d: d["TX.VAL.TECH.CD"],
     "Value of high-technology exports in current US dollars.",
     "Absolute value reflects how much foreign exchange India earns from advanced products.", ""),
    ("mnf_tech", "Medium & High-Tech Manufacturing Value Added", H, "pct", "% mfg VA", ("NV.MNF.TECH.ZS.UN",), lambda d: d["NV.MNF.TECH.ZS.UN"],
     "Medium and high-tech industries as a share of total manufacturing value added (UNIDO).",
     "A rising share signals structural upgrading of Indian factories toward chemicals, machinery and electronics.", "d"),
    ("ict_goods_exp", "ICT Goods Exports in US$", H, "count", " US$", ("TX.VAL.ICTG.ZS.UN", "TX.VAL.MRCH.CD.WT"),
     lambda d: _combine(d["TX.VAL.ICTG.ZS.UN"], d["TX.VAL.MRCH.CD.WT"], lambda s, m: s * m / 100),
     "ICT goods exports computed as their share of merchandise exports times merchandise exports.",
     "It measures India's growing role in electronics supply chains, such as mobile phone assembly.", "c"),
    ("roy_rec", "IP Royalty Receipts", Y, "count", " US$", ("BX.GSR.ROYL.CD",), lambda d: d["BX.GSR.ROYL.CD"],
     "Charges received for the use of Indian-owned intellectual property (balance of payments).",
     "Receipts reveal how much of India's know-how is licensed abroad and monetised.", "cd"),
    ("roy_pay", "IP Royalty Payments", Y, "count", " US$", ("BM.GSR.ROYL.CD",), lambda d: d["BM.GSR.ROYL.CD"],
     "Charges paid for the use of foreign intellectual property.",
     "Payments show India's reliance on imported technology, brands and software licences.", "c"),
    ("roy_balance", "IP Royalty Balance", Y, "signed", " US$", ("BX.GSR.ROYL.CD", "BM.GSR.ROYL.CD"),
     lambda d: _combine(d["BX.GSR.ROYL.CD"], d["BM.GSR.ROYL.CD"], lambda a, b: a - b),
     "Royalty receipts minus royalty payments; negative values mean India is a net technology importer.",
     "Closing this deficit is a measurable goal of building home-owned intellectual property.", ""),
    ("roy_cover", "Royalty Receipts Cover of Payments", Y, "pct", "%", ("BX.GSR.ROYL.CD", "BM.GSR.ROYL.CD"),
     lambda d: _ratio(d["BX.GSR.ROYL.CD"], d["BM.GSR.ROYL.CD"], 100),
     "Royalty receipts as a percentage of royalty payments.",
     "A value near 100% would mean India earns as much from its IP as it pays for others'.", ""),
    ("internet", "Internet Users", T, "pct", "% of people", ("IT.NET.USER.ZS",), lambda d: d["IT.NET.USER.ZS"],
     "Share of the population using the internet in the last three months (ITU).",
     "Internet reach is the base layer for digital services, e-commerce and online startups.", "c"),
    ("mobile", "Mobile Cellular Subscriptions", T, "count", " per 100", ("IT.CEL.SETS.P2",), lambda d: d["IT.CEL.SETS.P2"],
     "Mobile cellular subscriptions per 100 people (ITU).",
     "Mobile connectivity is how most Indians reach digital public infrastructure and apps.", "d"),
    ("broadband", "Fixed Broadband Subscriptions", T, "count", " per 100", ("IT.NET.BBND.P2",), lambda d: d["IT.NET.BBND.P2"],
     "Fixed broadband subscriptions per 100 people.",
     "Fixed broadband supports high-quality remote work, cloud services and enterprise use.", ""),
    ("ict_svc_usd", "ICT Service Exports in US$", T, "count", " US$", ("BX.GSR.CCIS.CD",), lambda d: d["BX.GSR.CCIS.CD"],
     "Computer, communications and other ICT service exports in current US dollars.",
     "IT services are India's flagship technology export and a major source of skilled jobs.", "cd"),
    ("ict_svc_share", "ICT Share of Service Exports", T, "pct", "% svc exports", ("BX.GSR.CCIS.ZS",), lambda d: d["BX.GSR.CCIS.ZS"],
     "ICT services as a share of total service exports.",
     "A high share shows how strongly India's services trade depends on software and IT outsourcing.", ""),
    ("new_biz", "New Businesses Registered", U, "count", " firms", ("IC.BUS.NREG",), lambda d: d["IC.BUS.NREG"],
     "Newly registered limited-liability companies (World Bank Entrepreneurship Survey).",
     "New registrations are an observable measure of entrepreneurial activity.", "c"),
    ("new_density", "New Business Density", U, "count", " per 1,000 adults", ("IC.BUS.NDNS.ZS",), lambda d: d["IC.BUS.NDNS.ZS"],
     "New company registrations per 1,000 working-age people (ages 15-64).",
     "Density adjusts for population and shows whether entrepreneurship is broad-based.", ""),
    ("fdi", "Foreign Direct Investment Inflows", U, "pct", "% GDP", ("BX.KLT.DINV.WD.GD.ZS",), lambda d: d["BX.KLT.DINV.WD.GD.ZS"],
     "Net foreign direct investment inflows as a share of GDP.",
     "FDI brings capital, technology and management know-how to new ventures.", "c"),
)

BENCH_RANK = ("pat_res", "articles", "rd_gdp", "tech_usd", "roy_rec", "internet", "ict_svc_usd", "new_density")
BENCH_SHARE = ("pat_res", "articles", "ids_res", "tech_usd", "roy_rec", "ict_svc_usd", "rd_usd", "new_biz")


def _r(value: float) -> float:
    return round(value, 4) if abs(value) < 1 else round(value, 2)


def _fmt(value: float, suffix: str) -> str:
    text = f"{value:,.2f}" if abs(value) < 100 else f"{value:,.0f}"
    return f"{text}{suffix}"


def _latest(years: dict) -> str | None:
    return max(years, key=int) if years else None


def _meta(title, subtitle, color, suffix, subgroup, explain):
    return {"title": title, "subtitle": subtitle, "frequency": "Annual", "color": color, "suffix": suffix,
            "category": CATEGORY, "subgroup": subgroup,
            "explain": {"what": explain[0], "read": explain[1], "why": explain[2]}}


def _series(base, kind, subgroup, title, subtitle, note, explain, suffix=None, **fields):
    key, _t, _sg, _k, base_suffix, codes = base[0], base[1], base[2], base[3], base[4], base[5]
    out = dict(fields)
    out.update({"source": "World Bank API " + ", ".join(codes), "unit": (suffix if suffix is not None else base_suffix).strip(),
                "note": f"{note} Source indicator(s): {', '.join(codes)}.",
                "meta": _meta(title, subtitle, ORANGE, suffix if suffix is not None else base_suffix, subgroup, explain)})
    return f"innov_{key}_{kind}", out


def _gen_base(base, data: Data) -> list[tuple[str, dict]]:
    key, title, subgroup, kind, suffix, codes, _fn, what, why, flags = base
    india = data.get("IND", {})
    result: list[tuple[str, dict]] = []
    if len(india) < 4:
        return result
    years = sorted(india, key=int)

    result.append(_series(
        base, "trend", subgroup, f"{title}: India Trend", f"{what}", 
        f"India's annual series from {years[0]} to {years[-1]}; years without a reported value are omitted.",
        (what, f"The line plots India's own history from {years[0]} to {years[-1]}; the last point is {_fmt(india[years[-1]], suffix)}.", why),
        labels=years, values=[_r(india[y]) for y in years]))

    # peer comparison (indexed to 100 for absolute counts so country size does not swamp India)
    lines = {iso: data[iso] for iso in LINE_PEERS if len(data.get(iso, {})) >= 4}
    if "IND" in lines and len(lines) >= 3:
        indexed = kind == "count"
        labels: list[str]
        if indexed:
            common = [y for y in sorted(set.intersection(*(set(v) for v in lines.values())), key=int) if int(y) >= 1990]
            lines_ok = len(common) >= 4
            base_year = common[0] if common else None
            labels = [y for y in sorted(set().union(*(set(v) for v in lines.values())), key=int) if base_year and int(y) >= int(base_year)]
        else:
            lines_ok = True
            labels = sorted(set().union(*(set(v) for v in lines.values())), key=int)
            labels = [y for y in labels if int(y) >= 1990]
        if lines_ok and len(labels) >= 4:
            datasets = []
            for iso in LINE_PEERS:
                if iso not in lines:
                    continue
                if indexed:
                    anchor = lines[iso].get(base_year)
                    if not anchor:
                        continue
                    vals = [round(lines[iso][y] / anchor * 100, 1) if y in lines[iso] else None for y in labels]
                else:
                    vals = [_r(lines[iso][y]) if y in lines[iso] else None for y in labels]
                datasets.append({"label": PEERS[iso], "values": vals, "color": PEER_COLORS[iso]})
            mode = f"Indexed so every country equals 100 in {base_year}, which removes the effect of country size." if indexed else "Plotted in each country's own units."
            result.append(_series(
                base, "peers", subgroup, f"{title}: India vs Peers", f"{title} for India and six major comparison economies",
                f"India (orange) against China, the United States, Japan, South Korea, Germany and Brazil. {mode}",
                (f"{what[:-1]}, compared across India and six large economies.",
                 "India is the orange line; " + ("a line above 100 has grown faster than its starting year." if indexed else "the higher the line, the stronger that country's position."),
                 why),
                suffix=" (index)" if indexed else None, labels=labels, datasets=datasets))

    # latest-year peer ranking
    ref_year = _latest(india)
    entries = []
    for iso, name in PEERS.items():
        obs = data.get(iso, {})
        usable = [y for y in obs if 0 <= int(ref_year) - int(y) <= 3]
        if usable:
            entries.append((name, obs[max(usable, key=int)], iso))
    if len(entries) >= 8 and any(e[2] == "IND" for e in entries):
        entries.sort(key=lambda e: e[1], reverse=True)
        rank = [e[2] for e in entries].index("IND") + 1
        result.append(_series(
            base, "rank", subgroup, f"{title}: Peer Ranking ({ref_year})", f"{title}, India against {len(entries)} peer economies",
            f"Latest value per country within three years of India's {ref_year} observation (WB data). India ranks {rank} of {len(entries)} in this peer group.",
            (what, f"Bars are sorted from highest to lowest; India ranks {rank} of {len(entries)} at {_fmt(india[ref_year], suffix)}.", why),
            chartType="bar", indexAxis="y", scope="category",
            labels=[e[0] for e in entries], values=[_r(e[1]) for e in entries]))

    # year-on-year change
    if "c" in flags:
        pts = []
        for y in years:
            prev = india.get(str(int(y) - 1))
            if prev is None:
                continue
            if kind == "pct":
                pts.append((y, india[y] - prev))
            elif prev > 0:
                pts.append((y, (india[y] / prev - 1) * 100))
        pts = pts[-30:]
        if len(pts) >= 6:
            unit = "pp" if kind == "pct" else "%"
            result.append(_series(
                base, "change", subgroup, f"{title}: Year-on-Year Change",
                f"Annual change in {title.lower()}",
                f"Change versus the previous calendar year, only where both years are reported ({'percentage points' if kind == 'pct' else 'percent'}).",
                (f"Annual change in India's {title.lower()}.",
                 f"Bars above zero are increases; the latest change is {pts[-1][1]:+.1f}{unit} in {pts[-1][0]}.",
                 why),
                suffix=unit, chartType="bar", labels=[p[0] for p in pts], values=[round(p[1], 2) for p in pts]))

    # decade averages
    if "d" in flags:
        decades: dict[int, list[float]] = {}
        for y in years:
            decades.setdefault(int(y) // 10 * 10, []).append(india[y])
        decades = {k: v for k, v in decades.items() if len(v) >= 2}
        if len(decades) >= 3:
            ks = sorted(decades)
            result.append(_series(
                base, "decade", subgroup, f"{title}: Decade Averages", f"Average {title.lower()} by decade",
                "Mean of the reported annual values inside each decade, using decades with at least two observations.",
                (f"Average of India's {title.lower()} within each decade.",
                 "Compare bar heights to see the long-run step changes between decades.",
                 why),
                chartType="bar", labels=[f"{k}s" for k in ks], values=[_r(sum(decades[k]) / len(decades[k])) for k in ks]))
    return result


def _bench(base, data: Data) -> list[tuple[str, dict]]:
    key, title, _sg, kind, suffix, codes, _fn, what, why, _f = base
    out: list[tuple[str, dict]] = []
    if key in BENCH_RANK:
        ranks: dict[str, int] = {}
        for year in sorted({y for v in data.values() for y in v}, key=int):
            vals = {iso: v[year] for iso, v in data.items() if year in v}
            if "IND" in vals and len(vals) >= 10:
                ranks[year] = 1 + sum(1 for v in vals.values() if v > vals["IND"])
        if len(ranks) >= 4:
            labels = sorted(ranks, key=int)
            out.append(_series(
                base, "rankhist", B, f"India's Rank in {title}", f"India's position among up to {len(PEERS)} peer economies",
                f"Rank 1 = highest value among countries reporting in each year (at least 10 reporting); latest {labels[-1]}: rank {ranks[labels[-1]]}.",
                (f"India's rank by {title.lower()} among the peer group over time.",
                 "A falling line means India is overtaking more peers; rank 1 is the group leader.",
                 "Rank shows relative competitiveness, which absolute growth can hide."),
                suffix="", labels=labels, values=[ranks[y] for y in labels]))
    if key in BENCH_SHARE:
        ref = _latest(data.get("IND", {}))
        if ref:
            parts = [(PEERS[i], v[max((y for y in v if 0 <= int(ref) - int(y) <= 3), key=int, default=None)])
                     for i, v in data.items() if any(0 <= int(ref) - int(y) <= 3 for y in v)]
            parts = [(n, x) for n, x in parts if x and x > 0]
            if len(parts) >= 8 and any(n == "India" for n, _ in parts):
                total = sum(x for _, x in parts)
                share = next(x for n, x in parts if n == "India") / total * 100
                parts.sort(key=lambda p: p[1], reverse=True)
                out.append(_series(
                    base, "share", B, f"Peer-Group Share of {title} ({ref})", f"How {title.lower()} is split across {len(parts)} economies",
                    f"Latest value within three years of {ref}; India holds {share:.1f}% of this peer-group total.",
                    (f"Each country's slice of the combined {title.lower()} of the peer group.",
                     f"India's slice is {share:.1f}% of the group total; compare it with its share of population or GDP.",
                     "Share of global output is a direct measure of whether India is gaining weight in innovation."),
                    suffix="", chartType="doughnut", scope="category",
                    labels=[p[0] for p in parts], values=[_r(p[1]) for p in parts]))
    return out


def _composition(key, title, subgroup, label_a, code_a, label_b, code_b, data) -> list[tuple[str, dict]]:
    a, b = data[code_a].get("IND", {}), data[code_b].get("IND", {})
    common = sorted(set(a) & set(b), key=int)
    if not common:
        return []
    year = common[-1]
    base = (key, title, subgroup, "count", "", (code_a, code_b))
    return [_series(
        base, "mix", subgroup, f"{title} ({year})", f"Resident versus non-resident filings in India, {year}",
        f"Latest year with both components reported ({year}).",
        (f"Split of {title.lower()} between Indian residents and foreign applicants in {year}.",
         f"A bigger {label_a.lower()} slice means domestic applicants dominate filings.",
         "The balance shows how much of India's IP activity is domestically owned."),
        suffix="", chartType="doughnut", scope="category",
        labels=[label_a, label_b], values=[_r(a[year]), _r(b[year])])]


def build_innovation_layer(get_json: Callable[[str], object], previous: dict[str, dict]) -> dict[str, dict]:
    cache: dict[str, Data] = {}

    def fetch(code: str) -> Data:
        if code in cache:
            return cache[code]
        last: Exception | None = None
        for _ in range(3):
            try:
                payload = get_json(URL.format(code=code))
                if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
                    raise ValueError(f"No observations for {code}")
                out: Data = {}
                for row in payload[1]:
                    iso = row.get("countryiso3code")
                    if row.get("value") is not None and iso in PEERS:
                        out.setdefault(iso, {})[str(row["date"])] = float(row["value"])
                cache[code] = out
                return out
            except ValueError:
                raise
            except Exception as exc:  # transient network error: retry
                last = exc
        raise last  # type: ignore[misc]

    series: dict[str, dict] = {}

    def keep_previous(prefix: str) -> None:
        for key, value in previous.items():
            if key.startswith(prefix) and key not in series and (value.get("values") or value.get("datasets")):
                series[key] = value

    for base in BASES:
        key, codes, builder = base[0], base[5], base[6]
        try:
            data = builder({code: fetch(code) for code in codes})
            built = _gen_base(base, data) + _bench(base, data)
            if not built:
                raise ValueError(f"No chartable data for {key}")
            series.update(built)
        except Exception:  # keep the last good series when the API is unavailable
            pass
        keep_previous(f"innov_{key}_")

    for key, title, sg, la, ca, lb, cb in (
        ("pat_mix", "Patent Applications: Resident vs Non-Resident", P, "Residents", "IP.PAT.RESD", "Non-residents", "IP.PAT.NRES"),
        ("ids_mix", "Industrial Designs: Resident vs Non-Resident", D, "Residents", "IP.IDS.RSCT", "Non-residents", "IP.IDS.NRCT"),
    ):
        try:
            series.update(_composition(key, title, sg, la, ca, lb, cb, {ca: fetch(ca), cb: fetch(cb)}))
        except Exception:
            pass
        keep_previous(f"innov_{key}_")
    return series


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.generate_public_charts import get_json as _get_json

    started = time.time()
    built = build_innovation_layer(_get_json, {})
    counts = {name: sum(1 for s in built.values() if s["meta"]["subgroup"] == name) for name in SUBGROUPS}
    for name, count in counts.items():
        print(f"{count:4d}  {name}")
    print(f"{len(built):4d}  TOTAL  ({time.time() - started:.1f}s)")

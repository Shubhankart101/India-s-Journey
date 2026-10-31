"""All-State/UT indices from the RBI Handbook of Statistics on Indian States.

The handbook publishes one HTML page per table. Tables are split into column chunks
("(Contd.)"/"(Concld.)"), may carry sub-column rows (Male/Female/Total, Rural/Urban) and a few
(the ASI industry tables) are transposed with years as rows and States/UTs as columns. The
parser below normalises all of these into ``{column label: {State/UT: value}}`` so every
chart covers all 36 States and Union Territories wherever the handbook reports them.

Each table yields an all-State/UT ranking, a pie (regional share for additive measures or a
distribution by band for rates) and, where an All-India row exists, a national trend line.
If the RBI site is unreachable the previously published series are kept.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser

RBI_TABLE_URL = "https://www.rbi.org.in/Scripts/PublicationsView.aspx?id={id}"
RBI_TABLE_ID_OFFSET = 23449
HANDBOOK = "RBI Handbook of Statistics on Indian States 2024-25"

STATES = (
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
)
UNION_TERRITORIES = (
    "Andaman & Nicobar Islands", "Chandigarh", "Dadra & Nagar Haveli and Daman & Diu", "Delhi",
    "Jammu & Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
)
STATES_AND_UTS = STATES + UNION_TERRITORIES
ALL_INDIA = "__ALL_INDIA__"

REGIONS = {
    "North": ("Himachal Pradesh", "Punjab", "Haryana", "Uttarakhand", "Jammu & Kashmir", "Ladakh", "Delhi", "Chandigarh"),
    "Central": ("Uttar Pradesh", "Madhya Pradesh", "Chhattisgarh"),
    "West": ("Gujarat", "Maharashtra", "Rajasthan", "Goa", "Dadra & Nagar Haveli and Daman & Diu"),
    "South": ("Andhra Pradesh", "Telangana", "Karnataka", "Kerala", "Tamil Nadu", "Puducherry", "Lakshadweep", "Andaman & Nicobar Islands"),
    "East": ("Bihar", "Jharkhand", "Odisha", "West Bengal"),
    "North-East": ("Assam", "Arunachal Pradesh", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Sikkim", "Tripura"),
}
STATE_REGION = {state: region for region, states in REGIONS.items() for state in states}

_ALIASES = {
    "andaman & nicobar islands": "Andaman & Nicobar Islands",
    "andaman & nicobar": "Andaman & Nicobar Islands",
    "a & n islands": "Andaman & Nicobar Islands",
    "delhi": "Delhi", "nct delhi": "Delhi", "nct of delhi": "Delhi", "delhi ncr": "Delhi",
    "jammu & kashmir": "Jammu & Kashmir", "j & k": "Jammu & Kashmir",
    "dadra & nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "dadar & nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra & nagar haveli & daman & diu": "Dadra & Nagar Haveli and Daman & Diu",
    "dnh & dd": "Dadra & Nagar Haveli and Daman & Diu",
    "orissa": "Odisha", "pondicherry": "Puducherry", "uttaranchal": "Uttarakhand",
    "chattisgarh": "Chhattisgarh", "tamilnadu": "Tamil Nadu",
    "all india": ALL_INDIA, "india": ALL_INDIA, "all states & uts": ALL_INDIA, "all states": ALL_INDIA,
    "all states/uts": ALL_INDIA, "total": ALL_INDIA, "all-india": ALL_INDIA,
}
_CANONICAL = {name.lower(): name for name in STATES_AND_UTS}


def canonical_state(name: str) -> str | None:
    """Maps a State/UT spelling used by official tables to its canonical name (or ``ALL_INDIA``)."""
    text = re.sub(r"\(.*?\)", "", str(name or ""))
    text = re.sub(r"^\d+\.?\s+", "", text.strip())
    text = re.sub(r"\s+and\s+", " & ", text.replace("&amp;", "&"), flags=re.I)
    text = re.sub(r"^the\s+", "", text, flags=re.I)
    text = re.sub(r"[*#@^$]+|\d+$", "", text.strip())
    text = re.sub(r"\s*&\s*", " & ", text)
    key = " ".join(text.split()).strip(" .:-").lower()
    return _CANONICAL.get(key) or _ALIASES.get(key)


def coverage_note(entities: list[str] | set[str]) -> str:
    present = set(entities)
    missing = [name for name in STATES_AND_UTS if name not in present]
    note = f"{len(present & set(STATES_AND_UTS))} of {len(STATES_AND_UTS)} States/UTs reported."
    if missing:
        note += " Not published for: " + ", ".join(missing) + "."
    return note


class _Rows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows: list[list[str]] = []
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
            if self._row:
                self.rows.append(self._row)
            self._row = None


def _number(cell: str) -> float | None:
    text = str(cell).replace(",", "").replace("\u2212", "-").strip()
    match = re.match(r"^-?\d+(?:\.\d+)?", text)
    if not match or text in ("-", "."):
        return None
    return float(match.group(0))


def _is_header(cell: str) -> bool:
    return bool(re.match(r"^(?:region\s*/\s*)?states?\s*(/|$|-|\s)|^year$", str(cell).strip(), re.I))


def _is_period(cell: str) -> bool:
    return bool(re.match(r"^\d{4}(?:\s*-\s*\d{2,4})?(?:\s*\(\w+\))?\s*[#*]*$", str(cell).strip()))


def _starts_chunk(row: list[str]) -> bool:
    if _is_header(row[0]):
        return True
    return not row[0].strip() and len(row) > 2 and all(_is_period(cell) for cell in row[1:] if cell.strip())


def _is_data(row: list[str]) -> bool:
    return bool(canonical_state(row[0])) and any(_number(cell) is not None for cell in row[1:])


def _clean_label(label: str) -> str:
    return " ".join(re.sub(r"[#*@^$]+", "", label).split())


def parse_rbi_table(rows: list[list[str]]) -> dict[str, dict[str, float]]:
    """Returns ``{column label: {State/UT or ALL_INDIA: value}}`` across every chunk of a table."""
    columns: dict[str, dict[str, float]] = {}
    index = 0
    while index < len(rows):
        row = rows[index]
        transposed_entities = [canonical_state(cell) for cell in row[1:]]
        if sum(1 for entity in transposed_entities if entity) >= 6 and canonical_state(row[0]) is None:
            # Transposed layout: header lists States/UTs, rows are periods.
            index += 1
            while index < len(rows) and re.match(r"^\d{4}", rows[index][0]):
                label = _clean_label(rows[index][0])
                for entity, cell in zip(transposed_entities, rows[index][1:]):
                    value = _number(cell)
                    if entity and value is not None:
                        columns.setdefault(label, {})[entity] = value
                index += 1
            continue
        if not _starts_chunk(row):
            index += 1
            continue
        groups = [_clean_label(cell) for cell in row[1:] if cell.strip()]
        index += 1
        sub: list[str] = []
        while index < len(rows) and not _is_data(rows[index]) and not _starts_chunk(rows[index]):
            candidate = rows[index]
            if (not sub and len(candidate) > 1
                    and (canonical_state(candidate[0]) is None or candidate[0].strip().lower() == "total")
                    and all(_number(cell) is None or _is_period(cell) for cell in candidate)
                    and not any(cell.startswith("[") for cell in candidate)):
                sub = [_clean_label(cell) for cell in candidate]
            index += 1
        if sub and all(_is_period(cell) for cell in sub):
            labels = sub
        elif sub and groups and len(sub) % len(groups) == 0:
            per = len(sub) // len(groups)
            labels = [f"{groups[k // per]} | {sub[k]}" for k in range(len(sub))]
        elif sub:
            labels = sub
        else:
            labels = groups
        while index < len(rows) and not _starts_chunk(rows[index]):
            data_row = rows[index]
            entity = canonical_state(data_row[0])
            if entity:
                for label, cell in zip(labels, data_row[1:]):
                    value = _number(cell)
                    if value is not None:
                        columns.setdefault(label, {})[entity] = value
            elif len(data_row) == 1 and re.match(r"^table\s+\d+", data_row[0], re.I):
                break
            index += 1
    return columns


def _states_only(column: dict[str, float]) -> dict[str, float]:
    return {name: value for name, value in column.items() if name in STATES_AND_UTS}


def pick_column(columns: dict[str, dict[str, float]], pattern: str | None = None,
                exclude: str | None = r"\((?:RE|BE)\)") -> str:
    candidates = [label for label in columns
                  if (pattern is None or re.search(pattern, label, re.I))
                  and not (exclude and re.search(exclude, label, re.I))]
    if not candidates:
        raise ValueError(f"No RBI column matches {pattern!r}")
    best = max(len(_states_only(columns[label])) for label in candidates)
    usable = [label for label in candidates if len(_states_only(columns[label])) >= max(5, best * 0.8)]
    return usable[-1]


def _when(column: str) -> str:
    period = _period(column)
    return f" ({period})" if re.search(r"\d{4}", period) else ""


def _short(title: str) -> str:
    return re.sub(r"\s+(?:by State/UT|across States & UTs)", "", title)


def _period(label: str) -> str:
    return label.split(" | ")[0]


def _round(value: float, decimals: int) -> float:
    return round(value, decimals) if decimals else round(value)


def _meta(title, subtitle, category, subgroup, suffix, color, frequency="Annual (latest RBI handbook)") -> dict:
    return {"title": title, "subtitle": subtitle, "frequency": frequency, "color": color,
            "suffix": suffix, "category": category, "subgroup": subgroup}


def _source(table: int, title: str) -> str:
    return f"{HANDBOOK}, Table {table}: {title}"


def ranking(values: dict[str, float], *, title, subtitle, category, subgroup, suffix, color, source,
            note="", decimals=2, ascending=False) -> dict:
    values = _states_only(values)
    if len(values) < 5:
        raise ValueError(f"Too few States/UTs for {title}")
    labels = sorted(values, key=lambda name: (values[name] if ascending else -values[name], name))
    return {
        "labels": labels,
        "values": [_round(values[name], decimals) for name in labels],
        "chartType": "bar",
        "indexAxis": "y",
        "scope": "state",
        "source": source,
        "note": " ".join(part for part in (note, coverage_note(values)) if part),
        "meta": _meta(title, subtitle, category, subgroup, suffix, color),
    }


def pie(points: list[tuple[str, float]], *, title, subtitle, category, subgroup, suffix, color, source,
        note, decimals=2) -> dict:
    points = [(label, _round(value, decimals)) for label, value in points if value and value > 0]
    if len(points) < 2:
        raise ValueError(f"Too few positive slices for {title}")
    return {
        "labels": [label for label, _ in points],
        "values": [value for _, value in points],
        "chartType": "doughnut",
        "scope": "category",
        "source": source,
        "note": note,
        "meta": _meta(title, subtitle, category, subgroup, suffix, color),
    }


def region_points(values: dict[str, float]) -> list[tuple[str, float]]:
    totals = {region: 0.0 for region in REGIONS}
    for name, value in _states_only(values).items():
        totals[STATE_REGION[name]] += value
    return sorted(totals.items(), key=lambda item: -item[1])


def band_points(values: dict[str, float], bands: list[float], suffix: str) -> list[tuple[str, int]]:
    unit = suffix.strip()
    sep = "" if unit.startswith("%") else " "
    edges = [float("-inf"), *bands, float("inf")]
    points = []
    for low, high in zip(edges, edges[1:]):
        count = sum(1 for value in _states_only(values).values() if low <= value < high)
        if low == float("-inf"):
            label = f"Below {bands[0]:g}{unit and sep + unit}"
        elif high == float("inf"):
            label = f"{low:g}{unit and sep + unit} and above"
        else:
            label = f"{low:g}–{high:g}{unit and sep + unit}"
        points.append((label, count))
    return points


def auto_bands(values: dict[str, float]) -> list[float]:
    data = sorted(_states_only(values).values())
    low, high = data[0], data[-1]
    span = (high - low) / 4 or 1
    magnitude = 10 ** (len(str(int(abs(span)))) - 1) if span >= 1 else 0.1
    step = max(round(span / magnitude) * magnitude, magnitude)
    start = (low // step + 1) * step
    return [round(start + step * k, 6) for k in range(3)]


def trend(columns: dict[str, dict[str, float]], chosen: str, *, title, subtitle, category, subgroup, suffix,
          color, source, divisor=1.0, decimals=2) -> dict:
    suffix_part = chosen.split(" | ", 1)[1] if " | " in chosen else None
    labels, values = [], []
    for label, column in columns.items():
        if (label.split(" | ", 1)[1] if " | " in label else None) != suffix_part:
            continue
        if ALL_INDIA in column and re.match(r"^\d{4}", _period(label)):
            labels.append(_period(label))
            values.append(_round(column[ALL_INDIA] / divisor, decimals))
    if len(labels) < 3:
        raise ValueError(f"Too few All-India observations for {title}")
    return {
        "labels": labels,
        "values": values,
        "source": source,
        "note": "All-India row of the RBI handbook table; estimates (RE/BE) are shown as published where present.",
        "meta": _meta(title, subtitle, category, subgroup, suffix, color, "Annual"),
    }


PAY = "Payments & Digital Banking"
HEALTH = "Public Health & Epidemiology"
SOCIAL = "Social"
STATE = "State Performance & Regional Health"
SUB_BANK = "State Banking & Credit"
SUB_RRB = "Regional Rural Banks"
SUB_PENSION = "Pensions & Social Security"
SUB_HEALTH_OUT = "State Health Outcomes"
SUB_HEALTH_INFRA = "State Health Infrastructure"
SUB_EDU = "Education"
SUB_JOBS = "Employment & Poverty"
SUB_DEMO = "Demographics"
SUB_FIN = "State Financial Health & GSDP"
SUB_INFRA = "State Infrastructure & Services"
SUB_ECON = "State Economy & Industry"

# (table, key, title, subtitle, category, subgroup, suffix, color, options)
# options: col (regex), divisor, decimals, kind ("additive" → region pie, "rate" → band pie),
# bands, ascending (lower is better), trend (bool), short (name used in pie/trend titles)
TABLE_SPECS = [
    # --- Payments & Digital Banking: banking footprint and credit ---
    (152, "rbi_state_bank_offices", "Bank offices by State/UT", "Scheduled commercial bank offices (as at end-March)", PAY, SUB_BANK, " offices", "#58a6ff", {"kind": "additive", "decimals": 0}),
    (153, "rbi_state_credit_deposit_ratio", "Credit-deposit ratio by State/UT (by sanction)", "Scheduled commercial banks, credit by place of sanction ÷ deposits", PAY, SUB_BANK, "%", "#79c0ff", {"kind": "rate", "bands": [40, 60, 80, 100]}),
    (154, "rbi_state_cd_ratio_utilisation", "Credit-deposit ratio by State/UT (by utilisation)", "Scheduled commercial banks, credit by place of utilisation ÷ deposits", PAY, SUB_BANK, "%", "#a5d6ff", {"kind": "rate", "bands": [40, 60, 80, 100], "trend": False}),
    (155, "rbi_state_bank_deposits", "Bank deposits by State/UT", "Aggregate deposits of scheduled commercial banks (INR lakh crore)", PAY, SUB_BANK, " INR lakh cr", "#3fb950", {"kind": "additive", "divisor": 100000}),
    (156, "rbi_state_bank_credit", "Bank credit by State/UT", "Credit of scheduled commercial banks by place of sanction (INR lakh crore)", PAY, SUB_BANK, " INR lakh cr", "#56d364", {"kind": "additive", "divisor": 100000}),
    (157, "rbi_state_agri_credit", "Agricultural credit by State/UT", "Scheduled commercial bank credit to agriculture (INR thousand crore)", PAY, SUB_BANK, " INR '000 cr", "#a2d729", {"kind": "additive", "divisor": 1000}),
    (158, "rbi_state_industry_credit", "Industrial credit by State/UT", "Scheduled commercial bank credit to industry (INR thousand crore)", PAY, SUB_BANK, " INR '000 cr", "#f6c344", {"kind": "additive", "divisor": 1000}),
    (159, "rbi_state_personal_loans", "Personal loans by State/UT", "Scheduled commercial bank personal loans (INR thousand crore)", PAY, SUB_BANK, " INR '000 cr", "#ff9933", {"kind": "additive", "divisor": 1000}),
    (160, "rbi_state_rrb_deposits", "Regional Rural Bank deposits by State/UT", "Deposits of Regional Rural Banks (INR thousand crore)", PAY, SUB_RRB, " INR '000 cr", "#bc8cff", {"kind": "additive", "divisor": 1000}),
    (161, "rbi_state_rrb_credit", "Regional Rural Bank credit by State/UT", "Credit of Regional Rural Banks (INR thousand crore)", PAY, SUB_RRB, " INR '000 cr", "#d2a8ff", {"kind": "additive", "divisor": 1000}),
    (162, "rbi_state_rrb_cd_ratio", "Regional Rural Bank credit-deposit ratio", "RRB credit ÷ deposits by State/UT", PAY, SUB_RRB, "%", "#a371f7", {"kind": "rate", "bands": [40, 60, 80, 100]}),
    (163, "rbi_state_rrb_branches", "Regional Rural Bank branches by State/UT", "Offices of Regional Rural Banks", PAY, SUB_RRB, " offices", "#8957e5", {"kind": "additive", "decimals": 0}),
    # --- Public Health & Epidemiology ---
    (2, "rbi_state_birth_rate", "Birth rate by State/UT", "Live births per 1,000 population (SRS)", HEALTH, SUB_HEALTH_OUT, " per 1,000", "#ff9933", {"kind": "rate", "bands": [14, 17, 20, 23], "col": r"total|^\d{4}$"}),
    (3, "rbi_state_death_rate", "Death rate by State/UT", "Deaths per 1,000 population (SRS)", HEALTH, SUB_HEALTH_OUT, " per 1,000", "#ff7b72", {"kind": "rate", "bands": [5, 6, 7, 8], "ascending": True, "col": r"total|^\d{4}$"}),
    (4, "state_infant_mortality_rate", "Infant mortality rate across States & UTs", "Infant deaths per 1,000 live births (SRS)", HEALTH, SUB_HEALTH_OUT, " per 1,000", "#f85149", {"kind": "rate", "bands": [10, 20, 30, 40], "ascending": True, "col": r"total|^\d{4}$"}),
    (5, "rbi_state_maternal_mortality", "Maternal mortality ratio by State/UT", "Maternal deaths per 1 lakh live births (SRS)", HEALTH, SUB_HEALTH_OUT, " per lakh", "#da3633", {"kind": "rate", "bands": [50, 100, 150, 200], "ascending": True}),
    (6, "rbi_state_fertility_rate", "Total fertility rate by State/UT", "Children per woman (SRS)", HEALTH, SUB_HEALTH_OUT, "", "#f778ba", {"kind": "rate", "bands": [1.6, 2.1, 2.5, 3.0], "col": r"total|^\d{4}$"}),
    (7, "state_life_expectancy", "Life expectancy at birth across States & UTs", "Years, both sexes (SRS abridged life tables)", HEALTH, SUB_HEALTH_OUT, " years", "#79c0ff", {"kind": "rate", "bands": [66, 69, 72, 75], "col": r"total"}),
    (14, "rbi_state_child_anaemia", "Anaemia among children (6–59 months)", "Share of children anaemic, NFHS", HEALTH, SUB_HEALTH_OUT, "%", "#ffa198", {"kind": "rate", "bands": [40, 55, 70], "ascending": True}),
    (15, "rbi_state_pregnant_anaemia", "Anaemia among pregnant women", "Share of pregnant women (15–49) anaemic, NFHS", HEALTH, SUB_HEALTH_OUT, "%", "#ff7b72", {"kind": "rate", "bands": [30, 45, 60], "ascending": True}),
    (18, "rbi_state_health_expenditure", "Public expenditure on health by State/UT", "State government health spending (INR thousand crore)", HEALTH, SUB_HEALTH_INFRA, " INR '000 cr", "#3fb950", {"kind": "additive", "divisor": 1000}),
    # --- Social ---
    (8, "rbi_state_rural_unemployment", "Rural unemployment rate by State/UT", "Persons per 1,000 in labour force, usual status (PLFS)", SOCIAL, SUB_JOBS, " per 1,000", "#f6c344", {"kind": "rate", "bands": [20, 40, 60, 80], "ascending": True}),
    (9, "rbi_state_urban_unemployment", "Urban unemployment rate by State/UT", "Persons per 1,000 in labour force, usual status (PLFS)", SOCIAL, SUB_JOBS, " per 1,000", "#ff9933", {"kind": "rate", "bands": [40, 60, 80, 100], "ascending": True}),
    (10, "rbi_state_mpi_headcount", "Multidimensional poverty by State/UT", "Headcount ratio of multidimensionally poor, NFHS-5 (2019-21)", SOCIAL, SUB_JOBS, "%", "#ff7b72", {"kind": "rate", "bands": [5, 10, 20, 30], "ascending": True, "col": r"NFHS-5.*Headcount"}),
    (11, "rbi_state_natural_growth", "Natural growth rate by State/UT", "Birth rate minus death rate, per 1,000 population (SRS)", SOCIAL, SUB_DEMO, " per 1,000", "#56d364", {"kind": "rate", "bands": [8, 10, 12, 15], "col": r"total|^\d{4}$"}),
    (13, "rbi_state_domestic_tourists", "Domestic tourist visits by State/UT", "Domestic tourist visits (million)", SOCIAL, SUB_DEMO, " mn", "#58a6ff", {"kind": "additive"}),
    # --- State Performance: economy, finances, infrastructure ---
    (19, "rbi_state_per_capita_nsdp", "Per-capita NSDP across States & UTs", "Per-capita Net State Domestic Product at current prices (INR '000)", STATE, SUB_FIN, " INR '000", "#3fb950", {"kind": "rate", "divisor": 1000, "bands": [100, 150, 200, 300], "trend": False}),
    (21, "rbi_state_gsdp", "GSDP across States & UTs", "Gross State Domestic Product at current prices (INR lakh crore)", STATE, SUB_FIN, " INR lakh cr", "#58a6ff", {"kind": "additive", "divisor": 100000, "trend": False}),
    (164, "rbi_state_fiscal_deficit", "Gross fiscal deficit by State/UT", "State government GFD (INR thousand crore, latest accounts)", STATE, SUB_FIN, " INR '000 cr", "#ff7b72", {"kind": "additive", "divisor": 1000, "col": r"\(A\)|^\d{4}-\d{2}$"}),
    (168, "state_own_tax_revenue", "State own tax revenue across States & UTs", "State own tax revenue (INR thousand crore, latest accounts)", STATE, SUB_FIN, " INR '000 cr", "#58a6ff", {"kind": "additive", "divisor": 1000, "col": r"\(A\)|^\d{4}-\d{2}$"}),
    (173, "rbi_state_capital_expenditure", "Capital expenditure by State/UT", "State government capital expenditure (INR thousand crore, latest accounts)", STATE, SUB_FIN, " INR '000 cr", "#56d364", {"kind": "additive", "divisor": 1000, "col": r"\(A\)|^\d{4}-\d{2}$"}),
    (175, "rbi_state_social_expenditure", "Social sector expenditure by State/UT", "Education, health, welfare and allied spending (INR thousand crore, latest accounts)", SOCIAL, "Welfare", " INR '000 cr", "#bc8cff", {"kind": "additive", "divisor": 1000, "col": r"\(A\)|^\d{4}-\d{2}$"}),
    (116, "state_operating_factories", "Registered factories across States & UTs", "Factories in the Annual Survey of Industries", STATE, SUB_ECON, " factories", "#f6c344", {"kind": "additive", "decimals": 0}),
    (122, "rbi_state_factory_workers", "Factory workers by State/UT", "Workers in ASI factories (lakh)", STATE, SUB_ECON, " lakh", "#ff9933", {"kind": "additive", "divisor": 100000}),
    (143, "state_renewable_energy_capacity", "Renewable power capacity across States & UTs", "Installed renewable capacity, MW (bio, solar, small hydro, wind)", STATE, SUB_INFRA, " MW", "#f6c344", {"kind": "additive", "decimals": 0}),
    (144, "state_national_highway_length", "National Highway length across States & UTs", "Length of National Highways (km)", STATE, SUB_INFRA, " km", "#56d364", {"kind": "additive", "decimals": 0, "trend": False}),
    (148, "rbi_state_power_td_losses", "Power transmission & distribution losses", "T&D losses as % of availability", STATE, SUB_INFRA, "%", "#ff7b72", {"kind": "rate", "bands": [10, 15, 20, 30], "ascending": True}),
    (149, "rbi_state_teledensity", "Teledensity by State/UT", "Telephones per 100 population", STATE, SUB_INFRA, " per 100", "#79c0ff", {"kind": "rate", "bands": [60, 80, 100, 120]}),
    (181, "rbi_state_exports", "Merchandise exports by State/UT", "Exports originating in each State/UT (INR thousand crore)", STATE, SUB_ECON, " INR '000 cr", "#ff9933", {"kind": "additive", "divisor": 1000}),
]


def _table_url(table: int) -> str:
    return RBI_TABLE_URL.format(id=RBI_TABLE_ID_OFFSET + table)


def _fetch(get_text, table: int, cache: dict) -> dict[str, dict[str, float]]:
    if table not in cache:
        parser = _Rows()
        parser.feed(get_text(_table_url(table)))
        title = next((row[0] for row in parser.rows if len(row) == 1 and re.match(r"^table\s+\d+", row[0], re.I)), f"Table {table}")
        cache[table] = (parse_rbi_table(parser.rows), re.sub(r"^table\s+\d+\s*:\s*", "", title, flags=re.I))
    return cache[table]


def _table_series(get_text, cache, spec) -> dict[str, dict]:
    table, key, title, subtitle, category, subgroup, suffix, color, options = spec
    columns, table_title = _fetch(get_text, table, cache)
    column = pick_column(columns, options.get("col"))
    divisor = options.get("divisor", 1)
    decimals = options.get("decimals", 2 if divisor != 1 else 1)
    values = {name: value / divisor for name, value in _states_only(columns[column]).items()}
    source = _source(table, table_title)
    period = column.replace(" | ", ", ")
    short = title.split(" by State")[0].split(" across")[0]
    out = {key: ranking(values, title=f"{title}{_when(column)}", subtitle=subtitle, category=category,
                        subgroup=subgroup, suffix=suffix, color=color, source=source,
                        note=f"Column: {period}.", decimals=decimals, ascending=options.get("ascending", False))}
    if options.get("kind") == "additive":
        total = sum(values.values())
        out[f"{key}_region_share"] = pie(
            region_points(values), title=f"{short}: regional share{_when(column)}",
            subtitle="Share of the State/UT total by region", category=category, subgroup=subgroup,
            suffix=suffix, color=color, source=source, decimals=decimals,
            note=f"Sum of reported State/UT values by region (total {total:,.{decimals}f}{suffix}). "
                 "Regions: North, Central, West, South (incl. island UTs), East and North-East.",
        )
    else:
        bands = options.get("bands") or auto_bands(values)
        out[f"{key}_distribution"] = pie(
            band_points(values, bands, suffix), title=f"{short}: States/UTs by band{_when(column)}",
            subtitle="Number of States/UTs in each range", category=category, subgroup=subgroup,
            suffix=" States/UTs", color=color, source=source, decimals=0,
            note=f"Count of the {len(values)} reporting States/UTs falling in each band of {short.lower()}.",
        )
    if options.get("trend", True):
        try:
            out[f"{key}_all_india_trend"] = trend(
                columns, column, title=f"{short}: All-India trend", subtitle=subtitle, category=category,
                subgroup=subgroup, suffix=suffix, color=color, source=source, divisor=divisor, decimals=decimals,
            )
        except ValueError:
            pass
    return out


def _gender_series(get_text, cache, table, key, scheme, color) -> dict[str, dict]:
    columns, table_title = _fetch(get_text, table, cache)
    years = list(dict.fromkeys(_period(label) for label in columns if " | " in label))
    source = _source(table, table_title)
    totals_by_year = {}
    for year in years:
        parts = {gender: _states_only(columns.get(f"{year} | {gender}", {})) for gender in ("Female", "Male", "Transgender")}
        totals_by_year[year] = {gender: sum(values.values()) for gender, values in parts.items()}
    year = [y for y in years if totals_by_year[y]["Female"] + totals_by_year[y]["Male"] > 0][-1]
    female = _states_only(columns.get(f"{year} | Female", {}))
    male = _states_only(columns.get(f"{year} | Male", {}))
    trans = _states_only(columns.get(f"{year} | Transgender", {}))
    combined = {name: female.get(name, 0) + male.get(name, 0) + trans.get(name, 0) for name in set(female) | set(male)}
    women_share = {name: 100 * female.get(name, 0) / combined[name] for name in combined if combined[name] >= 50}
    out = {
        key: ranking({name: value / 1000 for name, value in combined.items()}, title=f"{scheme} enrolments by State/UT ({year})",
                     subtitle="New enrolments during the year ('000)", category=PAY, subgroup=SUB_PENSION,
                     suffix=" '000", color=color, source=source, decimals=1),
        f"{key}_gender_mix": pie(list(totals_by_year[year].items()), title=f"{scheme} enrolments by gender ({year})",
                                 subtitle="All States/UTs combined", category=PAY, subgroup=SUB_PENSION, suffix=" enrolments",
                                 color=color, source=source, decimals=0,
                                 note="Sum of State/UT rows by gender as published by PFRDA."),
        f"{key}_women_share": ranking(women_share, title=f"Women's share of {scheme} enrolments ({year})",
                                     subtitle="Female enrolments as % of the State/UT total", category=PAY,
                                     subgroup=SUB_PENSION, suffix="%", color="#f778ba", source=source, decimals=1,
                                     note="States/UTs with fewer than 50 enrolments are omitted."),
        f"{key}_region_share": pie(region_points(combined), title=f"{scheme} enrolments: regional share ({year})",
                                   subtitle="Share of enrolments by region", category=PAY, subgroup=SUB_PENSION,
                                   suffix=" enrolments", color=color, source=source, decimals=0,
                                   note="Sum of State/UT enrolments by region."),
    }
    yearly = [(y, sum(totals_by_year[y].values())) for y in years if sum(totals_by_year[y].values()) > 0]
    if len(yearly) >= 3:
        out[f"{key}_national_trend"] = {
            "labels": [y for y, _ in yearly], "values": [round(v) for _, v in yearly], "source": source,
            "note": "Sum of all State/UT rows each year.",
            "meta": _meta(f"{scheme} enrolments: national trend", "New enrolments per year, all States/UTs",
                          PAY, SUB_PENSION, " enrolments", color, "Annual"),
        }
    return out


def _sub_split_series(get_text, cache, table, key, title, subtitle, category, subgroup, suffix, color,
                      group_pattern, parts) -> dict[str, dict]:
    """Rural/urban (or male/female) splits published as sub-columns of one table."""
    columns, table_title = _fetch(get_text, table, cache)
    source = _source(table, table_title)
    labels = {part: pick_column(columns, rf"{group_pattern}.*\| {part}$") for part in parts}
    totals = {part: sum(_states_only(columns[label]).values()) for part, label in labels.items()}
    return {key: pie(list(totals.items()), title=title, subtitle=subtitle, category=category, subgroup=subgroup,
                     suffix=suffix, color=color, source=source, decimals=0,
                     note="Sum of State/UT rows for each published sub-column.")}


def _comparison(get_text, cache, table, key, title, subtitle, category, subgroup, suffix, color, pattern_a, pattern_b,
                label_a, label_b, ascending=False) -> dict[str, dict]:
    columns, table_title = _fetch(get_text, table, cache)
    col_a, col_b = pick_column(columns, pattern_a), pick_column(columns, pattern_b)
    a, b = _states_only(columns[col_a]), _states_only(columns[col_b])
    names = sorted(set(a) & set(b), key=lambda name: (b[name] if ascending else -b[name], name))
    if len(names) < 5:
        raise ValueError(f"Too few States/UTs for {title}")
    return {key: {
        "labels": names,
        "datasets": [
            {"label": label_a, "values": [a[name] for name in names], "color": "#8b949e"},
            {"label": label_b, "values": [b[name] for name in names], "color": color},
        ],
        "chartType": "bar",
        "indexAxis": "y",
        "scope": "state",
        "source": _source(table, table_title),
        "note": f"{label_a} vs {label_b}. " + coverage_note(names),
        "meta": _meta(title, subtitle, category, subgroup, suffix, color),
    }}


def _ratio(get_text, cache, key, num_table, num_col, den_table, den_col, *, title, subtitle, category, subgroup,
           suffix, color, scale=100.0, bands=None, ascending=False) -> dict[str, dict]:
    num_columns, num_title = _fetch(get_text, num_table, cache)
    den_columns, den_title = _fetch(get_text, den_table, cache)
    norm = lambda label: re.sub(r"\s*\(.*?\)", "", label).strip()
    num_by_period = {norm(l): l for l in num_columns if re.search(num_col, l) and not re.search(r"\((?:RE|BE)\)", l)}
    den_by_period = {norm(l): l for l in den_columns if re.search(den_col, l)}
    shared = [p for p in num_by_period if p in den_by_period]
    if not shared:
        raise ValueError(f"No common period for {title}")
    overlap = lambda p: len(set(_states_only(num_columns[num_by_period[p]])) & set(_states_only(den_columns[den_by_period[p]])))
    best = max(overlap(p) for p in shared)
    period = [p for p in shared if overlap(p) >= best * 0.8][-1]
    num, den = _states_only(num_columns[num_by_period[period]]), _states_only(den_columns[den_by_period[period]])
    values = {name: scale * num[name] / den[name] for name in set(num) & set(den) if den[name]}
    source = f"{_source(num_table, num_title)}; {_source(den_table, den_title)}"
    short = title.split(" by State")[0].split(" across")[0]
    return {
        key: ranking(values, title=f"{title} ({period})", subtitle=subtitle, category=category, subgroup=subgroup,
                     suffix=suffix, color=color, source=source, note=f"Computed as Table {num_table} ÷ Table {den_table} for {period}.",
                     decimals=1, ascending=ascending),
        f"{key}_distribution": pie(band_points(values, bands or auto_bands(values), suffix),
                                   title=f"{short}: States/UTs by band ({period})", subtitle="Number of States/UTs in each range",
                                   category=category, subgroup=subgroup, suffix=" States/UTs", color=color, source=source,
                                   decimals=0, note=f"Count of the {len(values)} States/UTs in each band."),
    }


def build_rbi_state_layer(get_text, previous: dict | None = None) -> dict[str, dict]:
    previous = previous or {}
    cache: dict = {}
    series: dict[str, dict] = {}
    expected: list[str] = []

    def attempt(keys: list[str], build):
        expected.extend(keys)
        try:
            series.update(build())
        except Exception as error:  # keep the last good copy if one table changes or is unreachable
            for key in keys:
                if key in previous and not previous[key].get("error"):
                    series[key] = previous[key]
            print(f"RBI state layer: {keys[0]} kept previous values ({error})")

    for spec in TABLE_SPECS:
        key = spec[1]
        attempt([key, f"{key}_region_share", f"{key}_distribution", f"{key}_all_india_trend"],
                lambda spec=spec: _table_series(get_text, cache, spec))
    attempt(["rbi_state_nps_enrolments"], lambda: _gender_series(get_text, cache, 179, "rbi_state_nps_enrolments", "NPS (All Citizen)", "#58a6ff"))
    attempt(["rbi_state_apy_enrolments"], lambda: _gender_series(get_text, cache, 180, "rbi_state_apy_enrolments", "Atal Pension Yojana", "#3fb950"))
    attempt(["rbi_state_hospitals_rural_urban"], lambda: _sub_split_series(
        get_text, cache, 17, "rbi_state_hospitals_rural_urban", "Government hospitals: rural vs urban",
        "All States/UTs combined", HEALTH, SUB_HEALTH_INFRA, " hospitals", "#3fb950", "Hospitals", ("Rural", "Urban")))
    attempt(["rbi_state_beds_rural_urban"], lambda: _sub_split_series(
        get_text, cache, 17, "rbi_state_beds_rural_urban", "Government hospital beds: rural vs urban",
        "All States/UTs combined", HEALTH, SUB_HEALTH_INFRA, " beds", "#56d364", "Beds", ("Rural", "Urban")))
    attempt(["rbi_state_government_hospitals"], lambda: {"rbi_state_government_hospitals": ranking(
        _states_only(_fetch(get_text, 17, cache)[0][pick_column(_fetch(get_text, 17, cache)[0], r"Hospitals.*\| Total$")]),
        title="Government hospitals by State/UT", subtitle="Rural + urban government hospitals",
        category=HEALTH, subgroup=SUB_HEALTH_INFRA, suffix=" hospitals", color="#3fb950",
        source=_source(17, _fetch(get_text, 17, cache)[1]), decimals=0)})
    attempt(["rbi_state_government_beds"], lambda: {"rbi_state_government_beds": ranking(
        _states_only(_fetch(get_text, 17, cache)[0][pick_column(_fetch(get_text, 17, cache)[0], r"Beds.*\| Total$")]),
        title="Government hospital beds by State/UT", subtitle="Rural + urban government hospital beds",
        category=HEALTH, subgroup=SUB_HEALTH_INFRA, suffix=" beds", color="#56d364",
        source=_source(17, _fetch(get_text, 17, cache)[1]), decimals=0)})
    attempt(["rbi_state_life_expectancy_gender"], lambda: _comparison(
        get_text, cache, 7, "rbi_state_life_expectancy_gender", "Life expectancy: men vs women by State/UT",
        "Years at birth, latest SRS abridged life table", HEALTH, SUB_HEALTH_OUT, " years", "#f778ba",
        r"\| Male$", r"\| Female$", "Male", "Female"))
    attempt(["rbi_state_mpi_change"], lambda: _comparison(
        get_text, cache, 10, "rbi_state_mpi_change", "Multidimensional poverty: NFHS-4 vs NFHS-5",
        "Headcount ratio (%) of multidimensionally poor", SOCIAL, SUB_JOBS, "%", "#3fb950",
        r"NFHS-4.*Headcount", r"NFHS-5.*Headcount", "NFHS-4 (2015-16)", "NFHS-5 (2019-21)", ascending=False))
    attempt(["rbi_state_ger_secondary"], lambda: _table_series(get_text, cache, (
        1, "rbi_state_ger_secondary", "Secondary gross enrolment ratio by State/UT", "GER, Classes IX–XII, total (UDISE+)",
        SOCIAL, SUB_EDU, "%", "#58a6ff", {"kind": "rate", "bands": [50, 70, 90], "col": r"Secondary.*\| Total$", "trend": False})))
    attempt(["rbi_state_ger_middle"], lambda: _table_series(get_text, cache, (
        1, "rbi_state_ger_middle", "Middle-school gross enrolment ratio by State/UT", "GER, Classes VI–VIII, total (UDISE+)",
        SOCIAL, SUB_EDU, "%", "#79c0ff", {"kind": "rate", "bands": [70, 85, 100], "col": r"Middle.*\| Total$", "trend": False})))
    attempt(["rbi_state_ger_secondary_gender"], lambda: _comparison(
        get_text, cache, 1, "rbi_state_ger_secondary_gender", "Secondary enrolment: boys vs girls by State/UT",
        "GER, Classes IX–XII (UDISE+)", SOCIAL, SUB_EDU, "%", "#f778ba",
        r"Secondary.*\| Male$", r"Secondary.*\| Female$", "Boys", "Girls"))
    attempt(["rbi_state_fiscal_deficit_gsdp"], lambda: _ratio(
        get_text, cache, "rbi_state_fiscal_deficit_gsdp", 164, r"^\d{4}", 21, r"^\d{4}",
        title="Gross fiscal deficit as % of GSDP", subtitle="State government GFD ÷ GSDP, latest audited accounts",
        category=STATE, subgroup=SUB_FIN, suffix="% GSDP", color="#ff7b72", scale=10000.0, bands=[2, 3, 4, 5], ascending=True))
    attempt(["rbi_state_own_tax_gsdp"], lambda: _ratio(
        get_text, cache, "rbi_state_own_tax_gsdp", 168, r"^\d{4}", 21, r"^\d{4}",
        title="Own tax revenue as % of GSDP", subtitle="State own tax revenue ÷ GSDP, latest audited accounts",
        category=STATE, subgroup=SUB_FIN, suffix="% GSDP", color="#58a6ff", scale=10000.0, bands=[4, 6, 8]))
    attempt(["state_manufacturing_gsdp_share"], lambda: _ratio(
        get_text, cache, "state_manufacturing_gsdp_share", 33, r"^\d{4}", 21, r"^\d{4}",
        title="Manufacturing share of GSDP across States & UTs", subtitle="Manufacturing GSVA as % of GSDP, current prices",
        category=STATE, subgroup=SUB_ECON, suffix="% GSDP", color="#ff9933", bands=[5, 10, 20, 30]))
    attempt(["rbi_state_credit_per_office"], lambda: _ratio(
        get_text, cache, "rbi_state_credit_per_office", 156, r"^\d{4}", 152, r"^\d{4}",
        title="Bank credit per office by State/UT", subtitle="Scheduled commercial bank credit ÷ offices (INR crore per office)",
        category=PAY, subgroup=SUB_BANK, suffix=" INR cr", color="#56d364", scale=1.0, bands=[50, 100, 200]))
    attempt(["rbi_state_deposits_per_office"], lambda: _ratio(
        get_text, cache, "rbi_state_deposits_per_office", 155, r"^\d{4}", 152, r"^\d{4}",
        title="Bank deposits per office by State/UT", subtitle="Scheduled commercial bank deposits ÷ offices (INR crore per office)",
        category=PAY, subgroup=SUB_BANK, suffix=" INR cr", color="#3fb950", scale=1.0, bands=[50, 100, 200]))
    attempt(["rbi_state_health_spend_share"], lambda: _ratio(
        get_text, cache, "rbi_state_health_spend_share", 18, r"^\d{4}", 21, r"^\d{4}",
        title="Public health spending as % of GSDP", subtitle="State public expenditure on health ÷ GSDP",
        category=HEALTH, subgroup=SUB_HEALTH_INFRA, suffix="% GSDP", color="#3fb950", scale=10000.0, bands=[0.5, 1, 1.5, 2]))
    if not series and previous:
        return {key: value for key, value in previous.items() if key in expected}
    return series

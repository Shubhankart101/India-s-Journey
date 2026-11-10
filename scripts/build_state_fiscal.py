"""Build data/state_fiscal.json: state fiscal matrix, head-to-head and spending-by-function data.

Sources: RBI Handbook of Statistics on Indian States 2024-25 (time series) and
RBI 'State Finances: A Study of Budgets 2025-26' (debt ratio, Appendix II functional spending).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rbi_state_layer import _Rows, canonical_state, parse_rbi_table  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE = os.path.join(ROOT, "data", "raw_fiscal", "rbi")
OUT = os.path.join(ROOT, "data", "state_fiscal.json")
URL = "https://www.rbi.org.in/Scripts/PublicationsView.aspx?id={}"
HSI = "RBI Handbook of Statistics on Indian States 2024-25"
SFSB = "RBI State Finances: A Study of Budgets 2025-26"
HSI_ID = lambda n: 23449 + n  # noqa: E731
YEARS = [f"{y}-{str(y + 1)[2:]}" for y in range(2012, 2024)]


def rows_of(pid):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"p{pid}.html")
    if not os.path.exists(path) or os.path.getsize(path) <= 3000:
        last_error = "no valid cached RBI page"
        for attempt in range(3):
            try:
                request = Request(URL.format(pid), headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(request, timeout=60) as response:
                    payload = response.read()
                if len(payload) <= 3000 or b"<html" not in payload[:2000].lower():
                    raise ValueError("RBI response was empty or not an HTML page")
                with open(path, "wb") as handle:
                    handle.write(payload)
                break
            except Exception as error:
                last_error = str(error)
                if attempt < 2:
                    time.sleep(1)
        else:
            raise RuntimeError(f"Unable to retrieve RBI table {pid}: {last_error}")
    parser = _Rows()
    with open(path, encoding="utf-8", errors="replace") as handle:
        parser.feed(handle.read())
    if not parser.rows:
        raise ValueError(f"RBI table {pid} contained no parseable rows")
    return parser.rows


def hsi_table(n):
    """{year: {state: value}} for a Handbook table whose columns are years."""
    out = {}
    for col, states in parse_rbi_table(rows_of(HSI_ID(n))).items():
        m = re.match(r"(\d{4}-\d{2})", col)
        if m:
            out[m.group(1)] = {canonical_state(s): v for s, v in states.items() if canonical_state(s)}
    return out


def number(text):
    text = str(text).replace(",", "").strip()
    return float(text) if re.fullmatch(r"-?\d+(\.\d+)?", text) else None


def statement_state(name):
    return canonical_state(re.sub(r"^\d+\.\s*", "", name).strip())


def statement20():
    rows = rows_of(23729)
    head = next(r for r in rows if r and r[0] == "State/UT")
    cols = []
    for label in head[1:]:
        y = int(label[:4])
        cols.append(f"{y - 1}-{str(y)[2:]}")  # liabilities at end-March y close financial year y-1
    out = {}
    for r in rows:
        st = statement_state(r[0]) if r and re.match(r"^\d+\.", r[0]) else None
        if st:
            for y, v in zip(cols, r[1:]):
                if number(v) is not None:
                    out.setdefault(y, {})[st] = number(v)
    return out


FUNCTIONS = [
    ("Education", r"^1\. Education"),
    ("Health & family welfare", None),
    ("Water supply & sanitation", r"^4\. Water Supply"),
    ("Housing & urban development", None),
    ("SC/ST/OBC welfare", r"^7\. Welfare of Scheduled"),
    ("Social security & nutrition", None),
    ("Agriculture & allied", r"^1\. Agriculture and Allied"),
    ("Rural development", r"^2\. Rural Development"),
    ("Irrigation & flood control", r"^4\. Irrigation"),
    ("Energy", r"^5\. Energy"),
    ("Transport", r"^7\. Transport"),
    ("Police", r"^iii\) Police"),
    ("Interest payments", r"^2\. Interest Payments"),
]
FUNC_YEARS = {0: "2023-24", 2: "2024-25", 3: "2025-26"}  # 2024-25 uses Revised Estimates
SEARCH = {
    "Health & family welfare": [r"^2\. Medical and Public Health", r"^3\. Family Welfare"],
    "Housing & urban development": [r"^5\. Housing", r"^6\. Urban Development"],
    "Social security & nutrition": [r"^9\. Social Security", r"^10\. Nutrition"],
}


ALL_PATS = [p for _, p in FUNCTIONS if p] + [p for pats in SEARCH.values() for p in pats]


def functional_spending():
    result = {y: {} for y in FUNC_YEARS.values()}
    for pid in range(23755, 23763):
        rows = rows_of(pid)
        states, block = [], {}

        def flush():
            for i, st in enumerate(states):
                cs = canonical_state(st.title().replace(" And ", " and ").replace("&", "&"))
                if cs == "__ALL_INDIA__":
                    cs = "All States & UTs"
                if not cs or "TOTAL" not in block:
                    continue
                for off, year in FUNC_YEARS.items():
                    total = block["TOTAL"][i * 4 + off] if i * 4 + off < len(block["TOTAL"]) else None
                    if not total:
                        continue
                    shares = {}
                    for name, pat in FUNCTIONS:
                        pats = SEARCH.get(name) or [pat]
                        vals = [block.get(p, [None] * 16)[i * 4 + off] for p in pats]
                        vals = [v or 0.0 for v in vals]
                        shares[name] = round(100 * sum(vals) / total, 2)
                    result[year][cs] = shares

        for r in rows:
            if not r:
                continue
            if r[0] == "Item" and len(r) > 1:
                if r[1:] != states:
                    if states and block:
                        flush()
                    states, block = r[1:], {}
                continue
            if states and len(r) >= 1 + 4 * len(states):
                vals = [number(v) for v in r[1:]]
                keys = ["TOTAL"] if r[0].startswith("TOTAL EXPENDITURE") else ALL_PATS
                for k in keys:
                    if (k == "TOTAL" or re.match(k, r[0])) and k not in block:
                        block[k] = vals
        if states and block:
            flush()
    return result


def main():
    gfd, rd, rexp = hsi_table(164), hsi_table(165), hsi_table(166)
    otr, ontr, ip, pen = hsi_table(168), hsi_table(169), hsi_table(170), hsi_table(171)
    outlay, gsdp, gsdp_k, pcnsdp = hsi_table(174), hsi_table(21), hsi_table(22), hsi_table(19)
    debt = statement20()
    gsdp_rows = rows_of(HSI_ID(21))
    assert any("Lakh" in c for r in gsdp_rows[:8] for c in r), "unexpected GSDP unit"

    metrics = {}

    def put(key, label, unit, better, table_src, url, note, values):
        metrics[key] = {"label": label, "unit": unit, "better": better, "source": table_src, "source_url": url, "note": note, "values": values}

    def ratio(num, den, scale=100.0, minus=None):
        out = {}
        for y in YEARS:
            for s, n in num.get(y, {}).items():
                d = den.get(y, {}).get(s)
                if d:
                    out.setdefault(s, {})[y] = round(scale * n / d, 2)
        return out

    gsdp_cr = {y: {s: v / 100 for s, v in d.items()} for y, d in gsdp.items()}  # lakh -> crore
    rr = {y: {s: rexp[y][s] - rd[y][s] for s in rexp[y] if s in rd.get(y, {})} for y in rexp}
    transfers = {y: {s: rr[y][s] - otr[y][s] - ontr[y][s] for s in rr[y] if s in otr.get(y, {}) and s in ontr.get(y, {})} for y in rr}
    committed = {y: {s: ip[y][s] + pen[y][s] for s in ip[y] if s in pen.get(y, {})} for y in ip}

    def by_state(table):
        out = {}
        for y in YEARS:
            for s, v in table.get(y, {}).items():
                out.setdefault(s, {})[y] = round(v, 2)
        return out

    note_year = "Years are financial years; 2023-24 values are Revised Estimates in the RBI Handbook. "
    put("gfd_gsdp", "Fiscal deficit", "% of GSDP", "low", f"{HSI}, Tables 164 and 21", URL.format(HSI_ID(164)),
        note_year + "Gross fiscal deficit divided by GSDP at current prices.", ratio(gfd, gsdp_cr))
    put("rd_gsdp", "Revenue deficit (+) / surplus (-)", "% of GSDP", "low", f"{HSI}, Tables 165 and 21", URL.format(HSI_ID(165)),
        note_year + "Revenue deficit divided by GSDP at current prices.", ratio(rd, gsdp_cr))
    put("debt_gsdp", "Debt (outstanding liabilities)", "% of GSDP", "low", f"{SFSB}, Statement 20", URL.format(23729),
        "Outstanding liabilities at end-March as per cent of GSDP, reported as at the close of the financial year shown.", by_state(debt))
    put("interest_rr", "Interest payments", "% of revenue receipts", "low", f"{HSI}, Tables 170, 166 and 165", URL.format(HSI_ID(170)),
        note_year + "Revenue receipts derived as revenue expenditure minus revenue deficit.", ratio(ip, rr))
    put("own_tax_rr", "Own tax revenue", "% of revenue receipts", "high", f"{HSI}, Tables 168, 166 and 165", URL.format(HSI_ID(168)),
        note_year + "Revenue receipts derived as revenue expenditure minus revenue deficit.", ratio(otr, rr))
    put("transfers_rr", "Central transfers", "% of revenue receipts", None, f"{HSI}, Tables 166, 165, 168 and 169", URL.format(HSI_ID(166)),
        note_year + "Central transfers = revenue receipts minus own tax and own non-tax revenue (shared taxes plus grants).", ratio(transfers, rr))
    put("committed_rr", "Committed expenditure (interest + pensions)", "% of revenue receipts", "low", f"{HSI}, Tables 170, 171, 166 and 165", URL.format(HSI_ID(170)),
        note_year + "Interest payments plus pension payments; salaries are excluded so this is a floor.", ratio(committed, rr))
    put("capex_gsdp", "Capital outlay", "% of GSDP", "high", f"{HSI}, Tables 174 and 21", URL.format(HSI_ID(174)),
        note_year + "Capital outlay divided by GSDP at current prices.", ratio(outlay, gsdp_cr))
    growth = {}
    ys = sorted(gsdp_k)
    for a, b in zip(ys, ys[1:]):
        if b in YEARS:
            for s, v in gsdp_k[b].items():
                p = gsdp_k[a].get(s)
                if p:
                    growth.setdefault(s, {})[b] = round(100 * (v / p - 1), 2)
    put("gsdp_growth", "GSDP growth (real)", "% y/y", "high", f"{HSI}, Table 22", URL.format(HSI_ID(22)),
        "Year-on-year growth of GSDP at constant prices (2011-12 base).", growth)
    put("gsdp", "GSDP (current prices)", "₹ lakh crore", None, f"{HSI}, Table 21", URL.format(HSI_ID(21)),
        "Gross State Domestic Product at current prices; Handbook reports ₹ lakh, converted to ₹ lakh crore.",
        {s: {y: round(v / 1e7, 3) for y, v in d.items()} for s, d in by_state({y: gsdp[y] for y in gsdp}).items()})
    put("pcnsdp", "Per-capita NSDP", "₹", None, f"{HSI}, Table 19", URL.format(HSI_ID(19)),
        "Net State Domestic Product per person at current prices.", by_state(pcnsdp))

    states = sorted({s for m in metrics.values() for s in m["values"]})
    func = functional_spending()
    categories = [n for n, _ in FUNCTIONS]
    for y in list(func):
        if not func[y]:
            del func[y]
    out = {
        "years": YEARS, "states": states, "metrics": metrics,
        "functions": {
            "categories": categories, "values": func,
            "unit": "% of revenue expenditure",
            "source": f"{SFSB}, Appendix II (Revenue Expenditure of States and UTs with Legislature)",
            "source_url": URL.format(23755),
            "note": "Share of each function in revenue expenditure; 2023-24 are Accounts, 2024-25 Revised Estimates and 2025-26 Budget Estimates. Police is reported under general services.",
        },
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(states), "states;", {k: len(v["values"]) for k, v in metrics.items()}, {y: len(v) for y, v in func.items()})


if __name__ == "__main__":
    main()

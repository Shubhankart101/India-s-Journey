"""Build data/borrowing.json ('How India Borrows') from RBI Handbook of Statistics on the Indian Economy 2024-25.

Every table is fetched from the RBI publication page and parsed; each series records its source_url.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rbi_state_layer import _Rows  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE = os.path.join(ROOT, "data", "raw_fiscal", "rbi")
OUT = os.path.join(ROOT, "data", "borrowing.json")
HBS = "Handbook of Statistics on the Indian Economy 2024-25 (RBI)"
URL = "https://www.rbi.org.in/Scripts/PublicationsView.aspx?id={}"
TABLES = {105: 23279, 106: 23280, 107: 23281, 109: 23283, 110: 23284, 113: 23287, 149: 23323, 239: 23413}


def fetch(pid):
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


def num(text):
    text = str(text).replace(",", "").strip()
    return float(text) if re.fullmatch(r"-?\d+(\.\d+)?", text) else None


def fy(label):
    return label if re.fullmatch(r"\d{4}-\d{2}", label) else None


def end_march(label):
    """'2025' (as on 31 March 2025) -> financial year '2024-25'."""
    if re.fullmatch(r"\d{4}", label):
        y = int(label)
        return f"{y - 1}-{str(y)[2:]}"
    return None


def year_table(rows, columns, first="2004-05"):
    out = {name: {} for name in columns.values()}
    for row in rows:
        year = fy(row[0]) if row else None
        if not year or year < first:
            continue
        for idx, name in columns.items():
            if idx < len(row) and (v := num(row[idx])) is not None:
                out[name][year] = v
    return out


def main():
    t = {n: fetch(pid) for n, pid in TABLES.items()}
    series = {}

    def add(key, title, unit, data, table, note=""):
        data = {k: v for k, v in data.items() if v is not None}
        if data:
            series[key] = {"title": title, "unit": unit, "values": dict(sorted(data.items())),
                           "source": f"{HBS}, Table {table}", "source_url": URL.format(TABLES[table]), "note": note}

    m = year_table(t[105], {1: "centre_gross", 2: "centre_net", 3: "states_gross", 4: "states_net", 5: "comb_gross", 6: "comb_net"})
    for k, title in {"centre_gross": "Centre: gross market borrowings", "centre_net": "Centre: net market borrowings",
                     "states_gross": "States: gross market borrowings", "states_net": "States: net market borrowings",
                     "comb_gross": "Centre + States: gross market borrowings", "comb_net": "Centre + States: net market borrowings"}.items():
        add(f"mb_{k}", title, "₹ crore", m[k], 105)

    r = year_table(t[106], {})
    wa = {}
    for row in t[106]:
        year = fy(row[0]) if row else None
        if year and year >= "2004-05" and len(row) >= 5:
            wa[year] = (num(row[2]), num(row[4]))
    add("wa_centre", "Weighted average interest rate: Central dated securities (issued in year)", "%", {k: v[0] for k, v in wa.items()}, 106)
    add("wa_states", "Weighted average interest rate: State dated securities (issued in year)", "%", {k: v[1] for k, v in wa.items()}, 106)

    l = year_table(t[107],     {1: "internal_debt", 2: "market_loans", 3: "tb91", 4: "tb_182_364", 5: "small_savings", 6: "other_accounts",
                                7: "reserve_funds", 8: "total_internal", 9: "external", 10: "total"}, "2004-05")
    tb = {y: (l["tb91"].get(y, 0) + l["tb_182_364"].get(y, 0)) for y in l["tb91"] if y in l["tb_182_364"]}
    note = "Revised Estimates for 2024-25 and Budget Estimates for 2025-26."
    add("liab_market_loans", "Central liabilities: dated securities (market loans)", "₹ crore", l["market_loans"], 107, note)
    add("liab_tbills", "Central liabilities: Treasury Bills (91-day + 182/364-day)", "₹ crore", tb, 107, note)
    add("liab_small_savings", "Central liabilities: small savings, deposits & provident funds", "₹ crore", l["small_savings"], 107, note)
    add("liab_total", "Central government total liabilities", "₹ crore", l["total"], 107, note)

    c = year_table(t[109], {3: "centre", 4: "states", 6: "combined"})
    add("liab_combined", "Combined liabilities of Centre and States", "₹ crore", c["combined"], 109,
        "Revised Estimates 2023-24 and Budget Estimates 2024-25 as flagged by RBI.")

    d = year_table(t[239], {3: "centre", 4: "states", 6: "combined"}, "1990-91")
    add("debt_gdp_centre", "Central government liabilities as % of GDP", "% of GDP", d["centre"], 239, "RBI estimates; latest two years are RE/BE.")
    add("debt_gdp_states", "State government liabilities as % of GDP", "% of GDP", d["states"], 239, "RBI estimates; latest two years are RE/BE.")
    add("debt_gdp_general", "General government (Centre + States) liabilities as % of GDP", "% of GDP", d["combined"], 239, "RBI estimates; latest two years are RE/BE.")

    mat = {"under5": {}, "five10": {}, "over10": {}}
    for row in t[113]:
        year = end_march(row[0]) if row else None
        if year and year >= "2004-05" and len(row) >= 6:
            for key, idx in (("under5", 1), ("five10", 2), ("over10", 3)):
                mat[key][year] = num(row[idx])
    add("mat_under5", "Outstanding rupee loans maturing in under 5 years", "₹ crore", mat["under5"], 113, "Excludes special securities and compensation bonds.")
    add("mat_five10", "Outstanding rupee loans maturing in 5-10 years", "₹ crore", mat["five10"], 113, "Excludes special securities and compensation bonds.")
    add("mat_over10", "Outstanding rupee loans maturing in over 10 years", "₹ crore", mat["over10"], 113, "Excludes special securities and compensation bonds.")

    ext = {"long": {}, "short": {}, "total": {}}
    cols = None
    for row in t[149]:
        if row and row[0] == "Item":
            cols = [end_march(x) for x in row[1:]]
            continue
        if not cols or not row:
            continue
        label = row[0].lower()
        key = "long" if label.startswith("viii") else "short" if label.startswith("ix.") or label.startswith("ix ") else "total" if label.startswith("x.") or label.startswith("x ") else None
        if key:
            for year, v in zip(cols, row[1:]):
                if year and num(v) is not None:
                    ext[key][year] = num(v)
    add("ext_long", "External debt: long-term (end-March)", "₹ crore", ext["long"], 149)
    add("ext_short", "External debt: short-term (end-March)", "₹ crore", ext["short"], 149)
    add("ext_total", "India's total external debt (end-March)", "₹ crore", ext["total"], 149)

    holders = {}
    section = None
    for row in t[110]:
        if row and row[0].startswith(("(A)", "(B)", "(C)")):
            section = {"(A)": "gsec", "(B)": "sdl", "(C)": "tbill"}[row[0][:3]]
            holders[section] = {"Total": dict(zip(("2022-23", "2023-24", "2024-25"), map(num, row[1:4])))}
            continue
        mm = re.match(r"^(\d+)\s+(.*)$", row[0]) if row else None
        if section and mm and "." not in mm.group(1) and len(row) >= 4:
            holders[section][mm.group(2)] = dict(zip(("2022-23", "2023-24", "2024-25"), map(num, row[1:4])))
    series["holders"] = {"title": "Ownership of government securities (outstanding as on 31 March)", "unit": "₹ crore", "values": holders,
                         "source": f"{HBS}, Table 110", "source_url": URL.format(TABLES[110]),
                         "note": "gsec = Central dated securities; sdl = State government securities; tbill = Treasury Bills. 'Others' includes State governments."}

    json.dump({"source": HBS, "series": series}, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for k, v in series.items():
        vals = v["values"]
        ks = list(vals)
        print(k, len(vals), ks[0], ks[-1])


if __name__ == "__main__":
    main()

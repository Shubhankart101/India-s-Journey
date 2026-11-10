"""Build data/union_budget.json from the Budget-at-a-Glance PDFs (see union_budget_parse.py).

Usage:  python scripts/build_union_budget.py [--fetch]
Every value keeps its basis (Actual / RE / BE) and the BaG document it was read from.
"""
import json
import os
import sys

import union_budget_parse as u

OUT = os.path.join(u.ROOT, "data", "union_budget.json")

# key -> (label regex variants, kwargs). All values are Rs crore unless noted.
ITEMS = {
    "revenue_receipts": ([r"Revenue Receipts", r"Total\s*-?\s*Revenue"], {}),
    "net_tax_revenue": ([r"Tax Revenue \(Net", r"Centre.?s Net Tax", r"Net Tax Revenue"], {}),
    "non_tax_revenue": ([r"Non[\s-]*Tax Revenue"], {}),
    "total_expenditure": ([r"Total Expenditure(?=\s*\(|\s*\d)", r"Total Expenditure"], {}),
    "revenue_expenditure": ([r"On Revenue Account"], {}),
    "interest_payments": ([r"Interest Payments"], {}),
    "capital_expenditure": ([r"On Capital Account\s*\(11\+15\)", r"On Capital Account"], {}),
    "fiscal_deficit": ([r"Fiscal Deficit"], {}),
    "revenue_deficit": ([r"Revenue Deficit"], {}),
    "primary_deficit": ([r"Primary Deficit"], {}),
    # Receipts (BaG receipts part)
    "corporation_tax": ([r"Corporation Tax"], {}),
    "income_tax": ([r"Taxes on Income", r"Income Tax"], {}),
    "customs": ([r"Customs"], {}),
    "union_excise": ([r"Union Excise"], {}),
    "gross_tax_revenue": ([r"Gross Tax Revenue"], {}),
    "states_share_taxes": ([r"Less\s*-?\s*States?.?s share"], {}),
    # Transfers to States (3 columns: Actuals, RE, BE)
    "total_transfers_states": ([r"Total Transfer to States/UTs"], {"ncols": 3}),
    # Financing of the fiscal deficit
}
PCT_ITEMS = ("fiscal_deficit", "revenue_deficit", "primary_deficit")
# The BaG 2019-20 summary table is image-only, so 2017-18 Actuals are not machine-readable; use RE for every item.
NO_ACTUALS = {"2017-18"}
TYPE_KEYS = {
    "type_establishment": "establishment",
    "type_central_sector": "central_sector",
    "type_other_central_sector": "other_central_sector",
    "type_centrally_sponsored": "centrally_sponsored",
    "type_finance_commission": "finance_commission_grants",
    "type_other_transfers": "other_grants_transfers",
}


class Bag:
    def __init__(self, year):
        self.year = year
        self.lines = u.layout_lines(year)
        self.cache = {}
        self.types = None

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        if key in TYPE_KEYS:
            if self.types is None:
                self.types = u.expenditure_types(self.lines)
            v = self.types.get(TYPE_KEYS[key])
            self.cache[key] = (v, None) if v and any(x is not None for x in v) else (None, None)
            return self.cache[key]
        variants, kw = ITEMS[key]
        res = (None, None)
        for pat in variants:
            v, idx = u.find_row(self.lines, pat, **kw)
            if v:
                res = (v, u.find_pct(self.lines, idx) if key in PCT_ITEMS else None)
                break
        self.cache[key] = res
        return res


def plausible(a, ref):
    return ref is None or ref == 0 or 0.25 < abs(a) / abs(ref) < 4 or abs(a - ref) < 50


def resolve(bags, key, year, conflicts):
    y = int(year[:4])
    nm = lambda d: f"{y + d}-{str(y + d + 1)[2:]}"
    b0, b1, b2 = bags.get(year), bags.get(nm(1)), bags.get(nm(2))
    be_cands = []
    g1, g0 = (b1.get(key) if b1 else (None, None)), (b0.get(key) if b0 else (None, None))
    pick = lambda g, i: (g[0][i], g[1][i] if g[1] else None)
    if g1[0] and g1[0][1] is not None:
        be_cands.append(pick(g1, 1) + (nm(1),))
    if g0[0] and g0[0][3] is not None:
        be_cands.append(pick(g0, 3) + (year,))
    re_c = pick(g1, 2) + (nm(1),) if g1[0] and g1[0][2] is not None else None
    a_c = None
    if b2 and b2.get(key)[0] and b2.get(key)[0][0] is not None:
        a_c = pick(b2.get(key), 0) + (nm(2),)
    if len(be_cands) == 2 and be_cands[0][0] != be_cands[1][0]:
        conflicts.append((key, year, be_cands[0][0], be_cands[1][0]))
        ok = [c for c in be_cands if plausible(c[0], re_c[0] if re_c else None)]
        be_cands = ok or be_cands
    be = be_cands[0] if be_cands else None
    ref = (re_c or be or (None,))[0]
    if a_c and year not in NO_ACTUALS and plausible(a_c[0], ref):
        return "Actuals", a_c
    if re_c and plausible(re_c[0], be[0] if be else None):
        return "Revised Estimates", re_c
    if be:
        return "Budget Estimates", be
    return None, None


def main():
    if "--fetch" in sys.argv:
        u.fetch_all()
    bags = {y: Bag(y) for y in u.YEARS}
    conflicts = []
    items = {}
    for key in list(ITEMS) + list(TYPE_KEYS):
        series = {}
        for year in u.YEARS:
            basis, cand = resolve(bags, key, year, conflicts)
            if cand is None:
                continue
            rec = {"value": cand[0], "basis": basis, "source_url": u.source_url(cand[2])}
            if cand[1] is not None:
                rec["pct_gdp"] = cand[1]
            series[year] = rec
        items[key] = series
    for key in ("revenue_expenditure", "capital_expenditure", "net_tax_revenue"):
        parsed = items.pop(key, {})
        items[key] = {}
        for year in u.YEARS:
            rr, rd, te, nt = (items.get(k, {}).get(year) for k in ("revenue_receipts", "revenue_deficit", "total_expenditure", "non_tax_revenue"))
            if key == "revenue_expenditure" and rr and rd:
                val, src = rr["value"] + rd["value"], rd
            elif key == "capital_expenditure" and te and rr and rd:
                val, src = te["value"] - (rr["value"] + rd["value"]), rd
            elif key == "net_tax_revenue" and rr and nt:
                val, src = rr["value"] - nt["value"], rr
            else:
                continue
            rec = {"value": val, "basis": src["basis"], "source_url": src["source_url"], "derived": True}
            items[key][year] = rec
            p = parsed.get(year)
            if p and abs(p["value"] - val) > 5:
                print("DERIVED-vs-PARSED", key, year, val, p["value"])
    items["gst_other_taxes"] = {}
    for year in u.YEARS:
        parts = [items.get(k, {}).get(year) for k in ("gross_tax_revenue", "corporation_tax", "income_tax", "customs", "union_excise")]
        if all(parts):
            g = parts[0]
            items["gst_other_taxes"][year] = {"value": g["value"] - sum(p["value"] for p in parts[1:]), "basis": g["basis"],
                                              "source_url": g["source_url"], "derived": True}
    out = {"years": u.YEARS, "unit": "Rs crore", "items": items}
    current_count = len(items.get("total_expenditure", {}))
    if current_count < 8:
        raise RuntimeError(f"parsed only {current_count} budget years; previous data retained")
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding="utf-8") as fh:
                previous = json.load(fh)
            previous_count = len(previous.get("items", {}).get("total_expenditure", {}))
            if previous_count and current_count < max(3, int(previous_count * 0.8)):
                raise RuntimeError(f"parsed {current_count} budget years, down from {previous_count}; previous data retained")
        except (json.JSONDecodeError, OSError):
            pass
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    for c in conflicts:
        print("CONFLICT", c)
    for key, s in items.items():
        miss = [y for y in u.YEARS if y not in s]
        print(key, len(s), "missing", miss)


if __name__ == "__main__":
    main()

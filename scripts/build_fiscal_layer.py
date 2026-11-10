"""Build the 'Union Budget' catalog group, 'How India Borrows' charts and the State Fiscal Explorer data.

Inputs (all produced from official documents with a source_url on every value):
  data/union_budget.json  <- scripts/build_union_budget.py   (Budget at a Glance, 2014-15 to 2026-27)
  data/borrowing.json     <- scripts/build_borrowing.py      (RBI Handbook of Statistics on the Indian Economy)
  data/state_fiscal.json  <- scripts/build_state_fiscal.py   (RBI State Finances / Handbook of Statistics on Indian States)

Outputs:
  data/fiscal-series.json             catalog series merged by scripts/export_catalog.mjs
  frontend/src/data/fiscal-views.json data for the React fiscal views
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

UNION = "Union Budget"
STATE_GROUP = "State Performance & Regional Health"
STATE_SUB = "State Fiscal Explorer"
SUB_ANATOMY, SUB_RUPEE, SUB_RECEIPTS, SUB_SPEND, SUB_DEFICITS, SUB_TRANSFERS, SUB_BORROW = (
    "Budget Anatomy", "The Rupee", "Receipts", "Expenditure", "Deficits & Capex", "Transfers to States", "Borrowing")
BASIS_SUFFIX = {"Actuals": "", "RE": " RE", "BE": " BE"}
LAKH = 1e5  # rupees crore per lakh crore
SOURCE_NAME = "Union Budget, Budget at a Glance (indiabudget.gov.in)"

NODE_INFO = {
    "income_tax": ("Income tax", "#ff9933", "Tax on personal incomes, collected by the Centre; shared with States through the tax-devolution pool."),
    "corporation_tax": ("Corporation tax", "#f6c344", "Tax on company profits; part of the divisible pool shared with States."),
    "gst_other_taxes": ("GST, service tax & other taxes", "#3fb950", "Goods and Services Tax (Union share incl. IGST/UTGST/cess) plus service tax and other taxes, derived as gross tax revenue less the four headline taxes."),
    "customs": ("Customs", "#58a6ff", "Import duties and other customs levies."),
    "union_excise": ("Union excise duties", "#bc8cff", "Excise on petroleum, tobacco and other goods outside GST, plus special duties."),
    "non_tax_revenue": ("Non-tax revenue", "#39c5bb", "Dividends and profits (RBI, PSUs), interest receipts, spectrum and other fees."),
    "non_debt_capital": ("Non-debt capital receipts", "#a5d6ff", "Recovery of loans and disinvestment/other capital receipts that do not create debt (total spending less revenue receipts less the fiscal deficit)."),
    "borrowings": ("Borrowings & other liabilities", "#ff7b72", "The fiscal deficit: what the Centre has to borrow (dated securities, Treasury Bills, small savings, external debt) to meet spending."),
    "states_share_taxes": ("States' share of taxes", "#f778ba", "Tax devolution: the part of the Centre's gross taxes passed to States on the Finance Commission formula (derived as gross tax revenue less net tax revenue, so it also includes small assignments to Union Territories and the NCCD fund)."),
    "interest_payments": ("Interest payments", "#ff7b72", "Interest on the Centre's past borrowings (dated securities, T-bills, small savings, external debt)."),
    "type_establishment": ("Establishment expenditure", "#d2a8ff", "Salaries, pensions and running costs of the Union government."),
    "type_central_sector": ("Central sector schemes", "#58a6ff", "Schemes fully funded and run by the Centre."),
    "type_other_central_sector": ("Other central sector (excl. interest)", "#8b949e", "Central sector expenditure outside schemes and establishment, e.g. defence capital, subsidies and loans, excluding interest."),
    "type_centrally_sponsored": ("Centrally sponsored schemes", "#3fb950", "Schemes run by States with Central funding."),
    "type_finance_commission": ("Finance Commission grants", "#ffa657", "Grants to States and local bodies recommended by the Finance Commission."),
    "type_other_transfers": ("Other transfers to States", "#f6c344", "Other grants and loans to States and Union Territories."),
    "other_revenue_expenditure": ("Other revenue expenditure", "#8b949e", "All revenue expenditure other than interest (before the detailed scheme classification began in 2015-16)."),
    "capital_expenditure": ("Capital expenditure", "#39c5bb", "Spending that creates assets: roads, railways, defence equipment, loans to States for capex."),
}
USES_DETAILED = ["states_share_taxes", "interest_payments", "type_establishment", "type_central_sector", "type_other_central_sector",
                 "type_centrally_sponsored", "type_finance_commission", "type_other_transfers"]
USES_COARSE = ["states_share_taxes", "interest_payments", "other_revenue_expenditure", "capital_expenditure"]
SOURCES = ["income_tax", "corporation_tax", "gst_other_taxes", "customs", "union_excise", "non_tax_revenue", "non_debt_capital", "borrowings"]


def jload(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class Budget:
    def __init__(self, raw):
        self.raw = raw
        self.years = raw["years"]
        self.items = raw["items"]

    def rec(self, key, year):
        return self.items.get(key, {}).get(year)

    def val(self, key, year):
        rec = self.rec(key, year)
        return rec["value"] if rec else None

    def basis(self, year):
        return self.items["total_expenditure"][year]["basis"]

    def label(self, year):
        return year + BASIS_SUFFIX.get(self.basis(year), "")

    def series(self, key):
        return {y: self.val(key, y) for y in self.years if self.val(key, y) is not None}


def lakh(values):
    return {y: round(v / LAKH, 2) for y, v in values.items()}


def make_series(title, subtitle, sub, datasets, *, suffix, source, note, category=UNION, chart="line", label_for=lambda y: y,
                color="#ff9933", frequency="Annual", extra_note=""):
    years = sorted(set.intersection(*(set(d[2]) for d in datasets)))
    if len(years) < 2:
        raise ValueError(f"Too few observations for {title}")
    entry = {
        "labels": [label_for(y) for y in years],
        "chartType": chart,
        "source": source,
        "note": " ".join(part for part in (note, extra_note) if part),
        "meta": {"title": title, "subtitle": subtitle, "frequency": frequency, "color": color, "suffix": suffix,
                 "category": category, "subgroup": sub},
    }
    if len(datasets) == 1:
        entry["values"] = [datasets[0][2][y] for y in years]
    else:
        entry["datasets"] = [{"label": label, "color": colour, "values": [values[y] for y in years]} for label, colour, values in datasets]
    return entry


def pie_series(title, subtitle, sub, points, *, suffix, source, note, color):
    points = [(label, round(value, 2)) for label, value in points if value and value > 0]
    return {"labels": [p[0] for p in points], "values": [p[1] for p in points], "chartType": "doughnut", "scope": "category",
            "source": source, "note": note,
            "meta": {"title": title, "subtitle": subtitle, "frequency": "Annual", "color": color, "suffix": suffix,
                     "category": UNION, "subgroup": sub}}


def build_anatomy(b: Budget):
    by_year = {}
    for year in b.years:
        te, rr, fd = (b.val(k, year) for k in ("total_expenditure", "revenue_receipts", "fiscal_deficit"))
        gross, nontax, net_tax = (b.val(k, year) for k in ("gross_tax_revenue", "non_tax_revenue", "net_tax_revenue"))
        interest, capex, rexp = (b.val(k, year) for k in ("interest_payments", "capital_expenditure", "revenue_expenditure"))
        if None in (te, rr, fd, gross, nontax, net_tax, interest, capex, rexp):
            continue
        states_share = gross - net_tax
        sources = {k: b.val(k, year) for k in ("income_tax", "corporation_tax", "gst_other_taxes", "customs", "union_excise", "non_tax_revenue")}
        sources["borrowings"] = fd
        sources["non_debt_capital"] = te - rr - fd
        types = {k: b.val(k, year) for k in ("type_establishment", "type_central_sector", "type_other_central_sector",
                                              "type_centrally_sponsored", "type_finance_commission", "type_other_transfers")}
        uses = {"states_share_taxes": states_share, "interest_payments": interest}
        if all(v is not None for v in types.values()):
            uses.update(types)
            uses["type_other_central_sector"] = types["type_other_central_sector"] - interest
            order = USES_DETAILED
        else:
            uses["other_revenue_expenditure"] = rexp - interest
            uses["capital_expenditure"] = capex
            order = USES_COARSE
        total = te + states_share
        assert abs(sum(sources.values()) - total) < 2 and abs(sum(uses.values()) - total) < 2, (year, sum(sources.values()), sum(uses.values()), total)
        prev = by_year.get(b.years[b.years.index(year) - 1]) if b.years.index(year) else None

        def node(kind, key, value):
            label, colour, desc = NODE_INFO[key]
            record = {"id": key, "label": label, "value": round(value), "pct": round(100 * value / total, 1), "paise": round(100 * value / total),
                      "color": colour, "desc": desc}
            if prev:
                before = {n["id"]: n["value"] for n in prev[kind]}.get(key)
                if before:
                    record["prev"] = before
                    record["yoy"] = round(100 * (value / before - 1), 1)
            return record

        rec_te = b.rec("total_expenditure", year)
        by_year[year] = {
            "label": b.label(year), "basis": b.basis(year), "source_url": rec_te["source_url"], "total": round(total),
            "sources": [node("sources", k, sources[k]) for k in SOURCES],
            "uses": [node("uses", k, uses[k]) for k in order],
            "headline": {
                "total_expenditure": round(te), "revenue_receipts": round(rr), "gross_tax_revenue": round(gross),
                "capital_expenditure": round(capex), "interest_payments": round(interest),
                "interest_share_of_revenue_receipts": round(100 * interest / rr, 1),
                "fiscal_deficit": round(fd), "fiscal_deficit_pct_gdp": (b.rec("fiscal_deficit", year) or {}).get("pct_gdp"),
                "revenue_deficit": round(b.val("revenue_deficit", year)), "revenue_deficit_pct_gdp": (b.rec("revenue_deficit", year) or {}).get("pct_gdp"),
                "primary_deficit": round(b.val("primary_deficit", year)), "primary_deficit_pct_gdp": (b.rec("primary_deficit", year) or {}).get("pct_gdp"),
                "transfers_to_states": round(b.val("total_transfers_states", year)) if b.val("total_transfers_states", year) else None,
            },
        }
    return by_year


def union_series(b: Budget, anatomy):
    out = {}
    latest = b.years[-1]
    src = b.rec("total_expenditure", latest)["source_url"]
    lab = b.label
    base = f"{SOURCE_NAME}. Each year's figure comes from that Budget's own Budget at a Glance (links in data/union_budget.json): Actuals where published, otherwise Revised (RE) or Budget Estimates (BE)."

    def one(key, title, subtitle, sub, color, chart="line", unit_note=""):
        s = lakh(b.series(key))
        return make_series(title, subtitle, sub, [(title, color, s)], suffix=" ₹ lakh cr", source=src, note=f"{unit_note} {base}".strip(),
                           chart=chart, label_for=b.label, color=color)

    out["ub_anatomy"] = {
        "labels": ["Interactive anatomy"], "values": [1], "chartType": "budget-anatomy", "scope": "module", "source": src,
        "note": f"Pick a Budget year, see the Centre's receipts flow into expenditure, and click any block for its size, share and change. {base}",
        "meta": {"title": "Anatomy of the Union Budget", "subtitle": "Where the money comes from and where it goes, 2014-15 to 2026-27",
                 "frequency": "Interactive, annual", "color": "#ff9933", "category": UNION, "subgroup": SUB_ANATOMY},
    }
    for year, tag in ((latest, "BE"), ("2024-25", "Actuals")):
        if year not in anatomy:
            continue
        data = anatomy[year]
        label = f"{year} {tag}"
        out[f"ub_rupee_comes_from_{year.replace('-', '_')}"] = pie_series(
            f"Where the rupee comes from ({label})", "Paise in every rupee of the Centre's receipts", SUB_RUPEE,
            [(n["label"], n["paise"] if n["paise"] >= 1 else n["pct"]) for n in data["sources"]], suffix=" paise", source=data["source_url"], color="#ff9933",
            note=f"Share of total Central receipts including the States' share of taxes (gross basis): taxes by type, non-tax revenue, non-debt capital receipts and borrowings. {base}")
        out[f"ub_rupee_goes_to_{year.replace('-', '_')}"] = pie_series(
            f"Where the rupee goes ({label})", "Paise in every rupee of Central spending", SUB_RUPEE,
            [(n["label"], n["paise"] if n["paise"] >= 1 else n["pct"]) for n in data["uses"]], suffix=" paise", source=data["source_url"], color="#58a6ff",
            note=f"Total spending plus the States' share of taxes, split by expenditure type; interest is carved out of 'other central sector'. {base}")

    # Receipts
    out["ub_gross_tax_revenue"] = one("gross_tax_revenue", "Gross tax revenue of the Union", "Total taxes collected by the Centre before States' share", SUB_RECEIPTS, "#ff9933")
    out["ub_net_tax_revenue"] = one("net_tax_revenue", "Net tax revenue to the Centre", "Gross taxes less States' share (derived)", SUB_RECEIPTS, "#f6c344", unit_note="Derived as revenue receipts minus non-tax revenue.")
    out["ub_revenue_receipts"] = one("revenue_receipts", "Revenue receipts", "Net taxes plus non-tax revenue", SUB_RECEIPTS, "#3fb950")
    out["ub_non_tax_revenue"] = one("non_tax_revenue", "Non-tax revenue", "Dividends, interest receipts, fees and other non-tax receipts", SUB_RECEIPTS, "#39c5bb")
    out["ub_tax_by_type"] = make_series(
        "Union taxes by type", "Income tax, corporation tax, GST & other, customs and excise", SUB_RECEIPTS,
        [("Income tax", "#ff9933", lakh(b.series("income_tax"))), ("Corporation tax", "#f6c344", lakh(b.series("corporation_tax"))),
         ("GST, service tax & other", "#3fb950", lakh(b.series("gst_other_taxes"))), ("Customs", "#58a6ff", lakh(b.series("customs"))),
         ("Union excise", "#bc8cff", lakh(b.series("union_excise")))],
        suffix=" ₹ lakh cr", source=src, note=f"GST, service tax & other is derived as gross tax revenue less the other four. {base}", label_for=b.label)
    out["ub_income_tax"] = one("income_tax", "Income tax receipts", "Personal income tax, gross to the Centre", SUB_RECEIPTS, "#ff9933")
    out["ub_corporation_tax"] = one("corporation_tax", "Corporation tax receipts", "Tax on company profits, gross to the Centre", SUB_RECEIPTS, "#f6c344")
    out["ub_gst_other"] = one("gst_other_taxes", "GST, service tax & other taxes", "Derived: gross taxes less income, corporation, customs and excise", SUB_RECEIPTS, "#3fb950")
    out["ub_customs"] = one("customs", "Customs duties", "Import duties collected by the Centre", SUB_RECEIPTS, "#58a6ff")
    out["ub_union_excise"] = one("union_excise", "Union excise duties", "Excise duties collected by the Centre", SUB_RECEIPTS, "#bc8cff")
    out["ub_borrowings_fd"] = one("fiscal_deficit", "Borrowings and other liabilities (fiscal deficit)", "What the Centre borrows each year", SUB_RECEIPTS, "#ff7b72")

    # Expenditure
    out["ub_total_expenditure"] = one("total_expenditure", "Union Budget total expenditure", "Revenue plus capital expenditure", SUB_SPEND, "#58a6ff")
    out["ub_revenue_expenditure"] = one("revenue_expenditure", "Revenue expenditure", "Spending that does not create assets (derived)", SUB_SPEND, "#bc8cff", unit_note="Derived as revenue receipts plus revenue deficit.")
    out["ub_capital_expenditure"] = one("capital_expenditure", "Capital expenditure (capex)", "Spending that creates assets (derived)", SUB_SPEND, "#39c5bb", unit_note="Derived as total expenditure minus revenue expenditure.")
    out["ub_interest_payments"] = one("interest_payments", "Interest payments", "Interest on the Centre's debt", SUB_SPEND, "#ff7b72")
    out["ub_interest_revenue_receipts"] = make_series(
        "Interest payments as % of revenue receipts", "How much of each rupee of revenue goes to interest", SUB_BORROW,
        [("Interest ÷ revenue receipts", "#ff7b72", {y: round(100 * b.val("interest_payments", y) / b.val("revenue_receipts", y), 1) for y in b.years})],
        suffix="%", source=src, note=f"Interest payments divided by revenue receipts (net of States' share). {base}", label_for=b.label, color="#ff7b72")
    types = [("type_establishment", "Establishment"), ("type_central_sector", "Central sector schemes"), ("type_other_central_sector", "Other central sector (incl. interest)"),
             ("type_centrally_sponsored", "Centrally sponsored"), ("type_finance_commission", "Finance Commission grants"), ("type_other_transfers", "Other transfers")]
    colours = ["#d2a8ff", "#58a6ff", "#8b949e", "#3fb950", "#ffa657", "#f6c344"]
    out["ub_expenditure_by_type"] = make_series(
        "Expenditure by type", "Establishment, schemes and transfers (2015-16 onwards)", SUB_SPEND,
        [(lab, col, lakh(b.series(k))) for (k, lab), col in zip(types, colours)], suffix=" ₹ lakh cr", source=src,
        note=f"The six-way classification in the Budget at a Glance; interest is part of other central sector. {base}", label_for=b.label)
    out["ub_capex_share"] = make_series(
        "Capital expenditure as % of total spending", "Share of the Budget that builds assets", SUB_SPEND,
        [("Capex share", "#39c5bb", {y: round(100 * b.val("capital_expenditure", y) / b.val("total_expenditure", y), 1) for y in b.years})],
        suffix="%", source=src, note=f"Derived: capital expenditure divided by total expenditure. {base}", label_for=b.label, color="#39c5bb")

    # Deficits & capex
    pct = lambda key: {y: b.rec(key, y)["pct_gdp"] for y in b.years if b.rec(key, y) and b.rec(key, y).get("pct_gdp") is not None}  # noqa: E731
    out["ub_deficits_pct_gdp"] = make_series(
        "Fiscal, revenue and primary deficit (% of GDP)", "The three deficits as printed in each Budget", SUB_DEFICITS,
        [("Fiscal deficit", "#ff7b72", pct("fiscal_deficit")), ("Revenue deficit", "#f6c344", pct("revenue_deficit")), ("Primary deficit", "#58a6ff", pct("primary_deficit"))],
        suffix="% GDP", source=src, note=f"Percent of GDP as printed in the Budget at a Glance for that year's basis. {base}", label_for=b.label)
    out["ub_fiscal_deficit_pct_gdp"] = make_series(
        "Fiscal deficit (% of GDP)", "Gross fiscal deficit of the Centre", SUB_DEFICITS, [("Fiscal deficit", "#ff7b72", pct("fiscal_deficit"))],
        suffix="% GDP", source=src, note=f"Percent of GDP as printed in the Budget at a Glance. {base}", label_for=b.label, color="#ff7b72")
    out["ub_fiscal_deficit"] = one("fiscal_deficit", "Fiscal deficit (₹ lakh crore)", "Gross fiscal deficit of the Centre", SUB_DEFICITS, "#ff7b72")
    out["ub_revenue_deficit"] = one("revenue_deficit", "Revenue deficit (₹ lakh crore)", "Revenue expenditure minus revenue receipts", SUB_DEFICITS, "#f6c344")
    out["ub_primary_deficit"] = one("primary_deficit", "Primary deficit (₹ lakh crore)", "Fiscal deficit minus interest payments", SUB_DEFICITS, "#58a6ff")
    out["ub_capex_trend"] = one("capital_expenditure", "Central capex trajectory", "Capital expenditure of the Union government", SUB_DEFICITS, "#39c5bb", unit_note="Derived as total expenditure minus revenue expenditure.")

    # Transfers to states
    out["ub_states_share_taxes"] = one("states_share_taxes", "States' share of Central taxes", "Tax devolution to States", SUB_TRANSFERS, "#f778ba")
    out["ub_total_transfers"] = one("total_transfers_states", "Total transfers to States", "Tax devolution plus grants and loans", SUB_TRANSFERS, "#ffa657")
    out["ub_finance_commission"] = one("type_finance_commission", "Finance Commission grants to States", "Grants recommended by the Finance Commission", SUB_TRANSFERS, "#f6c344")
    out["ub_centrally_sponsored"] = one("type_centrally_sponsored", "Centrally sponsored schemes", "Central funding for State-run schemes", SUB_TRANSFERS, "#3fb950")
    devol = {y: round(100 * b.val("states_share_taxes", y) / b.val("gross_tax_revenue", y), 1) for y in b.years if b.val("states_share_taxes", y)}
    out["ub_devolution_share"] = make_series(
        "States' share as % of gross Central taxes", "How much of Central tax collections is passed to States", SUB_TRANSFERS,
        [("Share devolved", "#f778ba", devol)], suffix="%", source=src, note=f"States' share of taxes divided by gross tax revenue. {base}", label_for=b.label, color="#f778ba")
    return out


def borrowing_series(b: Budget, raw):
    s = raw["series"]
    out = {}

    def vals(key, scale=LAKH, digits=2):
        return {y: round(v / scale, digits) for y, v in s[key]["values"].items()}

    def src(key):
        return s[key]["source_url"]

    hbs = "RBI Handbook of Statistics on the Indian Economy 2024-25"

    def add(key, title, subtitle, datasets, suffix, source_key, note, chart="line", first="2004-05", color="#ff7b72", label_for=lambda y: y):
        trimmed = [(l, c, {y: v for y, v in d.items() if y >= first}) for l, c, d in datasets]
        out[key] = make_series(title, subtitle, SUB_BORROW, trimmed, suffix=suffix, source=src(source_key), note=f"{note} Source: {hbs}, {s[source_key]['source'].split(', ')[-1]}.",
                               chart=chart, color=color, label_for=label_for)

    add("hib_gross_net_centre", "Centre's gross and net market borrowings", "Dated-security issuance by the Union government",
        [("Gross", "#ff7b72", vals("mb_centre_gross")), ("Net", "#58a6ff", vals("mb_centre_net"))], " ₹ lakh cr", "mb_centre_gross",
        "Gross is the amount raised; net is gross less repayments.", chart="bar")
    add("hib_gross_net_states", "States' gross and net market borrowings", "State Development Loans issued by States",
        [("Gross", "#ff7b72", vals("mb_states_gross")), ("Net", "#58a6ff", vals("mb_states_net"))], " ₹ lakh cr", "mb_states_gross",
        "State Development Loans; net is after repayments.", chart="bar")
    add("hib_combined_borrowing", "Centre + States gross market borrowings", "Combined government appetite for market debt",
        [("Centre", "#ff9933", vals("mb_centre_gross")), ("States", "#3fb950", vals("mb_states_gross")), ("Combined", "#bc8cff", vals("mb_comb_gross"))],
        " ₹ lakh cr", "mb_comb_gross", "Gross amounts raised in the year.")
    add("hib_instruments", "Central government liabilities by instrument", "Dated securities vs Treasury Bills vs small savings (outstanding, end-March)",
        [("Dated securities", "#ff9933", vals("liab_market_loans")), ("Treasury Bills", "#58a6ff", vals("liab_tbills")), ("Small savings, deposits & PF", "#3fb950", vals("liab_small_savings"))],
        " ₹ lakh cr", "liab_market_loans", "Last year shown is a Budget Estimate; the year before a Revised Estimate. Treasury Bills are 91-day plus 182/364-day.")
    add("hib_total_liabilities", "Central government total liabilities", "Outstanding liabilities of the Union government",
        [("Total liabilities", "#ff7b72", vals("liab_total"))], " ₹ lakh cr", "liab_total", "End-March stock; latest years are estimates.")
    add("hib_central_debt_gdp", "Central government debt (% of GDP)", "Outstanding liabilities of the Centre as a share of GDP",
        [("Centre", "#ff9933", vals("debt_gdp_centre", 1, 2))], "% GDP", "debt_gdp_centre", "RBI estimates; latest two years are RE/BE.", first="1990-91")
    add("hib_general_govt_debt", "General government debt (% of GDP)", "Centre + States liabilities as a share of GDP",
        [("Centre", "#ff9933", vals("debt_gdp_centre", 1, 2)), ("States", "#3fb950", vals("debt_gdp_states", 1, 2)), ("Combined", "#ff7b72", vals("debt_gdp_general", 1, 2))],
        "% GDP", "debt_gdp_general", "Combined = Centre + States, net of loans from Centre as reported by RBI.", first="1990-91")
    add("hib_combined_liabilities", "Combined liabilities of Centre and States", "Outstanding liabilities, end-March",
        [("Combined", "#bc8cff", vals("liab_combined"))], " ₹ lakh cr", "liab_combined", "Includes external liabilities of the Centre at current exchange rates.")
    add("hib_external_debt", "India's external debt", "Long-term and short-term external debt, end-March",
        [("Long-term", "#58a6ff", vals("ext_long")), ("Short-term", "#ff9933", vals("ext_short")), ("Total", "#ff7b72", vals("ext_total"))],
        " ₹ lakh cr", "ext_total", "Government plus private external debt in rupee terms.", first="2006-07")
    mats = {k: s[f"mat_{k}"]["values"] for k in ("under5", "five10", "over10")}
    totals = {y: sum(mats[k][y] for k in mats) for y in mats["under5"] if all(y in mats[k] for k in mats)}
    add("hib_maturity_profile", "Maturity profile of Central rupee loans", "Share of outstanding rupee loans by residual maturity",
        [("Under 5 years", "#ff7b72", {y: round(100 * mats["under5"][y] / t, 1) for y, t in totals.items()}),
         ("5-10 years", "#f6c344", {y: round(100 * mats["five10"][y] / t, 1) for y, t in totals.items()}),
         ("Over 10 years", "#3fb950", {y: round(100 * mats["over10"][y] / t, 1) for y, t in totals.items()})],
        "%", "mat_under5", "Shares of outstanding Government of India rupee loans, excluding special securities and compensation bonds; computed from the amounts in RBI Table 113.")
    add("hib_weighted_average_rate", "Weighted average interest rate on new dated securities", "Rate on securities issued during the year",
        [("Central government", "#ff9933", vals("wa_centre", 1, 2)), ("State governments", "#3fb950", vals("wa_states", 1, 2))], "%", "wa_centre",
        "Weighted average interest rate on the dated securities issued in each year.")
    for key, title, sub, colour in (("gsec", "Who holds Central government securities", "Holders of Central dated securities, 31 March 2025", "#ff9933"),
                                    ("sdl", "Who holds State government securities", "Holders of State Development Loans, 31 March 2025", "#3fb950")):
        h = s["holders"]["values"][key]
        total = h["Total"]["2024-25"]
        points = [(name, round(100 * v["2024-25"] / total, 1)) for name, v in h.items() if name != "Total" and v.get("2024-25")]
        out[f"hib_holders_{key}"] = pie_series(title, sub, SUB_BORROW, sorted(points, key=lambda p: -p[1]), suffix="%", source=s["holders"]["source_url"], color=colour,
                                              note=f"Share of outstanding amount by category of holder. 'Others' includes State governments. Source: {hbs}, Table 110.")
    return out


STATE_NOTE = "Source: RBI Handbook of Statistics on Indian States 2024-25 and RBI State Finances: A Study of Budgets 2025-26."
STATE_RANK = ["gfd_gsdp", "rd_gsdp", "debt_gsdp", "interest_rr", "own_tax_rr", "transfers_rr", "committed_rr", "capex_gsdp", "gsdp_growth"]


def state_series(sf):
    out = {}
    year = "2023-24"
    modules = [
        ("sf_fiscal_matrix", "fiscal-matrix", "State fiscal matrix", "Every State against every fiscal metric as a colour-scaled, sortable heatmap"),
        ("sf_head_to_head", "fiscal-compare", "State fiscal head-to-head", "Compare any two States on fiscal health, with mirrored bars and a shareable link"),
        ("sf_spending_by_function", "fiscal-spending", "State spending by function", "How each State splits its revenue spending: education, health, police, agriculture and more"),
    ]
    for key, chart, title, subtitle in modules:
        out[key] = {"labels": ["Interactive"], "values": [1], "chartType": chart, "scope": "module",
                    "source": sf["metrics"]["gfd_gsdp"]["source_url"], "note": f"{subtitle}. {STATE_NOTE}",
                    "meta": {"title": title, "subtitle": subtitle, "frequency": "Interactive, annual", "color": "#ff9933",
                             "category": STATE_GROUP, "subgroup": STATE_SUB}}
    for metric in STATE_RANK:
        m = sf["metrics"][metric]
        values = {s: v[year] for s, v in m["values"].items() if year in v and s != "All States & UTs"}
        labels = sorted(values, key=lambda s: (-values[s], s))
        unit = m["unit"]
        out[f"sf_rank_{metric}"] = {
            "labels": labels, "values": [values[s] for s in labels], "chartType": "bar", "indexAxis": "y", "scope": "state",
            "source": m["source_url"], "note": f"{m['note']} {m['source']}. Year: {year}; {len(labels)} States/UTs with data.",
            "meta": {"title": f"{m['label']} by State ({year})", "subtitle": unit, "frequency": "Annual", "color": "#ff9933",
                     "suffix": "%" if unit.startswith("%") else "", "category": STATE_GROUP, "subgroup": STATE_SUB},
        }
    return out


def main():
    budget = Budget(jload(DATA / "union_budget.json"))
    borrowing = jload(DATA / "borrowing.json")
    states = jload(DATA / "state_fiscal.json")
    anatomy = build_anatomy(budget)
    series = {}
    series.update(union_series(budget, anatomy))
    series.update(borrowing_series(budget, borrowing))
    series.update(state_series(states))

    views = {
        "union_budget": {
            "years": [{"year": y, "label": anatomy[y]["label"], "basis": anatomy[y]["basis"]} for y in budget.years if y in anatomy],
            "by_year": anatomy,
            "unit": "₹ crore",
            "source": SOURCE_NAME,
            "note": "Gross basis: receipts include the States' share of taxes, which is shown as an outflow. Actuals where published, else Revised or Budget Estimates.",
        },
        "states": {
            "states": [s for s in states["states"]], "years": states["years"],
            "metrics": [{"key": k, **{f: m[f] for f in ("label", "unit", "better", "source", "source_url", "note")}} for k, m in states["metrics"].items()],
            "values": {k: m["values"] for k, m in states["metrics"].items()},
        },
        "functions": states["functions"],
    }
    (DATA / "fiscal-series.json").write_text(json.dumps({"series": series}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    payload = json.dumps(views, ensure_ascii=False, separators=(",", ":"))
    (ROOT / "frontend" / "src" / "data" / "fiscal-views.json").write_text(payload + "\n", encoding="utf-8")
    print(len(series), "series;", sum(1 for s in series.values() if s["meta"]["category"] == UNION), "in Union Budget;", len(anatomy), "anatomy years")


if __name__ == "__main__":
    main()

"""Parse the Union Budget 'Budget at a Glance' (BaG) PDFs published at indiabudget.gov.in.

Each BaG table carries four columns: Actuals(t-2), BE(t-1), RE(t-1), BE(t) (2024-25 adds a Provisional
Actuals column that is dropped here). A fiscal year Y is therefore resolved as
    Actual  <- BaG(Y+2) column 1
    RE      <- BaG(Y+1) column 3
    BE      <- BaG(Y)   column 4  (cross-checked against BaG(Y+1) column 2)
and the best available stage (Actual > RE > BE) is reported with its basis.
"""
import os
import re
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, "data", "raw_fiscal")
FIRST_YEAR, LAST_YEAR = 2014, 2026
YEARS = [f"{y}-{str(y + 1)[2:]}" for y in range(FIRST_YEAR, LAST_YEAR + 1)]
SITE = "https://www.indiabudget.gov.in"


def bag_url(year, part):
    y = int(year[:4])
    if y >= 2020:
        if y == 2026:
            return f"{SITE}/doc/Budget_at_Glance/bag{part}.pdf"
        return f"{SITE}/budget{year}/doc/Budget_at_Glance/bag{part}.pdf"
    return f"{SITE}/budget_archive/ub{year}/bag/bag{part}.pdf"


def source_url(year, part=1):
    if year == "2026-27" and part == 1:
        return f"{SITE}/doc/Budget_at_Glance/budget_at_a_glance.pdf"
    return bag_url(year, part)


def pdf_path(year, part):
    return os.path.join(CACHE, f"bag{year}_bag{part}.pdf")


def fetch_all():
    os.makedirs(CACHE, exist_ok=True)
    failures = []
    for year in YEARS:
        for part in range(1, 7):
            dest = pdf_path(year, part)
            layout = dest.replace(".pdf", ".lay.txt")
            if os.path.exists(layout) and os.path.getsize(layout) > 0:
                continue
            if os.path.exists(dest) and os.path.getsize(dest) > 1000:
                with open(dest, "rb") as handle:
                    if handle.read(5) == b"%PDF-":
                        continue
            last_error = "invalid PDF response"
            for attempt in range(3):
                try:
                    request = Request(bag_url(year, part), headers={"User-Agent": "Mozilla/5.0"})
                    with urlopen(request, timeout=90) as response:
                        payload = response.read()
                    if len(payload) <= 1000 or not payload.startswith(b"%PDF-"):
                        raise ValueError("Budget at a Glance response was not a PDF")
                    with open(dest, "wb") as handle:
                        handle.write(payload)
                    break
                except HTTPError as error:
                    if error.code == 404:
                        last_error = "optional budget part is not published"
                        break
                    last_error = str(error)
                    if attempt < 2:
                        time.sleep(1)
                except Exception as error:
                    last_error = str(error)
                    if attempt < 2:
                        time.sleep(1)
            else:
                failures.append(f"{year} part {part}: {last_error}")
    if failures:
        raise RuntimeError("could not fetch required Budget at a Glance files: " + "; ".join(failures[:8]))


def layout_lines(year):
    """All layout-mode text lines of every cached part of a BaG, tagged with the part number."""
    from pypdf import PdfReader
    out = []
    for part in range(1, 7):
        lay = os.path.join(CACHE, f"bag{year}_bag{part}.lay.txt")
        if not os.path.exists(lay):
            pdf = pdf_path(year, part)
            if not os.path.exists(pdf) or os.path.getsize(pdf) < 1000:
                continue
            try:
                pages = ["=====P%d\n%s" % (i, p.extract_text(extraction_mode="layout")) for i, p in enumerate(PdfReader(pdf).pages)]
            except Exception:
                continue
            with open(lay, "w", encoding="utf-8") as fh:
                fh.write("\n".join(pages))
        with open(lay, encoding="utf-8") as fh:
            out.extend((part, ln) for ln in fh.read().split("\n"))
    return out


TOKEN = re.compile(r"\(-\)\s*\d[\d,]*|-?\d[\d,]*(?:\.\d+)?|(?<=\s)(?:\.{2,3}|-)(?=\s|$)")


def row_values(tail, min_abs=100, placeholders=False):
    tail = re.sub(r"\(\s*-?\d+\.\d+\s*\)", " ", tail)
    tail = re.sub(r"\[[^\]]*\]|\([^)]*[+\-][^)]*\)", " ", tail)
    vals = []
    for tok in TOKEN.findall(" " + tail + " "):
        t = tok.strip()
        if t in ("..", "...", "-"):
            if placeholders:
                vals.append(0.0)
            continue
        neg = t.startswith("(-)")
        t = t.replace("(-)", "").replace(",", "").strip()
        v = float(t) * (-1 if neg else 1)
        if abs(v) >= min_abs or (placeholders and v == 0):
            vals.append(v)
    return vals


def norm4(vals, ncols=4):
    if ncols == 3:
        return [vals[0], None, vals[1], vals[2]] if len(vals) == 3 else None
    if len(vals) == 5:
        vals = vals[:3] + vals[4:]
    return vals if len(vals) == 4 else None


def find_row(lines, label, parts=None, min_abs=100, placeholders=False, skip=0, ncols=4):
    rx = re.compile(label, re.I)
    seen = 0
    for idx, (part, ln) in enumerate(lines):
        if parts and part not in parts:
            continue
        m = rx.search(ln)
        if not m:
            continue
        tail = ln[m.end():]
        first_digit = re.search(r"\d", tail)
        if first_digit:
            tail = tail[:first_digit.start()] + re.split(r"[A-Za-z]", tail[first_digit.start():], maxsplit=1)[0]
        v = norm4(row_values(re.sub(r"[A-Za-z]+", " ", tail[:first_digit.start()]) + tail[first_digit.start():] if first_digit else tail, min_abs, placeholders), ncols)
        if v:
            if seen < skip:
                seen += 1
                continue
            return v, idx
    return None, None


def find_pct(lines, idx):
    """Printed '% of GDP' figures belonging to the row at lines[idx] (same line or the next two)."""
    if idx is None:
        return None
    blob = " ".join(ln for _, ln in lines[idx: idx + 3])
    got = [float(x) for x in re.findall(r"\(\s*(-?\d+\.\d+)\s*\)", blob)]
    if len(got) >= 5:
        got = got[:3] + got[4:5]
    return got[:4] if len(got) >= 4 else None


def clean_line(ln):
    return re.sub(r"\s+", " ", re.sub(r"[^\x20-\x7e]", " ", ln)).strip()


def expenditure_types(lines):
    """Six-way economic classification of total expenditure (BaG 'Expenditure' table, 2015-16 onwards).

    Returns {slot: [4 values]} and only when every column adds up to the printed Grand Total."""
    start = next((i for i, (_, ln) in enumerate(lines) if "Establishment Expenditure" in clean_line(ln)), None)
    if start is None:
        return {}
    rows = []
    for _, ln in lines[start:start + 60]:
        s = clean_line(ln)
        m = re.search(r"(\d{4,7}\s+-?\d{4,8}\s+-?\d{4,8}\s+\d{4,9})\s*$", s) or re.search(r"((?:-?\d{4,9}\s+){3}-?\d{4,9})\b", s)
        if not m:
            continue
        label = s[: m.start()]
        vals = [float(x) for x in m.group(1).split()]
        rows.append((label, vals))
        if "Grand Total" in s:
            break
    if not rows or "Grand Total" not in rows[-1][0] + "Grand Total" * 0 and not any("Grand Total" in r[0] for r in rows):
        return {}
    grand = next(v for lab, v in rows if "Grand Total" in lab)
    slots, order = {}, ["establishment", "central_sector", "other_central_sector", "centrally_sponsored", "finance_commission_grants", "other_grants_transfers"]
    state = 0
    for lab, v in rows:
        low = lab.lower()
        if "grand total" in low:
            break
        if "establishment expenditure" in low:
            slots["establishment"] = v; state = 1
        elif "interest" in low and "interest" not in slots:
            slots["interest"] = v
        elif "centrally sponsored" in low:
            slots["centrally_sponsored"] = v; state = 4
        elif "finance commission" in low:
            slots["finance_commission_grants"] = v; state = 5
        elif re.search(r"\bother\b", low) and state >= 5 and "other_grants_transfers" not in slots:
            slots["other_grants_transfers"] = v
        elif state == 1 and "central_sector" not in slots and ("project" in low or "central sector" in low):
            slots["central_sector"] = v
        elif state == 1 and "central_sector" in slots and "other_central_sector" not in slots and "interest" not in low:
            slots["other_central_sector"] = v
    if any(k not in slots for k in order):
        return {}
    out = {}
    for c in range(4):
        total = sum(slots[k][c] for k in order)
        ok = abs(total - grand[c]) <= max(5, 0.0005 * grand[c])
        for k in order + ["interest"]:
            if k in slots:
                out.setdefault(k, [None] * 4)[c] = slots[k][c] if ok else None
    return out


def gdp_note(lines):
    for _, ln in lines:
        m = re.search(r"GDP for BE[^`]*?`\s*([\d,]{7,})", ln)
        if m:
            return float(m.group(1).replace(",", ""))
    return None


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch_all()

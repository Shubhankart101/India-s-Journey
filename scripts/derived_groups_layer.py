"""Build dashboard subgroups derived from official data already committed in data/."""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

NEW_SUBGROUPS = {
    "Pew Research": ("Publication Activity", "Report Themes", "Survey Snapshot Comparisons"),
    "Elections": ("Historical Candidate Field & Competition", "Historical Victory Margins", "Recent Effective Candidate Field"),
    "U.S. Elections": ("Cycle-over-Cycle Finance Trends", "State Finance Rankings"),
}
COLORS = ("#ff9933", "#58a6ff", "#3fb950", "#bc8cff", "#f6c344", "#f778ba", "#39c5bb")
THEMES = (
    ("Economy & livelihoods", (r"econom(?:y|ic)", r"jobs?", r"poverty", r"income", r"business")),
    ("Religion & society", (r"religio(?:n|us)", r"hindus?", r"muslims?", r"christians?", r"caste", r"marriage", r"family")),
    ("Politics & governance", (r"politic(?:s|al)", r"democra(?:cy|tic)", r"government", r"election", r"leader(?:ship)?", r"parliament", r"modi")),
    ("International affairs", (r"foreign", r"global", r"china", r"pakistan", r"u\.s\.", r"world", r"international")),
    ("Technology & media", (r"internet", r"social media", r"news", r"technology", r"smartphone", r"\bai\b")),
    ("Climate & environment", (r"climate", r"environment", r"pollution", r"energy", r"water")),
    ("Gender & demographics", (r"gender", r"women", r"men", r"population", r"young", r"age")),
)


def _read_json(root: Path, filename: str) -> dict[str, Any] | None:
    try:
        data = json.loads((root / "data" / filename).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _series(key, labels, values, *, title, subtitle, category, subgroup, source, unit,
            note, explain, frequency, color=COLORS[0], chart_type="bar", index_axis=None):
    item = {
        "labels": labels, "values": values, "chartType": chart_type, "scope": "category",
        "source": source, "unit": unit,
        "note": note,
        "meta": {"title": title, "subtitle": subtitle, "frequency": frequency, "color": color,
                 "suffix": unit if unit == "%" else (f" {unit}" if unit else ""),
                 "category": category, "subgroup": subgroup,
                 "explain": {"what": explain[0], "read": explain[1], "why": explain[2]}},
    }
    if index_axis:
        item["indexAxis"] = index_axis
    return item


def _count_values(counter, labels):
    return [float(counter[label]) for label in labels]


def _publication_series(payload):
    reports = payload.get("reports", [])
    if not isinstance(reports, list):
        return {}
    dates = []
    for report in reports:
        if not isinstance(report, dict) or not isinstance(report.get("date"), str):
            continue
        try:
            dates.append(datetime.strptime(report["date"][:10], "%Y-%m-%d").date())
        except ValueError:
            continue
    if not dates:
        return {}
    source = "Pew Research Center India report catalogue (data/pew-india-reports.json)"
    category, subgroup = "Pew Research", "Publication Activity"
    yearly = Counter(date.year for date in dates)
    years = sorted(yearly)
    labels = [str(year) for year in years]
    coverage = (f"Counts the {len(dates)} catalogue entries with parseable publication dates. "
                "The search-result catalogue may not include every Pew India publication.")
    output = {}
    key = "dg_pew_reports_per_year"
    output[key] = _series(key, labels, [float(yearly[int(label)]) for label in labels], title="Pew India Reports Published per Year",
        subtitle="Dated catalogue entries by publication year", category=category, subgroup=subgroup,
        source=source, unit="reports", note=coverage,
        explain=("Number of dated catalogue reports published in each year.", "A higher count means more dated entries in the collected catalogue.", "Shows the publication cadence represented in Pew's India report catalogue."), frequency="Annual")
    cumulative, running = [], 0
    for year in years:
        running += yearly[year]
        cumulative.append(float(running))
    key = "dg_pew_reports_cumulative"
    output[key] = _series(key, labels, cumulative, title="Cumulative Pew India Reports in Catalogue",
        subtitle="Dated catalogue entries accumulated over time", category=category, subgroup=subgroup,
        source=source, unit="reports", note=coverage,
        explain=("Running total of catalogue entries through each publication year.", "This cumulative total only rises and is not an annual publication count.", "Makes growth of the collected catalogue visible over its dated coverage."), frequency="Cumulative by publication year", color=COLORS[1])
    quarters = Counter((date.month - 1) // 3 + 1 for date in dates)
    quarter_labels = ["Q1", "Q2", "Q3", "Q4"]
    key = "dg_pew_publications_by_quarter"
    output[key] = _series(key, quarter_labels, [float(quarters[i]) for i in range(1, 5)],
        title="Pew India Reports by Publication Quarter", subtitle="Catalogue dates grouped by calendar quarter",
        category=category, subgroup=subgroup, source=source, unit="reports", note=coverage,
        explain=("Counts dated catalogue entries in each calendar quarter across all available years.", "These pooled quarter totals are not a single-year seasonal comparison.", "Summarizes when dated reports appear within the calendar year."), frequency="Pooled catalogue", color=COLORS[2], chart_type="doughnut")
    weekdays = Counter(date.weekday() for date in dates)
    weekday_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    key = "dg_pew_publications_by_weekday"
    output[key] = _series(key, weekday_labels, [float(weekdays[i]) for i in range(7)],
        title="Pew India Reports by Publication Weekday", subtitle="Catalogue dates grouped by weekday",
        category=category, subgroup=subgroup, source=source, unit="reports", note=coverage,
        explain=("Counts dated catalogue entries by weekday of publication.", "Totals pool all years and are not adjusted for archive coverage.", "Describes the weekday pattern in the catalogue dates."), frequency="Pooled catalogue", color=COLORS[3], chart_type="doughnut")
    months = Counter(date.month for date in dates)
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    key = "dg_pew_publications_by_month"
    output[key] = _series(key, month_labels, [float(months[i]) for i in range(1, 13)],
        title="Pew India Reports by Publication Month", subtitle="Catalogue dates grouped by calendar month",
        category=category, subgroup=subgroup, source=source, unit="reports", note=coverage,
        explain=("Counts dated catalogue entries in each month, pooling all years.", "Pooled totals reflect the collected archive and changing yearly volume.", "Highlights the month distribution in the currently collected catalogue."), frequency="Pooled catalogue", color=COLORS[4])
    decades = Counter((date.year // 10) * 10 for date in dates)
    decade_labels = [f"{decade}s" for decade in sorted(decades)]
    key = "dg_pew_publications_by_decade"
    output[key] = _series(key, decade_labels, [float(decades[int(label[:-1])]) for label in decade_labels],
        title="Pew India Reports by Publication Decade", subtitle="Catalogue entries grouped into calendar decades",
        category=category, subgroup=subgroup, source=source, unit="reports", note=coverage,
        explain=("Counts dated catalogue entries by publication decade.", "Totals depend on archive coverage; the current decade may be incomplete.", "Offers a coarse view of the archive's publication history."), frequency="By publication decade", color=COLORS[5])
    return output


def _theme_series(payload):
    reports = payload.get("reports", [])
    if not isinstance(reports, list):
        return {}
    dated = []
    for report in reports:
        if not isinstance(report, dict) or not isinstance(report.get("title"), str):
            continue
        try:
            year = int(report["date"][:4])
        except (TypeError, ValueError, KeyError):
            continue
        dated.append((report["title"], year))
    if not dated:
        return {}
    labels = [str(year) for year in sorted({year for _, year in dated})]
    source = "Pew Research Center India report catalogue (data/pew-india-reports.json)"
    output = {}
    for index, (theme, terms) in enumerate(THEMES):
        patterns = [re.compile(rf"(?<!\w){term}(?!\w)", re.IGNORECASE) for term in terms]
        counts = Counter(year for title, year in dated if any(pattern.search(title) for pattern in patterns))
        key = "dg_pew_theme_" + re.sub(r"[^a-z0-9]+", "_", theme.lower()).strip("_")
        output[key] = _series(key, labels, [float(counts[int(label)]) for label in labels],
            title=f"Pew India Report Titles Matching {theme}", subtitle="Annual count of catalogue titles matching theme keywords",
            category="Pew Research", subgroup="Report Themes", source=source, unit="title matches",
            note=(f"Counts dated catalogue titles containing at least one of these keywords: {', '.join(terms)}. "
                  "A title may match multiple themes; this descriptive filter is not Pew's taxonomy."),
            explain=(f"Number of dated catalogue titles matching at least one keyword for {theme.lower()}.",
                     "Compare years within this keyword filter; themes overlap and a match does not imply a report is solely about that topic.",
                     "Shows how represented subject matter changes in the collected Pew India catalogue."),
            frequency="Annual", color=COLORS[index % len(COLORS)])
    return output


def _snapshot_series(payload):
    snapshots = payload.get("series", {})
    if not isinstance(snapshots, dict):
        return {}
    output = {}

    def entries(series_key, matcher):
        record = snapshots.get(series_key)
        if not isinstance(record, dict):
            return []
        labels, values = record.get("labels", []), record.get("values", [])
        if not isinstance(labels, list) or not isinstance(values, list):
            return []
        points = []
        for label, value in zip(labels, values):
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue
            if math.isfinite(number) and isinstance(label, str) and matcher(label):
                points.append((label, number))
        return points

    def add(key, title, subtitle, source_key, points, note, explain, frequency="Pew survey snapshot"):
        if len(points) < 2:
            return
        source_record = snapshots.get(source_key, {})
        source = "Pew Research Center India survey snapshots (data/pew-snapshots.json)"
        if isinstance(source_record, dict) and source_record.get("source"):
            source += f"; report source: {source_record['source']}"
        output[key] = _series(key, [label for label, _ in points], [value for _, value in points],
            title=title, subtitle=subtitle, category="Pew Research", subgroup="Survey Snapshot Comparisons",
            source=source, unit="% of respondents", note=note, explain=explain,
            frequency=frequency, chart_type="bar")

    smartphone = entries("pew_india_technology", lambda label: "owns a smartphone" in label.casefold())
    smartphone.sort(key=lambda point: point[0])
    add("dg_pew_smartphone_ownership_trend", "Smartphone Ownership in Pew India Snapshots", "Reported adult smartphone ownership across listed survey years",
        "pew_india_technology", smartphone,
        "Selects only snapshot entries whose label says respondents owned a smartphone; figures are copied from the committed snapshot catalogue. Wording and survey populations are source-defined.",
        ("Published shares of respondents reported as owning a smartphone in each listed year.", "Read each point as the source-reported percentage; do not extend beyond the listed snapshots.", "Provides a limited view of reported smartphone ownership over time."))
    economy = entries("pew_india_economy_confidence", lambda label: "rated national economy good" in label.casefold())
    economy.sort(key=lambda point: point[0])
    add("dg_pew_economy_rating_trend", "Pew Snapshot: National Economy Rated Good", "Repeated survey item on views of India's national economy",
        "pew_india_economy_confidence", economy,
        "Selects only labels stating respondents rated the national economy good; no interpolation is used.",
        ("Reported respondent share rating the national economy good in each listed year.", "Compare published survey-year points; unreported years are not filled.", "Tracks the available repeated Pew item."))
    leadership = entries("pew_india_leadership", lambda label: "favorable view of national leadership" in label.casefold())
    leadership.sort(key=lambda point: point[0])
    add("dg_pew_leadership_favorability_trend", "Pew Snapshot: Favorable View of National Leadership", "Repeated favorability item in available survey years",
        "pew_india_leadership", leadership,
        "Selects labels explicitly describing a favorable view of national leadership; distinct confidence and global-influence items are excluded.",
        ("Reported respondent share with a favorable view of national leadership in selected years.", "Only years with matching item wording are shown; values are source-published percentages.", "Makes available repeated leadership-favorability observations easier to compare."))
    pairs = (
        ("dg_pew_religion_respect_groups", "pew_india_religion_tolerance", "respecting all religions is very important", "Pew Snapshot: Respect for All Religions", "Hindu and Muslim respondents on the same 2021 item"),
        ("dg_pew_religion_diversity_groups", "pew_india_religion_tolerance", "better off with religious diversity", "Pew Snapshot: Views on Religious Diversity", "Hindu and Muslim respondents on the same 2021 item"),
        ("dg_pew_interfaith_marriage_groups", "pew_india_demographics_family", "important to stop inter-religious marriage", "Pew Snapshot: Views on Inter-religious Marriage", "Hindu and Muslim respondents on the same 2021 item"),
    )
    for key, source_key, phrase, title, subtitle in pairs:
        matched = entries(source_key, lambda label, phrase=phrase: phrase in label.casefold())
        points = []
        for label, value in matched:
            if "hindu" in label.casefold():
                points.append(("Hindus", value))
            elif "muslim" in label.casefold():
                points.append(("Muslims", value))
        points.sort(key=lambda point: point[0])
        add(key, title, subtitle, source_key, points,
            "Compares only the source-listed Hindu and Muslim respondent percentages for the same survey item. The figures are published snapshots, not estimates or legal classifications.",
            (f"Pew's reported shares for the same item, shown separately for Hindu and Muslim respondents.", "The labels identify respondent groups; this is a within-survey descriptive comparison.", "Makes available subgroup figures for the same question directly readable."),
            frequency="2021 survey snapshot")
    return output


def _number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _is_nota(row):
    return str(row.get("party", "")).strip().casefold() in {"nota", "none of the above"}


def _historical_events(payload):
    rows = payload.get("observations", [])
    if not isinstance(rows, list):
        return []
    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if not isinstance(row, dict) or str(row.get("election_type", "")).casefold() != "state assembly":
            continue
        try:
            year = int(row.get("year"))
        except (TypeError, ValueError):
            continue
        state = row.get("state_or_ut")
        seat = row.get("constituency_number") or row.get("constituency")
        if isinstance(state, str) and state and seat is not None and str(seat).strip():
            grouped[(year, state)][str(seat).strip().casefold()].append(row)
    return [(year, state, contests) for (year, state), contests in sorted(grouped.items())]


def _election_series(payload):
    events = _historical_events(payload)
    if not events:
        return {}
    source = "Election Commission of India statistical reports and detailed-result XLSX downloads (data/historical-elections.json)"
    output = {}
    field_group, margin_group = NEW_SUBGROUPS["Elections"][:2]
    for index, (year, state, contests) in enumerate(events):
        slug = re.sub(r"[^a-z0-9]+", "_", state.lower()).strip("_")
        label = f"{state} {year}"
        base_note = (f"Uses candidate-level rows in the partial ECI historical archive for {state} ({year}). "
                     "Available reports are selected downloads, not a complete national or state-time series.")
        bands = ("1–3", "4–6", "7–9", "10+")
        candidate_counts = Counter()
        for candidates in contests.values():
            count = sum(1 for candidate in candidates if not _is_nota(candidate))
            if count:
                candidate_counts["1–3" if count <= 3 else "4–6" if count <= 6 else "7–9" if count <= 9 else "10+"] += 1
        if sum(candidate_counts.values()):
            key = f"dg_elections_candidate_field_{year}_{slug}"
            output[key] = _series(key, list(bands), _count_values(candidate_counts, list(bands)),
                title=f"{label}: Candidates per Assembly Constituency", subtitle="Contested seats grouped by listed candidate count",
                category="Elections", subgroup=field_group, source=source, unit="constituencies",
                note=base_note + " Counts listed candidates and excludes NOTA.",
                explain=(f"Distribution of constituency candidate counts in archived {state} Assembly results.", "NOTA entries are excluded; candidate totals are grouped into the displayed count bands.", "Shows how candidate-field size varied across this archived election."),
                frequency=f"State Assembly {year}", color=COLORS[index % len(COLORS)])
        at_or_below, above = 0, 0
        for candidates in contests.values():
            for candidate in candidates:
                if _is_nota(candidate):
                    continue
                share = _number(candidate.get("vote_share_percent"))
                if share is not None:
                    if share <= 100 / 6:
                        at_or_below += 1
                    else:
                        above += 1
        if at_or_below + above:
            key = f"dg_elections_vote_share_threshold_{year}_{slug}"
            output[key] = _series(key, ["At or below 1/6", "Above 1/6"], [float(at_or_below), float(above)],
                title=f"{label}: Candidate Vote Shares Around One-Sixth", subtitle="Candidates grouped by reported vote share",
                category="Elections", subgroup=field_group, source=source, unit="candidates",
                note=base_note + " Uses each row's reported vote_share_percent and excludes NOTA; one-sixth is a descriptive threshold only, not a determination of deposit forfeiture.",
                explain=("Counts candidates with reported vote share at or below one-sixth versus above one-sixth.", "Shares are taken as published; this descriptive grouping does not establish a candidate's legal deposit status.", "Shows the candidate vote-share distribution for this archived election."),
                frequency=f"State Assembly {year}", color=COLORS[(index + 1) % len(COLORS)], chart_type="doughnut")

        margin_bands = ("Under 1 point", "1–5 points", "5–10 points", "10–20 points", "20+ points")
        margin_counts = Counter()
        for candidates in contests.values():
            valid = [candidate for candidate in candidates if not _is_nota(candidate) and _number(candidate.get("votes")) is not None]
            valid.sort(key=lambda candidate: _number(candidate.get("votes")) or 0, reverse=True)
            total = sum(_number(candidate.get("votes")) or 0 for candidate in valid)
            if len(valid) < 2 or total <= 0:
                continue
            margin = ((_number(valid[0].get("votes")) or 0) - (_number(valid[1].get("votes")) or 0)) / total * 100
            band = "Under 1 point" if margin < 1 else "1–5 points" if margin < 5 else "5–10 points" if margin < 10 else "10–20 points" if margin < 20 else "20+ points"
            margin_counts[band] += 1
        if sum(margin_counts.values()):
            key = f"dg_elections_victory_margins_{year}_{slug}"
            output[key] = _series(key, list(margin_bands), _count_values(margin_counts, list(margin_bands)),
                title=f"{label}: Victory Margin Distribution", subtitle="Contested seats grouped by winner's share lead",
                category="Elections", subgroup=margin_group, source=source, unit="constituencies",
                note=base_note + " Margin is (winner votes minus runner-up votes) divided by listed non-NOTA candidate votes; seats without two reported candidate vote totals are excluded.",
                explain=("Distribution of winning candidates' vote leads over the runner-up by constituency.", "The denominator is the sum of listed non-NOTA candidate votes; values are grouped in percentage-point bands.", "Shows how often archived contests were close or decisive without reusing the 2024/2022–2026 index charts."),
                frequency=f"State Assembly {year}", color=COLORS[(index + 2) % len(COLORS)])
    return output


def _recent_competition_series(payload):
    observations = payload.get("observations", [])
    if not isinstance(observations, list):
        return {}
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for row in observations:
        if not isinstance(row, dict) or _is_nota(row):
            continue
        try:
            year = int(row.get("year"))
        except (TypeError, ValueError):
            continue
        election_type, state = row.get("election_type"), row.get("state_or_ut")
        seat = row.get("constituency_number") or row.get("constituency")
        if not isinstance(election_type, str) or not isinstance(state, str) or seat is None:
            continue
        grouped[(year, election_type)][state][str(seat).strip().casefold()].append(row)
    source = "Election Commission of India candidate results (data/recent-indian-elections.json)"
    output = {}
    for index, ((year, election_type), states) in enumerate(sorted(grouped.items())):
        state_means = []
        for state, contests in states.items():
            effective_numbers = []
            for candidates in contests.values():
                votes = [_number(row.get("votes")) for row in candidates]
                votes = [value for value in votes if value is not None and value > 0]
                total = sum(votes)
                if len(votes) >= 2 and total > 0:
                    effective_numbers.append(1 / sum((value / total) ** 2 for value in votes))
            if effective_numbers:
                state_means.append((state, sum(effective_numbers) / len(effective_numbers)))
        ranked = sorted(state_means, key=lambda item: item[1], reverse=True)
        if not ranked:
            continue
        key = f"dg_elections_effective_candidates_{year}_{re.sub(r'[^a-z0-9]+', '_', election_type.lower()).strip('_')}"
        note = (f"For each state/UT in the {year} {election_type} results, calculates the effective number of candidates in each seat as 1 / sum(candidate vote-share squared), then averages those seat values. "
                "NOTA and seats without at least two candidates with reported votes are excluded. This competition measure is distinct from raw candidate counts in the existing election indices.")
        if year == 2026:
            note += " 2026 assembly reporting is ongoing and incomplete."
        output[key] = _series(key, [state for state, _ in ranked], [value for _, value in ranked],
            title=f"{year} {election_type}: Effective Candidates per Seat by State", subtitle="Mean constituency effective number of candidates",
            category="Elections", subgroup="Recent Effective Candidate Field", source=source, unit="effective candidates",
            note=note,
            explain=("Mean constituency-level effective number of candidates for each state/UT.", "A seat's value is 1 divided by the sum of squared candidate vote shares; larger values indicate votes are spread across more candidates.", "Complements raw candidate-count charts with a vote-weighted measure of electoral competition."),
            frequency=f"{election_type} {year}", color=COLORS[index % len(COLORS)], index_axis="y")
    return output


def _finance_series(payload):
    raw = payload.get("series", {})
    if not isinstance(raw, dict):
        return {}
    cycles = sorted({int(match.group(1)) for key in raw
                     if (match := re.fullmatch(r"us_fec_(\d{4})_[psh]_(?:receipts|disbursements|cash_on_hand|debts_owed)", str(key)))})
    if not cycles:
        return {}
    offices = (("p", "Presidential"), ("s", "Senate"), ("h", "House"))
    metrics = ("receipts", "disbursements", "cash_on_hand", "debts_owed")
    metric_titles = {"receipts": "Receipts", "disbursements": "Disbursements", "cash_on_hand": "Cash on Hand", "debts_owed": "Debts Owed"}
    source = "Federal Election Commission candidate summary bulk files (data/us-campaign-finance.json)"
    output = {}

    def total(cycle, office, metric):
        record = raw.get(f"us_fec_{cycle}_{office}_{metric}")
        if not isinstance(record, dict):
            return None
        labels, values = record.get("labels", []), record.get("values", [])
        if not isinstance(labels, list) or not isinstance(values, list) or len(labels) != len(values):
            return None
        numbers = [_number(value) for value in values]
        numbers = [value for value in numbers if value is not None]
        return sum(numbers) if numbers else None

    for office, office_name in offices:
        for metric in metrics:
            entries = [(cycle, total(cycle, office, metric)) for cycle in cycles]
            valid = [(cycle, value) for cycle, value in entries if value is not None]
            if len(valid) < 2:
                continue
            labels = [str(cycle) for cycle, _ in valid]
            values = [float(value) for _, value in valid]
            subgroup = "Cycle-over-Cycle Finance Trends"
            key = f"dg_us_finance_{office}_{metric}_by_cycle"
            caveat = "Nominal amounts are not inflation-adjusted; cycle length and candidate coverage differ."
            if valid[-1][0] == 2026:
                caveat += " The 2026 election cycle is ongoing and reporting is incomplete."
            output[key] = _series(key, labels, values,
                title=f"{office_name} Campaign {metric_titles[metric]} by FEC Cycle",
                subtitle=f"Sum of listed candidate/state aggregates for {office_name.lower()} office",
                category="U.S. Elections", subgroup=subgroup, source=source, unit="USD",
                note=f"For each cycle, sums the values in the committed FEC {office_name.lower()} {metric} series. {caveat}",
                explain=(f"Total listed {metric_titles[metric].lower()} for {office_name} candidate summaries in each FEC cycle.", "Compare displayed nominal totals only; candidate/state coverage and election type differ between cycles.", "Shows the scale and direction of campaign-finance aggregates across the available FEC cycles."),
                frequency="FEC election cycle", color=COLORS[len(output) % len(COLORS)])
            growth = []
            for (prev_cycle, prev), (cycle, current) in zip(valid, valid[1:]):
                if prev is not None and current is not None and prev > 0:
                    change = (current / prev - 1) * 100
                    if math.isfinite(change):
                        growth.append((f"{prev_cycle}–{cycle}", change))
            if growth:
                key = f"dg_us_finance_{office}_{metric}_growth"
                output[key] = _series(key, [label for label, _ in growth], [value for _, value in growth],
                    title=f"{office_name} Campaign {metric_titles[metric]} Cycle Growth",
                    subtitle="Nominal percentage change between adjacent available FEC cycles",
                    category="U.S. Elections", subgroup=subgroup, source=source, unit="% change",
                    note="Calculated as (later cycle total / prior available cycle total − 1) × 100. No inflation adjustment is applied; cycles differ in coverage and duration, and a zero or missing baseline is omitted.",
                    explain=("Percentage change in the listed nominal aggregate between adjacent FEC cycles.", "Positive values indicate a higher later-cycle total; negative values indicate a lower total.", "Provides a relative comparison alongside nominal dollar totals."),
                    frequency="Adjacent FEC cycles", color=COLORS[len(output) % len(COLORS)])

    # Senate/House records are state aggregates; Presidential records are committee labels.
    for office, office_name in (("s", "Senate"), ("h", "House")):
        for metric in metrics:
            for cycle in cycles:
                record = raw.get(f"us_fec_{cycle}_{office}_{metric}")
                if not isinstance(record, dict):
                    continue
                labels, values = record.get("labels", []), record.get("values", [])
                if not isinstance(labels, list) or not isinstance(values, list) or len(labels) != len(values):
                    continue
                rows = [(str(label), _number(value)) for label, value in zip(labels, values)]
                ranked = sorted(((label, value) for label, value in rows if value is not None), key=lambda row: row[1], reverse=True)[:15]
                if len(ranked) < 6:
                    continue
                key = f"dg_us_state_{office}_{metric}_{cycle}"
                note = f"Ranks the 15 largest state/territory aggregate values in the FEC {cycle} {office_name.lower()} {metric} series. Amounts are nominal and inherit that cycle's reporting coverage."
                if cycle == 2026:
                    note += " 2026 is ongoing and coverage is incomplete."
                output[key] = _series(key, [label for label, _ in ranked], [float(value) for _, value in ranked],
                    title=f"{cycle} {office_name} Campaign {metric_titles[metric]} by State",
                    subtitle="Top state aggregates in the FEC cycle data", category="U.S. Elections",
                    subgroup="State Finance Rankings", source=source, unit="USD", note=note,
                    explain=(f"Top state/territory totals for {office_name.lower()} campaign {metric_titles[metric].lower()} in this FEC cycle.", "States are sorted from the largest to smallest listed aggregate; only the 15 largest are shown.", "Highlights the geographic distribution of campaign-finance totals in this cycle."),
                    frequency=f"FEC cycle {cycle}", color=COLORS[cycle % len(COLORS)], index_axis="y")
    return output


def build_derived_groups_layer(root: Path) -> dict[str, dict]:
    """Return new series derived only from JSON already present under root/data."""
    root = Path(root)
    result = {}
    reports = _read_json(root, "pew-india-reports.json")
    if reports:
        result.update(_publication_series(reports))
        result.update(_theme_series(reports))
    snapshots = _read_json(root, "pew-snapshots.json")
    if snapshots:
        result.update(_snapshot_series(snapshots))
    recent = _read_json(root, "recent-indian-elections.json")
    if recent:
        result.update(_recent_competition_series(recent))
    historical = _read_json(root, "historical-elections.json")
    if historical:
        result.update(_election_series(historical))
    finance = _read_json(root, "us-campaign-finance.json")
    if finance:
        result.update(_finance_series(finance))
    return result


if __name__ == "__main__":
    from collections import Counter

    series = build_derived_groups_layer(Path(__file__).resolve().parents[1])
    counts = Counter((item["meta"]["category"], item["meta"]["subgroup"]) for item in series.values())
    for category, subgroups in NEW_SUBGROUPS.items():
        print(category)
        for subgroup in subgroups:
            print(f"  {subgroup}: {counts[(category, subgroup)]}")
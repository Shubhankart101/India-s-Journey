"""Build official NJDG charts for the Judiciary & Pending Cases group."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

CATEGORY = "Judiciary & Pending Cases"
SUBGROUPS = {
    "supreme_court": "Supreme Court",
    "high_courts": "High Courts",
    "lower_courts": "Lower Courts",
}
COLORS = ("#ff9933", "#58a6ff", "#3fb950", "#bc8cff", "#f6c344", "#f778ba", "#39c5bb")
CASE_TYPES = {"1": "Total cases", "2": "Civil cases", "3": "Criminal cases"}
FLAG_TITLES = {
    "ins": "Cases Instituted in the Last Month",
    "disp": "Cases Disposed in the Last Month",
    "citizen": "Cases Filed by Senior Citizens",
    "women": "Cases Filed by Women",
    "delay": "Delayed Cases",
    "insCurr": "Cases Instituted This Year",
    "dispCurr": "Cases Disposed This Year",
}
DASHBOARD_TABLES = (
    ("casecount", "case_types", "Case-type breakdown", "Case counts by case type"),
    ("caseChartcount", "case_groups", "Case-category breakdown", "Case counts by broad case category"),
    ("ageChartcount", "pending_age", "Pending-case age profile", "Pending cases by age bucket"),
    ("stagewiseCount", "case_stage", "Cases by listed stage", "Cases by the stage recorded in NJDG"),
    ("agewiseCount", "filing_year", "Cases by filing year", "Cases grouped by filing year"),
)


def _read_snapshot(root: Path) -> dict[str, Any]:
    path = root / "data" / "legal" / "njdg_snapshot.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return text or "series"


def _numbers(values: list[Any]) -> list[float | int]:
    result: list[float | int] = []
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            result.append(value)
        elif isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            try:
                number = float(cleaned)
            except ValueError:
                continue
            result.append(int(number) if number.is_integer() else number)
    return result


def _table_pairs(table: Any) -> tuple[list[str], list[float | int]]:
    if not isinstance(table, list) or len(table) < 2:
        return [], []
    labels: list[str] = []
    values: list[float | int] = []
    for row in table[1:]:
        if not isinstance(row, list) or len(row) < 2:
            continue
        label = str(row[0]).strip()
        if not label or label.lower().startswith("total"):
            continue
        numeric = _numbers([row[-1]])
        if not numeric or numeric[0] <= 0:
            continue
        labels.append(label)
        values.append(numeric[0])
    if not any(values):
        return [], []
    return labels, values


def _array_pairs(data: dict[str, Any], labels_key: str, values_key: str) -> tuple[list[str], list[float | int]]:
    arrays = data.get("arrays", {}) if isinstance(data, dict) else {}
    labels_raw = arrays.get(labels_key, [])
    values_raw = arrays.get(values_key, [])
    if not isinstance(labels_raw, list) or not isinstance(values_raw, list):
        return [], []
    labels: list[str] = []
    values: list[float | int] = []
    for label, value in zip(labels_raw, values_raw):
        numeric = _numbers([value])
        text = str(label).strip() if label is not None else ""
        if text and numeric and numeric[0] > 0:
            labels.append(text)
            values.append(numeric[0])
    return labels, values


def _meta(title: str, subtitle: str, subgroup: str, unit: str, explain: tuple[str, str, str], color: str) -> dict[str, Any]:
    return {
        "title": title,
        "subtitle": subtitle,
        "frequency": "NJDG dashboard snapshot",
        "color": color,
        "suffix": f" {unit}" if unit else "",
        "category": CATEGORY,
        "subgroup": subgroup,
        "explain": {"what": explain[0], "read": explain[1], "why": explain[2]},
    }


def _add_series(
    output: dict[str, dict[str, Any]], key: str, labels: list[str], values: list[float | int] | None,
    *, title: str, subtitle: str, subgroup: str, source: str, unit: str, note: str,
    explain: tuple[str, str, str], scope: str, chart_type: str = "bar",
    datasets: list[dict[str, Any]] | None = None, color_index: int = 0,
) -> None:
    labels = [str(label) for label in labels]
    if not labels:
        return
    if datasets is None and (not values or len(values) != len(labels)):
        return
    if datasets is not None and (not datasets or any(len(item.get("values", [])) != len(labels) for item in datasets)):
        return
    item: dict[str, Any] = {
        "labels": labels,
        "chartType": chart_type,
        "scope": scope,
        "source": source,
        "unit": unit,
        "note": note,
        "meta": _meta(title, subtitle, subgroup, unit, explain, COLORS[color_index % len(COLORS)]),
    }
    if datasets is None:
        item["values"] = values
    else:
        item["datasets"] = datasets
    output[key] = item


def _scope_title(name: str, is_national: bool) -> tuple[str, str]:
    if is_national:
        return "India", "national"
    return name, f"jurisdiction:{name}"


def _add_dashboard_series(
    output: dict[str, dict[str, Any]], dashboard: dict[str, Any], *, portal: str,
    portal_url: str, subgroup: str, subgroup_key: str, scope_name: str,
    scope_slug: str, ci_cri: str, tab: str, year: str | None,
    is_national: bool,
) -> None:
    scope_label, scope = _scope_title(scope_name, is_national)
    case_label = CASE_TYPES.get(ci_cri, "Cases")
    selector = f"{scope_slug}_ci{ci_cri}_{tab}" + (f"_{year}" if year else "")
    source_base = f"National Judicial Data Grid (NJDG), {portal_url}"
    source_action = f"{source_base} (home/newPendDashboard; {case_label.lower()}, {tab}" + (f", year {year}" if year else "") + ")"
    tables = dashboard.get("tables", {}) if isinstance(dashboard, dict) else {}
    for index, (table_key, metric_key, display, explanation) in enumerate(DASHBOARD_TABLES):
        labels, values = _table_pairs(tables.get(table_key))
        if not labels:
            continue
        if metric_key == "pending_age" and tab == "disposed":
            title = f"{scope_label}: {case_label} disposed in {year} by case age"
            what = f"Shows how old {scope_label.lower()} {case_label.lower()} were when disposed in {year}."
            read = "Age buckets are the categories published in the NJDG dashboard; longer-age buckets indicate older cases at disposal."
            why = "Disposal age helps distinguish recent work from the backlog of older pending cases."
        elif metric_key == "pending_age":
            title = f"{scope_label}: {case_label} pending by age"
            what = f"Shows the age profile of pending {scope_label.lower()} {case_label.lower()}."
            read = "Each bar is an NJDG age bucket; compare the bucket counts to see where pending cases are concentrated."
            why = "Older pending cases identify where delay-reduction efforts may be most urgent."
        elif metric_key == "filing_year":
            title = f"{scope_label}: {case_label} by filing year" + (f" (disposed in {year})" if tab == "disposed" else " pending")
            what = f"Shows {scope_label.lower()} {case_label.lower()} grouped by year of filing."
            read = "The horizontal axis is the filing year and the bar height is the reported case count."
            why = "Filing-year patterns make long-running backlogs visible."
        else:
            title = f"{scope_label}: {case_label} {display.lower()}" + (f" (disposed in {year})" if tab == "disposed" else " pending")
            what = f"Shows {scope_label.lower()} {case_label.lower()} across NJDG's {display.lower()} categories."
            read = "Each category comes from the source dashboard; larger bars represent more cases in that category."
            why = f"This view helps identify which {display.lower()} categories account for the reported docket."
        key = f"jud_{subgroup_key}_{selector}_{metric_key}"
        _add_series(
            output, key, labels, values, title=title,
            subtitle=f"{explanation} for {scope_label}; case classification: {case_label}.",
            subgroup=subgroup, source=source_action, unit="cases",
            note=(f"Official NJDG {tab} dashboard response. Counts are shown as published and are not estimates."),
            explain=(what, read, why), scope=scope, chart_type="doughnut" if len(labels) <= 8 and metric_key in {"pending_age", "case_groups"} else "bar",
            color_index=index + int(ci_cri),
        )

    arrays = dashboard.get("arrays", {}) if isinstance(dashboard, dict) else {}
    if tab == "disposed":
        pairs = (
            ("dispYear", "dispCount", "disposal_time", "Disposal time", "cases", "doughnut"),
            ("subNatureName", "subNatureCount", "disposal_nature", "Disposal outcome", "cases", "doughnut"),
            ("delayName", "delay_count", "delay_reason", "Delay reason", "cases", "bar"),
        )
        for index, (labels_key, values_key, metric, title_part, unit, chart_type) in enumerate(pairs):
            labels, values = _array_pairs(dashboard, labels_key, values_key)
            if not labels:
                continue
            title = f"{scope_label}: {case_label} disposed in {year} by {title_part.lower()}"
            _add_series(
                output, f"jud_{subgroup_key}_{selector}_{metric}", labels, values,
                title=title, subtitle=f"Reported {title_part.lower()} categories for disposed {case_label.lower()}.",
                subgroup=subgroup, source=source_action, unit=unit,
                note="Categories and counts are reported by the NJDG disposed-case dashboard.",
                explain=(
                    f"Shows the reported {title_part.lower()} breakdown for {scope_label.lower()} {case_label.lower()} disposed in {year}.",
                    "Compare categories within this selected year; values are counts, not percentages.",
                    f"The distribution adds context to {scope_label.lower()}'s {case_label.lower()} disposal profile.",
                ), scope=scope, chart_type=chart_type, color_index=4 + index + int(ci_cri),
            )
    elif tab == "pending":
        labels = arrays.get("insyear", [])
        institutions = _numbers(arrays.get("ins_count", []))
        disposals = _numbers(arrays.get("disp_count", []))
        if (
            isinstance(labels, list) and len(labels) == len(institutions) == len(disposals)
            and len(labels) >= 3 and all(re.fullmatch(r"\d{4}", str(label)) for label in labels)
        ):
            datasets = [
                {"label": "Instituted", "values": institutions, "color": COLORS[0]},
                {"label": "Disposed", "values": disposals, "color": COLORS[1]},
            ]
            title = f"{scope_label}: annual {case_label.lower()} institutions and disposals"
            _add_series(
                output, f"jud_{subgroup_key}_{selector}_institution_vs_disposal", [str(label) for label in labels], None,
                title=title, subtitle=f"Year-wise institution and disposal counts reported for {scope_label}.",
                subgroup=subgroup, source=f"{source_base} (home/newPendDashboard)", unit="cases",
                note="Annual counts are published by NJDG; the latest calendar year may be incomplete.",
                explain=(
                    f"Compares annual {case_label.lower()} institutions with disposals in {scope_label.lower()}.",
                    "Each line is a separate reported count; compare their positions within the same year.",
                    "The comparison shows whether disposals have kept pace with new filings over the published years.",
                ), scope=scope, chart_type="line", datasets=datasets, color_index=1 + int(ci_cri),
            )


def _state_rows(data: dict[str, Any], ci_cri: str) -> tuple[list[str], list[float | int]]:
    tables = data.get("tables", {}) if isinstance(data, dict) else {}
    table = tables.get("tbl_str")
    if not isinstance(table, list) or len(table) < 2:
        return [], []
    header = [str(cell).strip().lower() for cell in table[0]]
    target = {"1": "total", "2": "civil", "3": "criminal"}.get(ci_cri, "total")
    value_index = next((index for index, cell in enumerate(header) if target in cell), None)
    label_index = next((index for index, cell in enumerate(header) if any(word in cell for word in ("state", "court", "name"))), None)
    if label_index is None:
        label_index = 1 if len(header) > 1 else 0
    if value_index is None:
        value_index = min(len(header) - 1, {"1": 4, "2": 2, "3": 3}.get(ci_cri, 4))
    labels: list[str] = []
    values: list[float | int] = []
    for row in table[1:]:
        if len(row) <= max(label_index, value_index):
            continue
        label = str(row[label_index]).strip()
        if not label or label.lower().startswith("total") or label.isdigit():
            continue
        value = _numbers([row[value_index]])
        if value and value[0] > 0:
            labels.append(label)
            values.append(value[0])
    return labels, values


def _add_state_metrics(output: dict[str, dict[str, Any]], portal_data: dict[str, Any], *, portal: str,
                       portal_url: str, subgroup: str, subgroup_key: str) -> None:
    state_metrics = portal_data.get("state_metrics", {})
    if not isinstance(state_metrics, dict):
        return
    for flag, flag_title in FLAG_TITLES.items():
        for ci_cri, case_label in CASE_TYPES.items():
            raw = state_metrics.get(f"{flag}:{ci_cri}") or state_metrics.get(f"{flag}:1", {})
            labels, values = _state_rows(raw, ci_cri)
            if len(labels) < 2:
                continue
            order = sorted(range(len(values)), key=lambda index: values[index], reverse=True)
            top = order[:15]
            rank_labels = [labels[index] for index in top]
            rank_values = [values[index] for index in top]
            title = f"Top jurisdictions by {flag_title.lower()} - {case_label}"
            key = f"jud_{subgroup_key}_rank_{flag.lower()}_ci{ci_cri}"
            _add_series(
                output, key, rank_labels, rank_values, title=title,
                subtitle=f"Highest reported {flag_title.lower()} counts across {subgroup.lower()} jurisdictions.",
                subgroup=subgroup, source=f"National Judicial Data Grid (NJDG), {portal_url} (home/fetchStateData; flag={flag}, ci_cri={ci_cri})",
                unit="cases", note="Ranks the jurisdiction rows returned by NJDG; it does not adjust for population or court size.",
                explain=(
                    f"Ranks {subgroup.lower()} jurisdictions by the NJDG-reported count of {flag_title.lower()} ({case_label.lower()}).",
                    "Read the bars from largest to smallest; only the 15 highest reported jurisdiction counts are shown.",
                    "The ranking helps locate where this part of the docket is concentrated.",
                ), scope="jurisdiction ranking", chart_type="bar", color_index=int(ci_cri),
            )
            top_share = order[:9]
            share_labels = [labels[index] for index in top_share]
            share_values = [values[index] for index in top_share]
            remainder = sum(values[index] for index in order[9:])
            if remainder > 0:
                share_labels.append("All other jurisdictions")
                share_values.append(remainder)
            share_title = f"Share of {flag_title.lower()} by leading jurisdictions - {case_label}"
            _add_series(
                output, f"jud_{subgroup_key}_share_{flag.lower()}_ci{ci_cri}", share_labels, share_values,
                title=share_title, subtitle=f"Reported jurisdiction shares of {flag_title.lower()} across {subgroup.lower()}.",
                subgroup=subgroup, source=f"National Judicial Data Grid (NJDG), {portal_url} (home/fetchStateData; flag={flag}, ci_cri={ci_cri})",
                unit="cases", note="The chart shows counts grouped by jurisdiction, not a population-adjusted rate.",
                explain=(
                    f"Shows how the reported {flag_title.lower()} count ({case_label.lower()}) is distributed among leading {subgroup.lower()} jurisdictions.",
                    "The largest nine jurisdictions are shown separately; remaining reported rows are combined as other jurisdictions.",
                    "A share view makes concentration across the national court network easier to compare.",
                ), scope="jurisdiction share", chart_type="doughnut", color_index=5 + int(ci_cri),
            )


def _add_monthly_series(output: dict[str, dict[str, Any]], data: dict[str, Any], *, portal_url: str,
                        subgroup: str, subgroup_key: str, ci_cri: str) -> None:
    arrays = data.get("arrays", {}) if isinstance(data, dict) else {}
    labels = arrays.get("insyear", [])
    institutions = _numbers(arrays.get("ins_count", []))
    disposals = _numbers(arrays.get("disp_count", []))
    if not isinstance(labels, list) or len(labels) != len(institutions) or len(labels) != len(disposals) or not labels:
        return
    labels = [str(label) for label in labels]
    title = f"Monthly institutions and disposals - {CASE_TYPES[ci_cri]}"
    _add_series(
        output, f"jud_{subgroup_key}_monthly_institution_vs_disposal_ci{ci_cri}", labels, None,
        title=title, subtitle=f"Month-by-month filing and disposal counts published by the NJDG portal.",
        subgroup=subgroup, source=f"National Judicial Data Grid (NJDG), {portal_url} (home/updateInstitutionDisp)",
        unit="cases", note="The selected calendar year's latest month may be incomplete.",
        explain=(
            f"Compares monthly {CASE_TYPES[ci_cri].lower()} institutions and disposals for the selected year.",
            "The two lines are separate portal-reported counts; the final month can be partial.",
            "Monthly comparison shows how filings and disposals move through the year.",
        ), scope="national", chart_type="line", datasets=[
            {"label": "Instituted", "values": institutions, "color": COLORS[0]},
            {"label": "Disposed", "values": disposals, "color": COLORS[1]},
        ], color_index=int(ci_cri),
    )


def build_legal_layer(root: Path) -> dict[str, dict]:
    """Return NJDG chart series keyed with ``jud_`` identifiers."""
    snapshot = _read_snapshot(Path(root))
    courts = snapshot.get("courts", {})
    output: dict[str, dict[str, Any]] = {}
    for subgroup_key, subgroup in SUBGROUPS.items():
        portal_data = courts.get(subgroup_key, {})
        if not isinstance(portal_data, dict) or not portal_data.get("available"):
            continue
        portal_url = str(snapshot.get("source_urls", {}).get(subgroup_key) or portal_data.get("source_url", ""))
        portal = "Supreme Court NJDG" if subgroup_key == "supreme_court" else (
            "High Courts NJDG" if subgroup_key == "high_courts" else "District and subordinate courts NJDG"
        )
        _add_state_metrics(
            output, portal_data, portal=portal, portal_url=portal_url,
            subgroup=subgroup, subgroup_key=subgroup_key,
        )
        if subgroup_key == "supreme_court":
            landing = portal_data.get("landing_metrics", {})
            civil = _numbers([landing.get("Pending Civil Cases")])
            criminal = _numbers([landing.get("Pending Criminal Cases")])
            if civil and criminal:
                _add_series(
                    output, "jud_supreme_court_pending_case_mix", ["Civil", "Criminal"],
                    [civil[0], criminal[0]],
                    title="Supreme Court: civil and criminal pending-case mix",
                    subtitle="Pending cases by the case-class totals displayed on the Supreme Court NJDG landing page.",
                    subgroup=subgroup, source=f"National Judicial Data Grid (NJDG), {portal_url} (landing-page pending totals)",
                    unit="cases", note="Uses the portal's reported civil and criminal pending totals; no estimate is added.",
                    explain=(
                        "Compares the Supreme Court's reported pending civil and criminal case totals.",
                        "Each segment is a case count; the chart excludes the overall total so parts are not counted twice.",
                        "The mix shows how the pending docket is divided between the two case classes.",
                    ), scope="national", chart_type="doughnut", color_index=0,
                )
        dashboards = portal_data.get("national_dashboards", {})
        if isinstance(dashboards, dict):
            for dashboard_key, dashboard in dashboards.items():
                parts = dashboard_key.split(":")
                ci_cri = parts[0]
                tab = parts[1] if len(parts) > 1 else "pending"
                year = parts[2] if len(parts) > 2 else None
                if ci_cri not in CASE_TYPES or not isinstance(dashboard, dict):
                    continue
                selector = f"national_ci{ci_cri}_{tab}" + (f"_{year}" if year else "")
                _add_dashboard_series(
                    output, dashboard, portal=portal, portal_url=portal_url,
                    subgroup=subgroup, subgroup_key=subgroup_key, scope_name="India",
                    scope_slug="national", ci_cri=ci_cri, tab=tab, year=year,
                    is_national=True,
                )
        for ci_cri, data in portal_data.get("institution_disposal", {}).items():
            if ci_cri in CASE_TYPES and isinstance(data, dict):
                _add_monthly_series(output, data, portal_url=portal_url, subgroup=subgroup,
                                    subgroup_key=subgroup_key, ci_cri=ci_cri)
        jurisdictions = portal_data.get("jurisdictions", [])
        if isinstance(jurisdictions, list):
            for jurisdiction in jurisdictions:
                if not isinstance(jurisdiction, dict):
                    continue
                name = str(jurisdiction.get("name", "")).strip()
                if not name:
                    continue
                for ci_cri, dashboard in jurisdiction.get("dashboards", {}).items():
                    if ci_cri not in CASE_TYPES or not isinstance(dashboard, dict):
                        continue
                    _add_dashboard_series(
                        output, dashboard, portal=portal, portal_url=portal_url,
                        subgroup=subgroup, subgroup_key=subgroup_key, scope_name=name,
                        scope_slug=_slug(name), ci_cri=ci_cri, tab="pending", year=None,
                        is_national=False,
                    )
    return output



def merge_chart_files(root: Path) -> int:
    """Merge this layer into both generated chart JSONs without running the network-heavy builder."""
    root = Path(root)
    additions = build_legal_layer(root)
    if not additions:
        raise RuntimeError("No Judiciary & Pending Cases series were built from data/legal/njdg_snapshot.json")
    paths = (root / "data" / "chart-latest.json", root / "docs" / "data" / "chart-latest.json")
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("series"), dict):
            raise ValueError(f"Invalid generated chart payload: {path}")
        payload["series"] = {key: value for key, value in payload["series"].items() if not key.startswith("jud_")}
        payload["series"].update(additions)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "docs" / "data.js").write_text(f"window.INDIA_DASHBOARD_DATA = {json.dumps(payload, indent=2)};\n", encoding="utf-8")
    return len(additions)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build judiciary charts from a committed NJDG snapshot")
    parser.add_argument("--merge", action="store_true", help="merge into data/chart-latest.json and docs/data/chart-latest.json")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    if not args.merge:
        parser.error("pass --merge to update the generated chart JSON files")
    count = merge_chart_files(args.root.resolve())
    print(f"Merged {count} NJDG series into both generated chart JSON files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

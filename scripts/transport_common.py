"""Shared builders for the Air Travel and Indian Railways layers.

Every builder returns a ``(key, series)`` pair shaped like the other layers: ``labels`` plus ``values`` or
``datasets``, a ``source`` link, a ``note`` and ``meta`` so the dashboard registers the chart without a
hand-written definition.
"""
from __future__ import annotations

from typing import Callable, Iterable

PALETTE = ("#ff9933", "#58a6ff", "#3fb950", "#bc8cff", "#ff7b72", "#f6c344", "#39c5bb", "#f778ba")
WB_PAGE = "https://data.worldbank.org/indicator/{code}?locations=IN"


def wb_url(countries: Iterable[str], code: str, first: int = 1990, last: int = 2025) -> str:
    return (f"https://api.worldbank.org/v2/country/{';'.join(countries)}/indicator/{code}"
            f"?format=json&per_page=5000&date={first}:{last}")


def wb_observations(get_json: Callable[[str], object], countries: Iterable[str], code: str) -> dict[str, dict[str, float]]:
    countries = tuple(countries)
    payload = get_json(wb_url(countries, code))
    if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
        raise ValueError(f"World Bank returned no observations for {code}")
    observed: dict[str, dict[str, float]] = {}
    for row in payload[1]:
        if row.get("value") is not None and row.get("countryiso3code") in countries:
            observed.setdefault(row["countryiso3code"], {})[row["date"]] = float(row["value"])
    return observed


def meta(category: str, subgroup: str, title: str, subtitle: str, suffix: str, color: str = "#ff9933",
         frequency: str = "Annual", what: str = "", read: str = "", why: str = "") -> dict:
    result = {"title": title, "subtitle": subtitle, "frequency": frequency, "color": color, "suffix": suffix,
              "category": category, "subgroup": subgroup}
    explain = {k: v for k, v in (("what", what), ("read", read), ("why", why)) if v}
    if explain:
        result["explain"] = explain
    return result


def _finish(series: dict, chart: str | None, horizontal: bool) -> dict:
    if chart == "doughnut":
        series.update(chartType="doughnut", scope="category")
    elif chart == "bar":
        series.update(chartType="bar", scope="category")
        if horizontal:
            series["indexAxis"] = "y"
    return series


def single(key, labels, values, *, source, unit, note, meta_, chart=None, horizontal=False):
    """One series: a line by default, or a bar / doughnut."""
    if len(labels) != len(values) or len(labels) < 2:
        raise ValueError(f"{key}: need matching labels and values")
    series = {"labels": [str(label) for label in labels], "values": list(values), "source": source,
              "unit": unit.strip(), "note": note, "meta": meta_}
    return key, _finish(series, chart, horizontal)


def multi(key, labels, datasets, *, source, unit, note, meta_, chart=None):
    """Several datasets over shared labels: a multi-line chart, or grouped bars with chart="bar"."""
    if not datasets or any(len(d["values"]) != len(labels) for d in datasets):
        raise ValueError(f"{key}: every dataset must match the labels")
    colored = [{**d, "color": d.get("color") or PALETTE[i % len(PALETTE)]} for i, d in enumerate(datasets)]
    series = {"labels": [str(label) for label in labels], "datasets": colored, "source": source,
              "unit": unit.strip(), "note": note, "meta": meta_}
    return key, _finish(series, chart, False)


def ranked(key, points: dict[str, float], *, source, unit, note, meta_, chart="bar", top=None):
    ordered = sorted(points.items(), key=lambda item: -item[1])
    if top:
        ordered = ordered[:top]
    return single(key, [name for name, _ in ordered], [round(value, 2) for _, value in ordered],
                  source=source, unit=unit, note=note, meta_=meta_, chart=chart, horizontal=chart == "bar")


def with_fallback(builders: dict[str, Callable[[], tuple[str, dict]]], previous: dict[str, dict]) -> dict[str, dict]:
    """Run each builder; if one fails, keep the last good series instead of dropping the chart."""
    result: dict[str, dict] = {}
    for key, build in builders.items():
        try:
            built_key, series = build()
            result[built_key] = series
        except Exception:
            old = previous.get(key)
            if old and (old.get("values") or old.get("datasets")):
                result[key] = old
    return result

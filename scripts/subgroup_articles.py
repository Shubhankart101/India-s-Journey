"""Long-form article sections for every subgroup, written from each indicator's own published values.

Each section introduces 1-5 charts (referenced by indicator key) and a short narrative composed from the
first and latest observations, the leaders of a ranking, or the shares of a breakdown. No text is copied
from sources; every figure comes from data/catalog.json.
"""
import math
import re

MAX_CHARTS_PER_SECTION = 5
MIN_SECTIONS = 3
MAX_SECTIONS = 6
MAP_MIN_INDICATORS = 3
PLAIN_TYPES = {"line", "bar", "doughnut", "pie", "map"}
STOP_SUFFIX = re.compile(r"\s*[\u2014\u2013-]\s*map$", re.I)
CORRUPTION = re.compile("\ufffd|\u00c3|\u00e2\u20ac|\u00ef\u00bf|\\?\\?|\u00c2")

TITLES = (
    "{stem}: the headline view",
    "{stem} and its neighbours",
    "Reading {stem} in context",
    "{stem}: a closer look",
    "More on {stem}",
    "{stem}: the wider picture",
)
READING_TIPS = {
    "line": "Hover along the line to read each period's value; the axis shows the unit.",
    "bar": "Bars follow the published order; hover a bar for its exact figure.",
    "doughnut": "Slices are shares of one total, with the smallest folded into Other.",
    "pie": "Slices are shares of one total, with the smallest folded into Other.",
    "map": "Shading marks quintiles of States and Union Territories; the bars show the leaders.",
    "special": "This view is interactive: use its own controls to change the period, place or layer.",
}


def clean(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def stem_of(title):
    text = STOP_SUFFIX.sub("", clean(title))
    text = re.split(r"\s+[\u2014\u2013]\s+|:\s|\s\(", text, maxsplit=1)[0].strip(" -:,")
    if len(text) > 52:
        text = text[:52].rsplit(" ", 1)[0].rstrip(" ,-:&")
    return text or clean(title)[:52]


def chart_type_of(indicator):
    return (indicator.get("series") or {}).get("chart_type") or "line"


def numeric_points(indicator):
    series = indicator.get("series") or {}
    labels = [str(label) for label in series.get("labels") or []]
    datasets = series.get("datasets") or []
    values = datasets[0].get("values") if datasets else []
    points = []
    for index, label in enumerate(labels):
        value = values[index] if index < len(values) else None
        if isinstance(value, bool) or value is None:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(number):
            points.append((label, number))
    return points


def fmt(value, suffix=""):
    magnitude = abs(value)
    if magnitude >= 1e12:
        number = f"{value / 1e12:.2f}".rstrip("0").rstrip(".") + " trillion"
    elif magnitude >= 1e9:
        number = f"{value / 1e9:.2f}".rstrip("0").rstrip(".") + " billion"
    elif magnitude >= 1e7:
        number = f"{value / 1e6:.1f}".rstrip("0").rstrip(".") + " million"
    elif magnitude >= 100:
        number = f"{value:,.0f}"
    else:
        number = f"{value:.2f}".rstrip("0").rstrip(".")
    unit = clean(suffix)
    if not unit:
        return number
    if unit[0] in "\u20b9$\u20ac\u00a3":
        rest = unit[1:].strip()
        return f"{unit[0]}{number}" + (f" {rest}" if rest else "")
    return f"{number}{unit}" if unit.startswith("%") else f"{number} {unit}"


def fact_for(indicator):
    """Returns (sentence, weight); weight ranks how striking the sentence is for the pull quote."""
    stem = stem_of(indicator.get("title", ""))
    suffix = indicator.get("suffix", "")
    kind = chart_type_of(indicator)
    points = numeric_points(indicator)
    if not points or kind not in PLAIN_TYPES:
        return "", 0.0
    timeline = len(points) >= 3 and re.match(r"^(19|20)\d{2}", points[0][0]) and kind in {"line", "bar"}
    if timeline:
        (first_label, first), (last_label, last) = points[0], points[-1]
        peak_label, peak = max(points, key=lambda item: item[1])
        if first and abs(first) > 1e-9:
            change = (last - first) / abs(first) * 100
            verb = "rose" if change >= 0 else "fell"
            if clean(suffix).startswith("%"):
                span = f"a shift of {abs(last - first):.2f}".rstrip("0").rstrip(".") + " percentage points"
            else:
                span = f"a change of {abs(change):,.0f}%"
            sentence = f"{stem} {verb} from {fmt(first, suffix)} in {first_label} to {fmt(last, suffix)} in {last_label}, {span}."
            weight = min(abs(change), 5000.0)
        else:
            sentence = f"{stem} stood at {fmt(first, suffix)} in {first_label} and {fmt(last, suffix)} in {last_label}."
            weight = 1.0
        if peak_label not in (first_label, last_label):
            sentence += f" Its high point was {fmt(peak, suffix)} in {peak_label}."
        return sentence, weight
    ranked = sorted(points, key=lambda item: item[1], reverse=True)
    if len(ranked) == 1:
        return f"{stem} is {fmt(ranked[0][1], suffix)} ({ranked[0][0]}).", 1.0
    lead, second, bottom = ranked[0], ranked[1], ranked[-1]
    total = sum(value for _, value in ranked if value > 0)
    sentence = f"In {stem}, {lead[0]} leads at {fmt(lead[1], suffix)}, ahead of {second[0]} at {fmt(second[1], suffix)}"
    if kind in {"doughnut", "pie"} and total > 0 and lead[1] > 0:
        sentence += f", and holds {lead[1] / total * 100:.0f}% of the total"
    elif len(ranked) > 3 and bottom[0] not in (lead[0], second[0]):
        sentence += f"; {bottom[0]} is lowest at {fmt(bottom[1], suffix)}"
    return sentence + ".", 2.0 + (lead[1] / ranked[-1][1] if ranked[-1][1] > 0 else 0)


def pick_charts(live, limit):
    if len(live) <= limit:
        return list(live)
    special = [item for item in live if chart_type_of(item) not in PLAIN_TYPES][:limit]
    rest = [item for item in live if item not in special]
    slots = max(0, limit - len(special))
    chosen = [rest[round(i * (len(rest) - 1) / max(slots - 1, 1))] for i in range(slots)] if slots else []
    keep = {item["key"] for item in special + chosen}
    return [item for item in live if item["key"] in keep]


def chunk(items, count):
    base, extra = divmod(len(items), count)
    parts, start = [], 0
    for index in range(count):
        size = base + (1 if index < extra else 0)
        parts.append(items[start:start + size])
        start += size
    return parts


def has_values(indicator):
    return bool(numeric_points(indicator)) or chart_type_of(indicator) not in PLAIN_TYPES


def join_names(names):
    names = [name for name in names if name]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


def dedupe(values):
    seen, result = set(), []
    for value in values:
        if value.lower() not in seen:
            seen.add(value.lower())
            result.append(value)
    return result


def build_subgroup_article(name, description, indicators, intro="", publishers=()):
    ordered = sorted(indicators, key=lambda item: int(item.get("position") or 0))
    live = [item for item in ordered if has_values(item)]
    maps = [item["key"] for item in ordered if chart_type_of(item) == "map" and len(numeric_points(item)) >= 8]
    limit = MAX_SECTIONS * MAX_CHARTS_PER_SECTION
    selected = pick_charts(live, limit) or ordered[:MAX_CHARTS_PER_SECTION]
    section_count = min(len(selected), MAX_SECTIONS, max(math.ceil(len(selected) / MAX_CHARTS_PER_SECTION), MIN_SECTIONS))
    groups = chunk(selected, section_count) if selected else []
    sections, facts = [], []
    for index, members in enumerate(groups):
        stems = dedupe([stem_of(item["title"]) for item in members])
        kinds = dedupe([chart_type_of(item) if chart_type_of(item) in PLAIN_TYPES else "special" for item in members])
        pairs = [fact_for(item) for item in members]
        pairs = [pair for pair in pairs if pair[0]]
        facts.extend(pairs)
        title = TITLES[index % len(TITLES)].format(stem=stems[0])
        if index == 0 and len(stems) == 1 and len(groups) == 1:
            title = stems[0]
        lead = (f"This chart follows {stems[0]}." if len(members) == 1
                else f"The {len(members)} charts here follow {join_names(stems[:3])}" + (f" and {len(stems) - 3} related series." if len(stems) > 3 else "."))
        if index == 0 and intro:
            lead = f"{intro} {lead}"
        parts = [lead] + [pair[0] for pair in pairs[:2]] + [READING_TIPS[kinds[0]]]
        sections.append({"title": title, "text": clean(" ".join(parts)), "keys": [item["key"] for item in members]})
    pull = max(facts, key=lambda pair: pair[1])[0] if facts else clean(description)
    return {
        "sections": sections,
        "pullQuote": pull,
        "mapKeys": maps,
        "format": "map" if len(maps) >= MAP_MIN_INDICATORS else "article",
        "chartKeys": [item["key"] for item in ordered],
    }

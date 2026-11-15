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

# Explicit semantic section recipes for known multi-theater / multi-thematic subgroups
CUSTOM_SUBGROUP_CLUSTERS = {
    "Insurgency & Militancy": [
        ("North East Insurgency: Fatalities, Incidents & Trajectory",
         ["northeast_insurgency_fatalities", "northeast_insurgency_incidents", "northeast_fatalities_by_period"]),
        ("Jammu & Kashmir and Punjab Militancy: Conflict Trajectories & Incidents",
         ["kashmir_insurgency_fatalities", "kashmir_terror_incidents", "kashmir_fatalities_by_period", "khalistan_insurgency_historical", "khalistan_fatalities_by_period"]),
        ("Left-Wing Extremism: Annual Fatalities & Force Casualties",
         ["lwe_incidents", "lwe_civilian_casualties", "lwe_security_force_casualties", "lwe_perpetrator_casualties", "lwe_casualties_cumulative"]),
        ("Left-Wing Extremism: Period Trajectories & Recent Civilian Toll",
         ["lwe_casualties_latest", "lwe_civilian_casualties_by_period"]),
        ("Left-Wing Extremism: Affected Districts & Violent Incidents",
         ["lwe_affected_districts", "lwe_most_affected_districts", "lwe_violent_incidents", "lwe_fatalities", "lwe_civilians_killed"]),
        ("Left-Wing Extremism: Surrenders, Security Operations & Infrastructure",
         ["lwe_attacks_economic_infrastructure", "lwe_maoist_surrenders", "lwe_security_buildup", "lwe_roads_towers"]),
    ],
    "Health Spending & Disease Burden": [
        ("Health Expenditure, Public Financing & Out-of-Pocket Spending",
         ["current_health_spending", "government_health_spending_per_capita", "wb_government_health_share", "wb_health_financing_mix", "wb_health_spending_split"]),
        ("Drinking Water, Sanitation Access & Healthcare Capacity",
         ["basic_water_access", "basic_sanitation_access", "safely_managed_drinking_water", "physicians_density", "wb_hospital_beds"]),
        ("Communicable Diseases: Tuberculosis, Vector-Borne Cases & Mortality",
         ["wb_tb_incidence", "wb_malaria_incidence", "mospi_malaria_cases", "mospi_dengue_cases", "wb_causes_of_death"]),
        ("Immunisation Coverage, Child Nutrition & Preventable Risk Factors",
         ["wb_dpt_immunization", "wb_measles_immunisation", "wb_undernourishment", "wb_child_stunting", "wb_smoking"]),
    ],
    "Coal, Oil & Gas": [
        ("Coal, Lignite & Hydrocarbon Production Trajectories",
         ["coal_production", "lignite_production", "crude_petroleum_domestic", "natural_gas_production", "coal_output_by_period"]),
        ("Energy Consumption & Import Dependence",
         ["energy_use_per_capita", "electricity_use_per_capita", "net_energy_imports_share", "energy_supply_composition", "wb_fossil_fuel_share"]),
        ("Renewable Energy & Electricity Generation Mix",
         ["renewable_energy_consumption", "renewable_electricity_output", "wb_renewable_final_energy", "wb_electricity_generation_mix"]),
        ("Resource Depletion, Coal Rents & Forest Cover",
         ["wb_coal_rents", "wb_oil_rents", "wb_natural_gas_rents", "wb_energy_depletion", "forest_area_share"]),
        ("Wholesale Price Indices for Energy Minerals",
         ["wpi_crude_petroleum", "wpi_natural_gas", "wpi_coking_coal", "wpi_lignite", "wpi_non_coking_coal"]),
        ("Comparative Energy Price Trends & Particulate Exposure",
         ["wpi_compare_energy_minerals", "pm25_exposure"]),
    ],
    "Defence Budget, Production & Exports": [
        ("Defence Expenditure, Modernisation Outlay & R&D Budget",
         ["defence_expenditure", "defence_budget_share", "defence_budget_composition", "defence_capital_acquisition", "defence_rd_budget"]),
        ("Indigenous Defence Production & Exports Engine",
         ["defence_production", "defence_exports", "defence_production_exports", "defence_stockpile"]),
        ("Arms Imports & Global Arms Trade (SIPRI)",
         ["sipri_arms_imports", "wb_arms_imports_tiv", "wb_arms_exports_tiv"]),
        ("Military Spending in Global Perspective",
         ["military_expenditure_usd", "military_expenditure_per_capita", "wb_military_gdp", "wb_military_govt", "wb_military_budget_share"]),
        ("Armed Forces Personnel & Military Strength",
         ["wb_armed_forces_personnel"]),
    ],
    "Heritage & Visitor Trends": [
        ("Domestic and Foreign Tourist Visits & Forex Earnings",
         ["tourist_visits_domestic", "tourist_visits_foreign", "tourism_foreign_exchange_earnings", "tourism_contribution_gdp", "tourist_arrivals_foreign"]),
        ("UNESCO World Heritage Sites & Cultural Preservation",
         ["unesco_world_heritage_sites", "unesco_cultural_sites", "unesco_natural_sites"]),
        ("International Tourism Receipts & Travel Spending",
         ["wb_international_tourism_receipts", "wb_international_tourism_expenditures", "wb_tourism_inbound_share"]),
    ],
    "Terrorism, Conflict & Displacement": [
        ("Terrorism Fatalities, Incidents & Historical Trajectory",
         ["terror_fatalities", "terror_incidents", "terror_fatalities_trend", "insurgency_fatalities_overview", "terror_fatalities_by_region"]),
        ("Civilian Impact & Internal Conflict Displacement",
         ["terror_civilian_casualties", "conflict_displaced_persons", "xp_idp_conflict_trend", "xp_idp_conflict_peers"]),
        ("Global Peace & Counter-Terrorism Index Comparisons",
         ["global_terrorism_index", "global_peace_index", "xp_terrorism_index_trend", "xp_peace_index_rank"]),
    ],
    "The Indus Valley Civilisation Comprehensive Excavation Map": [
        ("Urban Planning & Hydraulic Sanitation",
         ["ivc_urban_settlement_area"]),
        ("Standardized Metrology & Glyptic Seals",
         ["ivc_steatite_seals_by_site"]),
        ("Long-Distance Maritime Trade Corridors",
         ["ivc_international_trade_distance"]),
        ("Epigraphic Sign Concordance & Positional Entropy",
         ["ivc_top_script_signs_frequency"]),
        ("Settlement Chronology & Radiocarbon Horizons",
         ["ivc_radiocarbon_phases"]),
    ],
    "Empires of Ancient India: Dynastic Atlases, Battles & Inscriptions": [
        ("Imperial Territorial Extent & Hegemony",
         ["ancient_empires_territorial_span"]),
        ("Standing Armies & Military Formations",
         ["ancient_empires_military_infantry", "ancient_empires_war_elephants"]),
        ("Epigraphic Records & Royal Charters",
         ["ancient_empires_inscriptions_count", "ancient_empires_reign_durations"]),
        ("Statecraft, Numismatics & Trans-Eurasian Commerce",
         ["mahajanapadas_political_systems", "indogreek_numismatic_coin_types", "kushan_silkroad_monasteries", "harsha_imperial_assemblies", "sangam_maritime_ports_trade"]),
    ],
}


def clean(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def stem_of(title):
    text = STOP_SUFFIX.sub("", clean(title))
    text = re.split(r"\s+[\u2014\u2013]\s+|:\s|\s\(", text, maxsplit=1)[0].strip(" -:,")
    if len(text) > 52:
        text = text[:52].rsplit(" ", 1)[0].rstrip(" ,-:&")
    return text or clean(title)[:52]


def topic_of(indicator):
    title = indicator.get("title", "")
    key = indicator.get("key", "")
    for pat, label in [
        (r"north\s*east|northeast", "North East Insurgency"),
        (r"jammu\s*&?\s*kashmir|kashmir", "Jammu & Kashmir Militancy"),
        (r"punjab|khalistan", "Punjab Militancy"),
        (r"maoist|naxal|left-wing|lwe", "Left-Wing Extremism (LWE)"),
        (r"drinking\s*water", "Drinking Water Access"),
        (r"sanitation", "Sanitation Infrastructure"),
        (r"health\s*(spending|expenditure|financing)", "Health Expenditure & Financing"),
        (r"hospital|physician", "Healthcare Capacity"),
        (r"malaria|dengue|tuberculosis|\btb\b", "Communicable Diseases"),
        (r"immunis|immuniz|vaccin", "Immunisation Coverage"),
        (r"stunting|undernourish|malnutrition", "Child Nutrition"),
        (r"smoking|tobacco", "Risk Factors & Lifestyle"),
        (r"coal|lignite", "Coal & Lignite"),
        (r"crude|petroleum|oil", "Crude Oil & Petroleum"),
        (r"natural\s*gas", "Natural Gas"),
        (r"renewable|solar|wind", "Renewable Energy"),
        (r"defence\s*expenditure|defence\s*budget|military\s*expenditure", "Defence Spending"),
        (r"defence\s*production|defence\s*export", "Defence Production & Exports"),
        (r"arms\s*import|arms\s*export", "Arms Trade (SIPRI)"),
        (r"tourist\s*visit|tourism\s*foreign", "Tourism Visits & Earnings"),
        (r"unesco", "UNESCO World Heritage"),
        (r"international\s*tourism", "International Tourism Receipts"),
    ]:
        if re.search(pat, title, re.I) or re.search(pat, key, re.I):
            return label
    return stem_of(title)


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


def cluster_indicators(selected, subgroup_name=""):
    """Clusters selected indicators into 3-6 sections of 1-5 indicators each.
    Returns list of dicts: [{"title": custom_title_or_None, "members": [...]}, ...]
    """
    by_key = {item["key"]: item for item in selected}
    recipe = CUSTOM_SUBGROUP_CLUSTERS.get(subgroup_name)
    if recipe:
        sections = []
        used_keys = set()
        for custom_title, key_list in recipe:
            members = [by_key[k] for k in key_list if k in by_key]
            if members:
                for i in range(0, len(members), MAX_CHARTS_PER_SECTION):
                    slice_part = members[i:i + MAX_CHARTS_PER_SECTION]
                    sections.append({
                        "title": custom_title if i == 0 else f"{custom_title} (Part {i//MAX_CHARTS_PER_SECTION + 1})",
                        "members": slice_part,
                    })
                    used_keys.update(item["key"] for item in slice_part)
        remaining = [item for item in selected if item["key"] not in used_keys]
        if remaining:
            for i in range(0, len(remaining), MAX_CHARTS_PER_SECTION):
                sections.append({
                    "title": None,
                    "members": remaining[i:i + MAX_CHARTS_PER_SECTION],
                })
        while len(sections) > MAX_SECTIONS:
            merged = False
            for i in range(len(sections) - 1):
                if len(sections[i]["members"]) + len(sections[i+1]["members"]) <= MAX_CHARTS_PER_SECTION:
                    t1 = sections[i]["title"] or ""
                    t2 = sections[i+1]["title"] or ""
                    joint_title = f"{t1} & {t2}" if t1 and t2 and t1 != t2 else (t1 or t2 or None)
                    sections[i] = {
                        "title": joint_title,
                        "members": sections[i]["members"] + sections[i+1]["members"],
                    }
                    sections.pop(i+1)
                    merged = True
                    break
            if not merged:
                last_two = sections[-2]["members"] + sections[-1]["members"]
                sections.pop()
                sections.pop()
                sections.append({"title": None, "members": last_two[:MAX_CHARTS_PER_SECTION]})
                if len(last_two) > MAX_CHARTS_PER_SECTION:
                    sections.append({"title": None, "members": last_two[MAX_CHARTS_PER_SECTION:]})
                break
        min_target = min(MIN_SECTIONS, len(selected))
        while len(sections) < min_target:
            split_idx = max(range(len(sections)), key=lambda i: len(sections[i]["members"]))
            if len(sections[split_idx]["members"]) <= 1:
                break
            big = sections[split_idx]["members"]
            mid = len(big) // 2
            t = sections[split_idx]["title"]
            sections[split_idx] = {"title": t, "members": big[:mid]}
            sections.insert(split_idx + 1, {"title": None, "members": big[mid:]})
        return sections

    # Generic clustering for other subgroups
    target_count = min(len(selected), MAX_SECTIONS, max(math.ceil(len(selected) / MAX_CHARTS_PER_SECTION), MIN_SECTIONS))
    raw_chunks = chunk(selected, target_count)
    return [{"title": None, "members": c} for c in raw_chunks]


def synthesize_section_title(members, subgroup_name, section_index, total_sections):
    """Generates an accurate, composite section title reflecting all indicators in the section."""
    topics = dedupe([topic_of(item) for item in members])
    stems = dedupe([stem_of(item["title"]) for item in members])

    if len(members) == 1:
        return stems[0]

    if len(topics) == 1:
        topic = topics[0]
        if ":" in topic:
            return topic
        return clean(f"{topic}: Key Trends & Indicators")

    if len(topics) == 2:
        return clean(f"{topics[0]} & {topics[1]}: Core Measures")

    if len(topics) == 3:
        joint = f"{topics[0]}, {topics[1]} & {topics[2]}"
        return clean(joint if len(joint) <= 64 else f"{topics[0]} & {topics[1]}: Comparative Trends")

    return clean(f"{stems[0]} and Related Measures")


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

    clusters = cluster_indicators(selected, subgroup_name=name) if selected else []
    sections, facts = [], []

    for index, cluster in enumerate(clusters):
        members = cluster["members"]
        stems = dedupe([stem_of(item["title"]) for item in members])
        kinds = dedupe([chart_type_of(item) if chart_type_of(item) in PLAIN_TYPES else "special" for item in members])
        pairs = [fact_for(item) for item in members]
        pairs = [pair for pair in pairs if pair[0]]
        facts.extend(pairs)

        title = cluster["title"] or synthesize_section_title(members, name, index, len(clusters))
        lead = (f"This chart follows {stems[0]}." if len(members) == 1
                else f"The {len(members)} charts here follow {join_names(stems[:3])}" + (f" and {len(stems) - 3} related series." if len(stems) > 3 else "."))
        if index == 0 and intro:
            lead = f"{intro} {lead}"
        parts = [lead] + [pair[0] for pair in pairs[:2]] + [READING_TIPS[kinds[0]]]
        sections.append({"title": title, "text": clean(" ".join(parts)), "keys": [item["key"] for item in members]})

    # Prioritize pull quote from the headline section indicators to ensure alignment with topic
    first_facts = [fact_for(item) for item in clusters[0]["members"]] if clusters else []
    first_facts = [p for p in first_facts if p[0]]
    if first_facts:
        pull = max(first_facts, key=lambda pair: pair[1])[0]
    elif facts:
        pull = max(facts, key=lambda pair: pair[1])[0]
    else:
        pull = clean(description)

    return {
        "sections": sections,
        "pullQuote": pull,
        "mapKeys": maps,
        "format": "map" if len(maps) >= MAP_MIN_INDICATORS else "article",
        "chartKeys": [item["key"] for item in ordered],
    }

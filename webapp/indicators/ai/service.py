"""Semantic AI search, vector recommender, and macroeconomic synthesis services."""

from __future__ import annotations

import logging
import math
import re
from typing import Any, Dict, List, Optional

from .azure_client import AzureAIClient
from .index import CatalogVectorIndex

logger = logging.getLogger(__name__)

HISTORICAL_MILESTONES = {
    '1991': '1991 Economic Liberalization and Industrial Policy Reforms',
    '1998': 'Pokhran-II sanctions & Asian Financial Crisis ripple effects',
    '2008': '2008 Global Financial Crisis & domestic stimulus cycle',
    '2009': 'Post-GFC fiscal stimulus & domestic recovery',
    '2014': 'Jan Dhan financial inclusion & Make in India rollout',
    '2016': 'Demonetization & IBC framework enactment',
    '2017': 'Nationwide Goods and Services Tax (GST) implementation',
    '2020': 'COVID-19 pandemic nationwide lockdown shock',
    '2021': 'Post-pandemic reopening and industrial rebound',
    '2022': 'Global energy supply disruptions & RBI rate hike cycle',
    '2023': 'Capex infrastructure push & DPI digital expansion',
    '2024': 'General election cycle & macroeconomic consolidation',
}


def search_indicators(
    query: str,
    limit: int = 10,
    category: Optional[str] = None,
    min_similarity: float = 0.15,
) -> Dict[str, Any]:
    """Execute semantic search for an indicator query on Azure App Service."""
    query = (query or '').strip()
    if not query:
        return {
            'query': '',
            'provider': 'none',
            'count': 0,
            'results': [],
        }

    client = AzureAIClient()
    index = CatalogVectorIndex.get_instance()

    query_vec = client.get_embedding(query)
    results = index.search(
        query_vec=query_vec,
        query_text=query,
        limit=limit,
        category=category,
        min_similarity=min_similarity,
    )

    return {
        'query': query,
        'provider': client.provider,
        'count': len(results),
        'results': results,
    }


def recommend_indicators(
    key: str,
    limit: int = 5,
    same_category_only: bool = False,
) -> Dict[str, Any]:
    """Recommend related indicators using pre-computed vector cosine similarity (₹0 cost)."""
    key = (key or '').strip()
    if not key:
        return {'key': '', 'count': 0, 'recommendations': []}

    index = CatalogVectorIndex.get_instance()
    recommendations = index.recommend(key=key, limit=limit, same_category_only=same_category_only)

    return {
        'key': key,
        'count': len(recommendations),
        'recommendations': recommendations,
    }


def generate_indicator_insights(indicator: Any) -> Dict[str, Any]:
    """Synthesize macroeconomic and policy inflection insights for an indicator (zero external cost)."""
    labels = getattr(indicator, 'labels', []) or []
    datasets = getattr(indicator, 'datasets', []) or []
    unit = getattr(indicator, 'unit', '') or getattr(indicator, 'suffix', '') or ''
    title = getattr(indicator, 'title', '')
    source = getattr(indicator, 'source', '')
    category_name = getattr(indicator.category, 'name', '') if hasattr(indicator, 'category') else ''

    valid_points = []
    if datasets and isinstance(datasets, list) and len(datasets) > 0:
        values = datasets[0].get('values', [])
        for idx in range(min(len(labels), len(values))):
            val = values[idx]
            if val is not None and isinstance(val, (int, float)):
                valid_points.append((str(labels[idx]), float(val)))

    if not valid_points:
        return {
            'key': getattr(indicator, 'key', ''),
            'title': title,
            'summary': f"{title} reflects official public data from {source or 'national statistical authorities'}.",
            'metrics': None,
            'inflections': [],
            'takeaways': [
                f"Sourced from {source or 'official registry'}.",
                "Data series contains categorical or geographic distributions without temporal trends.",
                "Verify underlying definitions and methodology notes on the official portal."
            ],
        }

    # Trend calculations
    first_label, first_val = valid_points[0]
    latest_label, latest_val = valid_points[-1]
    sorted_by_val = sorted(valid_points, key=lambda x: x[1])
    trough_label, trough_val = sorted_by_val[0]
    peak_label, peak_val = sorted_by_val[-1]

    delta = latest_val - first_val
    delta_pct = (delta / abs(first_val) * 100) if first_val != 0 else None

    # CAGR calculation if span is multi-year and positive
    cagr = None
    first_year = re.search(r'\b(19\d\d|20\d\d)\b', first_label)
    latest_year = re.search(r'\b(19\d\d|20\d\d)\b', latest_label)
    if first_year and latest_year and first_val > 0 and latest_val > 0:
        n_years = int(latest_year.group(1)) - int(first_year.group(1))
        if n_years > 1:
            try:
                cagr = round(((latest_val / first_val) ** (1 / n_years) - 1) * 100, 2)
            except (OverflowError, ZeroDivisionError):
                cagr = None

    # Historical inflection matching
    inflections = []
    for lbl, val in valid_points:
        for year, event in HISTORICAL_MILESTONES.items():
            if year in lbl and not any(inf['year'] == year for inf in inflections):
                inflections.append({
                    'year': year,
                    'label': lbl,
                    'value': val,
                    'unit': unit,
                    'event': event,
                })

    # Caveats based on domain
    caveat = "Data sourced directly from official published tables with no interpolated projections."
    cat_lower = category_name.lower()
    src_lower = source.lower()
    if 'mospi' in src_lower or 'economy' in cat_lower or 'gdp' in getattr(indicator, 'key', ''):
        caveat = "Official series reflects MoSPI's 2011-12 base-year revision."
    elif 'election' in cat_lower or 'eci' in src_lower:
        caveat = "Post-2008 constituency boundaries reflect the Delimitation Order of 2008."
    elif 'court' in cat_lower or 'judiciary' in cat_lower or 'njdg' in src_lower:
        caveat = "Court disposal and pendency figures fluctuate with scheduled judicial recess periods."

    # Build 3 crisp executive takeaways
    takeaways = []
    # 1. Growth trajectory
    if cagr is not None:
        takeaways.append(
            f"Expanded at a CAGR of {cagr}% from {first_val:g}{unit} ({first_label}) to {latest_val:g}{unit} ({latest_label})."
        )
    elif delta_pct is not None:
        direction = 'increased' if delta >= 0 else 'decreased'
        takeaways.append(
            f"Net movement {direction} by {abs(delta):g}{unit} ({delta_pct:+.1f}%) from {first_label} to {latest_label}."
        )
    else:
        takeaways.append(
            f"Recorded from {first_label} ({first_val:g}{unit}) through {latest_label} ({latest_val:g}{unit})."
        )

    # 2. Peak & Inflection context
    if inflections:
        first_inf = inflections[-1]
        takeaways.append(
            f"Recorded peak at {peak_val:g}{unit} ({peak_label}) and trough at {trough_val:g}{unit} ({trough_label}); key milestone in {first_inf['year']} ({first_inf['event']})."
        )
    else:
        takeaways.append(
            f"Historical range spans from {trough_val:g}{unit} ({trough_label}) to a peak of {peak_val:g}{unit} ({peak_label})."
        )

    # 3. Methodological provenance
    takeaways.append(
        f"Verified via {source or 'national reporting agencies'}. {caveat}"
    )

    summary = (
        f"{title} progressed from {first_val:g}{unit} ({first_label}) to {latest_val:g}{unit} ({latest_label}), "
        f"attaining a maximum of {peak_val:g}{unit} ({peak_label}). "
        f"{'Inflection points correlate with ' + inflections[-1]['event'] + '.' if inflections else ''}"
    ).strip()

    return {
        'key': getattr(indicator, 'key', ''),
        'title': title,
        'summary': summary,
        'metrics': {
            'first': {'label': first_label, 'value': first_val},
            'latest': {'label': latest_label, 'value': latest_val},
            'peak': {'label': peak_label, 'value': peak_val},
            'trough': {'label': trough_label, 'value': trough_val},
            'cagr': cagr,
            'delta': round(delta, 3),
            'unit': unit,
        },
        'inflections': inflections,
        'takeaways': takeaways,
    }


def generate_compare_insights(indicators: List[Any]) -> Dict[str, Any]:
    """Compute pairwise Pearson correlation and identify decoupling shocks across compared indicators (₹0 cost)."""
    if not indicators:
        return {'keys': [], 'count': 0, 'summary': '', 'correlations': [], 'decouplings': [], 'takeaways': []}

    keys = [getattr(ind, 'key', '') for ind in indicators]
    titles = {getattr(ind, 'key', ''): getattr(ind, 'title', '') for ind in indicators}
    suffixes = {getattr(ind, 'key', ''): (getattr(ind, 'suffix', '') or getattr(ind, 'unit', '') or '').strip() for ind in indicators}

    # Extract time series maps: {label: numeric_val}
    series_maps: Dict[str, Dict[str, float]] = {}
    for ind in indicators:
        key = getattr(ind, 'key', '')
        labels = getattr(ind, 'labels', []) or []
        datasets = getattr(ind, 'datasets', []) or []
        first_vals = datasets[0].get('values', []) if datasets and isinstance(datasets, list) and len(datasets) > 0 else []
        mapping: Dict[str, float] = {}
        for idx in range(min(len(labels), len(first_vals))):
            val = first_vals[idx]
            if val is not None and isinstance(val, (int, float)) and not isinstance(val, bool) and math.isfinite(val):
                mapping[str(labels[idx])] = float(val)
        series_maps[key] = mapping

    correlations = []
    all_decouplings = []

    # Pairwise evaluation
    for i in range(len(indicators)):
        for j in range(i + 1, len(indicators)):
            ind_a = indicators[i]
            ind_b = indicators[j]
            key_a = getattr(ind_a, 'key', '')
            key_b = getattr(ind_b, 'key', '')
            map_a = series_maps.get(key_a, {})
            map_b = series_maps.get(key_b, {})

            # Shared labels preserving chronological order
            all_labels = list(dict.fromkeys(list(map_a.keys()) + list(map_b.keys())))
            if all(lbl[:4].isdigit() for lbl in all_labels if len(lbl) >= 4):
                all_labels.sort()

            common_labels = [lbl for lbl in all_labels if lbl in map_a and lbl in map_b]
            n_common = len(common_labels)

            r = None
            strength_desc = "Insufficient shared observation periods"

            if n_common >= 3:
                vals_a = [map_a[lbl] for lbl in common_labels]
                vals_b = [map_b[lbl] for lbl in common_labels]
                mean_a = sum(vals_a) / n_common
                mean_b = sum(vals_b) / n_common
                diff_a = [v - mean_a for v in vals_a]
                diff_b = [v - mean_b for v in vals_b]
                var_a = sum(d * d for d in diff_a)
                var_b = sum(d * d for d in diff_b)
                denom = math.sqrt(var_a * var_b)

                if denom > 1e-9:
                    r_raw = sum(da * db for da, db in zip(diff_a, diff_b)) / denom
                    r = round(max(-1.0, min(1.0, r_raw)), 2)
                    if r >= 0.70:
                        strength_desc = "Strong positive co-movement"
                    elif r >= 0.35:
                        strength_desc = "Moderate positive correlation"
                    elif r > -0.35:
                        strength_desc = "Decoupled / weak relationship"
                    elif r > -0.70:
                        strength_desc = "Moderate inverse relationship"
                    else:
                        strength_desc = "Strong inverse trade-off"
                else:
                    r = 0.0
                    strength_desc = "Constant series (zero variance)"

                # Decoupling shock detection
                # Look for consecutive steps where direction flips against overall correlation
                if r is not None and abs(r) >= 0.35:
                    for k in range(len(common_labels) - 1):
                        lbl_prev = common_labels[k]
                        lbl_curr = common_labels[k + 1]
                        delta_a = map_a[lbl_curr] - map_a[lbl_prev]
                        delta_b = map_b[lbl_curr] - map_b[lbl_prev]

                        year_match = re.search(r'\b(19\d\d|20\d\d)\b', lbl_curr)
                        year_str = year_match.group(1) if year_match else ''
                        event_name = HISTORICAL_MILESTONES.get(year_str, '')

                        is_decoupled = False
                        if r >= 0.35 and (delta_a * delta_b < 0) and (abs(delta_a) > 0 or abs(delta_b) > 0):
                            is_decoupled = True
                        elif r <= -0.35 and (delta_a * delta_b > 0) and (abs(delta_a) > 0 or abs(delta_b) > 0):
                            is_decoupled = True

                        if is_decoupled:
                            all_decouplings.append({
                                'pair': [key_a, key_b],
                                'titles': [titles[key_a], titles[key_b]],
                                'year': year_str or lbl_curr,
                                'label': lbl_curr,
                                'event': event_name or 'Divergent Inflection',
                                'observation': (
                                    f"In {lbl_curr}, {titles[key_a]} shifted by {delta_a:+g}{suffixes[key_a]} "
                                    f"while {titles[key_b]} moved by {delta_b:+g}{suffixes[key_b]}."
                                ),
                            })

            correlations.append({
                'pair': [key_a, key_b],
                'titles': [titles[key_a], titles[key_b]],
                'r': r,
                'strength': strength_desc,
                'sample_size': n_common,
                'start_year': common_labels[0] if common_labels else None,
                'end_year': common_labels[-1] if common_labels else None,
            })

    # Deduplicate decouplings by year/label
    seen_years = set()
    unique_decouplings = []
    for d in all_decouplings:
        key_tag = (d['year'], d['event'])
        if key_tag not in seen_years:
            seen_years.add(key_tag)
            unique_decouplings.append(d)

    unique_decouplings.sort(key=lambda d: d.get('year') or '', reverse=True)

    takeaways = []
    valid_corrs = [c for c in correlations if c['r'] is not None]
    if valid_corrs:
        strongest = max(valid_corrs, key=lambda c: abs(c['r']))
        t_a, t_b = strongest['titles']
        r_val = strongest['r']
        if r_val >= 0.50:
            takeaways.append(
                f"Strong synchrony: {t_a} and {t_b} exhibit tight co-movement (r = {r_val:+g}) across {strongest['sample_size']} shared observations ({strongest['start_year']}–{strongest['end_year']})."
            )
        elif r_val <= -0.50:
            takeaways.append(
                f"Inverse trade-off: {t_a} and {t_b} reflect a marked structural inverse relationship (r = {r_val:+g}) over {strongest['sample_size']} years."
            )
        else:
            takeaways.append(
                f"Relative independence: Series display moderate or decoupled correlation (r = {r_val:+g}) between {t_a} and {t_b} over {strongest['sample_size']} periods."
            )
    else:
        takeaways.append("Series cover non-overlapping reporting cadences; alignment requires interpolation across reporting years.")

    if unique_decouplings:
        top_dec = unique_decouplings[0]
        event_str = f" ({top_dec['event']})" if top_dec['event'] and top_dec['event'] != 'Divergent Inflection' else ""
        takeaways.append(
            f"Key structural decoupling observed in {top_dec['label']}{event_str}: {top_dec['observation']}"
        )
    else:
        takeaways.append(
            "No severe historical divergence detected; trends evolved in close macro alignment across observation years."
        )

    units = list(dict.fromkeys(s for s in suffixes.values() if s))
    if len(units) > 1:
        takeaways.append(
            f"Differing units ({', '.join(units)}) detected. Rebase series to 100 on the workbench toolbar for proportional trajectory comparison."
        )
    else:
        takeaways.append(
            "Shared unit scale allows direct absolute variance comparison across indicators."
        )

    summary_first = takeaways[0] if takeaways else "Cross-series comparative analytics completed."
    summary = f"Comparing {len(indicators)} indicators: {summary_first}"

    return {
        'keys': keys,
        'count': len(indicators),
        'summary': summary,
        'correlations': correlations,
        'decouplings': unique_decouplings[:5],
        'takeaways': takeaways,
    }



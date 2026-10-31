"""Loads data/catalog.json (exported from the static dashboard) into the database."""
import json
import math
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from django.db import transaction
from django.utils import timezone as dj_timezone
from django.utils.text import slugify

from .models import Article, Category, DataRefresh, Indicator, Subgroup

PREVIEW_POINTS = 40
RADIAL_TYPES = {'pie', 'doughnut'}


def _clean_number(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _latest_point(labels, datasets):
    if not datasets:
        return '', None
    values = datasets[0]['values']
    for index in range(min(len(labels), len(values)) - 1, -1, -1):
        if values[index] is not None:
            return str(labels[index]), values[index]
    return '', None


def build_preview(labels, datasets, chart_type, max_points=PREVIEW_POINTS):
    """Downsamples ordered time series for list cards; categorical charts keep every label."""
    if chart_type in RADIAL_TYPES or chart_type == 'bar' or len(labels) <= max_points:
        indexes = list(range(len(labels)))
    else:
        step = (len(labels) - 1) / (max_points - 1)
        indexes = sorted({round(position * step) for position in range(max_points)})
    return {
        'labels': [labels[index] for index in indexes],
        'datasets': [
            {
                'label': dataset['label'],
                'color': dataset.get('color'),
                'values': [dataset['values'][index] if index < len(dataset['values']) else None for index in indexes],
            }
            for dataset in datasets[:6]
        ],
    }


def parse_published(value):
    if not value:
        return None
    text = str(value).strip()
    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(text.replace('Z', '+00:00'))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _normalise_series(raw_series, title, color):
    labels = [str(label) for label in raw_series.get('labels') or []]
    datasets = []
    for index, dataset in enumerate(raw_series.get('datasets') or []):
        values = [_clean_number(value) for value in dataset.get('values') or []]
        if not values:
            continue
        datasets.append({
            'label': str(dataset.get('label') or (title if index == 0 else f'Series {index + 1}')),
            'color': dataset.get('color') or (color if index == 0 else None),
            'values': values,
        })
    has_points = bool(labels) and any(value is not None for dataset in datasets for value in dataset['values'])
    return labels, datasets, has_points


def load_catalog(path):
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


@transaction.atomic
def import_catalog(catalog, prune=True):
    refresh = DataRefresh.objects.create(source_generated_at=str(catalog.get('generated_at_utc') or ''))
    categories = {}
    subgroups = {}
    for category_order, item in enumerate(catalog.get('categories') or []):
        category, _ = Category.objects.update_or_create(
            name=item['name'],
            defaults={
                'slug': slugify(item['name']) or f'group-{category_order}',
                'order': item.get('order', category_order),
                'title': item.get('title') or item['name'],
                'description': item.get('description') or '',
                'badges': item.get('badges') or [],
                'art': item.get('art') or '',
            },
        )
        categories[category.name] = category
        for subgroup_order, sub in enumerate(item.get('subgroups') or []):
            subgroup, _ = Subgroup.objects.update_or_create(
                category=category,
                slug=slugify(sub['name']) or f'subgroup-{subgroup_order}',
                defaults={
                    'name': sub['name'],
                    'order': sub.get('order', subgroup_order),
                    'title': sub.get('title') or sub['name'],
                    'description': sub.get('description') or '',
                    'art': sub.get('art') or category.art,
                },
            )
            subgroups[(category.name, subgroup.name)] = subgroup

    seen_keys = set()
    live_count = 0
    for position, item in enumerate(catalog.get('indicators') or []):
        key = item['key']
        if key in seen_keys:
            raise ValueError(f'Duplicate indicator key in catalogue: {key}')
        seen_keys.add(key)
        category = categories.get(item['category'])
        if category is None:
            category, _ = Category.objects.get_or_create(
                name=item['category'], defaults={'slug': slugify(item['category']), 'order': len(categories)})
            categories[category.name] = category
        subgroup = subgroups.get((category.name, item['subgroup']))
        if subgroup is None:
            subgroup, _ = Subgroup.objects.get_or_create(
                category=category, slug=slugify(item['subgroup']) or 'general',
                defaults={'name': item['subgroup'], 'order': 99, 'art': category.art})
            subgroups[(category.name, subgroup.name)] = subgroup

        raw_series = item.get('series') or {}
        color = item.get('color') or '#58a6ff'
        labels, datasets, has_points = _normalise_series(raw_series, item['title'], color)
        error = str(raw_series.get('error') or '')
        is_live = has_points and not error
        live_count += int(is_live)
        chart_type = raw_series.get('chart_type') or 'line'
        latest_label, latest_value = _latest_point(labels, datasets)
        search_text = ' '.join([
            key.replace('_', ' '), item['title'], item.get('subtitle') or '', category.name, subgroup.name,
            item.get('frequency') or '', item.get('suffix') or '', raw_series.get('source') or '',
        ]).lower()
        Indicator.objects.update_or_create(
            key=key,
            defaults={
                'title': item['title'][:300],
                'subtitle': (item.get('subtitle') or '')[:500],
                'frequency': (item.get('frequency') or '')[:80],
                'color': color[:20],
                'suffix': (item.get('suffix') or '')[:80],
                'source_url': (item.get('source_url') or '')[:600],
                'details': item.get('details') or '',
                'category': category,
                'subgroup': subgroup,
                'position': item.get('position', position),
                'labels': labels,
                'datasets': datasets,
                'preview': build_preview(labels, datasets, chart_type) if is_live else {'labels': [], 'datasets': []},
                'chart_type': chart_type[:20],
                'index_axis': 'y' if raw_series.get('index_axis') == 'y' else 'x',
                'scope': (raw_series.get('scope') or '')[:40],
                'scope_label': (raw_series.get('scope_label') or '')[:120],
                'note': raw_series.get('note') or '',
                'source': raw_series.get('source') or '',
                'unit': (raw_series.get('unit') or '')[:80],
                'error': error,
                'is_live': is_live,
                'point_count': len(labels),
                'first_label': (labels[0] if labels else '')[:80],
                'latest_label': latest_label[:80],
                'latest_value': latest_value,
                'search_text': search_text,
            },
        )

    article_count = 0
    for item in catalog.get('articles') or []:
        url = (item.get('url') or '').strip()
        if not url.startswith(('http://', 'https://')):
            continue
        kind = item.get('kind') if item.get('kind') in dict(Article.KIND_CHOICES) else 'other'
        Article.objects.update_or_create(
            url=url[:700],
            defaults={
                'title': (item.get('title') or 'Untitled public article')[:500],
                'published': str(item.get('published') or '')[:80],
                'published_at': parse_published(item.get('published')),
                'publisher': (item.get('publisher') or '')[:120],
                'kind': kind,
            },
        )
        article_count += 1

    if prune:
        Indicator.objects.exclude(key__in=seen_keys).delete()
        Subgroup.objects.filter(indicators__isnull=True).delete()
        Category.objects.filter(indicators__isnull=True).delete()

    refresh.status = 'success'
    refresh.finished_at = dj_timezone.now()
    refresh.indicators_count = len(seen_keys)
    refresh.live_count = live_count
    refresh.articles_count = article_count
    refresh.message = f'Imported {len(seen_keys)} indicators ({live_count} live) and {article_count} articles.'
    refresh.save()
    return refresh

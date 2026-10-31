import copy

from indicators.catalog import import_catalog

SAMPLE_CATALOG = {
    'generated_at_utc': '2026-05-01T00:00:00+00:00',
    'categories': [
        {
            'name': 'Economic', 'order': 0, 'title': 'Economic engine', 'description': 'Growth and prices',
            'badges': ['GDP', 'CPI'], 'art': 'parliament.svg',
            'subgroups': [
                {'name': 'Macro Overview', 'order': 0, 'title': 'Macro', 'description': 'Headline macro', 'art': 'parliament.svg'},
                {'name': 'Trade', 'order': 1, 'title': 'Trade', 'description': 'Exports', 'art': 'rail-station.svg'},
            ],
        },
        {
            'name': 'Elections', 'order': 1, 'title': 'Elections', 'description': 'Votes', 'badges': [], 'art': 'eci-building.svg',
            'subgroups': [{'name': 'Indian Elections', 'order': 0, 'title': 'Indian Elections', 'description': '', 'art': ''}],
        },
    ],
    'indicators': [
        {
            'key': 'gdp_growth', 'title': 'Real GDP growth', 'subtitle': 'Annual real GDP growth', 'frequency': 'Annual',
            'color': '#ff9933', 'suffix': '%', 'source_url': 'https://data.worldbank.org/', 'details': 'World Bank series.',
            'category': 'Economic', 'subgroup': 'Macro Overview', 'position': 0,
            'series': {
                'labels': [str(year) for year in range(1961, 2025)],
                'datasets': [{'label': 'Real GDP growth', 'color': '#ff9933', 'values': [float(year % 9) for year in range(1961, 2025)]}],
                'chart_type': 'line', 'index_axis': 'x', 'source': 'World Bank',
            },
        },
        {
            'key': 'exports_usd', 'title': 'Merchandise exports', 'subtitle': 'Exports in USD', 'frequency': 'Annual',
            'color': '#3fb950', 'suffix': ' USD', 'source_url': 'https://data.worldbank.org/', 'details': '',
            'category': 'Economic', 'subgroup': 'Trade', 'position': 1,
            'series': {
                'labels': ['2022', '2023', '2024'],
                'datasets': [
                    {'label': 'Exports', 'color': '#3fb950', 'values': [450e9, 431e9, None]},
                    {'label': 'Imports', 'color': '#ff7b72', 'values': [720e9, 'bad', 700e9]},
                ],
                'chart_type': 'line',
            },
        },
        {
            'key': 'seat_share', 'title': 'Lok Sabha seat share', 'subtitle': 'Seats by party', 'frequency': 'Election',
            'color': '#58a6ff', 'suffix': ' seats', 'source_url': 'https://results.eci.gov.in/', 'details': '',
            'category': 'Elections', 'subgroup': 'Indian Elections', 'position': 2,
            'series': {
                'labels': ['BJP', 'INC', 'SP'],
                'datasets': [{'label': 'Seats', 'values': [240, 99, 37]}],
                'chart_type': 'doughnut', 'scope': 'category',
            },
        },
        {
            'key': 'pending_series', 'title': 'Pending official series', 'subtitle': 'Awaiting publication', 'frequency': 'Monthly',
            'color': '#bc8cff', 'suffix': '', 'source_url': '', 'details': '',
            'category': 'Elections', 'subgroup': 'Indian Elections', 'position': 3,
            'series': {'labels': [], 'datasets': [], 'error': 'Source blocked automated access'},
        },
    ],
    'articles': [
        {'title': 'Older article', 'url': 'https://example.com/older', 'published': 'Mon, 01 Jan 2024 10:00:00 GMT',
         'publisher': 'Indian Matrix', 'kind': 'indian_matrix'},
        {'title': 'Newer article', 'url': 'https://example.com/newer', 'published': '2026-04-02T08:00:00Z',
         'publisher': 'Polity and Policy', 'kind': 'polity_policy'},
        {'title': 'Bad link', 'url': 'javascript:alert(1)', 'published': '', 'publisher': 'X', 'kind': 'other'},
    ],
}


def sample_catalog():
    return copy.deepcopy(SAMPLE_CATALOG)


def load_sample():
    return import_catalog(sample_catalog())

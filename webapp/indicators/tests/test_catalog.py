import json
import tempfile
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from indicators.catalog import build_preview, import_catalog, parse_published
from indicators.models import Article, Category, DataRefresh, Indicator, SavedChart, Subgroup

from .fixtures import load_sample, sample_catalog


class CatalogImportTests(TestCase):
    def test_import_creates_groups_subgroups_indicators_and_articles(self):
        refresh = load_sample()
        self.assertEqual(refresh.status, 'success')
        self.assertEqual(refresh.indicators_count, 4)
        self.assertEqual(refresh.live_count, 3)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Subgroup.objects.count(), 3)
        self.assertEqual(Indicator.objects.count(), 4)
        self.assertEqual(Article.objects.count(), 2, 'non-http links must be skipped')
        self.assertEqual(Subgroup.objects.get(slug='indian-elections').art, 'eci-building.svg')

    def test_indicator_fields_and_latest_value(self):
        load_sample()
        gdp = Indicator.objects.get(key='gdp_growth')
        self.assertTrue(gdp.is_live)
        self.assertEqual(gdp.point_count, 64)
        self.assertEqual((gdp.first_label, gdp.latest_label), ('1961', '2024'))
        self.assertEqual(gdp.latest_value, float(2024 % 9))
        self.assertEqual(gdp.category.name, 'Economic')
        self.assertIn('real gdp growth', gdp.search_text)

    def test_non_numeric_values_become_null_and_latest_skips_gaps(self):
        load_sample()
        exports = Indicator.objects.get(key='exports_usd')
        self.assertEqual(exports.datasets[1]['values'], [720e9, None, 700e9])
        self.assertEqual(exports.latest_label, '2023')
        self.assertEqual(exports.latest_value, 431e9)

    def test_error_series_is_not_live(self):
        load_sample()
        pending = Indicator.objects.get(key='pending_series')
        self.assertFalse(pending.is_live)
        self.assertEqual(pending.error, 'Source blocked automated access')
        self.assertEqual(pending.preview, {'labels': [], 'datasets': []})

    def test_reimport_is_idempotent_and_keeps_saved_charts(self):
        load_sample()
        user = self.make_user()
        SavedChart.objects.create(user=user, indicator=Indicator.objects.get(key='gdp_growth'))
        load_sample()
        self.assertEqual(Indicator.objects.count(), 4)
        self.assertEqual(SavedChart.objects.count(), 1)

    def test_reimport_prunes_stale_indicators_and_empty_groups(self):
        load_sample()
        catalog = sample_catalog()
        catalog['indicators'] = [item for item in catalog['indicators'] if item['category'] == 'Economic']
        catalog['categories'] = catalog['categories'][:1]
        import_catalog(catalog)
        self.assertEqual(set(Indicator.objects.values_list('key', flat=True)), {'gdp_growth', 'exports_usd'})
        self.assertFalse(Category.objects.filter(name='Elections').exists())

    def test_duplicate_keys_fail_atomically(self):
        catalog = sample_catalog()
        catalog['indicators'].append(dict(catalog['indicators'][0]))
        with self.assertRaises(ValueError):
            import_catalog(catalog)
        self.assertEqual(Indicator.objects.count(), 0)

    def test_unknown_category_is_created_on_the_fly(self):
        catalog = sample_catalog()
        catalog['indicators'][0]['category'] = 'Brand New'
        catalog['indicators'][0]['subgroup'] = 'Fresh'
        import_catalog(catalog)
        self.assertEqual(Indicator.objects.get(key='gdp_growth').subgroup.name, 'Fresh')

    def test_preview_downsamples_time_series_but_not_categories(self):
        labels = [str(year) for year in range(1900, 2000)]
        datasets = [{'label': 'x', 'values': list(range(100))}]
        preview = build_preview(labels, datasets, 'line')
        self.assertLessEqual(len(preview['labels']), 40)
        self.assertEqual(preview['labels'][0], '1900')
        self.assertEqual(preview['labels'][-1], '1999')
        self.assertEqual(len(build_preview(labels, datasets, 'bar')['labels']), 100)
        self.assertEqual(len(build_preview(labels, datasets, 'doughnut')['labels']), 100)

    def test_parse_published_handles_rss_iso_and_garbage(self):
        self.assertEqual(parse_published('Mon, 01 Jan 2024 10:00:00 GMT').year, 2024)
        self.assertEqual(parse_published('2026-04-02T08:00:00Z').month, 4)
        self.assertIsNotNone(parse_published('2026-04-02').tzinfo)
        self.assertIsNone(parse_published('not a date'))
        self.assertIsNone(parse_published(''))

    @staticmethod
    def make_user():
        from django.contrib.auth import get_user_model
        return get_user_model().objects.create_user('saver', password='Strong-pass-123')


class ManagementCommandTests(TestCase):
    def test_import_catalog_command_reads_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'catalog.json'
            path.write_text(json.dumps(sample_catalog()), encoding='utf-8')
            out = StringIO()
            call_command('import_catalog', path=str(path), stdout=out)
        self.assertIn('Imported 4 indicators (3 live)', out.getvalue())
        self.assertEqual(DataRefresh.objects.filter(status='success').count(), 1)

    def test_import_catalog_command_missing_file(self):
        with self.assertRaises(CommandError):
            call_command('import_catalog', path='does-not-exist.json')

    def test_import_catalog_command_records_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'catalog.json'
            path.write_text('{"indicators": [{"key": "broken"}]}', encoding='utf-8')
            with self.assertRaises(CommandError):
                call_command('import_catalog', path=str(path))
        self.assertEqual(DataRefresh.objects.get().status, 'failed')

    def test_refresh_data_can_skip_pipelines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'catalog.json'
            path.write_text(json.dumps(sample_catalog()), encoding='utf-8')
            with self.settings(CATALOG_PATH=path):
                out = StringIO()
                call_command('refresh_data', skip_collect=True, skip_export=True, stdout=out)
        self.assertEqual(Indicator.objects.count(), 4)

    def test_repository_catalog_is_importable(self):
        if not settings.CATALOG_PATH.exists():
            self.skipTest('data/catalog.json has not been exported')
        call_command('import_catalog', stdout=StringIO())
        self.assertGreater(Indicator.objects.count(), 500)
        self.assertGreaterEqual(Category.objects.count(), 13)
        self.assertGreater(Indicator.objects.filter(chart_type__in=['pie', 'doughnut']).count(), 100)
        self.assertGreater(Article.objects.count(), 0)

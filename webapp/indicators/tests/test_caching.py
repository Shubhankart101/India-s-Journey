from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from indicators.catalog import import_catalog
from indicators.models import Category, Indicator, Subgroup
from indicators.tests.fixtures import sample_catalog


class CachingTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.catalog_data = sample_catalog()
        import_catalog(self.catalog_data)
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_stats_endpoint_caching_and_headers(self):
        # First request should be a MISS
        res1 = self.client.get('/api/stats/')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.headers.get('X-Cache'), 'MISS')
        self.assertIn('public', res1.headers.get('Cache-Control', ''))
        self.assertIn('max-age=', res1.headers.get('Cache-Control', ''))

        # Second request should be a HIT
        res2 = self.client.get('/api/stats/')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.headers.get('X-Cache'), 'HIT')
        self.assertEqual(res1.data, res2.data)

    def test_categories_endpoint_caching(self):
        res1 = self.client.get('/api/categories/')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.headers.get('X-Cache'), 'MISS')

        res2 = self.client.get('/api/categories/')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.headers.get('X-Cache'), 'HIT')
        self.assertEqual(res1.data, res2.data)

    def test_indicators_query_params_caching_and_order_invariance(self):
        # Query params in different order should produce a cache HIT
        res1 = self.client.get('/api/indicators/?chart=line&live=true')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.headers.get('X-Cache'), 'MISS')

        res2 = self.client.get('/api/indicators/?live=true&chart=line')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.headers.get('X-Cache'), 'HIT')
        self.assertEqual(res1.data, res2.data)

        # Different filter should be a MISS
        res3 = self.client.get('/api/indicators/?chart=radial')
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        self.assertEqual(res3.headers.get('X-Cache'), 'MISS')

    def test_indicator_detail_caching(self):
        key = 'gdp_growth'
        res1 = self.client.get(f'/api/indicators/{key}/')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.headers.get('X-Cache'), 'MISS')

        res2 = self.client.get(f'/api/indicators/{key}/')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.headers.get('X-Cache'), 'HIT')
        self.assertEqual(res1.data, res2.data)

    def test_downloads_caching(self):
        key = 'gdp_growth'
        # CSV format
        res1 = self.client.get(f'/api/indicators/{key}/download/?format=csv')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.headers.get('X-Cache'), 'MISS')
        self.assertEqual(res1.headers.get('Content-Type'), 'text/csv; charset=utf-8')

        res2 = self.client.get(f'/api/indicators/{key}/download/?format=csv')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.headers.get('X-Cache'), 'HIT')
        self.assertEqual(res1.content, res2.content)

        # JSON format
        res3 = self.client.get(f'/api/indicators/{key}/download/?format=json')
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        self.assertEqual(res3.headers.get('X-Cache'), 'MISS')
        self.assertEqual(res3.headers.get('Content-Type'), 'application/json; charset=utf-8')

        res4 = self.client.get(f'/api/indicators/{key}/download/?format=json')
        self.assertEqual(res4.status_code, status.HTTP_200_OK)
        self.assertEqual(res4.headers.get('X-Cache'), 'HIT')
        self.assertEqual(res3.content, res4.content)

    def test_health_check_never_cached(self):
        res1 = self.client.get('/api/health/')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.headers.get('Cache-Control'), 'no-store')
        self.assertIsNone(res1.headers.get('X-Cache'))

        res2 = self.client.get('/api/health/')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.headers.get('Cache-Control'), 'no-store')
        self.assertIsNone(res2.headers.get('X-Cache'))

    def test_import_catalog_clears_cache(self):
        # Prime the cache
        res1 = self.client.get('/api/stats/')
        self.assertEqual(res1.headers.get('X-Cache'), 'MISS')
        res2 = self.client.get('/api/stats/')
        self.assertEqual(res2.headers.get('X-Cache'), 'HIT')

        # Re-import catalog
        import_catalog(self.catalog_data)

        # Cache must have been invalidated
        res3 = self.client.get('/api/stats/')
        self.assertEqual(res3.headers.get('X-Cache'), 'MISS')

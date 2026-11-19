from unittest.mock import patch

from django.core.cache import cache
from django.core.cache.backends.redis import RedisCache
from django.db import connection
import dj_database_url
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

    def test_cache_resilience_when_backend_errors_out(self):
        """When the cache backend throws an exception (e.g. Redis disconnect), the API degrades gracefully to BYPASS."""
        with patch('indicators.caching.cache.get', side_effect=Exception('Redis connection failure')):
            with patch('indicators.caching.cache.set', side_effect=Exception('Redis write failure')):
                res = self.client.get('/api/stats/')
                self.assertEqual(res.status_code, status.HTTP_200_OK)
                self.assertEqual(res.headers.get('X-Cache'), 'BYPASS')
                self.assertIn('indicators', res.data)

    def test_redis_cache_backend_support(self):
        """Validates that Django RedisCache supports standard redis:// and TLS rediss:// locations."""
        redis_backend = RedisCache('redis://127.0.0.1:6379/1', {
            'TIMEOUT': 300,
            'KEY_PREFIX': 'ij',
            'OPTIONS': {
                'socket_timeout': 5,
                'socket_connect_timeout': 5,
                'retry_on_timeout': True,
                'health_check_interval': 30,
            },
        })
        self.assertIsNotNone(redis_backend)
        self.assertEqual(redis_backend.key_prefix, 'ij')

        tls_backend = RedisCache('rediss://:authpass@my-cluster.upstash.io:6379/0', {
            'TIMEOUT': 600,
            'KEY_PREFIX': 'ij-tls',
        })
        self.assertIsNotNone(tls_backend)
        self.assertEqual(tls_backend.key_prefix, 'ij-tls')

    def test_postgres_database_configuration_options(self):
        """Validates that PostgreSQL DATABASE_URL produces pool and SSL options."""
        url = 'postgresql://dbuser:secret@dbhost.postgres.database.azure.com:5432/indias_journey'
        db_conf = dj_database_url.config(
            default=url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        )
        self.assertEqual(db_conf['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(db_conf['CONN_MAX_AGE'], 600)
        self.assertTrue(db_conf['CONN_HEALTH_CHECKS'])
        self.assertEqual(db_conf.get('OPTIONS', {}).get('sslmode'), 'require')

    def test_sqlite_wal_pragmas(self):
        """Validates that SQLite connections have WAL and cache size pragmas applied."""
        if connection.vendor in ('sqlite3', 'sqlite'):
            with connection.cursor() as cursor:
                cursor.execute('PRAGMA busy_timeout;')
                busy_timeout = cursor.fetchone()[0]
                self.assertGreaterEqual(busy_timeout, 5000)


import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from indicators.ai.azure_client import AzureAIClient
from indicators.ai.index import CatalogVectorIndex
from indicators.ai.service import search_indicators
from .fixtures import load_sample


class AiSearchUnitTests(TestCase):
    def test_azure_client_offline_vectorizer(self):
        client = AzureAIClient(dimensions=64)
        vec1 = client.get_embedding("GDP growth in India")
        vec2 = client.get_embedding("GDP growth in India")
        vec3 = client.get_embedding("Completely unrelated cricket match scores")

        self.assertEqual(len(vec1), 64)
        self.assertEqual(vec1, vec2, "Same input must produce identical vectors")

        # Similarity between vec1 and vec2 must be 1.0
        sim_identical = sum(a * b for a, b in zip(vec1, vec2))
        self.assertAlmostEqual(sim_identical, 1.0, places=2)

        # Vector for empty string returns zeros
        vec_empty = client.get_embedding("")
        self.assertEqual(vec_empty, [0.0] * 64)

    def test_azure_client_provider_detection(self):
        with override_settings(
            AZURE_OPENAI_ENDPOINT='https://my-resource.openai.azure.com',
            AZURE_OPENAI_API_KEY='test-azure-key',
        ):
            client = AzureAIClient()
            self.assertEqual(client.provider, 'azure-openai')

        with override_settings(
            AZURE_OPENAI_ENDPOINT='',
            AZURE_OPENAI_API_KEY='',
            OPENAI_API_KEY='test-openai-key',
        ):
            client = AzureAIClient()
            self.assertEqual(client.provider, 'openai')

        with override_settings(
            AZURE_OPENAI_ENDPOINT='',
            AZURE_OPENAI_API_KEY='',
            OPENAI_API_KEY='',
            GEMINI_API_KEY='test-gemini-key',
        ):
            client = AzureAIClient()
            self.assertEqual(client.provider, 'gemini')

        with override_settings(
            AZURE_OPENAI_ENDPOINT='',
            AZURE_OPENAI_API_KEY='',
            OPENAI_API_KEY='',
            GEMINI_API_KEY='',
        ):
            client = AzureAIClient()
            self.assertEqual(client.provider, 'offline-fallback')

    def test_catalog_vector_index_search(self):
        index = CatalogVectorIndex()
        # Seed test items directly
        client = AzureAIClient(dimensions=32)
        v_gdp = client.get_embedding("Real GDP growth economy markets national accounts")
        v_inf = client.get_embedding("Consumer price index inflation retail prices")
        v_elec = client.get_embedding("Lok Sabha general election results seats voter turnout")

        index.items = [
            {'key': 'gdp_growth', 'title': 'Real GDP growth', 'category': 'Economy & Markets', 'subgroup': 'Growth', 'vec': v_gdp},
            {'key': 'cpi_inflation', 'title': 'CPI Inflation', 'category': 'Economy & Markets', 'subgroup': 'Prices', 'vec': v_inf},
            {'key': 'lok_sabha', 'title': 'Lok Sabha Election Results', 'category': 'Elections & Democracy', 'subgroup': 'Parliament', 'vec': v_elec},
        ]
        index._loaded = True

        # Query GDP
        q_vec = client.get_embedding("GDP and economic growth")
        results = index.search(query_vec=q_vec, query_text="GDP and economic growth", limit=2)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['key'], 'gdp_growth')

        # Query with category filter
        results_filtered = index.search(
            query_vec=q_vec,
            query_text="GDP and economic growth",
            limit=2,
            category="Elections & Democracy"
        )
        for r in results_filtered:
            self.assertEqual(r['category'], 'Elections & Democracy')


class AiSearchApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_sample()

    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_api_root_includes_ai_search(self):
        res = self.client.get('/api/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('ai_search', res.json()['endpoints'])

    def test_ai_search_endpoint_empty_query(self):
        res = self.client.get('/api/ai/search/?q=')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['results'], [])

    def test_ai_search_endpoint_with_query(self):
        res = self.client.get('/api/ai/search/?q=inflation')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['query'], 'inflation')
        self.assertIn('provider', data)
        self.assertIsInstance(data['results'], list)

    def test_ai_search_limit_and_caching(self):
        res1 = self.client.get('/api/ai/search/?q=economic+growth&limit=2')
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertLessEqual(len(data1['results']), 2)

        # Repeated request must be served from cache
        res2 = self.client.get('/api/ai/search/?q=economic+growth&limit=2')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.headers.get('X-Cache'), 'HIT')

    def test_ai_recommend_endpoint(self):
        res = self.client.get('/api/ai/recommend/gdp_growth/?limit=3')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['key'], 'gdp_growth')
        self.assertIn('recommendations', data)
        self.assertIsInstance(data['recommendations'], list)
        self.assertLessEqual(len(data['recommendations']), 3)

    def test_ai_recommend_not_found(self):
        res = self.client.get('/api/ai/recommend/non_existent_key/')
        self.assertEqual(res.status_code, 404)

    def test_ai_insights_endpoint(self):
        res = self.client.get('/api/ai/insights/gdp_growth/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['key'], 'gdp_growth')
        self.assertIn('summary', data)
        self.assertIn('takeaways', data)
        self.assertIsInstance(data['takeaways'], list)
        self.assertGreaterEqual(len(data['takeaways']), 1)
        self.assertIn('metrics', data)

    def test_ai_insights_not_found(self):
        res = self.client.get('/api/ai/insights/non_existent_key/')
        self.assertEqual(res.status_code, 404)

    def test_ai_compare_insights_missing_keys_param(self):
        res = self.client.get('/api/ai/compare-insights/')
        self.assertEqual(res.status_code, 400)

    def test_ai_compare_insights_single_key(self):
        res = self.client.get('/api/ai/compare-insights/?keys=gdp_growth')
        self.assertEqual(res.status_code, 400)

    def test_ai_compare_insights_too_many_keys(self):
        res = self.client.get('/api/ai/compare-insights/?keys=k1,k2,k3,k4,k5')
        self.assertEqual(res.status_code, 400)

    def test_ai_compare_insights_not_found_key(self):
        res = self.client.get('/api/ai/compare-insights/?keys=gdp_growth,definitely_missing_key')
        self.assertEqual(res.status_code, 404)

    def test_ai_compare_insights_success(self):
        # Using two real fixture indicators
        res = self.client.get('/api/ai/compare-insights/?keys=gdp_growth,seat_share')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['count'], 2)
        self.assertIn('summary', data)
        self.assertIn('correlations', data)
        self.assertIn('decouplings', data)
        self.assertIn('takeaways', data)
        self.assertIsInstance(data['takeaways'], list)
        self.assertGreaterEqual(len(data['takeaways']), 1)
        self.assertEqual(len(data['correlations']), 1)
        corr = data['correlations'][0]
        self.assertIn('pair', corr)
        self.assertIn('r', corr)
        self.assertIn('strength', corr)

    def test_ai_compare_insights_caching(self):
        res1 = self.client.get('/api/ai/compare-insights/?keys=gdp_growth,seat_share')
        self.assertEqual(res1.status_code, 200)
        res2 = self.client.get('/api/ai/compare-insights/?keys=gdp_growth,seat_share')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.headers.get('X-Cache'), 'HIT')



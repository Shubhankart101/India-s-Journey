import json
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from indicators.models import SavedChart

from .fixtures import load_sample


class ApiTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_sample()

    def setUp(self):
        cache.clear()
        self.client = APIClient()


class PublicApiTests(ApiTestCase):
    def test_api_root_lists_endpoints(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('indicators', response.json()['endpoints'])

    def test_health(self):
        self.assertEqual(self.client.get('/api/health/').json(), {'status': 'ok', 'indicators': 4})

    def test_categories_include_counts_and_subgroups(self):
        data = self.client.get('/api/categories/').json()
        self.assertEqual([item['slug'] for item in data], ['economic', 'elections'])
        economic = data[0]
        self.assertEqual((economic['indicator_count'], economic['live_count']), (2, 2))
        self.assertEqual([sub['slug'] for sub in economic['subgroups']], ['macro-overview', 'trade'])
        elections = data[1]
        self.assertEqual((elections['indicator_count'], elections['live_count']), (2, 1))
        self.assertEqual(elections['subgroups'][0]['indicator_count'], 2)

    def test_indicator_list_is_paginated_summaries_without_full_data(self):
        data = self.client.get('/api/indicators/', {'page_size': 2}).json()
        self.assertEqual(data['count'], 4)
        self.assertEqual(len(data['results']), 2)
        self.assertIsNotNone(data['next'])
        first = data['results'][0]
        self.assertEqual(first['key'], 'gdp_growth')
        self.assertNotIn('labels', first)
        self.assertNotIn('datasets', first)
        self.assertLessEqual(len(first['preview']['labels']), 40)

    def test_page_size_is_capped(self):
        response = self.client.get('/api/indicators/', {'page_size': 10000})
        self.assertEqual(response.status_code, 200)

    def test_search_matches_all_terms_case_insensitively(self):
        keys = lambda params: [item['key'] for item in self.client.get('/api/indicators/', params).json()['results']]
        self.assertEqual(keys({'q': 'GDP'}), ['gdp_growth'])
        self.assertEqual(keys({'q': 'lok seat'}), ['seat_share'])
        self.assertEqual(keys({'q': 'economic exports'}), ['exports_usd'])
        self.assertEqual(keys({'q': 'nothing-matches-this'}), [])

    def test_filters_by_category_subgroup_live_and_chart(self):
        keys = lambda params: sorted(item['key'] for item in self.client.get('/api/indicators/', params).json()['results'])
        self.assertEqual(keys({'category': 'elections'}), ['pending_series', 'seat_share'])
        self.assertEqual(keys({'category': 'economic', 'subgroup': 'trade'}), ['exports_usd'])
        self.assertEqual(keys({'live': 'false'}), ['pending_series'])
        self.assertEqual(keys({'live': 'true', 'category': 'elections'}), ['seat_share'])
        self.assertEqual(keys({'chart': 'radial'}), ['seat_share'])

    def test_sorting_and_invalid_sort(self):
        titles = [item['title'] for item in self.client.get('/api/indicators/', {'sort': 'title'}).json()['results']]
        self.assertEqual(titles, sorted(titles))
        self.assertEqual(self.client.get('/api/indicators/', {'sort': 'nope'}).status_code, 400)

    def test_indicator_detail_has_full_series_related_and_neighbours(self):
        data = self.client.get('/api/indicators/exports_usd/').json()
        self.assertEqual(data['labels'], ['2022', '2023', '2024'])
        self.assertEqual(len(data['datasets']), 2)
        self.assertEqual(data['category'], 'Economic')
        self.assertFalse(data['is_saved'])
        self.assertEqual(data['previous_key'], 'gdp_growth')
        self.assertIsNone(data['next_key'])
        self.assertEqual(data['related'], [])
        self.assertEqual(self.client.get('/api/indicators/does_not_exist/').status_code, 404)

    def test_csv_download(self):
        response = self.client.get('/api/indicators/exports_usd/download/', {'format': 'csv'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment; filename="exports_usd.csv"', response['Content-Disposition'])
        lines = response.content.decode().strip().splitlines()
        self.assertEqual(lines[0], 'label,Exports,Imports')
        self.assertEqual(lines[2], '2023,431000000000.0,')

    def test_json_download_and_bad_format(self):
        response = self.client.get('/api/indicators/seat_share/download/', {'format': 'json'})
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['labels'], ['BJP', 'INC', 'SP'])
        self.assertEqual(payload['category'], 'Elections')
        self.assertEqual(self.client.get('/api/indicators/seat_share/download/', {'format': 'xml'}).status_code, 400)
        self.assertEqual(self.client.get('/api/indicators/missing/download/').status_code, 404)

    def test_compare_aligns_labels(self):
        data = self.client.get('/api/compare/', {'keys': 'gdp_growth,exports_usd,missing'}).json()
        self.assertEqual(data['missing'], ['missing'])
        self.assertEqual(len(data['labels']), 64)
        self.assertEqual(data['labels'], sorted(data['labels']))
        exports = data['series'][1]
        self.assertEqual(exports['values'][data['labels'].index('2023')], 431e9)
        self.assertIsNone(exports['values'][0])

    def test_compare_validation(self):
        self.assertEqual(self.client.get('/api/compare/').status_code, 400)
        self.assertEqual(self.client.get('/api/compare/', {'keys': 'a,b,c,d,e'}).status_code, 400)
        data = self.client.get('/api/compare/', {'keys': 'gdp_growth,gdp_growth'}).json()
        self.assertEqual(len(data['series']), 1)

    def test_articles_are_newest_first_and_filterable(self):
        data = self.client.get('/api/articles/').json()
        self.assertEqual([item['title'] for item in data['results']], ['Newer article', 'Older article'])
        self.assertEqual(self.client.get('/api/articles/', {'kind': 'indian_matrix'}).json()['count'], 1)
        self.assertEqual(self.client.get('/api/articles/', {'q': 'newer'}).json()['count'], 1)

    def test_stats(self):
        data = self.client.get('/api/stats/').json()
        self.assertEqual(data['indicators'], 4)
        self.assertEqual(data['live_indicators'], 3)
        self.assertEqual(data['radial_indicators'], 1)
        self.assertEqual(data['categories'], 2)
        self.assertEqual(data['source_generated_at'], '2026-05-01T00:00:00+00:00')

    def test_list_endpoint_query_count_is_constant(self):
        with self.assertNumQueries(2):
            self.client.get('/api/indicators/')


class AuthAndSavedChartTests(ApiTestCase):
    password = 'Strong-pass-123'

    def register(self, username='asha'):
        return self.client.post('/api/auth/register/', {'username': username, 'password': self.password, 'email': 'a@example.com'}, format='json')

    def test_me_is_anonymous_by_default_and_sets_csrf_cookie(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.json(), {'authenticated': False, 'user': None})
        self.assertIn('csrftoken', response.cookies)

    def test_register_logs_in(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['user']['username'], 'asha')
        self.assertTrue(self.client.get('/api/auth/me/').json()['authenticated'])

    def test_register_validation(self):
        self.register()
        self.client.post('/api/auth/logout/')
        duplicate = self.client.post('/api/auth/register/', {'username': 'ASHA', 'password': self.password}, format='json')
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn('username', duplicate.json())
        weak = self.client.post('/api/auth/register/', {'username': 'ravi', 'password': '123'}, format='json')
        self.assertEqual(weak.status_code, 400)
        bad_name = self.client.post('/api/auth/register/', {'username': 'a b', 'password': self.password}, format='json')
        self.assertEqual(bad_name.status_code, 400)

    def test_login_logout(self):
        get_user_model().objects.create_user('meera', password=self.password)
        bad = self.client.post('/api/auth/login/', {'username': 'meera', 'password': 'wrong'}, format='json')
        self.assertEqual(bad.status_code, 400)
        good = self.client.post('/api/auth/login/', {'username': 'meera', 'password': self.password}, format='json')
        self.assertEqual(good.status_code, 200)
        self.assertEqual(good.json()['user']['saved_count'], 0)
        self.client.post('/api/auth/logout/')
        self.assertFalse(self.client.get('/api/auth/me/').json()['authenticated'])

    def test_session_writes_require_csrf_token(self):
        get_user_model().objects.create_user('csrf', password=self.password)
        client = APIClient(enforce_csrf_checks=True)
        client.post('/api/auth/login/', {'username': 'csrf', 'password': self.password}, format='json')
        blocked = client.post('/api/saved/', {'key': 'gdp_growth'}, format='json')
        self.assertEqual(blocked.status_code, 403)
        token = client.get('/api/auth/me/').cookies['csrftoken'].value
        allowed = client.post('/api/saved/', {'key': 'gdp_growth'}, format='json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(allowed.status_code, 201)

    def test_saved_charts_require_login(self):
        self.assertEqual(self.client.get('/api/saved/').status_code, 403)
        self.assertEqual(self.client.post('/api/saved/', {'key': 'gdp_growth'}, format='json').status_code, 403)
        self.assertEqual(self.client.delete('/api/saved/gdp_growth/').status_code, 403)

    def test_saved_chart_crud(self):
        self.register()
        created = self.client.post('/api/saved/', {'key': 'gdp_growth', 'note': 'watch'}, format='json')
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()['indicator']['key'], 'gdp_growth')
        again = self.client.post('/api/saved/', {'key': 'gdp_growth', 'note': 'updated'}, format='json')
        self.assertEqual(again.status_code, 200)
        listing = self.client.get('/api/saved/').json()
        self.assertEqual([(item['indicator']['key'], item['note']) for item in listing], [('gdp_growth', 'updated')])
        self.assertTrue(self.client.get('/api/indicators/gdp_growth/').json()['is_saved'])
        self.assertEqual(self.client.post('/api/saved/', {'key': 'nope'}, format='json').status_code, 400)
        self.assertEqual(self.client.delete('/api/saved/gdp_growth/').status_code, 204)
        self.assertEqual(self.client.delete('/api/saved/gdp_growth/').status_code, 404)
        self.assertEqual(self.client.get('/api/saved/').json(), [])

    def test_saved_charts_are_private_per_user(self):
        self.register('first')
        self.client.post('/api/saved/', {'key': 'seat_share'}, format='json')
        self.client.post('/api/auth/logout/')
        self.register('second')
        self.assertEqual(self.client.get('/api/saved/').json(), [])
        self.assertEqual(self.client.delete('/api/saved/seat_share/').status_code, 404)
        self.assertEqual(SavedChart.objects.count(), 1)

    def test_auth_endpoints_are_throttled(self):
        statuses = [
            self.client.post('/api/auth/login/', {'username': 'x', 'password': 'y'}, format='json').status_code
            for _ in range(25)
        ]
        self.assertIn(429, statuses)


class SpaAndAdminTests(ApiTestCase):
    def test_spa_routes_serve_built_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'index.html').write_text('<div id="root"></div>', encoding='utf-8')
            with override_settings(FRONTEND_DIST=Path(tmp)):
                for url in ['/', '/explore', '/indicator/gdp_growth', '/compare?keys=a']:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 200, url)
                    self.assertIn(b'id="root"', b''.join(response.streaming_content))

    def test_spa_reports_missing_build(self):
        with override_settings(FRONTEND_DIST=Path('/definitely/missing')):
            self.assertEqual(self.client.get('/explore').status_code, 503)

    def test_unknown_api_routes_are_not_swallowed_by_spa(self):
        self.assertEqual(self.client.get('/api/unknown/').status_code, 404)

    def test_admin_lists_models_for_staff(self):
        get_user_model().objects.create_superuser('admin', 'admin@example.com', 'Admin-pass-123')
        self.client.login(username='admin', password='Admin-pass-123')
        for url in ['/admin/', '/admin/indicators/indicator/', '/admin/indicators/article/',
                    '/admin/indicators/category/', '/admin/indicators/savedchart/', '/admin/indicators/datarefresh/',
                    '/admin/indicators/indicator/?q=gdp']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_admin_requires_staff(self):
        response = self.client.get('/admin/indicators/indicator/')
        self.assertEqual(response.status_code, 302)

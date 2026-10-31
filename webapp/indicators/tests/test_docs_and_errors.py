"""OpenAPI / Swagger docs, error pages with the GitHub Pages backup link, and API hardening."""
from pathlib import Path
from unittest import mock

import yaml
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .fixtures import load_sample

BACKUP = 'https://shubhankart101.github.io/India-s-Journey/'


class DocsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_sample()

    def setUp(self):
        self.client = APIClient()

    def schema(self):
        response = self.client.get('/api/schema/', HTTP_ACCEPT='application/vnd.oai.openapi')
        self.assertEqual(response.status_code, 200)
        return yaml.safe_load(response.content)


class SchemaTests(DocsTestCase):
    def test_schema_is_openapi_3_and_documents_every_endpoint(self):
        schema = self.schema()
        self.assertTrue(schema['openapi'].startswith('3.'))
        self.assertEqual(schema['info']['title'], "India's Journey API")
        self.assertEqual(set(schema['paths']), {
            '/api/', '/api/health/', '/api/categories/', '/api/indicators/', '/api/indicators/{key}/',
            '/api/indicators/{key}/download/', '/api/compare/', '/api/articles/', '/api/stats/',
            '/api/auth/csrf/', '/api/auth/me/', '/api/auth/providers/', '/api/auth/logout/',
            '/api/saved/', '/api/saved/{key}/',
        })

    def test_schema_has_no_password_endpoints(self):
        paths = self.schema()['paths']
        self.assertNotIn('/api/auth/login/', paths)
        self.assertNotIn('/api/auth/register/', paths)

    def test_schema_methods(self):
        paths = self.schema()['paths']
        self.assertEqual(set(paths['/api/saved/']), {'get', 'post'})
        self.assertIn('delete', paths['/api/saved/{key}/'])
        self.assertNotIn('post', paths['/api/saved/{key}/'])
        self.assertIn('post', paths['/api/auth/logout/'])
        self.assertNotIn('get', paths['/api/auth/logout/'])

    def test_query_parameters_are_documented(self):
        paths = self.schema()['paths']
        names = {p['name'] for p in paths['/api/indicators/']['get']['parameters']}
        self.assertTrue({'q', 'category', 'subgroup', 'live', 'chart', 'sort', 'page', 'page_size'} <= names)
        download = {p['name']: p for p in paths['/api/indicators/{key}/download/']['get']['parameters']}
        self.assertEqual(download['format']['schema']['enum'], ['csv', 'json'])
        compare = {p['name']: p for p in paths['/api/compare/']['get']['parameters']}
        self.assertTrue(compare['keys']['required'])

    def test_download_documents_both_media_types(self):
        content = self.schema()['paths']['/api/indicators/{key}/download/']['get']['responses']['200']['content']
        self.assertEqual(set(content), {'text/csv', 'application/json'})

    def test_session_auth_and_csrf_are_described(self):
        schema = self.schema()
        self.assertIn('cookieAuth', schema['components']['securitySchemes'])

    def test_schema_json_format(self):
        response = self.client.get('/api/schema/?format=json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('paths', response.json())

    def test_concurrent_schema_requests_do_not_crash(self):
        from concurrent.futures import ThreadPoolExecutor

        def fetch(_):
            return APIClient(raise_request_exception=False).get('/api/schema/?format=json').status_code

        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(set(pool.map(fetch, range(16))), {200})

    def test_documented_responses_match_live_payloads(self):
        schema = self.schema()
        components = schema['components']['schemas']

        def properties(ref):
            return set(components[ref.split('/')[-1]]['properties'])

        def ref_for(path, code='200'):
            body = schema['paths'][path]['get']['responses'][code]['content']['application/json']['schema']
            return body.get('$ref') or body.get('items', {}).get('$ref')

        stats = self.client.get('/api/stats/').json()
        self.assertEqual(set(stats), properties(ref_for('/api/stats/')))
        health = self.client.get('/api/health/').json()
        self.assertEqual(set(health), properties(ref_for('/api/health/')))
        detail = self.client.get('/api/indicators/gdp_growth/').json()
        self.assertTrue(properties(ref_for('/api/indicators/{key}/')) <= set(detail))
        compare = self.client.get('/api/compare/?keys=gdp_growth,exports_usd').json()
        self.assertEqual(set(compare), properties(ref_for('/api/compare/')))
        page = self.client.get('/api/indicators/').json()
        self.assertEqual(set(page), properties(ref_for('/api/indicators/')))
        categories = self.client.get('/api/categories/').json()
        self.assertEqual(set(categories[0]), properties(ref_for('/api/categories/')))
        providers = schema['paths']['/api/auth/providers/']['get']['responses']['200']['content']['application/json']['schema']
        self.assertEqual(providers['type'], 'array')

    def test_every_documented_get_endpoint_responds(self):
        user = get_user_model().objects.create_user('docs', 'docs@example.com')
        self.client.force_login(user)
        samples = {'{key}': 'gdp_growth'}
        for path, operations in self.schema()['paths'].items():
            if 'get' not in operations:
                continue
            url = path
            for token, value in samples.items():
                url = url.replace(token, value)
            if path == '/api/compare/':
                url += '?keys=gdp_growth'
            response = self.client.get(url)
            self.assertLess(response.status_code, 400, f'{url} -> {response.status_code}')


class SwaggerUiTests(DocsTestCase):
    def test_swagger_ui_is_served_from_sidecar_not_cdn(self):
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('swagger-ui', html)
        self.assertIn('/static/drf_spectacular_sidecar/swagger-ui-dist/', html)
        self.assertNotIn('cdn.jsdelivr.net', html)

    def test_swagger_ui_sends_csrf_token_for_try_it_out(self):
        self.client.get('/api/auth/csrf/')
        response = self.client.get('/api/docs/')
        script_url = '/api/docs/?script='
        script = self.client.get(script_url).content.decode() if 'script=' in response.content.decode() else response.content.decode()
        self.assertIn('X-CSRFTOKEN', script.upper())

    def test_redoc_is_served(self):
        response = self.client.get('/api/redoc/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('redoc', response.content.decode().lower())

    def test_api_root_links_docs_and_backup(self):
        body = self.client.get('/api/').json()
        self.assertEqual(body['docs']['swagger'], '/api/docs/')
        self.assertEqual(body['backup_url'], BACKUP)
        self.assertNotIn('/api/auth/login/', body['endpoints']['auth'])


@override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver'])
class ErrorPageTests(DocsTestCase):
    def test_html_404_links_backup_site(self):
        # Non-API paths are owned by the SPA, so an unknown /accounts/ path exercises Django's 404 handler.
        response = self.client.get('/accounts/definitely-missing/', HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, BACKUP, status_code=404)
        self.assertContains(response, 'status.html', status_code=404)
        self.assertContains(response, 'wandered off', status_code=404)

    def test_api_404_is_json_with_backup(self):
        response = self.client.get('/api/nope/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['backup_url'], BACKUP)

    @override_settings(DEBUG=True)
    def test_unknown_api_paths_are_json_404_for_any_method_even_in_debug(self):
        client = APIClient(enforce_csrf_checks=True)
        for method in ('get', 'post', 'put', 'delete'):
            response = getattr(client, method)('/api/auth/login/')
            self.assertEqual(response.status_code, 404, method)
            self.assertEqual(response.json()['detail'], 'Not found.')
        self.assertEqual(client.get('/api/health').status_code, 301)

    def test_unknown_indicator_is_json_404(self):
        response = self.client.get('/api/indicators/does-not-exist/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('detail', response.json())

    def test_500_page_links_backup_site(self):
        from indicators import views

        client = APIClient(raise_request_exception=False)
        with mock.patch.object(views.StatsView, 'get', side_effect=RuntimeError('boom')):
            response = client.get('/api/stats/')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['backup_url'], BACKUP)

    def test_500_html_page_links_backup_site(self):
        from indicators.views import error_500
        from django.test import RequestFactory

        response = error_500(RequestFactory().get('/explore', HTTP_ACCEPT='text/html'))
        self.assertEqual(response.status_code, 500)
        self.assertIn(BACKUP.encode(), response.content)
        self.assertIn(b'Something broke', response.content)

    def test_403_page_links_backup_site(self):
        from indicators.views import error_403
        from django.test import RequestFactory

        response = error_403(RequestFactory().get('/accounts/x', HTTP_ACCEPT='text/html'))
        self.assertEqual(response.status_code, 403)
        self.assertIn(BACKUP.encode(), response.content)

    def test_missing_frontend_build_is_503_html_with_backup(self):
        with override_settings(FRONTEND_DIST=Path('/definitely/missing')):
            response = self.client.get('/explore', HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, BACKUP, status_code=503)

    @override_settings(BACKUP_SITE_URL='https://mirror.example/', BACKUP_STATUS_URL='https://mirror.example/status.html')
    def test_backup_url_is_configurable(self):
        self.assertEqual(self.client.get('/api/health/').json()['backup_url'], 'https://mirror.example/')
        self.assertContains(self.client.get('/accounts/missing/'), 'https://mirror.example/status.html', status_code=404)


class HardeningTests(DocsTestCase):
    def test_hostile_search_input_is_harmless(self):
        for q in ["' OR 1=1 --", '<script>alert(1)</script>', '_', 'x' * 5000, 'ग्रोथ']:
            response = self.client.get('/api/indicators/', {'q': q})
            self.assertIn(response.status_code, (200, 400), q[:20])
            if response.status_code == 200:
                self.assertEqual(response.json()['count'], 0, q[:20])
        self.assertLess(self.client.get('/api/indicators/', {'q': '\x00'}).status_code, 500)

    def test_bad_pagination_values(self):
        self.assertEqual(self.client.get('/api/indicators/?page=999').status_code, 404)
        self.assertEqual(self.client.get('/api/indicators/?page=abc').status_code, 404)
        self.assertEqual(self.client.get('/api/indicators/?page_size=-5').status_code, 200)
        self.assertLessEqual(len(self.client.get('/api/indicators/?page_size=100000').json()['results']), 100)

    def test_unknown_filters_return_empty_not_errors(self):
        self.assertEqual(self.client.get('/api/indicators/?category=nope').json()['count'], 0)
        self.assertEqual(self.client.get('/api/indicators/?chart=nope').status_code, 200)
        self.assertEqual(self.client.get('/api/articles/?kind=nope').json()['count'], 0)

    def test_compare_edge_cases(self):
        self.assertEqual(self.client.get('/api/compare/?keys=,,,').status_code, 400)
        dupes = self.client.get('/api/compare/?keys=gdp_growth,gdp_growth').json()
        self.assertEqual(len(dupes['series']), 1)
        self.assertEqual(self.client.get('/api/compare/?keys=a,b,c,d,e').status_code, 400)
        missing = self.client.get('/api/compare/?keys=gdp_growth,ghost').json()
        self.assertEqual(missing['missing'], ['ghost'])

    def test_read_only_endpoints_reject_writes(self):
        for url in ['/api/indicators/', '/api/indicators/gdp_growth/', '/api/categories/', '/api/stats/', '/api/articles/']:
            self.assertEqual(self.client.post(url, {}).status_code, 405, url)
            self.assertEqual(self.client.delete(url).status_code, 405, url)

    def test_download_ignores_accept_header(self):
        response = self.client.get('/api/indicators/gdp_growth/download/?format=csv', HTTP_ACCEPT='text/csv')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('text/csv'))
        response = self.client.get('/api/indicators/gdp_growth/download/?format=xml', HTTP_ACCEPT='application/xml')
        self.assertEqual(response.status_code, 400)

    def test_download_unknown_indicator(self):
        self.assertEqual(self.client.get('/api/indicators/ghost/download/').status_code, 404)

    def test_csv_download_is_well_formed(self):
        import csv
        import io

        body = self.client.get('/api/indicators/seat_share/download/?format=csv').content.decode()
        rows = list(csv.reader(io.StringIO(body)))
        self.assertGreater(len(rows), 1)
        self.assertTrue(all(len(row) == len(rows[0]) for row in rows))

    def test_responses_are_gzipped_when_requested(self):
        response = self.client.get('/api/indicators/?page_size=100', HTTP_ACCEPT_ENCODING='gzip')
        self.assertEqual(response.get('Content-Encoding'), 'gzip')

    def test_session_and_csrf_cookie_settings(self):
        from django.conf import settings

        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)
        self.assertEqual(settings.SESSION_COOKIE_SAMESITE, 'Lax')
        self.assertFalse(settings.CSRF_COOKIE_HTTPONLY)  # the SPA and Swagger UI read it to send X-CSRFToken

    def test_clickjacking_protection(self):
        self.assertEqual(self.client.get('/api/').get('X-Frame-Options'), 'DENY')

    def test_only_health_is_readable_cross_origin(self):
        health = self.client.get('/api/health/', HTTP_ORIGIN='https://shubhankart101.github.io')
        self.assertEqual(health['Access-Control-Allow-Origin'], '*')
        self.assertEqual(health['Cache-Control'], 'no-store')
        self.assertNotIn('Access-Control-Allow-Credentials', health)
        for url in ['/api/auth/me/', '/api/saved/', '/api/indicators/']:
            self.assertNotIn('Access-Control-Allow-Origin', self.client.get(url, HTTP_ORIGIN='https://evil.example'), url)

    def test_admin_login_is_staff_only(self):
        user = get_user_model().objects.create_user('plain', 'p@example.com', 'Strong-pass-123')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/admin/').status_code, 302)

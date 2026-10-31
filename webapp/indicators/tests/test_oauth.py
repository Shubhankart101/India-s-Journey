"""End-to-end OAuth flows for Google and Microsoft with the provider HTTP calls mocked."""
import json
from unittest import mock
from urllib.parse import parse_qs, urlparse

from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings

from indicators.models import SavedChart

from .fixtures import load_sample

GOOGLE_USER = {
    'id': '1093', 'email': 'asha@gmail.com', 'verified_email': True,
    'name': 'Asha Rao', 'given_name': 'Asha', 'family_name': 'Rao',
}
MICROSOFT_USER = {
    'id': 'ms-42', 'mail': 'ravi@outlook.com', 'userPrincipalName': 'ravi@outlook.com',
    'displayName': 'Ravi Kumar', 'givenName': 'Ravi', 'surname': 'Kumar', 'mailNickname': 'ravi',
}


def providers_settings(google=True, microsoft=True, tenant='common'):
    def app(prefix, **extra):
        return [{'client_id': f'{prefix}-client', 'secret': f'{prefix}-secret', 'key': '', **extra}]

    return {
        'google': {'APPS': app('google') if google else [], 'SCOPE': ['openid', 'profile', 'email'],
                   'AUTH_PARAMS': {'prompt': 'select_account'}, 'OAUTH_PKCE_ENABLED': True},
        'microsoft': {'APPS': app('microsoft', settings={'tenant': tenant}) if microsoft else [], 'SCOPE': ['User.Read'],
                      'AUTH_PARAMS': {'prompt': 'select_account'}, 'OAUTH_PKCE_ENABLED': True},
    }


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = json.dumps(payload)
        self.content = self.text.encode()
        self.headers = {'content-type': 'application/json'}
        self._payload = payload

    def json(self):
        return self._payload


class FakeSession:
    """Stands in for requests.Session: answers the token endpoint and the profile endpoint."""

    def __init__(self, profile, token_status=200, profile_status=200):
        self.profile, self.token_status, self.profile_status = profile, token_status, profile_status
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeResponse({'access_token': 'token-123', 'token_type': 'Bearer', 'expires_in': 3600}, self.token_status)

    def get(self, url, **kwargs):
        self.calls.append(('GET', url, kwargs))
        return FakeResponse(self.profile, self.profile_status)


@override_settings(SOCIALACCOUNT_PROVIDERS=providers_settings())
class OAuthTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_sample()

    def start(self, provider, next_url='/saved'):
        self.client.get('/api/auth/csrf/')
        response = self.client.post(f'/accounts/{provider}/login/', {'next': next_url, 'process': 'login'})
        self.assertEqual(response.status_code, 302)
        return urlparse(response['Location'])

    def finish(self, provider, profile, **session_kwargs):
        authorize = self.start(provider, session_kwargs.pop('next_url', '/saved'))
        state = parse_qs(authorize.query)['state'][0]
        session = FakeSession(profile, **session_kwargs)
        with mock.patch('allauth.socialaccount.adapter.DefaultSocialAccountAdapter.get_requests_session', return_value=session):
            response = self.client.get(f'/accounts/{provider}/login/callback/', {'code': 'auth-code', 'state': state})
        return response, session


class ProviderDiscoveryTests(OAuthTestCase):
    def test_lists_only_google_and_microsoft(self):
        providers = self.client.get('/api/auth/providers/').json()
        self.assertEqual([p['id'] for p in providers], ['google', 'microsoft'])
        self.assertEqual(providers[0]['login_url'], '/accounts/google/login/')
        self.assertEqual(providers[1]['login_url'], '/accounts/microsoft/login/')
        self.assertIn('Outlook', providers[1]['name'])

    @override_settings(SOCIALACCOUNT_PROVIDERS=providers_settings(google=False, microsoft=False))
    def test_lists_nothing_when_unconfigured(self):
        self.assertEqual(self.client.get('/api/auth/providers/').json(), [])

    @override_settings(SOCIALACCOUNT_PROVIDERS=providers_settings(google=True, microsoft=False))
    def test_lists_partially_configured(self):
        self.assertEqual([p['id'] for p in self.client.get('/api/auth/providers/').json()], ['google'])

    @override_settings(SOCIALACCOUNT_PROVIDERS=providers_settings(google=False, microsoft=False))
    def test_admin_configured_social_app_is_listed(self):
        app = SocialApp.objects.create(provider='microsoft', name='Outlook', client_id='db-id', secret='db-secret')
        app.sites.add(Site.objects.get_current())
        self.assertEqual([p['id'] for p in self.client.get('/api/auth/providers/').json()], ['microsoft'])

    @override_settings(SOCIALACCOUNT_PROVIDERS=providers_settings(google=False, microsoft=False))
    def test_unconfigured_provider_redirects_to_login_page(self):
        self.client.get('/api/auth/csrf/')
        response = self.client.post('/accounts/google/login/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/login?error=unavailable')


class RedirectTests(OAuthTestCase):
    def test_google_authorize_url_uses_pkce_and_select_account(self):
        url = self.start('google')
        query = parse_qs(url.query)
        self.assertEqual(url.netloc, 'accounts.google.com')
        self.assertEqual(query['client_id'], ['google-client'])
        self.assertEqual(query['response_type'], ['code'])
        self.assertEqual(query['prompt'], ['select_account'])
        self.assertEqual(query['code_challenge_method'], ['S256'])
        self.assertIn('email', query['scope'][0])
        self.assertTrue(query['redirect_uri'][0].endswith('/accounts/google/login/callback/'))

    def test_microsoft_authorize_url_uses_common_tenant(self):
        url = self.start('microsoft')
        query = parse_qs(url.query)
        self.assertEqual(url.netloc, 'login.microsoftonline.com')
        self.assertTrue(url.path.startswith('/common/oauth2/v2.0/authorize'))
        self.assertEqual(query['client_id'], ['microsoft-client'])
        self.assertEqual(query['scope'], ['User.Read'])
        self.assertIn('code_challenge', query)

    @override_settings(SOCIALACCOUNT_PROVIDERS=providers_settings(tenant='consumers'))
    def test_microsoft_tenant_is_configurable(self):
        self.assertTrue(self.start('microsoft').path.startswith('/consumers/'))

    def test_get_does_not_start_oauth(self):
        response = self.client.get('/accounts/google/login/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Location', response)
        self.assertContains(response, 'github.io')

    def test_login_post_requires_csrf(self):
        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/accounts/google/login/').status_code, 403)

    def test_each_attempt_gets_a_fresh_state(self):
        first = parse_qs(self.start('google').query)['state'][0]
        second = parse_qs(self.start('google').query)['state'][0]
        self.assertNotEqual(first, second)


class CallbackTests(OAuthTestCase):
    def test_google_sign_in_creates_user_and_returns_to_next(self):
        response, session = self.finish('google', GOOGLE_USER)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/saved')
        user = get_user_model().objects.get(email='asha@gmail.com')
        self.assertEqual((user.first_name, user.last_name), ('Asha', 'Rao'))
        self.assertFalse(user.has_usable_password())
        self.assertEqual(SocialAccount.objects.get(user=user).provider, 'google')
        token_call = session.calls[0]
        self.assertEqual(token_call[0], 'POST')
        self.assertEqual(token_call[1], 'https://oauth2.googleapis.com/token')
        self.assertIn('code_verifier', token_call[2]['data'])
        me = self.client.get('/api/auth/me/').json()
        self.assertTrue(me['authenticated'])
        self.assertEqual(me['user']['providers'], ['google'])
        self.assertEqual(me['user']['name'], 'Asha Rao')

    def test_microsoft_sign_in_creates_user(self):
        response, session = self.finish('microsoft', MICROSOFT_USER)
        self.assertEqual(response['Location'], '/saved')
        user = get_user_model().objects.get(email='ravi@outlook.com')
        self.assertEqual(user.first_name, 'Ravi')
        self.assertEqual(SocialAccount.objects.get(user=user).uid, 'ms-42')
        self.assertTrue(session.calls[0][1].startswith('https://login.microsoftonline.com/common/oauth2/v2.0/token'))
        self.assertTrue(session.calls[1][1].startswith('https://graph.microsoft.com/v1.0/me'))
        self.assertEqual(self.client.get('/api/auth/me/').json()['user']['providers'], ['microsoft'])

    def test_microsoft_falls_back_to_user_principal_name(self):
        profile = {**MICROSOFT_USER, 'mail': None, 'userPrincipalName': 'work@contoso.com'}
        self.finish('microsoft', profile)
        self.assertTrue(get_user_model().objects.filter(email='work@contoso.com').exists())

    def test_returning_user_signs_into_same_account(self):
        self.finish('google', GOOGLE_USER)
        user = get_user_model().objects.get(email='asha@gmail.com')
        self.client.post('/api/saved/', {'key': 'gdp_growth'}, content_type='application/json')
        self.client.post('/api/auth/logout/')
        self.finish('google', GOOGLE_USER)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(self.client.get('/api/auth/me/').json()['user']['id'], user.id)
        self.assertEqual(SavedChart.objects.filter(user=user).count(), 1)

    def test_verified_google_email_links_existing_account(self):
        existing = get_user_model().objects.create_user('asha', 'asha@gmail.com')
        self.finish('google', GOOGLE_USER)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(SocialAccount.objects.get().user, existing)

    def test_unverified_microsoft_email_never_takes_over_existing_account(self):
        victim = get_user_model().objects.create_user('asha', 'asha@gmail.com')
        profile = {**MICROSOFT_USER, 'mail': 'asha@gmail.com'}
        self.finish('microsoft', profile)
        self.assertFalse(SocialAccount.objects.filter(user=victim).exists())
        me = self.client.get('/api/auth/me/').json()
        self.assertFalse(me['authenticated'] and me['user']['id'] == victim.id)

    def test_offsite_next_is_ignored(self):
        response, _ = self.finish('google', GOOGLE_USER, next_url='https://evil.example/steal')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response['Location'].startswith('https://evil.example'))

    def test_state_mismatch_is_rejected(self):
        self.start('google')
        with mock.patch('allauth.socialaccount.adapter.DefaultSocialAccountAdapter.get_requests_session') as session:
            response = self.client.get('/accounts/google/login/callback/', {'code': 'x', 'state': 'forged'})
            session.assert_not_called()
        self.assertContains(response, "couldn't sign you in", status_code=401)
        self.assertContains(response, 'github.io', status_code=401)
        self.assertFalse(self.client.get('/api/auth/me/').json()['authenticated'])

    def test_token_exchange_failure_shows_error_page(self):
        response, _ = self.finish('google', GOOGLE_USER, token_status=400)
        self.assertContains(response, "couldn't sign you in", status_code=401)
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_profile_failure_shows_error_page(self):
        response, _ = self.finish('microsoft', {'error': {'message': 'denied'}}, profile_status=401)
        self.assertContains(response, "couldn't sign you in", status_code=401)
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_user_cancelling_at_provider(self):
        state = parse_qs(self.start('google').query)['state'][0]
        response = self.client.get('/accounts/google/login/callback/', {'error': 'access_denied', 'state': state})
        if response.status_code == 302:
            response = self.client.get(response['Location'])
        self.assertContains(response, 'cancelled')
        self.assertEqual(get_user_model().objects.count(), 0)


class LocalAccountsDisabledTests(OAuthTestCase):
    def test_allauth_login_and_signup_pages_redirect_to_spa(self):
        self.assertEqual(self.client.get('/accounts/login/')['Location'], '/login')
        self.assertEqual(self.client.get('/accounts/signup/?next=/saved')['Location'], '/login?next=/saved')

    def test_password_signup_is_impossible(self):
        self.client.post('/accounts/signup/', {'email': 'x@example.com', 'password1': 'Strong-pass-123', 'password2': 'Strong-pass-123'})
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_password_login_is_impossible_for_site_users(self):
        get_user_model().objects.create_user('pw', 'pw@example.com', 'Strong-pass-123')
        self.client.post('/accounts/login/', {'login': 'pw@example.com', 'password': 'Strong-pass-123'})
        self.assertFalse(self.client.get('/api/auth/me/').json()['authenticated'])

    def test_password_reset_is_not_exposed(self):
        self.assertEqual(self.client.get('/accounts/password/reset/').status_code, 404)

"""Google + Microsoft (Outlook) sign-in. There are no local usernames/passwords for site users."""
from urllib.parse import urlencode

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, get_adapter
from allauth.socialaccount.models import SocialApp
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse

ALLOWED_PROVIDERS = {'google': 'Google', 'microsoft': 'Microsoft (Outlook)'}


def configured_providers(request):
    """Providers with a client id configured, either via environment settings or a SocialApp in the admin."""
    configured = {app.provider for app in get_adapter(request).list_apps(request) if app.client_id}
    providers = []
    for provider_id, name in ALLOWED_PROVIDERS.items():
        if provider_id not in configured:
            continue
        try:
            login_url = reverse(f'{provider_id}_login')
        except NoReverseMatch:
            continue
        providers.append({'id': provider_id, 'name': name, 'login_url': login_url})
    return providers


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return sociallogin.account.provider in ALLOWED_PROVIDERS

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.first_name and data.get('name'):
            first, _, last = data['name'].partition(' ')
            user.first_name, user.last_name = first[:150], last[:150]
        return user


class MissingProviderMiddleware:
    """A provider whose credentials are not configured redirects to the sign-in page instead of a 500."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, SocialApp.DoesNotExist):
            return redirect(f"/login?{urlencode({'error': 'unavailable'})}")
        return None

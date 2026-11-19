import hashlib
import urllib.parse
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework.response import Response


def get_cache_timeout():
    return getattr(settings, 'API_CACHE_TIMEOUT', 900)


def get_cache_control():
    return getattr(settings, 'API_CACHE_CONTROL', 'public, max-age=300, stale-while-revalidate=60')


def make_cache_key(request):
    """Deterministic, fixed-length cache key based on URL path and sorted query parameters."""
    query_str = urllib.parse.urlencode(sorted(request.GET.lists(), key=lambda x: x[0]), doseq=True)
    raw = f'{request.path}?{query_str}'
    digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    return f'api:{digest}'


class CachedAPIViewMixin:
    """Mixin for DRF APIViews and generic views that caches read-only GET responses

    in Django's in-memory LocMemCache and attaches public Cache-Control headers.
    """

    cache_timeout = None
    cache_control = None

    def get_cache_timeout(self):
        return self.cache_timeout if self.cache_timeout is not None else get_cache_timeout()

    def get_cache_control(self):
        return self.cache_control if self.cache_control is not None else get_cache_control()

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        drf_request = self.initialize_request(request, *args, **kwargs)
        self.request = drf_request
        self.headers = self.default_response_headers

        try:
            self.initial(drf_request, *args, **kwargs)

            if drf_request.method.lower() == 'get':
                cache_key = make_cache_key(request)
                try:
                    cached = cache.get(cache_key)
                except Exception:
                    cached = None
                if cached is not None:
                    if cached.get('type') == 'http':
                        resp = HttpResponse(
                            cached['content'],
                            status=cached['status'],
                            content_type=cached.get('content_type'),
                        )
                        if cached.get('disposition'):
                            resp['Content-Disposition'] = cached['disposition']
                        self.response = resp
                    else:
                        resp = Response(cached['data'], status=cached['status'])
                        self.response = self.finalize_response(drf_request, resp, *args, **kwargs)
                    self.response['Cache-Control'] = self.get_cache_control()
                    self.response['X-Cache'] = 'HIT'
                    return self.response

            if drf_request.method.lower() in self.http_method_names:
                handler = getattr(self, drf_request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(drf_request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(drf_request, response, *args, **kwargs)
        if drf_request.method.lower() == 'get' and self.response.status_code == 200:
            cache_key = make_cache_key(request)
            ttl = self.get_cache_timeout()
            try:
                if hasattr(response, 'data'):
                    cache.set(cache_key, {'type': 'drf', 'data': response.data, 'status': response.status_code}, ttl)
                else:
                    cache.set(cache_key, {
                        'type': 'http',
                        'content': self.response.content,
                        'status': self.response.status_code,
                        'content_type': self.response.get('Content-Type'),
                        'disposition': self.response.get('Content-Disposition'),
                    }, ttl)
                self.response['X-Cache'] = 'MISS'
            except Exception:
                self.response['X-Cache'] = 'BYPASS'
        self.response['Cache-Control'] = self.get_cache_control()
        return self.response


def cache_api_root(view_func):
    """Caches function-based api_root with public Cache-Control headers."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.method != 'GET':
            return view_func(request, *args, **kwargs)
        cache_key = make_cache_key(request)
        try:
            cached = cache.get(cache_key)
        except Exception:
            cached = None
        ttl = get_cache_timeout()
        c_control = get_cache_control()
        if cached is not None:
            resp = Response(cached['data'], status=cached['status'])
            resp['Cache-Control'] = c_control
            resp['X-Cache'] = 'HIT'
            return resp
        resp = view_func(request, *args, **kwargs)
        if getattr(resp, 'status_code', None) == 200 and hasattr(resp, 'data'):
            try:
                cache.set(cache_key, {'type': 'drf', 'data': resp.data, 'status': resp.status_code}, ttl)
                resp['X-Cache'] = 'MISS'
            except Exception:
                resp['X-Cache'] = 'BYPASS'
        resp['Cache-Control'] = c_control
        return resp

    return _wrapped

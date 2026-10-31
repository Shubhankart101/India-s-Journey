from django.conf import settings


class FrameAncestorsMiddleware:
    """Allows framing only by the origins in ``DJANGO_FRAME_ANCESTORS``; otherwise X-Frame-Options stays DENY."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        ancestors = getattr(settings, 'FRAME_ANCESTORS', [])
        if ancestors:
            response['Content-Security-Policy'] = "frame-ancestors 'self' " + ' '.join(ancestors)
            # Listed before XFrameOptionsMiddleware, so its DENY header is already set on the way out.
            if response.has_header('X-Frame-Options'):
                del response['X-Frame-Options']
        return response

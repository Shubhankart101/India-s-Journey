import csv
import io
import json
import threading

from django.conf import settings
from django.contrib.auth import logout
from django.db.models import Count, Prefetch, Q
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from drf_spectacular.views import SpectacularAPIView
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import configured_providers
from .models import Article, Category, DataRefresh, Indicator, SavedChart, Subgroup
from .serializers import (
    ArticleSerializer, AuthStateSerializer, CategorySerializer, CompareSerializer, DetailSerializer, HealthSerializer,
    IndicatorDetailSerializer, IndicatorSummarySerializer, ProviderSerializer, SavedChartSerializer, StatsSerializer,
    UserSerializer,
)

MAX_COMPARE = 4
LIVE_COUNT = Count('indicators', filter=Q(indicators__is_live=True))
INDICATOR_FILTERS = [
    OpenApiParameter('q', str, description='Space-separated search terms (all must match).'),
    OpenApiParameter('category', str, description='Category slug, e.g. `macroeconomics`.'),
    OpenApiParameter('subgroup', str, description='Subgroup slug.'),
    OpenApiParameter('live', bool, description='Only live (or only non-live) indicators.'),
    OpenApiParameter('chart', str, enum=['radial', 'line', 'bar'], description='Chart family.'),
    OpenApiParameter('sort', str, enum=['position', 'title', 'recent', 'points'], default='position'),
]


class SchemaView(SpectacularAPIView):
    """drf-spectacular's generator keeps per-run global state, so concurrent generation can crash; serialise it."""

    _lock = threading.Lock()

    def _get_schema_response(self, request):
        with self._lock:
            return super()._get_schema_response(request)


def _truthy(value):
    return str(value).lower() in {'1', 'true', 'yes', 'on'}


def _summary_queryset():
    return Indicator.objects.select_related('category', 'subgroup').defer(
        'labels', 'datasets', 'details', 'note', 'source', 'search_text')


@extend_schema_view(get=extend_schema(summary='Groups with subgroup counts'))
class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = None

    def get_queryset(self):
        subgroups = Subgroup.objects.annotate(indicator_count=Count('indicators'), live_count=LIVE_COUNT)
        return Category.objects.annotate(indicator_count=Count('indicators', distinct=True)).annotate(
            live_count=Count('indicators', filter=Q(indicators__is_live=True), distinct=True),
        ).prefetch_related(Prefetch('subgroups', queryset=subgroups, to_attr='annotated_subgroups'))


@extend_schema_view(get=extend_schema(summary='Search and filter indicators', parameters=INDICATOR_FILTERS))
class IndicatorListView(generics.ListAPIView):
    """Searchable, filterable, paginated indicator list.

    Query params: q, category, subgroup (slugs), live (true/false), chart (radial|line|bar), sort (position|title|recent|points).
    """
    serializer_class = IndicatorSummarySerializer
    sort_options = {'position': 'position', 'title': 'title', 'recent': '-updated_at', 'points': '-point_count'}

    def get_queryset(self):
        params = self.request.query_params
        queryset = _summary_queryset()
        for term in params.get('q', '').lower().split()[:8]:
            queryset = queryset.filter(search_text__contains=term)
        if params.get('category'):
            queryset = queryset.filter(category__slug=params['category'])
        if params.get('subgroup'):
            queryset = queryset.filter(subgroup__slug=params['subgroup'])
        if params.get('live') not in (None, ''):
            queryset = queryset.filter(is_live=_truthy(params['live']))
        chart = params.get('chart')
        if chart == 'radial':
            queryset = queryset.filter(chart_type__in=['pie', 'doughnut'])
        elif chart in {'line', 'bar'}:
            queryset = queryset.filter(chart_type=chart)
        sort = params.get('sort', 'position')
        if sort not in self.sort_options:
            raise ValidationError({'sort': f'Choose one of: {", ".join(self.sort_options)}'})
        return queryset.order_by(self.sort_options[sort], 'position')


@extend_schema_view(get=extend_schema(
    summary='Full indicator data with related indicators',
    description='Adds `related` (same subgroup), `previous_key` and `next_key` (same group).'))
class IndicatorDetailView(generics.RetrieveAPIView):
    serializer_class = IndicatorDetailSerializer
    lookup_field = 'key'
    queryset = Indicator.objects.select_related('category', 'subgroup')

    def retrieve(self, request, *args, **kwargs):
        indicator = self.get_object()
        data = self.get_serializer(indicator).data
        related = _summary_queryset().filter(subgroup=indicator.subgroup).exclude(pk=indicator.pk)[:6]
        data['related'] = IndicatorSummarySerializer(related, many=True).data
        neighbours = list(Indicator.objects.filter(category=indicator.category).order_by('position').values_list('key', flat=True))
        index = neighbours.index(indicator.key)
        data['previous_key'] = neighbours[index - 1] if index > 0 else None
        data['next_key'] = neighbours[index + 1] if index + 1 < len(neighbours) else None
        return Response(data)


def _rows(indicator):
    headers = ['label'] + [dataset['label'] for dataset in indicator.datasets]
    rows = []
    for index, label in enumerate(indicator.labels):
        rows.append([label] + [
            dataset['values'][index] if index < len(dataset['values']) else None for dataset in indicator.datasets])
    return headers, rows


class IgnoreAcceptNegotiation(BaseContentNegotiation):
    """Downloads always return the file type chosen by ?format=, whatever the Accept header says."""

    def select_parser(self, request, parsers):
        return parsers[0]

    def select_renderer(self, request, renderers, format_suffix=None):
        return renderers[0], renderers[0].media_type


@extend_schema(
    summary='Download an indicator as CSV or JSON',
    parameters=[OpenApiParameter('format', str, enum=['csv', 'json'], default='csv', description='File format.')],
    responses={
        (200, 'text/csv'): OpenApiTypes.STR,
        (200, 'application/json'): OpenApiTypes.OBJECT,
        400: DetailSerializer, 404: DetailSerializer,
    },
)
class IndicatorDownloadView(APIView):
    content_negotiation_class = IgnoreAcceptNegotiation

    def get(self, request, key):
        indicator = get_object_or_404(Indicator.objects.select_related('category', 'subgroup'), key=key)
        file_format = request.query_params.get('format', 'csv').lower()
        if file_format == 'json':
            payload = {
                'key': indicator.key, 'title': indicator.title, 'subtitle': indicator.subtitle,
                'category': indicator.category.name, 'subgroup': indicator.subgroup.name, 'unit': indicator.suffix.strip(),
                'frequency': indicator.frequency, 'source_url': indicator.source_url, 'source': indicator.source,
                'labels': indicator.labels, 'datasets': indicator.datasets,
            }
            response = HttpResponse(
                json.dumps(payload, indent=2, ensure_ascii=False), content_type='application/json; charset=utf-8')
        elif file_format == 'csv':
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            headers, rows = _rows(indicator)
            writer.writerow(headers)
            writer.writerows(['' if value is None else value for value in row] for row in rows)
            response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
        else:
            return Response({'detail': 'format must be csv or json'}, status=status.HTTP_400_BAD_REQUEST)
        response['Content-Disposition'] = f'attachment; filename="{indicator.key}.{file_format}"'
        return response


class CompareView(APIView):
    """Aligns up to four indicators on a shared label axis (first dataset of each)."""

    @extend_schema(
        summary='Compare up to four indicators',
        parameters=[OpenApiParameter('keys', str, required=True, description='Comma-separated keys, e.g. `gdp_growth,cpi_inflation`.')],
        responses={200: CompareSerializer, 400: DetailSerializer},
    )
    def get(self, request):
        keys = [key.strip() for key in request.query_params.get('keys', '').split(',') if key.strip()]
        keys = list(dict.fromkeys(keys))
        if not keys:
            return Response({'detail': 'Pass ?keys=a,b with up to four indicator keys.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(keys) > MAX_COMPARE:
            return Response({'detail': f'Compare at most {MAX_COMPARE} indicators.'}, status=status.HTTP_400_BAD_REQUEST)
        found = {item.key: item for item in Indicator.objects.select_related('category', 'subgroup').filter(key__in=keys)}
        missing = [key for key in keys if key not in found]
        indicators = [found[key] for key in keys if key in found]
        labels = list(dict.fromkeys(label for item in indicators for label in item.labels))
        if all(label[:4].isdigit() for label in labels):
            labels.sort()
        series = []
        for item in indicators:
            first = item.datasets[0]['values'] if item.datasets else []
            lookup = {label: first[index] for index, label in enumerate(item.labels) if index < len(first)}
            series.append({
                'key': item.key, 'title': item.title, 'suffix': item.suffix, 'color': item.color,
                'category': item.category.name, 'subgroup': item.subgroup.name, 'chart_type': item.chart_type,
                'values': [lookup.get(label) for label in labels],
            })
        return Response({'labels': labels, 'series': series, 'missing': missing})


@extend_schema_view(get=extend_schema(summary='Articles and reports', parameters=[
    OpenApiParameter('kind', str, description='Publisher kind, e.g. `substack`, `pew`.'),
    OpenApiParameter('q', str, description='Title search.'),
]))
class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = Article.objects.all()
        kind = self.request.query_params.get('kind')
        if kind:
            queryset = queryset.filter(kind=kind)
        query = self.request.query_params.get('q', '').strip()
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset.order_by('-is_featured', '-published_at', 'title')


class StatsView(APIView):
    @extend_schema(summary='Catalogue totals and last refresh', responses=StatsSerializer)
    def get(self, request):
        last = DataRefresh.objects.filter(status='success').first()
        return Response({
            'indicators': Indicator.objects.count(),
            'live_indicators': Indicator.objects.filter(is_live=True).count(),
            'radial_indicators': Indicator.objects.filter(chart_type__in=['pie', 'doughnut']).count(),
            'categories': Category.objects.count(),
            'subgroups': Subgroup.objects.count(),
            'articles': Article.objects.count(),
            'data_points': sum(Indicator.objects.values_list('point_count', flat=True)),
            'source_generated_at': last.source_generated_at if last else None,
            'last_refresh': last.finished_at if last else None,
        })


def _auth_state(request):
    if not request.user.is_authenticated:
        return {'authenticated': False, 'user': None}
    return {'authenticated': True, 'user': UserSerializer(request.user).data}


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfView(APIView):
    @extend_schema(summary='Set the csrftoken cookie', responses=DetailSerializer)
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class MeView(APIView):
    @extend_schema(summary='Current session user', responses=AuthStateSerializer)
    def get(self, request):
        return Response(_auth_state(request))


class ProvidersView(APIView):
    """Sign-in is only through Google or Microsoft (Outlook/Live/Microsoft 365) accounts."""

    @extend_schema(summary='Configured sign-in providers', responses=ProviderSerializer(many=True))
    def get(self, request):
        return Response(configured_providers(request))


class LogoutView(APIView):
    @extend_schema(summary='Sign out', request=None, responses=AuthStateSerializer)
    def post(self, request):
        logout(request)
        return Response({'authenticated': False, 'user': None})


@extend_schema_view(
    get=extend_schema(summary="Signed-in user's saved charts"),
    post=extend_schema(summary='Save a chart (upsert)', responses={200: SavedChartSerializer, 201: SavedChartSerializer}),
)
class SavedChartListView(generics.ListCreateAPIView):
    serializer_class = SavedChartSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return SavedChart.objects.filter(user=self.request.user).select_related(
            'indicator__category', 'indicator__subgroup').defer(
            'indicator__labels', 'indicator__datasets', 'indicator__details', 'indicator__search_text')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved, created = SavedChart.objects.update_or_create(
            user=request.user, indicator=serializer.validated_data['indicator'],
            defaults={'note': serializer.validated_data.get('note', '')})
        return Response(self.get_serializer(saved).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SavedChartDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary='Remove a saved chart', responses={204: None, 404: DetailSerializer})
    def delete(self, request, key):
        deleted, _ = SavedChart.objects.filter(user=request.user, indicator__key=key).delete()
        if not deleted:
            return Response({'detail': 'Not saved.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthView(APIView):
    authentication_classes = []

    @extend_schema(summary='Liveness check', responses=HealthSerializer)
    def get(self, request):
        response = Response({'status': 'ok', 'indicators': Indicator.objects.count(), 'backup_url': settings.BACKUP_SITE_URL})
        # Public, non-sensitive payload: lets the GitHub Pages status page poll it cross-origin.
        response['Access-Control-Allow-Origin'] = '*'
        response['Cache-Control'] = 'no-store'
        return response


def spa_index(request, *args, **kwargs):
    index = settings.FRONTEND_DIST / 'index.html'
    if not index.exists():
        return render(request, 'errors/error.html', {
            'status_code': 503, 'title': 'The web app is being set up',
            'message': 'The frontend has not been built yet. The backup dashboard has the same data.',
        }, status=503)
    response = FileResponse(index.open('rb'), content_type='text/html; charset=utf-8')
    response['Cache-Control'] = 'no-cache'
    return response


def _wants_json(request):
    return request.path.startswith('/api/') or 'application/json' in request.headers.get('Accept', '')


def error_404(request, exception=None):
    if _wants_json(request):
        return JsonResponse({'detail': 'Not found.', 'backup_url': settings.BACKUP_SITE_URL}, status=404)
    return render(request, 'errors/error.html', {
        'status_code': 404, 'title': 'This page wandered off.',
        'message': 'The link may be old, or the page was renamed.',
    }, status=404)


def error_500(request):
    if _wants_json(request):
        return JsonResponse({'detail': 'Server error.', 'backup_url': settings.BACKUP_SITE_URL}, status=500)
    return render(request, 'errors/error.html', {
        'status_code': 500, 'title': 'Something broke on our side.',
        'message': 'The error has been logged. Meanwhile the backup dashboard is available.',
    }, status=500)


def error_403(request, exception=None):
    if _wants_json(request):
        return JsonResponse({'detail': 'Forbidden.', 'backup_url': settings.BACKUP_SITE_URL}, status=403)
    return render(request, 'errors/error.html', {
        'status_code': 403, 'title': 'That action was blocked.',
        'message': 'Your session may have expired. Reload the page and try again.',
    }, status=403)


@extend_schema(summary='API index', responses=OpenApiTypes.OBJECT)
@api_view(['GET'])
@ensure_csrf_cookie
def api_root(request):
    return Response({
        'name': "India's Journey API",
        'docs': {'swagger': '/api/docs/', 'redoc': '/api/redoc/', 'schema': '/api/schema/'},
        'backup_url': settings.BACKUP_SITE_URL,
        'endpoints': {
            'health': '/api/health/',
            'categories': '/api/categories/',
            'indicators': '/api/indicators/?q=&category=&subgroup=&live=&chart=&sort=&page=',
            'indicator': '/api/indicators/<key>/',
            'download': '/api/indicators/<key>/download/?format=csv|json',
            'compare': '/api/compare/?keys=a,b',
            'articles': '/api/articles/?kind=&q=',
            'stats': '/api/stats/',
            'auth': ['/api/auth/providers/', '/api/auth/me/', '/api/auth/csrf/', '/api/auth/logout/'],
            'saved': ['/api/saved/', '/api/saved/<key>/'],
        },
    })

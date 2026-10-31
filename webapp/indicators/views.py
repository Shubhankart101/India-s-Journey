import csv
import io
import json

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Prefetch, Q
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Article, Category, DataRefresh, Indicator, SavedChart, Subgroup
from .serializers import (
    ArticleSerializer, CategorySerializer, IndicatorDetailSerializer, IndicatorSummarySerializer, LoginSerializer,
    RegisterSerializer, SavedChartSerializer, UserSerializer,
)

MAX_COMPARE = 4
LIVE_COUNT = Count('indicators', filter=Q(indicators__is_live=True))


def _truthy(value):
    return str(value).lower() in {'1', 'true', 'yes', 'on'}


def _summary_queryset():
    return Indicator.objects.select_related('category', 'subgroup').defer(
        'labels', 'datasets', 'details', 'note', 'source', 'search_text')


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = None

    def get_queryset(self):
        subgroups = Subgroup.objects.annotate(indicator_count=Count('indicators'), live_count=LIVE_COUNT)
        return Category.objects.annotate(indicator_count=Count('indicators', distinct=True)).annotate(
            live_count=Count('indicators', filter=Q(indicators__is_live=True), distinct=True),
        ).prefetch_related(Prefetch('subgroups', queryset=subgroups, to_attr='annotated_subgroups'))


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


def indicator_download(request, key):
    """Plain Django view: DRF reserves ?format= for renderer negotiation."""
    if request.method != 'GET':
        return JsonResponse({'detail': 'Method not allowed.'}, status=405)
    indicator = get_object_or_404(Indicator.objects.select_related('category', 'subgroup'), key=key)
    file_format = request.GET.get('format', 'csv').lower()
    if file_format == 'json':
        payload = {
            'key': indicator.key, 'title': indicator.title, 'subtitle': indicator.subtitle,
            'category': indicator.category.name, 'subgroup': indicator.subgroup.name, 'unit': indicator.suffix.strip(),
            'frequency': indicator.frequency, 'source_url': indicator.source_url, 'source': indicator.source,
            'labels': indicator.labels, 'datasets': indicator.datasets,
        }
        response = HttpResponse(json.dumps(payload, indent=2, ensure_ascii=False), content_type='application/json; charset=utf-8')
    elif file_format == 'csv':
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        headers, rows = _rows(indicator)
        writer.writerow(headers)
        writer.writerows(['' if value is None else value for value in row] for row in rows)
        response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
    else:
        return JsonResponse({'detail': 'format must be csv or json'}, status=400)
    response['Content-Disposition'] = f'attachment; filename="{indicator.key}.{file_format}"'
    return response


class CompareView(APIView):
    """Aligns up to four indicators on a shared label axis (first dataset of each)."""

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


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfView(APIView):
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class MeView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'authenticated': False, 'user': None})
        return Response({'authenticated': True, 'user': UserSerializer(request.user).data})


class RegisterView(APIView):
    throttle_scope = 'auth'
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response({'authenticated': True, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(RegisterView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response({'authenticated': True, 'user': UserSerializer(user).data})


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'authenticated': False, 'user': None})


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

    def delete(self, request, key):
        deleted, _ = SavedChart.objects.filter(user=request.user, indicator__key=key).delete()
        if not deleted:
            return Response({'detail': 'Not saved.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'indicators': Indicator.objects.count()})


def spa_index(request, *args, **kwargs):
    index = settings.FRONTEND_DIST / 'index.html'
    if not index.exists():
        return JsonResponse({
            'detail': 'The React frontend has not been built. Run `npm run build` in frontend/ or use the Vite dev server.',
            'api': '/api/',
        }, status=503)
    response = FileResponse(index.open('rb'), content_type='text/html; charset=utf-8')
    response['Cache-Control'] = 'no-cache'
    return response


@ensure_csrf_cookie
def api_root(request):
    return JsonResponse({
        'name': "India's Journey API",
        'endpoints': {
            'categories': '/api/categories/',
            'indicators': '/api/indicators/?q=&category=&subgroup=&live=&chart=&sort=&page=',
            'indicator': '/api/indicators/<key>/',
            'download': '/api/indicators/<key>/download/?format=csv|json',
            'compare': '/api/compare/?keys=a,b',
            'articles': '/api/articles/?kind=&q=',
            'stats': '/api/stats/',
            'auth': ['/api/auth/me/', '/api/auth/register/', '/api/auth/login/', '/api/auth/logout/'],
            'saved': ['/api/saved/', '/api/saved/<key>/'],
        },
    })

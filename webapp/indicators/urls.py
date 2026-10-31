from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView

from . import views

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('schema/', views.SchemaView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('health/', views.HealthView.as_view(), name='health'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('indicators/', views.IndicatorListView.as_view(), name='indicators'),
    path('indicators/<slug:key>/', views.IndicatorDetailView.as_view(), name='indicator-detail'),
    path('indicators/<slug:key>/download/', views.IndicatorDownloadView.as_view(), name='indicator-download'),
    path('compare/', views.CompareView.as_view(), name='compare'),
    path('articles/', views.ArticleListView.as_view(), name='articles'),
    path('stats/', views.StatsView.as_view(), name='stats'),
    path('auth/csrf/', views.CsrfView.as_view(), name='auth-csrf'),
    path('auth/me/', views.MeView.as_view(), name='auth-me'),
    path('auth/providers/', views.ProvidersView.as_view(), name='auth-providers'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('saved/', views.SavedChartListView.as_view(), name='saved'),
    path('saved/<slug:key>/', views.SavedChartDetailView.as_view(), name='saved-detail'),
    # Unknown API paths answer with JSON (even with DEBUG on); slash-less paths still get APPEND_SLASH redirects first.
    re_path(r'^.*/$', csrf_exempt(views.error_404), name='api-not-found'),
]

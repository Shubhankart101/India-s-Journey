from django.urls import path

from . import views

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('health/', views.HealthView.as_view(), name='health'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('indicators/', views.IndicatorListView.as_view(), name='indicators'),
    path('indicators/<slug:key>/', views.IndicatorDetailView.as_view(), name='indicator-detail'),
    path('indicators/<slug:key>/download/', views.indicator_download, name='indicator-download'),
    path('compare/', views.CompareView.as_view(), name='compare'),
    path('articles/', views.ArticleListView.as_view(), name='articles'),
    path('stats/', views.StatsView.as_view(), name='stats'),
    path('auth/csrf/', views.CsrfView.as_view(), name='auth-csrf'),
    path('auth/me/', views.MeView.as_view(), name='auth-me'),
    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('saved/', views.SavedChartListView.as_view(), name='saved'),
    path('saved/<slug:key>/', views.SavedChartDetailView.as_view(), name='saved-detail'),
]

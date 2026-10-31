from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from indicators.views import spa_index

admin.site.site_header = "India's Journey admin"
admin.site.site_title = "India's Journey admin"

handler403 = 'indicators.views.error_403'
handler404 = 'indicators.views.error_404'
handler500 = 'indicators.views.error_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('indicators.urls')),
    # allauth's own sign-in/sign-up pages are replaced by the React /login page (Google + Microsoft buttons).
    path('accounts/login/', RedirectView.as_view(url='/login', query_string=True)),
    path('accounts/signup/', RedirectView.as_view(url='/login', query_string=True)),
    path('accounts/', include('allauth.urls')),
    re_path(r'^(?!api/|admin/|static/|accounts/).*$', spa_index, name='spa'),
]

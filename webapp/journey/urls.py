from django.contrib import admin
from django.urls import include, path, re_path

from indicators.views import spa_index

admin.site.site_header = "India's Journey admin"
admin.site.site_title = "India's Journey admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('indicators.urls')),
    re_path(r'^(?!api/|admin/|static/).*$', spa_index, name='spa'),
]

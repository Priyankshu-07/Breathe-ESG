from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/auth/', include('apps.users.urls')),
    path('api/tenants/', include('apps.tenants.urls')),
    path('api/ingestion/', include('apps.ingestion.urls')),
    path('api/emissions/', include('apps.emissions.urls')),
    path('api/review/', include('apps.review.urls')),
    path('api/audit/', include('apps.audit.urls')),
]

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
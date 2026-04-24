"""URL Configuration."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.api.views import root_view

urlpatterns = [
    path("", root_view, name="root"),
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/auth/", include("apps.api.urls_auth")),
    path("api/", include("apps.api.urls_news")),
    path("api/", include("apps.api.urls_user")),
    path("api/admin/", include("apps.api.urls_admin")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

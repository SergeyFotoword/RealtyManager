from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/accounts/", include("apps.accounts.urls")),
    path("api/", include("apps.reviews.urls")),
    path("api/", include("apps.routers")),
    path("api/", include("apps.listings.urls")),
    path("api/", include("apps.properties.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from apps.accounts.views.auth_views import RegisterView


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/accounts/", include("apps.accounts.urls")),
    path("api/bookings/", include("apps.bookings.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/listings/", include("apps.listings.urls")),
    path("api/properties/", include("apps.properties.urls")),

    path("api/auth/register/", RegisterView.as_view(), name="auth_register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
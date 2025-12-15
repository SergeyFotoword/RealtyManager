from django.urls import path, include

urlpatterns = [
    path("accounts/", include('apps.accounts.urls')),
    path("bookings/", include("apps.bookings.urls")),
]
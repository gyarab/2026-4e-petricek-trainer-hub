"""Hlavní směrování URL. Další aplikace sem přidáme pomocí include()."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("exercises/", include("exercises.urls")),
    path("plans/", include("plans.urls")),
    path("", include("accounts.urls")),
]

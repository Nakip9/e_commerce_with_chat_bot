"""URL configuration for the AutoDrive project."""
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("market.urls")),
    path('chat/',include('chat_bot.urls')),
]

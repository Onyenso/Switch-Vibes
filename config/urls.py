"""project_switch_vibes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


# This is used in settings.py
api_info = openapi.Info(
    title="Switch Vibes API",
    default_version="v1",
    description="API for Switch Vibes",
    contact=openapi.Contact(
        name="Uchenna Onyenso",
        email="alphadev.onyenso@gmail.com",
        url="https://onyenso.github.io/alphadev/"
    )
)


schema_view = get_schema_view(
    public=True,
    permission_classes=[permissions.AllowAny]
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("yt_to_spotify.urls")),
    path("", include("spotify_to_yt.urls")),
    path("docs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]

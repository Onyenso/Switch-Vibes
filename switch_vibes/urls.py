from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="sw-index"),
    path("switch_vibes/", views.SwitchVibes.as_view(), name="sw-switch_vibes")
]
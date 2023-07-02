from django.urls import path

from switch_vibes.views import index, YtToSpotify


urlpatterns = [
    path("", index, name="sw-index"),
    path("yt_to_spotify/", YtToSpotify.as_view(), name="yt-to-spotify"),
]
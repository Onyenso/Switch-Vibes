from django.urls import path

from spotify_to_yt.views import SpotifyToYt


urlpatterns = [
    path("spotify_to_yt/", SpotifyToYt.as_view(), name="spotify-to-yt"),
]

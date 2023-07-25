from django.urls import path

from switch_vibes.views import index, YtToSpotify, SpotifyToYt


urlpatterns = [
    path("", index, name="sw-index"),
    path("yt_to_spotify/", YtToSpotify.as_view(), name="yt-to-spotify"),
    path("spotify_to_yt/", SpotifyToYt.as_view(), name="spotify-to-yt"),
    # path("yt_to_spotify2/", YtToSpotify2.as_view(), name="yt-to-spotify2"),
]

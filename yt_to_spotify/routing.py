from django.urls import re_path

from yt_to_spotify.consumers import YtToSpotifyConsumer


websocket_urlpatterns = [
    re_path(r"ws/yt_to_spotify/$", YtToSpotifyConsumer.as_asgi())
]
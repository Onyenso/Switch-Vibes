from django.urls import re_path

from switch_vibes.consumers import YtToSpotifyConsumer


websocket_urlpatterns = [
    re_path(r"ws/yt_to_spotify/$", YtToSpotifyConsumer.as_asgi())
]
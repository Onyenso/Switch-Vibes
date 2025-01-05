from django.urls import re_path

from spotify_to_yt.consumers import SpotifyToYtConsumer


websocket_patterns = [
    re_path(r"ws/spotify_to_yt/$", SpotifyToYtConsumer.as_asgi())
]
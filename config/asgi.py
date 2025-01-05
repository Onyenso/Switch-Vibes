"""
ASGI config for project_switch_vibes project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from decouple import config
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from yt_to_spotify.routing import websocket_urlpatterns as yt_to_spotify_websocket_urlpatterns
from spotify_to_yt.routing import websocket_patterns as spotify_to_yt_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', config("DJANGO_SETTINGS_MODULE"))

django_asgi_app = get_asgi_application()
all_websocket_urlpatterns = yt_to_spotify_websocket_urlpatterns + spotify_to_yt_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(all_websocket_urlpatterns)
})

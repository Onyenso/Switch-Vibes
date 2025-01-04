"""
ASGI config for project_switch_vibes project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from dotenv import load_dotenv

from channels.routing import ProtocolTypeRouter, URLRouter


load_dotenv()

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get("DJANGO_SETTINGS_MODULE"))

django_asgi_app = get_asgi_application()

from yt_to_spotify.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns)
})

"""
WSGI config for project_switch_vibes project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv


load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get("DJANGO_SETTINGS_MODULE"))

application = get_wsgi_application()
